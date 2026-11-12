"""GalleryVault artifacts that read one database per Android user must read every user's.

file_action_log.db is found under data/media/0/.galleryvault_DoNotDelete_<id>/backup/ on
the tested images; data/media/<n> for another user is assumed from the Android layout.
AppLock.db and cloud_cache.db sit in each user's app data directory. The artifacts used to take the first match only, so a
second user's rows were silently dropped. These tests build synthetic databases for two
users (no evidence bytes) and assert both users' rows are reported, that the
file_action_log.db.tmp found beside file_action_log.db is not read, and that cloud folder paths resolve
only within the database a row came from. Each two-user test fails on the first-match code.
"""
import os
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import galleryVault  # noqa: E402  pylint: disable=wrong-import-position

PKG = 'com.thinkyeah.galleryvault'


def _unwrap(func):
    return func.__wrapped__


class GalleryVaultEveryUserTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)
        self.files = []

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def _db(self, relative, statements):
        full = os.path.join(self.data_folder, relative)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        conn = sqlite3.connect(full)
        try:
            conn.executescript(statements)
            conn.commit()
        finally:
            conn.close()
        self.files.append(full)
        return full

    def _run(self, func):
        Context.set_files_found(list(self.files))
        return _unwrap(func)(Context)

    # file_action_log.db

    @staticmethod
    def _file_action_sql(paths):
        rows = ''.join(
            f"INSERT INTO file_action VALUES ({i + 1}, {1700000000000 + i}, 1, '{p}');"
            for i, p in enumerate(paths))
        return ('CREATE TABLE file_action (_id INTEGER PRIMARY KEY, action_time INTEGER, '
                'action_type INTEGER, file_path TEXT);' + rows)

    def _file_action_log(self, user, paths, suffix=''):
        backup = f'data/media/{user}/.galleryvault_DoNotDelete_1/backup'
        return self._db(f'{backup}/file_action_log.db{suffix}', self._file_action_sql(paths))

    def test_file_actions_reads_every_users_log(self):
        self._file_action_log(0, ['/u0/a', '/u0/b'])
        self._file_action_log(10, ['/u10/a', '/u10/b'])
        # A valid SQLite copy with rows of its own, which must not be read.
        self._file_action_log(0, ['/tmp/x'], suffix='.tmp')
        headers, rows, source_path = self._run(galleryVault.galleryvault_file_actions)

        self.assertEqual(headers[1:3], ('Android User', 'Store'))
        self.assertEqual(len(rows), 4)
        self.assertEqual({(r[1], r[2], r[4]) for r in rows},
                         {('0', 'Vault backup', '/u0/a'), ('0', 'Vault backup', '/u0/b'),
                          ('10', 'Vault backup', '/u10/a'), ('10', 'Vault backup', '/u10/b')})
        cited = source_path.split('\n')
        self.assertEqual(len(cited), 2)
        for path in cited:
            self.assertTrue(path.endswith('file_action_log.db'))

    def test_file_actions_single_user_unchanged(self):
        self._file_action_log(0, ['/u0/a'])
        _headers, rows, source_path = self._run(galleryVault.galleryvault_file_actions)
        self.assertEqual([r[4] for r in rows], ['/u0/a'])
        self.assertTrue(source_path.endswith('data/media/0/.galleryvault_DoNotDelete_1/'
                                             'backup/file_action_log.db'))

    def test_file_actions_reads_backup_and_app_database(self):
        self._file_action_log(0, ['/both/a', '/both/b'])
        self._db(f'data/data/{PKG}/databases/file_action_log.db',
                 self._file_action_sql(['/both/a', '/both/b', '/app/c', '/app/d']))
        self._file_action_log(0, ['/tmp/x'], suffix='.tmp')
        _headers, rows, source_path = self._run(galleryVault.galleryvault_file_actions)
        # Every row from both stores is kept, labelled with its store; the .tmp is not read.
        stores = sorted((r[2], r[4]) for r in rows)
        self.assertEqual(stores, [('App database', '/app/c'), ('App database', '/app/d'),
                                  ('App database', '/both/a'), ('App database', '/both/b'),
                                  ('Vault backup', '/both/a'), ('Vault backup', '/both/b')])
        self.assertEqual({r[1] for r in rows}, {'0'})
        self.assertEqual(len(source_path.split('\n')), 2)

    def test_galleryvault_db_artifacts_and_preferences_name_the_user(self):
        for view, url in (('data/data', 'https://zero.test/'), ('data/user/10', 'https://ten.test/')):
            self._db(f'{view}/{PKG}/databases/galleryvault.db',
                     'CREATE TABLE browser_history (last_visit_time_utc INTEGER, title TEXT, '
                     'url TEXT, host TEXT);'
                     f"INSERT INTO browser_history VALUES (1700000000000, 't', '{url}', 'h');")
            prefs = os.path.join(self.data_folder, f'{view}/{PKG}/shared_prefs/Kidd.xml')
            os.makedirs(os.path.dirname(prefs), exist_ok=True)
            with open(prefs, 'w', encoding='utf-8') as handle:
                handle.write("<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n"
                             f'<map><string name="launch_times">{len(url)}</string></map>')
            self.files.append(prefs)

        headers, rows, _s = self._run(galleryVault.galleryvault_browser_history)
        self.assertEqual(headers[1], 'Android User')
        self.assertEqual(sorted((r[1], r[3]) for r in rows),
                         [('0', 'https://zero.test/'), ('10', 'https://ten.test/')])

        headers, rows, source_path = self._run(galleryVault.galleryvault_preferences)
        self.assertEqual(headers[0], 'Android User')
        launches = sorted((r[0], r[2]) for r in rows if r[1] == 'Launch Count')
        self.assertEqual(launches, [('0', '18'), ('10', '17')])
        self.assertEqual(len(source_path.split('\n')), 2)

    # AppLock.db

    def _applock(self, view, package):
        return self._db(
            f'{view}/{PKG}/databases/AppLock.db',
            'CREATE TABLE locked_app (_id INTEGER PRIMARY KEY, package_name TEXT, '
            'disguise_lock INTEGER);'
            f"INSERT INTO locked_app VALUES (1, '{package}', 0);"
            'CREATE TABLE break_in_report_in_applock (_id INTEGER PRIMARY KEY, '
            'timestamp INTEGER, package_name TEXT, wrongly_attempt_code TEXT, '
            'locking_type INTEGER, photo_path TEXT, is_new INTEGER);'
            f"INSERT INTO break_in_report_in_applock VALUES "
            f"(1, 1700000000000, '{package}', '1', 1, NULL, 1);")

    def test_applock_artifacts_read_every_user(self):
        self._applock('data/data', 'pkg.zero')
        self._applock('data/user/10', 'pkg.ten')
        # A second storage view of user 0's database must not add rows.
        self._applock('data/user/0', 'pkg.zero')

        _h, rows, source_path = self._run(galleryVault.galleryvault_locked_apps)
        self.assertEqual(sorted((r[0], r[1]) for r in rows), [('0', 'pkg.zero'), ('10', 'pkg.ten')])
        self.assertEqual(len(source_path.split('\n')), 2)

        _h, rows, _s = self._run(galleryVault.galleryvault_applock_break_ins)
        self.assertEqual(sorted((r[1], r[2]) for r in rows), [('0', 'pkg.zero'), ('10', 'pkg.ten')])

    # cloud_cache.db

    def _cloud(self, view, prefix):
        # The same entry ids in both databases, so a merged folder map would resolve one
        # user's parent ids against the other user's folders.
        return self._db(
            f'{view}/{PKG}/databases/cloud_cache.db',
            'CREATE TABLE cloud_folders (entry_id INTEGER, name TEXT, parent_folder_id INTEGER, '
            'create_date_utc INTEGER, folder_uuid TEXT, files_count INTEGER, '
            'revision_id INTEGER, cloud_drive_id TEXT);'
            f"INSERT INTO cloud_folders VALUES (1, '{prefix}root', 0, 1, '{prefix}f1', 1, 1, 'd');"
            f"INSERT INTO cloud_folders VALUES (2, '{prefix}top', 1, 2, '{prefix}f2', 1, 1, 'd');"
            f"INSERT INTO cloud_folders VALUES (3, '{prefix}child', 2, 3, '{prefix}f3', 1, 1, 'd');"
            'CREATE TABLE cloud_files (file_add_time_utc INTEGER, file_org_create_time_utc INTEGER,'
            ' name TEXT, file_uuid TEXT, mime_type TEXT, size INTEGER, image_width INTEGER, '
            'image_height INTEGER, parent_folder_id INTEGER, is_complete INTEGER, '
            'has_thumb INTEGER, cloud_file_storage_key TEXT, file_encryption_key BLOB, '
            'move_to_recycle_bin_time_utc INTEGER, file_content_hash TEXT, '
            'cloud_drive_id TEXT, entry_id INTEGER);'
            f"INSERT INTO cloud_files VALUES (1, 1, '{prefix}file', '{prefix}u1', 'image/png', "
            f"1, 0, 0, 3, 1, 0, 'k', NULL, 0, 'h', 'd', 7);"
            'CREATE TABLE entry_change_history (modify_date_utc INTEGER, entry_type INTEGER, '
            'entry_uuid TEXT, change_action INTEGER, revision_id INTEGER, entry_id INTEGER, '
            'cloud_drive_id TEXT);'
            f"INSERT INTO entry_change_history VALUES (1, 2, '{prefix}u1', 1, 1, 7, 'd');"
            'CREATE TABLE user_cloud_drive (drive_provider TEXT, drive_account_id TEXT, '
            'drive_id TEXT, drive_identity_id TEXT, is_primary INTEGER, status INTEGER, '
            'space_used INTEGER, drive_storage_size INTEGER, root_folder_internal_id INTEGER);'
            f"INSERT INTO user_cloud_drive VALUES ('p', '{prefix}acct', 'd', 'i', 1, 1, 0, 0, 1);"
            'CREATE TABLE cloud_file_upload_tasks (_id INTEGER PRIMARY KEY, begin_time INTEGER, '
            'cloud_file_id INTEGER, bytes_current INTEGER, bytes_total INTEGER, state INTEGER, '
            'error_code INTEGER, cloud_file_storage_key TEXT, cloud_file_encryption_key BLOB);'
            "INSERT INTO cloud_file_upload_tasks VALUES (1, 1, 7, 0, 1, 1, 0, 'k', NULL);"
            'CREATE TABLE cloud_upload_part_tasks (cloud_file_transfer_task_id INTEGER, '
            'type INTEGER, bytes_current INTEGER, bytes_total INTEGER, error_code INTEGER);')

    def test_cloud_artifacts_read_every_user_within_their_own_database(self):
        self._cloud('data/data', 'zero-')
        self._cloud('data/user/10', 'ten-')

        _h, rows, source_path = self._run(galleryVault.galleryvault_cloud_folders)
        self.assertEqual(len(source_path.split('\n')), 2)
        self.assertEqual({r[2]: r[1] for r in rows if r[2].endswith('child')},
                         {'zero-child': '0', 'ten-child': '10'})
        parents = {r[2]: r[3] for r in rows}
        # The drive root (parent 0) is left out of paths by _cloud_folder_path.
        self.assertEqual(parents, {'zero-root': '/', 'zero-top': '/', 'zero-child': 'zero-top',
                                   'ten-root': '/', 'ten-top': '/', 'ten-child': 'ten-top'})

        _h, rows, _s = self._run(galleryVault.galleryvault_cloud_files)
        self.assertEqual({r[3]: (r[2], r[4]) for r in rows},
                         {'zero-file': ('0', 'zero-top/zero-child'),
                          'ten-file': ('10', 'ten-top/ten-child')})

        _h, rows, _s = self._run(galleryVault.galleryvault_cloud_change_history)
        self.assertEqual(sorted((r[1], r[3]) for r in rows), [('0', 'zero-file'), ('10', 'ten-file')])

        _h, rows, _s = self._run(galleryVault.galleryvault_cloud_account)
        accounts = sorted((u, v) for u, n, v in rows if n == 'Cloud Account')
        self.assertEqual(accounts, [('0', 'zero-acct'), ('10', 'ten-acct')])

        _h, rows, _s = self._run(galleryVault.galleryvault_cloud_upload_tasks)
        self.assertEqual(sorted((r[1], r[2]) for r in rows), [('0', 'zero-file'), ('10', 'ten-file')])


if __name__ == '__main__':
    unittest.main()
