"""Actual independent encrypted stores expose cross-root and ambiguity mistakes."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from scripts.artifacts import AVG as avg
from admin.test.scripts.test_avg_key_only_report import create_avg_fixture
from admin.test.scripts.test_history_doclist_all_sources import Context


def png(color):
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))
            +chunk(b'IDAT',zlib.compress(b'\0'+bytes([color,2,3])))+chunk(b'IEND',b''))


def encrypt(data, key):
    iv=bytes(range(16))
    cipher=AES.new(key,AES.MODE_CBC,iv).encrypt(pad(data,16))
    return struct.pack('>I',16)+iv+struct.pack('>I',len(cipher))+cipher


def create_root_fixture(root, ambiguous=False):
    root=Path(root)
    files=[]
    expected={}
    for name,color in [('A',10),('B',20)]+([('C',30),('D',40),('E',50)] if ambiguous else []):
        key=bytes([color])*32
        image=png(color)
        paths=create_avg_fixture(root/name,media=True,master=key,image=image)
        if name=='B':
            for index,path in enumerate(paths):
                target=Path(path).with_name(Path(path).name)
                target=Path(str(target).replace('/data/data/','/data/user/10/'))
                target.parent.mkdir(parents=True,exist_ok=True)
                Path(path).rename(target)
                paths[index]=str(target)
        vault=Path(paths[0]).parent.parent
        meta=vault/'.metadata_store/meta'
        meta.parent.mkdir(parents=True,exist_ok=True)
        payload={'items':[{'vaultFileName':'encrypted-picture','originFilePath':name+'/original.png',
                           'date':1700000000000+color,'size':len(image)}]}
        meta.write_bytes(encrypt(json.dumps(payload).encode(),key))
        paths.append(str(meta))
        if name=='C':
            other=meta.with_name('other');other.write_bytes(encrypt(b'{"items":[]}',key));paths.append(str(other))
        if name=='D':
            other=Path(paths[0]).with_name('other')
            with tempfile.TemporaryDirectory() as temporary:
                extra=create_avg_fixture(temporary,master=bytes([41])*32)[0]
                other.write_bytes(Path(extra).read_bytes())
            paths.append(str(other))
        if name=='E':
            Path(paths[0]).write_bytes(b'short')
        files.extend(paths)
        if name not in ['D','E']:expected[name]=(key,image,payload)
    # Only identical storage aliases may collapse.
    for path in list(files):
        if '/A/data/data/' in path:
            alias=Path(path.replace('/data/data/','/data/user/0/'))
            alias.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,alias);files.append(str(alias))
    # Standalone settings remain visible and independent of a Vault.
    settings_root=root/'SETTINGS'
    settings=create_avg_fixture(settings_root,settings=True)[1]
    files.append(settings)
    shutil.rmtree(Path(settings).parents[1]/'Vault')
    return files,expected


class TestAvgVaultRoots(unittest.TestCase):
    def test_two_keys_metadata_exports_and_aliases_are_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            files,expected=create_root_fixture(directory)
            exports=[]
            def record(source,data,*_args,**_kwargs):
                exports.append((source,data))
                return hashlib.sha256(data).hexdigest()
            with patch.object(avg,'check_in_embedded_media',side_effect=record):
                _,rows,_=avg.get_AVG_media.__wrapped__(Context(directory,list(reversed(files))))
                _,details,_=avg.get_AVG.__wrapped__(Context(directory,files))
            self.assertEqual(len(rows),2)
            self.assertEqual(len(exports),2)
            self.assertEqual({data for _,data in exports},{value[1] for value in expected.values()})
            for row in rows:
                name=row[1].split('/')[0]
                self.assertEqual(row[6],name+'/original.png')
                self.assertEqual(row[0],expected[name][2]['items'][0]['date'])
                self.assertTrue(row[2].startswith(name+'/'))
                self.assertTrue(row[3].startswith(name+'/'))
            keys=[row for row in details if row[0]=='Master Key']
            self.assertEqual({row[1] for row in keys},{value[0].hex() for value in expected.values()})
            self.assertTrue(all(row[2] for row in keys))
            independent=[row for row in details if row[3].startswith('SETTINGS/')]
            self.assertTrue(independent)
            self.assertTrue(all(row[2]=='' for row in independent))
            _,inventory,_=avg.get_AVG_inventory.__wrapped__(Context(directory,files))
            self.assertEqual(len(inventory),7)
            self.assertEqual(sum(len(json.loads(row[5])) for row in inventory),len(files))

    def test_ambiguous_and_malformed_roots_do_not_poison_healthy_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            files,_=create_root_fixture(directory,ambiguous=True)
            with patch.object(avg,'check_in_embedded_media',return_value='constructed-reference'),patch.object(avg,'logfunc'):
                _,rows,_=avg.get_AVG_media.__wrapped__(Context(directory,files))
                _,inventory,_=avg.get_AVG_inventory.__wrapped__(Context(directory,files))
            self.assertEqual({row[1].split('/')[0] for row in rows},{'A','B','C'})
            ambiguous=[row for row in rows if row[1].startswith('C/')][0]
            self.assertEqual((ambiguous[0],ambiguous[3],ambiguous[6],ambiguous[7]),('','','',''))
            self.assertEqual(ambiguous[4],'ambiguous metadata candidates')
            self.assertEqual(sum(row[2]=='key' and row[0].startswith('D/') for row in inventory),2)
            self.assertTrue(any(row[6]=='ambiguous key candidates' for row in inventory))


    def test_conflicting_aliases_unknown_prefix_and_staging_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            files,_=create_root_fixture(root)
            conflict=next(Path(p) for p in files if '/A/data/user/0/' in p and '/.key_store/' in p)
            with tempfile.TemporaryDirectory() as temporary:
                extra=create_avg_fixture(temporary,master=bytes([99])*32)[0]
                conflict.write_bytes(Path(extra).read_bytes())
            for source in list(files):
                if '/A/data/data/' in source:
                    target=Path(source.replace('/A/data/data/','/UNKNOWN/data/data/'))
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(source,target)
                    files.append(str(target))
            with patch.object(avg,'check_in_embedded_media',return_value='constructed-reference'),patch.object(avg,'logfunc'):
                _,rows,_=avg.get_AVG_media.__wrapped__(Context(root,files))
                _,inventory,_=avg.get_AVG_inventory.__wrapped__(Context(root,files))
                self.assertEqual({r[1].split('/')[0] for r in rows},{'B','UNKNOWN'})
                self.assertEqual(sum(r[2]=='key' and r[0].startswith('A/') for r in inventory),2)
                staged=root/'mirror-user0-stage'
                staged_files=[]
                for source in files:
                    target=staged/Path(source).relative_to(root)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(source,target)
                    staged_files.append(str(target))
                self.assertEqual(avg.get_AVG_media.__wrapped__(Context(staged,staged_files))[1],rows)

    def test_nearest_nested_root_and_missing_key_do_not_borrow_parent_key(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            files,_=create_root_fixture(root)
            missing=root/'MISSING/Vault/pictures/encrypted-picture'
            missing.parent.mkdir(parents=True)
            shutil.copy2(next(p for p in files if '/A/data/data/' in p and '/pictures/' in p),missing)
            files.append(str(missing))
            nested=create_avg_fixture(root/'NESTED/Vault',media=True,master=bytes([60])*32,image=png(60))
            files.extend(nested)
            outer=root/'NESTED/Vault/unscoped.txt';outer.write_text('source inventory',encoding='utf-8')
            files.append(str(outer))
            with patch.object(avg,'check_in_embedded_media',return_value='constructed-reference'),patch.object(avg,'logfunc'):
                _,rows,_=avg.get_AVG_media.__wrapped__(Context(root,files))
                _,inventory,_=avg.get_AVG_inventory.__wrapped__(Context(root,files))
            self.assertEqual(len(rows),3)
            self.assertFalse(any(row[1] in ['MISSING/Vault','NESTED/Vault'] for row in rows))
            self.assertTrue(any(row[1]=='NESTED/Vault/data/data/com.antivirus/Vault' for row in rows))
            self.assertTrue(any(row[0]=='MISSING/Vault' and row[6]=='no key candidate' for row in inventory))

    def test_unreadable_candidate_remains_in_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            files,_=create_root_fixture(directory)
            blocked=next(p for p in files if '/A/data/data/' in p and '/.key_store/' in p)
            ordinary_open=open
            def read_source(path,*args,**kwargs):
                if str(path)==blocked:
                    raise PermissionError('constructed unreadable source')
                return ordinary_open(path,*args,**kwargs)
            with patch('builtins.open',side_effect=read_source),patch.object(avg,'logfunc'):
                _,inventory,_=avg.get_AVG_inventory.__wrapped__(Context(directory,files))
            unreadable=[row for row in inventory if row[3]==str(Path(blocked).relative_to(directory))]
            self.assertEqual(len(unreadable),1)
            self.assertEqual(unreadable[0][4],'')
            self.assertIn('source unreadable',unreadable[0][6])

    def test_wrong_shape_metadata_retains_images_and_healthy_roots(self):
        for payload in ([], 42, {"items": None}, {"items": [42]}):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                files,expected=create_root_fixture(directory)
                for candidate in files:
                    if '/A/' in candidate and '/.metadata_store/' in candidate:
                        Path(candidate).write_bytes(encrypt(json.dumps(payload).encode(),expected['A'][0]))
                with patch.object(avg,'check_in_embedded_media',return_value='constructed-reference'),patch.object(avg,'logfunc') as log:
                    _,rows,_=avg.get_AVG_media.__wrapped__(Context(directory,files))
                self.assertEqual(len(rows),2)
                healthy=next(row for row in rows if row[1].startswith('B/'))
                self.assertEqual(healthy[6],'B/original.png')
                invalid=next(row for row in rows if row[1].startswith('A/'))
                self.assertEqual(invalid[6],'No Data')
                self.assertTrue(any('could not read metadata store' in str(call) for call in log.call_args_list))
