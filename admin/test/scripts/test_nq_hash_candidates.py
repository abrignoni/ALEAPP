"""Known hash candidates preserve leading zeros and exact bounded XOR output."""
from pathlib import Path
import hashlib
import sqlite3
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib
from scripts.artifacts import NQ_Vault as nq
from admin.test.scripts.test_history_doclist_all_sources import Context

KNOWN={'1509442':'1234','1477632':'0000','-1867378635':'123456789','-1812067894':'25101988'}


def image_bytes(color):
    def chunk(kind,value):
        return struct.pack('>I',len(value))+kind+value+struct.pack('>I',zlib.crc32(kind+value))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))
            +chunk(b'tEXt',b'Comment\0'+b'bounded fixture '*30)
            +chunk(b'IDAT',zlib.compress(b'\0'+bytes([color,2,3])))+chunk(b'IEND',b''))


def create_nq_fixture(root):
    folder=Path(root)/'SystemAndroid/Data';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'322w465ay423xy11';db=sqlite3.connect(path)
    db.execute('CREATE TABLE hideimagevideo(file_path_from,file_name_from,file_path_new,time,viode_time,resolution,album_id,password_id)')
    db.execute('CREATE TABLE albums(_id,album_name)');db.execute('CREATE TABLE albumstemp(album_temp_id,album_name_temp)')
    expected={};files=[str(path)]
    for index,identifier in enumerate(KNOWN):
        image=image_bytes(index+10);key=int(identifier)&255;encrypted=bytes(b^key if i<128 else b for i,b in enumerate(image))
        media=folder/'.image'/f'file{index}.bin';media.parent.mkdir(exist_ok=True);media.write_bytes(encrypted);files.append(str(media));expected[str(media)]=image
        db.execute('INSERT INTO hideimagevideo VALUES(?,?,?,?,?,?,?,?)',('/original',f'image{index}.png',f'/SystemAndroid/Data/.image/file{index}.bin',1700000000000+index,0,'1x1',None,identifier))
    db.commit();db.close();return files,expected


class TestNqHashCandidates(unittest.TestCase):
    def test_known_text_integer_inputs_never_enumerate(self):
        nq.brute_force_pin.cache_clear()
        with patch.object(nq.itertools,'product',side_effect=AssertionError('unexpected search')):
            for identifier,candidate in KNOWN.items():
                for stored in [identifier,int(identifier)]:
                    self.assertEqual(nq.brute_force_pin(stored),candidate)
                    self.assertEqual(nq.java_string_hashcode(candidate),int(identifier))
                    self.assertEqual(int(nq.raw_pin_to_xor_key(candidate),16),int(identifier)&255)

    def test_actual_database_candidates_exports_and_source(self):
        with tempfile.TemporaryDirectory() as root:
            files,expected=create_nq_fixture(root);exports={}
            def check_in(source,data,*_args,**_kwargs):
                exports[source]=data;return hashlib.sha256(data).hexdigest()
            with patch.object(nq,'check_in_embedded_media',side_effect=check_in),patch.object(nq.itertools,'product',side_effect=AssertionError('unexpected search')):
                _,candidates,_=nq.get_NQVault.__wrapped__(Context(root,files))
                headers,rows,_=nq.get_NQVault_media.__wrapped__(Context(root,files))
            self.assertEqual(dict(candidates),KNOWN)
            self.assertEqual(exports,expected)
            self.assertEqual(headers[0],('Timestamp','datetime'))
            self.assertEqual(len(rows),4)
            for source,image in exports.items():
                self.assertGreater(len(image),128)
                self.assertEqual(Path(source).read_bytes()[128:],image[128:])
            names=[h[0] if isinstance(h,tuple) else h for h in headers]
            for values in rows:
                row=dict(zip(names,values));self.assertEqual(row['Matching Digit String Candidate'],KNOWN[row['Stored Password ID']]);self.assertTrue((Path(root)/row['Full Path']).is_file())
