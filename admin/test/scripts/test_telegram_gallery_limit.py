"""Preference representation boundaries for the gallery limit rendering."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from scripts.artifacts.telegramAndroid import get_telegramSaveToGallery


class TestGalleryLimit(unittest.TestCase):
    def parse(self, xml):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'mainconfig.xml'
            path.write_text(xml, encoding='utf-8')
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            headers, rows, source = get_telegramSaveToGallery.__wrapped__(context)
            self.assertEqual(len(headers), 4)
            self.assertEqual(source, str(path))
            return rows

    def test_absent_limit_preserves_separate_flag_rendering(self):
        rows = self.parse('<map/>')
        self.assertEqual([r[0] for r in rows], ['Private chats', 'Groups', 'Channels'])
        self.assertEqual(rows[0][1:3], ('Not set (app default, off)',) * 2)
        self.assertEqual(rows[0][3], 'Not stored or empty (decoded value)')

    def test_empty_attribute_falls_back_to_text_and_zero_stays_text(self):
        rows = self.parse('<map><long name="user_save_gallery_limitVideo" value="">0</long>'
                          '<string name="groups_save_gallery_limitVideo"> </string></map>')
        self.assertEqual([r[3] for r in rows[:2]], ['0', ' '])

    def test_duplicate_key_last_assignment_and_legacy_cells(self):
        rows = self.parse('<map><long name="user_save_gallery_limitVideo" value="12"/>'
                          '<string name="user_save_gallery_limitVideo"/>'
                          '<boolean name="save_gallery" value="true"/></map>')
        self.assertEqual(rows[0][3], 'Not stored or empty (decoded value)')
        self.assertEqual(rows[-1], ('All chats (legacy setting)', 'Yes', '', ''))

    def test_malformed_xml_stays_caught_without_fabricated_settings(self):
        self.assertEqual(self.parse('<map><broken></map>'), [])
