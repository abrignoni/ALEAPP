"""Actual SQLite storage classes and live WAL for the raw channel value."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import hikvision


class TestHikvisionRawEnable(unittest.TestCase):
    def run_channels(self, paths):
        return hikvision.get_hikvision.__wrapped__(
            SimpleNamespace(get_files_found=lambda: paths))

    def test_sqlite_affinity_unknowns_and_repeated_rows(self):
        values = [None, 0, 1, -1, 0.5, '0', '1', '', 'unknown', b'', b'1', 0]
        with tempfile.TemporaryDirectory() as directory:
            for affinity in ['', 'TEXT', 'INTEGER']:
                with self.subTest(affinity=affinity):
                    folder = Path(directory) / (affinity or 'NONE')
                    folder.mkdir()
                    path = folder / 'database.hik'
                    with sqlite3.connect(path) as db:
                        db.execute('CREATE TABLE channelinfo(nDeviceID,nChannelNo,chChannelName,nEnable ' + affinity + ')')
                        db.executemany('INSERT INTO channelinfo VALUES(1,2,"name",?)', [(v,) for v in values])
                        expected = db.execute('SELECT nDeviceID,nChannelNo,chChannelName,nEnable FROM channelinfo').fetchall()
                        old = db.execute("SELECT CASE nEnable WHEN '0' THEN 'Disabled' WHEN '1' THEN 'Enabled' END FROM channelinfo").fetchall()
                    headers, rows, source = self.run_channels([str(path)])
                    self.assertEqual(headers[-1], 'nEnable (As Stored)')
                    self.assertEqual(rows, expected)
                    self.assertEqual([type(r[3]) for r in rows], [type(r[3]) for r in expected])
                    self.assertEqual(source, str(path))
                    self.assertEqual(rows[8][3], 'unknown')
                    self.assertIsNone(old[8][0])
                    self.assertEqual(rows[9][3], b'')
                    self.assertIsNone(old[9][0])
                    self.assertEqual(rows[1], rows[-1])

    def test_live_wal_and_first_main_even_when_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'a' / 'database.hik'
            second = Path(directory) / 'b' / 'database.hik'
            first.parent.mkdir()
            second.parent.mkdir()
            with sqlite3.connect(first) as db:
                db.execute('CREATE TABLE channelinfo(nDeviceID,nChannelNo,chChannelName,nEnable)')
            db = sqlite3.connect(second)
            try:
                db.execute('CREATE TABLE channelinfo(nDeviceID,nChannelNo,chChannelName,nEnable)')
                db.execute('INSERT INTO channelinfo VALUES(1,2,"base",0)')
                db.commit()
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA wal_autocheckpoint=0')
                db.execute('UPDATE channelinfo SET nEnable="unknown"')
                db.execute('INSERT INTO channelinfo SELECT * FROM channelinfo')
                db.commit()
                _, rows, source = self.run_channels([str(second) + '-wal', str(first), str(second)])
                self.assertEqual((rows, source), ([], str(first)))
                _, rows, source = self.run_channels([str(second) + '-wal', str(second), str(first)])
                self.assertEqual(rows, [(1, 2, 'base', 'unknown')] * 2)
                self.assertEqual(source, str(second))
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
