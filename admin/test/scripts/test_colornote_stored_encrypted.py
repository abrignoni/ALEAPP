"""Stored encrypted values retain native SQLite distinctions and WAL observations."""
import datetime
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import colorNote
VALUES=[None,0,1,-1,0.0,0.5,'0','','unknown',b'',b'ascii',b'\x00\xff']


def fixture(root,wal=False,affinity=''):
    path=root/'data/data/com.socialnmobile.dictapps.notepad.color.note/databases/colornote.db';path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path)
    if wal:db.execute('pragma journal_mode=WAL');db.execute('pragma wal_autocheckpoint=0')
    db.execute('create table notes(created_date,modified_date,minor_modified_date,reminder_date,title,note,type,active_state,space,reminder_type,color_index,encrypted '+affinity+',latitude,longitude,uuid)');db.commit()
    if wal:db.execute('pragma wal_checkpoint(truncate)')
    for i,value in enumerate(VALUES+[VALUES[1]]):
        if i==len(VALUES):i=1
        row=(1700000000000,1700000001000,0,-1,'title '+str(i),'stored note '+str(i),0,0,0,0,i,value,0,None,'uuid-'+str(i));db.execute('insert into notes values('+','.join('?' for _ in row)+')',row)
    db.commit()
    if not wal:db.close();db=None
    return path,db


def context(root,paths):
    return SimpleNamespace(get_files_found=lambda:[str(p) for p in paths],get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))


def oracle(root,path):
    db=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True);raw=db.execute('select created_date,modified_date,minor_modified_date,reminder_date,title,note,type,active_state,space,reminder_type,color_index,encrypted,latitude,longitude,uuid from notes order by created_date').fetchall();db.close()
    return [(datetime.datetime.fromtimestamp(r[0]//1000,datetime.timezone.utc),datetime.datetime.fromtimestamp(r[1]//1000,datetime.timezone.utc),'','',r[4],r[5],'Text (0)','Active (0)','Normal (0)','None (0)',r[10],r[11],'','',r[14],str(path.relative_to(root))) for r in raw]


class StoredEncryptedTest(unittest.TestCase):
    def test_native_storage_types_and_repeat_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory)
            for i,affinity in enumerate(['','INTEGER']):
                path,_=fixture(root/str(i),affinity=affinity);_,rows,_=colorNote.colornote_notes.__wrapped__(context(root,[path]));expected=oracle(root,path)
                self.assertEqual(rows,expected);self.assertEqual(len(rows),13);self.assertEqual([[type(v) for v in r] for r in rows],[[type(v) for v in r] for r in expected]);self.assertIsNone(rows[0][11]);self.assertEqual(rows[1][11],0);self.assertEqual(rows[-1],rows[1])

    def test_live_wal_copied_effective_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);path,db=fixture(root/'writer',True,'INTEGER')
            try:
                working=root/'working';shutil.copytree(root/'writer',working);target=working/path.relative_to(root/'writer');self.assertGreater(pathlib.Path(str(target)+'-wal').stat().st_size,32)
                _,rows,_=colorNote.colornote_notes.__wrapped__(context(working,[pathlib.Path(str(target)+'-wal'),target]));self.assertEqual(rows,oracle(working,target));self.assertEqual(len(rows),13)
                main=root/'main-only';shutil.copyfile(path,main);conn=sqlite3.connect(main);self.assertEqual(conn.execute('select count(*) from notes').fetchone()[0],0);conn.close()
            finally:db.close()


if __name__=='__main__':unittest.main()
