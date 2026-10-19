"""userDict: every Android user's dictionary is read, once per storage location.

The provider keeps one user_dict.db per Android user, and 19 registered images (17
snapshots of one emulator and 2 phones) hold a data/user/10 copy beside user 0's. The
artifact used to open files_found[0], so every user but one was left out, and a sidecar
listed first would be opened as the database.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts.artifacts.userDict import get_userDict  # pylint: disable=wrong-import-position

PROVIDER = 'com.android.providers.userdictionary/databases'


class FakeContext:
    def __init__(self, data_folder, files):
        self._data_folder = data_folder
        self._files = files

    def get_files_found(self):
        return list(self._files)

    def get_relative_path(self, full_path):
        return os.path.relpath(full_path, self._data_folder).replace(os.sep, '/')


class UserDictStoresTest(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.data, ignore_errors=True)

    def _store(self, view, words):
        folder = os.path.join(self.data, *view.split('/'), *PROVIDER.split('/'))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, 'user_dict.db')
        con = sqlite3.connect(path)
        con.execute('CREATE TABLE words (_id INTEGER PRIMARY KEY, word TEXT, frequency INTEGER, '
                    'locale TEXT, appid INTEGER, shortcut TEXT)')
        for word in words:
            con.execute("INSERT INTO words (word, frequency, locale, appid, shortcut) "
                        "VALUES (?, 250, 'en_US', 0, NULL)", (word,))
        con.commit()
        con.close()
        return path

    def _run(self, files):
        return get_userDict.__wrapped__(FakeContext(self.data, files))

    def test_every_android_user_is_read(self):
        owner = self._store('data/data', ['syntheticone'])
        second = self._store('data/user/10', ['synthetictwo'])
        headers, rows, source = self._run([owner, second])
        self.assertEqual(headers[-1], 'Source File')
        self.assertEqual(sorted(row[0] for row in rows), ['syntheticone', 'synthetictwo'])
        self.assertEqual({row[0]: row[-1] for row in rows}['synthetictwo'],
                         f'data/user/10/{PROVIDER}/user_dict.db')
        self.assertEqual(sorted(source.split('\n')), sorted([owner, second]))

    def test_storage_views_of_one_user_are_read_once(self):
        stores = [self._store(view, ['syntheticone'])
                  for view in ('data/data', 'data/user/0', 'data_mirror/data_ce/null/0')]
        _, rows, source = self._run(list(reversed(stores)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(source, stores[0])

    def test_a_sidecar_listed_first_is_not_opened_as_the_database(self):
        store = self._store('data/data', ['syntheticone'])
        sidecar = store + '-wal'
        with open(sidecar, 'wb'):
            pass
        _, rows, source = self._run([sidecar, store])
        self.assertEqual(len(rows), 1)
        self.assertEqual(source, store)


if __name__ == '__main__':
    unittest.main()
