"""Dropbox - Files reads every matched account database once per storage class and user."""
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts.dropbox import dropbox_files  # pylint: disable=wrong-import-position

COLUMNS = ('server_modified_millis', 'modified_millis', 'local_modified', 'accessed_millis',
           '_display_name', 'path', 'bytes', 'mime_type', 'is_dir', 'is_favorite',
           'shared_folder_id', 'read_only', 'is_vault_folder', 'revision')


def make_database(root, relative, name):
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute(f'CREATE TABLE dropbox({",".join(COLUMNS)})')
    con.execute('INSERT INTO dropbox VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (1700000000000, None, 0, 1700000001000, name, '/' + name, 5, 'text/plain',
                 None, 0, None, 1, 2, 'rev'))
    con.commit()
    con.close()
    return path


class DropboxFilesEveryDatabaseTest(unittest.TestCase):
    def test_two_prefixes_second_user_and_storage_alias(self):
        with tempfile.TemporaryDirectory() as root:
            base = 'com.dropbox.android/databases/'
            one = make_database(root, 'data/data/' + base + 'one-db.db', 'one')
            alias = make_database(root, 'data/user/0/' + base + 'one-db.db', 'alias')
            two = make_database(root, 'data/data/' + base + 'two-db.db', 'two')
            user = make_database(root, 'data/user/10/' + base + 'one-db.db', 'user10')
            paths = [str(one) + '-wal', str(alias), str(one), str(two), str(user)]
            headers, rows, source = dropbox_files.__wrapped__(SimpleNamespace(
                get_files_found=lambda: paths,
                get_relative_path=lambda p: str(Path(p).relative_to(root))))
            self.assertEqual(headers[0], ('Server Modified', 'datetime'))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual([r[4] for r in rows], ['one', 'two', 'user10'])
            self.assertEqual([r[-1] for r in rows],
                             [str(Path(p).relative_to(root)) for p in (one, two, user)])
            self.assertEqual(source, '\n'.join(str(p) for p in (one, two, user)))
            self.assertEqual(rows[0][8:13], (None, 0, None, 1, 2))
            self.assertEqual((rows[0][1], rows[0][2]), ('', ''))


if __name__ == '__main__':
    unittest.main()
