"""Distinct SQLite/WAL states retain every source row and its origin."""
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from scripts.artifacts.SamsungDeviceHealthManagement import sdhms_netstat, sdhms_cpustats, _stat_sources

PARSERS = [sdhms_netstat, sdhms_cpustats]

def make_database(path, value=1, optional=True, bad=False, empty=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    if bad:
        con.execute('CREATE TABLE unrelated(value)')
    else:
        con.execute('CREATE TABLE NETSTAT(start_time,end_time,id,package_name' + (',uid,net_usage)' if optional else ')'))
        con.execute('CREATE TABLE CPUSTAT(start_time,end_time,uptime,process_name,pid' + (',uid,process_usage)' if optional else ')'))
        if not empty:
            net = (1700000000000, 1700000060000, 1, 'package') + ((value, value * 10) if optional else ())
            cpu = (1700000000000, 1700000060000, 60, 'process', 1) + ((value, value * 20) if optional else ())
            con.executemany('INSERT INTO NETSTAT VALUES(' + ','.join('?' * len(net)) + ')', [net, net])
            con.executemany('INSERT INTO CPUSTAT VALUES(' + ','.join('?' * len(cpu)) + ')', [cpu, cpu])
    con.commit()
    con.close()
    return path

def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: [str(path) for path in paths],
                           get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)))

def make_multisource(root):
    root = pathlib.Path(root)
    first = make_database(root / 'data/data/com.sec.android.sdhms/databases/thermal_log', 1)
    mirror = root / 'data/user/0/com.sec.android.sdhms/databases/thermal_log'
    mirror.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(first, mirror)
    second = make_database(root / 'data/user/10/com.sec.android.sdhms/databases/thermal_log', 9, optional=False)
    third = make_database(root / 'OtherRoot/data/data/com.sec.android.sdhms/databases/thermal_log', 5)
    bad = make_database(root / 'data/user/20/com.sec.android.sdhms/databases/thermal_log', bad=True)
    return [first, mirror, second, third, bad]

class SDHMSStatSourcesTest(unittest.TestCase):
    def test_aliases_users_optional_columns_bad_schema_and_repeated_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_multisource(folder)
            ctx = context(folder, paths)
            for parser in PARSERS:
                with self.subTest(parser=parser.__name__), patch('scripts.artifacts.SamsungDeviceHealthManagement.logfunc') as log:
                    headers, rows, sources = parser.__wrapped__(ctx)
                    self.assertEqual(len(rows), 6)
                    self.assertEqual(headers[-1], 'Source File')
                    expected = {ctx.get_relative_path(path) for path in (paths[0], paths[2], paths[3])}
                    self.assertEqual({row[-1] for row in rows}, expected)
                    self.assertEqual(set(sources.splitlines()), {str(paths[i]) for i in (0, 2, 3)})
                    self.assertTrue(any('unsupported' in call.args[0] and '20' in call.args[0] for call in log.call_args_list))
                    self.assertEqual(rows[0], rows[1])
                    missing = [row for row in rows if row[-1] == ctx.get_relative_path(paths[2])]
                    uid_index = 4 if parser is sdhms_netstat else 4
                    self.assertTrue(all(row[uid_index] is None for row in missing))

    def test_main_equal_conflicting_actual_wal_aliases_remain_distinct(self):
        with tempfile.TemporaryDirectory() as folder:
            live = make_database(pathlib.Path(folder) / 'live', empty=True)
            con = sqlite3.connect(live)
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            paths = []
            for user_path, value in [('data/data', 1), ('data/user/0', 2)]:
                con.execute('INSERT INTO NETSTAT VALUES(1700000000000,1700000060000,1,\'package\',?,10)', (value,)); con.commit()
                target = pathlib.Path(folder) / user_path / 'com.sec.android.sdhms/databases/thermal_log'
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live) + suffix, str(target) + suffix)
                paths.append(target)
            con.close()
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            ctx = context(folder, paths)
            self.assertEqual(len(_stat_sources(ctx)), 2)
            _, rows, _ = sdhms_netstat.__wrapped__(ctx)
            self.assertEqual([row[4] for row in rows], [1, 1, 2])
            self.assertEqual({row[-1] for row in rows}, {ctx.get_relative_path(path) for path in paths})

    def test_single_source_no_redundant_source_column_and_empty_table(self):
        with tempfile.TemporaryDirectory() as folder:
            main = make_database(pathlib.Path(folder) / 'thermal_log', empty=True)
            for parser in PARSERS:
                headers, rows, source = parser.__wrapped__(context(folder, [main]))
                self.assertNotIn('Source File', headers)
                self.assertEqual(rows, [])
                self.assertEqual(source, '')
