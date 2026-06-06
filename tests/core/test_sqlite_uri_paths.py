import argparse
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
import uuid
from contextlib import closing
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import scripts.ilapfuncs as ilapfuncs


UNC_TEST_ROOT = None


class TestSQLiteUriPaths(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix='aleapp_sqlite_uri_'))

    def tearDown(self):
        path = self._extended_path(self.test_dir) if os.name == 'nt' else self.test_dir
        shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def _extended_path(path):
        path = str(Path(path).resolve())
        if path.startswith('\\\\?\\'):
            return path
        return f'\\\\?\\{path}'

    def _create_database(self, db_path):
        with closing(sqlite3.connect(db_path)) as db:
            db.execute('CREATE TABLE sample (value TEXT)')
            db.execute("INSERT INTO sample VALUES ('expected')")
            db.commit()

    def _assert_database_can_be_opened_and_attached(self, db_path):
        db_path = str(db_path)
        db = ilapfuncs.open_sqlite_db_readonly(db_path)
        self.assertIsNotNone(db)
        try:
            self.assertEqual(
                db.execute('SELECT value FROM sample').fetchone(),
                ('expected',),
            )
        finally:
            db.close()

        with closing(sqlite3.connect(':memory:', uri=True)) as db:
            db.execute(
                ilapfuncs.attach_sqlite_db_readonly(
                    db_path,
                    'attached',
                )
            )
            self.assertEqual(
                db.execute('SELECT value FROM attached.sample').fetchone(),
                ('expected',),
            )

    def test_readonly_database_paths(self):
        folder_names = [
            'normal',
            'with spaces',
            'with#hash',
            'with%percent',
            'unicode-\u00e9',
        ]
        if os.name != 'nt':
            folder_names.append('with?question')

        for folder_name in folder_names:
            with self.subTest(folder_name=folder_name):
                db_dir = self.test_dir / folder_name
                db_dir.mkdir()
                db_path = db_dir / 'sample.db'
                self._create_database(db_path)
                self._assert_database_can_be_opened_and_attached(db_path)


    @unittest.skipUnless(os.name == 'nt', 'Windows extended-length path test')
    def test_readonly_database_long_path(self):
        db_dir = self.test_dir
        while len(str(db_dir / 'sample.db')) <= 280:
            db_dir /= 'nested_path_segment'

        Path(self._extended_path(db_dir)).mkdir(parents=True)
        db_path = self._extended_path(db_dir / 'sample.db')
        self.assertGreater(len(db_path), 260)

        self._create_database(db_path)
        self._assert_database_can_be_opened_and_attached(db_path)

    def test_readonly_database_unc_path(self):
        if os.name != 'nt':
            self.skipTest('Windows UNC path test')
        if UNC_TEST_ROOT is None:
            self.skipTest('Pass --unc-root to run the UNC integration test')

        unc_root = Path(UNC_TEST_ROOT)
        test_dir = unc_root / f'ALEAPP SQLite UNC # test {uuid.uuid4().hex}'
        db_path = test_dir / 'sample.db'

        try:
            test_dir.mkdir()
            with tempfile.TemporaryDirectory() as local_dir:
                local_db_path = Path(local_dir) / 'sample.db'
                self._create_database(local_db_path)
                db_path.write_bytes(local_db_path.read_bytes())

            self._assert_database_can_be_opened_and_attached(db_path)

            extended_unc_path = f'\\\\?\\UNC\\{str(db_path)[2:]}'
            self._assert_database_can_be_opened_and_attached(extended_unc_path)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--unc-root',
        help=r'Authenticated UNC directory for optional integration testing',
    )
    args, unittest_args = parser.parse_known_args()
    UNC_TEST_ROOT = args.unc_root
    unittest.main(argv=[sys.argv[0], *unittest_args])
