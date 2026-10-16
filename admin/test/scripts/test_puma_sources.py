"""Database identity retains independent users, WAL states and repeated records."""
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_puma_raw_duration import make_database
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.PumaUsers import get_puma_users, open_sqlite_db_readonly

def make_multisource(root):
    root = pathlib.Path(root)
    first = make_database(root / 'data/data/com.pumapumatrac/databases/pumatrac-db')
    mirror = root / 'data/user/0/com.pumapumatrac/databases/pumatrac-db'
    mirror.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(first, mirror)
    second = make_database(root / 'data/user/10/com.pumapumatrac/databases/pumatrac-db')
    third = make_database(root / 'OtherRoot/data/data/com.pumapumatrac/databases/pumatrac-db')
    for path, email in [(second, 'user10@example.invalid'), (third, 'prefix@example.invalid')]:
        con = sqlite3.connect(path)
        con.execute('UPDATE users SET email=?', (email,))
        con.commit()
        con.close()
    bad = root / 'data/user/20/com.pumapumatrac/databases/pumatrac-db'
    bad.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(bad)
    con.execute('CREATE TABLE unrelated(value)')
    con.close()
    return [bad, first, mirror, second, third]

class PumaSourcesTest(unittest.TestCase):
    def test_aliases_users_unknown_prefix_bad_schema_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_multisource(folder)
            with patch('scripts.artifacts.PumaUsers.logfunc') as log:
                headers, rows, sources = get_puma_users.__wrapped__(context(folder, paths))
            self.assertEqual(len(rows), 18)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual({row[-1] for row in rows}, {str(p.relative_to(folder)) for p in [paths[1], paths[3], paths[4]]})
            self.assertEqual(len(sources.splitlines()), 3)
            for row in rows:
                expected = 'user10@example.invalid' if '/10/' in row[-1] else 'prefix@example.invalid' if row[-1].startswith('OtherRoot/') else 'fixture@example.invalid'
                self.assertEqual(row[headers.index('Email')], expected)
            self.assertEqual(rows[2], rows[5])
            self.assertTrue(any('query failed' in call.args[0] and '20' in call.args[0] for call in log.call_args_list))

    def test_unavailable_first_then_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_multisource(folder)[1:4:2]
            def opener(path):
                return None if path == str(paths[0]) else open_sqlite_db_readonly(path)
            with patch('scripts.artifacts.PumaUsers.open_sqlite_db_readonly', side_effect=opener), patch('scripts.artifacts.PumaUsers.logfunc') as log:
                _, rows, _ = get_puma_users.__wrapped__(context(folder, paths))
            self.assertEqual(len(rows), 6)
            self.assertTrue(any('unavailable' in call.args[0] for call in log.call_args_list))

    def test_actual_conflicting_wal_states(self):
        with tempfile.TemporaryDirectory() as folder:
            live = make_database(pathlib.Path(folder) / 'live', empty=True)
            con = sqlite3.connect(live)
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            paths = []
            for user, value in [('data/data', 10), ('data/user/0', 20)]:
                con.execute('INSERT INTO users(id,dateOfBirth,preferences_workoutDuration) VALUES(1,0,?)', (value,))
                con.commit()
                target = pathlib.Path(folder) / user / 'com.pumapumatrac/databases/pumatrac-db'
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live) + suffix, str(target) + suffix)
                paths.append(target)
            con.close()
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            headers, rows, _ = get_puma_users.__wrapped__(context(folder, paths))
            self.assertEqual([row[headers.index('Workout Duration (as stored)')] for row in rows], [10, 10, 20])
            self.assertEqual(len({row[-1] for row in rows}), 2)

    def test_sidecar_only_and_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            main = make_database(pathlib.Path(folder) / 'pumatrac-db', empty=True)
            for paths in [[str(main) + '-wal'], [main]]:
                headers, rows, source = get_puma_users.__wrapped__(context(folder, paths))
                self.assertNotIn('Source File', headers)
                self.assertEqual(rows, [])
                self.assertEqual(source, '')
