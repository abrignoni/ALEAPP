"""Google app suggestion cache artifacts, run over files built here from the layout.

The files are written by this test's own encoder, so nothing in them came from a device and
the expected rows are worked out from what was written, not from the reader.
"""
from datetime import datetime, timezone
import fnmatch
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import googleQuickSearchboxZeroPrefix as module  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

PACKAGE = 'com.google.android.googlequicksearchbox'
CACHE = 'cache/accounts/{}/CompleteServerZeroPrefixCache.pb'
ACCOUNTS = 'files/AccountData.pb'


def varint(value):
    out = bytearray()
    while True:
        out.append((value & 0x7f) | (0x80 if value > 0x7f else 0))
        value >>= 7
        if not value:
            return bytes(out)


def number(field, value):
    return varint(field << 3) + varint(value)


def block(field, payload):
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    return varint(field << 3 | 2) + varint(len(payload)) + payload


def suggestion(text, kind, subtypes, packed=False):
    out = block(1, text)
    if kind:
        out += number(2, kind)   # a zero type is left off the wire
    if packed:
        out += block(3, b''.join(varint(value) for value in subtypes))
    else:
        out += b''.join(number(3, value) for value in subtypes)
    # fields the reader does not take, in three wire types
    return out + block(4, block(1, '<b>' + text + '</b>')) + number(9, 601) + b'\x51' + bytes(8) + b'\x5d' + bytes(4)


def cache_file(first_ms, later_ms, suggestions):
    out = number(1, first_ms) + block(3, block(1, '') + b''.join(block(2, item) for item in suggestions))
    if later_ms:
        out += number(4, later_ms)
    return out + number(5, 1)


def account_data(entries):
    """entries: [(number, type, display name, account name)]"""
    out = number(1, 4)
    for entry, kind, display, name in entries:
        account = block(1, 'x') + block(2, display) + block(3, name) + block(7, kind)
        out += block(2, number(1, entry) + block(2, number(1, entry) + block(2, account)) + number(3, 1))
    return out


def utc(milliseconds):
    return datetime.fromtimestamp(milliseconds / 1000, timezone.utc)


OWNER = [
    suggestion('first personal text', 35, [362, 39]),
    suggestion('personal entity', 46, [199, 465, 362, 39]),
    suggestion('packed personal text', 35, [362, 39], packed=True),
    suggestion('trending one', 0, [3, 143, 362]),
    suggestion('trending entity', 46, [3, 143, 362, 308]),
]
GUEST = [
    suggestion('guest personal text', 35, [362, 39]),
    suggestion('trending two', 0, [3, 143, 362]),
]
SIGNED_OUT = [suggestion('trending three', 0, [3, 143, 362]), suggestion('unknown type', 999, [362])]


class ZeroPrefixCacheTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name) / 'data'
        self.files = []
        self.decoy = ''
        Context.clear()
        Context.set_data_folder(str(self.root))
        Context.set_report_folder(str(Path(folder.name)))
        self.addCleanup(Context.set_data_folder, None)
        self.addCleanup(Context.clear)
        quiet = patch.object(module, 'logfunc')
        self.logged = quiet.start()
        self.addCleanup(quiet.stop)

    def put(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.files.append(str(path))
        return str(path)

    def run_artifact(self, function):
        Context.set_files_found(list(self.files))
        return function.__wrapped__(Context)

    def build_tree(self):
        owner_accounts = account_data([(1, 'pseudonymous', 'Signed out', ':-)'),
                                       (3, 'google', 'Owner Name', 'owner@example.com')])
        guest_accounts = account_data([(3, 'google', 'Guest Name', 'guest@example.com')])
        owner_cache = cache_file(1700000000123, 1700000600456, OWNER)
        # the same app data folder under two storage paths, which is one folder
        for view in ('data/data', 'data/user/0'):
            self.put(f'{view}/{PACKAGE}/{ACCOUNTS}', owner_accounts)
            self.put(f'{view}/{PACKAGE}/{CACHE.format(3)}', owner_cache)
            self.put(f'{view}/{PACKAGE}/{CACHE.format(1)}', cache_file(1700001000000, 0, SIGNED_OUT))
        # a second Android user with the same folder number and another account
        self.put(f'data/user/10/{PACKAGE}/{ACCOUNTS}', guest_accounts)
        self.put(f'data/user/10/{PACKAGE}/{CACHE.format(3)}', cache_file(1700002000000, 0, GUEST))
        # another package with the same layout, which the declared paths do not match
        self.decoy = str(self.root / f'data/data/com.example.decoy/{CACHE.format(3)}')

    def test_personal_rows_per_user_and_account(self):
        self.build_tree()
        headers, rows, sources = self.run_artifact(module.quicksearch_personal_suggestions)
        self.assertEqual(len(headers), 9)
        self.assertEqual(rows, [
            (utc(1700002000000), '', 'guest personal text', '35 (TYPE_PERSONALIZED_QUERY)', '362, 39', 1,
             'guest@example.com', '3', '10'),
            (utc(1700000000123), utc(1700000600456), 'first personal text', '35 (TYPE_PERSONALIZED_QUERY)',
             '362, 39', 1, 'owner@example.com', '3', '0'),
            (utc(1700000000123), utc(1700000600456), 'personal entity', '46 (TYPE_ENTITY)', '199, 465, 362, 39',
             2, 'owner@example.com', '3', '0'),
            (utc(1700000000123), utc(1700000600456), 'packed personal text', '35 (TYPE_PERSONALIZED_QUERY)',
             '362, 39', 3, 'owner@example.com', '3', '0'),
        ])
        # five files read once each: two caches and the account list of user 0, one of each for user 10
        self.assertEqual(len(sources.split('\n')), 5)
        self.assertTrue(all('/data/data/' in path or '/data/user/10/' in path for path in sources.split('\n')))

    def test_one_row_per_cache_file(self):
        self.build_tree()
        _headers, rows, _sources = self.run_artifact(module.quicksearch_suggestion_caches)
        self.assertEqual(rows, [
            (utc(1700002000000), '', 'google', 'guest@example.com', '3', '10', 2, 1),
            (utc(1700001000000), '', 'pseudonymous', ':-)', '1', '0', 2, 0),
            (utc(1700000000123), utc(1700000600456), 'google', 'owner@example.com', '3', '0', 5, 3),
        ])

    def test_unlisted_type_is_shown_as_stored_and_a_missing_type_is_zero(self):
        fields = module._wire_fields(SIGNED_OUT[1], {1, 2, 3})  # pylint: disable=protected-access
        self.assertEqual(module._type_label(fields[2][0]), '999')  # pylint: disable=protected-access
        self.assertEqual(module._type_label(None), '0 (TYPE_QUERY)')  # pylint: disable=protected-access

    def test_cache_without_an_account_list_keeps_its_rows(self):
        self.put(f'data/data/{PACKAGE}/{CACHE.format(7)}', cache_file(1700000000000, 0, GUEST))
        _headers, rows, _sources = self.run_artifact(module.quicksearch_personal_suggestions)
        self.assertEqual([(row[2], row[6], row[7], row[8]) for row in rows], [('guest personal text', '', '7', '0')])

    def test_account_list_of_another_user_is_not_borrowed(self):
        self.put(f'data/user/10/{PACKAGE}/{ACCOUNTS}', account_data([(3, 'google', 'Guest', 'guest@example.com')]))
        self.put(f'data/data/{PACKAGE}/{CACHE.format(3)}', cache_file(1700000000000, 0, GUEST))
        _headers, rows, _sources = self.run_artifact(module.quicksearch_suggestion_caches)
        self.assertEqual([(row[2], row[3], row[5]) for row in rows], [('', '', '0')])

    def test_damaged_and_empty_files_are_logged_and_skipped(self):
        good = self.put(f'data/data/{PACKAGE}/{CACHE.format(3)}', cache_file(1700000000000, 0, GUEST))
        self.put(f'data/data/{PACKAGE}/{CACHE.format(4)}', cache_file(1700000000000, 0, GUEST)[:-9] + b'\x1a\xff')
        self.put(f'data/data/{PACKAGE}/{CACHE.format(5)}', b'')
        self.put(f'data/data/{PACKAGE}/{CACHE.format(6)}', bytes(64))
        self.put(f'data/data/{PACKAGE}/{ACCOUNTS}', b'\x12\xff')
        _headers, rows, sources = self.run_artifact(module.quicksearch_suggestion_caches)
        self.assertEqual([row[4] for row in rows], ['3'])
        self.assertEqual(sources, good)
        self.assertEqual(self.logged.call_count, 4)

    def test_folders_and_other_files_give_no_rows_and_no_source(self):
        folder = self.root / f'data/data/{PACKAGE}/cache/accounts/3'
        folder.mkdir(parents=True)
        self.files.append(str(folder))
        self.put(f'data/data/{PACKAGE}/files/Other.pb', cache_file(1700000000000, 0, GUEST))
        self.put(f'data/data/com.example.decoy/{CACHE.format(3)}', cache_file(1700000000000, 0, GUEST))
        for function in (module.quicksearch_personal_suggestions, module.quicksearch_suggestion_caches):
            _headers, rows, sources = self.run_artifact(function)
            self.assertEqual((rows, sources), ([], ''))

    def test_declared_paths_match_the_app_and_not_a_decoy(self):
        self.build_tree()
        for artifact in module.__artifacts_v2__.values():
            matched = [path for path in self.files + [self.decoy]
                       if any(fnmatch.fnmatchcase('root/' + Path(path).relative_to(self.root).as_posix(), pattern)
                              for pattern in artifact['paths'])]
            self.assertEqual(sorted(matched), sorted(self.files))


if __name__ == '__main__':
    unittest.main()
