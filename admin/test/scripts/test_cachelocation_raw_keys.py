"""Packed binary records retain exact keys, repeated observations and decoded prefixes."""
import pathlib
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.cachelocation import get_cachelocation


def record(key, accuracy=10):
    return struct.pack('>h',len(key))+key+struct.pack('>iiddQ',accuracy,20,12.5,-45.25,1700000000123)


def write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);return path


def make_fixture(root):
    first=write(root/'A/com.google.android.location/files/cache.cell/cache.cell',struct.pack('>hh',1,3)+record(b'\x00\xff\x80')*2+record(b''))
    second=write(root/'B/com.google.android.location/files/cache.wifi/cache.wifi',struct.pack('>hh',2,1)+record(b'other',30))
    empty=write(root/'EMPTY/com.google.android.location/files/cache.cell/cache.cell',struct.pack('>hh',1,0))
    return [first,second,empty]


class CacheLocationRawKeysTest(unittest.TestCase):
    def test_actual_packed_keys_order_sources_and_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);files=make_fixture(root)
            headers,rows,sources=get_cachelocation.__wrapped__(context(root,files))
            self.assertEqual(headers[0],('Readtime','datetime'))
            self.assertEqual([bytes.fromhex(row[1]) for row in rows],[b'\x00\xff\x80',b'\x00\xff\x80',b'',b'other'])
            self.assertEqual(rows[0],rows[1]);self.assertEqual(rows[0][2:6],(10,20,12.5,-45.25))
            self.assertEqual(sources.splitlines(),[str(files[0]),str(files[1])])
            self.assertEqual([r[-1] for r in rows],[str(files[0].relative_to(root))]*3+[str(files[1].relative_to(root))])
            headers,rows,sources=get_cachelocation.__wrapped__(context(root,files[1:]))
            self.assertNotIn('Source File',headers);self.assertEqual(len(rows),1);self.assertEqual(sources,str(files[1]))
            _,reverse,_=get_cachelocation.__wrapped__(context(root,list(reversed(files))))
            self.assertEqual([r[1] for r in reverse],['6f74686572','00ff80','00ff80',''])

    def test_short_fields_guard_and_prefix_without_fabricated_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);prefix=record(b'long-key'*10)
            cases=[b'\x00',struct.pack('>hh',1,10),struct.pack('>hh',1,2)+prefix+b'\x00',struct.pack('>hh',1,2)+prefix+struct.pack('>h',50)+b'short',struct.pack('>hh',1,2)+prefix+struct.pack('>h',0)+b'body',struct.pack('>hh',1,2)+prefix+struct.pack('>h',-1)]
            files=[write(root/str(i)/'cache.cell',data) for i,data in enumerate(cases)]
            with patch('scripts.artifacts.cachelocation.logfunc') as log:
                _,rows,sources=get_cachelocation.__wrapped__(context(root,files))
            self.assertEqual(len(rows),4);self.assertEqual(len(sources.splitlines()),4)
            self.assertTrue(all(bytes.fromhex(r[1])==b'long-key'*10 for r in rows))
            messages='\n'.join(str(c.args[0]) for c in log.call_args_list)
            for label in ['short header','size guard','short key length','short key','short body','negative key length']:self.assertIn(label,messages)
            self.assertNotIn(str(root),messages)

if __name__=='__main__':
    unittest.main()
