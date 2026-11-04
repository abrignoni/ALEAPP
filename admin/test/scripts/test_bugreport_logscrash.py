"""Android bug report text: logs, kernel log, thread dumps, tombstones, dropbox, reset reasons and vendor services."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import struct
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as base
from admin.test.scripts import bugreport_logscrash_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts import dumpstate_logscrash as logscrash
from scripts.artifacts import bugreportLogsCrash as artifacts


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


def scan_text(text):
    report = reader.Report(reader.Source('memory', ''))
    data = text.encode('utf-8') if isinstance(text, str) else text
    reader.scan_lines(reader.iter_lines(io.BytesIO(data)), report)
    report.finish()
    return report


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


def tiny(sections, zone='Europe/Paris', report='2026-11-02 10:15:30'):
    """A report text with the given sections after the properties."""
    return (base.BANNER.format(report=report) + '\n' + base.properties('a16', zone, 'reboot,x,1790000000') + sections)


class RegistrationTests(unittest.TestCase):
    def test_readers_are_registered_once_and_listed_in_the_section_index(self):
        for cls in logscrash.READERS:
            self.assertEqual(reader.READERS.count(cls), 1, cls.__name__)
            self.assertIn((cls.kind, cls.name), reader.READ_BY, cls.__name__)
        self.assertEqual(reader.READ_BY[('command', 'SYSTEM LOG')], 'System Log')
        for service in ('knoxguard_service', 'knoxcustom'):         # read by the security artifacts only, each fact once
            self.assertNotIn(service, logscrash.VENDOR_SERVICES)
            self.assertNotIn('Vendor Service Lines', reader.READ_BY[('service', service)])


class LogcatTests(unittest.TestCase):
    def test_line_with_a_uid_column(self):
        parsed = logscrash.parse_logcat_line('11-01 21:05:02.250 10201  2201  2260 D ExampleChat: invented message one')
        self.assertEqual(parsed, ('11-01 21:05:02.250', '10201', 2201, 2260, 'D', 'ExampleChat', 'invented message one'))
        parsed = logscrash.parse_logcat_line('11-01 21:05:02.250  root   501   501 W init    : padded tag line')
        self.assertEqual((parsed[1], parsed[5], parsed[6]), ('root', 'init', 'padded tag line'))

    def test_line_without_a_uid_column_and_with_a_year(self):
        parsed = logscrash.parse_logcat_line('11-01 21:05:02.250  2201  2260 I Tag: plain threadtime')
        self.assertEqual(parsed, ('11-01 21:05:02.250', '', 2201, 2260, 'I', 'Tag', 'plain threadtime'))
        parsed = logscrash.parse_logcat_line('2026-11-01 21:05:02.250 1000 2201 2260 I Tag: with year')
        self.assertEqual((parsed[0], parsed[1]), ('2026-11-01 21:05:02.250', '1000'))

    def test_tags_and_empty_messages(self):
        self.assertEqual(logscrash.split_tag('Tag With Spaces: message'), ('Tag With Spaces', 'message'))
        self.assertEqual(logscrash.split_tag('EmptyMessage:'), ('EmptyMessage', ''))
        self.assertEqual(logscrash.split_tag('a: b: c'), ('a', 'b: c'))
        self.assertEqual(logscrash.split_tag('no separator'), ('', 'no separator'))
        self.assertIsNone(logscrash.parse_logcat_line('--------- beginning of main'))
        self.assertIsNone(logscrash.parse_logcat_line('    a continuation'))
        self.assertIsNone(logscrash.parse_logcat_line('11-01 21:05:02 too short a time'))

    def test_sections_buffers_and_lines_that_are_not_rows(self):
        report = scan_text(fixture.build_report('l16'))
        rows = logscrash.tables(report).system_log
        self.assertEqual(len(rows), 13)
        self.assertEqual({row[0] for row in rows}, {'SYSTEM LOG', 'SYSTEM LOG AFTER DONE'})
        self.assertEqual([row[8] for row in rows[:3]], ['crash', 'system', 'system'])
        self.assertEqual([row[8] for row in rows if row[7].startswith('silent')], ['main'])
        colon = [row for row in rows if row[6] == 'ExampleDaemon'][0]
        self.assertEqual(colon[7], 'error with a colon: inside the message')       # the next line has no header: not a row
        self.assertEqual((colon[2], colon[3], colon[4], colon[5]), ('shell', 600, 600, 'E'))
        self.assertEqual(logscrash.tables(report).unparsed, {'SYSTEM LOG': 1, 'EVENT LOG': 1})
        trailing = [row for row in rows if row[7].startswith('message with trailing')][0]
        self.assertEqual(trailing[7], 'message with trailing text   ')
        self.assertEqual([row for row in rows if row[6] == 'EmptyMessage'][0][7], '')
        self.assertEqual([row[9] for row in rows][:2], sorted(row[9] for row in rows)[:2])

    def test_event_log_keeps_the_event_name_as_tag(self):
        report = scan_text(fixture.build_report('l16'))
        rows = logscrash.tables(report).event_log
        self.assertEqual([row[6] for row in rows], ['am_proc_bound', 'notification_enqueue', 'power_partial_wake_state'])
        self.assertEqual(rows[0][7], '[0,4321,com.example.user.chat]')
        self.assertEqual(rows[1][7], '[10300,1,com.example.user.chat,1,invented-key')
        self.assertEqual({row[8] for row in rows}, {'events'})

    def test_android_10_layout_has_no_uid(self):
        report = scan_text(fixture.build_report('l10', newline='\r\n'))
        rows = logscrash.tables(report).system_log
        self.assertEqual(len(rows), 3)
        self.assertEqual({row[2] for row in rows}, {''})
        self.assertEqual({row[0] for row in rows}, {'SYSTEM LOG'})

    def test_year_comes_from_the_report_time(self):
        report = scan_text(fixture.build_report('l16', zone='Europe/Paris'))
        self.assertEqual(logscrash.logcat_utc(report, '11-01 21:05:02.250'), utc(2026, 11, 1, 20, 5, 2, 250000))
        self.assertEqual(logscrash.logcat_utc(report, '11-03 00:00:00.000'), utc(2026, 11, 2, 23, 0, 0))     # less than a day after
        self.assertEqual(logscrash.logcat_utc(report, '11-04 01:00:00.000'), utc(2025, 11, 4, 0, 0, 0))      # more than a day after
        self.assertEqual(logscrash.logcat_utc(report, '2026-11-01 21:05:02.250'), utc(2026, 11, 1, 20, 5, 2, 250000))
        self.assertIsNone(logscrash.logcat_utc(report, '11-01 21:05'))

    def test_no_zone_gives_no_utc(self):
        report = scan_text(fixture.build_report('l16', zone=''))
        self.assertIsNone(logscrash.logcat_utc(report, '11-01 21:05:02.250'))

    def test_the_minute_cache_gives_the_same_value_as_a_direct_conversion(self):
        report = scan_text(fixture.build_report('l16', zone='Asia/Kolkata'))
        for text in ('11-01 21:05:02.250', '11-01 21:05:59.999', '11-01 21:06:00.001'):
            _full, direct = report.setting_change_time(text)
            self.assertEqual(logscrash.logcat_utc(report, text), direct)

    def test_a_table_stops_at_the_row_limit_with_one_warning(self):
        text = fixture.build_report('l16')
        with mock.patch.object(logscrash, 'MAX_ROWS', 5):
            report = scan_text(text)
        self.assertEqual(len(logscrash.tables(report).system_log), 5)
        self.assertEqual(len([w for w in report.warnings if w.startswith('system_log: more than 5 rows')]), 1)

    def test_a_command_stopped_by_a_time_limit_is_reported_once(self):
        report = scan_text(fixture.build_cut_report())
        self.assertEqual([w for w in report.warnings if 'stopped by a time limit' in w],
                         ['SYSTEM LOG: the command was stopped by a time limit, the rows may be partial'])
        self.assertEqual(logscrash.tables(report).cut_sections, {'SYSTEM LOG'})
        self.assertFalse([row for row in logscrash.tables(report).system_log if '***' in row[7]])


class StampTests(unittest.TestCase):
    def test_offset_and_zone(self):
        report = scan_text(fixture.build_report('l16', zone='Europe/Paris'))
        self.assertEqual(logscrash.stamp_utc(report, '2026-02-03 10:11:12+0700'), (utc(2026, 2, 3, 3, 11, 12), ''))
        self.assertEqual(logscrash.stamp_utc(report, '2026-10-30 07:00:00-0330'), (utc(2026, 10, 30, 10, 30), ''))
        self.assertEqual(logscrash.stamp_utc(report, '2026-11-02 10:15:00.123456789+0000'), (utc(2026, 11, 2, 10, 15, 0, 123456), ''))
        self.assertEqual(logscrash.stamp_utc(report, '2026-11-02 10:15:00'), (utc(2026, 11, 2, 9, 15), ''))
        self.assertEqual(logscrash.stamp_utc(report, ''), (None, ''))
        self.assertEqual(logscrash.stamp_utc(report, 'not a time')[0], None)
        moment, note = logscrash.stamp_utc(report, '1970-01-01 00:00:44+0000')
        self.assertEqual((moment, note), (None, logscrash.NOTE_PRE_2009))

    def test_no_zone(self):
        report = scan_text(fixture.build_report('l16', zone=''))
        self.assertEqual(logscrash.stamp_utc(report, '2026-11-02 10:15:00'), (None, reader.NOTE_NO_ZONE))
        self.assertEqual(logscrash.stamp_utc(report, '2026-11-02 10:15:00+0000')[0], utc(2026, 11, 2, 10, 15))


class KernelTests(unittest.TestCase):
    def test_line_forms(self):
        self.assertEqual(logscrash.parse_kernel_line('<6>[12345.678901][T21461] invented_driver: x'),
                         ('12345.678901', '6', 'T21461', 'invented_driver: x'))
        self.assertEqual(logscrash.parse_kernel_line('<6>[12345.678950][ T9474] [wlan] y'), ('12345.678950', '6', 'T9474', '[wlan] y'))
        self.assertEqual(logscrash.parse_kernel_line('<5>[    1.500000] c1 invented'), ('1.500000', '5', 'c1', 'invented'))
        self.assertEqual(logscrash.parse_kernel_line('[   62.000001][    T1] z'), ('62.000001', '', 'T1', 'z'))
        self.assertEqual(logscrash.parse_kernel_line('[    0.785860]  [ 2:  kworker/u16:2:   86] m'),
                         ('0.785860', '', '2:  kworker/u16:2:   86', 'm'))
        self.assertEqual(logscrash.parse_kernel_line('<6>[12348.000000]'), ('12348.000000', '6', '', ''))
        self.assertEqual(logscrash.parse_kernel_line('a line without a stamp'), ('', '', '', 'a line without a stamp'))
        self.assertEqual(logscrash.parse_kernel_line(' 0.785203]  [ 2: x] cut line')[0], '')
        self.assertEqual(logscrash.parse_kernel_line('<6>[1.0] c0')[3], 'c0')     # a lone cpu word with no text is the message

    def test_sections(self):
        report = scan_text(fixture.build_report('l16'))
        rows = logscrash.tables(report).kernel_lines
        self.assertEqual([row for row in rows if row[0] == 'KERNEL LOG'][1], ('KERNEL LOG', '12345.678901', '6', 'T21461',
                                                                               'invented_driver: input id(0) value(1)',
                                                                               rows[1][5]))
        self.assertEqual(len([row for row in rows if row[0] == 'KERNEL LOG']), 7)       # the blank line is not a row
        self.assertEqual(len([row for row in rows if row[0] == 'LAST KMSG']), 3)
        self.assertEqual([row[1] for row in rows if row[0] == 'LAST KMSG'], ['', '0.785860', '62.000001'])
        report = scan_text(fixture.build_report('l10', newline='\r\n'))
        self.assertEqual({row[3] for row in logscrash.tables(report).kernel_lines if row[1] == '0.000000'}, {'c0'})


class TraceTests(unittest.TestCase):
    def rows(self, layout='l16'):
        return logscrash.tables(scan_text(fixture.build_report(layout))).anr_threads

    def test_native_and_java_threads(self):
        rows = self.rows()
        by_name = {}
        for row in rows:
            by_name.setdefault(row[5], row)
        self.assertEqual(len(rows), 6)
        native = by_name['binder:1099_2']
        self.assertEqual(native[:5], ('VM TRACES JUST NOW', '1099', '/apex/com.example.runtime/bin/exampled',
                                      '2026-11-02 10:15:00.123456789+0000', ''))
        self.assertEqual((native[8], native[10], native[9], native[18]), (None, 1099, '', 2))
        self.assertTrue(native[17].startswith('#00 pc 3456789abc23229a'))
        main = by_name['main']
        self.assertEqual((main[1], main[6], main[7], main[8], main[9], main[10], main[11], main[12], main[13]),
                         ('2201', False, 5, 1, 'Native', 2201, -10, 'top-app', 'S'))
        self.assertEqual((main[14], main[15], main[16], main[18]), (17, 9, 3, 3))
        self.assertTrue(main[17].startswith('native: #00 pc 34abaa12'))
        daemon = by_name['ReferenceQueueDaemon']
        self.assertEqual((daemon[6], daemon[9], daemon[18]), (True, 'Waiting', 2))
        self.assertTrue(daemon[17].startswith('at java.lang.Object.wait'))
        unattached = by_name['NativeHelper']
        self.assertEqual((unattached[9], unattached[10], unattached[8]), ('(not attached)', 2210, None))

    def test_the_waiting_channel_block_gives_no_threads(self):
        names = [row[5] for row in self.rows()]
        self.assertNotIn('not a thread', names)
        self.assertEqual(names.count('main'), 2)        # one in the just now dump and one in the last ANR dump

    def test_subject_comes_with_the_section_that_prints_it(self):
        rows = self.rows()
        last = [row for row in rows if row[0] == 'VM TRACES AT LAST ANR']
        self.assertEqual(len(last), 1)
        self.assertEqual(last[0][4], 'Input dispatching timed out (example.user.chat/.Main)')
        self.assertEqual(last[0][9], 'Blocked')
        self.assertEqual({row[4] for row in rows if row[0] == 'VM TRACES JUST NOW'}, {''})

    def test_android_10_dump_without_an_offset(self):
        rows = self.rows('l10')
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0][3], rows[0][5], rows[0][9], rows[0][11]), ('2026-11-02 10:15:00', 'main', 'Native', -1))

    def test_trace_text_of_a_member(self):
        rows, full = logscrash.read_trace_text('anr_x', fixture.anr_file().split('\n'), 100)
        self.assertEqual([(row[0], row[4], row[5]) for row in rows],
                         [('anr_x', 'No response to onStopJob, (1234567, com.example.user.chat)', 'main'),
                          ('anr_x', 'No response to onStopJob, (1234567, com.example.user.chat)', 'androidx.work-1')])
        self.assertFalse(full)
        rows, full = logscrash.read_trace_text('anr_x', fixture.anr_file().split('\n'), 1)
        self.assertEqual((len(rows), full), (1, True))

    def test_nothing_to_read(self):
        self.assertEqual(logscrash.read_trace_text('x', [], 10), ([], False))
        self.assertEqual(logscrash.read_trace_text('x', ['', 'garbage', '"quoted line without a thread'], 10), ([], False))


class DropboxTests(unittest.TestCase):
    def rows(self, layout='l16'):
        return logscrash.tables(scan_text(fixture.build_report(layout))).dropbox_entries

    def test_service_listing(self):
        rows = [row for row in self.rows() if row[0] == 'DUMP OF SERVICE dropbox']
        self.assertEqual([(row[1], row[2], row[3], row[4]) for row in rows],
                         [('2026-11-01 20:00:00', 'system_app_crash', 'text', 1885),
                          ('2026-11-01 20:01:00', 'keymaster', 'contents lost', None),
                          ('2026-11-01 20:02:00', 'storage_trim', 'text', 15),
                          ('2026-11-01 20:03:00', 'SYSTEM_RESTART', 'compressed text', 514),
                          ('2026-11-01 20:04:00', 'system_server_wtf', 'data', 20)])
        self.assertEqual(rows[0][12], 'Process: com.example.user.chat/PID: 4321/UID: 10300/Flags: 0x1 ...')
        self.assertEqual(rows[1][12], '')
        self.assertEqual(rows[2][12], 'example 0 1234')

    def test_printed_entries(self):
        rows = [row for row in self.rows() if row[0] == 'DROPBOX SYSTEM APP CRASHES']
        self.assertEqual(len(rows), 2)
        first, second = rows
        self.assertEqual((first[2], first[3], first[4], first[5], first[6], first[7]),
                         ('system_app_crash', 'text', 1885, 'com.example.user.chat', '4321', '10300'))
        self.assertEqual(first[8], 'com.example.user.chat v12 (1.2.3); com.example.user.helper v3 (0.3)')
        self.assertEqual((first[9], first[10]), ('No', ''))
        self.assertEqual(first[11], 'java.lang.IllegalStateException: invented crash message')
        self.assertEqual((second[5], second[9], second[10], second[11]),
                         ('com.example.user.chat:sync', 'Yes', 'invented subject line', 'java.lang.RuntimeException: second invented crash'))

    def test_a_tag_with_no_entries_gives_no_rows_and_no_error(self):
        report = scan_text(fixture.build_report('l16'))
        self.assertFalse([row for row in logscrash.tables(report).dropbox_entries if row[0] == 'DROPBOX SYSTEM SERVER CRASHES'])
        self.assertFalse([row for row in logscrash.tables(report).dropbox_entries if row[0] == 'DROPBOX SYSTEM WATCHDOG CRASHES'])
        totals = {name: (contents, maximum) for name, contents, maximum in logscrash.tables(report).dropbox_totals}
        self.assertEqual(totals['dropbox'], ('Drop box contents: 5 entries', 'Max entries: 1000'))
        self.assertEqual(totals['DROPBOX SYSTEM SERVER CRASHES'], ('Drop box contents: 5 entries', 'Max entries: 1000'))

    def test_android_10_has_two_print_sections(self):
        names = {row[0] for row in self.rows('l10')}
        self.assertEqual(names, {'DUMP OF SERVICE dropbox', 'DROPBOX SYSTEM APP CRASHES'})

    def test_an_entry_without_headers_keeps_its_first_line(self):
        section = ('------ DROPBOX SYSTEM APP CRASHES (/system/bin/dumpsys -T 30000 dropbox -p system_app_crash) ------\n'
                   'Drop box contents: 1 entries\n\n' + '=' * 40 + '\n2026-11-01 20:00:00 system_app_crash (text, 12 bytes)\n'
                   'plain body line\nmore\n' + '=' * 40 + '\n')
        rows = logscrash.tables(scan_text(tiny(section))).dropbox_entries
        self.assertEqual((rows[0][2], rows[0][5], rows[0][11]), ('system_app_crash', '', 'plain body line'))


class ResetTests(unittest.TestCase):
    def rows(self):
        return logscrash.tables(scan_text(fixture.build_report('l16'))).reset_events

    def test_ap_reset_info_lines(self):
        rows = [row for row in self.rows() if row[0] == 'AP RESET INFO EXTEND']
        self.assertEqual(len(rows), 7)                      # the binary first line and blank lines are not rows
        self.assertEqual(tuple(rows[0][1:6]), ('2026-02-03 10:11:12+0700', 'event line', 'ON', 'RP', 'EXAMPLEBUILD1 [13]'))
        self.assertEqual(tuple(rows[1][3:6]), ('SHUTDOWN', '', 'REASON: [FactoryTest] invented reset [13] ,1'))
        self.assertEqual((rows[3][3], rows[3][4], rows[3][5]), ('LPM', '', ''))
        self.assertEqual(tuple(rows[5][3:5]), ('PLATFORM', 'PF_SR'))

    def test_power_off_records(self):
        rows = [row for row in self.rows() if row[0] == 'POWER OFF RESET REASON']
        records = [row for row in rows if row[2] == 'record']
        self.assertEqual([(row[1], row[3], row[5]) for row in records],
                         [('26/09/20 02:12:41', 'reason', 'no power'), ('26/09/22 16:03:21', 'reason', 'invented-low-memory')])
        self.assertEqual(records[0][6].split(' | ')[0], 'com.example.server.BatteryService$16.run(example:160)')
        self.assertEqual(len(records[0][6].split(' | ')), 3)
        self.assertEqual(records[1][6].split(' | ')[0], 'com.example.server.power.PowerManagerService$4.run(example:43)')
        events = [row for row in rows if row[2] == 'event line']
        self.assertEqual(tuple(events[0][1:6]), ('2026-09-20 02:12:51+0000', 'event line', 'SHUTDOWN', '', 'REASON: no power [64]'))
        self.assertEqual(len(events), 3)                    # the "terminating init service" line is not one
        backup = [row for row in self.rows() if row[0] == 'POWER OFF RESET REASON BACKUP']
        self.assertEqual(len(backup), 1)
        self.assertEqual(backup[0][6], '')                  # the only frame is a ShutdownThread frame

    def test_record_time_text(self):
        self.assertEqual(logscrash.record_time_text('26/09/20 02:12:41'), '2026-09-20 02:12:41')
        self.assertEqual(logscrash.record_time_text('2026-09-20 02:12:41'), '')


class VendorTests(unittest.TestCase):
    def test_times_in_the_first_eighty_characters(self):
        self.assertEqual(logscrash.vendor_time('2026-02-03 10:13:14 : [action] x'), '2026-02-03 10:13:14')
        self.assertEqual(logscrash.vendor_time('  02/03/2026 03:05:06.789   > Created'), '02/03/2026 03:05:06.789')
        self.assertEqual(logscrash.vendor_time('lastControlTime: 2026/08/14 18:20:30 , packageName: x'), '2026/08/14 18:20:30')
        self.assertEqual(logscrash.vendor_time('  02/03/*026 02:54:29.863   > Created'), '02/03/*026 02:54:29.863')
        self.assertEqual(logscrash.vendor_time('05-09 08:41:12.345 D [NFC_SE]x'), '05-09 08:41:12.345')
        self.assertEqual(logscrash.vendor_time('[2026-10-30 08:15:30.111] L/ab12/x'), '2026-10-30 08:15:30.111')
        self.assertEqual(logscrash.vendor_time('+ 2026/10/24 20:21:52:209\t3\tx'), '2026/10/24 20:21:52:209')
        self.assertEqual(logscrash.vendor_time('no time here'), '')
        self.assertEqual(logscrash.vendor_time('x' * 90 + ' 2026-02-03 10:13:14'), '')

    def test_conversion_to_wall_time(self):
        self.assertEqual(logscrash.vendor_time_to_wall('02/03/2026 03:05:06.789'), ('2026-02-03 03:05:06.789', ''))
        self.assertEqual(logscrash.vendor_time_to_wall('2026/10/24 20:21:52:209'), ('2026-10-24 20:21:52.209', ''))
        self.assertEqual(logscrash.vendor_time_to_wall('2026-10-25T06:06:22'), ('2026-10-25 06:06:22', ''))
        self.assertEqual(logscrash.vendor_time_to_wall('02/03/*026 02:54:29.863'), ('', logscrash.NOTE_MASKED_YEAR))
        self.assertEqual(logscrash.vendor_time_to_wall('05-09 08:41:12.345'), ('', logscrash.NOTE_NO_YEAR))
        self.assertEqual(logscrash.vendor_time_to_wall(''), ('', ''))

    def test_lines_of_the_listed_services_only(self):
        report = scan_text(fixture.build_report('l16'))
        rows = logscrash.tables(report).vendor_lines
        self.assertEqual({row[0] for row in rows}, {'SveService', 'secims', 'sec_location', 'sem_wifi',
                                                    'nfc SamsungExtension', 'persona'})
        self.assertFalse([row for row in rows if row[0] in ('knoxguard_service', 'knoxcustom')])   # read by the Security artifacts
        sve = [row for row in rows if row[0] == 'SveService']
        self.assertEqual([row[1] for row in sve], [0, 2, 2])
        persona = [row for row in rows if row[0] == 'persona']
        self.assertEqual(persona[-1][3], '2010.01.01.00.01.22')

    def test_encoded_blobs_are_counted_not_kept(self):
        report = scan_text(fixture.build_report('l16'))
        nfc = [row for row in logscrash.tables(report).vendor_lines if row[0] == 'nfc SamsungExtension']
        self.assertEqual(len(nfc), 4)
        self.assertEqual(logscrash.tables(report).vendor_blobs, {'nfc SamsungExtension': 3})
        self.assertFalse([row for row in nfc if row[3].startswith('QmFzZTY0')])

    def test_the_line_limit_gives_one_warning(self):
        with mock.patch.object(logscrash, 'VENDOR_MAX_LINES', 2):
            report = scan_text(fixture.build_report('l16'))
        self.assertEqual(len([row for row in logscrash.tables(report).vendor_lines if row[0] == 'secims']), 2)
        self.assertEqual(len([w for w in report.warnings if w.startswith('secims: more than 2 lines')]), 1)

    def test_the_cut_dumps_carry_a_timeout_marker(self):
        report = scan_text(fixture.build_cut_report())
        cut = sorted(section.name for section in report.sections if section.kind == 'service' and section.timeout_ms)
        self.assertEqual(cut, ['knoxguard_service', 'sem_wifi'])


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def stage(self, name, data):
        path = Path(self.work) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data.encode('utf-8') if isinstance(data, str) else data)
        return path

    def run_artifact(self, function, *paths):
        return function.__wrapped__(Context(self.work, paths))

    FUNCTIONS = (artifacts.bugreport_system_log, artifacts.bugreport_event_log, artifacts.bugreport_kernel_log,
                 artifacts.bugreport_anr_threads, artifacts.bugreport_tombstones, artifacts.bugreport_dropbox_entries,
                 artifacts.bugreport_reset_reasons, artifacts.bugreport_vendor_services)

    def test_row_width_matches_the_headers(self):
        text = self.stage('Dump/dumpstate.txt', fixture.build_report('l16'))
        zipped = self.stage('Dump/bugreport-example-2026-11-02.zip', fixture.bug_report_zip('l16'))
        for function in self.FUNCTIONS:
            for path in (text, zipped):
                headers, rows, source_path = self.run_artifact(function, path)
                self.assertTrue(rows or (function is artifacts.bugreport_tombstones and path is text), function.__name__)
                self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
                self.assertEqual(source_path, str(path))

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)

    def test_a_text_without_these_sections_gives_no_rows(self):
        path = self.stage('Dump/dumpstate.txt', base.BANNER.format(report='2026-11-02 10:15:30'))
        for function in self.FUNCTIONS:
            self.assertEqual(self.run_artifact(function, path)[1], [])

    def test_system_log_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_system_log, path)
        self.assertEqual(headers[0], ('Time (UTC)', 'datetime'))
        first = [row for row in rows if row[7] == 'invented message one'][0]
        self.assertEqual(first[:8], (utc(2026, 11, 1, 20, 5, 2, 250000), '11-01 21:05:02.250', '10201', 2201, 2260, 'D',
                                     'ExampleChat', 'invented message one'))
        self.assertEqual((first[8], first[9], first[11]), ('system', 'SYSTEM LOG', 'Dump/dumpstate.txt'))
        self.assertEqual([row[0] for row in rows if row[1] == '11-04 01:00:00.000'], [utc(2025, 11, 4, 0, 0, 0)])
        self.assertEqual({row[9] for row in rows}, {'SYSTEM LOG', 'SYSTEM LOG AFTER DONE'})

    def test_event_log_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_event_log, path)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][6], 'am_proc_bound')
        self.assertNotIn('Source Section', headers)             # one section: the column would hold one value
        self.assertEqual(headers[-2:], ('Source Line', 'Source File'))

    def test_lines_that_are_not_rows_are_logged(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append), mock.patch.object(reader, 'say_once', lambda log, m: log(m)):
            self.run_artifact(artifacts.bugreport_system_log, path)
            self.run_artifact(artifacts.bugreport_event_log, path)
            self.run_artifact(artifacts.bugreport_vendor_services, path)
        text = '\n'.join(messages)
        self.assertIn('1 non-blank lines of SYSTEM LOG are not in logcat form and are not rows', text)
        self.assertIn('1 non-blank lines of EVENT LOG are not in logcat form and are not rows', text)
        self.assertIn('3 encoded blob lines of nfc SamsungExtension are not rows', text)

    def test_kernel_log_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_kernel_log, path)
        self.assertEqual(rows[1][:5], ('12345.678901', '6', 'T21461', 'invented_driver: input id(0) value(1)', 'KERNEL LOG'))
        self.assertEqual(len(rows), 10)

    def test_anr_thread_rows_include_the_zip_members(self):
        zipped = self.stage('Dump/bugreport-example-2026-11-02.zip', fixture.bug_report_zip('l16', zone='Europe/Paris'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_anr_threads, zipped)
        sections = {}
        for row in rows:
            sections[row[19]] = sections.get(row[19], 0) + 1
        self.assertEqual(sections, {'VM TRACES JUST NOW': 5, 'VM TRACES AT LAST ANR': 1,
                                    'FS/data/anr/anr_2026-10-14-04-23-05-111': 2})
        member = [row for row in rows if row[19].startswith('FS/data/anr')][0]
        self.assertEqual((member[0], member[1], member[2], member[3], member[4]),
                         (utc(2026, 10, 14, 4, 22, 59, 123456), '2026-10-14 04:22:59.123456789+0000', '4321',
                          'com.example.user.chat', 'No response to onStopJob, (1234567, com.example.user.chat)'))
        self.assertEqual(member[21], 'Dump/bugreport-example-2026-11-02.zip')
        offset = [row for row in rows if row[1] == '2026-11-02 10:15:01.000000001+0100'][0]
        self.assertEqual(offset[0], utc(2026, 11, 2, 9, 15, 1, 0))

    def test_tombstone_rows_come_from_the_zip(self):
        zipped = self.stage('Dump/bugreport-example-2026-11-02.zip', fixture.bug_report_zip('l16'))
        text = self.stage('Dump2/dumpstate.txt', fixture.build_report('l16'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_tombstones, zipped, text)
        self.assertEqual(len(rows), 6)
        self.assertEqual([row[13] for row in rows], ['FS/data/tombstones/tombstone_00', 'FS/data/tombstones/tombstone_00.pb',
                                                     'FS/data/tombstones/tombstone_01', 'FS/data/tombstones/tombstone_02',
                                                     'FS/data/tombstones/tombstone_02.pb', 'FS/data/tombstones/tombstone_03.pb'])
        text_row, proto_row, empty_row, wrapped_text, wrapped_proto, bad_proto = rows
        self.assertEqual(text_row[0], utc(2026, 10, 9, 18, 7, 22, 123456))
        self.assertEqual(text_row[1:12], ('com.example.user.nfc', 'com.example.user.nfc', 'exampleThread', '5001', '5002', '1055',
                                          'signal 6 (SIGABRT), code -1 (SI_QUEUE), fault addr --------',
                                          'invented abort message', '5551s',
                                          'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys', 'text'))
        self.assertEqual(proto_row[0], text_row[0])
        self.assertEqual(proto_row[1:12], ('com.example.user.nfc', 'com.example.user.nfc --arg', '', '5001', '5002', '1055',
                                           'signal 6 (SIGABRT), code -1 (SI_QUEUE)', 'invented abort message', '5551s',
                                           'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys',
                                           'protobuf'))
        self.assertEqual(empty_row[0], None)
        self.assertEqual((empty_row[1], empty_row[11], empty_row[12]), ('', 'text', 0))
        self.assertEqual(wrapped_text[0], utc(2026, 10, 8, 15, 0, 0))
        self.assertEqual(wrapped_proto[1], '')              # the wrapped message is not unwrapped here
        self.assertEqual(bad_proto[1], '')
        self.assertTrue(all(row[14] == 'Dump/bugreport-example-2026-11-02.zip' for row in rows))

    def test_a_tombstone_that_does_not_decode_is_logged(self):
        zipped = self.stage('Dump/bugreport-example-2026-11-02.zip', fixture.bug_report_zip('l16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_tombstones, zipped)
        self.assertTrue([m for m in messages if 'tombstone_01 (0 bytes) holds no tombstone fields' in m])
        self.assertTrue([m for m in messages if 'tombstone_03.pb (11 bytes) holds no tombstone fields' in m])

    def test_a_zip_with_a_text_only_has_no_members(self):
        path = self.stage('Dump/bugreport-example-2026-11-02.zip', fixture.bug_report_zip('l16', members=False))
        self.assertEqual(self.run_artifact(artifacts.bugreport_tombstones, path)[1], [])
        rows = self.run_artifact(artifacts.bugreport_anr_threads, path)[1]
        self.assertEqual({row[19] for row in rows}, {'VM TRACES JUST NOW', 'VM TRACES AT LAST ANR'})

    def test_dropbox_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16', zone='Europe/Paris'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_dropbox_entries, path)
        self.assertEqual(len(rows), 7)
        printed = [row for row in rows if row[13] == 'DROPBOX SYSTEM APP CRASHES'][0]
        self.assertEqual((printed[0], printed[1], printed[2]), (utc(2026, 11, 1, 19, 0, 0), '2026-11-01 20:00:00', 'system_app_crash'))

    def test_reset_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16', zone='Asia/Kolkata'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_reset_reasons, path)
        self.assertEqual(headers[:3], (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note'))
        by_time = {(row[8], row[1]): row for row in rows}
        offset = by_time[('AP RESET INFO EXTEND', '2026-02-03 10:11:12+0700')]
        self.assertEqual((offset[0], offset[2]), (utc(2026, 2, 3, 3, 11, 12), ''))
        negative = by_time[('AP RESET INFO EXTEND', '2026-10-30 07:00:00-0330')]
        self.assertEqual(negative[0], utc(2026, 10, 30, 10, 30))
        unset = by_time[('AP RESET INFO EXTEND', '2010-01-01 00:00:12+0000')]
        self.assertEqual((unset[0], unset[2]), (utc(2010, 1, 1, 0, 0, 12), ''))
        record = by_time[('POWER OFF RESET REASON', '26/09/20 02:12:41')]
        self.assertEqual((record[0], record[2]), (utc(2026, 9, 19, 20, 42, 41), 'printed without an offset, converted with the report time zone'))
        path = self.stage('Dump2/dumpstate.txt', fixture.build_report('l16', zone=''))
        rows = self.run_artifact(artifacts.bugreport_reset_reasons, path)[1]
        record = [row for row in rows if row[1] == '26/09/20 02:12:41'][0]
        self.assertEqual((record[0], record[2]), (None, 'printed without an offset, converted with the report time zone; '
                                                        + reader.NOTE_NO_ZONE))
        self.assertEqual([row for row in rows if row[1] == '2026-02-03 10:11:12+0700'][0][0], utc(2026, 2, 3, 3, 11, 12))

    def test_vendor_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('l16', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_vendor_services, path)
        self.assertEqual(headers[:4], (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Service'))
        by_text = {row[4]: row for row in rows}
        iso = by_text['[2026-10-30 08:15:30.111] L/ab12/example.user.chat/0/10300/Bg/{Prm:Fn/Bg}/AcLmt:true']
        self.assertEqual((iso[0], iso[1], iso[2]), (utc(2026, 10, 30, 7, 15, 30, 111000), '2026-10-30 08:15:30.111', ''))
        slash = by_text['02/03/2026 03:05:06.789   > Created (pid: 3333, binary: EXAMPLEBUILD1)']
        self.assertEqual(slash[0], utc(2026, 2, 3, 2, 5, 6, 789000))
        masked = by_text['02/03/*026 02:54:29.863   > Created (pid: *489, binary: EXAMPLEBUILD1)']
        self.assertEqual((masked[0], masked[2]), (None, logscrash.NOTE_MASKED_YEAR))
        nfc = by_text['05-09 08:41:12.345 D [NFC_SE]SamsungExtension invented state line']
        self.assertEqual((nfc[0], nfc[2]), (utc(2026, 5, 9, 6, 41, 12, 345000),
                                            'printed without a year, the year is taken from the report time'))
        old = by_text['11-20 12:58:59.973 D [NFC_SE]SamsungExtension a line of the previous year']
        self.assertEqual(old[0], utc(2025, 11, 20, 11, 58, 59, 973000))
        plain = by_text['Wi-Fi api call history:']
        self.assertEqual((plain[0], plain[1], plain[2]), (None, '', ''))

    def test_cut_dumps_are_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_cut_report())
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append), mock.patch.object(reader, 'say_once', lambda log, m: log(m)):
            self.run_artifact(artifacts.bugreport_vendor_services, path)
            self.run_artifact(artifacts.bugreport_system_log, path)
        text = '\n'.join(messages)
        self.assertNotIn('knoxguard_service', text)     # that dump is read by the Security artifact
        self.assertIn('the sem_wifi service dump was cut by a 10000 ms timeout', text)

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('l16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('l10'))
        alone = len(self.run_artifact(artifacts.bugreport_system_log, first)[1])
        both = self.run_artifact(artifacts.bugreport_system_log, first, second)[1]
        self.assertGreater(len(both), alone)
        self.assertEqual({row[11] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})

    def test_odd_bytes_do_not_stop_the_pass(self):
        odd = fixture.cases()['synthetic_odd_bytes'][0][1]
        path = self.stage('Dump/dumpstate.txt', odd)
        for function in self.FUNCTIONS:
            self.run_artifact(function, path)
        rows = self.run_artifact(artifacts.bugreport_system_log, path)[1]
        self.assertEqual([row[0] for row in rows if row[7].startswith('invented')][0], None)       # no zone in this text
        text = {row[7] for row in rows}
        self.assertIn('invented � message  one', text)
        self.assertTrue([m for m in text if m.startswith('control')])
        self.assertTrue(all('\x00' not in row[7] and '\x01' not in row[7] for row in rows))

    def test_a_damaged_member_is_logged_and_the_others_are_still_read(self):
        data = bytearray(fixture.bug_report_zip('l16'))
        with zipfile.ZipFile(io.BytesIO(bytes(data))) as archive:
            info = archive.getinfo('FS/data/tombstones/tombstone_00')
            name_length, extra_length = struct.unpack('<HH', bytes(data[info.header_offset + 26:info.header_offset + 30]))
            start = info.header_offset + 30 + name_length + extra_length
        for offset in range(start + 2, start + 12):
            data[offset] ^= 0xFF
        path = self.stage('Dump/bugreport-example-2026-11-02.zip', bytes(data))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append), mock.patch.object(reader, 'say_once', lambda log, m: log(m)):
            rows = self.run_artifact(artifacts.bugreport_tombstones, path)[1]
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0][1], '')                    # the damaged member keeps a blank row
        self.assertEqual(rows[1][1], 'com.example.user.nfc')
        self.assertTrue([m for m in messages if 'tombstone_00 could not be read' in m])

    def test_a_zip_that_cannot_be_opened_is_logged(self):
        path = self.stage('Dump/bugreport-example-2026-11-02.zip', fixture.bug_report_zip('l16'))
        messages = []
        with mock.patch.object(artifacts.zipfile, 'ZipFile', side_effect=zipfile.BadZipFile('bad')),                 mock.patch.object(artifacts, 'logfunc', messages.append), mock.patch.object(reader, 'say_once', lambda log, m: log(m)),                 mock.patch.object(artifacts.dumpstate_reader, 'load_reports', return_value=[(
                    'Dump/bugreport-example-2026-11-02.zip!/main.txt', scan_text_with_source(path))]):
            rows = self.run_artifact(artifacts.bugreport_tombstones, path)[1]
        self.assertEqual(rows, [])
        self.assertTrue([m for m in messages if 'could not open the zip' in m])


def scan_text_with_source(path):
    report = scan_text(fixture.build_report('l16'))
    report.source = reader.Source(str(path), 'main.txt')
    return report


if __name__ == '__main__':
    unittest.main()
