"""Unknown storage layouts retain file origins without new message associations."""
import base64
import os
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import smsmms as parser

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aV1sAAAAASUVORK5CYII=')


def fixture(root):
    package='com.android.providers.telephony'
    dbpath=root/'data/user_de/0'/package/'databases/mmssms.db'
    dbpath.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(dbpath)
    db.executescript('CREATE TABLE pdu(_id,thread_id,date,msg_box); CREATE TABLE part(_id,mid,ct,_data); CREATE TABLE addr(msg_id,type,address);')
    db.execute('INSERT INTO pdu VALUES(1,7,1700000000,1)')
    db.execute('INSERT INTO addr VALUES(1,137,?)',('stored address',))
    db.executemany('INSERT INTO part VALUES(?,?,?,?)',[(1,1,'image/png',f'/data/user_de/0/{package}/app_parts/linked.png'),(2,1,'image/png',f'/data/user_de/0/{package}/app_parts/same.png')])
    db.commit();db.close()
    paths=[str(dbpath)]
    files=[(f'data/user_de/0/{package}/app_parts/linked.png',PNG),
           (f'data/user_de/0/{package}/parts/orphan.png',PNG),
           (f'unknownA/{package}/app_parts/same.png',PNG),
           (f'unknownB/{package}/app_parts/same.png',PNG+b'different bytes'),
           (f'unknownA/{package}/parts/empty',b''),
           (f'unknownA/{package}/parts/data.bin',b'opaque stored bytes')]
    for relative,data in files:
        path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);paths.append(str(path))
    original=root/files[2][0]
    for name,link in [('hardlink.png',os.link),('symlink.png',os.symlink)]:
        target=original.with_name(name);link(original,target);paths.append(str(target))
    return paths


def context(root,paths):
    return SimpleNamespace(get_files_found=lambda:paths,get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))


class UnresolvedInventoryTest(unittest.TestCase):
    def test_old_rows_and_distinct_file_origins(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);paths=fixture(root)
            with patch.object(parser,'check_in_media',side_effect=lambda p,*_:'media:'+p):
                headers,rows,source=parser.get_sms_mms_attachments.__wrapped__(context(root,paths+[paths[3]]))
            self.assertEqual(len(headers),14)
            self.assertEqual([r[7] for r in rows[:3]],['Referenced by message','Referenced, file not in extraction','Not referenced by any part row'])
            candidates=rows[3:];self.assertEqual(len(candidates),6)
            self.assertTrue(all(r[7]=='File candidate, storage identity unresolved' and r[:3]==('','','') and r[9:13]==('','','','') for r in candidates))
            origins=[r[13] for r in candidates];self.assertEqual(origins,sorted(origins));self.assertEqual(len(set(origins)),6)
            self.assertTrue(any(p.endswith('hardlink.png') for p in origins));self.assertTrue(any(p.endswith('symlink.png') for p in origins))
            self.assertEqual(next(r[4] for r in candidates if r[13].endswith('/empty')),'')
            self.assertEqual(source.splitlines(),[paths[0]]+[str(root/p) for p in origins])
            with patch.object(parser,'check_in_media',side_effect=lambda p,*_:'media:'+p):
                _,reversed_rows,_=parser.get_sms_mms_attachments.__wrapped__(context(root,list(reversed(paths))))
            self.assertEqual(rows,reversed_rows)

    def test_existing_unknown_tail_reference_is_not_duplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);paths=fixture(root);unique=root/'unknownC/com.android.providers.telephony/parts/unique.png';unique.parent.mkdir(parents=True);unique.write_bytes(PNG);paths.append(str(unique))
            db=sqlite3.connect(paths[0]);db.execute('INSERT INTO part VALUES(3,1,?,?)',('image/png','/unrecognized/parts/unique.png'));db.commit();db.close()
            with patch.object(parser,'check_in_media',return_value='media'):
                _,rows,_=parser.get_sms_mms_attachments.__wrapped__(context(root,paths))
            self.assertEqual(sum(r[13]==str(unique.relative_to(root)) for r in rows),1)
            self.assertEqual(rows[2][7],'Referenced by message')

    def test_file_only_and_excluded_parents(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);path=root/'unknown/com.android.providers.telephony/parts/data.bin';path.parent.mkdir(parents=True);path.write_bytes(b'opaque')
            directory_path=path.parent/'directory';directory_path.mkdir()
            with patch.object(parser,'check_in_media',return_value='media'):
                _,rows,source=parser.get_sms_mms_attachments.__wrapped__(context(root,[str(path),str(path),str(directory_path)]))
            self.assertEqual(len(rows),1);self.assertEqual(source,str(path))


if __name__=='__main__':
    unittest.main()
