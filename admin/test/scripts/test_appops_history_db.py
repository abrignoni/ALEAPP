"""App Ops history databases: decoding helpers and the two artifacts on constructed databases."""
# pylint: disable=protected-access
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import appOpsHistoryDb as module
from admin.test.scripts import appops_history_fixture as fixture


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


class DecoderTests(unittest.TestCase):
    def test_op_names(self):
        self.assertEqual(module._op_name(26), 'CAMERA')
        self.assertEqual(module._op_name('27'), 'RECORD_AUDIO')
        self.assertEqual(module._op_name(163), 'POST_PROMOTED_NOTIFICATIONS')
        self.assertEqual(module._op_name(169), 'ACCESS_LOCAL_NETWORK')
        for unnamed in (96, 170, -1, None, 'x', 2 ** 40):
            self.assertEqual(module._op_name(unnamed), '')

    def test_uid_state(self):
        self.assertEqual(module._uid_state(200), 'TOP')
        self.assertEqual(module._uid_state(2147483647), 'NONEXISTENT')
        self.assertEqual(module._uid_state(12345), '12345')
        self.assertEqual(module._uid_state(None), '')
        self.assertEqual(module._uid_state('z'), 'z')

    def test_flag_names(self):
        self.assertEqual(module._flag_names(9, module.ATTRIBUTION_FLAGS, 'NONE'), 'ACCESSOR | TRUSTED')
        self.assertEqual(module._flag_names(0, module.ATTRIBUTION_FLAGS, 'NONE'), 'NONE')
        self.assertEqual(module._flag_names(16 | 32, module.OP_FLAGS, '0'), 'UNTRUSTED_PROXIED | 32')
        self.assertEqual(module._flag_names(None, module.OP_FLAGS, '0'), '')
        self.assertEqual(module._flag_names('v', module.OP_FLAGS, '0'), 'v')

    def test_epoch_ms(self):
        moment = module._epoch_ms(1787562005120)
        self.assertEqual(moment.isoformat(), '2026-08-24T09:00:05.120000+00:00')
        for unreadable in (None, 'not a time', 9223372036854775807, -(2 ** 63), 10 ** 20, True):
            self.assertIsNone(module._epoch_ms(unreadable))


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.history = Path(fixture.build_history(self.work))
        self.root = Path(self.work) / 'extraction'
        self.appops = self.root / 'data' / 'system' / 'appops'
        self.appops.mkdir(parents=True)
        for item in self.history.iterdir():
            shutil.copy(item, self.appops / item.name)

    def run_artifact(self, function, files=None):
        files = sorted(self.appops.iterdir()) if files is None else files
        return function.__wrapped__(Context(self.root, files))

    def test_current_rows_cover_every_user_and_interval(self):
        headers, rows, source = self.run_artifact(module.appops_history_db)
        self.assertEqual(len(rows), 18)
        index = headers.index
        self.assertEqual({row[index('Interval')] for row in rows}, {'Short', 'Long'})
        self.assertEqual({row[index('Android User')] for row in rows}, {0, 150})
        self.assertEqual(len(source.split('\n')), 2)
        # The log is applied: the two deleted rows are gone and the changed row has its new count.
        long_ids = {row[index('Row ID')]: row for row in rows if row[index('Interval')] == 'Long'}
        self.assertNotIn(1, long_ids)
        self.assertNotIn(2, long_ids)
        self.assertEqual(long_ids[3][index('Access Count')], 7)
        self.assertEqual(rows[0][len(headers) - 1].count('app_op_history'), 1)

    def test_file_only_rows_are_the_log_difference(self):
        headers, rows, _ = self.run_artifact(module.appops_history_db_file_only)
        status = headers.index('Row Status')
        by_id = {row[headers.index('Row ID')]: row[status] for row in rows}
        self.assertEqual(set(by_id), {1, 2, 3})
        self.assertTrue(by_id[1].startswith('Not in'))
        self.assertTrue(by_id[3].startswith('Different'))
        changed = [row for row in rows if row[headers.index('Row ID')] == 3][0]
        self.assertEqual(changed[headers.index('Access Count')], 6)

    def test_no_log_means_no_file_only_rows(self):
        for suffix in ('-wal', '-shm'):
            (self.appops / ('app_op_history_long_interval.db' + suffix)).unlink()
        _, rows, source = self.run_artifact(module.appops_history_db_file_only)
        self.assertEqual(rows, [])
        self.assertEqual(source, '')
        _, current, _ = self.run_artifact(module.appops_history_db)
        self.assertEqual(len(current), 8 + 10)

    def test_unreadable_database_does_not_stop_the_others(self):
        (self.appops / 'app_op_history_short_interval.db').write_bytes(bytes(8192))
        _, rows, source = self.run_artifact(module.appops_history_db)
        self.assertEqual(len(rows), 8)
        self.assertEqual(len(source.split('\n')), 2)
        _, rows, _ = self.run_artifact(module.appops_history_db_file_only)
        self.assertEqual(len(rows), 3)

    def test_log_that_does_not_belong_falls_back_to_the_file(self):
        shutil.copy(self.appops / 'app_op_history_long_interval.db-wal',
                    self.appops / 'app_op_history_short_interval.db-wal')
        (self.appops / 'app_op_history_short_interval.db-shm').write_bytes(bytes(32768))
        headers, rows, _ = self.run_artifact(module.appops_history_db)
        short = [row for row in rows if row[headers.index('Interval')] == 'Short']
        self.assertEqual(len(short), 10)

    def test_missing_table_and_empty_table(self):
        path = self.appops / 'app_op_history_short_interval.db'
        path.unlink()
        for suffix in ('-wal', '-shm'):
            sidecar = self.appops / ('app_op_history_short_interval.db' + suffix)
            if sidecar.exists():
                sidecar.unlink()
        connection = sqlite3.connect(path)
        connection.execute('CREATE TABLE other (id INTEGER)')
        connection.commit()
        connection.close()
        _, rows, _ = self.run_artifact(module.appops_history_db, [path])
        self.assertEqual(rows, [])

    def test_sidecar_files_alone_are_not_databases(self):
        files = [self.appops / 'app_op_history_long_interval.db-wal', self.appops / 'app_op_history_long_interval.db-shm']
        _, rows, source = self.run_artifact(module.appops_history_db, files)
        self.assertEqual(rows, [])
        self.assertEqual(source, '')

    def test_odd_values_are_kept_and_not_dropped(self):
        odd = Path(fixture.build_odd(self.work))
        shutil.rmtree(self.appops)
        self.appops.mkdir(parents=True)
        shutil.copy(odd / 'app_op_history_long_interval.db', self.appops)
        headers, rows, _ = self.run_artifact(module.appops_history_db)
        self.assertEqual(len(rows), 10)
        stored = headers.index('Access Time (ms As Stored)')
        self.assertIn('not a time', [row[stored] for row in rows])
        self.assertEqual(sum(1 for row in rows if row[0] is None), 4)


if __name__ == '__main__':
    unittest.main()
