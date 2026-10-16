"""Actual downloads tables retain storage types, repeats and effective WAL rows."""
import datetime
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import chrome

VALUES=[None,0,1,2,3,4,23,50,-1,999,'0','1','','unknown',0.0,1.0,0.5,b'',b'\x00\xff']


def fixture(root,wal=False,optional=True,affinity=''):
    path=root/'data/data/com.android.chrome/app_chrome/Default/History';path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    if wal:db.execute('pragma journal_mode=WAL');db.execute('pragma wal_autocheckpoint=0')
    cols=['start_time','end_time']+(['last_access_time','tab_url'] if optional else [])+['target_path','state '+affinity,'danger_type '+affinity,'interrupt_reason '+affinity,'opened','received_bytes','total_bytes']
    db.execute('create table downloads('+','.join(cols)+')');db.commit()
    if wal:db.execute('pragma wal_checkpoint(truncate)')
    for i,value in enumerate(VALUES+[VALUES[3]]):
        if i==len(VALUES):i=3
        row=[13344473600000000,13344473601000000]+([0,'https://tab/'+str(i)] if optional else [])+['/stored/'+str(i),value,value,value,[0,1,None,7][i%4],i,i+100]
        db.execute('insert into downloads values('+','.join('?' for _ in row)+')',row)
    db.commit()
    if not wal:db.close();db=None
    return path,db


def context(root,paths):
    return SimpleNamespace(get_files_found=lambda:[str(p) for p in paths],get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))


def timestamp(value):
    return '' if value in (None,0,'') else datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(microseconds=int(value))


def oracle(path):
    db=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True)
    columns={r[1] for r in db.execute('pragma table_info(downloads)')}
    last='last_access_time' if 'last_access_time' in columns else "''"
    tab='tab_url' if 'tab_url' in columns else "''"
    rows=db.execute(f"select start_time,end_time,{last},{tab},target_path,state,danger_type,interrupt_reason,CASE opened WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,received_bytes,total_bytes from downloads").fetchall();db.close()
    return [(timestamp(r[0]),timestamp(r[1]),timestamp(r[2]))+r[3:]+('Chrome',) for r in rows]


class DownloadStoredFlagsTest(unittest.TestCase):
    def test_storage_classes_optional_columns_and_repeats(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory)
            for i,(optional,affinity) in enumerate([(True,''),(False,'INTEGER')]):
                path,_=fixture(root/str(i),optional=optional,affinity=affinity)
                _,rows,source=chrome.get_chromeDownloads.__wrapped__(context(root,[path]))
                expected=oracle(path);self.assertEqual(rows,expected);self.assertEqual(len(rows),20);self.assertEqual(source,str(path))
                self.assertEqual([[type(v) for v in r] for r in rows],[[type(v) for v in r] for r in expected])
                self.assertEqual(rows[0][5:8],(None,None,None));self.assertEqual(rows[1][5:8],(0,0,0));self.assertEqual(rows[-1],rows[3])
                if not optional:self.assertEqual(rows[0][2:4],('',''))

    def test_actual_wal_effective_state_from_separate_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);path,db=fixture(root/'writer',wal=True)
            try:
                self.assertGreater(pathlib.Path(str(path)+'-wal').stat().st_size,32)
                derived=root/'working';shutil.copytree(root/'writer',derived)
                target=derived/path.relative_to(root/'writer')
                _,rows,_=chrome.get_chromeDownloads.__wrapped__(context(derived,[pathlib.Path(str(target)+'-wal'),target]))
                self.assertEqual(rows,oracle(target));self.assertEqual(len(rows),20)
                mainonly=root/'mainonly';shutil.copyfile(path,mainonly)
                conn=sqlite3.connect(mainonly);self.assertEqual(conn.execute('select count(*) from downloads').fetchone()[0],0);conn.close()
            finally:db.close()


if __name__=='__main__':unittest.main()
