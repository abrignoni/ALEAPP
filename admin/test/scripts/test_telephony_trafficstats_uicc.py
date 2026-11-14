"""UICC log and telephony traffic statistics artifacts, on constructed databases with invented values.

Covers the line parser, the stored-text parsers and the artifacts' behaviour on damaged, empty and
unexpected files: a truncated file, a file that is not SQLite, a database without the table, a missing
column, a second Android user and a large table.
"""
import datetime
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import telephonyTrafficStats, uiccLog  # pylint: disable=wrong-import-position

TRAFFIC_V1 = ('create table trafficstats (_id integer primary key autoincrement, cellId integer not null, '
              'rsrp real not null, techType text not null, networkDetail text not null, bandNumber text not null, '
              'timeStamp text not null, transactionID integer not null, DNSType text not null, '
              'IPAddress text not null, responseTime integer not null, responseCode integer not null, '
              'consumed text not null)')
UICC = 'create table uicclog (_id integer primary key, time timestamp not null, log text not null)'
SIMINFO = 'create table siminfo (_id integer primary key, icc_id text, display_name text, carrier_name text, number text, sim_id integer)'


def make_db(path, statements, rows=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    for statement in statements:
        db.execute(statement)
    for statement, values in rows:
        db.execute(statement, values)
    db.commit()
    db.close()
    return path


def context(root, paths):
    root = pathlib.Path(root)
    return SimpleNamespace(
        get_files_found=lambda: [str(path) for path in paths],
        get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)))


def traffic_row(i, stamp='1788000000000', cell=1100000001, rsrp=-100.0, ips='[ip : 0123456789abcdef0123456789abcdef]'):
    return ('insert into trafficstats values (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (i, cell, rsrp, 'NR', 'SA', 'n41', stamp, 100, 'A', ips, 5, 0, '0'))


class LineParserTest(unittest.TestCase):
    def test_sim_state(self):
        self.assertEqual(uiccLog.parse_uicc_line('SIM_STATE_CHANGED[1] LOADED,null(4)'),
                         ('SIM_STATE_CHANGED', 1, 'LOADED', 4, '', '', '', '', ''))
        self.assertEqual(uiccLog.parse_uicc_line('SIM_STATE_CHANGED[0] ABSENT,null(-1)')[3], -1)

    def test_card_state(self):
        line = 'CardState[1]: CARDSTATE_PRESENT,num_apps=2,SupportedMepMode=MEP_A1,SlotPortMapping={physicalSlotIndex=1, portIndex=0}'
        self.assertEqual(uiccLog.parse_uicc_line(line),
                         ('CardState', 1, 'CARDSTATE_PRESENT', '', 2, 'MEP_A1', 1, 0, ''))

    def test_slot_lines_keep_text(self):
        self.assertEqual(uiccLog.parse_uicc_line('SlotStatus: count=1{x}')[0::8], ('SlotStatus', 'count=1{x}'))
        self.assertEqual(uiccLog.parse_uicc_line('switchSlots: [a, b]')[0::8], ('switchSlots', '[a, b]'))

    def test_unknown_and_damaged_lines(self):
        for text in ('', None, 'SIM_STATE_CHANGED[x] READY,null(2)', 'CardState[0]: truncated', 'SIM_STATE_CHANGED[0] READY',
                     'something else', 'SIM_STATE_CHANGED[0] READY,null(2) trailing'):
            self.assertEqual(uiccLog.parse_uicc_line(text)[0], 'Other', text)


class StoredTextTest(unittest.TestCase):
    def test_address_items(self):
        self.assertEqual(telephonyTrafficStats.parse_address_items('[ip : 0123456789abcdef0123456789abcdef, ip : fedcba9876543210fedcba9876543210]'),
                         '0123456789abcdef0123456789abcdef, fedcba9876543210fedcba9876543210')
        self.assertEqual(telephonyTrafficStats.parse_address_items('[]'), '[]')
        self.assertEqual(telephonyTrafficStats.parse_address_items('garbage'), 'garbage')
        self.assertEqual(telephonyTrafficStats.parse_address_items(None), '')

    def test_stamp_units_and_junk(self):
        expected = datetime.datetime(2026, 8, 29, 10, 40, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(telephonyTrafficStats._stamp('1788000000000'), expected)  # pylint: disable=protected-access
        self.assertEqual(telephonyTrafficStats._stamp('1788000000'), expected)  # pylint: disable=protected-access
        self.assertEqual(telephonyTrafficStats._stamp('1788000000000000'), expected)  # pylint: disable=protected-access
        for junk in (None, '', 'abc', '0', '-5', '1.5', '9' * 40):
            self.assertIsNone(telephonyTrafficStats._stamp(junk), junk)  # pylint: disable=protected-access


class ArtifactTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = pathlib.Path(self.folder.name)

    def run_artifact(self, module, function, paths):
        with patch.object(module, 'logfunc'):
            return getattr(module, function).__wrapped__(context(self.root, paths))

    def traffic(self, relative, rows, schema=TRAFFIC_V1):
        return make_db(self.root / relative, [schema], rows)

    def test_traffic_rows_and_summary(self):
        path = self.traffic('data/user_de/0/com.android.phone/databases/echolocate_system_network_db',
                            [traffic_row(1), traffic_row(2, cell=7, rsrp=-999.0),
                             traffic_row(3, stamp='1788000060000', rsrp=-90.0)])
        headers, rows, source = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [path])
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual(rows[0][0].year, 2026)
        self.assertEqual(rows[0][9], '0123456789abcdef0123456789abcdef')
        self.assertEqual(source, str(path))
        headers, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_cell_summary', [path])
        self.assertEqual(len(rows), 2)
        by_cell = {row[2]: row for row in rows}
        self.assertEqual(by_cell[1100000001][6:9], (2, -100.0, -90.0))
        self.assertEqual(by_cell[7][6:9], (1, None, None))

    def test_traffic_second_user_and_mirror_view(self):
        rows = [traffic_row(1), traffic_row(2)]
        paths = [self.traffic(f'{base}/com.android.phone/databases/echolocate_system_network_db', rows)
                 for base in ('data/user_de/0', 'data_mirror/data_de/null/0')]
        paths.append(self.traffic('data/user_de/150/com.android.phone/databases/echolocate_system_network_db', rows[:1]))
        _, out, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', paths)
        self.assertEqual(sorted(row[-1] for row in out), ['0', '0', '150'])

    def test_traffic_bad_values_are_kept_not_dropped(self):
        path = self.traffic('data/user_de/0/com.android.phone/databases/echolocate_system_network_db',
                            [traffic_row(1, stamp='not-a-time', ips='garbage'), traffic_row(2, stamp='0')])
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [path])
        self.assertEqual([row[0] for row in rows], [None, None])
        self.assertEqual(rows[0][9], 'garbage')
        _, summary, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_cell_summary', [path])
        self.assertEqual(summary[0][6], 2)
        self.assertIsNone(summary[0][0])

    def test_traffic_missing_network_detail_column(self):
        schema = TRAFFIC_V1.replace('networkDetail text not null, ', '')
        path = make_db(self.root / 'data/user_de/0/com.android.phone/databases/echolocate_system_network_db', [schema],
                       [('insert into trafficstats values (?,?,?,?,?,?,?,?,?,?,?,?)',
                         (1, 5, -100.0, 'LTE', '66', '1788000000000', 100, 'A', '[ip : 0123456789abcdef0123456789abcdef]', 5, 0, '0'))])
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [path])
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0][5])

    def test_traffic_damaged_files_give_no_rows_and_no_crash(self):
        folder = self.root / 'data/user_de/0/com.android.phone/databases'
        folder.mkdir(parents=True)
        empty = folder / 'echolocate_system_network_db'
        empty.write_bytes(b'')
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [empty])
        self.assertEqual(rows, [])
        empty.write_bytes(b'not a database' * 100)
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_cell_summary', [empty])
        self.assertEqual(rows, [])
        good = self.traffic('data/user_de/0/x.db', [traffic_row(i) for i in range(1, 200)])
        empty.write_bytes(good.read_bytes()[:3000])
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [empty])
        self.assertLessEqual(len(rows), 199)
        other = make_db(self.root / 'data/user_de/150/com.android.phone/databases/echolocate_system_network_db',
                        ['create table other (a)'])
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [other])
        self.assertEqual(rows, [])

    def test_traffic_large_table(self):
        statements = [traffic_row(i, stamp=str(1788000000000 + i * 1000), cell=i % 300) for i in range(1, 60001)]
        path = self.traffic('data/user_de/0/com.android.phone/databases/echolocate_system_network_db', statements)
        _, rows, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_trafficstats', [path])
        self.assertEqual(len(rows), 60000)
        _, summary, _ = self.run_artifact(telephonyTrafficStats, 'get_telephony_cell_summary', [path])
        self.assertEqual(sum(row[6] for row in summary), 60000)

    def uicc(self, relative, lines):
        rows = [('insert into uicclog values (?,?,?)', (i, when, log)) for i, (when, log) in enumerate(lines, 1)]
        return make_db(self.root / relative, [UICC], rows)

    def test_uicc_rows_and_history(self):
        base = 'data/user_de/0/'
        log = self.uicc(base + 'com.android.phone/databases/uicc_log.db', [
            ('2026-01-01 10:00:00', 'SIM_STATE_CHANGED[0] READY,null(2)'),
            ('2026-01-01 10:00:01', 'SIM_STATE_CHANGED[0] LOADED,null(2)'),
            ('2026-01-05 09:00:00', 'SIM_STATE_CHANGED[0] ABSENT,null(-1)'),
            ('2026-01-06 09:00:00', 'SIM_STATE_CHANGED[0] LOADED,null(7)'),
            ('2026-01-06 08:59:00', 'SIM_STATE_CHANGED[0] READY,null(7)'),
            ('2026-01-06 09:01:00', 'free text')])
        tel = make_db(self.root / (base + 'com.android.providers.telephony/databases/telephony.db'), [SIMINFO],
                      [('insert into siminfo values (?,?,?,?,?,?)', (2, '8900000000000000002', 'Example', 'Carrier', '', 0))])
        wal = self.root / (base + 'com.android.phone/databases/uicc_log.db-journal')
        wal.write_bytes(b'')
        headers, rows, source = self.run_artifact(uiccLog, 'get_uicc_log', [log, wal, tel])
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual(source, str(log))
        headers, rows, _ = self.run_artifact(uiccLog, 'get_uicc_sim_history', [log, wal, tel])
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        first, second = rows
        self.assertEqual(first[:6], ('2026-01-01 10:00:00', '2026-01-01 10:00:01', 0, 2, 1, 1))
        self.assertEqual((first[6], first[9]), ('Example', '8900000000000000002'))
        self.assertEqual(second[:6], ('2026-01-06 08:59:00', '2026-01-06 09:00:00', 0, 7, 1, 1))
        self.assertEqual(second[6:14], ('',) * 8)

    def test_uicc_damaged_and_missing_inputs(self):
        folder = self.root / 'data/user_de/0/com.android.phone/databases'
        folder.mkdir(parents=True)
        damaged = folder / 'uicc_log.db'
        for content in (b'', b'x' * 5000):
            damaged.write_bytes(content)
            for function in ('get_uicc_log', 'get_uicc_sim_history'):
                _, rows, _ = self.run_artifact(uiccLog, function, [damaged])
                self.assertEqual(rows, [])
        other = make_db(self.root / 'data/user_de/150/com.android.phone/databases/uicc_log.db', ['create table other (a)'])
        _, rows, _ = self.run_artifact(uiccLog, 'get_uicc_log', [other])
        self.assertEqual(rows, [])
        _, rows, _ = self.run_artifact(uiccLog, 'get_uicc_sim_history', [])
        self.assertEqual(rows, [])

    def test_uicc_stored_time_not_converted_and_second_user(self):
        a = self.uicc('data/user_de/0/com.android.phone/databases/uicc_log.db', [('2026-03-01 01:02:03', 'SIM_STATE_CHANGED[1] LOADED,null(3)')])
        b = self.uicc('data/user_de/150/com.android.phone/databases/uicc_log.db', [('2026-03-02 01:02:03', 'SIM_STATE_CHANGED[1] LOADED,null(3)')])
        _, rows, _ = self.run_artifact(uiccLog, 'get_uicc_log', [b, a])
        self.assertEqual(sorted((row[0], row[-1]) for row in rows), [('2026-03-01 01:02:03', '0'), ('2026-03-02 01:02:03', '150')])
        _, rows, _ = self.run_artifact(uiccLog, 'get_uicc_sim_history', [b, a])
        self.assertEqual(sorted(row[-1] for row in rows), ['0', '150'])


if __name__ == '__main__':
    unittest.main()
