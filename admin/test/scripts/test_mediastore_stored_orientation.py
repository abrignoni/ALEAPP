"""Native SQLite orientation values and live WAL state survive four reports."""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import emulatedSmeta

VALUES = [None, 0, 90, 180, 270, -90, 45, 360, 0.0, 90.0, 90.5,
          '0', '90', '', 'unknown', b'', b'90', b'\x00\xff', 0, 180]
COLUMNS = ('date_added date_modified datetaken _data title _display_name _size latitude longitude '
           'orientation owner_package_name bucket_display_name relative_path is_download is_favorite '
           'is_trashed referer_uri download_uri width height _id').split()
WRAPPERS = [('get_emulatedSmeta_images', 'images', 18, 10),
            ('get_emulatedSmeta_files', 'files', 20, 10),
            ('get_emulatedSmeta_videos', 'video', 18, 10),
            ('get_emulatedSmeta_files_legacy', 'files', 15, 9)]


def fixture(root, affinity='', wal=False):
    path = root/'external.db'
    db = sqlite3.connect(path)
    for table in ['images', 'files', 'video']:
        db.execute('create table '+table+'('+','.join(
            c+(' '+affinity if c == 'orientation' else '') for c in COLUMNS)+')')
        for value in ([0] if wal else VALUES):
            row = {c: '' for c in COLUMNS}
            row.update(date_added=1700000000, date_modified=1700000001,
                       datetaken=1700000000123, orientation=value)
            db.execute('insert into '+table+' values('+','.join('?' for _ in COLUMNS)+')',
                       list(row.values()))
    db.commit()
    if wal:
        db.execute('pragma journal_mode=WAL')
        db.execute('pragma wal_autocheckpoint=0')
        for table in ['images', 'files', 'video']:
            db.execute('update '+table+' set orientation=180')
            db.execute('insert into '+table+' select * from '+table)
        db.commit()
    return path, db


def check(test, root, path):
    context = SimpleNamespace(get_files_found=lambda: [str(path)],
                              get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
    with sqlite3.connect(path) as db:
        for key, table, width, index in WRAPPERS:
            # Isolate discovery only; execute the real SQL and native constructor.
            with patch.object(emulatedSmeta, '_external_dbs', return_value=[str(path)]):
                headers, rows, source = getattr(emulatedSmeta, key).__wrapped__(context)
            raw = [r[0] for r in db.execute('select orientation from '+table)]
            test.assertEqual(len(headers), width)
            test.assertEqual(headers[index], 'Orientation (As Stored)')
            test.assertEqual([r[index] for r in rows], raw)
            test.assertEqual([type(r[index]) for r in rows], [type(v) for v in raw])
            test.assertEqual(source, str(path))
            test.assertTrue(all(r[-1] == 'external.db' for r in rows))
            test.assertEqual(rows[-1][index], raw[-1])


class StoredOrientationTest(unittest.TestCase):
    def test_native_types_affinity_and_repeated_rows(self):
        for affinity in ['', 'INTEGER']:
            with tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                path, db = fixture(root, affinity)
                db.close()
                check(self, root, path)

    def test_live_wal_update_and_repeated_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            path, db = fixture(root, wal=True)
            try:
                copy = root/'copy'
                copy.mkdir()
                for suffix in ['', '-wal', '-shm']:
                    shutil.copyfile(str(path)+suffix, str(copy/'external.db')+suffix)
                check(self, copy, copy/'external.db')
                main = sqlite3.connect('file:'+str(path)+'?immutable=1', uri=True)
                self.assertEqual(main.execute('select orientation from files').fetchall(), [(0,)])
                main.close()
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
