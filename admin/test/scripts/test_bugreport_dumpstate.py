"""Android bug report text: the reader (sections, times, factory stamps, sources) and the device artifacts."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts.artifacts import bugreportDevice as device


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


def scan_text(text):
    """A Report from a text, without a file."""
    report = reader.Report(reader.Source('memory', ''))
    data = text.encode('utf-8') if isinstance(text, str) else text
    reader.scan_lines(reader.iter_lines(io.BytesIO(data)), report)
    report.finish()
    return report


class TimeTests(unittest.TestCase):
    def test_wall_time_forms(self):
        self.assertEqual(reader.parse_wall_time('2026-10-25 06:43:00'), datetime(2026, 10, 25, 6, 43))
        self.assertEqual(reader.parse_wall_time('2026-10-25T06:43:00.123456789').microsecond, 123456)
        for bad in ('', 'not a time', '2026-13-25 06:43:00', '2026-10-25', '2026/10/25 06:43:00', None):
            self.assertIsNone(reader.parse_wall_time(bad))

    def test_zone_conversion(self):
        paris = reader.ZoneClock('Europe/Paris')
        self.assertEqual(paris.to_utc('2026-07-01 12:00:00'), datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc))
        self.assertEqual(paris.to_utc('2026-01-01 12:00:00'), datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc))
        kolkata = reader.ZoneClock('Asia/Kolkata')
        self.assertEqual(kolkata.to_utc('2026-01-01 12:00:00'), datetime(2026, 1, 1, 6, 30, tzinfo=timezone.utc))

    def test_daylight_saving_edges(self):
        paris = reader.ZoneClock('Europe/Paris')
        # clocks go back on 2026-10-25 03:00 to 02:00: 02:30 happens twice and is read with the summer offset
        self.assertEqual(paris.to_utc('2026-10-25 02:30:00'), datetime(2026, 10, 25, 0, 30, tzinfo=timezone.utc))
        # clocks go forward on 2026-03-29 02:00 to 03:00: 02:30 does not happen
        self.assertIsNone(paris.to_utc('2026-03-29 02:30:00'))

    def test_times_at_the_edge_of_the_calendar_have_no_value_instead_of_an_error(self):
        for zone in ('Asia/Kolkata', 'America/Sao_Paulo', 'UTC', 'Pacific/Kiritimati', 'Pacific/Pago_Pago'):
            clock = reader.ZoneClock(zone)
            for text in ('0001-01-01 00:00:00', '0001-01-01 05:00:00', '9999-12-31 23:59:59', '9999-12-31 12:00:00'):
                result = clock.to_utc(text)
                self.assertTrue(result is None or result.tzinfo is not None, (zone, text))
        self.assertIsNone(reader.ZoneClock('Asia/Kolkata').to_utc('0001-01-01 00:00:00'))
        self.assertIsNone(reader.ZoneClock('America/Sao_Paulo').to_utc('9999-12-31 23:59:59'))

    def test_only_ascii_digits_are_numbers(self):
        for text in ('0', '12', '1790000000'):
            self.assertTrue(reader.is_digits(text))
        for text in ('', 'x', '1x', '²', '١٢', '-1', '1.5'):
            self.assertFalse(reader.is_digits(text), text)

    def test_unknown_zone(self):
        for name in ('', 'Not/AZone', None):
            clock = reader.ZoneClock(name)
            self.assertFalse(clock.known)
            self.assertIsNone(clock.to_utc('2026-01-01 12:00:00'))


class FactoryStampTests(unittest.TestCase):
    def test_placeholder_window(self):
        for text in ('2009-01-01 00:00:00', '2008-12-31 15:00:00', '2008-12-31 10:00:00', '2009-01-01 14:00:00',
                     '2009-01-01 05:30:00', '2009-01-01 05:45:00', '2022-01-01 00:00:00'):
            self.assertTrue(reader.is_placeholder_time(text), text)
        for text in ('2009-01-01 00:00:01', '2009-01-01 00:15:00', '2008-12-31 09:59:00', '2009-01-01 14:30:00',
                     '2022-01-01 00:00:01', '2010-01-01 00:00:00', '', 'x'):
            self.assertFalse(reader.is_placeholder_time(text), text)

    def test_image_resident(self):
        self.assertTrue(reader.sits_on_image('/system/app/X'))
        self.assertTrue(reader.sits_on_image('/data/app/x', hidden_system=True))
        self.assertFalse(reader.sits_on_image('/data/app/~~a/x-b/'))
        self.assertFalse(reader.sits_on_image('/mnt/expand/x'))
        self.assertFalse(reader.sits_on_image(''))

    def entries(self, count, text, on_image=True, prefix='p'):
        return [('%s%d' % (prefix, number), text, on_image) for number in range(count)]

    def test_shared_time_needs_twenty_packages_on_the_image(self):
        self.assertEqual(reader.find_shared_stamps(self.entries(19, '2015-05-05 05:05:05')), set())
        self.assertEqual(reader.find_shared_stamps(self.entries(20, '2015-05-05 05:05:05')), {'2015-05-05 05:05:05'})
        # the same package printing the time many times is one package
        repeated = [('p', '2015-05-05 05:05:05', True)] * 50
        self.assertEqual(reader.find_shared_stamps(repeated), set())

    def test_user_installed_packages_are_never_marked(self):
        self.assertEqual(reader.find_shared_stamps(self.entries(40, '2026-10-01 07:00:00', on_image=False)), set())

    def test_burst_of_image_packages(self):
        times = ['2010-01-01 00:01:23', '2010-01-01 00:01:24', '2010-01-01 00:01:25', '2010-01-01 00:01:27']
        entries = [('p%d' % n, times[n % 4], True) for n in range(24)]       # 6 packages per second: none reaches 20
        self.assertEqual(reader.find_shared_stamps(entries), set(times))
        spread = [('p%d' % n, '2010-01-01 00:%02d:00' % n, True) for n in range(24)]    # a minute apart: not a burst
        self.assertEqual(reader.find_shared_stamps(spread), set())
        slow = [('p%d' % n, '2011-01-01 00:00:%02d' % (n * 2), True) for n in range(24)]
        self.assertEqual(reader.find_shared_stamps(slow), set())              # two seconds apart for 46 seconds: span over 30

    def test_years_before_1980_are_not_counted(self):
        self.assertEqual(reader.find_shared_stamps(self.entries(30, '1970-01-01 00:00:00')), set())


class ScannerTests(unittest.TestCase):
    def test_service_ends_at_its_trailer_and_line_numbers_count_newlines_only(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n'
                'Build: X\r\n'
                'Kernel: line with a lone\rcarriage return and a form\x0cfeed\n'
                'Uptime: up 1 minutes\n'
                '------ SYSTEM PROPERTIES (getprop) ------\n'
                '[persist.sys.timezone]: [Europe/Paris]\n'
                '[ro.build.version.sdk]: [36]\n'
                "------ 0.1s was the duration of 'SYSTEM PROPERTIES' ------\n"
                '[persist.sys.locale]: [fr-FR]\n')
        report = scan_text(text)
        by_name = {fact.name: fact for fact in report.facts}
        self.assertEqual(by_name['Report time (as printed)'].line, 1)
        self.assertEqual(by_name['Build'].line, 2)
        self.assertEqual(by_name['Kernel'].line, 3)
        self.assertIn(' carriage', by_name['Kernel'].value)          # the lone CR and the form feed are shown as spaces
        self.assertEqual(by_name['Uptime'].line, 4)
        self.assertEqual(by_name['persist.sys.timezone'].line, 6)
        self.assertNotIn('persist.sys.locale', by_name)             # after the trailer: not part of the section
        self.assertEqual(report.zone_name, 'Europe/Paris')
        self.assertEqual(report.total_lines, 9)

    def test_section_without_trailer_ends_at_the_next_header(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n'
                '------ SYSTEM PROPERTIES (getprop) ------\n'
                '[persist.sys.timezone]: [Europe/Paris]\n'
                '------ OTHER (cmd) ------\n'
                '[persist.sys.locale]: [fr-FR]\n')
        report = scan_text(text)
        names = [fact.name for fact in report.facts]
        self.assertIn('persist.sys.timezone', names)
        self.assertNotIn('persist.sys.locale', names)

    def test_text_cut_in_the_middle_of_a_package_still_gives_the_complete_packages(self):
        text = fixture.build_report('a16', cut=True)
        report = scan_text(text[:len(text) // 2])
        self.assertTrue(report.packages)
        self.assertTrue(all(p.package for p in report.packages))
        cut = [s for s in scan_text(text).sections if s.timeout_ms]
        self.assertEqual([(s.name, s.timeout_ms) for s in cut], [('package', 10000)])
        report = scan_text(text[:-37])                                   # cut inside the last line, no newline at the end
        self.assertTrue(report.packages)

    def test_byte_order_mark_and_invalid_bytes(self):
        text = b'\xef\xbb\xbf== dumpstate: 2026-01-01 10:00:00\nBuild: bad\xff\xfebytes\x00here\n'
        report = scan_text(text)
        self.assertEqual(report.report_wall, '2026-01-01 10:00:00')
        build = [fact for fact in report.facts if fact.name == 'Build'][0]
        self.assertIn('bad', build.value)
        self.assertNotIn('\x00', build.value)

    def test_empty_and_header_only_inputs(self):
        for text in (b'', b'\n', b'== dumpstate: 2026-01-01 10:00:00', b'------ ', b'DUMP OF SERVICE package:'):
            report = scan_text(text)
            self.assertEqual(report.packages, [])
            self.assertEqual(report.package_times, [])

    def test_very_long_line_is_cut(self):
        text = b'== dumpstate: 2026-01-01 10:00:00\nBuild: ' + b'A' * 5000000 + b'\nUptime: up 1 minutes\n'
        report = scan_text(text)
        build = [fact for fact in report.facts if fact.name == 'Build'][0]
        self.assertLessEqual(len(build.value), 400)
        self.assertIn('Uptime', [fact.name for fact in report.facts])

    def test_lines_split_on_newline_only_and_a_long_line_is_one_line(self):
        long_line = b'X' * (3 * reader.MAX_LINE_BYTES + 5)
        lines = list(reader.iter_lines(io.BytesIO(b'a\rb\x0cc\n' + long_line + b'\nlast')))
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], b'a\rb\x0cc\n')
        self.assertEqual(len(lines[1]), reader.MAX_LINE_BYTES + 1)
        self.assertTrue(lines[1].endswith(b'\n'))
        self.assertEqual(lines[2], b'last')
        self.assertEqual(list(reader.iter_lines(io.BytesIO(b''))), [])

    def test_row_cap(self):
        text = fixture.build_report('a16')
        with mock.patch.object(reader, 'MAX_ROWS', 5):
            report = scan_text(text)
        self.assertEqual(len(report.packages), 5)
        self.assertEqual(len(report.package_times), 5)
        self.assertTrue(any('rows' in warning for warning in report.warnings))

    def test_identifiers_are_reported_as_printed(self):
        report = scan_text(fixture.build_report('a16'))
        facts = {(fact.name, fact.origin): fact for fact in report.facts}
        self.assertEqual(facts[('ro.serialno', 'getprop')].value, 'SYNTH0000EXAMPLE')
        self.assertEqual(facts[('ro.boot.serialno', 'getprop')].value, 'SYNTH0000EXAMPLE')
        self.assertEqual(facts[('Command line', 'header')].value,
                         'console=ttynull androidboot.serialno=SYNTH0000EXAMPLE androidboot.hardware=example')
        self.assertEqual(facts[('androidboot.hardware', 'bootconfig')].value, '"example"')
        self.assertEqual(facts[('androidboot.serialno', 'bootconfig')].value, '"SYNTH0000EXAMPLE"')
        self.assertEqual(facts[('androidboot.serialno', 'bootconfig')].line, facts[('androidboot.hardware', 'bootconfig')].line + 1)
        # a property that is not on either list stays out, whatever its name says
        self.assertNotIn('gsm.sim.imei.example', {fact.name for fact in report.facts})
        old = scan_text(fixture.build_report('a10'))
        self.assertEqual([fact.value for fact in old.facts if fact.name == 'Command line'],
                         ['loglevel=1 androidboot.serialno=SYNTH0001EXAMPLE'])
        self.assertFalse([fact for fact in old.facts if fact.origin == 'bootconfig'])

    def test_identifier_properties_one_row_each(self):
        lines = ['[%s]: [INVENTED-%d]' % (name, number) for number, name in enumerate(reader.IDENTIFIER_PROPERTIES)]
        lines += ['[%s]: [again]' % reader.IDENTIFIER_PROPERTIES[0], '[ro.not.listed.serialno]: [INVENTED-X]',
                  '[persist.log.tag.Phone]: [D]']
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ SYSTEM PROPERTIES (getprop) ------\n' + '\n'.join(lines) + '\n')
        report = scan_text(text)
        found = {fact.name: fact.value for fact in report.facts}
        self.assertEqual(len(report.facts) - 1, len(reader.IDENTIFIER_PROPERTIES))     # the report time row is the other
        for number, name in enumerate(reader.IDENTIFIER_PROPERTIES):
            self.assertEqual(found[name], 'INVENTED-%d' % number)
        self.assertNotIn('ro.not.listed.serialno', found)

    def test_command_line_and_bootconfig_edges(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\nBuild: X\nCommand line: ' + 'a=1 ' * 2000 + '\n'
                'Bootconfig: androidboot.a = "1"\nandroidboot.b = "x", "y"\nnot a bootconfig line\n'
                'androidboot.after = "2"\nUptime: up 1 minutes\n')
        report = scan_text(text)
        by_name = {(fact.name, fact.origin): fact.value for fact in report.facts}
        self.assertEqual(len(by_name[('Command line', 'header')]), reader.COMMAND_LINE_CHARS)
        self.assertEqual(by_name[('androidboot.a', 'bootconfig')], '"1"')
        self.assertEqual(by_name[('androidboot.b', 'bootconfig')], '"x", "y"')
        self.assertNotIn(('androidboot.after', 'bootconfig'), by_name)      # the bootconfig lines ended at the first other line
        self.assertIn(('Uptime', 'header'), by_name)
        with mock.patch.object(reader, 'MAX_BOOTCONFIG_LINES', 1):
            capped = scan_text(text)
        self.assertEqual([fact.name for fact in capped.facts if fact.origin == 'bootconfig'], ['androidboot.a'])
        self.assertIn(('Uptime', 'header'), {(fact.name, fact.origin) for fact in capped.facts})

    def test_property_value_over_several_lines(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ SYSTEM PROPERTIES (getprop) ------\n'
                '[ro.build.fingerprint]: [first part\nsecond part]\n[persist.sys.timezone]: [UTC]\n')
        report = scan_text(text)
        by_name = {fact.name: fact.value for fact in report.facts}
        self.assertEqual(by_name['ro.build.fingerprint'], 'first part second part')
        self.assertEqual(by_name['persist.sys.timezone'], 'UTC')


class SectionIndexTests(unittest.TestCase):
    def test_sections_durations_and_groups(self):
        report = scan_text(fixture.build_report('a16'))
        by_name = {(s.kind, s.name): s for s in report.sections}
        self.assertEqual(report.sections[0].name, 'preamble')
        self.assertEqual(by_name[('preamble', 'preamble')].line, 1)
        properties = by_name[('command', 'SYSTEM PROPERTIES')]
        self.assertEqual(properties.duration, 0.05)
        package = by_name[('service', 'package')]
        self.assertEqual(package.duration, 0.321)
        self.assertGreater(package.end_line, package.line + 100)
        group = by_name[('command', 'DUMPSYS CRITICAL')]
        self.assertTrue(group.group)
        self.assertFalse(properties.group)
        self.assertLessEqual(group.line, package.line)
        self.assertGreaterEqual(group.end_line, package.end_line)
        self.assertTrue(all(s.end_line > s.line for s in report.sections))

    def test_section_cut_by_the_end_of_the_text_has_no_duration(self):
        report = scan_text(fixture.build_report('a16', cut=True))
        package = [s for s in report.sections if s.name == 'package'][0]
        self.assertIsNone(package.duration)
        self.assertEqual(package.end_line, report.total_lines + 1)

    def test_service_priority_words_are_dropped(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\n'
                'DUMP OF SERVICE CRITICAL SurfaceFlinger:\nx\nDUMP OF SERVICE HIGH meminfo:\ny\n')
        names = [s.name for s in scan_text(text).sections]
        self.assertEqual(names, ['preamble', 'DUMPSYS', 'SurfaceFlinger', 'meminfo'])

    def test_markers_and_stray_duration_lines_are_not_sections(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ A (cmd) ------\n== Checkins\n'
                "------ 1.0s was the duration of 'OTHER' ------\n------ B (cmd) ------\n")
        report = scan_text(text)
        self.assertEqual([s.name for s in report.sections], ['preamble', 'A', 'B'])


    def test_a_marker_line_inside_the_header_keeps_the_header(self):
        # Samsung's automatically generated dumps print a '== automatically generated by' line under the banner
        plain = scan_text(fixture.build_report('a16'))
        text = fixture.build_report('a16').replace(
            '========================================================\n\n',
            '========================================================\n== automatically generated by example_app\n\n', 1)
        self.assertIn('== automatically generated by', text)
        marked = scan_text(text)
        self.assertEqual([f[:2] for f in marked.facts], [f[:2] for f in plain.facts])
        self.assertIn('Kernel', [f[0] for f in marked.facts])


class PackageTests(unittest.TestCase):
    def test_a16_blocks_users_and_times(self):
        report = scan_text(fixture.build_report('a16', users=(0, 10)))
        by_name = {(p.block, p.package): p for p in report.packages}
        chat = by_name[('Packages', 'com.example.user.chat')]
        self.assertEqual(chat.app_id, 10300)
        self.assertEqual(chat.app_id_key, 'appId')
        self.assertEqual(chat.installer, 'com.example.store')
        self.assertEqual(chat.users_installed, '0')                       # not installed for user 10
        self.assertIn('10: installed=false', chat.user_states)
        shared = by_name[('Packages', 'com.example.system.shared')]
        self.assertEqual(shared.shared_user, 'example.uid.shared/1001')
        sideloaded = by_name[('Packages', 'com.example.user.sideloaded')]
        self.assertEqual(sideloaded.installer, '')
        self.assertIn(('Hidden system packages', 'com.example.updated.one'), by_name)
        self.assertIn(('Packages', 'com.example.updated.one'), by_name)   # the same name appears in both blocks
        events = [(t.event, t.user) for t in report.package_times if t.package == 'com.example.user.chat']
        self.assertEqual(sorted(events, key=str), sorted([('timeStamp', None), ('lastUpdateTime', None),
                                                          ('firstInstallTime', 0), ('firstInstallTime', 10)], key=str))

    def test_a10_package_level_first_install_and_missing_installer(self):
        report = scan_text(fixture.build_report('a10'))
        by_name = {(p.block, p.package): p for p in report.packages}
        self.assertEqual(by_name[('Packages', 'com.example.user.chat')].app_id_key, 'userId')
        self.assertEqual(by_name[('Packages', 'com.example.user.sideloaded')].installer, '')
        first = [t for t in report.package_times if t.package == 'com.example.user.chat' and t.event == 'firstInstallTime']
        self.assertEqual([t.user for t in first], [None])

    def test_a_damaged_line_at_column_zero_does_not_end_the_list(self):
        text = fixture.build_report('a16')
        whole = len(scan_text(text).packages)
        damaged = text.replace('\n    pkg=Package{def456 com.example.system.app05}', '\n\rpkg=Package{def456 com.example.system.app05}', 1)
        self.assertNotEqual(damaged, text)
        report = scan_text(damaged)
        self.assertEqual(len(report.packages), whole)
        self.assertEqual(len(report.package_times), len(scan_text(text).package_times))

    def test_time_notes(self):
        report = scan_text(fixture.build_report('a16', zone='Europe/Paris'))
        moment, note = report.time_value('2026-07-04 23:30:00')
        self.assertEqual(moment, datetime(2026, 7, 4, 21, 30, tzinfo=timezone.utc))
        self.assertEqual(note, '')
        for text in ('1970-01-01 00:00:00', '1969-12-31 23:59:59'):
            moment, note = report.time_value(text)
            self.assertIsNone(moment)
            self.assertEqual(note, reader.NOTE_UNSET)
        moment, note = report.time_value('2010-01-01 00:01:23')
        self.assertIsNotNone(moment)                                      # the value is kept, with the note
        self.assertEqual(note, reader.NOTE_FACTORY_STAMP)
        self.assertEqual(report.time_value('garbage')[1], reader.NOTE_NOT_A_TIME)
        # user-installed packages that were updated within seconds of each other are not stamps
        self.assertEqual(report.time_value('2026-10-01 07:00:00')[1], '')

    def test_the_epoch_printed_in_the_report_zone_is_unset(self):
        seoul = scan_text(fixture.build_report('a16', zone='Asia/Seoul'))
        for text in ('1970-01-01 09:00:00', '1970-01-01 08:59:59', '1970-01-01 00:00:00'):
            moment, note = seoul.time_value(text)
            self.assertIsNone(moment, text)
            self.assertEqual(note, reader.NOTE_UNSET, text)
        self.assertEqual(seoul.time_value('1970-01-01 09:00:01')[1], '')
        unknown = scan_text(fixture.build_report('a16', zone=''))
        self.assertIn(reader.NOTE_UNSET, unknown.time_value('1969-12-31 23:59:59')[1])
        self.assertNotIn(reader.NOTE_UNSET, unknown.time_value('1970-01-01 09:00:00')[1])

    def test_a_time_at_the_edge_of_the_calendar_gets_a_note_not_an_error(self):
        report = scan_text(fixture.build_report('a16', zone='Asia/Kolkata'))
        moment, note = report.time_value('0001-01-01 00:00:00')
        self.assertIsNone(moment)
        self.assertEqual(note, reader.NOTE_NONEXISTENT)
        text = fixture.build_report('a16', zone='America/Sao_Paulo').replace(
            'lastUpdateTime=2026-09-14 08:30:11', 'lastUpdateTime=9999-12-31 23:59:59', 1)
        report = scan_text(text)
        edge = [t for t in report.package_times if t.wall == '9999-12-31 23:59:59']
        self.assertTrue(edge)
        self.assertIsNone(report.time_value(edge[0].wall)[0])
        self.assertEqual(report.time_value(edge[0].wall)[1], reader.NOTE_NONEXISTENT)

    def test_no_zone_gives_no_utc_but_keeps_the_stamp_note(self):
        report = scan_text(fixture.build_report('a16', zone=''))
        moment, note = report.time_value('2010-01-01 00:01:23')
        self.assertIsNone(moment)
        self.assertIn(reader.NOTE_NO_ZONE, note)
        self.assertIn(reader.NOTE_FACTORY_STAMP, note)


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def write(self, name, data):
        path = Path(self.work) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))
        return path

    def test_text_needs_the_banner(self):
        good = self.write('a/dumpstate.txt', fixture.build_report('a16'))
        bad = self.write('b/dumpstate.txt', 'no banner here\n')
        sources, notes = reader.find_sources([str(good), str(bad), str(Path(self.work) / 'missing.txt')])
        self.assertEqual([s.path for s in sources], [str(good)])
        self.assertEqual(len(notes), 1)

    def test_identical_copies_are_read_once(self):
        report = fixture.build_report('a16')
        first = self.write('data/log/dumpstate.txt', report)
        second = self.write('data/media/0/log/dumpstate.txt', report)
        other = self.write('other/dumpstate.txt', fixture.build_report('a10'))
        sources, notes = reader.find_sources([str(first), str(second), str(other)])
        self.assertEqual([s.path for s in sources], [str(first), str(other)])
        self.assertEqual(len(notes), 1)
        self.assertIn('byte-identical', notes[0])

    def test_same_size_different_content_is_read_twice(self):
        report = fixture.build_report('a16')
        changed = report.replace('== dumpstate: ', '== dumpstate: ', 1)[:-1] + ('x' if not report.endswith('x') else 'y')
        first = self.write('a/dumpstate.txt', report)
        second = self.write('b/dumpstate.txt', changed)
        self.assertEqual(first.stat().st_size, second.stat().st_size)
        sources, notes = reader.find_sources([str(first), str(second)])
        self.assertEqual(len(sources), 2)
        self.assertEqual(notes, [])

    def test_zip_main_text_is_taken_from_main_entry(self):
        archive = self.write('z/bugreport-x.zip', fixture.bug_report_zip('a16'))
        sources, notes = reader.find_sources([str(archive)])
        self.assertEqual(notes, [])
        self.assertEqual(sources[0].member, 'bugreport-example-EXAMPLE-2026-11-02-10-15-30.txt')

    def test_zip_without_main_entry_uses_the_largest_top_level_text(self):
        buffer = io.BytesIO()
        fixture.write_zip(buffer, [('dumpstate.txt', fixture.build_report('a10').encode()),
                                   ('dumpstate_log.txt', b'x' * 100000), ('FS/a.txt', b'y')])
        archive = self.write('z/bugreport-y.zip', buffer.getvalue())
        sources, _ = reader.find_sources([str(archive)])
        self.assertEqual(sources[0].member, 'dumpstate.txt')

    def test_damaged_zip_is_reported_not_raised(self):
        data = fixture.bug_report_zip('a16')
        broken = self.write('z/bugreport-broken.zip', data[:len(data) // 2])
        self.assertEqual(reader.find_sources([str(broken)])[0], [])
        self.assertEqual(len(reader.find_sources([str(broken)])[1]), 1)
        not_a_zip = self.write('z/bugreport-text.zip', b'plain text, not a zip')
        self.assertEqual(reader.find_sources([str(not_a_zip)])[0], [])

    def test_zip_that_breaks_after_the_banner_keeps_what_was_read(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('dumpstate.txt', fixture.build_report('a16'))
        data = bytearray(buffer.getvalue())
        data[len(data) // 2:len(data) // 2 + 40] = b'\x00' * 40            # damage the compressed stream
        archive_path = self.write('z/bugreport-damaged.zip', bytes(data))
        sources, _ = reader.find_sources([str(archive_path)])
        if sources:
            report = reader.read_report(sources[0])
            self.assertTrue(report.warnings or report.total_lines > 0)

    def test_reports_are_read_once_per_run(self):
        path = self.write('a/dumpstate.txt', fixture.build_report('a16'))
        sources, _ = reader.find_sources([str(path)])
        first = reader.read_report(sources[0])
        self.assertIs(reader.read_report(sources[0]), first)
        path.write_text(fixture.build_report('a10'), encoding='utf-8')
        self.assertIsNot(reader.read_report(sources[0]), first)           # a changed file is read again

    def test_the_file_is_not_modified(self):
        path = self.write('a/dumpstate.txt', fixture.build_report('a16'))
        before = (path.read_bytes(), path.stat().st_mtime_ns)
        context = Context(self.work, [path])
        for function in (device.bugreport_device_facts, device.bugreport_sections, device.bugreport_packages,
                         device.bugreport_package_times):
            function.__wrapped__(context)
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def stage(self, name, text):
        path = Path(self.work) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode('utf-8'))
        return path

    def run_artifact(self, function, *paths):
        return function.__wrapped__(Context(self.work, paths))

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', users=(0, 10)))
        for function in (device.bugreport_device_facts, device.bugreport_sections, device.bugreport_packages,
                         device.bugreport_package_times):
            headers, rows, source_path = self.run_artifact(function, path)
            self.assertTrue(rows)
            self.assertTrue(all(len(row) == len(headers) for row in rows))
            self.assertEqual(source_path, str(path))

    def test_device_facts(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        _headers, rows, _source = self.run_artifact(device.bugreport_device_facts, path)
        facts = {row[0]: row for row in rows}
        self.assertEqual(facts['Build fingerprint'][1],
                         'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys')
        self.assertEqual(facts['Report time (UTC)'][1], '2026-11-02 09:15:30')
        self.assertEqual(facts['Time zone used for UTC values'][1], 'Europe/Paris')
        self.assertEqual(facts['persist.sys.timezone'][2], 'getprop')
        self.assertEqual(facts['Kernel'][4], 'Dump/dumpstate.txt')

    def test_device_facts_without_a_zone(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone=''))
        _headers, rows, _source = self.run_artifact(device.bugreport_device_facts, path)
        facts = {row[0]: row for row in rows}
        self.assertEqual(facts['Report time (UTC)'][1], '')
        self.assertTrue(facts['Time zone used for UTC values'][1].startswith('none'))

    def test_sections_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        _headers, rows, _source = self.run_artifact(device.bugreport_sections, path)
        by_name = {row[0]: row for row in rows}
        self.assertEqual(by_name['preamble'][1], 'header')
        self.assertEqual(by_name['preamble'][7], 'Device Facts')
        self.assertEqual(by_name['package'][1], 'dumpsys service')
        self.assertEqual(by_name['package'][5], 0.321)
        self.assertEqual(by_name['package'][6], None)
        self.assertEqual(by_name['package'][7], 'Installed Packages; Package Times; Package Permissions; Permission Definitions')
        self.assertEqual(by_name['DUMPSYS CRITICAL'][1], 'dumpsys group')
        self.assertEqual(by_name['DUMPSYS'][7], 'not read')
        self.assertTrue(all(row[3] >= row[2] for row in rows))

    def test_package_times_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', users=(0, 10)))
        _headers, rows, _source = self.run_artifact(device.bugreport_package_times, path)
        by_key = {(row[2], row[3], row[4]): row for row in rows}
        update = by_key[('com.example.user.chat', 'lastUpdateTime', None)]
        self.assertEqual(update[0], datetime(2026, 10, 30, 6, 45, tzinfo=timezone.utc))
        self.assertEqual(update[1], '2026-10-30 07:45:00')
        self.assertEqual(update[7], '')
        no_time = by_key[('com.example.user.notime', 'timeStamp', None)]
        self.assertIsNone(no_time[0])
        self.assertEqual(no_time[7], reader.NOTE_UNSET)
        stamped = [row for row in rows if reader.NOTE_FACTORY_STAMP in row[7]]
        self.assertTrue(stamped)
        self.assertFalse([row for row in stamped if row[2].startswith('com.example.bulk')])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10'))
        alone = len(self.run_artifact(device.bugreport_packages, first)[1])
        both = self.run_artifact(device.bugreport_packages, first, second)[1]
        self.assertGreater(len(both), alone)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})
        same = self.run_artifact(device.bugreport_packages, first, first)[1]
        self.assertEqual(len(same), alone)                                  # the same file twice is read once

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in (device.bugreport_device_facts, device.bugreport_sections, device.bugreport_packages,
                         device.bugreport_package_times):
            headers, rows, source_path = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)
            self.assertEqual(source_path, str(path))

    def test_zip_on_the_device(self):
        path = self.stage('Dump/data/user_de/0/com.android.shell/files/bugreports/bugreport-example.zip',
                          fixture.bug_report_zip('a16'))
        _headers, rows, _source = self.run_artifact(device.bugreport_packages, path)
        self.assertEqual(len(rows), 52)
        self.assertTrue(rows[0][-1].endswith('bugreport-example.zip!/bugreport-example-EXAMPLE-2026-11-02-10-15-30.txt'))


if __name__ == '__main__':
    unittest.main()
