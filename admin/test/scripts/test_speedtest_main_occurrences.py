"""Actual SQLite selection, occurrence and handled-failure checks for Speedtest."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import speedtest


class SpeedtestMainOccurrences(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def database(self, folder, rows, valid=True):
        path = self.root / folder / 'AmplifyDatastore.db'
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            if valid:
                db.execute('CREATE TABLE UnivSpeedTestResult(date,connectionType,ssid,'
                           'userLatitude,userLongitude,externalIp,internalIp,downloadKbps,uploadKbps)')
                db.executemany('INSERT INTO UnivSpeedTestResult VALUES(?,?,?,?,?,?,?,?,?)', rows)
            else:
                db.execute('CREATE TABLE unrelated(value)')
        db.close()
        return path

    def run_rows(self, paths):
        context = SimpleNamespace(get_files_found=lambda: paths,
                                  get_relative_path=lambda p: str(Path(p).relative_to(self.root)))
        with patch.object(speedtest, 'logfunc') as log:
            result = speedtest.speedtest_tests.__wrapped__(context)
        return result, log

    def test_repeated_occurrences_and_distinct_contributors(self):
        row = (0, None, 'wifi', 0, 0, b'\xff\x00', '', 0, -1)
        first = self.database('first', [row, row])
        second = self.database('second', [row])
        (headers, rows, source), _ = self.run_rows([str(first) + '-wal', first, second, first])
        self.assertEqual(len(headers), 10)
        self.assertEqual([r[:9] for r in rows], [list(row)] * 5)
        self.assertEqual([r[9] for r in rows], ['first/AmplifyDatastore.db'] * 2 +
                         ['second/AmplifyDatastore.db'] + ['first/AmplifyDatastore.db'] * 2)
        self.assertEqual(source, f'{first}\n{second}')

    def test_failed_query_continues_without_partial_or_failed_source(self):
        bad = self.database('bad', [], valid=False)
        good = self.database('good', [(0, 0, '', None, None, '', '', 1, 2)])
        (headers, rows, source), log = self.run_rows([bad, good, bad])
        self.assertEqual(len(headers), 9)
        self.assertEqual(len(rows), 1)
        self.assertEqual(source, str(good))
        self.assertEqual(log.call_count, 2)
        self.assertTrue(all('OperationalError' in call.args[0] for call in log.call_args_list))

    def test_successful_empty_sources_and_sidecars(self):
        first = self.database('first', [])
        second = self.database('second', [])
        (headers, rows, source), _ = self.run_rows([first, second, first])
        self.assertEqual(len(headers), 9)
        self.assertEqual(rows, [])
        self.assertEqual(source, f'{first}\n{second}')
        (headers, rows, source), _ = self.run_rows([str(first) + '-shm'])
        self.assertEqual((len(headers), rows, source), (9, [], ''))


if __name__ == '__main__':
    unittest.main()
