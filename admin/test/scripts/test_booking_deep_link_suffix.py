"""Exercise actual preference and OkHttp source projections, without the report wrapper."""
import gzip
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from scripts.artifacts import booking


class TestBookingDeepLinkSuffix(unittest.TestCase):
    def parse(self, root, files):
        context = SimpleNamespace(
            get_files_found=lambda: [str(p) for p in files],
            get_relative_path=lambda p: str(Path(p).relative_to(root)),
        )
        return booking.booking_deep_links.__wrapped__(context)

    def prefs(self, root, text, prefix='data/user/0'):
        path = root / prefix / 'com.booking/shared_prefs/original_link_storage.xml'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_empty_suffix_retains_occurrence_and_other_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.prefs(root, '<map><string name="original_link-">link</string>'
                                   '<string name="original_link-city">second</string>'
                                   '<string name="link_action">action</string></map>')
            _, rows, source = self.parse(root, [path])
            self.assertEqual(rows, [('', 'Stored link', 'link', '', '', '', '', 'action', '',
                                     str(path.relative_to(root))),
                                    ('', 'Stored link', 'second', '', 'city', '', '', 'action', '',
                                     str(path.relative_to(root)))])
            self.assertEqual(source, str(path))

    def test_duplicate_preference_and_empty_attribute_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.prefs(root, '<map><string name="original_link-">first</string>'
                                   '<string name="original_link-">last &amp; value</string>'
                                   '<string name="original_link-ignored" value="">ignored</string>'
                                   '<set name="original_link-set"><string>A</string>'
                                   '<string>B</string></set></map>')
            _, rows, _ = self.parse(root, [path])
            self.assertEqual([(r[2], r[4], r[7]) for r in rows],
                             [('last & value', '', ''), ('A, B', 'set', '')])

    def test_gzip_resolved_fields_are_distinct_from_preference_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'data/user/0/com.booking/cache/okhttp/entry.0'
            path.parent.mkdir(parents=True)
            path.write_text('https://api/mobile.decodeUniversalLink?url=A%2BB+space&url=ignored\n'
                            'GET\n0\nHTTP/1.1 200 OK\n1\nokhttp-sent-millis: 0\n', encoding='utf-8')
            path.with_suffix('.1').write_bytes(gzip.compress(json.dumps({
                'booking_url': 0, 'dest_type': False, 'dest_id': None, 'aid': [1, None],
                'label': {'x': 'Ω'}, 'additional_parameters': {'landing_page_subheader_copy': True},
            }).encode('utf-8')))
            _, rows, source = self.parse(root, [path, path.with_suffix('.1')])
            self.assertEqual(rows, [('', 'Resolved link', 'A+B space', 0, 'False', '',
                                     '[1, null]', '{"x": "Ω"}', 'True', str(path.relative_to(root)))])
            self.assertEqual(source, str(path))

    def test_alias_rank_keeps_independent_user_occurrence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            user0 = self.prefs(root, '<map><string name="original_link-">alias</string></map>')
            preferred = self.prefs(root, '<map><string name="original_link-">preferred</string></map>', 'data/data')
            user10 = self.prefs(root, '<map><string name="original_link-">preferred</string></map>', 'data/user/10')
            _, rows, source = self.parse(root, [user0, user10, preferred])
            self.assertEqual([r[2] for r in rows], ['preferred', 'preferred'])
            self.assertEqual([r[4] for r in rows], ['', ''])
            self.assertEqual(source, str(preferred) + '\n' + str(user10))

    def test_invalid_xml_and_utf8_body_keep_existing_failure_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefs = self.prefs(root, '<map><broken>')
            meta = root / 'data/user/0/com.booking/cache/okhttp/bad.0'
            meta.parent.mkdir(parents=True)
            meta.write_bytes(b'https://api/mobile.decodeUniversalLink?url=one%2Btwo\n'
                             b'GET\n0\nHTTP/1.1 200 OK\n0\n')
            meta.with_suffix('.1').write_bytes(b'\xff')
            _, rows, source = self.parse(root, [prefs, meta, meta.with_suffix('.1')])
            self.assertEqual(rows, [('', 'Resolved link', 'one+two', '', '', '', '', '', '',
                                     str(meta.relative_to(root)))])
            self.assertEqual(source, str(meta))


if __name__ == '__main__':
    unittest.main()
