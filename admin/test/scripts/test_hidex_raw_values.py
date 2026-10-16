"""Preserve actual SQLite flag values without app-state assumptions."""
import pathlib
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from scripts.artifacts.HideX import get_HideX

FLAGS = [None, 0, 1, 2, -1, '', 'unknown', '0', '1', 2]

def create_hidex_fixture(root, empty=False):
    main = pathlib.Path(root) / 'data/data/com.flatfish.cal.privacy/databases/hidex.db'
    main.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(main)
    con.execute('CREATE TABLE p_lock_app(id, packageName, isActive)')
    if not empty:
        con.executemany('INSERT INTO p_lock_app VALUES (?, ?, ?)',
                        [(i if i < 9 else 3, 'package', flag) for i, flag in enumerate(FLAGS)])
    con.commit()
    con.close()
    return main

class HideXRawValuesTest(unittest.TestCase):
    def test_raw_types_repeated_records_and_other_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_hidex_fixture(folder)
            con = sqlite3.connect(main)
            expected = con.execute('SELECT id, packageName, isActive FROM p_lock_app').fetchall()
            con.close()
            headers, rows, source = get_HideX.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
            self.assertEqual(headers, ('ID', 'Package Name', 'Is Active (as stored)'))
            self.assertEqual(rows, expected)
            self.assertEqual([[type(value) for value in row] for row in rows],
                             [[type(value) for value in row] for row in expected])
            self.assertEqual(rows[3], rows[9])
            self.assertEqual(source, str(main))

    def test_valid_empty_table(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_hidex_fixture(folder, empty=True)
            _, rows, source = get_HideX.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(main))
