"""SMS Device Clock Gap on a synthetic mmssms.db (values invented for the test)."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import smsClockGap as parser  # noqa: E402

BASE = 1_700_000_000_000


def fixture(root):
    path = root / 'data/user_de/0/com.android.providers.telephony/databases/mmssms.db'
    path.parent.mkdir(parents=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE sms(_id INTEGER PRIMARY KEY, thread_id, address, date, date_sent, type)')
    db.executemany('INSERT INTO sms VALUES(?,?,?,?,?,?)', [
        (1, 1, '+15550001', BASE + 1_200_000 + 700, BASE, 1),      # received, clock ahead
        (2, 1, '+15550001', BASE + 60_000 - 5_000, BASE + 60_000, 1),  # received, clock behind
        (3, 1, '+15550001', BASE + 30_000, 0, 1),                  # received, no SC time
        (4, 1, '+15550001', BASE + 40_000, 0, 2),                  # sent
        (5, 2, '+15550002', BASE + 90_000, BASE + 89_000, 2),      # sent with a value: not inbox
    ])
    db.commit()
    db.close()
    return [str(path)]


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: paths,
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


class SmsClockGapTest(unittest.TestCase):
    def test_inbox_rows_with_service_centre_time_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = fixture(root)
            headers, rows, source = parser.get_sms_clock_gap.__wrapped__(context(root, paths))
        self.assertEqual(len(headers), 6)
        self.assertEqual([r[5] for r in rows], [1, 2])          # ordered by service-centre time
        self.assertEqual([r[2] for r in rows], [1200.7, -5.0])   # signed seconds
        self.assertTrue(all(len(r) == len(headers) for r in rows))
        self.assertEqual(source, paths[0])

    def test_database_without_sms_table(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            path = root / 'data/data/com.android.providers.telephony/databases/mmssms.db'
            path.parent.mkdir(parents=True)
            sqlite3.connect(path).close()
            _, rows, source = parser.get_sms_clock_gap.__wrapped__(context(root, [str(path)]))
        self.assertEqual(rows, [])
        self.assertEqual(source, str(path))


if __name__ == '__main__':
    unittest.main()
