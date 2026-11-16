"""Pin how chromeAccounts reads Chromium Preferences and chromeReadingList reads the reading list.

Author: @AlexisBrignoni, Claude.

Every input here is synthetic. Preferences files are JSON written below with the key
names of Chromium's account_info_util.cc, signin_pref_names.cc and sync prefs; reading
list records are ReadingListLocal messages encoded by hand with the field numbers of
components/reading_list/core/proto/reading_list.proto. Expected values are written out,
never read back from the code under test.
"""
import base64
import datetime
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / 'admin' / 'test' / 'scripts'))

from scripts.artifacts import chromeAccounts, chromeReadingList  # pylint: disable=wrong-import-position
from test_chrome_sync_sessions import field, log_file, message  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
CHROME = 'data/data/com.android.chrome/app_chrome/Default'
CHROME_USER0 = 'data/user/0/com.android.chrome/app_chrome/Default'
CHROME_USER10 = 'data/user/10/com.android.chrome/app_chrome/Default'
EDGE = 'data/data/com.microsoft.emmx/app_chrome/Default'
DECOY = 'sdcard/Download/backup/app_chrome/Default'


def account(gaia, email, name='Full Name'):
    return {'account_id': gaia, 'gaia': gaia, 'email': email, 'full_name': name,
            'given_name': 'Given', 'hd': 'NO_HOSTED_DOMAIN', 'locale': 'en'}


def gaia_hash(gaia):
    return base64.b64encode(hashlib.sha256(gaia.encode()).digest()).decode()


# 2026-11-16 15:23:04 UTC in microseconds since 1601-01-01
SYNCED = str(int((datetime.datetime(2026, 11, 16, 15, 23, 4, tzinfo=UTC)
                  - datetime.datetime(1601, 1, 1, tzinfo=UTC)).total_seconds()) * 1_000_000)


def signed_in(gaia='111', email='a@example.com', per_account=True):
    prefs = {'account_info': [account(gaia, email), account('222', 'b@example.com')],
             'google': {'services': {'account_id': gaia, 'consented_to_sync': True,
                                     'last_gaia_id': gaia, 'last_username': email}},
             'sync': {'has_setup_completed': True}}
    if per_account:
        prefs['sync']['transport_data_per_account'] = {
            gaia_hash(gaia): {'sync.last_synced_time': SYNCED}}
    else:
        prefs['sync'].update({'gaia_id': gaia, 'last_synced_time': SYNCED})
    return prefs


def signed_out(gaia='111', email='a@example.com'):
    return {'account_info': [account(gaia, email)],
            'google': {'services': {'account_id': '', 'consented_to_sync': False,
                                    'last_gaia_id': gaia, 'last_username': email}},
            'sync': {}}


class AccountsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.files = []

    def tearDown(self):
        self._tmp.cleanup()

    def _prefs(self, profile, prefs):
        path = self.root / profile / 'Preferences'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(prefs))
        self.files.append(str(path))

    def _avatar(self, profile, account_id):
        path = self.root / profile / 'Accounts' / 'Avatar Images' / account_id
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'\x89PNG\r\n\x1a\n')
        self.files.append(str(path))
        return str(path)

    def _run(self):
        context = SimpleNamespace(
            get_files_found=lambda: list(self.files),
            get_relative_path=lambda p: pathlib.Path(p).relative_to(self.root).as_posix())
        with mock.patch.object(chromeAccounts, 'logfunc'), \
                mock.patch.object(chromeAccounts, 'check_in_media',
                                  side_effect=lambda path, name: f'media:{path}'):
            return chromeAccounts.chromeAccounts.__wrapped__(context)

    def test_signed_in_profile_reports_primary_consent_and_last_synced(self):
        self._prefs(CHROME, signed_in())
        avatar = self._avatar(CHROME, '111')
        headers, rows, source = self._run()
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(len(rows), 2)
        first, second = rows
        self.assertEqual(first[0], datetime.datetime(2026, 11, 16, 15, 23, 4, tzinfo=UTC))
        self.assertEqual(first[1:9], ('a@example.com', 'Full Name', 'Given', '111', 'Yes', 'Yes',
                                      'Yes', 'Yes'))
        self.assertEqual(first[11], f'media:{avatar}')
        self.assertEqual(first[12:], ('0', 'com.android.chrome', 'Default'))
        self.assertEqual(second[0], '')
        self.assertEqual(second[5:9], ('No', '', '', 'No'))
        self.assertEqual(second[11], '')
        self.assertEqual(source, str(self.root / CHROME / 'Preferences'))

    def test_older_top_level_last_synced_time_is_read_for_the_syncing_account(self):
        self._prefs(CHROME, signed_in(per_account=False))
        _headers, rows, _source = self._run()
        self.assertEqual(rows[0][0], datetime.datetime(2026, 11, 16, 15, 23, 4, tzinfo=UTC))
        self.assertEqual(rows[1][0], '')

    def test_signed_out_profile_keeps_the_entry_but_not_primary(self):
        self._prefs(CHROME, signed_out())
        _headers, rows, _source = self._run()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], '')
        self.assertEqual(rows[0][5:9], ('No', '', '', 'Yes'))

    def test_last_syncing_account_missing_from_the_list_still_gets_a_row(self):
        prefs = signed_out()
        prefs['account_info'] = []
        self._prefs(CHROME, prefs)
        _headers, rows, _source = self._run()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 'a@example.com')
        self.assertEqual(rows[0][4], '111')
        self.assertEqual(rows[0][5:9], ('No', '', '', 'Yes'))

    def test_a_profile_without_the_primary_preference_leaves_primary_blank(self):
        self._prefs(CHROME, {'account_info': [account('111', 'a@example.com')]})
        _headers, rows, _source = self._run()
        self.assertEqual(rows[0][5:9], ('', '', '', ''))

    def test_storage_views_collapse_second_user_adds_decoy_adds_nothing(self):
        self._prefs(CHROME, signed_in())
        self._prefs(CHROME_USER0, signed_in())
        self._prefs(CHROME_USER10, signed_out(gaia='333', email='c@example.com'))
        self._prefs(EDGE, signed_in(gaia='444', email='d@example.com'))
        self._prefs(DECOY, signed_in(gaia='999', email='z@example.com'))
        _headers, rows, _source = self._run()
        seen = sorted((row[12], row[13], row[4]) for row in rows)
        self.assertEqual(seen, [('0', 'com.android.chrome', '111'),
                                ('0', 'com.android.chrome', '222'),
                                ('0', 'com.microsoft.emmx', '222'),
                                ('0', 'com.microsoft.emmx', '444'),
                                ('10', 'com.android.chrome', '333')])

    def test_avatar_joins_by_profile_and_account_id_only(self):
        self._prefs(CHROME, signed_in())
        self._avatar(CHROME_USER10, '111')
        _headers, rows, _source = self._run()
        self.assertEqual(rows[0][11], '')

    def test_a_profile_with_no_account_reports_no_row_and_no_source(self):
        self._prefs(CHROME, {'google': {'services': {'signin_scoped_device_id': 'x'}}})
        _headers, rows, source = self._run()
        self.assertEqual((rows, source), ([], ''))


def reading_entry(url, title, created_us, updated_us=None, first_read_us=None, status=None):
    parts = [field(1, url), field(2, title), field(3, url), field(4, created_us)]
    if updated_us is not None:
        parts.append(field(5, updated_us))
    if status is not None:
        parts.append(field(6, status))
    if first_read_us is not None:
        parts.append(field(11, first_read_us))
    return message(*parts)


ADDED = 1_794_842_205_524_540        # 2026-11-16 15:16:45.524540 UTC, Unix microseconds
READ_AT = 1_794_842_568_688_165      # 2026-11-16 15:22:48.688165 UTC


class ReadingListTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.files = []

    def tearDown(self):
        self._tmp.cleanup()

    def _store(self, profile, records):
        folder = self.root / profile / 'Sync Data' / 'LevelDB'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / '000003.log').write_bytes(log_file(records))
        (folder / 'CURRENT').write_bytes(b'MANIFEST-000001\n')
        self.files += [str(folder / '000003.log'), str(folder / 'CURRENT')]

    def _run(self):
        context = SimpleNamespace(
            get_files_found=lambda: list(self.files),
            get_relative_path=lambda p: pathlib.Path(p).relative_to(self.root).as_posix())
        with mock.patch('scripts.artifacts.chromeSyncSessions.logfunc'):
            return chromeReadingList.chromeReadingList.__wrapped__(context)

    def test_read_entry_reports_times_and_status(self):
        url = 'https://example.com/a'
        self._store(CHROME, [
            (1, f'reading_list-dt-{url}'.encode(), reading_entry(url, 'A', ADDED, ADDED, 0, 2)),
            (2, f'reading_list-dt-{url}'.encode(),
             reading_entry(url, 'A', ADDED, READ_AT, READ_AT, 1)),
        ])
        headers, rows, _source = self._run()
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows, [(
            datetime.datetime(2026, 11, 16, 15, 16, 45, 524540, tzinfo=UTC),
            datetime.datetime(2026, 11, 16, 15, 22, 48, 688165, tzinfo=UTC),
            datetime.datetime(2026, 11, 16, 15, 22, 48, 688165, tzinfo=UTC),
            'A', url, 'READ (1)', '0', 'com.android.chrome', 'Default')])

    def test_unread_entry_has_blank_first_read_and_absent_status_is_blank(self):
        self._store(CHROME, [
            (1, b'reading_list-dt-https://example.com/u',
             reading_entry('https://example.com/u', 'U', ADDED, first_read_us=0, status=2)),
            (2, b'reading_list-dt-https://example.com/n',
             reading_entry('https://example.com/n', 'N', ADDED)),
        ])
        _headers, rows, _source = self._run()
        by_url = {row[4]: row for row in rows}
        self.assertEqual(by_url['https://example.com/u'][1], '')
        self.assertEqual(by_url['https://example.com/u'][5], 'UNSEEN (2)')
        self.assertEqual(by_url['https://example.com/n'][5], '')

    def test_deleted_entry_is_not_reported(self):
        self._store(CHROME, [
            (1, b'reading_list-dt-https://example.com/a',
             reading_entry('https://example.com/a', 'A', ADDED)),
            (2, b'reading_list-dt-https://example.com/a', None),
        ])
        _headers, rows, source = self._run()
        self.assertEqual((rows, source), ([], ''))

    def test_storage_views_collapse_and_second_user_adds_its_own(self):
        record = [(1, b'reading_list-dt-https://example.com/a',
                   reading_entry('https://example.com/a', 'A', ADDED))]
        self._store(CHROME, record)
        self._store(CHROME_USER0, record)
        self._store(CHROME_USER10, record)
        self._store(DECOY, record)
        _headers, rows, _source = self._run()
        self.assertEqual(sorted(row[6] for row in rows), ['0', '10'])


if __name__ == '__main__':
    unittest.main()
