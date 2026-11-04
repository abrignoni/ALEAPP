"""Boot reason history and setup flags: the shared parsers, persistentProp and Setup Flags."""
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from admin.test.scripts import reset_boot_setup_fixture as fixture
from scripts import android_boot_reason as boot
from scripts import android_setup_flags as setup
from scripts.artifacts import androidSetupFlags as setupflags
from scripts.artifacts import persistentProp


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


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


class Workspace(unittest.TestCase):
    """A temporary folder that holds the files of a case and runs an artifact function over them."""

    def setUp(self):
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
# boot reason parser
# ---------------------------------------------------------------------------------------------
class BootParserTests(unittest.TestCase):
    def test_store_round_trip(self):
        data = fixture.persistent_properties([('a.b', 'one'), ('c.d', ''), ('e.f', 'x\ny'), ('g.h', 'café')])
        records, warning = boot.read_persistent_properties(data)
        self.assertEqual(warning, '')
        self.assertEqual([(r.name, r.value) for r in records], [('a.b', 'one'), ('c.d', ''), ('e.f', 'x\ny'), ('g.h', 'café')])

    def test_long_values_and_large_numbers(self):
        value = 'v' * 300
        records, _ = boot.read_persistent_properties(fixture.persistent_properties([('n' * 200, value)]))
        self.assertEqual(records[0].value, value)

    def test_truncated_store_keeps_the_records_before_the_cut(self):
        records, warning = boot.read_persistent_properties(fixture.store_truncated())
        self.assertGreater(len(records), 3)
        self.assertIn('reading stopped after', warning)

    def test_not_a_store(self):
        with self.assertRaises(boot.StoreError):
            boot.read_persistent_properties(b'This is a text file, not a store.\n')
        self.assertEqual(boot.read_persistent_properties(b''), ([], ''))

    def test_entries_and_flag(self):
        rows = boot.history_rows('reboot,userrequested,1790000000\nreboot,factory_reset,1789000000\nreboot,1788000000')
        self.assertEqual([(r.reason, r.subreason, r.epoch_text) for r in rows], [
            ('reboot', 'userrequested', '1790000000'), ('reboot', 'factory_reset', '1789000000'), ('reboot', '', '1788000000')])
        self.assertEqual([r.factory_reset for r in rows], [False, True, False])
        self.assertEqual(rows[0].moment, utc(2026, 9, 21, 14, 13, 20))
        self.assertEqual([r.position for r in rows], [0, 1, 2])

    def test_epoch_bounds(self):
        self.assertIsNone(boot.epoch_moment('100'))
        self.assertIsNone(boot.epoch_moment('99999999999999'))
        self.assertIsNone(boot.epoch_moment('-5'))
        self.assertIsNone(boot.epoch_moment('12.5'))
        self.assertIsNone(boot.epoch_moment(''))
        self.assertEqual(boot.epoch_moment('1230768000'), utc(2009, 1, 1))

    def test_single_value_properties(self):
        self.assertEqual(boot.single_rows('sys.boot.reason', ''), [])
        row = boot.single_rows('sys.boot.reason', 'reboot,recovery,extra')[0]
        self.assertEqual((row.reason, row.subreason, row.epoch_text, row.moment), ('reboot', 'recovery,extra', '', None))
        self.assertTrue(boot.single_rows('persist.sys.boot.reason', 'shutdown,Factory_Reset')[0].factory_reset)

    def test_rows_from_records_keep_only_boot_properties(self):
        records, _ = boot.read_persistent_properties(fixture.store_with_factory_reset())
        rows = boot.rows_from_records(records)
        self.assertEqual([r.property for r in rows], [boot.HISTORY_PROPERTY] * 4 + ['persist.sys.boot.reason'])


# ---------------------------------------------------------------------------------------------
# setup flag parser
# ---------------------------------------------------------------------------------------------
class SetupParserTests(unittest.TestCase):
    def test_names_and_users(self):
        self.assertEqual(setup.namespace_of('a/users/0/settings_secure.xml'), 'secure')
        self.assertEqual(setup.namespace_of('a\\users\\0\\settings_history_global.json'), 'global')
        self.assertEqual(setup.namespace_of('a/users/0/settings_global.xml.fallback'), '')
        self.assertEqual(setup.user_of('Dump/data/system/users/150/settings_secure.xml'), '150')
        self.assertEqual(setup.user_of('Dump/other/settings_secure.xml'), '')

    def test_ms_moment(self):
        self.assertEqual(setup.ms_moment('1780000000000'), utc(2026, 5, 28, 20, 26, 40))
        self.assertIsNone(setup.ms_moment('18199875'))
        self.assertIsNone(setup.ms_moment('x'))
        self.assertIsNone(setup.ms_moment('99999999999999999'))

    def test_history_rows(self):
        rows, warning = setup.history_rows(fixture.history_secure_json().decode(), 'secure', '0', 'f')
        self.assertEqual(warning, '')
        self.assertEqual([(r[2], r[3], r[0] is not None) for r in rows], [
            ('user_setup_complete', '0', False), ('user_setup_complete', '1', True), ('last_setup_shown', 'eclair_1', True)])
        self.assertEqual(rows[1][5], 'History entry (settings history file, mode 1)')
        self.assertEqual(rows[1][6], '0')
        self.assertEqual(setup.history_rows('{bad', 'secure', '0', 'f')[0], [])
        self.assertEqual(setup.history_rows('[1]', 'secure', '0', 'f')[0], [])


# ---------------------------------------------------------------------------------------------
# artifacts of the file system side
# ---------------------------------------------------------------------------------------------
class FileSystemArtifactTests(Workspace):
    def test_boot_reason_entries_from_the_store(self):
        cases = fixture.ffs_cases()['get_persistentProp']
        headers, rows, source = self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_factory_reset'])
        self.assertEqual(self.column(headers, rows, 'factory_reset Reason Present'), ['no', 'yes', 'no', 'no', 'yes'])
        self.assertEqual(self.column(headers, rows, 'Timestamp')[1], utc(2026, 5, 10, 7, 30, 15))
        self.assertEqual(self.column(headers, rows, 'Reason')[1:2], ['reboot'])
        self.assertEqual(self.column(headers, rows, 'Subreason')[1:2], ['factory_reset'])
        self.assertEqual(self.column(headers, rows, 'Event')[1], 'reboot,factory_reset')
        self.assertEqual(self.column(headers, rows, 'Input Line Ordinal'), [''] * 5)
        self.assertEqual(source, 'Dump/data/property/persistent_properties')
        _, rows, _ = self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_no_factory_reset'])
        self.assertEqual({row[10] for row in rows}, {'no'})
        self.assertEqual(len(rows), 2)

    def test_boot_reason_store_edge_cases(self):
        cases = fixture.ffs_cases()['get_persistentProp']
        self.assertEqual(self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_not_a_store'])[1], [])
        self.assertEqual(self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_empty_store'])[1], [])
        self.assertEqual(len(self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_truncated'])[1]), 5)
        _, rows, _ = self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_odd_entries'])
        self.assertEqual([r[10] for r in rows], ['no'] * 6 + ['yes'])

    def test_a_text_file_is_read_with_the_earlier_rules(self):
        cases = fixture.ffs_cases()['get_persistentProp']
        headers, rows, _ = self.run_artifact(persistentProp.get_persistentProp, cases['synthetic_text_lines'])
        self.assertEqual(self.column(headers, rows, 'Event'), ['persist.sys.boot.reason.historyDreboot', 'reboot', 'reboot factory_reset'])
        self.assertEqual(len(rows), 3)
        self.assertEqual({row[6:] for row in rows}, {('', '', '', '', '')})        # the columns of the store reading stay blank
        self.assertEqual(self.column(headers, rows, 'Timestamp')[1], utc(2026, 9, 30, 0, 0, 0))

    def test_setup_flags_xml_and_history(self):
        cases = fixture.ffs_cases()['android_setup_flags']
        headers, rows, _ = self.run_artifact(setupflags.android_setup_flags, cases['synthetic_xml_two_users'])
        names = self.column(headers, rows, 'Setting')
        records = self.column(headers, rows, 'Record')
        self.assertEqual(sum(1 for r in records if r.startswith('Current')), 4)
        self.assertEqual(sum(1 for r in records if r.startswith('History')), 6)
        self.assertEqual(sum(1 for r in records if r == 'Persistent property'), 3)
        self.assertNotIn('android_id', names)
        self.assertNotIn('adb_enabled', names)
        users = {(n, u): v for n, u, v, r in zip(names, self.column(headers, rows, 'User'), self.column(headers, rows, 'Value'), records)
                 if r.startswith('Current') and n == 'user_setup_complete'}
        self.assertEqual(users, {('user_setup_complete', '0'): '1', ('user_setup_complete', '10'): '0'})
        times = [t for t, r in zip(self.column(headers, rows, 'Time (UTC)'), records) if r.startswith('History') and t is not None]
        self.assertEqual(set(times), {utc(2026, 5, 28, 20, 26, 40), utc(2026, 5, 28, 20, 26, 40, 500000)})

    def test_setup_flags_abx_matches_xml(self):
        cases = fixture.ffs_cases()['android_setup_flags']
        headers, rows, _ = self.run_artifact(setupflags.android_setup_flags, cases['synthetic_abx'])
        current = {(r[8], r[2]): r[3] for r in rows if r[5].startswith('Current')}
        self.assertEqual(current[('secure', 'user_setup_complete')], '1')
        self.assertEqual(len(current), 3)
        self.assertEqual(len(rows), 6)
        self.assertEqual(headers[0], ('Time (UTC)', 'datetime'))

    def test_setup_flags_do_not_repeat_the_rows_of_settings_global(self):
        patterns = setupflags.__artifacts_v2__['android_setup_flags']['paths']
        self.assertFalse([p for p in patterns if p.endswith('settings_global.xml')])

    def test_setup_flags_skip_a_mirror_copy(self):
        members = [('Dump/mirror/data/system/users/0/settings_secure.xml', fixture.settings_xml(fixture.secure_settings()))]
        self.assertEqual(self.run_artifact(setupflags.android_setup_flags, members)[1], [])

    def test_setup_flags_absent_and_unreadable(self):
        cases = fixture.ffs_cases()['android_setup_flags']
        self.assertEqual(self.run_artifact(setupflags.android_setup_flags, cases['synthetic_no_flags'])[1], [])
        self.assertEqual(self.run_artifact(setupflags.android_setup_flags, cases['synthetic_malformed_settings'])[1], [])


# ---------------------------------------------------------------------------------------------
# registration, names and committed case files
# ---------------------------------------------------------------------------------------------
MODULES = (('persistentProp', persistentProp), ('androidSetupFlags', setupflags))


class RegistrationTests(unittest.TestCase):
    def test_names_categories_and_paths(self):
        for module in (persistentProp, setupflags):
            self.assertEqual({info['category'] for info in module.__artifacts_v2__.values()}, {'Wipe & Setup'})
        for _name, module in MODULES:
            for key in module.__artifacts_v2__:
                self.assertTrue(callable(getattr(module, key)), key)

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
