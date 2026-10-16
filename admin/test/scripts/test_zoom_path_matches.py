"""Exercise retained filesystem candidate occurrences and unchanged store counters."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from scripts.artifacts import zoom


class TestZoomPathMatches(unittest.TestCase):
    def context(self, root, entries):
        paths = []
        for rel, data in entries:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            paths.append(str(path))
        return SimpleNamespace(get_files_found=lambda: paths,
                               get_relative_path=lambda p: str(Path(p).relative_to(root)))

    def test_all_occurrences_and_magic_counters(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prefix = 'data/data/us.zoom.videomeetings/'
            relative = prefix + 'data/a@xmpp.zoom.us/a@xmpp.zoom.us+b@xmpp.zoom.us.enc.db'
            context = self.context(root, [(relative, b'not sqlite'),
                                         (prefix + 'data/sqlite.enc.db', b'SQLite format 3\x00'),
                                         (prefix + 'data/empty.enc.db', b''),
                                         (prefix + 'shared_prefs/enc_x.xml', b'<map/>')])
            headers, rows, source = zoom.zoom_account.__wrapped__(context)
            self.assertEqual(len(headers), 5)
            self.assertEqual(rows[0][0:3], ('a@xmpp.zoom.us', 1, 1))
            self.assertEqual(json.loads(rows[0][4]),
                             [{'match': value, 'path': relative} for value in
                              ['a@xmpp.zoom.us', 'a@xmpp.zoom.us', '+b@xmpp.zoom.us']])
            self.assertIn(relative, source)

    def test_source_caps_and_no_name_counted_row(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prefix = 'data/data/us.zoom.videomeetings/shared_prefs/'
            entries = [(prefix + f'enc_{i:02}.xml', b'x') for i in range(51)]
            context = self.context(root, entries)
            _, rows, source = zoom.zoom_account.__wrapped__(context)
            self.assertEqual(rows[0][0:3], ('', 0, 51))
            self.assertEqual(rows[0][4], '[]')
            self.assertEqual(rows[0][3], '; '.join(p for p, _ in entries[:5]))
            self.assertEqual(source, '; '.join(p for p, _ in entries[:50]))

    def test_alias_preference_and_distinct_user(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            suffix = 'us.zoom.videomeetings/data/a@xmpp.zoom.us.enc.db'
            context = self.context(root, [('data/data/' + suffix, b'old'),
                                         ('data/user/0/' + suffix, b'new'),
                                         ('data/user/10/' + suffix, b'ten')])
            _, rows, _ = zoom.zoom_account.__wrapped__(context)
            self.assertEqual(len(rows), 2)
            paths = [json.loads(row[4])[0]['path'] for row in rows]
            self.assertEqual(set(paths), {'data/data/' + suffix, 'data/user/10/' + suffix})


if __name__ == '__main__':
    unittest.main()
