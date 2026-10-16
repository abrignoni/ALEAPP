"""Exercise both cache branches against stored SQLite URL values."""
import pathlib
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from scripts.artifacts.Grok import grok_generatedvideos

URLS = ['https://assets.grok.com/users/a/video', 'https://assets.grok.com/public/video',
        'https://assets.grok.com/users-lookalike/video', 'HTTPS://assets.grok.com/users/a',
        'https://other.test/users/a', '', None]

def create_grok_fixture(root, media=b'constructed cache bytes', empty=False):
    root = pathlib.Path(root)
    main = root / 'data/data/ai.x.grok/databases/exoplayer_internal.db'
    main.parent.mkdir(parents=True, exist_ok=True)
    cache = root / 'data/data/ai.x.grok/cache/test/video-cache/test'
    cache.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(main)
    con.execute('CREATE TABLE ExoPlayerCacheFileMetadata_test(name, length, last_touch_timestamp)')
    con.execute('CREATE TABLE ExoPlayerCacheIndex_test(id, key)')
    files = [main]
    if not empty:
        for index, url in enumerate(URLS):
            for physical in (True, False):
                identity = index * 2 + int(not physical)
                name = str(identity) + '.0.1700000000000.v3.exo'
                con.execute('INSERT INTO ExoPlayerCacheFileMetadata_test VALUES (?, ?, ?)', (name, len(media), 1700000001000))
                con.execute('INSERT INTO ExoPlayerCacheIndex_test VALUES (?, ?)', (identity, url))
                if physical:
                    target = cache / name
                    target.write_bytes(media)
                    files.append(target)
    con.commit()
    con.close()
    return files

class GrokURLPrefixTest(unittest.TestCase):
    def test_present_and_missing_url_boundaries_preserve_raw_urls(self):
        with tempfile.TemporaryDirectory() as folder:
            files = create_grok_fixture(folder)
            context = SimpleNamespace(get_files_found=lambda: files,
                                      get_relative_path=lambda path: str(pathlib.Path(path).relative_to(folder)))
            with patch('scripts.artifacts.Grok.check_in_media', side_effect=lambda path, _name: str(path)):
                headers, rows, _ = grok_generatedvideos.__wrapped__(context)
            labels = [h[0] if isinstance(h, tuple) else h for h in headers]
            mapped = [dict(zip(labels, row)) for row in rows]
            self.assertEqual(len(mapped), 14)
            for index, url in enumerate(URLS):
                expected = 'Matched' if index == 0 else 'Not matched' if url else ''
                matches = [row for row in mapped if int(row['File Name'].split('.')[0]) in (index * 2, index * 2 + 1)]
                self.assertEqual(len(matches), 2)
                self.assertEqual({row['Cache Video'] for row in matches}, {'Present', 'Not Present'})
                for row in matches:
                    self.assertEqual(row['Original URL'], url or '')
                    self.assertEqual(row['Users URL Prefix Match'], expected)

    def test_empty_cache_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            files = create_grok_fixture(folder, empty=True)
            context = SimpleNamespace(get_files_found=lambda: files)
            _, rows, _ = grok_generatedvideos.__wrapped__(context)
            self.assertEqual(rows, [])
