"""Actual SQLite storage classes and WAL for Joplin resource flag retention."""
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import joplin


class TestJoplinResourceRawEncryption(unittest.TestCase):
    def context(self, root, paths):
        return SimpleNamespace(get_files_found=lambda: paths,
                               get_relative_path=lambda p: str(Path(p).relative_to(root)))

    def create(self, path, affinity=''):
        path.parent.mkdir(parents=True)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE resources(created_time,updated_time,title,filename,mime,file_extension,size,ocr_text,encryption_applied ' + affinity + ',id)')
        return db

    def test_actual_affinity_and_unknown_values(self):
        values = [None, 0, 1, -1, 0.5, 1.0, '0', '1', '', 'unknown', b'', b'1', 0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for affinity in ['', 'TEXT', 'INTEGER']:
                with self.subTest(affinity=affinity):
                    path = root / (affinity or 'NONE') / 'databases' / 'joplin.sqlite'
                    db = self.create(path, affinity)
                    for value in values:
                        db.execute('INSERT INTO resources VALUES(1700000000000,1700000001000,"title","file","text/plain","txt",5,"ocr",?,"id")', (value,))
                    db.commit()
                    expected = db.execute('SELECT encryption_applied FROM resources ORDER BY created_time DESC').fetchall()
                    db.close()
                    headers, rows, source = joplin.joplin_resources.__wrapped__(self.context(root, [str(path)]))
                    self.assertEqual(headers[8], 'encryption_applied (As Stored)')
                    self.assertEqual([(r[8], type(r[8])) for r in rows], [(r[0], type(r[0])) for r in expected])
                    self.assertEqual(rows[9][8], 'unknown')
                    self.assertEqual(rows[10][8], b'')
                    self.assertIsNone(rows[0][8])
                    self.assertEqual(rows[1], rows[-1])
                    self.assertEqual(source, str(path))

    def test_live_wal_and_identical_storage_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'data/user/0/net.cozic.joplin/databases/joplin.sqlite'
            db = self.create(path)
            try:
                db.execute('INSERT INTO resources VALUES(1700000000000,1700000001000,"title","file","text/plain","txt",5,"ocr",0,"id")')
                db.commit()
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA wal_autocheckpoint=0')
                db.execute('UPDATE resources SET encryption_applied="unknown"')
                db.execute('INSERT INTO resources SELECT * FROM resources')
                db.commit()
                alias = root / 'data/data/net.cozic.joplin/databases/joplin.sqlite'
                alias.parent.mkdir(parents=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(path) + suffix, str(alias) + suffix)
                _, rows, source = joplin.joplin_resources.__wrapped__(self.context(root, [str(path), str(alias)]))
                self.assertEqual(len(rows), 2)
                self.assertEqual([r[8] for r in rows], ['unknown', 'unknown'])
                self.assertEqual(rows[0], rows[1])
                self.assertEqual(source, str(alias))
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
