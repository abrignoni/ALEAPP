"""Contributing databases carry row provenance without inferred user ownership."""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.chromeNetworkActionPredictor import get_chromeNetworkActionPredictor


def make_db(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path)
    db.execute('CREATE TABLE network_action_predictor(user_text,url,number_of_hits,number_of_misses)')
    db.executemany('INSERT INTO network_action_predictor VALUES(?,?,?,?)',rows);db.commit();db.close();return path


def make_fixture(root):
    rows=[('same','https://example.test',2,3),('same','https://example.test',2,3)]
    suffix='com.android.chrome/app_chrome/Default/Network Action Predictor'
    first=make_db(root/'data/data'/suffix,rows)
    second=make_db(root/'data/user/10'/suffix,rows+[('other','https://other.test',0,1)])
    unknown=make_db(root/'unknown/data/data'/suffix,[('unknown','https://unknown.test',1,0)])
    empty=make_db(root/'empty/data/data'/suffix,[])
    return [first,second,unknown,empty]


class PredictorRowSourcesTest(unittest.TestCase):
    def test_combined_repeats_unknown_namespace_and_empty_last(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);files=make_fixture(root)
            headers,rows,sources=get_chromeNetworkActionPredictor.__wrapped__(context(root,files))
            self.assertEqual(headers[-1],'Source File');self.assertEqual(len(rows),6)
            self.assertEqual(rows[0],rows[1]);self.assertEqual(sources.splitlines(),list(map(str,files[:3])))
            self.assertEqual([r[-1] for r in rows],[str(files[0].relative_to(root))]*2+[str(files[1].relative_to(root))]*3+[str(files[2].relative_to(root))])
            for path in files[:3]:
                db=sqlite3.connect(path);expected=db.execute('SELECT * FROM network_action_predictor').fetchall();db.close()
                self.assertEqual([r[:4] for r in rows if r[-1]==str(path.relative_to(root))],expected)
            headers,rows,sources=get_chromeNetworkActionPredictor.__wrapped__(context(root,[files[0],files[3]]))
            self.assertNotIn('Source File',headers);self.assertEqual(sources,str(files[0]));self.assertEqual(len(rows),2)

    def test_actual_wal_sidecars_existing_alias_and_failed_last(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);path=make_db(root/'data/data/com.android.chrome/app_chrome/Default/Network Action Predictor',[])
            db=sqlite3.connect(path);db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0');db.execute('INSERT INTO network_action_predictor VALUES(?,?,?,?)',('wal','https://wal.test',8,9));db.commit()
            alias=root/'data/user/0/com.android.chrome/app_chrome/Default/Network Action Predictor';alias.parent.mkdir(parents=True,exist_ok=True)
            for suffix in ['', '-wal','-shm']:shutil.copy2(str(path)+suffix,str(alias)+suffix)
            bad=root/'failed/Network Action Predictor';bad.parent.mkdir(parents=True);sqlite3.connect(bad).close()
            with patch('scripts.artifacts.chromeNetworkActionPredictor.logfunc'):
                headers,rows,sources=get_chromeNetworkActionPredictor.__wrapped__(context(root,[pathlib.Path(str(path)+'-wal'),alias,path,bad]))
            self.assertNotIn('Source File',headers);self.assertEqual(rows[0][:4],('wal','https://wal.test',8,9));self.assertEqual(len(rows),1);self.assertEqual(sources,str(path));db.close()

if __name__=='__main__':
    unittest.main()
