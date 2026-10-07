"""Full transition storage survives SQLite coercion, joins and WAL snapshots."""
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
MASKS=[1<<i for i in range(23,32)]
VALUES=[None]+list(range(12))+[255,256]+[6|m for m in MASKS]+[6|sum(MASKS),6|0xc0000000,6|0x00100000,6|(1<<40),6|0x80000000,-2147483642,(1<<63)-1,-(1<<63),'0','6','unknown','',0.0,1.0,1.5,-0.5,b'',b'6',b'\x00\xff']
LABELS=['LINK','TYPED','AUTO_BOOKMARK','AUTO_SUBFRAME','MANUAL_SUBFRAME','GENERATED','START_PAGE','FORM_SUBMIT','RELOAD','KEYWORD','KEYWORD_GENERATED']
QUALIFIERS=['BLOCKED','FORWARD_BACK','FROM_ADDRESS_BAR','HOME_PAGE','FROM_API','CHAIN_START','CHAIN_END','CLIENT_REDIRECT','SERVER_REDIRECT']


def fixture(root,wal=False,affinity=''):
    path=root/'data/data/com.android.chrome/app_chrome/Default/History';path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path)
    if wal:db.execute('pragma journal_mode=WAL');db.execute('pragma wal_autocheckpoint=0')
    db.execute('create table urls(id,url,title)');db.execute('create table visits(id,url,visit_time,visit_duration,transition '+affinity+',from_visit)');db.commit()
    if wal:db.execute('pragma wal_checkpoint(truncate)')
    db.executemany('insert into urls values(?,?,?)',[(1,'https://fixture/one','one'),(2,'https://fixture/two','two'),(5,'https://fixture/duplicate-a','dup-a'),(5,'https://fixture/duplicate-b','dup-b')])
    rows=[(9000,1,0,0,0,None),(9001,1,None,None,1,None),(9001,2,'',1250000,2,None)]
    for i,value in enumerate(VALUES):rows.append((i+1,5 if i%7==0 else (999 if i%11==0 else 1),13344473600000000+i,1250000 if i%3 else 0,value,9001 if i%5==0 else (777 if i%13==0 else 9000)))
    rows.append(rows[4]);db.executemany('insert into visits values(?,?,?,?,?,?)',rows);db.commit()
    if not wal:db.close();db=None
    return path,db


def context(root,paths):return SimpleNamespace(get_files_found=lambda:[str(p) for p in paths],get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))


def oracle(path,browser='Chrome'):
    db=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True)
    rows=db.execute("""SELECT v.visit_time,u.url,u.title,CASE v.visit_duration WHEN 0 THEN '' ELSE strftime('%H:%M:%f',v.visit_duration/1000000.000,'unixepoch') END,v.transition,v.transition & 255,v.transition & 4294967295,parent.url FROM visits v LEFT JOIN urls u ON v.url=u.id LEFT JOIN (SELECT u.url,v.id FROM visits v LEFT JOIN urls u ON v.url=u.id) parent ON v.from_visit=parent.id""").fetchall();db.close();expected=[]
    for stamp,url,title,duration,raw,core,bits,previous in rows:
        date='' if stamp in (None,0,'') else datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(microseconds=int(stamp))
        label=LABELS[core] if core is not None and 0<=core<len(LABELS) else None
        qualifiers=', '.join(text for mask,text in zip(MASKS,QUALIFIERS) if bits is not None and bits&mask)
        expected.append((date,url,title,duration,raw,label,qualifiers,previous,browser))
    return expected


class VisitRawTransitionTest(unittest.TestCase):
    def test_typed_raw_join_fanout_and_old_interpretation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory)
            for i,affinity in enumerate(['','INTEGER']):
                path,_=fixture(root/str(i),affinity=affinity);_,rows,_=chrome.get_chromeWebVisits.__wrapped__(context(root,[path]));expected=oracle(path);self.assertEqual(rows,expected);self.assertEqual([[type(v) for v in r] for r in rows],[[type(v) for v in r] for r in expected]);self.assertGreater(len(rows),len(VALUES)+4)
                raw=[r[4] for r in rows];self.assertIn(None,raw);self.assertIn(b'\x00\xff',raw);self.assertIn(6|(1<<40),raw);self.assertIn(-(1<<63),raw)
                selected=[r for r in rows if r[4] in [6,6|0x00100000,6|(1<<40)]];self.assertTrue(all(r[5:7]==('START_PAGE','') for r in selected));self.assertGreaterEqual(len(selected),3)
                self.assertTrue(any(r[1] is None for r in rows));self.assertTrue(any(r[7] is None for r in rows))

    def test_actual_wal_effective_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);path,db=fixture(root/'writer',True,'INTEGER')
            try:
                working=root/'working';shutil.copytree(root/'writer',working);target=working/path.relative_to(root/'writer');self.assertGreater(pathlib.Path(str(target)+'-wal').stat().st_size,32);_,rows,_=chrome.get_chromeWebVisits.__wrapped__(context(working,[pathlib.Path(str(target)+'-wal'),target]));self.assertEqual(rows,oracle(target))
                main=root/'main-only';shutil.copyfile(path,main);conn=sqlite3.connect(main);self.assertEqual(conn.execute('select count(*) from visits').fetchone()[0],0);conn.close()
            finally:db.close()


if __name__=='__main__':unittest.main()
