"""Actual encoded images exercise Etsy WebP detection, export routing and fallback."""
import gzip
import hashlib
import io
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.artifacts import etsy


def image_bytes(format_name, color, lossless=False):
    buffer = io.BytesIO()
    Image.new('RGB', (2, 2), color).save(buffer, format=format_name, lossless=lossless)
    return buffer.getvalue()


def create_fixture(root):
    app = root / 'CONSTRUCTED/data/data/com.etsy.android'
    cache = app / 'cache/image_manager_disk_cache'
    cache.mkdir(parents=True)
    db = app / 'databases/recentlyViewedListings'
    db.parent.mkdir()
    con = sqlite3.connect(db)
    con.execute('CREATE TABLE recentlyViewedListings(listingId INTEGER, title TEXT, imageUrl TEXT, '
                'formattedOriginalPrice TEXT, formattedDiscountedPrice TEXT, visible INTEGER, '
                'rating REAL, ratingCount INTEGER, timestamp INTEGER)')
    bodies = {}
    def put(folder, url, data):
        folder.mkdir(parents=True, exist_ok=True)
        source = folder / (hashlib.sha256(url.encode()).hexdigest() + '.0')
        source.write_bytes(data)
        bodies[str(source)] = data
    for index in range(1, 8):
        url = f'https://i.etsystatic.com/{index}/il_fullxfull.{index}.jpg'
        con.execute('INSERT INTO recentlyViewedListings VALUES (?,?,?,?,?,?,?,?,?)',
                    (index, '<test listing>', url, '$1', None, 1, 4, 2, 1767225600000 + index))
        if index == 1:
            put(cache, url, image_bytes('WEBP', 'red'))
        elif index == 2:
            put(cache, url, gzip.compress(image_bytes('WEBP', 'blue', lossless=True)))
        elif index == 3:
            put(cache, url, b'not an image' * 200)
            put(cache, url.replace('il_fullxfull', 'il_794xN'), image_bytes('JPEG', 'green'))
        elif index == 4:
            put(cache, url, b'RIFF' + (12).to_bytes(4, 'little') + b'WAVEfmt ' + b'\0' * 4)
        elif index == 5:
            put(cache, url, image_bytes('WEBP', 'yellow')[:-1])
        elif index == 6:
            put(cache, url, gzip.compress(image_bytes('JPEG', 'purple')))
        else:
            put(root / 'CONSTRUCTED/data/user/10/com.etsy.android/cache/image_manager_disk_cache',
                url, image_bytes('PNG', 'black'))
    con.commit()
    con.close()
    return [str(db), *bodies], bodies


class EtsyWebpCache(unittest.TestCase):
    def test_valid_images_compression_fallback_and_container_isolation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            files, bodies = create_fixture(root)
            context = SimpleNamespace(get_files_found=lambda: files,
                                      get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
            checked = []
            def original(source, *_args, **kwargs):
                checked.append((source, bodies[source], kwargs))
                return f'media{len(checked)}'
            def decoded(source, data, *_args, **kwargs):
                checked.append((source, data, kwargs))
                return f'media{len(checked)}'
            with patch.object(etsy, 'check_in_media', side_effect=original), \
                 patch.object(etsy, 'check_in_embedded_media', side_effect=decoded):
                _, rows, _ = etsy.etsy_recently_viewed.__wrapped__(context)
            by_id = {row[1]: row for row in rows}
            self.assertEqual(len(rows), 7)
            self.assertTrue(all(by_id[index][8] for index in (1, 2, 3, 6)))
            self.assertTrue(all(not by_id[index][8] for index in (4, 5, 7)))
            self.assertEqual(by_id[3][9], 2)
            self.assertEqual(by_id[7][9], 0)
            self.assertEqual(len(checked), 4)
            self.assertEqual([item[2]['force_type'] for item in checked].count('image/webp'), 2)
            for source, data, options in checked:
                self.assertIn(source, bodies)
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    self.assertEqual(image.format, 'WEBP' if options['force_type'] == 'image/webp' else 'JPEG')
                self.assertFalse(data.startswith(b'\x1f\x8b'))
            _, summary, _ = etsy.etsy_image_caches.__wrapped__(context)
            self.assertEqual(sum(row[3] for row in summary), 8)
            self.assertTrue(any('WEBP 2' in row[5] and 'Unrecognised 3' in row[5] for row in summary))

    def test_riff_wav_and_short_webp_headers_are_rejected(self):
        for data in (b'RIFF', b'RIFF\0\0\0\0WEBP', b'RIFF\0\0\0\0WAVEfmt '):
            self.assertEqual(etsy._sniff_image(data), ('Unrecognised', '', ''))  # pylint: disable=protected-access
        with tempfile.TemporaryDirectory() as temporary:
            source = pathlib.Path(temporary) / 'fake-cache'
            source.write_bytes(b'RIFF' + (12).to_bytes(4, 'little') + b'WEBPVP8 ' + b'\0' * 4)
            self.assertEqual(etsy._cache_image(source)[0], 'Unrecognised')  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
