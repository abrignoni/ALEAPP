"""Verify selected observation multiplicity independently of session grouping."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts.untappd import untappd_dev_events


class TestUntappdDeviceOccurrences(unittest.TestCase):
    def check_rows(self, shadow=False, wal=False):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'superwall_database'
            connection = sqlite3.connect(path)
            extra = ', "Session ID" TEXT' if shadow else ''
            connection.execute('CREATE TABLE ManagedEventData(createdAt, name, parameters' + extra + ')')
            if wal:
                connection.execute('PRAGMA journal_mode=WAL')
                connection.execute('PRAGMA wal_autocheckpoint=0')
            expected = []
            for index, value in enumerate(['same', 'same', None, '', 0, '0']):
                params = {'$appVersion': str(index), '$app_session_id': value}
                row = (1790856000000 + index * 1000, 'device_attributes', json.dumps(params))
                if shadow:
                    row += ('one grouping column',)
                connection.execute('INSERT INTO ManagedEventData VALUES (' + ','.join('?' for _ in row) + ')', row)
                expected.append((str(index), value))
            connection.execute('INSERT INTO ManagedEventData SELECT * FROM ManagedEventData WHERE rowid=1')
            expected.insert(1, expected[0])
            connection.commit()
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            headers, rows, source = untappd_dev_events.__wrapped__(context)
            self.assertEqual(13, len(headers))
            self.assertEqual(expected, [(row[1], row[12]) for row in rows])
            self.assertEqual(str(path), source)
            self.assertEqual([('ok',)], connection.execute('PRAGMA integrity_check').fetchall())
            if wal:
                self.assertGreater(Path(str(path) + '-wal').stat().st_size, 0)
            connection.close()

    def test_shared_and_null_sessions_retain_duplicate_observations(self):
        self.check_rows()

    def test_real_session_column_does_not_collapse_projected_sessions(self):
        self.check_rows(shadow=True)

    def test_committed_wal_observations_are_retained(self):
        self.check_rows(wal=True)


if __name__ == '__main__':
    unittest.main()
