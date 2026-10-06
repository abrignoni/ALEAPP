"""Unsourced category names do not change stored measurement values."""
import pathlib
import sqlite3
import tempfile
import unittest
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.WithingsHealthMate import healthmate_measurements

CATEGORIES = [-22, -19, -16, 16, 99, None, 0, 'stored-text', -19]
VALUE_POSITIONS = [5, 11, 12, 13, 14, 18, 32, 33, 23, 22, 42]


def make_database(path, empty=False):
    """Synthetic 43-column layout exercises only the parser's existing positions."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE vasistas(' + ','.join(f'c{i}' for i in range(43)) + ')')
    rows = []
    if not empty:
        for index, category in enumerate(CATEGORIES):
            row = [None] * 43
            row[0], row[1], row[4], row[24] = index, 'stored-user', 1700000000123 + index * 1000, category
            for position in VALUE_POSITIONS:
                row[position] = None if position == 33 else 0 if position == 18 else index + position / 10
            rows.append(tuple(row))
        con.executemany('INSERT INTO vasistas VALUES(' + ','.join('?' for _ in range(43)) + ')', rows)
    con.commit()
    con.close()
    return path, rows


class WithingsCategoryLabelsTest(unittest.TestCase):
    def test_actual_sqlite_raw_ids_values_and_credited_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            path, original = make_database(pathlib.Path(folder) / 'Withings-WiScale')
            headers, rows, source = healthmate_measurements.__wrapped__(context(folder, [path]))
            self.assertEqual(len(rows), len(original))
            self.assertEqual(headers[0], ('Timestamp', 'datetime'))
            self.assertEqual(source, str(path))
            for report, record in zip(rows, original):
                self.assertEqual(report[1:3], (record[0], record[24]))
                self.assertEqual(report[3], {-16: 'Heart Rate', 16: 'Steps'}.get(record[24], 'Unknown Category ID'))
                self.assertEqual(report[4], record[1])
                self.assertEqual(report[5:], tuple(record[p] for p in VALUE_POSITIONS))
            self.assertEqual(rows[1][2], rows[-1][2])
            self.assertEqual(rows[1][3], 'Unknown Category ID')

    def test_empty_table_is_preserved_without_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path, _rows = make_database(pathlib.Path(folder) / 'Withings-WiScale', empty=True)
            _headers, rows, source = healthmate_measurements.__wrapped__(context(folder, [path]))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(path))
