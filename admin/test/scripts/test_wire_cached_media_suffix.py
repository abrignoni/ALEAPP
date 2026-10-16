"""Actual media registration preserves bytes and separates suffix from MIME and reuse."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts import ilapfuncs, lavafuncs
from scripts.artifacts.wireMessenger import get_wire_cached_files
from scripts.context import Context
from scripts.filetype import guess_mime
from scripts.search_files import FileInfo


class WireCachedMediaSuffixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / 'data'
        for folder in (self.data, self.root / 'media', self.root / '_HTML/media'):
            folder.mkdir(parents=True)
        lavafuncs.initialize_lava(str(self.data), str(self.root), 'fs')
        Context.clear()
        Context.set_output_params(SimpleNamespace(
            media_folder=str(self.root / 'media'), html_media_folder=str(self.root / '_HTML/media'),
            data_folder=str(self.data), output_folder_base=str(self.root)))
        Context.set_data_folder(str(self.data))
        Context.set_module_name('wireMessenger')
        Context.set_artifact_name('Wire Cached Files')

    def tearDown(self):
        lavafuncs.lava_db.close()
        lavafuncs.lava_db = None
        Context.clear()
        self.temp.cleanup()

    def run_case(self, payload, reuse=None):
        relative = 'data/data/com.wire/cache/wire.com/account/item'
        path = self.data / relative
        path.parent.mkdir(parents=True)
        path.write_bytes(payload)
        Context.set_files_found([str(path), str(path)])
        Context.set_seeker(SimpleNamespace(file_infos={str(path): FileInfo(relative, 0, 0)}))
        if reuse:
            ilapfuncs.check_in_media(str(path), 'item' if reuse == 'reference' else 'earlier-name',
                                    force_extension='mp4')
        headers, rows, source = get_wire_cached_files.__wrapped__(Context)
        self.assertEqual(4, len(headers))
        self.assertEqual(1, len(rows))
        self.assertEqual(('item', 'account', relative), (rows[0][0], rows[0][2], rows[0][3]))
        self.assertEqual(str(path), source)
        item = lavafuncs.lava_db.execute(
            'SELECT id, source_path, extraction_path, type FROM _lava_media_items').fetchone()
        self.assertEqual(hashlib.sha1(relative.encode()).hexdigest(), item[0])
        self.assertEqual(relative, item[1])
        self.assertEqual(guess_mime(payload), item[3])
        self.assertEqual(payload, (self.root / item[2]).read_bytes())
        self.assertEqual(payload, (self.root / '_HTML' / item[2]).read_bytes())
        self.assertEqual([('ok',)], lavafuncs.lava_db.execute('PRAGMA integrity_check').fetchall())
        self.assertEqual([('ok',)], lavafuncs.lava_db.execute('PRAGMA quick_check').fetchall())
        self.assertIsInstance(rows[0][1], str)
        return item[2]

    def test_ftyp_candidate_uses_generic_suffix_without_altering_bytes_or_mime(self):
        self.assertTrue(self.run_case(b'\x00\x00\x00\x14ftypisom\x00\x00\x00\x00isom').endswith('.bin'))

    def test_existing_reference_keeps_registered_suffix(self):
        self.assertTrue(self.run_case(b'\x00\x00\x00\x14ftypisom\x00\x00\x00\x00isom', 'reference').endswith('.mp4'))

    def test_existing_item_with_new_reference_keeps_registered_suffix(self):
        self.assertTrue(self.run_case(b'\x00\x00\x00\x14ftypisom\x00\x00\x00\x00isom', 'item').endswith('.mp4'))

    def test_png_prefix_precedes_ftyp_marker(self):
        self.assertTrue(self.run_case(b'\x89PNGftyp').endswith('.png'))


if __name__ == '__main__':
    unittest.main()
