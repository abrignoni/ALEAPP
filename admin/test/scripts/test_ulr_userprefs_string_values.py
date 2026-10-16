"""Actual XML coverage for direct ULR string text and attribute precedence."""
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from scripts.artifacts import ulrUserprefs


class ULRStringValueTests(unittest.TestCase):
    def parse(self, xml):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ULR_USER_PREFS.xml'
            path.write_bytes(xml.encode('utf-8'))
            context = SimpleNamespace(get_files_found=lambda: [path],
                                      get_relative_path=lambda value: Path(value).name)
            return ulrUserprefs.get_urluser.__wrapped__(context)

    def test_explicit_attributes_win_even_when_empty(self):
        _, rows, _ = self.parse('<map><string name="a" value="">ignored</string>'
                                '<string name="b" value="attr">ignored</string>'
                                '<int name="c" value="0"/></map>')
        self.assertEqual(rows, [('a', ''), ('b', 'attr'), ('c', '0')])

    def test_direct_text_is_not_stripped_or_expanded(self):
        _, rows, _ = self.parse('<map><string name="a"> 雪 &amp; text\n </string>'
                                '<string name="b">first<x>nested</x>tail</string>'
                                '<string name="c"/><string name="a">repeat</string></map>')
        self.assertEqual(rows, [('a', ' 雪 & text\n '), ('b', 'first'),
                                ('c', ''), ('a', 'repeat')])

    def test_exact_tag_and_nonstring_text_policy(self):
        headers, rows, source = self.parse('<map xmlns:x="urn:test">'
                                          '<x:string name="a">ignored</x:string>'
                                          '<int name="b">ignored</int>'
                                          '<unknown name="c" value="raw"/></map>')
        self.assertEqual(headers, ('Name', 'Value'))
        self.assertEqual(rows, [('a', ''), ('b', ''), ('c', 'raw')])
        self.assertEqual(Path(source).name, 'ULR_USER_PREFS.xml')

    def test_existing_recovery_and_xml_newline_normalization(self):
        _, rows, _ = self.parse('<map><string name="a">bare & text\x01</string></map>')
        self.assertEqual(rows, [('a', 'bare & text')])
        _, rows, _ = self.parse('\ufeff<map><string name="n">a\rb\r\nc</string></map>')
        self.assertEqual(rows, [('n', 'a\nb\nc')])

    def test_alias_rank_and_independent_user_storage_classes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = []
            for prefix, value in [('data/user/0', 'discard'), ('data/data', 'preferred'),
                                  ('data/user/10', 'user10'), ('data/user_de/0', 'DE')]:
                path = root / prefix / 'com.google.android.gms/shared_prefs/ULR_USER_PREFS.xml'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f'<map><string name="name">{value}</string></map>')
                files.append(path)
            context = SimpleNamespace(get_files_found=lambda: files + files,
                                      get_relative_path=lambda value: str(Path(value).relative_to(root)))
            _, rows, source = ulrUserprefs.get_urluser.__wrapped__(context)
            self.assertEqual(rows, [('name', 'preferred'), ('name', 'user10'), ('name', 'DE')])
            self.assertEqual(len(source.splitlines()), 3)


if __name__ == '__main__':
    unittest.main()
