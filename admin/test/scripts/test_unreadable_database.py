"""Unreadable evidence database tests.

open_sqlite_db_readonly used to return None when a database would not open,
and almost every artifact used the handle without checking it. An evidence
file that was locked, truncated or simply unreadable therefore surfaced as
"AttributeError: 'NoneType' object has no attribute 'row_factory'" further
down the module, naming neither the file nor the reason - even though the
real cause had already been logged one line earlier.

open_sqlite_db_readonly now raises SQLiteDatabaseError naming the file, and
the runner in aleapp.py logs that and skips the artifact. Helpers that probe
a database whose absence is a legitimate answer - does_table_exist_in_db and
friends - keep the tolerant behaviour through
open_sqlite_db_readonly_or_none.

These tests pin both halves: the probe helpers stay tolerant, and everything
else fails loudly enough to name the file.
"""
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.ilapfuncs import (SQLiteDatabaseError, does_column_exist_in_db,
                               does_table_exist_in_db, does_view_exist_in_db,
                               get_sqlite_db_records, open_sqlite_db_readonly,
                               open_sqlite_db_readonly_or_none)


class TestUnreadableDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = str(Path(self.temp_dir.name, 'mmssms.db'))
        db = sqlite3.connect(self.db_path)
        try:
            db.execute('CREATE TABLE sms (_id INTEGER, body TEXT)')
            db.execute("INSERT INTO sms VALUES (1, 'hello')")
            db.commit()
        finally:
            db.close()

    def _make_unreadable(self):
        '''Drop read permission, or skip where the OS does not honour that.'''
        os.chmod(self.db_path, 0o000)
        self.addCleanup(os.chmod, self.db_path, 0o600)
        if os.access(self.db_path, os.R_OK):
            # Windows ignores the mode, and root bypasses it entirely.
            self.skipTest('filesystem does not enforce the read permission here')

    # -- a database that opens is untouched by any of this --------------------

    def test_readable_database_still_opens(self):
        db = open_sqlite_db_readonly(self.db_path)
        try:
            self.assertEqual(db.execute('SELECT body FROM sms').fetchone(), ('hello',))
        finally:
            db.close()

    def test_probe_helpers_still_answer_for_a_readable_database(self):
        self.assertTrue(does_column_exist_in_db(self.db_path, 'sms', 'body'))
        self.assertFalse(does_column_exist_in_db(self.db_path, 'sms', 'not_a_column'))
        self.assertTrue(does_table_exist_in_db(self.db_path, 'sms'))
        self.assertFalse(does_table_exist_in_db(self.db_path, 'not_a_table'))
        self.assertEqual(list(get_sqlite_db_records(self.db_path, 'SELECT body FROM sms')),
                         [('hello',)])

    # -- a database that will not open ---------------------------------------

    def test_open_names_the_file_it_could_not_open(self):
        self._make_unreadable()
        with self.assertRaises(SQLiteDatabaseError) as caught:
            open_sqlite_db_readonly(self.db_path)
        self.assertIn(self.db_path, str(caught.exception))

    def test_open_rejects_an_empty_path(self):
        with self.assertRaises(SQLiteDatabaseError):
            open_sqlite_db_readonly('')

    def test_probe_helpers_report_absence_instead_of_raising(self):
        self._make_unreadable()
        # This is the call that used to raise AttributeError on a None handle.
        self.assertFalse(does_column_exist_in_db(self.db_path, 'sms', 'body'))
        self.assertFalse(does_table_exist_in_db(self.db_path, 'sms'))
        self.assertFalse(does_view_exist_in_db(self.db_path, 'sms_view'))
        self.assertEqual(list(get_sqlite_db_records(self.db_path, 'SELECT 1')), [])
        self.assertIsNone(open_sqlite_db_readonly_or_none(self.db_path))

    def test_artifact_style_caller_fails_with_the_database_error(self):
        '''The smsmms shape from the original report: open, then use the handle.'''
        self._make_unreadable()
        import scripts.artifacts.smsmms as smsmms
        read_rows = getattr(smsmms, '_rows')
        with self.assertRaises(SQLiteDatabaseError):
            read_rows(self.db_path, 'SELECT * FROM sms')


if __name__ == '__main__':
    unittest.main()
