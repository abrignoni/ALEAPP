"""Per-source schemas and conflicting WAL snapshots preserve event rows."""
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.SamsungDeviceHealthManagement import sdhms_config_reloads, sdhms_temperature

PARSERS = [sdhms_config_reloads, sdhms_temperature]

def make_database(path, value=10, alternate=False, bad=False, empty=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    if bad:
        con.execute('CREATE TABLE unrelated(value)')
    else:
        con.execute('CREATE TABLE config_history(time,reason,config_key,config_version)')
        con.execute('CREATE TABLE TEMPERATURE(' + ('time' if alternate else 'timestamp') + ',skin_temp)')
        if not empty:
            con.executemany('INSERT INTO config_history VALUES(1700000000000,?,?,?)', [(str(value), 'key', value)] * 2)
            con.executemany('INSERT INTO TEMPERATURE VALUES(1700000000000,?)', [(value,)] * 2)
    con.commit()
    con.close()
    return path

def make_multisource(root):
    root = pathlib.Path(root)
    paths = []
    for name in ['anomaly.db', 'thermal_log']:
        first = make_database(root / 'data/data/com.sec.android.sdhms/databases' / name)
        mirror = root / 'data/user/0/com.sec.android.sdhms/databases' / name
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(first, mirror)
        second = make_database(root / 'data/user/10/com.sec.android.sdhms/databases' / name, 50, alternate=True)
        bad = make_database(root / 'data/user/20/com.sec.android.sdhms/databases' / name, bad=True)
        paths.extend([bad, first, mirror, second])
    return paths

class ConfigTemperatureSourcesTest(unittest.TestCase):
    def test_all_sources_local_alias_schema_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_multisource(folder)
            for parser, subset in zip(PARSERS, [paths[:4], paths[4:]]):
                with patch('scripts.artifacts.SamsungDeviceHealthManagement.logfunc') as log:
                    headers, rows, sources = parser.__wrapped__(context(folder, subset))
                self.assertEqual(len(rows), 4)
                self.assertEqual(headers[-1], 'Source File')
                self.assertEqual(len(sources.splitlines()), 2)
                self.assertEqual(rows[0], rows[1])
                self.assertEqual(rows[2], rows[3])
                self.assertTrue(any('unsupported' in call.args[0] and '20' in call.args[0] for call in log.call_args_list))
                if parser is sdhms_temperature:
                    self.assertEqual([row[1] for row in rows], [1.0, 1.0, 5.0, 5.0])
                    self.assertTrue(all(row[2] is None for row in rows))

    def test_actual_conflicting_wal_states_not_collapsed(self):
        with tempfile.TemporaryDirectory() as folder:
            live = make_database(pathlib.Path(folder) / 'live', empty=True)
            con = sqlite3.connect(live)
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            paths = []
            for user, value in [('data/data', 10), ('data/user/0', 50)]:
                con.execute('INSERT INTO TEMPERATURE VALUES(1700000000000,?)', (value,))
                con.execute('INSERT INTO config_history VALUES(1700000000000,?,?,?)', (str(value), 'key', value))
                con.commit()
                target = pathlib.Path(folder) / user / 'com.sec.android.sdhms/databases/thermal_log'
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live) + suffix, str(target) + suffix)
                paths.append(target)
            con.close()
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            for parser in PARSERS:
                _, rows, sources = parser.__wrapped__(context(folder, paths))
                self.assertEqual(len(rows), 3)
                self.assertEqual(len(sources.splitlines()), 2)
                self.assertEqual(len({row[-1] for row in rows}), 2)

    def test_empty_and_sidecar_only_are_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            main = make_database(pathlib.Path(folder) / 'thermal_log', empty=True)
            for parser in PARSERS:
                for paths in [[main], [str(main) + '-wal']]:
                    headers, rows, source = parser.__wrapped__(context(folder, paths))
                    self.assertNotIn('Source File', headers)
                    self.assertEqual(rows, [])
                    self.assertEqual(source, '')
