"""Android bug report text: package permissions, permission definitions, app ops modes and accesses, roles, permissionmgr."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as base_fixture
from admin.test.scripts import bugreport_permissions_fixture as fixture
from scripts import dumpstate_permissions as permissions
from scripts import dumpstate_reader as reader
from scripts.artifacts import bugreportDevice
from scripts.artifacts import bugreportPermissions as artifacts


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


def rows(report, name):
    return permissions.rows_of(report, name)


def section_text(service, body, cut=False):
    """A small report text that holds one dumpsys service section."""
    end = "*** SERVICE '%s' DUMP TIMEOUT (10000ms) EXPIRED ***\n" % service if cut else \
        '--------- 0.1s was the duration of dumpsys %s, ending at: 2026-11-02 10:15:12\n' % service
    return ('== dumpstate: 2026-11-02 10:15:30\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE %s:\n%s\n%s'
            % (service, body, end))


class HelperTests(unittest.TestCase):
    def test_registration_in_the_shared_reader(self):
        classes = reader.readers_by_section()
        for service, expected in (('package', permissions.PackagePermissionsReader), ('appops', permissions.AppOpsReader),
                                  ('role', permissions.RoleReader), ('permissionmgr', permissions.PermissionManagerReader)):
            self.assertIn(expected, classes[('service', service)])
        self.assertEqual(reader.READ_BY[('service', 'package')],
                         'Installed Packages; Package Times; Package Permissions; Permission Definitions')
        self.assertEqual(reader.READ_BY[('service', 'appops')], 'App Ops Modes; App Ops Accesses')

    def test_duration_text(self):
        self.assertEqual(permissions.duration_ms('+250ms'), 250)
        self.assertEqual(permissions.duration_ms('+1d2h3m4s5ms'), 93784005)
        self.assertEqual(permissions.duration_ms('+1m0s0ms'), 60000)
        self.assertEqual(permissions.duration_ms('-5s20ms'), -5020)
        self.assertEqual(permissions.duration_ms('10s'), 10000)
        for text in ('', '+', 'x', '5', '1h x', '+1x', '+1m ms', 'ms', '--1s'):
            self.assertIsNone(permissions.duration_ms(text), text)
        self.assertIsNone(permissions.duration_ms('²s'))        # superscript digits are not numbers here

    def test_numeric_uid(self):
        self.assertEqual(permissions.uid_number('1000'), 1000)
        self.assertEqual(permissions.uid_number('u0a147'), 10147)
        self.assertEqual(permissions.uid_number('u10a100'), 1010100)
        self.assertEqual(permissions.uid_number('u11s1000'), 1101000)
        for text in ('u0i1', 'u0ai9000', 'root', '', 'u0a', 'ua1', '²', 'u0a²'):
            self.assertIsNone(permissions.uid_number(text), text)

    def test_permission_line(self):
        parse = permissions.parse_permission_line
        self.assertEqual(parse('a.b.C: granted=true'), ('a.b.C', 'true', '', None))
        self.assertEqual(parse('a.b.C: granted=false, flags=[ X|Y]'), ('a.b.C', 'false', 'X|Y', None))
        self.assertEqual(parse('a.b.C: granted=true, flags=[ GRANTED_BY_ROLE], userId=11'), ('a.b.C', 'true', 'GRANTED_BY_ROLE', 11))
        self.assertEqual(parse('a.b.C: granted=false, userId=11'), ('a.b.C', 'false', '', 11))
        self.assertEqual(parse('a.b.C: granted=maybe, flags=[]'), ('a.b.C', 'maybe', '', None))
        for text in ('', 'a.b.C', 'a.b.C: prot=signature', ': granted=true', 'two words: granted=true'):
            self.assertIsNone(parse(text), text)


class PackageTests(unittest.TestCase):
    def test_permission_lines_of_each_holder(self):
        report = scan_text(fixture.build_report('a16', zone='UTC'))
        found = [(r.holder_type, r.holder, r.kind, r.user, r.permission, r.granted, r.flags) for r in rows(report, 'package_permissions')]
        self.assertEqual(found, [
            ('Package', 'com.example.user.chat', 'install', None, 'android.permission.INTERNET', 'true', ''),
            ('Package', 'com.example.user.chat', 'install', None, 'android.permission.EXAMPLE_PRIV', 'false', ''),
            ('Package', 'com.example.user.chat', 'install', None, 'android.permission.SCHEDULE_EXACT_ALARM', 'true', 'GRANTED_BY_ROLE'),
            ('Package', 'com.example.user.chat', 'runtime', 0, 'android.permission.CAMERA', 'false', 'USER_SENSITIVE_WHEN_GRANTED'),
            ('Package', 'com.example.user.chat', 'runtime', 0, 'android.permission.READ_CONTACTS', 'true',
             'USER_SET|USER_SENSITIVE_WHEN_GRANTED'),
            ('Package', 'com.example.user.chat', 'runtime', 10, 'android.permission.CAMERA', 'true', 'USER_SET'),
            ('Package', 'com.example.system.settings', 'runtime', 0, 'android.permission.POST_NOTIFICATIONS', 'true', 'GRANTED_BY_DEFAULT'),
            ('Hidden system package', 'com.example.system.updated', 'install', None, 'android.permission.VIBRATE', 'true', ''),
            ('Hidden system package', 'com.example.system.updated', 'runtime', 0, 'android.permission.READ_CALENDAR', 'false', ''),
            ('Shared user', 'android.uid.example', 'install', None, 'android.permission.WRITE_SECURE_SETTINGS', 'true', ''),
            ('Shared user', 'android.uid.example', 'install', None, 'android.permission.MANAGE_EXAMPLE', 'false', ''),
            ('Shared user', 'android.uid.example', 'runtime', 0, 'android.permission.RECORD_AUDIO', 'true', 'SYSTEM_FIXED|PREGRANT'),
        ])
        by_holder = {r.holder: r.app_id for r in rows(report, 'package_permissions')}
        self.assertEqual(by_holder, {'com.example.user.chat': 10100, 'com.example.system.settings': 1000,
                                     'com.example.system.updated': 10120, 'android.uid.example': 1000})

    def test_other_lists_of_the_dump_are_not_permission_rows(self):
        names = {r.permission for r in rows(scan_text(fixture.build_report('a16')), 'package_permissions')}
        self.assertFalse([name for name in names if 'NOT_A_ROW' in name or name.endswith('.DECLARED')])
        # the sharedUser package has no permission rows of its own besides the runtime line it prints
        report = scan_text(fixture.build_report('a16'))
        self.assertEqual([r.kind for r in rows(report, 'package_permissions') if r.holder == 'com.example.system.settings'], ['runtime'])

    def test_user_id_on_an_install_line(self):
        report = scan_text(fixture.build_report('a15'))
        listed = [(r.permission, r.granted, r.user) for r in rows(report, 'package_permissions') if r.kind == 'install' and r.user is not None]
        self.assertEqual(listed, [('android.permission.SYSTEM_ALERT_WINDOW', 'false', 11)])
        self.assertEqual(sorted({r.user for r in rows(report, 'package_permissions') if r.kind == 'runtime'}), [0, 11])

    def test_heading_one_level_deeper_after_overlay_paths(self):
        report = scan_text(fixture.build_report('a10'))
        chat = [(r.user, r.permission) for r in rows(report, 'package_permissions')
                if r.holder == 'com.example.user.chat' and r.kind == 'runtime']
        self.assertEqual(chat, [(0, 'android.permission.CAMERA'), (0, 'android.permission.READ_CONTACTS')])
        self.assertEqual({r.app_id for r in rows(report, 'package_permissions') if r.holder == 'com.example.user.chat'}, {10100})   # userId=

    def test_definitions(self):
        report = scan_text(fixture.build_report('a16'))
        found = [(r.permission, r.source_package, r.uid, r.gids, r.perm_type, r.protection, r.flags) for r in rows(report, 'permission_definitions')]
        self.assertEqual(found[0], ('android.permission.EXAMPLE_SIGNATURE', 'android', '1000', '[]', '0', 'signature|privileged', '0x0'))
        self.assertEqual(found[3], ('android.permission.EXAMPLE_GROUPED', 'android', '1000', '[2001, 3003]', '0', 'normal|instant', '0x20'))
        self.assertEqual(len(found), 4)
        old = [(r.gids, r.flags) for r in rows(scan_text(fixture.build_report('a10')), 'permission_definitions')]
        self.assertEqual(old, [('null', '')] * 4)

    def test_a_package_dump_without_blocks_gives_nothing(self):
        report = scan_text(section_text('package', 'Database versions:\n  Internal:\n    sdkVersion=36\n'))
        self.assertEqual(rows(report, 'package_permissions'), [])
        self.assertEqual(rows(report, 'permission_definitions'), [])

    def test_a_line_that_is_not_a_permission_line_is_skipped(self):
        body = ('Packages:\n  Package [com.example.x] (1):\n    appId=10001\n    install permissions:\n'
                '      not a permission line\n      android.permission.A: granted=true\n      android.permission.B: prot=signature\n')
        found = rows(scan_text(section_text('package', body)), 'package_permissions')
        self.assertEqual([r.permission for r in found], ['android.permission.A'])

    def test_rows_are_capped(self):
        body = 'Packages:\n  Package [com.example.x] (1):\n    appId=10001\n    install permissions:\n' + ''.join(
            '      p.%d: granted=true\n' % n for n in range(30))
        with mock.patch.object(reader, 'MAX_ROWS', 10):
            report = scan_text(section_text('package', body))
        self.assertEqual(len(rows(report, 'package_permissions')), 10)
        self.assertTrue([w for w in report.warnings if 'package_permissions' in w])


class AppOpsTests(unittest.TestCase):
    def test_uid_modes_are_grouped_by_mode(self):
        report = scan_text(fixture.build_report('a16'))
        uid_rows = [(m.uid, m.mode, m.op_count, m.ops, m.uid_state, m.capability) for m in rows(report, 'appop_modes') if m.scope == 'Uid']
        self.assertEqual(uid_rows[:2], [
            ('0', 'ignore', 3, 'COARSE_LOCATION, FINE_LOCATION, READ_SMS', 'cch', '--------'),
            ('0', 'foreground', 1, 'CAMERA', 'cch', '--------')])
        self.assertIn(('u10a100', 'ignore', 2, 'CAMERA, RECORD_AUDIO', 'bg', '-------T'), uid_rows)
        self.assertIn(('u0a100', 'allow', 1, 'WRITE_SMS', 'fg', 'LCMNFUAT'), uid_rows)
        # the lines of a block are counted once, whatever the grouping
        self.assertEqual(sum(m.op_count for m in rows(report, 'appop_modes') if m.scope == 'Uid' and m.uid == '0'), 4)

    def test_uid_rows_come_before_the_package_rows_of_the_same_uid(self):
        report = scan_text(fixture.build_report('a16'))
        lines = [(m.scope, m.line) for m in rows(report, 'appop_modes') if m.uid == 'u0a100']
        self.assertEqual(lines[0][0], 'Uid')
        self.assertTrue(all(scope == 'Package' for scope, _line in lines[1:]))

    def test_package_op_lines_and_switch_text(self):
        report = scan_text(fixture.build_report('a16'))
        chat = [(m.op_count, m.ops, m.mode, m.switch) for m in rows(report, 'appop_modes')
                if m.scope == 'Package' and m.uid == 'u0a100']
        self.assertEqual(chat[0], (1, 'FINE_LOCATION', 'allow', 'COARSE_LOCATION=allow'))
        self.assertIn((1, 'NO_ACCESS_OP', 'deny', ''), chat)                      # an op without access lines still has its mode row
        self.assertEqual(len(chat), 6)

    def test_watchers_restrictions_and_event_log_are_not_rows(self):
        report = scan_text(fixture.build_report('a16'))
        text = ' '.join(m.ops for m in rows(report, 'appop_modes'))
        self.assertNotIn('MONITOR_HIGH_POWER_LOCATION', text)
        self.assertFalse([m for m in rows(report, 'appop_modes') if m.uid in ('', None)])
        self.assertFalse([a for a in rows(report, 'appop_accesses') if a.line > 255])     # nothing after the uid blocks

    def test_android_10_layout(self):
        report = scan_text(fixture.build_report('a10', newline='\r\n'))
        modes = rows(report, 'appop_modes')
        self.assertEqual({m.capability for m in modes}, {''})
        chat = [m for m in modes if m.uid == 'u0a100' and m.scope == 'Uid']
        self.assertEqual([(m.mode, m.ops) for m in chat], [('foreground', 'COARSE_LOCATION'), ('allow', 'WRITE_SMS')])
        accesses = rows(report, 'appop_accesses')
        self.assertEqual({a.tag for a in accesses}, {''})
        self.assertEqual([a.kind for a in accesses if a.op == 'WAKE_LOCK'], ['Access', 'Running'])
        self.assertEqual([a.start_nesting for a in accesses if a.kind == 'Running'], ['2'])

    def test_access_fields(self):
        report = scan_text(fixture.build_report('a16', zone='UTC'))
        accesses = rows(report, 'appop_accesses')
        first = accesses[0]
        self.assertEqual((first.kind, first.uid, first.package, first.op, first.op_mode, first.tag),
                         ('Access', 'u0a100', 'com.example.user.chat', 'FINE_LOCATION', 'allow', 'null'))
        self.assertEqual((first.uid_state, first.op_flags, first.duration_text, first.duration_ms),
                         ('top', 's', '+1d2h3m4s5ms', 93784005))
        reject = accesses[1]
        self.assertEqual((reject.kind, reject.uid_state, reject.op_flags, reject.duration_text), ('Reject', 'bg', 's', ''))
        proxy = accesses[2]
        self.assertEqual((proxy.uid_state, proxy.op_flags, proxy.proxy_uid, proxy.proxy_package, proxy.proxy_tag),
                         ('fg', 'tpd', '10101', 'com.example.proxy', 'proxy_tag'))
        self.assertEqual(accesses[3].proxy_package, '')                              # upd without proxy text: nothing invented
        self.assertEqual(accesses[4].uid_state, 'fgsvcl')                              # the state is split at the first hyphen only

    def test_the_time_agrees_with_its_offset(self):
        report = scan_text(fixture.build_report('a16', zone='UTC'))
        now = datetime(2026, 11, 2, 10, 15, 12, 500000)
        checked = 0
        for access in rows(report, 'appop_accesses'):
            if access.time_text and not access.time_text.startswith('1970'):
                moment = datetime.strptime(access.time_text, '%Y-%m-%d %H:%M:%S.%f')
                self.assertEqual(moment - timedelta(milliseconds=permissions.duration_ms(access.offset)), now, access)
                checked += 1
        self.assertGreater(checked, 8)

    def test_running_rows(self):
        report = scan_text(fixture.build_report('a16'))
        running = [(a.op, a.tag, a.running_start, a.start_nesting, a.time_text, a.uid_state) for a in rows(report, 'appop_accesses')
                   if a.kind == 'Running']
        self.assertEqual(running, [('WAKE_LOCK', 'null', '+12s34ms', '2', '', ''), ('MONITOR_LOCATION', 'com.example.tag', '+2s2ms', '1', '', '')])

    def test_tags_follow_the_tag_lines(self):
        report = scan_text(fixture.build_report('a16'))
        monitor = [(a.kind, a.tag) for a in rows(report, 'appop_accesses') if a.op == 'MONITOR_LOCATION']
        self.assertEqual(monitor, [('Access', 'com.example.tag'), ('Running', 'com.example.tag'), ('Reject', 'second_tag')])

    def test_second_user_and_isolated_uid(self):
        report = scan_text(fixture.build_report('a15'))
        packages = {(m.uid, m.package) for m in rows(report, 'appop_modes') if m.scope == 'Package'}
        self.assertIn(('u11a100', 'com.example.user.chat'), packages)
        self.assertIn(('u0i1', 'com.example.isolated'), packages)
        self.assertIn(('u11s1000', 'com.example.system.settings'), packages)

    def test_the_uid_level_lines_of_one_uid_are_bounded(self):
        body = 'Current AppOps Service state:\n  Uid 5:\n    state=cch\n' + ''.join('      OP_%d: mode=ignore\n' % n for n in range(20))
        with mock.patch.object(permissions, 'MAX_UID_MODES', 12):
            report = scan_text(section_text('appops', body))
        self.assertEqual([(m.op_count, m.mode) for m in rows(report, 'appop_modes')], [(12, 'ignore')])
        self.assertTrue([w for w in report.warnings if w.startswith('appops: 8 lines')], report.warnings)

    def test_lines_that_cannot_be_read_are_reported(self):
        body = ('Current AppOps Service state:\n  Uid 1000:\n    state=pers\n    Package android:\n      VIBRATE (allow): \n'
                '        null=[\n          Access: [pers-s] 2026-11-02 10:15:00.000 (-12s)\n        ]\n'
                '      READ_SMS: mode=ignore\n    Package other:\n          Access: [pers-s] 2026-11-02 10:15:00.000 (-12s)\n')
        report = scan_text(section_text('appops', body))
        self.assertEqual(len(rows(report, 'appop_accesses')), 1)
        self.assertTrue([w for w in report.warnings if w.startswith('appops: 2 lines')], report.warnings)

    def test_an_access_line_with_an_unexpected_shape_is_counted_not_dropped_silently(self):
        body = ('Current AppOps Service state:\n  Uid 1000:\n    Package android:\n      VIBRATE (allow): \n'
                '          Access: unexpected shape\n          Access: [top-s]\n')
        report = scan_text(section_text('appops', body))
        found = rows(report, 'appop_accesses')
        self.assertEqual([(a.kind, a.uid_state, a.op_flags, a.time_text) for a in found], [('Access', 'top', 's', '')])
        self.assertTrue([w for w in report.warnings if w.startswith('appops: 1 lines')], report.warnings)

    def test_the_cut_marker_is_kept_on_the_section(self):
        report = scan_text(fixture.build_report('a16', cut=True))
        cut = [s for s in report.sections if s.kind == 'service' and s.timeout_ms]
        self.assertEqual({s.name for s in cut}, {'package', 'appops'})
        self.assertTrue(rows(report, 'appop_accesses'))


class RoleAndGrantTests(unittest.TestCase):
    def test_android_10_roles(self):
        report = scan_text(fixture.build_report('a10'))
        found = [(r.user, r.role, r.holders, r.fallback) for r in rows(report, 'role_holders')]
        self.assertEqual(found, [(0, 'android.app.role.CALL_SCREENING', '', ''), (0, 'android.app.role.SMS', 'com.example.sms', ''),
                                 (0, 'android.app.role.HOME', 'com.example.launcher', '')])

    def test_android_15_roles_for_two_users(self):
        report = scan_text(fixture.build_report('a15'))
        found = [(r.user, r.role.rsplit('.', 1)[-1], r.holders, r.fallback) for r in rows(report, 'role_holders')]
        self.assertEqual(found, [(0, 'SMS', 'com.example.sms', 'true'), (0, 'HOME', 'com.example.launcher', 'true'),
                                 (0, 'BROWSER', '', 'true'), (11, 'SMS', '', 'true'), (11, 'HOME', 'com.example.launcher2', 'true')])

    def test_no_role_section_gives_no_rows(self):
        report = scan_text(fixture.build_report('a16'))
        self.assertEqual(rows(report, 'role_holders'), [])
        self.assertNotIn('role', report.sections_seen)

    def test_a_holders_text_is_kept_whole(self):
        body = 'ROLE STATE (dumpsys role):\n{\n user_states=[\n {\n user_id=3\n roles=[\n {\n name=r.A\n holders=a.b, c.d\n }\n ]\n }\n ]\n}\n'
        found = rows(scan_text(section_text('role', body)), 'role_holders')
        self.assertEqual([(r.user, r.role, r.holders) for r in found], [(3, 'r.A', 'a.b, c.d')])

    def test_grants(self):
        report = scan_text(fixture.build_report('a16'))
        found = [(r.app_id, r.user, r.permission, r.granted, r.flags) for r in rows(report, 'permission_grants')]
        self.assertEqual(found, [
            (1000, 0, 'android.permission.EXAMPLE_SIGNATURE', 'true', 'PROTECTION_GRANTED'),
            (1000, 0, 'com.example.permission.OTHER', 'false', 'INSTALL_REVOKED'),
            (10100, 0, 'android.permission.CAMERA', 'false', 'USER_SENSITIVE_WHEN_GRANTED'),
            (10100, 0, 'android.permission.READ_CONTACTS', 'true', 'RUNTIME_GRANTED|USER_SET'),
            (10100, 0, 'android.permission.NO_FLAGS', 'true', ''),
            (10100, 10, 'android.permission.CAMERA', 'true', 'RUNTIME_GRANTED')])

    def test_the_dump_without_permissionmgr_gives_no_grants(self):
        self.assertEqual(rows(scan_text(fixture.build_report('a10')), 'permission_grants'), [])


class ArtifactTests(unittest.TestCase):
    FUNCTIONS = (artifacts.bugreport_package_permissions, artifacts.bugreport_permission_definitions,
                 artifacts.bugreport_appops_modes, artifacts.bugreport_appops_accesses, artifacts.bugreport_role_holders,
                 artifacts.bugreport_permission_grants)

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

    def test_every_function_has_an_artifact_entry_of_its_own_name(self):
        self.assertEqual({f.__name__ for f in self.FUNCTIONS}, set(artifacts.__artifacts_v2__))
        for key, entry in artifacts.__artifacts_v2__.items():
            self.assertTrue(entry['category'].startswith('Android Bug Report - '))
            self.assertEqual(entry['paths'], ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'), key)

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a15'))
        for function in self.FUNCTIONS:
            headers, rows_, source_path = self.run_artifact(function, path)
            self.assertTrue(rows_, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows_), function.__name__)
            self.assertEqual(source_path, str(path))

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows_, _source = self.run_artifact(function, path)
            self.assertEqual(rows_, [])
            self.assertTrue(headers)

    def test_a_text_without_these_sections_gives_no_rows_and_says_so(self):
        path = self.stage('Dump/dumpstate.txt', base_fixture.BANNER.format(report='2026-11-02 10:15:30'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            for function in self.FUNCTIONS:
                self.assertEqual(self.run_artifact(function, path)[1], [])
        for service in ('package', 'appops', 'role', 'permissionmgr'):
            self.assertEqual(len([m for m in messages if 'no %s service dump' % service in m]), 1, service)

    def test_access_rows_with_the_report_zone(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Asia/Kolkata'))
        _headers, found, _source = self.run_artifact(artifacts.bugreport_appops_accesses, path)
        first = found[0]
        self.assertEqual(first[1], '2026-10-30 06:15:10.500')
        self.assertEqual(first[0], utc(2026, 10, 30, 0, 45, 10, 500000))
        self.assertEqual((first[2], first[3], first[5], first[6]), ('', 'Access', 10100, 'com.example.user.chat'))
        running = [row for row in found if row[3] == 'Running'][0]
        self.assertEqual((running[0], running[1], running[18], running[19]), (None, '', '+12s34ms', '2'))

    def test_unset_time_and_missing_zone_are_explained(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='UTC'))
        _headers, found, _source = self.run_artifact(artifacts.bugreport_appops_accesses, path)
        unset = [row for row in found if row[1].startswith('1970')][0]
        self.assertEqual((unset[0], unset[2]), (None, reader.NOTE_UNSET))
        reader.clear_cache()
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone=''))
        _headers, found, _source = self.run_artifact(artifacts.bugreport_appops_accesses, path)
        timed = [row for row in found if row[1] and not row[1].startswith('1970')]
        self.assertTrue(timed)
        self.assertTrue(all(row[0] is None and row[2] == reader.NOTE_NO_ZONE for row in timed))

    def test_numeric_uid_and_modes_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        _headers, found, _source = self.run_artifact(artifacts.bugreport_appops_modes, path)
        by_uid = {row[1]: row[2] for row in found}
        self.assertEqual(by_uid, {'0': 0, 'u0a100': 10100, 'u10a100': 1010100, 'u0i1': None, 'u10s1000': 1001000})

    def test_a_dump_cut_by_the_platform_is_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_package_permissions, path)
            self.run_artifact(artifacts.bugreport_permission_definitions, path)
            self.run_artifact(artifacts.bugreport_appops_modes, path)
            self.run_artifact(artifacts.bugreport_appops_accesses, path)
        self.assertEqual(len([m for m in messages if 'package service dump was cut by a 10000 ms timeout' in m]), 1)
        self.assertEqual(len([m for m in messages if 'appops service dump was cut by a 10000 ms timeout' in m]), 1)

    def test_a_cut_dump_without_rows_is_still_reported(self):
        path = self.stage('Dump/dumpstate.txt', section_text('appops', 'Current AppOps Service state:\n', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.assertEqual(self.run_artifact(artifacts.bugreport_appops_accesses, path)[1], [])
        self.assertTrue([m for m in messages if 'appops service dump was cut' in m])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16', zone='Asia/Kolkata'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10', zone='America/Sao_Paulo'))
        alone = self.run_artifact(artifacts.bugreport_appops_accesses, first)[1]
        both = self.run_artifact(artifacts.bugreport_appops_accesses, first, second)[1]
        self.assertGreater(len(both), len(alone))
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})
        old = [row for row in both if row[-1] == 'Dump2/bugreport-example.txt'][0]
        local = datetime.strptime(old[1], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
        self.assertEqual(old[0], local + timedelta(hours=3))                  # Sao Paulo is UTC-3 on that date
        india = [row for row in both if row[-1] == 'Dump1/dumpstate.txt'][0]
        local = datetime.strptime(india[1], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
        self.assertEqual(india[0], local - timedelta(hours=5, minutes=30))

    def test_odd_bytes_do_not_stop_the_pass(self):
        odd = fixture.cases()['synthetic_odd_bytes'][0][1]
        path = self.stage('Dump/dumpstate.txt', odd)
        for function in self.FUNCTIONS:
            headers, rows_, _source = self.run_artifact(function, path)
            self.assertTrue(all(len(row) == len(headers) for row in rows_))
        found = self.run_artifact(artifacts.bugreport_package_permissions, path)[1]
        names = {row[5] for row in found}
        self.assertIn('android.permission.INTERNET ', names)            # the NUL is shown as a space
        self.assertIn('android.permission.CAM ERA', names)              # a lone carriage return too, and the line is kept

    def test_a_long_run_stays_in_one_pass(self):
        """The readers are fed from the single pass of the shared reader: the file is opened once for all the artifacts."""
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        with mock.patch.object(reader, '_open_binary', wraps=reader._open_binary) as opened:
            for function in self.FUNCTIONS:
                self.run_artifact(function, path)
        self.assertEqual(opened.call_count, 1)

    def test_the_section_index_names_the_artifacts_that_read_a_section(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a15'))
        rows_ = bugreportDevice.bugreport_sections.__wrapped__(Context(self.work, [path]))[1]
        by_name = {row[0]: row for row in rows_}
        self.assertEqual(by_name['appops'][7], 'App Ops Modes; App Ops Accesses')
        self.assertEqual(by_name['role'][7], 'Role Holders')
        self.assertEqual(by_name['permissionmgr'][7], 'Permission Manager Grants')

    def test_synthetic_cases_build(self):
        names = set(fixture.cases())
        self.assertEqual(names, {'synthetic_a16', 'synthetic_a15', 'synthetic_a10', 'synthetic_two_reports', 'synthetic_cut',
                                 'synthetic_no_zone', 'synthetic_empty', 'synthetic_not_a_report', 'synthetic_odd_bytes'})


if __name__ == '__main__':
    unittest.main()
