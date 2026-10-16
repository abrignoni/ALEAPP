"""Retain actual SQLite events, raw millisecond precision and unknown codes."""
import pathlib
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from scripts.artifacts.SimpleStorage_applaunch import SimpleStorage_applaunch

EVENTS = [(1700000000123, 'package', 1), (1700000000123, 'package', 1),
          (1700000000456, 'package', 1), (1700000000123, 'package', 999),
          (None, 'package', None), (0, 'package', 0), ('1700000000999', 'package', 'unknown')]

def create_fixture(root, empty=False):
    main = pathlib.Path(root) / 'data/data/com.google.android.as/databases/SimpleStorage'
    main.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(main)
    con.execute('CREATE TABLE EchoAppLaunchMetricsEvents(timestampMillis, packageName, launchLocationId)')
    if not empty:
        con.executemany('INSERT INTO EchoAppLaunchMetricsEvents VALUES(?,?,?)', EVENTS)
    con.commit()
    con.close()
    return main

class SimpleStorageRawTest(unittest.TestCase):
    def test_duplicate_events_same_second_unknown_and_null_values(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_fixture(folder)
            context = SimpleNamespace(get_files_found=lambda: [str(main)])
            with patch('scripts.artifacts.SimpleStorage_applaunch.Context.get_relative_path', return_value='data/data/com.google.android.as/databases/SimpleStorage'):
                headers, rows, source = SimpleStorage_applaunch.__wrapped__(context)
            self.assertEqual(len(rows), len(EVENTS))
            self.assertEqual([(row[1], row[2], row[3]) for row in rows], EVENTS)
            self.assertEqual(rows[0], rows[1])
            self.assertEqual(rows[0][0], rows[2][0])
            self.assertNotEqual(rows[0][1], rows[2][1])
            self.assertEqual(rows[0][4], 'Home Screen')
            self.assertEqual(rows[3][4], 999)
            self.assertIsNone(rows[4][0])
            self.assertIsNone(rows[4][4])
            self.assertEqual(headers[0], ('App Launched Timestamp', 'datetime'))
            self.assertEqual(source, str(main))
            self.assertTrue(all(row[-1] == 'data/data/com.google.android.as/databases/SimpleStorage' for row in rows))

    def test_valid_empty_table(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_fixture(folder, empty=True)
            with patch('scripts.artifacts.SimpleStorage_applaunch.Context.get_relative_path', return_value='SimpleStorage'):
                _, rows, source = SimpleStorage_applaunch.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(main)]))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(main))
