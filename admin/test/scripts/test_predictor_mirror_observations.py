"""Selected mirror inputs are source observations, without assumed duplicate identity."""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_predictor_row_sources import make_db
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.chromeNetworkActionPredictor import get_chromeNetworkActionPredictor


def make_fixture(root):
    chrome='com.android.chrome/app_chrome/Default/Network Action Predictor'
    samsung='com.sec.android.app.sbrowser/app_sbrowser/Default/Network Action Predictor'
    original=make_db(root/'data/data'/chrome,[('ordinary','https://ordinary.test',1,0)])
    mirror=make_db(root/'sbin/.magisk/mirror/data/data'/chrome,[('mirror','https://mirror.test',2,0)])
    browser=make_db(root/'sbin/.magisk/mirror/data/data'/samsung,[('browser','https://browser.test',3,0)])
    identical=root/'copy/.magisk/mirror/data/data'/chrome;identical.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,identical)
    with tempfile.TemporaryDirectory() as folder:
        staging=pathlib.Path(folder)/'wal.db';shutil.copy2(mirror,staging);db=sqlite3.connect(staging)
        db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute('INSERT INTO network_action_predictor VALUES(?,?,?,?)',('wal','https://wal.test',4,0));db.commit()
        for suffix in ['', '-wal','-shm']:shutil.copy2(str(staging)+suffix,str(mirror)+suffix)
        db.close()
    return [original,mirror,browser,identical]


class PredictorMirrorObservationsTest(unittest.TestCase):
    def test_conflicting_and_identical_mirrors_wal_and_browser_consistency(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);files=make_fixture(root)
            headers,rows,sources=get_chromeNetworkActionPredictor.__wrapped__(context(root,[pathlib.Path(str(files[1])+'-wal'),*files]))
            self.assertEqual(headers[-1],'Source File');self.assertEqual(len(rows),5)
            self.assertEqual(sources.splitlines(),list(map(str,files)))
            self.assertEqual([r[0] for r in rows],['ordinary','mirror','wal','browser','ordinary'])
            self.assertEqual(rows[0][:5],rows[-1][:5]);self.assertNotEqual(rows[0][-1],rows[-1][-1])
            self.assertEqual(rows[3][4],'Browser')
            for path in files:
                db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);expected=db.execute('SELECT * FROM network_action_predictor').fetchall();db.close()
                self.assertEqual([r[:4] for r in rows if r[-1]==str(path.relative_to(root))],expected)
            headers,rows,sources=get_chromeNetworkActionPredictor.__wrapped__(context(root,[files[1]]))
            self.assertNotIn('Source File',headers);self.assertEqual(len(rows),2);self.assertEqual(sources,str(files[1]))

    def test_host_stage_keywords_do_not_change_evidence_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);ordinary=root/'normal';keywords=root/'stage-.magisk-mirror';files=make_fixture(ordinary)
            shutil.copytree(ordinary,keywords);other=[keywords/p.relative_to(ordinary) for p in files]
            first=get_chromeNetworkActionPredictor.__wrapped__(context(ordinary,files))
            second=get_chromeNetworkActionPredictor.__wrapped__(context(keywords,other))
            self.assertEqual(first[:2],second[:2])
            self.assertEqual([str(pathlib.Path(p).relative_to(ordinary)) for p in first[2].splitlines()],
                             [str(pathlib.Path(p).relative_to(keywords)) for p in second[2].splitlines()])

if __name__=='__main__':
    unittest.main()
