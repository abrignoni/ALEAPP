"""Named Nike projections survive reordered schemas and distinct source identities."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import NikeActivities as nike
from admin.test.scripts.test_history_doclist_all_sources import Context

ACTIVITY = ('as2_sa_id', 'as2_sa_platform_id', 'as2_sa_app_id', 'as2_sa_start_utc_ms',
            'as2_sa_end_utc_ms', 'as2_sa_active_duration_ms', 'as2_sa_type', 'as2_sa_user_category',
            'as2_sa_is_deleted', 'as2_sa_is_dirty', 'as2_sa_last_modified_ms', 'as2_sa_change_tokens',
            'as2_sa_metrics', 'as2_sa_sources', 'as2_sa_status')
TAG = ('as2_t_id', 'as2_t_activity_id', 'as2_t_type', 'as2_t_value')
SUMMARY = ('as2_s_id', 'as2_s_activity_id', 'as2_s_app_id', 'as2_s_metric_type', 'as2_s_source',
           'as2_s_type', 'as2_s_value')


def create_nike_fixture(root):
    root = Path(root)
    files = []
    for name, view, reorder, optional in [('A', 'data/data', False, False),
                                          ('B', 'data/user/10', True, False),
                                          ('C', 'data/user/20', True, True)]:
        path = root/name/view/'com.nike.plusgps/databases/com.nike.nrc.room.database'
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        for table, field_names in [('activity', ACTIVITY), ('activity_tag', TAG),
                                   ('activity_summary', SUMMARY)]:
            fields = list(reversed(field_names)) if reorder else list(field_names)
            if optional:
                absent = {'as2_sa_app_id', 'as2_t_value', 'as2_s_value'}
                fields = [f for f in fields if f not in absent]
            db.execute('CREATE TABLE '+table+' ('+','.join(fields)+')')
            records = []
            if table == 'activity':
                for deleted in ([0] if optional else [0, 1]):
                    record = dict.fromkeys(ACTIVITY)
                    record.update(as2_sa_id='same', as2_sa_platform_id='platform', as2_sa_app_id='app'+name,
                                  as2_sa_start_utc_ms=1700000000000, as2_sa_end_utc_ms=1700000090000,
                                  as2_sa_active_duration_ms=90000, as2_sa_is_deleted=deleted,
                                  as2_sa_status=99 if deleted else 0)
                    records.append(record)
            elif table == 'activity_tag':
                for key, value in [('com.nike.name', 'run <'+name+'>'), ('location', name),
                                   ('com.nike.running.recordingappversion', 'version'),
                                   ('com.nike.temperature', 'unknown'), ('com.nike.weather', 'cloudy')]:
                    records.append(dict(zip(TAG, (key, 'same', key, value))))
            else:
                for metric, kind, value in [('calories', 'total', 123.459), ('speed', 'max', 3.14159),
                                            ('speed', 'mean', 'unknown'), ('steps', 'total', 10),
                                            ('distance', 'total', 1.2345), ('pace', 'mean', None),
                                            ('cadence', 'mean', 80)]:
                    records.append(dict(zip(SUMMARY, (metric+kind, 'same', 'app'+name, metric,
                                                     'source', kind, value))))
            for record in records:
                db.execute('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in fields)+')',
                           [record[f] for f in fields])
        db.commit()
        db.close()
        files.append(path)
    for view in ['A/data/user/0', 'A/data_mirror/data_ce/null/0']:
        alias = root/view/'com.nike.plusgps/databases/com.nike.nrc.room.database'
        alias.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(files[0], alias)
        files.append(alias)
    for suffix in ['-wal', '-shm']:
        sidecar = files[0].with_name(files[0].name+suffix)
        sidecar.write_bytes(b'')
        files.append(sidecar)
    return files


class TestNikeActivitySources(unittest.TestCase):
    def test_reordered_columns_sources_and_lifecycle_multiplicity(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_nike_fixture(directory)
            with patch.object(nike, 'logfunc') as logs:
                headers, raw, sources = nike.get_nike_activities.__wrapped__(Context(directory, files))
            self.assertEqual(len(raw), 5)
            self.assertEqual(len(sources.splitlines()), 3)
            self.assertEqual(headers[:2], (('Start Time UTC', 'datetime'), ('End Time UTC', 'datetime')))
            labels = [h[0] if isinstance(h, tuple) else h for h in headers]
            rows = [dict(zip(labels, row)) for row in raw]
            self.assertEqual([r['Activity App ID'] for r in rows], ['appA', 'appA', 'appB', 'appB', None])
            self.assertEqual([r['Name'] for r in rows], ['run <A>', 'run <A>', 'run <B>', 'run <B>', None])
            self.assertTrue(all(r['Activity ID'] == 'same' for r in rows))
            self.assertTrue(all(r['Start Time UTC'].timestamp() == 1700000000 for r in rows))
            self.assertTrue(all(r['Duration (min)'] == 1.5 for r in rows))
            self.assertEqual([r['Max Speed (unit unknown)'] for r in rows], [3.14]*4+[None])
            self.assertEqual([r['Mean Speed (unit unknown)'] for r in rows], ['unknown']*4+[None])
            self.assertEqual([r['Distance (unit unknown)'] for r in rows], [1.23]*4+[None])
            self.assertTrue(all(Path(directory, r['Source File']).is_file() for r in rows))
            self.assertEqual(raw[0], raw[1])
            self.assertTrue(any('as2_sa_app_id' in str(c) and 'C/data/user/20/' in str(c)
                                for c in logs.call_args_list))

    def test_unavailable_first_source_keeps_later_databases(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_nike_fixture(directory)
            original_open = nike.open_sqlite_db_readonly

            def unavailable_first(path):
                return None if Path(path) == files[0] else original_open(path)

            with patch.object(nike, 'open_sqlite_db_readonly', side_effect=unavailable_first):
                with patch.object(nike, 'logfunc') as logs:
                    _, rows, sources = nike.get_nike_activities.__wrapped__(Context(directory, files))
            self.assertEqual(len(rows), 3)
            self.assertEqual(len(sources.splitlines()), 2)
            self.assertTrue(all(row[-1].startswith(('B/', 'C/')) for row in rows))
            self.assertTrue(any('database unavailable for A/data/data/' in str(call)
                                for call in logs.call_args_list))

    def test_missing_required_source_does_not_suppress_healthy_database(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_nike_fixture(directory)
            bad = Path(directory)/'BAD/data/user/30/com.nike.plusgps/databases/com.nike.nrc.room.database'
            bad.parent.mkdir(parents=True)
            db = sqlite3.connect(bad)
            db.execute('CREATE TABLE activity(unrelated)')
            db.close()
            with patch.object(nike, 'logfunc') as logs:
                self.assertEqual(len(nike.get_nike_activities.__wrapped__(Context(directory, [bad, *files]))[1]), 5)
            self.assertTrue(any('schema skipped' in str(c) and 'BAD/' in str(c) for c in logs.call_args_list))


if __name__ == '__main__':
    unittest.main()
