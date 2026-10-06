"""Independent session sources retain their own timestamp correlations and IDs."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from scripts.artifacts import OperaBrowser as opera
from admin.test.scripts.test_history_doclist_all_sources import Context

FUNCTIONS=[opera.opera_tabs,opera.opera_tab_navigation]


def create_opera_fixture(root):
    root=Path(root)
    for index,prefix in enumerate(['data/data','data/user/10','OTHER/data/data']):
        folder=root/prefix/'com.opera.browser/app_opera';folder.mkdir(parents=True,exist_ok=True)
        db=sqlite3.connect(folder/'session_db')
        for sql in ['CREATE TABLE tab(tab,current_entry)','CREATE TABLE tab_order(tab,ix)',
                    'CREATE TABLE recently_closed_tab(tab,restored)',
                    'CREATE TABLE navigation_entry(tab,ix,url,virtual_url,title)']:
            db.execute(sql)
        db.executemany('INSERT INTO tab VALUES(?,?)',[(1,1),(2,None)])
        db.executemany('INSERT INTO tab_order VALUES(?,?)',[(1,2),(2,0)])
        db.execute('INSERT INTO recently_closed_tab VALUES(2,NULL)')
        db.executemany('INSERT INTO navigation_entry VALUES(?,?,?,?,?)',
                       [(1,0,'https://example.invalid/same','',prefix.encode('utf-16-le')),
                        (1,1,'https://example.invalid/same','',b't\x00i\x00t\x00l\x00e\x00'),
                        (1,1,'https://example.invalid/same','',b't\x00i\x00t\x00l\x00e\x00'),
                        (2,0,'https://example.invalid/unmatched','',None)])
        db.commit();db.close()
        if index<2:
            db=sqlite3.connect(folder/'History');db.execute('CREATE TABLE urls(url,last_visit_time)')
            db.execute('INSERT INTO urls VALUES(?,?)',('https://example.invalid/same',11644473600000000+(1700000000+index*100)*1000000));db.commit();db.close()
    source=root/'data/data/com.opera.browser/app_opera'
    alias=root/'data/user/0/com.opera.browser/app_opera';alias.mkdir(parents=True)
    for path in source.iterdir():shutil.copy2(path,alias/path.name)
    return [str(path) for path in root.rglob('*') if path.is_file()]


class TestOperaRowSources(unittest.TestCase):
    def test_sources_dates_missing_lookup_and_multiplicity(self):
        with tempfile.TemporaryDirectory() as root:
            files=create_opera_fixture(root)
            for function,count in zip(FUNCTIONS,[6,12]):
                with self.subTest(artifact=function.__name__):
                    headers,data,sources=function.__wrapped__(Context(root,files));names=[h[0] if isinstance(h,tuple) else h for h in headers];rows=[dict(zip(names,row)) for row in data]
                    self.assertEqual(len(rows),count)
                    self.assertEqual(len({row['Session Source File'] for row in rows}),3)
                    self.assertIn('Visit Time',names[0])
                    known={}
                    for row in rows:
                        source=row['Session Source File'];self.assertTrue((Path(root)/source).is_file())
                        if source.startswith('OTHER/'):
                            self.assertEqual(row['History Lookup Source File'],'')
                            self.assertIsNone(row[names[0]])
                        else:
                            self.assertTrue((Path(root)/row['History Lookup Source File']).is_file())
                            if row[names[0]] is not None:known[source]=row[names[0]]
                            if row['Internal Tab ID']==2:self.assertIsNone(row[names[0]])
                    self.assertEqual(len(set(known.values())),2)
                    self.assertEqual(len(sources.split('\n')),5)
                    if function.__name__=='opera_tabs':self.assertEqual([row['Status'] for row in rows],['Open']*3+['Closed']*3)

    def test_staging_and_empty_inputs(self):
        with tempfile.TemporaryDirectory() as root:
            files=create_opera_fixture(root)
            staged=Path(root)/'mirror-user0-stage';staged_files=[]
            for path in files:
                target=staged/Path(path).relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target);staged_files.append(str(target))
            for function in FUNCTIONS:
                self.assertEqual(function.__wrapped__(Context(root,files))[1],function.__wrapped__(Context(staged,staged_files))[1])
                self.assertEqual(function.__wrapped__(Context(root,[]))[1],[])
