"""Stored trial JSON values retain type distinctions and unchanged subscription rows."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import burnerSubscription as parser

TRIALS=[('absent',None,None),('null',None,'null'),('true',True,'true'),('false',False,'false'),
        ('zero',0,'integer'),('one',1,'integer'),('two',2,'integer'),('negative',-1,'integer'),
        ('real',1.5,'real'),('empty','','text'),('literal','null','text'),('unicode','α\ntext','text'),
        ('array',[False,None,2],'array'),('object',{'key':[True,'value']},'object'),('repeat',False,'false')]


def fixture(root,wal=False):
    path=root/'data/data/com.adhoclabs.burner/databases/burnerDatabase.db';path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path);db.execute('CREATE TABLE SubscriptionEntity(value)')
    if wal:db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
    documents=[]
    for name,value,_ in TRIALS:
        doc={'burnerIds':['stored-user'],'creationDate':1700000000000,'renewalDate':1700000001000,'sku':'sku','store':'store','state':7}
        if name!='absent':doc['trial']=value
        documents.append(doc)
    for doc in documents:db.execute('INSERT INTO SubscriptionEntity VALUES(?)',(json.dumps(doc,ensure_ascii=False),))
    for raw in ['null','[]',None]:db.execute('INSERT INTO SubscriptionEntity VALUES(?)',(raw,))
    db.commit()
    if not wal:db.close();db=None
    return path,db


def context(paths):
    return SimpleNamespace(get_files_found=lambda:[str(p) for p in paths])


class BurnerTrialFieldsTest(unittest.TestCase):
    def test_native_types_and_dates_without_row_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path,_=fixture(pathlib.Path(directory));headers,rows,source=parser.get_burnerSubscription.__wrapped__(context([path]))
            self.assertEqual(len(rows),18);self.assertEqual([h[0] for h in headers[:2]],['Timestamp','Renewal Date']);self.assertEqual(source,str(path))
            for row,(_,value,kind) in zip(rows,TRIALS):
                self.assertEqual(row[6],kind);self.assertEqual(row[2:5],('["stored-user"]','sku','store'));self.assertEqual(row[7],7)
                if kind in ['array','object']:self.assertEqual(json.loads(row[5]),value)
                elif kind in ['true','false']:
                    self.assertEqual(row[5],int(value));self.assertIs(type(row[5]),int)
                else:self.assertEqual(row[5],value);self.assertIs(type(row[5]),type(value))
            self.assertEqual([(r[5],r[6]) for r in rows[-3:]],[(None,None)]*3)
            self.assertEqual(rows[3],rows[14])

    def test_actual_wal_and_last_source_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);first,db=fixture(root/'first',True);last,_=fixture(root/'last')
            try:
                self.assertTrue(pathlib.Path(str(first)+'-wal').stat().st_size>0)
                _,rows,source=parser.get_burnerSubscription.__wrapped__(context([pathlib.Path(str(first)+'-wal'),first,last]))
                self.assertEqual(len(rows),36);self.assertEqual(rows[:18],rows[18:]);self.assertEqual(source,str(last))
            finally:db.close()


if __name__=='__main__':
    unittest.main()
