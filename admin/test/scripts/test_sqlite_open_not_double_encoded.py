"""Artifacts open SQLite through open_sqlite_db_readonly with the plain path.

open_sqlite_db_readonly builds the URI itself through get_sqlite_db_path. Eight
artifacts passed it a path get_sqlite_db_path had already encoded, so it was
encoded twice: a space became %2520 and SQLite looked for a file named with a
literal %20, and on Windows the extended-length prefix was added twice. The
database then failed to open and the artifact returned nothing.

The folder below has a space and a '#' in its name, which shows the double
encoding on every platform.
"""
import ast
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import (capCut, hinge, nordVpn, payPal, revolut, threads,
                               vinted, yahooMail)

OPENERS = ('open_sqlite_db_readonly', 'attach_sqlite_db_readonly')


def make_database(path, statements):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    for statement in statements:
        con.execute(statement)
    con.commit()
    con.close()
    return str(path)


def read_marker(database):
    try:
        return database.execute('SELECT v FROM t').fetchone()[0]
    finally:
        database.close()


class OpenersTakeThePlainPath(unittest.TestCase):
    """Each artifact's opener opens a database in a folder with a space and a '#'."""

    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.root = pathlib.Path(self._folder.name) / 'case folder #1'

    def tearDown(self):
        self._folder.cleanup()

    def database(self, name):
        return make_database(self.root / 'databases' / name,
                             ['CREATE TABLE t (v TEXT)', "INSERT INTO t VALUES ('opened')"])

    def test_capcut(self):
        path = self.database('capcut.db')
        found, database = capCut._open([path], 'capcut.db')  # pylint: disable=protected-access
        self.assertEqual(found, path)
        self.assertIsNotNone(database)
        self.assertEqual(read_marker(database), 'opened')

    def test_nordvpn(self):
        path = self.database('nordvpn.db')
        found, database = nordVpn._open([path], 'nordvpn.db')  # pylint: disable=protected-access
        self.assertEqual(found, path)
        self.assertIsNotNone(database)
        self.assertEqual(read_marker(database), 'opened')

    def test_revolut(self):
        path = self.database('revolut.db')
        found, database = revolut._open([path], 'revolut.db')  # pylint: disable=protected-access
        self.assertEqual(found, path)
        self.assertIsNotNone(database)
        self.assertEqual(read_marker(database), 'opened')

    def test_threads(self):
        database = threads._open(self.database('threads.db'))  # pylint: disable=protected-access
        self.assertIsNotNone(database)
        self.assertEqual(read_marker(database), 'opened')

    def test_hinge(self):
        path = self.database(hinge._DATABASE)  # pylint: disable=protected-access
        opened = hinge._databases([path])  # pylint: disable=protected-access
        self.assertEqual([found for found, _ in opened], [path])
        self.assertIsNotNone(opened[0][1])
        self.assertEqual(read_marker(opened[0][1]), 'opened')

    def test_yahoo_mail(self):
        path = self.database(yahooMail._DATABASE)  # pylint: disable=protected-access
        opened = yahooMail._databases([path])  # pylint: disable=protected-access
        self.assertEqual([found for found, _ in opened], [path])
        self.assertIsNotNone(opened[0][1])
        self.assertEqual(read_marker(opened[0][1]), 'opened')

    def test_vinted(self):
        path = self.database(vinted._DATABASE)  # pylint: disable=protected-access
        context = SimpleNamespace(get_relative_path=lambda p: p)
        opened = vinted._databases(context, [path])  # pylint: disable=protected-access
        self.assertEqual([found for found, _ in opened], [path])
        self.assertIsNotNone(opened[0][1])
        self.assertEqual(read_marker(opened[0][1]), 'opened')

    def test_paypal(self):
        path = make_database(
            self.root / 'data' / 'data' / 'com.paypal.android.p2pmobile' / 'databases' / 'tracking',
            ['CREATE TABLE session_event (session_id TEXT, create_timestamp TEXT, '
             'api_version TEXT, is_encrypted INTEGER)',
             "INSERT INTO session_event VALUES ('s1', '2026-01-02 03:04:05', 'v1', 0)"])
        context = SimpleNamespace(
            get_files_found=lambda: [path],
            get_relative_path=lambda p: str(pathlib.Path(p).relative_to(self.root)))
        with mock.patch.object(payPal, 'logfunc'):
            _headers, rows, _source = payPal.paypal_app_sessions.__wrapped__(context)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], 's1')


class NoArtifactEncodesThePathFirst(unittest.TestCase):
    """No artifact hands open_sqlite_db_readonly a path get_sqlite_db_path already encoded."""

    def test_no_nested_get_sqlite_db_path(self):
        offenders = []
        for module in sorted((REPO_ROOT / 'scripts' / 'artifacts').glob('*.py')):
            tree = ast.parse(module.read_text(encoding='utf-8'), filename=str(module))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, 'id', getattr(node.func, 'attr', None))
                if name not in OPENERS:
                    continue
                for argument in node.args:
                    inner = getattr(argument, 'func', None)
                    if getattr(inner, 'id', getattr(inner, 'attr', None)) == 'get_sqlite_db_path':
                        offenders.append(f'{module.name}:{node.lineno}')
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
