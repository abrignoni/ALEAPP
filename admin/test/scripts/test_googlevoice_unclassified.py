"""Unknown records retain source-backed raw evidence without guessed message roles."""
import json
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.googlevoice_unclassified_fixture import make_database,wire
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts import googleVoice as parser


def restored(node):
    kind=node['type']
    if kind=='bytes':return bytes.fromhex(node['hex'])
    if kind=='int':return int(node['decimal'])
    if kind=='dict':return {restored(k):restored(v) for k,v in node['entries']}
    if kind=='list':return [restored(v) for v in node['items']]
    if kind=='null':return None
    return node['value']


class GoogleVoiceUnclassifiedTest(unittest.TestCase):
    def test_healthy_cells_overlap_and_media_side_effect(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(parser,'check_in_media',return_value='exported.png') as media:
            root=pathlib.Path(folder);path,raw=make_database(root)
            ctx=context(root,[str(path),str(next(root.rglob('*.png')))])
            _,legacy,source=parser.googlevoice_messages.__wrapped__(ctx)
            self.assertEqual(len(legacy),5);self.assertEqual(source,str(path));self.assertEqual(media.call_count,1)
            self.assertEqual([r[1] for r in legacy],['Incoming','Outgoing','Incoming','Outgoing',''])
            self.assertEqual(legacy[0][2:5],('other','MMS image','exported.png'))
            self.assertEqual(legacy[-1][2:5],('','body',''))
            headers,rows,source=parser.googlevoice_unclassified_store_records.__wrapped__(ctx)
            self.assertEqual(len(headers),8);self.assertEqual(len(rows),5);self.assertEqual(source,str(path))
            self.assertEqual([r[1] for r in rows],[5,6,7,8,9]);self.assertEqual(rows[0][2:],rows[3][2:])
            self.assertEqual(media.call_count,1)
            for row in rows:
                blob,cid=raw[row[1]-1]
                self.assertEqual(restored(json.loads(row[2])),cid)
                self.assertEqual(restored(json.loads(row[6])),blob)

    def test_routing_guards_null_nontext_missing13_and_later_healthy(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(parser,'logfunc') as logger:
            root=pathlib.Path(folder);path,raw=make_database(root,'BOUNDARIES');ctx=context(root,[str(path)])
            _,legacy,_=parser.googlevoice_messages.__wrapped__(ctx)
            self.assertEqual(len(legacy),3);self.assertEqual(legacy[-1][1],'Outgoing')
            messages=[call.args[0] for call in logger.call_args_list]
            self.assertEqual(len(messages),4);self.assertTrue(all('when enabled' in m and 'unordered query ordinal ' in m for m in messages))
            _,rows,_=parser.googlevoice_unclassified_store_records.__wrapped__(ctx)
            self.assertEqual(len(rows),8)
            for row in rows:
                blob,cid=raw[row[1]-1]
                self.assertEqual(restored(json.loads(row[2])),cid)
                self.assertEqual(restored(json.loads(row[6])),blob)
            self.assertEqual([r[5] for r in rows[:4]],['Yes','Yes','Yes','No'])
            self.assertEqual(rows[4][7],'');self.assertEqual(rows[5][7],'');self.assertEqual(rows[6][7],'')

    def test_new_only_decode_errors_schema_later_wal_and_repeated_inputs(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(parser,'logfunc'):
            root=pathlib.Path(folder);bad=root/'bad/LegacyMsgDbInstance.db';bad.parent.mkdir();db=sqlite3.connect(bad);db.execute('CREATE TABLE other(x)');db.close()
            first,_=make_database(root,'NEW_ONLY');later,_=make_database(root,'SAFE',prefix='copy/data/data',account='2')
            with tempfile.TemporaryDirectory() as staging:
                staged=pathlib.Path(staging)/'wal.db';shutil.copy2(first,staged);db=sqlite3.connect(staged)
                db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
                db.execute('INSERT INTO message_t VALUES(?,?)',(wire(0),'x-wal'));db.commit()
                for suffix in ['', '-wal','-shm']:shutil.copy2(str(staged)+suffix,str(first)+suffix)
                db.close()
            headers,rows,source=parser.googlevoice_unclassified_store_records.__wrapped__(context(root,[str(bad),str(first)+'-wal',str(first),str(later)]))
            self.assertEqual(len(headers),9);self.assertEqual(len(rows),10)
            self.assertEqual(source,'\n'.join(map(str,[first,later])))
            self.assertTrue(all(r[-1]==str(first.relative_to(root)) for r in rows[:5]))
            self.assertEqual(restored(json.loads(rows[4][2])),'x-wal')
            headers,rows,source=parser.googlevoice_unclassified_store_records.__wrapped__(context(root,[str(first),str(first)]))
            self.assertEqual(len(headers),8);self.assertEqual(len(rows),10);self.assertEqual(source,str(first))

    def test_actual_truncated_length_wire_retains_raw_and_bounded_diagnostics(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(parser,'logfunc') as logger:
            root=pathlib.Path(folder);path,_=make_database(root,'SAFE')
            db=sqlite3.connect(path)
            db.execute('DELETE FROM message_t')
            db.execute('INSERT INTO message_t VALUES(?,?)',(b'\x0a\x05a','t-truncated'))
            db.execute('INSERT INTO message_t VALUES(?,?)',(wire(0),'x-later'))
            db.commit();db.close()
            ctx=context(root,[str(path)])
            with patch.object(ctx,'get_relative_path',return_value='long\n"'+('x'*1000)):
                _,rows,_=parser.googlevoice_unclassified_store_records.__wrapped__(ctx)
            self.assertEqual(len(rows),2)
            self.assertEqual(restored(json.loads(rows[0][6])),b'\x0a\x05a')
            self.assertIn('DecodeError',rows[0][3])
            diagnostic=logger.call_args_list[0].args[0]
            self.assertNotIn('\n',diagnostic);self.assertIn('\\n',diagnostic)
            self.assertIn('[truncated]',diagnostic);self.assertLess(len(diagnostic),400)



if __name__=='__main__':
    unittest.main()
