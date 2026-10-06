"""Stored transfer values retain their types without inferred device roles."""
import datetime
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.Zapya import get_Zapya  # pylint: disable=wrong-import-position


def make_database(path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute('CREATE TABLE transfer(device,name,direction,createtime,path,title)')
    directions = [1, 1.0, 0, 2, -1, None, '', '1', 'Outgoing', 'unknown']
    devices = [0, None, '', 'device2', 'device-1', 'unknown-device', 0, 'device1', 'outgoing-text-device', 'other']
    records = [(device, str(index), direction, 1700000000123, 'path', 'title')
               for index, (device, direction) in enumerate(zip(devices, directions))]
    records.extend([records[0], (None, 'null-time', 0, None, None, None),
                    ('zero-device', 'zero-time', None, 0, '', ''),
                    ('subsecond-device', 'subsecond-time', 'stored', 999, 'path', 'title')])
    connection.executemany('INSERT INTO transfer VALUES(?,?,?,?,?,?)', records)
    connection.commit()
    connection.close()
    return path, records


class ZapyaRawDirectionTest(unittest.TestCase):
    def test_actual_sqlite_types_repeats_and_no_derived_parties(self):
        with tempfile.TemporaryDirectory() as directory:
            path, records = make_database(pathlib.Path(directory) / 'transfer20.db')
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            headers, rows, source = get_Zapya.__wrapped__(context)
            self.assertEqual(headers, (('createtime', 'datetime'), 'Recorded Device', 'Name',
                                       'Direction (as stored)', 'path', 'title'))
            self.assertEqual(source, str(path))
            self.assertEqual(len(rows), len(records))
            self.assertEqual(rows[0], rows[10])
            for row, stored in zip(rows, records):
                with self.subTest(name=stored[1]):
                    self.assertEqual(row[1:], (stored[0], stored[1], stored[2], stored[4], stored[5]))
                    self.assertIs(type(row[1]), type(stored[0]))
                    self.assertIs(type(row[3]), type(stored[2]))
            self.assertNotIn('Source File', headers)
            self.assertNotIn('fromid', headers)
            self.assertNotIn('toid', headers)

    def test_existing_integer_division_and_empty_date_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = make_database(pathlib.Path(directory) / 'transfer20.db')
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            _, rows, _ = get_Zapya.__wrapped__(context)
            expected = datetime.datetime(2023, 11, 14, 22, 13, 20, tzinfo=datetime.timezone.utc)
            self.assertTrue(all(row[0] == expected for row in rows[:11]))
            self.assertEqual([row[0] for row in rows[11:]], ['', '', ''])


if __name__ == '__main__':
    unittest.main()
