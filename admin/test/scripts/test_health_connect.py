"""Health Connect parsers read a synthetic healthconnect.db (see health_connect_fixture.py)."""
import datetime
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from health_connect_fixture import T0, make_database  # pylint: disable=wrong-import-position
from scripts.artifacts import healthConnect as hc  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
START = datetime.datetime(2026, 1, 1, tzinfo=UTC)


def context(root, paths):
    return SimpleNamespace(
        get_files_found=lambda: [str(path) for path in paths],
        get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)))


def fake_media(_source, data, name=''):
    return f'media:{name}:{len(data)}'


def run(parser, folder, paths):
    with patch.object(hc, 'logfunc'), \
            patch.object(hc, 'check_in_embedded_media', side_effect=fake_media):
        return parser.__wrapped__(context(folder, paths))


def named(headers, row):
    return dict(zip([h if isinstance(h, str) else h[0] for h in headers], row))


class HealthConnectTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        root = pathlib.Path(self.folder.name)
        self.db = make_database(root / 'data/system_ce/0/healthconnect/healthconnect.db')
        sidecar = self.db.with_name('healthconnect.db-journal')
        sidecar.write_bytes(b'')
        self.paths = [self.db, sidecar]

    def go(self, parser, paths=None):
        return run(parser, self.folder.name, paths or self.paths)

    def test_apps_icons_and_record_type_names(self):
        headers, rows, source = self.go(hc.healthconnect_apps)
        self.assertEqual(headers[0], 'Android User')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], '0')
        self.assertEqual(rows[0][2:4], ('com.example.syntheticfit', 'Synthetic Fit'))
        self.assertTrue(rows[0][4].startswith('media:'))
        self.assertEqual(rows[0][5], '1 (Steps), 7 (Distance), 11 (Heart rate), 99')
        self.assertEqual(rows[1][4:6], (None, ''))
        self.assertEqual(source, str(self.db))

    def test_sidecar_is_not_read_as_a_database(self):
        _, rows, _ = self.go(hc.healthconnect_apps, [self.paths[1], self.paths[0]])
        self.assertEqual(len(rows), 2)

    def test_preferences(self):
        _, rows, _ = self.go(hc.healthconnect_preferences)
        self.assertEqual({(r[1], r[2]) for r in rows},
                         {('migration_state', '5'),
                          ('current_state_start_time', '2026-01-01T00:00:00.000000Z')})

    def test_activity_units_offsets_and_provenance(self):
        headers, rows, _ = self.go(hc.healthconnect_activity)
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        by_type = {}
        for row in rows:
            by_type.setdefault(row[1], []).append(row)
        steps = sorted(by_type['Steps'], key=lambda r: r[2])
        self.assertEqual(steps[0][2], START)
        self.assertEqual(steps[0][3], START + datetime.timedelta(hours=1))
        self.assertEqual(steps[0][4:8], ('+01:00', '+01:00', 1200, 'steps'))
        self.assertEqual(steps[1][4], '-01:00')
        second = named(headers, steps[1])
        self.assertEqual(second['Package'], 'com.example.syntheticfit')
        self.assertEqual(second['Recording Method'], '1 (Actively recorded)')
        self.assertEqual((second['Device Manufacturer'], second['Device Type']), ('MakerY', '77'))
        self.assertEqual(second['Record UUID'], '02' * 16)
        self.assertEqual(second['Client Record ID'], 'client-2')
        first = named(headers, steps[0])
        self.assertEqual(first['Recording Method'], '3 (Manual entry)')
        self.assertEqual(first['Device Type'], '1 (Watch)')
        self.assertEqual(by_type['Distance'][0][6:8], (812.5, 'm'))
        self.assertEqual(by_type['Active calories burned'][0][7], 'cal')
        self.assertEqual(by_type['Hydration'][0][7], 'L')

    def test_measurements(self):
        headers, rows, _ = self.go(hc.healthconnect_measurements)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        by_type = {row[1]: row for row in rows}
        self.assertEqual(set(by_type), {'Weight', 'Height', 'Oxygen saturation',
                                        'Resting heart rate', 'Blood pressure'})
        self.assertEqual(by_type['Weight'][2], START)
        self.assertEqual(by_type['Weight'][3], '-05:00')
        self.assertEqual(by_type['Weight'][4:6], (70500.0, 'g'))
        self.assertEqual(by_type['Blood pressure'][4:7], (
            120.0, 'mmHg',
            'diastolic (as stored) 80.0; measurement_location (as stored) 1; '
            'body_position (as stored) 2'))

    def test_heart_rate_samples_join_parent(self):
        headers, rows, _ = self.go(hc.healthconnect_heart_rate)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual([r[2] for r in rows], [70, 74, 71])
        self.assertEqual(rows[1][1], START + datetime.timedelta(seconds=30))
        self.assertEqual(rows[0][3], START)
        self.assertEqual(rows[0][4], START + datetime.timedelta(minutes=1))

    def test_sleep_sessions_and_stages(self):
        headers, sessions, _ = self.go(hc.healthconnect_sleep)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(len(sessions[0]), len(headers))
        self.assertEqual(sessions[0][5:8], ('Night', 'n', 5))
        headers, stages, _ = self.go(hc.healthconnect_sleep_stages)
        self.assertEqual([r[3] for r in stages],
                         ['1 (Awake)', '4 (Light)', '5 (Deep)', '6 (REM)', '42'])
        self.assertEqual(stages[1][1], START + datetime.timedelta(hours=1))
        self.assertEqual(stages[1][2], START + datetime.timedelta(hours=4))
        self.assertEqual(len(headers), len(stages[0]))

    def test_exercise_sessions_and_route(self):
        headers, rows, _ = self.go(hc.healthconnect_exercise)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        record = [named(headers, r) for r in rows]
        running = [r for r in record if r['Exercise Type'].startswith('33')][0]
        self.assertEqual(
            (running['Exercise Type'], running['Title'], running['Notes'], running['Has Route'],
             running['Route Points'], running['Lap Count'], running['Segment Count'],
             running['Rate of Perceived Exertion']),
            ('33 (Running)', 'Morning run', '', 'Yes', 3, 1, 1, 6.0))
        other = [r for r in record if r['Exercise Type'] == '9999'][0]
        self.assertEqual((other['Has Route'], other['Route Points']), ('No', 0))
        headers, points, _ = self.go(hc.healthconnect_exercise_route)
        self.assertEqual(len(points), 3)
        self.assertIn('Latitude', headers)
        route = named(headers, points[0])
        self.assertEqual((route['Latitude'], route['Longitude']), (50.0, 10.0))
        self.assertEqual(route['Session Exercise Type'], '33 (Running)')

    def test_access_read_and_change_logs(self):
        _, access, _ = self.go(hc.healthconnect_access_logs)
        self.assertEqual([(r[2], r[4], r[5]) for r in access],
                         [('com.example.synthetictracker', '0 (Upsert)', '7 (Distance)'),
                          ('com.example.syntheticfit', '2 (Read)', '1 (Steps), 11 (Heart rate)')])
        _, reads, _ = self.go(hc.healthconnect_read_access_logs)
        self.assertEqual((reads[0][2], reads[0][4], reads[0][6]),
                         ('com.example.syntheticfit', 'com.example.synthetictracker',
                          '11 (Heart rate)'))
        self.assertEqual(reads[0][7], START + datetime.timedelta(milliseconds=100))
        _, changes, _ = self.go(hc.healthconnect_change_logs)
        self.assertEqual(changes[0][4:8],
                         ('0 (Upsert)', '1 (Steps)', 2,
                          '000102030405060708090a0b0c0d0e0f, 101112131415161718191a1b1c1d1e1f'))

    def test_older_schema_without_tables_and_empty_store(self):
        root = pathlib.Path(self.folder.name)
        old = make_database(root / 'data/system_ce/10/healthconnect/healthconnect.db', rich=False,
                            drop=('read_access_logs_table', 'change_logs_table',
                                  'sleep_stages_table'))
        for parser in (hc.healthconnect_read_access_logs, hc.healthconnect_change_logs,
                       hc.healthconnect_sleep_stages, hc.healthconnect_activity,
                       hc.healthconnect_measurements, hc.healthconnect_exercise,
                       hc.healthconnect_heart_rate, hc.healthconnect_access_logs):
            headers, rows, _ = run(parser, root, [old])
            self.assertEqual(rows, [], parser.__name__)
            self.assertTrue(headers)

    def test_two_users_are_both_read_and_named(self):
        root = pathlib.Path(self.folder.name)
        second = make_database(root / 'data/system_ce/150/healthconnect/healthconnect.db')
        _, rows, source = run(hc.healthconnect_activity, root, [self.db, second])
        self.assertEqual(sorted({r[0] for r in rows}), ['0', '150'])
        self.assertEqual(len(rows), 18)
        self.assertEqual(source, f'{self.db}\n{second}')

    def test_first_grant_times_plain_xml(self):
        xml = self.db.with_name('health-permissions-first-grant-times.xml')
        xml.write_text(
            "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>"
            '<first-grant-times version="1">'
            '<package name="com.example.a" first-grant-time="2026-01-01T00:00:01.500000Z" />'
            '<package name="com.example.b" first-grant-time="not a time" /></first-grant-times>',
            encoding='utf-8')
        _, rows, _ = self.go(hc.healthconnect_first_grants, [xml])
        self.assertEqual(rows[0][1:4], ('com.example.a', '2026-01-01T00:00:01.500000Z',
                                        datetime.datetime(2026, 1, 1, 0, 0, 1, 500000,
                                                          tzinfo=UTC)))
        self.assertEqual(rows[1][3], '')

    def test_time_helpers_reject_nonsense(self):
        # pylint: disable=protected-access
        self.assertEqual(hc._ms(None), '')
        self.assertEqual(hc._ms('x'), '')
        self.assertEqual(hc._ms(10 ** 30), '')
        self.assertEqual(hc._ms(T0), START)
        self.assertEqual(hc._offset(-19800), '-05:30')


if __name__ == '__main__':
    unittest.main()
