"""An artifact that reads every differing storage view reports their union and survives a bad copy.

Google Cast stands in for the eight artifacts that pass keep_differing_views to
unique_files: two copies of cast.db under data/data and data/user/0 that hold different
rows give the union of their rows, a copy identical to another adds nothing, and a copy
whose query fails is logged and skipped instead of costing the artifact the rows of the
copies that read.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.Spotify import spotify_playback_activity  # pylint: disable=wrong-import-position
from scripts.artifacts.googleCast import googleCast  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

CAST = 'com.google.android.gms/databases/cast.db'
COLUMNS = ('last_published_timestamp_millis', 'device_id', 'capabilities', 'device_version', 'friendly_name',
           'model_name', 'receiver_metrics_id', 'service_instance_name', 'service_address', 'service_port',
           'supported_criteria', 'rcn_enabled_status', 'hotspot_bssid', 'cloud_devcie_id',
           'last_discovered_timestamp_millis', 'last_discovered_by_ble_timestamp_millis')


class TestStorageViewAdopters(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data = pathlib.Path(self.tmpdir) / 'data'
        Context.clear()
        Context.set_report_folder(self.tmpdir)
        Context.set_data_folder(str(self.data))

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _cast(self, view, devices, table=True, times=1700000000000):
        path = self.data / view / CAST
        path.parent.mkdir(parents=True)
        db = sqlite3.connect(path)
        if table:
            db.execute(f'CREATE TABLE DeviceInfo ({", ".join(COLUMNS)})')
            for device in devices:
                db.execute(f'INSERT INTO DeviceInfo VALUES ({", ".join("?" * len(COLUMNS))})',
                           (times, device) + ('',) * (len(COLUMNS) - 4) + (times, times))
        else:
            db.execute('CREATE TABLE other (x)')
        db.commit()
        db.close()
        return str(path)

    def _run(self, files):
        Context.set_files_found(files)
        _headers, rows, source = googleCast.__wrapped__(Context)
        return sorted(row[1] for row in rows), source

    def test_differing_copies_give_the_union(self):
        files = [self._cast('Dump/data/data', ['A', 'B']), self._cast('Dump/data/user/0', ['A', 'C'])]
        devices, source = self._run(files)
        self.assertEqual(devices, ['A', 'B', 'C'])
        self.assertEqual(len(source.split('\n')), 2)

    def test_an_identical_copy_adds_nothing(self):
        files = [self._cast('Dump/data/data', ['A', 'B']), self._cast('Dump/data/user/0', ['A', 'B'])]
        devices, source = self._run(files)
        self.assertEqual(devices, ['A', 'B'])
        self.assertEqual(len(source.split('\n')), 1)

    def test_a_copy_whose_query_fails_does_not_cost_the_other_copys_rows(self):
        files = [self._cast('Dump/data/data', ['A', 'B']), self._cast('Dump/data/user/0', [], table=False)]
        devices, _source = self._run(files)
        self.assertEqual(devices, ['A', 'B'])

    def test_a_copy_with_zero_times_does_not_cost_the_rows(self):
        files = [self._cast('Dump/data/data', ['A']), self._cast('Dump/data/user/0', ['B'], times=0)]
        devices, _source = self._run(files)
        self.assertEqual(devices, ['A', 'B'])

    def test_a_spotify_copy_that_is_not_a_database_does_not_cost_the_good_copys_rows(self):
        good = self.data / 'Dump/data/data/com.spotify.music/databases/event-sender.db'
        good.parent.mkdir(parents=True)
        db = sqlite3.connect(good)
        db.execute('CREATE TABLE Events (id INTEGER, eventName TEXT, fragments BLOB)')
        db.commit()
        db.close()
        bad = self.data / 'Dump/data/user/0/com.spotify.music/databases/event-sender.db'
        bad.parent.mkdir(parents=True)
        bad.write_bytes(b'not a database' * 100)
        Context.set_files_found([str(good), str(bad)])
        _headers, rows, source = spotify_playback_activity.__wrapped__(Context)
        self.assertEqual(rows, [])
        self.assertIn('data/data', source)


if __name__ == '__main__':
    unittest.main()
