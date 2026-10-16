"""Exercise optional Favourite values through actual SQLite schemas and WAL."""
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import megaCloud


class TestMegaCloudNullFavourite(unittest.TestCase):
    def context(self, root, files):
        return SimpleNamespace(get_files_found=lambda: files,
                               get_relative_path=lambda p: str(Path(p).relative_to(root)))

    def create(self, path, affinity=''):
        path.parent.mkdir(parents=True)
        db = sqlite3.connect(path)
        optional = '' if affinity is None else ',fav ' + affinity
        db.execute('CREATE TABLE nodes(nodehandle,parenthandle,name,type' + optional + ')')
        return db

    def test_optional_null_and_actual_affinity(self):
        values = [None, 0, 1, -1, 0.0, 0.5, '0', '', 'unknown', b'', b'0']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for affinity in [None, '', 'TEXT', 'INTEGER']:
                with self.subTest(affinity=affinity):
                    path = root / (str(affinity) or "NO_AFFINITY") / 'megaclient_statecache15_account.db'
                    db = self.create(path, affinity)
                    if affinity is None:
                        db.execute('INSERT INTO nodes VALUES(1,NULL,"node",0)')
                        null_handles, false_handles, true_handles = [1], [], []
                    else:
                        for handle, value in enumerate(values, 1):
                            db.execute('INSERT INTO nodes VALUES(?,NULL,"node",0,?)', (handle, value))
                        # Oracle observes actual stored classes after affinity, including BLOB.
                        stored = db.execute('SELECT nodehandle,fav FROM nodes').fetchall()
                        null_handles = [h for h, v in stored if v is None]
                        false_handles = [h for h, v in stored if v is not None and not v]
                        true_handles = [h for h, v in stored if v is not None and v]
                    db.commit()
                    db.close()
                    headers, rows, source = megaCloud.mega_cloud_files.__wrapped__(self.context(root, [str(path)]))
                    self.assertEqual(len(headers), 25)
                    self.assertEqual(headers[12], 'Favourite')
                    self.assertEqual([rows[h - 1][12] for h in null_handles], [''] * len(null_handles))
                    self.assertEqual([rows[h - 1][12] for h in false_handles], ['No'] * len(false_handles))
                    self.assertEqual([rows[h - 1][12] for h in true_handles], ['Yes'] * len(true_handles))
                    self.assertEqual(len(rows), 1 if affinity is None else len(values))
                    self.assertEqual(source, str(path))

    def test_live_wal_and_alias_keep_first_account_handle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'data/user/0/mega.privacy.android.app/megaclient_statecache15_account.db'
            db = self.create(path)
            try:
                db.execute('INSERT INTO nodes VALUES(1,NULL,"node",0,0)')
                db.commit()
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA wal_autocheckpoint=0')
                db.execute('UPDATE nodes SET fav=NULL')
                db.execute('INSERT INTO nodes VALUES(2,NULL,"next",0,"0")')
                db.execute('INSERT INTO nodes SELECT * FROM nodes WHERE nodehandle=2')
                db.commit()
                alias = root / 'data/data/mega.privacy.android.app/megaclient_statecache15_account.db'
                alias.parent.mkdir(parents=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(path) + suffix, str(alias) + suffix)
                headers, rows, source = megaCloud.mega_cloud_files.__wrapped__(self.context(root, [str(path), str(alias)]))
                self.assertEqual(len(headers), 25)
                self.assertEqual([row[12] for row in rows], ['', 'Yes'])
                self.assertEqual(len(rows), 2)
                self.assertEqual(source, str(alias))
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
