"""Google app SqliteKeyValueCache artifacts, run over databases built here from the layout.

The databases and the protobuf blobs in them are written by this test, so nothing in them
came from a device and the expected rows are worked out from what was written.
"""
from datetime import datetime, timezone
import fnmatch
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import googleQuickSearchboxKeyValueCache as module  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

PACKAGE = 'com.google.android.googlequicksearchbox'
ACCOUNTS = 'files/AccountData.pb'
CREATE = ('CREATE TABLE cache_table(request_data BLOB PRIMARY KEY, response_data BLOB NOT NULL, '
          'write_ms INTEGER NOT NULL, access_ms INTEGER NOT NULL, invalid_flag INTEGER NOT NULL DEFAULT 0)')


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


def account_data(entries):
    out = number(1, 4)
    for entry, kind, name in entries:
        account = block(1, 'x') + block(2, 'Display') + block(3, name) + block(7, kind)
        out += block(2, number(1, entry) + block(2, number(1, entry) + block(2, account)) + number(3, 1))
    return out


def episode_request(feed, episode_id):
    return block(1, block(2, block(1, number(1, 6) + block(2, '301')))) + block(2, block(1, (
        block(1, feed) + block(2, 'second') + block(3, episode_id) + number(5, 1))))


def episode_response(title, audio, published, episode_id, show, feed):
    episode = (block(1, title) + block(2, 'description') + block(3, audio) + number(5, 794)
               + number(7, published) + block(11, episode_id) + block(20, block(1, show) + block(7, feed)))
    return block(1, b'\x08\x01') + block(2, block(1, number(1, 1) + block(2, episode)))


def suggest_response(texts):
    return b''.join(block(1, block(1, text)) for text in texts)


LISTED = suggest_response(['alpha show', 'beta show'])
SUGGESTED = suggest_response(['server one', 'server two'])
BISTO_REQUEST = block(1, 'AA:BB:CC:DD:EE:FF') + block(2, 'en_US')
BISTO_RESPONSE = block(2, block(1, block(1, 'en-US') + block(2, 'Test Buds')))
PAGE_REQUEST = block(1, block(1, b'\x22\x00') + block(2, block(1, block(1, 'https://page.example/a') + number(5, 1))))


def utc(milliseconds):
    return datetime.fromtimestamp(milliseconds / 1000, timezone.utc)


class KeyValueCacheTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name) / 'data'
        self.files = []
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

    def database(self, relative, rows, create=CREATE):
        """A cache database holding rows of (request, response, write ms, access ms, invalid)."""
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(path))
        connection.execute(create)
        if create == CREATE:
            connection.executemany('INSERT INTO cache_table VALUES (?, ?, ?, ?, ?)', rows)
        connection.commit()
        connection.close()
        self.files.append(str(path))
        return str(path)

    def run_artifact(self, function):
        Context.set_files_found(list(self.files))
        return function.__wrapped__(Context)

    def cache(self, view, folder, name, separator=':'):
        return f'{view}/{PACKAGE}/cache/accounts/{folder}/SqliteKeyValueCache{separator}{name}.db'

    def build_owner(self, view='data/data'):
        self.put(f'{view}/{PACKAGE}/{ACCOUNTS}', account_data([(3, 'google', 'owner@example.com')]))
        self.database(self.cache(view, 3, 'SearchSuggestDataServiceCache'), [
            (block(1, 'al'), SUGGESTED, 1700000001000, 1700000001002, 0),
            (block(1, 'alpha'), b'', 1700000002000, 1700000002000, 0),
            (b'', LISTED, 1700000009000, 1700000009500, 0),
        ])
        self.database(self.cache(view, 3, 'SearchResultsDataServiceCache', separator='_'), [
            (block(1, 'Alpha Show'), bytes(300), 1700000003000, 1700000004000, 1),
        ])
        self.database(self.cache(view, 3, 'EpisodeDataCache'), [
            (episode_request('https://feed.example/rss', 'episode-1'),
             episode_response('Episode One', 'https://audio.example/1.mp3', 1699990000, 'episode-1',
                              'Alpha Show', 'https://feed.example/rss'), 1700000005000, 1700000006000, 0),
        ])
        self.database(self.cache(view, 3, 'BistoDeviceCustomizeInfoCache'), [
            (BISTO_REQUEST, BISTO_RESPONSE, 1700000007000, 1700000007000, 0),
        ])
        self.database(self.cache(view, 3, 'GoogleOnContentGwsCache2'), [
            (PAGE_REQUEST, bytes(10), 1700000008000, 1700000008000, 0),
        ])
        self.database(self.cache(view, 3, 'UnicornStatusCache'), [(b'', b'\x08\x00', 1700000000500, 1700000099000, 0)])
        self.database(self.cache(view, 3, 'SearchCatalogCache'), [])

    def test_search_requests(self):
        self.build_owner()
        headers, rows, sources = self.run_artifact(module.quicksearch_cached_search_requests)
        self.assertEqual(len(headers), 10)
        self.assertEqual(rows, [
            (utc(1700000009000), utc(1700000009500), '', 'SearchSuggestDataServiceCache', 'alpha show | beta show', len(LISTED),
             0, 'owner@example.com', '3', '0'),
            (utc(1700000003000), utc(1700000004000), 'Alpha Show', 'SearchResultsDataServiceCache', '', 300, 1,
             'owner@example.com', '3', '0'),
            (utc(1700000002000), utc(1700000002000), 'alpha', 'SearchSuggestDataServiceCache', '', 0, 0,
             'owner@example.com', '3', '0'),
            (utc(1700000001000), utc(1700000001002), 'al', 'SearchSuggestDataServiceCache', '', len(SUGGESTED), 0,
             'owner@example.com', '3', '0'),
        ])
        self.assertEqual(sorted(Path(path).name for path in sources.split('\n')), [
            'AccountData.pb', 'SqliteKeyValueCache:SearchSuggestDataServiceCache.db',
            'SqliteKeyValueCache_SearchResultsDataServiceCache.db'])

    def test_episodes(self):
        self.build_owner()
        headers, rows, _sources = self.run_artifact(module.quicksearch_cached_episodes)
        self.assertEqual(len(headers), 12)
        self.assertEqual(rows, [
            (utc(1700000005000), utc(1700000006000), utc(1699990000000), 'Episode One', 'Alpha Show', 'episode-1',
             'https://feed.example/rss', 'https://audio.example/1.mp3', 0, 'owner@example.com', '3', '0'),
        ])

    def test_other_caches(self):
        self.build_owner()
        headers, rows, sources = self.run_artifact(module.quicksearch_cached_requests)
        self.assertEqual(len(headers), 11)
        self.assertEqual(rows, [
            (utc(1700000008000), utc(1700000008000), 'GoogleOnContentGwsCache2', 'https://page.example/a', '', len(PAGE_REQUEST), 10, 0,
             'owner@example.com', '3', '0'),
            (utc(1700000007000), utc(1700000007000), 'BistoDeviceCustomizeInfoCache', 'AA:BB:CC:DD:EE:FF', 'Test Buds',
             len(BISTO_REQUEST), len(BISTO_RESPONSE), 0, 'owner@example.com', '3', '0'),
            (utc(1700000000500), utc(1700000099000), 'UnicornStatusCache', '', '', 0, 2, 0, 'owner@example.com', '3', '0'),
        ])
        # a database with no row is not named as a source
        self.assertNotIn('SearchCatalogCache', sources)

    def test_second_view_collapses_and_second_user_adds_rows(self):
        self.build_owner('data/data')
        self.build_owner('data/user/0')
        self.put(f'data/user/10/{PACKAGE}/{ACCOUNTS}', account_data([(3, 'google', 'guest@example.com')]))
        self.database(self.cache('data/user/10', 3, 'SearchResultsDataServiceCache'), [
            (block(1, 'guest query'), bytes(5), 1700000100000, 1700000100000, 0)])
        self.database('data/data/com.example.decoy/cache/accounts/3/SqliteKeyValueCache:SearchResultsDataServiceCache.db',
                      [(block(1, 'decoy'), bytes(5), 1700000200000, 1700000200000, 0)])
        _headers, rows, _sources = self.run_artifact(module.quicksearch_cached_search_requests)
        self.assertEqual([(row[2], row[7], row[9]) for row in rows], [
            ('guest query', 'guest@example.com', '10'),
            ('', 'owner@example.com', '0'),
            ('Alpha Show', 'owner@example.com', '0'),
            ('alpha', 'owner@example.com', '0'),
            ('al', 'owner@example.com', '0'),
        ])

    def test_rows_held_only_in_the_write_ahead_log_are_read(self):
        relative = self.cache('data/data', 3, 'SearchResultsDataServiceCache')
        path = self.root / relative
        path.parent.mkdir(parents=True)
        writer = sqlite3.connect(str(path))
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('PRAGMA wal_autocheckpoint=0')
        writer.execute(CREATE)
        writer.commit()
        writer.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        writer.execute('INSERT INTO cache_table VALUES (?, ?, ?, ?, ?)', (block(1, 'in the log'), b'x', 1700000000000, 1700000000000, 0))
        writer.commit()
        # copy the three files while the writer still holds them, as an extraction of a running app does
        staged = self.root / 'staged'
        for suffix in ('', '-wal', '-shm'):
            self.put(f'staged/{relative}{suffix}', Path(str(path) + suffix).read_bytes())
        writer.close()
        self.assertGreater((staged / (relative + '-wal')).stat().st_size, 0)
        alone = sqlite3.connect(f'file:{staged / relative}?immutable=1', uri=True)
        self.assertEqual(alone.execute('SELECT count(*) FROM cache_table').fetchone()[0], 0)
        alone.close()
        Context.set_data_folder(str(staged))
        _headers, rows, sources = self.run_artifact(module.quicksearch_cached_search_requests)
        self.assertEqual([row[2] for row in rows], ['in the log'])
        self.assertEqual(sources, str(staged / relative))

    def test_unreadable_databases_are_logged_and_give_no_row(self):
        self.put(self.cache('data/data', 3, 'SearchResultsDataServiceCache'), b'not a database at all, only text')
        self.database(self.cache('data/data', 4, 'SearchResultsDataServiceCache'), [], create='CREATE TABLE other(x)')
        folder = self.root / f'data/data/{PACKAGE}/cache/accounts/5'
        folder.mkdir(parents=True)
        self.files.append(str(folder))
        _headers, rows, sources = self.run_artifact(module.quicksearch_cached_search_requests)
        self.assertEqual((rows, sources), ([], ''))
        self.assertEqual(self.logged.call_count, 2)

    def test_account_list_alone_is_not_a_source(self):
        self.put(f'data/data/{PACKAGE}/{ACCOUNTS}', account_data([(3, 'google', 'owner@example.com')]))
        self.database(self.cache('data/data', 3, 'SearchCatalogCache'), [])
        for function in (module.quicksearch_cached_search_requests, module.quicksearch_cached_episodes,
                         module.quicksearch_cached_requests):
            _headers, rows, sources = self.run_artifact(function)
            self.assertEqual((rows, sources), ([], ''))

    def test_blobs_that_are_not_the_expected_messages_give_blank_text(self):
        self.database(self.cache('data/data', 3, 'EpisodeDataCache'), [(b'\xff\xff', b'\x00\x00', 0, 0, 0)])
        self.database(self.cache('data/data', 3, 'XBlendResponseCache'), [(number(1, 7), b'', 1700000000000, 1700000000000, 0)])
        _headers, rows, _sources = self.run_artifact(module.quicksearch_cached_episodes)
        self.assertEqual(rows, [('', '', '', '', '', '', '', '', 0, '', '3', '0')])
        _headers, rows, _sources = self.run_artifact(module.quicksearch_cached_requests)
        self.assertEqual([(row[2], row[3], row[5]) for row in rows], [('XBlendResponseCache', '', 2)])

    def test_declared_paths_match_the_app_and_not_a_decoy(self):
        self.build_owner()
        decoy = str(self.root / 'data/data/com.example.decoy/cache/accounts/3/SqliteKeyValueCache:EpisodeDataCache.db')
        sidecar = str(self.root / self.cache('data/data', 3, 'EpisodeDataCache')) + '-wal'
        for artifact in module.__artifacts_v2__.values():
            matched = [path for path in self.files + [decoy, sidecar]
                       if any(fnmatch.fnmatchcase('root/' + Path(path).relative_to(self.root).as_posix(), pattern)
                              for pattern in artifact['paths'])]
            self.assertEqual(sorted(matched), sorted(self.files + [sidecar]))


if __name__ == '__main__':
    unittest.main()
