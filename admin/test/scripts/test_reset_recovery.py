"""Recovery history: the shared parser, sRecoveryhist and Bug Report - Recovery History."""
# pylint: disable=protected-access
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from datetime import datetime
from pathlib import Path

from admin.test.scripts import reset_recovery_fixture as fixture
from scripts import android_recovery_history as recovery
from scripts import dumpstate_reader as reader
from scripts.artifacts import bugreportRecovery as bug
from scripts.artifacts import sRecoveryhist
from scripts.artifacts import sWipehist


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


def unwrap(function):
    while hasattr(function, '__wrapped__'):
        function = function.__wrapped__
    return function


class Workspace(unittest.TestCase):
    """A temporary folder that holds the files of a case and runs an artifact function over them."""

    def setUp(self):
        reader.clear_cache()
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def stage(self, members):
        paths = []
        for name, data in members:
            path = Path(self.root) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            paths.append(path)
        return paths

    def run_artifact(self, function, members):
        paths = self.stage(members)
        context = Context(self.root, paths)
        headers, rows, source = unwrap(function)(context)
        return headers, rows, source

    def column(self, headers, rows, name):
        index = [h[0] if isinstance(h, tuple) else h for h in headers].index(name)
        return [row[index] for row in rows]


# ---------------------------------------------------------------------------------------------
# recovery history parser
# ---------------------------------------------------------------------------------------------
class RecoveryParserTests(unittest.TestCase):
    def setUp(self):
        self.entries, self.warnings = recovery.parse_history(fixture.wipe_and_sim_history())

    def test_entries_and_fields(self):
        self.assertEqual([e.code for e in self.entries], ['Aa', 'Bb', 'Cc', 'Dd', 'Ee'])
        self.assertEqual(self.warnings, [])
        wipe = self.entries[0]
        self.assertEqual(wipe.header_text, '1970/01/01 02:10:00')
        self.assertEqual(wipe.firmware, 'EXAMPLEFW1')
        self.assertEqual(wipe.requested, '2026/03/10 09:00:00.250')
        self.assertEqual(wipe.requested_time, datetime(2026, 3, 10, 9, 0, 0, 250000))
        self.assertEqual(wipe.reason, 'MasterClearConfirm,2026-01-01T00:00:00Z')
        self.assertEqual(wipe.status, 'NP [-]')
        self.assertEqual(wipe.reboot_reason, 'Reboot:100 RecoverySystem MasterClearConfirm')
        self.assertEqual(wipe.options[0], '--wipe_data')
        self.assertEqual(self.entries[3].status, 'RP | OFFSRC: - / ONSRC: PWRON / RSTSTAT: SWRESET')
        self.assertEqual(self.entries[3].update_package, '@/cache/recovery/block.map')

    def test_activity_words(self):
        self.assertEqual([e.activity for e in self.entries], [
            'Wipe requested (--wipe_data)', 'SIM region change (AAA -> BBB)', 'Wipe requested (--wipe_data)',
            'Update package (--update_package)', 'SIM region change (BBB -> CCC)'])
        self.assertEqual(recovery.activity_of(['--data_resizing'], ''), 'Other')
        self.assertEqual(recovery.activity_of(['--prompt_and_wipe_data'], ''), 'Prompt and wipe requested (--prompt_and_wipe_data)')
        self.assertEqual(recovery.activity_of(['--wipe_data', '--update_package=x'], ''),
                         'Wipe requested (--wipe_data); Update package (--update_package)')
        self.assertEqual(recovery.activity_of(['--just_exit'], '[SIMBasedChangeCSC] XAA->TMB'), 'SIM region change (XAA -> TMB)')

    def test_extra_history_volumes(self):
        extra, warnings = recovery.parse_extra_history(fixture.wipe_and_sim_extra())
        self.assertEqual(warnings, [])
        self.assertEqual(extra.created, 'Thu Jan  1 02:10:00 1970')
        volumes = recovery.formatted_volumes(extra)
        self.assertEqual(recovery.volumes_text(volumes['Aa']), '/data (start and end lines); /cache (start and end lines)')
        self.assertEqual(recovery.volumes_text(volumes['Cc']), '/data (start and end lines); /metadata (start line only)')
        self.assertEqual(sorted(volumes), ['Aa', 'Cc', 'Zz'])

    def test_records_attach_volumes_by_code_and_list_a_code_without_an_entry(self):
        records = recovery.records_from_texts(fixture.wipe_and_sim_history(), fixture.wipe_and_sim_extra(), 'history', 'extra_history')
        self.assertEqual(len(records), 6)
        by_code = {record['code']: record for record in records}
        self.assertEqual(by_code['Aa']['volumes'], '/data (start and end lines); /cache (start and end lines)')
        self.assertEqual(by_code['Bb']['volumes'], '')
        self.assertEqual(by_code['Zz']['activity'], 'No entry in the history file for this code')
        self.assertEqual(by_code['Zz']['source'], 'extra_history')
        self.assertIsNone(by_code['Zz']['entry'])
        self.assertNotIn('estimate', by_code['Bb'])
        self.assertEqual((by_code['Aa']['header_text'], by_code['Aa']['requested']), ('1970/01/01 02:10:00', '2026/03/10 09:00:00.250'))
        self.assertEqual((by_code['Bb']['header_text'], by_code['Bb']['requested']), ('1970/01/01 02:50:00', ''))
        rows = recovery.rows_for(*recovery.parse_history(fixture.wipe_and_sim_history())[:1], None, 'history')
        self.assertTrue(all(len(row) == len(recovery.ROW_KEYS) for row in rows))

    def test_option_values(self):
        entries, _ = recovery.parse_history(fixture.wipe_and_sim_history())
        self.assertEqual(recovery.option_value(entries[3], '--locale'), 'en-US')
        self.assertEqual(recovery.option_value(entries[3], '--carry_out'), 'open_fota')
        self.assertEqual(recovery.option_value(entries[0], '--carry_out'), '')

    def test_older_header_shape_without_brackets(self):
        entries, _ = recovery.parse_history('+ oldtag : 2021/01/02 03:04:05\n--wipe_data\n+junk\n')
        self.assertEqual([(e.code, e.header_text) for e in entries], [('', '2021/01/02 03:04:05'), ('', 'junk')])
        self.assertEqual(entries[0].options, ('--wipe_data',))

    def test_a_header_whose_first_bracket_closes_after_the_tag(self):
        text = ('+ [Qq] | 2026/01/02 03:04:05 | EXAMPLEFW9]\n--wipe_data\n'
                '+ [Rr] | 2026/01/03 03:04:05 | EXAMPLEFW9] [-]\n'
                '+ [Ss | 2026/01/04 03:04:05 | EXAMPLEFW9] [-]\n')
        entries, warnings = recovery.parse_history(text)
        self.assertEqual(warnings, [])
        self.assertEqual([(e.code, e.header_text, e.firmware) for e in entries],
                         [('Qq', '2026/01/02 03:04:05', 'EXAMPLEFW9'), ('Rr', '2026/01/03 03:04:05', 'EXAMPLEFW9'),
                          ('Ss', '2026/01/04 03:04:05', 'EXAMPLEFW9')])
        self.assertEqual(entries[0].header_time, datetime(2026, 1, 2, 3, 4, 5))
        self.assertEqual(recovery.entry_notes(entries[0], False), [])

    def test_a_lone_dash_separator_is_not_an_other_line(self):
        entries, _ = recovery.parse_history('+ [Qq | 2026/01/02 03:04:05 | EXAMPLEFW9]\n--wipe_data\nsome words\n - \n-\n'
                                            '+ [Rr | 2026/01/03 03:04:05 | EXAMPLEFW9]\n- not a separator\n-\n')
        self.assertEqual([e.other_lines for e in entries], [('some words',), ('- not a separator',)])

    def test_header_variants(self):
        entries, warnings = recovery.parse_history(fixture.malformed_history())
        self.assertEqual(len(entries), 3)
        self.assertEqual(warnings, ['1 non-blank lines before the first entry header were not read'])
        self.assertEqual(entries[0].code, '')
        self.assertEqual(entries[0].header_text, 'oldstyle header 2020/01/01 00:00:00')
        self.assertIsNone(entries[0].header_time)
        self.assertEqual(entries[1].header_text, 'not a date')
        self.assertIsNone(entries[1].requested_time)
        self.assertEqual(entries[1].reason, 'bad reason')           # the control character is shown as a space
        self.assertEqual(entries[1].reboot_reason, 'spaced form')
        self.assertEqual(entries[1].other_lines, ('status words',))
        self.assertEqual(entries[2].firmware, '')

    def test_empty_and_odd_inputs(self):
        self.assertEqual(recovery.parse_history(''), ([], []))
        self.assertEqual(recovery.parse_history('\n\n  \n'), ([], []))
        entries, warnings = recovery.parse_history('only text\nmore text\n')
        self.assertEqual(entries, [])
        self.assertEqual(len(warnings), 1)
        extra, warnings = recovery.parse_extra_history(fixture.malformed_extra())
        self.assertEqual(extra.created, 'never')
        self.assertEqual(len(warnings), 1)
        self.assertEqual(recovery.volumes_text(recovery.formatted_volumes(extra)['Nn']),
                         '/data (no start or end line); (no volume named) (start and end lines)')

    def test_crlf_text(self):
        entries, _ = recovery.parse_history(fixture.wipe_and_sim_history().replace('\n', '\r\n'))
        self.assertEqual([e.code for e in entries], ['Aa', 'Bb', 'Cc', 'Dd', 'Ee'])
        self.assertEqual(entries[0].requested, '2026/03/10 09:00:00.250')

    def test_pairing_of_files(self):
        files = [('f', 'last_history', 'a/last_history', fixture.no_wipe_history()),
                 ('f', 'last_all_history', 'a/last_all_history', fixture.no_wipe_history()),
                 ('f', 'last_extra_history', 'a/last_extra_history', 'Created at x\n[Gg][S] format_volume : /data\n'),
                 ('g', 'extra_history', 'b/extra_history', 'Created at x\n[Qq][S] format_volume : /cache\n')]
        messages = []
        rows = recovery.rows_from_files(files, lambda label, text: messages.append((label, text)))
        self.assertEqual(len(rows), 4 + 4 + 1)
        code, volume, source = (recovery.ROW_KEYS.index(key) for key in ('code', 'volumes', 'source'))
        volumes = [(row[code], row[volume], row[source]) for row in rows if row[volume]]
        self.assertEqual(sorted(volumes), [('Gg', '/data (start line only)', 'a/last_all_history'),
                                           ('Gg', '/data (start line only)', 'a/last_history'),
                                           ('Qq', '/cache (start line only)', 'b/extra_history')])
        self.assertEqual(messages, [])

    def test_an_orphan_code_of_a_shared_extra_file_is_listed_once(self):
        files = [('f', 'last_history', 'a/last_history', fixture.no_wipe_history()),
                 ('f', 'last_all_history', 'a/last_all_history', fixture.no_wipe_history()),
                 ('f', 'last_extra_history', 'a/last_extra_history', 'Created at x\n[Qq][S] format_volume : /cache\n')]
        records = recovery.records_from_files(files)
        orphans = [record for record in records if record['entry'] is None]
        self.assertEqual([(record['code'], record['source']) for record in orphans], [('Qq', 'a/last_extra_history')])
        self.assertEqual(len(records), 4 + 4 + 1)


# ---------------------------------------------------------------------------------------------
# artifacts of the file system side
# ---------------------------------------------------------------------------------------------
class FileSystemArtifactTests(Workspace):
    def recovery_rows(self, case):
        return self.run_artifact(sRecoveryhist.get_sRecoveryhist, fixture.ffs_cases()['get_sRecoveryhist'][case])
    def test_recovery_history_efs(self):
        headers, rows, source = self.recovery_rows('synthetic_wipe_and_sim')
        self.assertEqual(len(headers), 21)
        self.assertEqual(list(headers[:12]), ['Timestamp', 'Request Timestamp', 'Build', 'Entry Tag (as stored)', 'Wipe', 'Prompt & Wipe',
                                              'Reason', 'Reboot Reason', 'Locale', 'Carry Out', 'Update ORG', 'Update PKG'])
        self.assertEqual(headers[-1], 'Source File')
        self.assertEqual(self.column(headers, rows, 'Entry Tag (as stored)'), ['Aa', 'Bb', 'Cc', 'Dd', 'Ee', 'Zz'])
        self.assertEqual(set(self.column(headers, rows, 'Source File')) - {'Dump/efs/recovery/extra_history'}, {'Dump/efs/recovery/history'})
        self.assertEqual(source, 'Dump/efs/recovery/extra_history\nDump/efs/recovery/history')

    def test_the_columns_of_the_earlier_reading_keep_their_form(self):
        headers, rows, _ = self.recovery_rows('synthetic_wipe_and_sim')
        first = dict(zip(headers, rows[0]))
        self.assertEqual(first['Timestamp'], '1970-01-01 02:10:00')                  # slashes replaced by dashes, as before
        self.assertEqual(first['Request Timestamp'], '2026-03-10 09:00:00.250')
        self.assertEqual(first['Build'], 'EXAMPLEFW1')                                 # no closing bracket or dash of ' [-]'
        self.assertEqual((first['Wipe'], first['Prompt & Wipe']), ('Yes', ''))
        self.assertEqual(first['Reason'], 'MasterClearConfirm,2026-01-01T00:00:00Z')
        update = dict(zip(headers, rows[3]))
        self.assertEqual((update['Locale'], update['Carry Out'], update['Update PKG']), ('en-US', 'open_fota', '@/cache/recovery/block.map'))
        self.assertEqual(update['Activity'], 'Update package (--update_package)')
        sim = dict(zip(headers, rows[1]))
        self.assertEqual((sim['Timestamp'], sim['Request Timestamp']), ('1970-01-01 02:50:00', ''))   # as printed, nothing derived
        self.assertEqual(sim['Entry Notes'], 'header date is before 2012, shown as printed')
        self.assertFalse([h for h in headers if 'stimat' in h or 'Basis' in h])

    def test_the_wipe_rows_of_swipehist_are_the_wipe_rows_of_srecoveryhist(self):
        paths = self.stage(fixture.ffs_cases()['get_sRecoveryhist']['synthetic_wipe_and_sim'])
        headers, rows, _ = sRecoveryhist.get_sRecoveryhist.__wrapped__(Context(self.root, paths))
        _, wipe_rows, _ = sWipehist.get_sWipehist.__wrapped__(Context(self.root, [p for p in paths if p.name == 'history']))
        ours = sorted(row[0] for row in rows if row[headers.index('Wipe')] == 'Yes' or row[headers.index('Prompt & Wipe')] == 'Yes')
        self.assertEqual(sorted(row[0] for row in wipe_rows), ours)

    def test_recovery_history_cache_files_and_repeated_code(self):
        headers, rows, _ = self.recovery_rows('synthetic_cache_recovery')
        sources = self.column(headers, rows, 'Source File')
        self.assertEqual(sorted(set(sources)), ['Dump/cache/recovery/last_all_history', 'Dump/cache/recovery/last_extra_history',
                                                'Dump/cache/recovery/last_history', 'Dump/efs/recovery/history'])
        notes = [n for n, c in zip(self.column(headers, rows, 'Entry Notes'), self.column(headers, rows, 'Entry Tag (as stored)')) if c == 'Mm']
        self.assertEqual(len(notes), 2)
        self.assertTrue(all('more than one entry' in n for n in notes))

    def test_recovery_history_empty_and_malformed(self):
        self.assertEqual(self.recovery_rows('synthetic_empty')[1], [])
        _, rows, _ = self.recovery_rows('synthetic_malformed')
        self.assertEqual(len(rows), 3)


# ---------------------------------------------------------------------------------------------
# bug report artifact
# ---------------------------------------------------------------------------------------------
class BugReportArtifactTests(Workspace):
    def test_recovery_history_from_the_zip(self):
        cases = fixture.bugreport_cases()['bugreport_recovery_history']
        headers, rows, source = self.run_artifact(bug.bugreport_recovery_history, cases['synthetic_zip_recovery'])
        self.assertEqual(headers, sRecoveryhist.DATA_HEADERS)
        self.assertEqual(len(rows), 11)          # 5 + 5 entries and one code of the shared extra file, listed once
        sources = sorted(set(self.column(headers, rows, 'Source File')))
        base = 'Dump/bugreport-example-2026-11-02-10-15-30.zip!/FS/cache/recovery/'
        self.assertEqual(sources, [base + 'last_all_history', base + 'last_extra_history', base + 'last_history'])
        self.assertEqual(source, str(Path(self.root) / 'Dump' / 'bugreport-example-2026-11-02-10-15-30.zip'))
        activity, source_file = headers.index('Activity'), headers.index('Source File')
        wipes = [r for r in rows if r[activity].startswith('Wipe') and r[source_file].endswith('last_history')]
        self.assertEqual(len(wipes), 2)
        tag, requested = headers.index('Entry Tag (as stored)'), headers.index('Request Timestamp')
        self.assertEqual({r[requested] for r in rows if r[tag] == 'Bb'}, {''})

    def test_the_rows_are_those_of_srecoveryhist_for_the_same_files(self):
        members = fixture.recovery_members()
        zipped = self.run_artifact(bug.bugreport_recovery_history, [('Dump/bugreport-example-2026-11-02-10-15-30.zip',
                                                                      fixture.bug_report_zip(fixture.bug_report(), members))])[1]
        loose = self.run_artifact(sRecoveryhist.get_sRecoveryhist, [('Dump/' + name, data) for name, data in members
                                                                    if name.startswith('FS/cache/recovery/last_') and 'old' not in name])[1]
        width = sRecoveryhist.DATA_HEADERS.index('Extra History File')
        self.assertEqual(sorted(row[:width] for row in zipped), sorted(row[:width] for row in loose))

    def test_recovery_history_absent(self):
        cases = fixture.bugreport_cases()['bugreport_recovery_history']
        self.assertEqual(self.run_artifact(bug.bugreport_recovery_history, cases['synthetic_zip_no_recovery'])[1], [])

    def test_a_bug_report_text_alone_gives_no_rows_and_the_log_names_srecoveryhist(self):
        messages = []
        original = bug.logfunc
        bug.logfunc = messages.append
        try:
            _, rows, _ = self.run_artifact(bug.bugreport_recovery_history, [('Dump/dumpstate.txt', fixture.bug_report().encode())])
        finally:
            bug.logfunc = original
        self.assertEqual(rows, [])
        self.assertTrue(any('sRecoveryhist reads them' in m for m in messages))

    def test_recovery_history_unset_clock(self):
        cases = fixture.bugreport_cases()['bugreport_recovery_history']
        headers, rows, _ = self.run_artifact(bug.bugreport_recovery_history, cases['synthetic_zip_unset_clock'])
        self.assertEqual(self.column(headers, rows, 'Timestamp'), ['1970-01-01 00:05:00', '2010-01-01 00:06:15', '1970-01-02 00:00:00'])
        self.assertEqual(self.column(headers, rows, 'Request Timestamp'), ['', '', ''])
        self.assertEqual(self.column(headers, rows, 'Entry Notes'), ['header date is before 2012, shown as printed'] * 3)

    def test_recovery_history_damaged_zip_is_reported_and_skipped(self):
        messages = []
        original = bug.logfunc
        bug.logfunc = messages.append
        try:
            _, rows, _ = self.run_artifact(bug.bugreport_recovery_history, [('Dump/bugreport-broken.zip', b'PK\x03\x04 not a zip')])
        finally:
            bug.logfunc = original
        self.assertEqual(rows, [])
        self.assertTrue(any('could not be opened' in m for m in messages))


# ---------------------------------------------------------------------------------------------
# registration, names and committed case files
# ---------------------------------------------------------------------------------------------
MODULES = (('sRecoveryhist', sRecoveryhist), ('bugreportRecovery', bug))


class RegistrationTests(unittest.TestCase):
    def test_names_categories_and_paths(self):
        for key, info in bug.__artifacts_v2__.items():
            self.assertTrue(info['name'].startswith('Bug Report - '), key)
            self.assertTrue(info['category'].startswith('Android Bug Report - '), key)
            self.assertTrue(set(info['paths']) <= {'*/bugreport-*.zip', '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'}, key)
        self.assertEqual({info['category'] for info in sRecoveryhist.__artifacts_v2__.values()}, {'Wipe & Setup'})
        for _name, module in MODULES:
            for key in module.__artifacts_v2__:
                self.assertTrue(callable(getattr(module, key)), key)

    def test_one_artifact_reads_each_recovery_file(self):
        recovery_paths = set(sRecoveryhist.__artifacts_v2__['get_sRecoveryhist']['paths'])
        self.assertEqual(recovery_paths, {'*/efs/recovery/history', '*/efs/recovery/extra_history', '*/cache/recovery/last_history',
                                          '*/cache/recovery/last_all_history', '*/cache/recovery/last_extra_history'})
        # the bug report artifact reads zips only, and never a loose recovery file
        self.assertTrue(all(path.endswith('.zip') for path in bug.__artifacts_v2__['bugreport_recovery_history']['paths']))

    def test_every_case_has_its_zip_and_the_json_lists_it(self):
        root = Path(__file__).resolve().parents[3]
        for module, artifacts in MODULES:
            data = json.loads((root / 'admin' / 'test' / 'cases' / ('testdata.%s.json' % module)).read_text(encoding='utf-8'))
            expected = {'case' + name for artifact, named in fixture.cases().items() if fixture.MODULE_OF[artifact] == module
                        for name in named}
            self.assertEqual(sorted(data), sorted(expected))
            for key, case in data.items():
                for artifact, entry in case['artifacts'].items():
                    self.assertIn(artifact, artifacts.__artifacts_v2__)
                    self.assertEqual(entry['search_patterns'], list(artifacts.__artifacts_v2__[artifact]['paths']))
                    zip_path = root / 'admin' / 'test' / 'cases' / 'data' / module / ('testdata.%s.%s.%s.zip' % (module, artifact, key))
                    self.assertTrue(zip_path.exists(), zip_path)
                    with zipfile.ZipFile(zip_path) as archive:
                        self.assertEqual(len(archive.namelist()), entry['file_count'])


if __name__ == '__main__':
    unittest.main()
