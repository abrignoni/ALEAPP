"""groupMe: the database is chosen by name and storage location, never by file order.

The paths glob matches groupme.db and its -journal, -wal and -shm sidecars, and an
extraction can hold the app directory under data/data, data/user/<n> and data_mirror.
The artifacts used to open files_found[0], so a sidecar listed first was opened as the
database and a second Android user's copy was never read.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts.artifacts.groupMe import get_groupMe  # pylint: disable=wrong-import-position

SCHEMA = (
    'CREATE TABLE groups (group_id TEXT, created_at INTEGER, name TEXT, group_type TEXT, '
    'creator_user_id TEXT, message_count INTEGER, attachment_count INTEGER, '
    'last_message_created_at INTEGER, updated_at INTEGER)',
    'CREATE TABLE members (user_id TEXT, group_id TEXT, user_real_name TEXT, role TEXT)',
)


class FakeContext:
    def __init__(self, data_folder, files):
        self._data_folder = data_folder
        self._files = files

    def get_files_found(self):
        return list(self._files)

    def get_relative_path(self, full_path):
        return os.path.relpath(full_path, self._data_folder).replace(os.sep, '/')


class GroupMeStoresTest(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data, ignore_errors=True)

    def _store(self, relative_dir, groups):
        folder = os.path.join(self.data, *relative_dir.split('/'))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, 'groupme.db')
        con = sqlite3.connect(path)
        for statement in SCHEMA:
            con.execute(statement)
        for index, name in enumerate(groups):
            con.execute('INSERT INTO groups (group_id, created_at, name) VALUES (?, ?, ?)',
                        (f'g{index}', 1700000000 + index, name))
        con.commit()
        con.close()
        return path

    def _sidecar(self, path, suffix):
        # Empty, as the -journal and -wal files are on the tested images.
        with open(path + suffix, 'wb'):
            pass
        return path + suffix

    def _run(self, files):
        return get_groupMe.__wrapped__(FakeContext(self.data, files))

    def test_a_sidecar_listed_first_is_not_opened_as_the_database(self):
        store = self._store('data/data/com.groupme.android/databases', ['Synthetic Group'])
        files = [self._sidecar(store, '-wal'), self._sidecar(store, '-journal'), store]
        _, rows, source = self._run(files)
        self.assertEqual(len(rows), 1)
        self.assertEqual(source, store)

    def test_storage_views_of_one_directory_are_read_once(self):
        stores = [self._store(view + '/com.groupme.android/databases', ['Synthetic Group'])
                  for view in ('data/data', 'data/user/0', 'data_mirror/data_ce/null/0')]
        _, rows, source = self._run(list(reversed(stores)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][-1], 'data/data/com.groupme.android/databases/groupme.db')
        self.assertEqual(source, stores[0])

    def test_a_second_android_user_is_read_too(self):
        owner = self._store('data/data/com.groupme.android/databases', ['Owner Group'])
        second = self._store('data/user/10/com.groupme.android/databases', ['Second User Group'])
        headers, rows, source = self._run([second, owner])
        self.assertEqual(headers[-1], 'Source File')
        self.assertEqual(sorted(row[1] for row in rows), ['Owner Group', 'Second User Group'])
        self.assertEqual(sorted(source.split('\n')), sorted([owner, second]))


if __name__ == '__main__':
    unittest.main()
