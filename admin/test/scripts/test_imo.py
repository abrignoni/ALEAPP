"""IMO messages from imofriends.db and imofriends_<number>.db under both IMO packages.

The stores are built with the columns the artifact reads; the values are made up.
"""
import fnmatch
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import imo


class EvidenceContext:
    def __init__(self, root):
        self.root = root

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob('*')) if path.is_file()]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')


def friends_db(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE messages (buid TEXT, imdata TEXT, last_message TEXT, timestamp INTEGER, '
               'message_type INTEGER, message_read INTEGER)')
    db.execute('INSERT INTO messages VALUES (?, NULL, ?, 1767225600000000000, 1, 1)', ('peer', text))
    db.commit()
    db.close()


class ImoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'

    def tearDown(self):
        self.temp.cleanup()

    def test_both_packages_and_both_file_names_are_read(self):
        friends_db(self.root / 'data/data/com.imo.android.imous/databases/imofriends.db', 'old name')
        friends_db(self.root / 'data/data/com.imo.android.imoim/databases/imofriends_123.db', 'new name')
        (self.root / 'data/data/com.imo.android.imoim/databases/imofriends_123.db-journal').write_bytes(b'')
        context = EvidenceContext(self.root)
        patterns = imo.__artifacts_v2__['get_imo_messages']['paths']
        for path in context.get_files_found():
            self.assertTrue(any(fnmatch.fnmatch('root/' + context.get_relative_path(path), pattern)
                                for pattern in patterns))
        _headers, rows, source = imo.get_imo_messages.__wrapped__(context)
        self.assertEqual(sorted(row[3] for row in rows), ['new name', 'old name'])
        self.assertEqual(len(source.split('\n')), 2)
        # The same buid in two databases stays in two conversations.
        self.assertEqual(sorted(row[8] for row in rows), [
            'data/data/com.imo.android.imoim/databases/imofriends_123.db/peer',
            'data/data/com.imo.android.imous/databases/imofriends.db/peer'])

    def test_accounts_are_read_from_both_packages(self):
        for package, uid in (('com.imo.android.imous', 'u1'), ('com.imo.android.imoim', 'u2')):
            path = self.root / f'data/data/{package}/databases/accountdb.db'
            path.parent.mkdir(parents=True, exist_ok=True)
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE account (uid TEXT, name TEXT)')
            db.execute('INSERT INTO account VALUES (?, ?)', (uid, 'Name'))
            db.commit()
            db.close()
        context = EvidenceContext(self.root)
        patterns = imo.__artifacts_v2__['get_imo_account']['paths']
        for path in context.get_files_found():
            self.assertTrue(any(fnmatch.fnmatch('root/' + context.get_relative_path(path), pattern)
                                for pattern in patterns))
        _headers, rows, source = imo.get_imo_account.__wrapped__(context)
        self.assertEqual(sorted((row[0], row[2]) for row in rows), [
            ('u1', 'data/data/com.imo.android.imous/databases/accountdb.db'),
            ('u2', 'data/data/com.imo.android.imoim/databases/accountdb.db')])
        self.assertEqual(len(source.split('\n')), 2)


if __name__ == '__main__':
    unittest.main()
