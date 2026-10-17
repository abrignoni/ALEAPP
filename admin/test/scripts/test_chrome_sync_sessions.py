"""Pin how scripts/chromium_sync_data.py and the chromeSyncSessions artifacts read a Sync Data store.

Author: @AlexisBrignoni, Claude.

Every store here is synthetic: a LevelDB log file written by the helpers below,
whose values are protocol buffers encoded by hand with the field numbers of
Chromium's components/sync/protocol messages. The expected values are written
out, never read back from the code under test. Ported from DLEAPP's
admin/test/scripts/test_chromium_sync_data.py (abrignoni/DLEAPP#618), with
Android paths.
"""
import datetime
import pathlib
import struct
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import chromium_sync_data as sync_data  # pylint: disable=wrong-import-position
from scripts.artifacts import chromeSyncSessions  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
CHROME = 'data/data/com.android.chrome/app_chrome/Default'
CHROME_USER0 = 'data/user/0/com.android.chrome/app_chrome/Default'
CHROME_MIRROR = 'data_mirror/data_ce/null/0/com.android.chrome/app_chrome/Default'
CHROME_USER10 = 'data/user/10/com.android.chrome/app_chrome/Default'
EDGE = 'data/data/com.microsoft.emmx/app_chrome/Default'
OPERA = 'data/data/com.opera.browser/app_opera'
DECOY = 'data/data/com.example.decoy/files/app_chrome/Default'
STORE = 'Sync Data/LevelDB'


def varint(value):
    value &= (1 << 64) - 1
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    return bytes(out + bytes([value]))


def field(number, value):
    """One encoded field: an int is a varint, bytes or str length-delimited."""
    if isinstance(value, bool):
        return varint(number << 3) + varint(int(value))
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    if isinstance(value, str):
        value = value.encode('utf-8')
    return varint((number << 3) | 2) + varint(len(value)) + value


def message(*fields):
    return b''.join(fields)


def log_file(records):
    """A LevelDB log holding one write batch per (sequence, key, value) record; value None deletes."""
    out = b''
    for sequence, key, value in records:
        payload = struct.pack('<QI', sequence, 1)
        if value is None:
            payload += b'\x00' + varint(len(key)) + key
        else:
            payload += b'\x01' + varint(len(key)) + key + varint(len(value)) + value
        block = struct.pack('<IHB', 0, len(payload), 1) + payload
        out += block
    return out


def device(guid, name, updated_ms, os_type=None, version=None, old_version=None):
    parts = [field(1, guid), field(2, name), field(3, 6), field(4, 'Chrome ANDROID 1.0'),
             field(7, 'signin-' + guid), field(8, updated_ms), field(11, 'Model ' + name),
             field(12, 'Maker')]
    if old_version:
        parts.append(field(5, old_version))
    if version:
        parts.append(field(17, message(field(1, version))))
    if os_type is not None:
        parts.append(field(19, os_type))
    return message(*parts)


def header(tag, name, windows, start_ms=None):
    parts = [field(3, name), field(4, 1), field(5, 1)]
    for window_id, tabs in windows:
        parts.append(field(2, message(field(1, window_id), field(3, 1),
                                      *[field(4, tab) for tab in tabs])))
    if start_ms:
        parts.append(field(6, start_ms))
    return message(field(1, tag), field(2, message(*parts)))


def navigation(url, title, when_ms, transition=1, status=200, address_bar=True):
    return message(field(2, url), field(3, ''), field(4, title), field(6, transition),
                   field(9, when_ms), field(11, address_bar), field(20, status))


def tab(tag, node, tab_id, window_id, navigations, current, last_active_ms=None):
    parts = [field(1, tab_id), field(2, window_id), field(4, current), field(5, False)]
    parts += [field(7, nav) for nav in navigations]
    if last_active_ms:
        parts.append(field(14, last_active_ms))
    return message(field(1, tag), field(3, message(*parts)), field(4, node))


def global_metadata(guid):
    return message(field(5, guid))


def standard_records():
    """A phone's own store that also holds a desktop client's session."""
    return [
        (1, b'device_info-GlobalMetadata', global_metadata('LOCAL')),
        (2, b'sessions-GlobalMetadata', global_metadata('LOCAL')),
        (3, b'device_info-dt-LOCAL', device('LOCAL', 'Old Name', 1_600_000_000_000)),
        (9, b'device_info-dt-LOCAL', device('LOCAL', 'Phone', 1_700_000_000_000, os_type=5,
                                             version='120.0.1', old_version='119')),
        (4, b'device_info-dt-DESK', device('DESK', 'Desk', 1_690_000_000_000)),
        (5, b'device_info-dt-GONE', device('GONE', 'Gone', 1_650_000_000_000)),
        (6, b'device_info-dt-GONE', None),
        (7, b'sessions-dt-DESK-h', header('DESK', 'Desk', [(10, [20])], 1_680_000_000_000)),
        (8, b'sessions-dt-DESK-t', tab('DESK', 0, 20, 10, [
            navigation('https://example.com/a', 'A', 1_690_000_100_000),
            navigation('https://example.com/b', 'B', 1_690_000_200_000, transition=0,
                       status=404, address_bar=False)], current=1,
            last_active_ms=1_690_000_300_000)),
        (10, b'sessions-dt-NOHEADER-t', tab('DESK', 1, 21, 10, [], current=0)),
        (11, b'sessions-dt-BAD', b'\x0a\x05ab'),
        (12, b'preferences-dt-x', b'\x0a\x01x'),
    ]


class StoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.files = []

    def tearDown(self):
        self._tmp.cleanup()

    def _store(self, profile, records, name='000003.log'):
        folder = self.root / profile / STORE
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(log_file(records))
        (folder / 'CURRENT').write_bytes(b'MANIFEST-000001\n')
        self.files += [str(folder / name), str(folder / 'CURRENT')]
        return folder

    def _context(self):
        return SimpleNamespace(
            get_files_found=lambda: list(self.files),
            get_relative_path=lambda p: pathlib.Path(p).relative_to(self.root).as_posix())

    def _run(self, function):
        with mock.patch.object(chromeSyncSessions, 'logfunc'), \
                mock.patch('scripts.ilapfuncs.logfunc'):
            return getattr(chromeSyncSessions, function).__wrapped__(self._context())

    def test_only_the_newest_version_of_each_key_is_kept(self):
        folder = self._store(CHROME, standard_records())
        store = sync_data.SyncStore(str(folder))
        self.assertEqual(store.records, 12)
        self.assertEqual(store.superseded, 2)
        self.assertEqual(store.deleted, 1)
        guids = [key for _account, key, _value in store.records_of('device_info')]
        self.assertEqual(guids, ['DESK', 'LOCAL'])
        self.assertEqual(store.local_cache_guid('device_info'), 'LOCAL')
        self.assertEqual(store.local_cache_guid('send_tab_to_self'), '')

    def test_a_key_whose_newest_version_is_a_deletion_reports_nothing(self):
        self._store(CHROME, [
            (1, b'sessions-dt-DESK-t', tab('DESK', 0, 20, 10, [
                navigation('https://example.com/a', 'A', 1_690_000_100_000)], current=0)),
            (2, b'sessions-dt-DESK-t', None),
        ])
        _headers, rows, source = self._run('chrome_sync_sessions')
        self.assertEqual((rows, source), ([], ''))

    def test_an_older_version_of_a_tab_is_not_reported(self):
        self._store(CHROME, [
            (1, b'sessions-dt-DESK-t', tab('DESK', 0, 20, 10, [
                navigation('https://example.com/old', 'Old', 1_690_000_000_000)], current=0)),
            (2, b'sessions-dt-DESK-t', tab('DESK', 0, 20, 10, [
                navigation('https://example.com/new', 'New', 1_690_000_100_000)], current=0)),
        ])
        _headers, rows, _source = self._run('chrome_sync_sessions')
        self.assertEqual([row[4] for row in rows], ['https://example.com/new'])

    def test_decode_follows_the_published_field_numbers(self):
        decoded = sync_data.decode(device('G', 'Name', 1_700_000_000_000, os_type=5,
                                          version='1.2'), 'DeviceInfoSpecifics')
        self.assertEqual(decoded, {
            'cache_guid': 'G', 'client_name': 'Name', 'device_type': 6,
            'sync_user_agent': 'Chrome ANDROID 1.0', 'signin_scoped_device_id': 'signin-G',
            'last_updated_timestamp': 1_700_000_000_000, 'model': 'Model Name',
            'manufacturer': 'Maker', 'chrome_version_info': {'version_number': '1.2'},
            'os_type': 5})

    def test_a_negative_int32_reads_as_negative(self):
        self.assertEqual(sync_data.decode(field(2, -1), 'SessionWindow'),
                         {'selected_tab_index': -1})

    def test_a_wire_type_that_disagrees_with_the_schema_raises(self):
        with self.assertRaises(sync_data.ProtoError):
            sync_data.decode(field(1, 5), 'SessionSpecifics')
        with self.assertRaises(sync_data.ProtoError):
            sync_data.decode(b'\x0a\x05ab', 'SessionSpecifics')

    def test_device_info(self):
        self._store(CHROME, standard_records())
        headers, rows, source = self._run('chrome_sync_device_info')
        self.assertEqual(len(headers), len(rows[0]))
        tail = ('com.android.chrome', f'{CHROME}/{STORE}')
        self.assertEqual(rows, [
            (datetime.datetime(2023, 7, 22, 4, 26, 40, tzinfo=UTC), 'Desk', 'No', 'Maker',
             'Model Desk', '', '', 'TYPE_PHONE (6)', '', 'Chrome ANDROID 1.0', 'DESK',
             'signin-DESK') + tail,
            (datetime.datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC), 'Phone', 'Yes', 'Maker',
             'Model Phone', 'OS_TYPE_ANDROID (5)', '', 'TYPE_PHONE (6)', '120.0.1',
             'Chrome ANDROID 1.0', 'LOCAL', 'signin-LOCAL') + tail,
        ])
        self.assertEqual(source, str(self.root / CHROME / STORE))

    def test_synced_tabs_take_the_device_name_from_the_header(self):
        self._store(CHROME, standard_records())
        headers, rows, _source = self._run('chrome_sync_sessions')
        self.assertEqual(len(headers), len(rows[0]))
        tail = ('DESK', 'com.android.chrome', f'{CHROME}/{STORE}')
        self.assertEqual(rows, [
            (datetime.datetime(2023, 7, 22, 4, 28, 20, tzinfo=UTC),
             datetime.datetime(2023, 7, 22, 4, 31, 40, tzinfo=UTC), 'Desk', 'No',
             'https://example.com/a', 'A', '', 200, 'TYPED (1)', 'Yes', 0, 'No',
             'No', 20, 10) + tail,
            (datetime.datetime(2023, 7, 22, 4, 30, tzinfo=UTC),
             datetime.datetime(2023, 7, 22, 4, 31, 40, tzinfo=UTC), 'Desk', 'No',
             'https://example.com/b', 'B', '', 404, 'LINK (0)', 'No', 1, 'Yes',
             'No', 20, 10) + tail,
        ])

    def test_a_session_tag_that_is_no_listed_cache_guid_leaves_this_device_blank(self):
        self._store(CHROME, [
            (1, b'sessions-GlobalMetadata', global_metadata('LOCAL')),
            (2, b'device_info-dt-LOCAL', device('LOCAL', 'Phone', 1_700_000_000_000)),
            (3, b'sessions-dt-h', header('session_sync-OLD', 'Phone', [(10, [20])])),
            (4, b'sessions-dt-t', tab('session_sync-OLD', 0, 20, 10, [
                navigation('https://example.com/a', 'A', 1_690_000_100_000)], current=0)),
        ])
        _headers, tabs, _source = self._run('chrome_sync_sessions')
        self.assertEqual([(row[2], row[3]) for row in tabs], [('Phone', '')])
        _headers, sessions, _source = self._run('chrome_sync_devices')
        self.assertEqual([(row[1], row[2]) for row in sessions], [('Phone', '')])

    def test_session_devices(self):
        self._store(CHROME, standard_records())
        headers, rows, _source = self._run('chrome_sync_devices')
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows, [
            (datetime.datetime(2023, 3, 28, 10, 40, tzinfo=UTC), 'Desk', 'No',
             'DEVICE_FORM_FACTOR_DESKTOP (1)', 'TYPE_WIN (1)', 1, 1, 'TYPE_TABBED (1)', 'DESK',
             'com.android.chrome', f'{CHROME}/{STORE}'),
        ])

    def test_send_tab_to_self(self):
        shared = message(field(1, 'Title'), field(2, 'https://example.com/s'),
                         field(3, 13_340_000_000_000_000), field(4, 'Desk'), field(5, 'E1'),
                         field(7, 'PHONE'), field(8, True), field(9, False),
                         field(13, 13_340_000_001_000_000))
        self._store(CHROME, [
            (1, b'device_info-dt-PHONE', device('PHONE', 'Phone', 1_690_000_000_000)),
            (2, b'send_tab_to_self-dt-E1', message(field(1, shared))),
        ])
        headers, rows, _source = self._run('chrome_sync_send_tab_to_self')
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows, [
            (datetime.datetime(2023, 9, 24, 3, 33, 20, tzinfo=UTC),
             datetime.datetime(2023, 9, 24, 3, 33, 21, tzinfo=UTC), '', '', 'Title',
             'https://example.com/s', 'Desk', 'Phone', 'PHONE', 'Yes', 'No', 'E1',
             'com.android.chrome', f'{CHROME}/{STORE}'),
        ])

    def test_storage_views_collapse_a_second_user_adds_and_a_decoy_adds_nothing(self):
        # One store under three spellings of user 0's credential encrypted storage, a
        # second Android user's store with one more device, and a store with the same
        # layout inside another app's files folder.
        self._store(CHROME, standard_records())
        self._store(CHROME_USER0, standard_records())
        self._store(CHROME_MIRROR, standard_records())
        self._store(CHROME_USER10, standard_records() + [
            (13, b'device_info-dt-TABLET', device('TABLET', 'Tablet', 1_695_000_000_000))])
        self._store(DECOY, standard_records())
        _headers, rows, source = self._run('chrome_sync_device_info')
        self.assertEqual(len(rows), 2 * 2 + 1)
        self.assertEqual(sorted((row[-1], row[1]) for row in rows), [
            (f'{CHROME}/{STORE}', 'Desk'),
            (f'{CHROME}/{STORE}', 'Phone'),
            (f'{CHROME_USER10}/{STORE}', 'Desk'),
            (f'{CHROME_USER10}/{STORE}', 'Phone'),
            (f'{CHROME_USER10}/{STORE}', 'Tablet'),
        ])
        self.assertEqual(source.split('\n'), [str(self.root / CHROME / STORE),
                                              str(self.root / CHROME_USER10 / STORE)])
        _headers, tabs, _source = self._run('chrome_sync_sessions')
        self.assertEqual(len(tabs), 2 * 2)

    def test_the_preferred_view_is_read_even_when_listed_last(self):
        self._store(CHROME_MIRROR, standard_records())
        self._store(CHROME, standard_records())
        _headers, rows, _source = self._run('chrome_sync_device_info')
        self.assertEqual({row[-1] for row in rows}, {f'{CHROME}/{STORE}'})

    def test_browsers_are_named_by_package_and_opera_is_read(self):
        self._store(EDGE, [(1, b'device_info-dt-G', device('G', 'Edge Phone', 1))])
        self._store(OPERA, [(1, b'device_info-dt-H', device('H', 'Opera Phone', 1))])
        _headers, rows, _source = self._run('chrome_sync_device_info')
        self.assertEqual([(row[1], row[-2]) for row in rows], [
            ('Edge Phone', 'com.microsoft.emmx'), ('Opera Phone', 'com.opera.browser')])

    def test_a_folder_outside_a_browser_profile_is_not_read(self):
        self._store(DECOY, [(1, b'device_info-dt-G', device('G', 'Embedded', 1))])
        self._store('data/data/com.example.app/app_webview/Default',
                    [(1, b'device_info-dt-G', device('G', 'WebView', 1))])
        _headers, rows, source = self._run('chrome_sync_device_info')
        self.assertEqual((rows, source), ([], ''))


if __name__ == '__main__':
    unittest.main()
