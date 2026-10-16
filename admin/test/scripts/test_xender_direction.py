"""Check stored Xender direction and party values using an actual SQLite input."""
import datetime
import pathlib
import sqlite3
import tempfile
import unittest

from scripts.artifacts.Xender import get_Xender_messages


DIRECTIONS = [1, 1.0, 0, 2, -1, None, '', '1', 'Outgoing', 'unknown']


def make_database(path):
    """No affinity on direction or IDs, so SQLite retains the stored value types."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE new_history (
        f_path, f_display_name, f_size_str, c_start_time, c_direction, c_session_id,
        s_name, s_device_id, r_name, r_device_id)''')
    rows = []
    for index, direction in enumerate(DIRECTIONS):
        timestamp = [1700000000123, None, 0][index % 3]
        sender_id = [0, None, 'sender-id'][index % 3]
        recipient_id = [None, 0, 'recipient-id'][index % 3]
        rows.append((f'/stored/file-{index}', f'file-{index}', '10 KB', timestamp,
                     direction, f'session-{index}', 'sender-name', sender_id,
                     'recipient-name', recipient_id))
    rows.append(rows[0])  # A repeated source record must remain a repeated report row.
    db.executemany('INSERT INTO new_history VALUES (?,?,?,?,?,?,?,?,?,?)', rows)
    db.commit()
    db.close()
    return rows


class Context:
    """Only the real parser's input-selection interface is needed by this test."""
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        return [self.path]


class TestXenderDirection(unittest.TestCase):
    def test_direction_types_dates_parties_and_repeated_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'trans-history-db'
            source_rows = make_database(path)
            headers, rows, source = get_Xender_messages.__wrapped__(Context(path))
            self.assertEqual(source, str(path))
            self.assertEqual(headers, (
                ('timestamp', 'datetime'), 'file_path', 'file_display_name', 'file_size',
                'Direction (as stored)', 'to_id', 'from_id', 'session_id',
                'sender_name', 'sender_device_id', 'recipient_name', 'recipient_device_id'))
            self.assertEqual(len(rows), 11)
            self.assertEqual(rows[0], rows[-1])
            for raw, report in zip(source_rows, rows):
                self.assertEqual(len(report), 12)
                self.assertIs(type(report[4]), type(raw[4]))
                self.assertEqual(report[4], raw[4])
                expected_date = (datetime.datetime(2023, 11, 14, 22, 13, 20, 123000,
                                                   tzinfo=datetime.timezone.utc)
                                 if raw[3] else '')
                self.assertEqual(report[0], expected_date)
                self.assertEqual(report[1:4], raw[0:3])
                self.assertEqual(report[5], raw[9] if raw[9] else '')
                self.assertEqual(report[6], raw[7] if raw[7] else '')
                self.assertEqual(report[7:], raw[5:])


if __name__ == '__main__':
    unittest.main()
