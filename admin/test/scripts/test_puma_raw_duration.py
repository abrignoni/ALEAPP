"""Raw preference values survive zero/NULL and duplicate user records."""
import pathlib
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from scripts.artifacts.PumaUsers import get_puma_users

VALUES = [None, 0, 120, -60, 1.5, 120]

def make_database(path, empty=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE users(id,email,name,sex,dateOfBirth,weight,height,country,location,interestsIds,profileImageUrl,totalScore,followingCount,followersCount,goal_id,preferences_workoutTimeOfDay,preferences_workoutDuration)')
    if not empty:
        for value in VALUES:
            con.execute('INSERT INTO users VALUES(' + ','.join('?' * 17) + ')', (1, 'fixture@example.invalid', 'User', 'stored', -315619200000, 1, 2, 'country', 'location', 'ids', None, 1, 2, 3, 4, 'stored-time', value))
    con.commit()
    con.close()
    return path

class PumaRawDurationTest(unittest.TestCase):
    def test_raw_types_zero_null_duplicates_and_existing_derived_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = make_database(pathlib.Path(folder) / 'pumatrac-db')
            headers, rows, source = get_puma_users.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(path)], get_relative_path=lambda source: pathlib.Path(source).name))
            raw = headers.index('Workout Duration (as stored)')
            derived = headers.index('Workout Duration / 60 (unit unverified)')
            self.assertEqual([row[raw] for row in rows], VALUES)
            self.assertEqual([row[derived] for row in rows], ['N/A', 'N/A', 2.0, -1.0, 0.025, 2.0])
            self.assertIsNone(rows[0][raw])
            self.assertIsInstance(rows[1][raw], int)
            self.assertIsInstance(rows[4][raw], float)
            self.assertEqual(rows[2], rows[5])
            self.assertEqual(rows[0][0].year, 1960)
            self.assertEqual(source, str(path))
            self.assertNotIn('Source File', headers)

    def test_empty_table(self):
        with tempfile.TemporaryDirectory() as folder:
            path = make_database(pathlib.Path(folder) / 'pumatrac-db', empty=True)
            _, rows, _ = get_puma_users.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(path)], get_relative_path=lambda source: pathlib.Path(source).name))
            self.assertEqual(rows, [])
