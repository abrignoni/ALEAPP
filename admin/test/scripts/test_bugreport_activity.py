"""Android bug report text: usage events, process exit info, settings, settings changes and boot reasons."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts.artifacts import bugreportActivity as activity


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


class EpochTests(unittest.TestCase):
    def test_epoch_helpers(self):
        self.assertEqual(reader.epoch_ms_to_utc(1787562005120).isoformat(), '2026-08-24T09:00:05.120000+00:00')
        self.assertIsNone(reader.epoch_ms_to_utc(10 ** 30))
        self.assertIsNone(reader.epoch_ms_to_utc('x'))
        self.assertEqual(reader.epoch_s_to_utc(-1).isoformat(), '1969-12-31T23:59:59+00:00')
        self.assertIsNone(reader.epoch_s_to_utc(10 ** 30))
        self.assertTrue(reader.plausible_epoch_ms(1787562005120))
        self.assertFalse(reader.plausible_epoch_ms(0))
        self.assertFalse(reader.plausible_epoch_ms(892014384711))
        self.assertFalse(reader.plausible_epoch_ms(4102444800001))


class UsageTests(unittest.TestCase):
    def test_checkin_form_epoch_milliseconds(self):
        report = scan_text(fixture.build_report('a16', users=(0, 10)))
        events = report.usage_events
        self.assertEqual({e.section for e in events}, {'CHECKIN USAGESTATS'})
        self.assertEqual(sorted({e.user for e in events}), [0, 10])
        first = [e for e in events if e.user == 0][0]
        self.assertEqual(first.event_type, 'SCREEN_INTERACTIVE')
        self.assertEqual(report.usage_time(first.time_text), utc(2026, 11, 1, 21, 5, 10))   # printed as epoch milliseconds
        chat = [e for e in events if e.event_type == 'ACTIVITY_RESUMED' and e.user == 0][0]
        self.assertEqual(chat.class_name, 'com.example.user.chat.Main')
        self.assertIn('instanceId=11', chat.extras)
        self.assertEqual(chat.flags, '0x0')
        self.assertNotIn('flags=', chat.extras)
        self.assertEqual(len([e for e in events if e.user == 0]), len(fixture.USAGE_EVENTS) + 1)

    def test_implausible_epoch_gets_no_utc(self):
        report = scan_text(fixture.build_report('a16'))
        odd = [e for e in report.usage_events if e.time_text == '1000'][0]
        self.assertIsNone(report.usage_time(odd.time_text))

    def test_service_form_wall_clock_is_converted_with_the_report_zone(self):
        report = scan_text(fixture.build_report('a10', zone='Europe/Paris'))
        sections = {e.section for e in report.usage_events}
        self.assertEqual(sections, {'DUMP OF SERVICE usagestats', 'CHECKIN USAGESTATS'})   # Android 10 prints both forms
        plain = [e for e in report.usage_events if e.section == 'DUMP OF SERVICE usagestats'][0]
        self.assertEqual(plain.time_text, '2026-11-01 21:05:10')
        self.assertEqual(report.usage_time(plain.time_text), utc(2026, 11, 1, 20, 5, 10))

    def test_numbers_must_be_ascii_digits(self):
        report = scan_text(fixture.build_report('a16'))
        self.assertIsNone(report.usage_time('²'))
        self.assertIsNone(report.usage_time('١٢٣'))
        scan_text(fixture.build_report('a16').replace('user=0 ', 'user=² ', 1))        # must neither raise nor stop the pass
        scan_text(fixture.build_report('a16').replace("DUMP TIMEOUT (10000ms)", "DUMP TIMEOUT (²ms)"))

    def test_no_zone_and_unset_wall_times(self):
        report = scan_text(fixture.build_report('a10', zone=''))
        self.assertIsNone(report.usage_time('2026-11-01 21:05:10'))
        report = scan_text(fixture.build_report('a10', zone='UTC'))
        for text in ('1970-01-01 00:00:00', '1973-08-29 05:00:27', '1969-12-31 23:59:59', '2008-12-31 23:59:59', '', 'x'):
            self.assertIsNone(report.usage_time(text), text)
        self.assertEqual(report.usage_time('2009-01-01 00:00:00'), utc(2009, 1, 1))

    def test_lines_outside_the_event_list_are_not_events(self):
        report = scan_text(fixture.build_report('a10'))
        packages = {e.package for e in report.usage_events}
        self.assertNotIn('', packages)
        self.assertTrue(all(e.event_type for e in report.usage_events))
        # the pending events (times that start at 1970), the daily statistics and the standby states follow the events
        self.assertFalse([e for e in report.usage_events if e.time_text.startswith('1970')])
        self.assertIn('Pending events', fixture.build_report('a10'))
        self.assertEqual(len([e for e in report.usage_events if e.section == 'DUMP OF SERVICE usagestats' and e.user == 0]),
                         len(fixture.USAGE_EVENTS))


class ExitInfoTests(unittest.TestCase):
    def test_entries_and_fields(self):
        report = scan_text(fixture.build_report('a16', zone='Asia/Kolkata'))
        exits = report.process_exits
        self.assertEqual(len(exits), len(fixture.EXITS))
        first = exits[0]
        self.assertEqual((first.package, first.process, first.pid, first.real_uid, first.package_uid, first.user),
                         ('com.example.user.chat', 'com.example.user.chat', 4321, 10300, 10300, 0))
        self.assertEqual(first.reason, '2 (SIGNALED)')
        self.assertEqual(first.sub_reason, '0 (UNKNOWN)')
        self.assertEqual(first.status, '9')
        self.assertEqual(first.importance, 230)
        self.assertEqual(first.description, '')                 # printed as null
        self.assertEqual(report.exit_time(first.stamp), utc(2026, 11, 1, 17, 11, 3, 120000))
        self.assertEqual(exits[1].description, 'remove task')
        self.assertEqual(exits[1].process, 'com.example.user.chat:sync')
        self.assertEqual((exits[2].user, exits[2].package, exits[2].entry), (10, 'com.example.user.chat', 0))   # a second uid group
        self.assertEqual((exits[1].entry, exits[3].package, exits[3].entry), (1, 'com.example.user.sideloaded', 0))

    def test_other_activity_headings_end_the_list(self):
        text = fixture.build_report('a16').replace('ACTIVITY MANAGER OTHER (dumpsys activity other)',
                                                    'ACTIVITY MANAGER OTHER (dumpsys activity other)\n  ApplicationExitInfo #9:')
        self.assertEqual(len(scan_text(text).process_exits), len(fixture.EXITS))

    def test_android_10_has_no_exit_info(self):
        self.assertEqual(scan_text(fixture.build_report('a10')).process_exits, [])

    def test_unset_and_missing_times(self):
        report = scan_text(fixture.build_report('a16', zone=''))
        self.assertIsNone(report.exit_time(report.process_exits[0].stamp))
        self.assertIsNone(report.exit_time('1970-01-01 00:00:00.000'))
        self.assertIsNone(report.exit_time('not a time'))


class SettingsTests(unittest.TestCase):
    def test_history_layout_tables_users_and_trailers(self):
        report = scan_text(fixture.build_report('a16', users=(0, 10)))
        by_key = {(s.user, s.namespace, s.name): s for s in report.settings}
        adb = by_key[(0, 'global', 'adb_enabled')]
        self.assertEqual((adb.value, adb.default, adb.default_system_set, adb.preserved, adb.writer, adb.setting_id),
                         ('0', '0', 'true', 'true', 'android', 11))
        self.assertEqual(by_key[(10, 'global', 'adb_enabled')].user, 10)
        self.assertEqual(by_key[(0, 'global', 'device_name')].value, 'Example Phone')
        empty = by_key[(0, 'global', 'empty_value')]
        self.assertEqual((empty.value, empty.default, empty.value_length), ('', '', 0))
        null = by_key[(0, 'global', 'no_value')]
        self.assertEqual((null.value, null.default, null.value_length), ('{null}', '{null}', 0))
        self.assertEqual(by_key[(0, 'system', 'screen_off_timeout')].value, '30000')
        self.assertEqual({s.namespace for s in report.settings}, {'global', 'secure', 'system'})
        self.assertEqual(report.config_settings, {0: (1, 1), 10: (1, 1)})            # counted, not listed
        self.assertFalse([s for s in report.settings if s.name.startswith('example/')])

    def test_a_value_that_continues_on_the_next_line(self):
        report = scan_text(fixture.build_report('a16'))
        long_value = [s for s in report.settings if s.name == 'long_value'][0]
        self.assertEqual(long_value.value, 'QUJD' * 20 + ' ' + 'REVG' * 10)       # the line break is shown as a space
        self.assertEqual(long_value.value_length, 121)
        self.assertEqual(long_value.continuations, 1)

    def test_trailer_words_inside_a_multi_line_value_stay_in_the_value(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE settings:\n'
                'SECURE SETTINGS (user 0)\n_id:1 name:blob pkg:android value:first line\n'
                '  middle default: text and defaultSystemSet: words\n'
                '  last chunk default:the default defaultSystemSet:true\n_id:2 name:next pkg:android value:1\n')
        by_name = {s.name: s for s in scan_text(text).settings}
        blob = by_name['blob']
        self.assertEqual(blob.value, 'first line middle default: text and defaultSystemSet: words last chunk')
        self.assertEqual((blob.default, blob.default_system_set, blob.continuations), ('the default', 'true', 2))
        self.assertEqual(by_name['next'].value, '1')

    def test_plain_layout_and_old_trailing_token(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE settings:\n'
                'GLOBAL SETTINGS (user 0)\n'
                '_id:1 name:a pkg:android value:1 notPreservedInRestore\n'
                '_id:2 name:b pkg:com.example value:x y default:z defaultSystemSet:false\n'
                '_id:3 name:c pkg:android value:text with default: inside default:real defaultSystemSet:true\n'
                '_id:4 name:d value:5\n')
        by_name = {s.name: s for s in scan_text(text).settings}
        self.assertEqual((by_name['a'].value, by_name['a'].preserved, by_name['a'].default), ('1', 'false', ''))
        self.assertEqual((by_name['b'].value, by_name['b'].default, by_name['b'].default_system_set), ('x y', 'z', 'false'))
        self.assertEqual(by_name['c'].value, 'text with')                                  # the first trailer token ends the value
        self.assertEqual(by_name['d'].writer, '')
        self.assertEqual(by_name['d'].value, '5')

    def test_value_is_bounded_and_the_full_length_kept(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE settings:\n'
                'SECURE SETTINGS (user 0)\n_id:1 name:big pkg:android value:' + 'v' * 5000 + ' default:\n')
        setting = scan_text(text).settings[0]
        self.assertEqual(len(setting.value), reader.SETTING_VALUE_CHARS)
        self.assertEqual(setting.value_length, 5000)

    def test_unreadable_entry_is_warned_about(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE settings:\n'
                'GLOBAL SETTINGS (user 0)\n_id:1 no name here\n_id:2 name:ok pkg:android value:1\n')
        report = scan_text(text)
        self.assertEqual([s.name for s in report.settings], ['ok'])
        self.assertTrue(report.warnings)

    def test_changes_and_the_year(self):
        report = scan_text(fixture.build_report('a16', zone='Europe/Paris', report='2026-11-02 10:15:30'))
        changes = [c for c in report.setting_changes if c.user == 0 and c.name == 'adb_enabled']
        self.assertEqual([(c.mode, c.old_value, c.new_value, c.package) for c in changes],
                         [('update', '1', '0', 'com.example.settings'), ('update', '0', '1', 'com.example.settings')])
        full, moment = report.setting_change_time(changes[0].time_text)
        self.assertEqual(full, '2026-10-02 08:00:00.000')
        self.assertEqual(moment, utc(2026, 10, 2, 6, 0))
        self.assertEqual(len([c for c in report.setting_changes if c.name.startswith('example/')]), 0)     # config table
        self.assertEqual(report.setting_change_time('12-31 23:00:00.000')[0], '2025-12-31 23:00:00.000')   # after the report: last year
        self.assertEqual(report.setting_change_time('11-03 10:00:00.000')[0], '2026-11-03 10:00:00.000')   # within a day after it
        self.assertEqual(report.setting_change_time('02-29 12:00:00.000'), ('', None))                       # no 29 February
        self.assertEqual(report.setting_change_time('garbage'), ('', None))

    def test_changes_without_a_report_time_have_no_year(self):
        report = scan_text(fixture.build_report('a16', with_banner=False))
        self.assertTrue(report.setting_changes)
        self.assertEqual(report.setting_change_time(report.setting_changes[0].time_text), ('', None))

    def test_change_with_a_caller_and_values_with_spaces(self):
        text = ('== dumpstate: 2026-06-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE settings:\n'
                'GLOBAL SETTINGS (user 0)\n_id:1 name:k pkg:p value:n isValuePreservedInRestore:true\n  History (k)\n'
                '    time:05-30 01:02:03.004 mode:update oldValue:a b newValue:c d package:com.x caller:Some.method(a/1:2)\n')
        change = scan_text(text).setting_changes[0]
        self.assertEqual((change.old_value, change.new_value, change.package, change.caller),
                         ('a b', 'c d', 'com.x', 'Some.method(a/1:2)'))


class BootTests(unittest.TestCase):
    def test_history_entries(self):
        report = scan_text(fixture.build_report('a16'))
        history = report.boot_entries
        self.assertEqual([(e.position, e.reason, e.sub_reason) for e in history],
                         [(0, 'reboot', 'userrequested'), (1, 'cold', 'powerkey'), (2, 'reboot', 'ota')])
        self.assertEqual(history[0].epoch_text, str(fixture.epoch_s('2026-10-30 07:00:00')))
        self.assertEqual(reader.epoch_s_to_utc(int(history[0].epoch_text)), utc(2026, 10, 30, 7, 0))
        self.assertTrue(history[1].line > history[0].line)                    # each entry carries its own line

    def test_the_boot_reason_properties_are_device_facts(self):
        report = scan_text(fixture.build_report('a16'))
        facts = {fact.name: fact.value for fact in report.facts if fact.origin == 'getprop'}
        self.assertEqual({name: facts[name] for name in ('persist.sys.boot.reason', 'ro.boot.bootreason', 'sys.boot.reason',
                                                         'sys.boot.reason.last', 'sys.reset_reason')},
                         {'persist.sys.boot.reason': '', 'ro.boot.bootreason': 'reboot', 'sys.boot.reason': 'reboot,userrequested',
                          'sys.boot.reason.last': 'reboot,userrequested', 'sys.reset_reason': ''})

    def test_history_in_one_line_and_odd_entries(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ SYSTEM PROPERTIES (getprop) ------\n'
                '[persist.sys.boot.reason.history]: [reboot,shell,1790000000]\n')
        entries = scan_text(text).boot_entries
        self.assertEqual([(e.reason, e.sub_reason, e.epoch_text) for e in entries], [('reboot', 'shell', '1790000000')])
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ SYSTEM PROPERTIES (getprop) ------\n'
                '[persist.sys.boot.reason.history]: [no stamp here\nreboot,x,5\n\nkernel_panic,a,b,1790000000]\n')
        entries = scan_text(text).boot_entries
        self.assertEqual([(e.reason, e.sub_reason, e.epoch_text) for e in entries],
                         [('no stamp here', '', ''), ('reboot', 'x', '5'), ('kernel_panic', 'a,b', '1790000000')])
        self.assertEqual([e.position for e in entries], [0, 1, 2])           # blank lines are skipped, not counted

    def test_history_is_capped(self):
        body = '\n'.join('reboot,x,%d' % (1790000000 + n) for n in range(reader.MAX_BOOT_HISTORY + 50))
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ SYSTEM PROPERTIES (getprop) ------\n'
                '[persist.sys.boot.reason.history]: [' + body + ']\n')
        self.assertEqual(len(scan_text(text).boot_entries), reader.MAX_BOOT_HISTORY)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def stage(self, name, text):
        path = Path(self.work) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode('utf-8') if isinstance(text, str) else text)
        return path

    def run_artifact(self, function, *paths):
        return function.__wrapped__(Context(self.work, paths))

    FUNCTIONS = (activity.bugreport_usage_events, activity.bugreport_process_exits, activity.bugreport_settings,
                 activity.bugreport_settings_changes, activity.bugreport_boot_reasons)

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', users=(0, 10)))
        for function in self.FUNCTIONS:
            headers, rows, source_path = self.run_artifact(function, path)
            self.assertTrue(rows, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows))
            self.assertEqual(source_path, str(path))

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)

    def test_a_text_without_these_sections_gives_no_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.BANNER.format(report='2026-11-02 10:15:30'))
        for function in self.FUNCTIONS:
            self.assertEqual(self.run_artifact(function, path)[1], [])

    def test_usage_events_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        _headers, rows, _source = self.run_artifact(activity.bugreport_usage_events, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 21, 5, 10))          # epoch milliseconds: the zone does not matter
        self.assertEqual(rows[0][1], str(fixture.epoch_ms('2026-11-01 21:05:10')))
        self.assertEqual(rows[0][8], 'CHECKIN USAGESTATS')
        self.assertIsNone([row for row in rows if row[1] == '1000'][0][0])

    def test_process_exit_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Asia/Kolkata'))
        _headers, rows, _source = self.run_artifact(activity.bugreport_process_exits, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 17, 11, 3, 120000))
        self.assertEqual(rows[0][1], '2026-11-01 22:41:03.120')
        self.assertEqual(rows[3][8], '4 (APP CRASH(NATIVE))')

    def test_settings_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', users=(0, 10)))
        _headers, rows, _source = self.run_artifact(activity.bugreport_settings, path)
        self.assertEqual({row[0] for row in rows}, {0, 10})
        names = {(row[0], row[2]) for row in rows}
        self.assertIn((10, 'enabled_notification_listeners'), names)

    def test_settings_changes_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        _headers, rows, _source = self.run_artifact(activity.bugreport_settings_changes, path)
        first = [row for row in rows if row[4] == 'adb_enabled'][0]
        self.assertEqual(first[0], utc(2026, 10, 2, 6, 0))
        self.assertEqual(first[1], '10-02 08:00:00.000')

    def test_boot_reason_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        _headers, rows, _source = self.run_artifact(activity.bugreport_boot_reasons, path)
        self.assertEqual(rows[0][0], utc(2026, 10, 30, 7, 0))
        self.assertEqual([row[5] for row in rows], [0, 1, 2])
        self.assertEqual([row[3] for row in rows], ['reboot', 'cold', 'reboot'])

    def test_a_dump_cut_by_the_platform_is_logged_once(self):
        text = ('== dumpstate: 2026-06-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE settings:\n'
                'GLOBAL SETTINGS (user 0)\n_id:1 name:a pkg:p value:1\n  History (a)\n'
                '    time:05-30 00:00:00.000 mode:insert oldValue:null newValue:1 package:p\n'
                "*** SERVICE 'settings' DUMP TIMEOUT (10000ms) EXPIRED ***\n")
        path = self.stage('Dump/dumpstate.txt', text)
        messages = []
        with mock.patch.object(activity, 'logfunc', messages.append):
            self.run_artifact(activity.bugreport_settings, path)
            self.run_artifact(activity.bugreport_settings_changes, path)
        cut = [message for message in messages if 'settings service dump was cut by a 10000 ms timeout' in message]
        self.assertEqual(len(cut), 1)

    def test_only_the_cut_dump_that_holds_the_rows_is_reported(self):
        cut_first = ('== dumpstate: 2026-06-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE activity:\n'
                     "*** SERVICE 'activity' DUMP TIMEOUT (500ms) EXPIRED ***\n"
                     '--------- 0.5s was the duration of dumpsys activity, ending at: 2026-06-01 10:00:01\n'
                     'DUMP OF SERVICE activity:\nACTIVITY MANAGER PROCESS EXIT INFO (dumpsys activity exit-info)\n'
                     '  package: com.example.a\n        ApplicationExitInfo #0:\n'
                     '          timestamp=2026-05-30 01:02:03.004 pid=1 realUid=2 packageUid=2 definingUid=2 user=0\n'
                     '          process=com.example.a reason=2 (SIGNALED) subreason=0 (UNKNOWN) status=9\n'
                     '          importance=100 pss=0.00 rss=0.00 description=null state=empty trace=null\n')
        path = self.stage('Dump/dumpstate.txt', cut_first)
        messages = []
        with mock.patch.object(activity, 'logfunc', messages.append):
            rows = self.run_artifact(activity.bugreport_process_exits, path)[1]
        self.assertEqual(len(rows), 1)
        self.assertFalse([message for message in messages if 'was cut' in message])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10'))
        alone = len(self.run_artifact(activity.bugreport_usage_events, first)[1])
        both = self.run_artifact(activity.bugreport_usage_events, first, second)[1]
        self.assertGreater(len(both), alone)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})


if __name__ == '__main__':
    unittest.main()
