"""Omnibox Shortcuts names stored match types and transitions the way Chromium stores them."""
import pathlib
import sqlite3
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.chromeShortcuts import (  # pylint: disable=wrong-import-position
    _match_type, _shortcuts_version, _transition)


class Enums(unittest.TestCase):
    def test_a_qualifier_with_the_sign_bit_prints_unsigned(self):
        # PAGE_TRANSITION_SERVER_REDIRECT (0x80000000) on TYPED, stored as a signed int32.
        self.assertEqual(_transition(-2147483647), '1 (TYPED), qualifiers 0x80000000')
        self.assertEqual(_transition(0x01000001), '1 (TYPED), qualifiers 0x01000000')
        self.assertEqual(_transition(5), '5 (GENERATED)')

    def test_pre_migration_types_take_the_migrated_name(self):
        self.assertEqual(_match_type(9, 0), '9 (SEARCH_OTHER_ENGINE, pre-migration numbering)')
        self.assertEqual(_match_type(12, 0), '12 (BOOKMARK_TITLE, pre-migration numbering)')
        self.assertEqual(_match_type(9, 1), '9 (SEARCH_SUGGEST_ENTITY)')
        self.assertEqual(_match_type(7, 0), '7 (SEARCH_HISTORY)')

    def test_version_comes_from_the_meta_table(self):
        db = sqlite3.connect(':memory:')
        self.assertEqual(_shortcuts_version(db), 0)
        db.execute('CREATE TABLE meta (key, value)')
        db.execute("INSERT INTO meta VALUES ('version', '2')")
        self.assertEqual(_shortcuts_version(db), 2)


if __name__ == '__main__':
    unittest.main()
