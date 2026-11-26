"""An expected non-read is logged in plain words, not as a database error, and only when it is
really a non-read. All files and values are made up."""
# pylint: disable=protected-access
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import hldPrivacySafe as hld
from scripts.artifacts import mega_transfers as mega


class _Cursor:
    def __init__(self, fail):
        self.fail = fail

    def execute(self, sql):
        if self.fail and sql.startswith('SELECT'):
            raise sqlite3.DatabaseError('file is not a database')
        return self

    def fetchone(self):
        return (1,)


class _Connection:
    def __init__(self, fail):
        self.fail = fail

    def cursor(self):
        return _Cursor(self.fail)

    def close(self):
        pass


class HldOpenIndex(unittest.TestCase):
    SETS = (('set one', ()), ('set two', ()))

    def _open(self, failing_sets):
        tries = iter(failing_sets)
        fake = SimpleNamespace(connect=lambda *a, **k: _Connection(next(tries)))
        with patch.object(hld, '_CIPHER_PARAMETER_SETS', self.SETS), \
                patch.object(hld, 'sqlcipher', fake, create=True), \
                patch.object(hld, 'get_sqlite_db_path', lambda p: p), \
                patch.object(hld, 'logfunc') as log:
            connection = hld._open_index('/x/privacy_safe.db')
        return connection, [c.args[0] for c in log.call_args_list]

    def test_a_set_that_fails_before_one_that_opens_is_not_logged(self):
        connection, logged = self._open([True, False])
        self.assertIsNotNone(connection)
        self.assertEqual(logged, [])

    def test_every_failure_is_logged_when_nothing_opens(self):
        connection, logged = self._open([True, True])
        self.assertIsNone(connection)
        self.assertEqual(len(logged), 2)
        self.assertTrue(all('file is not a database' in line for line in logged))


class MegaHeader(unittest.TestCase):
    def _run(self, content):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'data/data/mega.privacy.android.app/databases/megapreferences'
            path.parent.mkdir(parents=True)
            content(path)
            context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                      get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
            with patch.object(mega, 'unique_files', lambda c: [str(path)]), \
                    patch.object(mega, 'logfunc') as log:
                _headers, rows, _source = mega.get_mega_transfers.__wrapped__(context)
        return rows, [c.args[0] for c in log.call_args_list], folder

    def test_a_file_without_the_sqlite_header_is_not_read_or_called_a_database_error(self):
        rows, logged, folder = self._run(lambda p: p.write_bytes(bytes(range(256)) * 16))
        self.assertEqual(rows, [])
        self.assertEqual(len(logged), 1)
        self.assertIn('does not start with the SQLite header', logged[0])
        self.assertNotIn('file is not a database', logged[0])
        self.assertNotIn(folder, logged[0])

    def test_a_sqlite_file_that_fails_to_read_keeps_the_sqlite_error_and_a_relative_path(self):
        def make(p):
            db = sqlite3.connect(p)
            db.execute('CREATE TABLE other (x)')
            db.commit()
            db.close()
        rows, logged, folder = self._run(make)
        self.assertEqual(rows, [])
        self.assertEqual(len(logged), 1)
        self.assertIn('no such table: completedtransfers', logged[0])
        self.assertNotIn(folder, logged[0])


if __name__ == '__main__':
    unittest.main()
