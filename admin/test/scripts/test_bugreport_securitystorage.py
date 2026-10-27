"""Android bug report text: device policy, lock settings, biometrics, trust, ADB, vendor services, storage, dbinfo and flags."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_securitystorage_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts import dumpstate_securitystorage as storage
from scripts.artifacts import bugreportSecurityStorage as art


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


def table(report, name):
    return getattr(report, name, [])


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


def service_text(name, body):
    """A minimal bug report text with one service dump."""
    return ('== dumpstate: 2026-06-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE %s:\n%s'
            '--------- 0.1s was the duration of dumpsys %s, ending at: 2026-06-01 10:00:01\n' % (name, body, name))


def zoned_service_text(name, body):
    """The base report (zone Europe/Paris, report time 2026-11-02 10:15:30) with one service dump."""
    plain = fixture.base.build_report('a16', zone='Europe/Paris', report='2026-11-02 10:15:30')
    closing = '== dumpstate: done (id 1)\n'
    return (plain[:plain.rindex(closing)] + '------ DUMPSYS HIGH (/system/bin/dumpsys) ------\n' + fixture.service(name, body)
            + "------ 0.900s was the duration of 'DUMPSYS HIGH' ------\n\n" + closing)


# invented values in the Android 13 Samsung layouts: an LSSLog indented by two spaces with no year, a Last changed key
A13_LOCK = ('Current lock settings service state:\n\nSP Enabled = true\n\nUser State:\n  User 7\n    SP Handle: 0\n'
            '    Last changed: 1970-01-01 00:00:00 (0)\n    SID: 0\n  \nLSSLog:\n  \n'
            '  ----------------- Start Summary state -----------------\n  <Summary not available>\n'
            '  ----------------- End Summary state -----------------\n  \n'
            '  ----------------- Start Example state -----------------\n'
            '  03-14 09:26:53.589 Example one -> Z9\n'
            '  03-14 09:26:53.600 Example two\n'
            '          <No example>\n'
            '          03-14 09:26:53.601 a detail line that starts with a time\n'
            '  03-14 09:26:53.700 Example three!\n'
            '  ----------------- End Example state -----------------\n  \n')
# invented values in the pid|tid layout of knoxguard_service
A13_GUARD = ('KG.example state: \n'
             '2026-03-12 07:31:44 : 4100|4100 : first example message: x? y, [a.b.c\n'
             '2026-03-12 07:31:45 : 4100|4122 : [ExampleTag] second example : k_v n: 9 p: f\n')


def command_text(title, body):
    return ('== dumpstate: 2026-06-01 10:00:00\n\n------ %s (some command) ------\n%s------ 0.1s was the duration of \'%s\' ------\n'
            % (title, body, title))


class RegistrationTests(unittest.TestCase):
    def test_every_reader_is_registered_once_and_listed(self):
        table_ = reader.readers_by_section()
        for cls in storage.SECURITY_STORAGE_READERS:
            self.assertIn(cls, table_[(cls.kind, cls.name)])
            self.assertEqual(table_[(cls.kind, cls.name)].count(cls), 1)
            self.assertIn((cls.kind, cls.name), reader.READ_BY)
        for key in storage.SECURITY_STORAGE_READ_BY:
            self.assertIn(key, table_)

    def test_the_read_by_text_names_artifacts_that_exist(self):
        names = {info['name'][len('Bug Report - '):] for info in art.__artifacts_v2__.values()}
        used = set()
        for text in storage.SECURITY_STORAGE_READ_BY.values():
            for name in text.split('; '):
                self.assertIn(name, names)
                used.add(name)
        self.assertEqual(used, names)              # every artifact is listed as reading some section

    def test_the_reader_tables_exist_only_when_a_row_was_read(self):
        report = scan_text('== dumpstate: 2026-06-01 10:00:00\n')
        for name in storage.TABLES:
            self.assertEqual(table(report, name), [])


class HelperTests(unittest.TestCase):
    def test_number_keeps_what_sqlite_can_hold(self):
        self.assertEqual(storage.number('12'), 12)
        self.assertEqual(storage.number('-5'), -5)
        self.assertEqual(storage.number('18446744073709551615'), '18446744073709551615')
        self.assertEqual(storage.number('9223372036854775807'), 9223372036854775807)
        self.assertEqual(storage.number('9223372036854775808'), '9223372036854775808')
        self.assertEqual(storage.number(''), '')
        self.assertEqual(storage.number('12x'), '12x')
        self.assertEqual(storage.number('\u0662'), '\u0662')           # not an ASCII digit

    def test_split_pair_takes_the_first_delimiter(self):
        self.assertEqual(storage.split_pair('a=b: c'), ('a', 'b: c'))
        self.assertEqual(storage.split_pair('a: b=c'), ('a', 'b=c'))
        self.assertEqual(storage.split_pair('plain'), ('plain', ''))

    def test_keyed_split_keeps_words_with_spaces(self):
        found = storage.keyed_split('mA=one two words mB=x mC=', r'm[A-Z]')
        self.assertEqual(dict(found), {'mA': 'one two words', 'mB': 'x', 'mC': ''})

    def test_parse_array(self):
        self.assertEqual(storage.parse_array('["a","b"]'), (['a', 'b'], True))
        self.assertEqual(storage.parse_array('[1,2,3]'), ([1, 2, 3], True))
        self.assertEqual(storage.parse_array('["a","b","c'), (['a', 'b'], False))
        self.assertEqual(storage.parse_array('[1,2,3'), ([1, 2], False))

    def test_nothing_is_masked(self):
        self.assertFalse(hasattr(storage, 'hide_token'))

    def test_times(self):
        report = scan_text(fixture.build_report('new', zone='Europe/Paris'))
        self.assertEqual(art.wall_time(report, '2026-06-09 18:42:05'), (utc(2026, 6, 9, 16, 42, 5), ''))
        self.assertEqual(art.wall_time(report, ''), (None, ''))
        self.assertEqual(art.wall_time(report, '1970-01-01 00:00:00'), (None, reader.NOTE_UNSET))
        self.assertEqual(art.wall_time(report, 'x'), (None, reader.NOTE_NOT_A_TIME))
        self.assertEqual(art.wall_time(report, '2026-03-29 02:30:00'), (None, reader.NOTE_NONEXISTENT))   # clocks set forward
        self.assertEqual(art.no_year_time(report, '10-29 11:02:14.250'), (utc(2026, 10, 29, 10, 2, 14, 250000), ''))
        self.assertEqual(art.no_year_time(report, 'garbage'), (None, art.NOTE_NO_YEAR))
        self.assertEqual(art.either_time(report, '2026-11-02 08:19:03.552')[0], utc(2026, 11, 2, 7, 19, 3, 552000))
        self.assertEqual(art.either_time(report, '11-02 08:19:03.552')[0], utc(2026, 11, 2, 7, 19, 3, 552000))
        self.assertEqual(art.either_time(report, ''), (None, ''))
        self.assertEqual(art.gmt_time('2026/10/04-03:07:02'), utc(2026, 10, 4, 3, 7, 2))
        self.assertEqual(art.gmt_time('2026/10/04-03:07:02(GMT)'), utc(2026, 10, 4, 3, 7, 2))
        self.assertIsNone(art.gmt_time('2026/13/04-03:07:02'))
        self.assertIsNone(art.gmt_time(''))
        self.assertEqual(art.iso_utc('2026-05-17T08:12:09.114233Z'), utc(2026, 5, 17, 8, 12, 9, 114233))
        self.assertEqual(art.iso_utc('1970-01-01T00:00:00Z'), utc(1970, 1, 1))
        self.assertIsNone(art.iso_utc('not a time'))
        no_zone = scan_text(fixture.build_report('new', zone=''))
        self.assertEqual(art.wall_time(no_zone, '2026-06-09 18:42:05'), (None, reader.NOTE_NO_ZONE))
        self.assertEqual(art.no_year_time(no_zone, '10-29 11:02:14.250'), (None, reader.NOTE_NO_ZONE))


class DevicePolicyTests(unittest.TestCase):
    def test_admins(self):
        report = scan_text(fixture.build_report('new'))
        admins = table(report, 'ss_dp_admins')
        self.assertEqual(len(admins), 2)
        first, second = admins[0], admins[1]
        self.assertEqual((first.user, first.component, first.package, first.uid, first.test_only),
                         (0, 'com.example.guard/.agent.GuardReceiver', 'com.example.guard', 5101, 'false'))
        self.assertEqual(first.policies, 'wipe-data, force-lock, disable-camera')
        self.assertEqual((first.password_quality, first.min_length, first.wipe_after, first.vpn_package),
                         ('0x0', 0, 5, 'null'))
        self.assertEqual(first.source_dir, '/system/priv-app/ExampleGuard/ExampleGuard.apk')
        self.assertEqual((second.user, second.uid, second.test_only, second.password_quality, second.keyguard_disabled),
                         (10, 1010123, 'true', '0x20000', '2'))
        self.assertEqual((second.vpn_package, second.vpn_lockdown, second.is_parent, second.common_criteria),
                         ('com.example.vpn', 'true', 'true', 'true'))
        self.assertEqual(second.source_dir, '')                       # this entry prints no application info
        self.assertEqual(first.package, 'com.example.guard')          # not the packageName printed inside the application info

    def test_state_rows(self):
        report = scan_text(fixture.build_report('new'))
        rows = {(row.group, row.user, row.name): row.value for row in table(report, 'ss_dp_state')}
        self.assertEqual(rows[('Profile Owner (User 10)', 10, 'package')], 'com.example.vault')
        self.assertEqual(rows[('Device admins state', 0, 'mUserSetupComplete')], 'true')
        self.assertEqual(rows[('Device admins state', 10, 'mAppsSuspended')], 'false')
        self.assertEqual(rows[('Admin policies size', 0, 'com.example.guard')], '77')
        self.assertEqual(rows[('Device policy cache', None, 'Password quality')], '{0=0, 10=131072}')
        self.assertEqual(rows[('Device state cache', None, 'Has PO / User 10')], 'true')
        self.assertEqual(rows[('Device policy manager', None, 'Encryption Status')], 'per-user')
        self.assertEqual(rows[('Personal apps suspension helper', None, 'Packages subject to suspension')], '2 apps')
        self.assertEqual(rows[('Immutable state', None, 'mHasFeature')], 'true')
        self.assertNotIn(('Personal apps suspension helper', None, '0'), rows)          # the package list is not read
        self.assertFalse([row for row in table(report, 'ss_dp_state') if row.name.startswith('DAS_DIED')])   # Constants

    def test_policies(self):
        report = scan_text(fixture.build_report('new'))
        policies = table(report, 'ss_dp_policies')
        self.assertEqual([(p.scope, p.user, p.key.split()[-1]) for p in policies],
                         [('Local', 0, 'userRestriction_no_factory_reset'), ('Global', None, 'exampleSetAllowMode'),
                          ('Global', None, 'exampleBlockAll')])
        self.assertEqual((policies[0].package, policies[0].mechanism, policies[0].resolved_value), ('', 'MostRestrictive', ''))
        self.assertEqual((policies[1].package, policies[1].authorities, policies[1].admin_value, policies[1].resolved_value),
                         ('com.example.guard', 'device_admin', 'IntegerPolicyValue { mValue= 2 }', 'IntegerPolicyValue { mValue= 2 }'))
        self.assertEqual(policies[2].mechanism, 'TopPriority')

    def test_old_layout_has_an_empty_admin_list(self):
        report = scan_text(fixture.build_report('old'))
        self.assertEqual(table(report, 'ss_dp_admins'), [])
        self.assertEqual(table(report, 'ss_dp_policies'), [])
        rows = {(row.group, row.name): row.value for row in table(report, 'ss_dp_state')}
        self.assertEqual(rows[('Device policy cache', 'Screen capture disabled')], '{0=false}')
        self.assertEqual(rows[('Device admins state', 'mPasswordOwner')], '-1')

    def test_two_admins_for_one_policy_and_a_device_owner(self):
        text = service_text('device_policy', (
            'Current Device Policy Manager state:\n  Device Owner: \n    admin=ComponentInfo{com.example.a/com.example.a.R}\n'
            '    package=com.example.a\n  Global Policies: \n    DefaultPolicyKey k\n      Per-admin Policy:\n        ' + fixture.ENFORCING + '\n'
            '          IntegerPolicyValue { mValue= 1 }\n        EnforcingAdmin { mPackageName= com.example.b, mAuthorities= [role] }\n'
            '          IntegerPolicyValue { mValue= 2 }\n      Resolved Policy (MostRecent):\n        IntegerPolicyValue { mValue= 2 }\n'))
        report = scan_text(text)
        self.assertEqual([(p.package, p.admin_value) for p in table(report, 'ss_dp_policies')],
                         [('com.example.guard', 'IntegerPolicyValue { mValue= 1 }'), ('com.example.b', 'IntegerPolicyValue { mValue= 2 }')])
        self.assertEqual({row.resolved_value for row in table(report, 'ss_dp_policies')}, {'IntegerPolicyValue { mValue= 2 }'})
        self.assertIn(('Device Owner', None, 'package', 'com.example.a'),
                      [(r.group, r.user, r.name, r.value) for r in table(report, 'ss_dp_state')])


class LockSettingsTests(unittest.TestCase):
    def test_users_new_layout(self):
        report = scan_text(fixture.build_report('new'))
        users = table(report, 'ss_lock_users')
        self.assertEqual([user.user for user in users], [0, 10])
        first, second = users[0], users[1]
        self.assertEqual((first.protector_id, first.changed_text, first.previous_protector, first.sid),
                         ('0123456789abcdef', '2026-06-09 18:42:05', 'fedcba9876543210', '1111222233334444'))
        self.assertEqual((first.credential_type, first.separate_challenge, first.metrics, first.failed_attempts, first.quality),
                         ('PIN', 'true', 'known', '0', '0'))
        self.assertIn('1970-01-01 00:00:00', first.backup_protector)
        self.assertEqual(first.si_checker, 'aaaaaaaaaaaaaaaa (For 0123456789abcdef)')
        self.assertEqual((second.credential_type, second.failed_attempts, second.backup_protector), ('PASSWORD', '', ''))
        self.assertEqual(second.other, 'Extra Field: odd value')       # a key the reader does not know

    def test_users_old_layout(self):
        users = table(scan_text(fixture.build_report('old')), 'ss_lock_users')
        self.assertEqual(len(users), 1)
        self.assertEqual((users[0].sp_handle, users[0].sid, users[0].protector_id, users[0].changed_text),
                         ('1234567890abcdef', 'fedcba0987654321', '', ''))

    def test_files_state_and_log(self):
        report = scan_text(fixture.build_report('new'))
        files = table(report, 'ss_lock_files')
        self.assertEqual([(f.location, f.size, f.name) for f in files],
                         [('User 0', 91, '0000000000000000.e0.bku'), ('User 0', 57, '0000000000000000.handle'),
                          ('User 0', 193, '0123456789abcdef.spblob'), ('Backup', 57, '0000000000000000.handle')])
        self.assertEqual(files[0].directory, '/data/system_de/0/spblob')
        self.assertEqual(files[0].mtime_text, '2026-06-09 18:42:07')
        state = {(row.group, row.user, row.name): row.value for row in table(report, 'ss_lock_state')}
        self.assertEqual(state[('Service', None, 'DO Enabled')], 'false')
        self.assertEqual(state[('Service', None, 'ThirdPartyAppsStarted')], 'true')
        self.assertEqual(state[('StrongAuth: PrimaryAuthFlags state', 10, 'primaryAuthFlags')], '5')
        self.assertEqual(state[('StrongAuth: NonStrongBiometricAllowed state', 0, 'allowed')], 'true')
        self.assertEqual(state[('StrongAuth: strong auth timeout state', None, 'strong biometric timeout')], '2026/11/05 06:01:36.858')
        self.assertEqual(state[('RebootEscrow', None, 'mRebootEscrowWanted')], 'false')
        self.assertEqual(state[('RebootEscrow', None, 'mPendingRebootEscrowKey is not set')], '')
        self.assertEqual(sorted(row.value for row in table(report, 'ss_lock_state') if row.group == 'Keys in namespace'),
                         ['synthetic_password_0123456789abcdef', 'synthetic_password_fedcba9876543210'])

    def test_log_entries(self):
        log = table(scan_text(fixture.build_report('new')), 'ss_lock_log')
        self.assertEqual([(entry.state, entry.time_text) for entry in log][:3],
                         [('Enroll', '2026-02-03 08:14:22.311'), ('Enroll', '2026-06-09 18:42:05.127'),
                          ('Enroll', '2026-06-09 18:42:05.481')])
        self.assertEqual(log[1].frames, 3)                 # two frames and the bottom of call stack marker
        self.assertEqual(log[1].detail, '')
        self.assertIn('Enroll Success(0)', log[2].detail)
        self.assertEqual(log[3].message, 'User 0 [/data/system_de/0/spblob]:')
        self.assertIn('0123456789abcdef.spblob', log[3].detail)       # the listing lines follow their entry
        self.assertEqual([entry.state for entry in log if entry.state == 'Verify'], ['Verify'] * 4)
        self.assertEqual(log[-1].message, 'User 0 PIN Fail on [com.example.systemui](2/5)]')
        self.assertEqual(len(log), 8)

    def test_android_13_log_without_a_year_and_indented(self):
        log = table(scan_text(service_text('lock_settings', A13_LOCK)), 'ss_lock_log')
        self.assertEqual([(entry.state, entry.time_text, entry.message) for entry in log],
                         [('Example', '03-14 09:26:53.589', 'Example one -> Z9'), ('Example', '03-14 09:26:53.600', 'Example two'),
                          ('Example', '03-14 09:26:53.700', 'Example three!')])
        self.assertEqual(log[1].detail, '<No example> | 03-14 09:26:53.601 a detail line that starts with a time')

    def test_android_13_last_changed(self):
        users = table(scan_text(service_text('lock_settings', A13_LOCK)), 'ss_lock_users')
        self.assertEqual([(user.user, user.changed_text, user.previous_protector, user.other) for user in users],
                         [(7, '1970-01-01 00:00:00 (0)', '', '')])

    def test_old_layout_has_no_log_files_or_strong_auth(self):
        report = scan_text(fixture.build_report('old'))
        self.assertEqual(table(report, 'ss_lock_log'), [])
        self.assertEqual(table(report, 'ss_lock_files'), [])
        self.assertEqual([(r.group, r.name, r.value) for r in table(report, 'ss_lock_state')], [('Service', 'SP Enabled', 'false')])


class BiometricTests(unittest.TestCase):
    def test_statistics(self):
        report = scan_text(fixture.build_report('new'))
        stats = table(report, 'ss_bio_stats')
        self.assertEqual([(s.service, s.sensor_id, s.provider, s.print_id) for s in stats],
                         [('fingerprint', 0, 'FingerprintProvider', 0), ('fingerprint', 0, 'FingerprintProvider', 10),
                          ('face', 1, 'FaceProvider', 0), ('face', 1, 'FaceProvider', 10)])
        self.assertEqual(stats[0].provider_service, 'FingerprintProvider/default')
        self.assertEqual(dict(stats[0].counters)['count'], 2)
        self.assertEqual(dict(stats[0].counters)['accept'], 3)
        self.assertEqual(stats[0].hal_deaths, 1)
        self.assertEqual(dict(stats[1].counters)['other'], 'future=7')
        self.assertEqual(dict(stats[2].counters)['count'], 0)
        self.assertEqual(stats[2].hal_deaths, 0)

    def test_statistics_old_layout(self):
        stats = table(scan_text(fixture.build_report('old')), 'ss_bio_stats')
        self.assertEqual([(s.service, s.sensor_id, s.provider, s.provider_service) for s in stats],
                         [('fingerprint', None, '', 'Fingerprint Manager'), ('face', None, '', 'Face Manager')])
        self.assertIn('lockoutCrypto', stats[0].counters)

    def test_a_statistics_line_that_is_not_json_is_warned_about(self):
        report = scan_text(service_text('fingerprint', '{"service":"x","prints":[{"id":0,\n{"service":"y","prints":"no"}\n'
                                                       '{"service":"z","prints":[{"id":3,"count":1}]}\n'))
        self.assertEqual([s.print_id for s in table(report, 'ss_bio_stats')], [3])
        self.assertTrue([w for w in report.warnings if 'could not be read' in w])

    def test_sensors(self):
        sensors = table(scan_text(fixture.build_report('new')), 'ss_bio_sensors')
        self.assertEqual([(s.sensor_id, s.oem_strength, s.modality, s.state, s.cookie) for s in sensors],
                         [(0, 15, 2, 0, 0), (1, 255, 8, 4, 770011)])
        self.assertEqual(table(scan_text(fixture.build_report('old')), 'ss_bio_sensors'), [])

    def test_events(self):
        events = [e for e in table(scan_text(fixture.build_report('new')), 'ss_bio_events') if e.service == 'fingerprint']
        self.assertEqual([e.sequence for e in events], [0, 1, 2, 3, 4, 5])
        self.assertEqual((events[0].event, events[0].user, events[0].request_id, events[0].strength, events[0].sensor_id),
                         ('resetLockoutFor', 0, -1, 15, None))
        self.assertEqual((events[1].event, events[1].sensor_id, events[1].request_id), ('authStartedFor', 0, 1))
        self.assertEqual((events[2].event, events[2].user), ('internal: onAuthSessionStarted', 0))
        self.assertEqual((events[3].event, events[3].successful), ('authEndedFor', 'false'))
        self.assertEqual(events[5].successful, 'true')
        self.assertEqual(events[3].text, 'authEndedFor(userId=0 ,biometricStrength=15, sensorId=0, requestId=1, wasSuccessful=false)')
        both = table(scan_text(fixture.build_report('new')), 'ss_bio_events')
        self.assertEqual({e.service for e in both}, {'fingerprint', 'face'})       # the same log under both services
        self.assertEqual(len(both), 12)
        self.assertEqual(table(scan_text(fixture.build_report('old')), 'ss_bio_events'), [])


class TrustTests(unittest.TestCase):
    def test_new_layout(self):
        report = scan_text(fixture.build_report('new'))
        agents = table(report, 'ss_trust_agents')
        self.assertEqual([(a.user_id, a.agent, a.bound, a.connected, a.managing, a.agent_trusted) for a in agents],
                         [(0, 'com.example.gms/.ExampleTrustAgent', '1', '1', '0', '0'),
                          (0, 'com.example.gms/.LockingAgent', '1', '0', '1', '1'), (10, '', '', '', '', '')])
        self.assertEqual((agents[0].user_name, agents[0].flags, agents[0].qualifiers, agents[0].trust_state, agents[0].trusted,
                          agents[0].device_locked, agents[0].strong_auth), ('Example Owner', '0x4a11', 'current', 'UNTRUSTED', '', '0', '0x0'))
        self.assertEqual((agents[2].qualifiers, agents[2].device_locked, agents[2].note),
                         ('profile with separate challenge', '1', 'Trust agents disabled because switching to this user is not possible.'))
        events = table(report, 'ss_trust_events')
        self.assertEqual([(e.user_id, e.sequence, e.time_text, e.event, e.detail) for e in events],
                         [(0, 0, '10-29 11:02:14.250', 'AgentConnected', 'agent=ExampleTrustAgent'),
                          (0, 1, '10-29 11:02:13.904', 'AgentConnected', 'agent=LockingAgent')])

    def test_old_layout_and_invisible_characters(self):
        report = scan_text(fixture.build_report('old'))
        agents = table(report, 'ss_trust_agents')
        self.assertEqual(len(agents), 1)
        self.assertEqual((agents[0].user_name, agents[0].trusted, agents[0].trust_state), ('Example \u200fOwner', '0', ''))
        self.assertEqual(len(table(report, 'ss_trust_events')), 1)

    def test_a_user_name_with_quotes_and_colons(self):
        report = scan_text(service_text('trust', 'Trust manager state:\n User "A \\"b\\": c" (id=3, flags=0x1) (current): trusted=1\n'))
        self.assertEqual([(a.user_id, a.user_name, a.trusted) for a in table(report, 'ss_trust_agents')],
                         [(3, 'A \\"b\\": c', '1')])


class AdbAndVendorTests(unittest.TestCase):
    def test_adb_state(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_adb')
        self.assertEqual([(r.path, r.value) for r in rows], [('debugging_manager.connected_to_adb', 'false')])

    def test_deeper_nesting(self):
        text = service_text('adb', 'ADB MANAGER STATE (dumpsys adb):\n{\n  debugging_manager={\n    connected_to_adb=true\n'
                                   '    user_keys={\n      count=2\n    }\n    trailing=1\n  }\n  top=x,\n}\n')
        self.assertEqual([(r.path, r.value) for r in table(scan_text(text), 'ss_adb')],
                         [('debugging_manager.connected_to_adb', 'true'), ('debugging_manager.user_keys.count', '2'),
                          ('debugging_manager.trailing', '1'), ('top', 'x')])

    def test_guard_log_and_token(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_knox_log')
        self.assertEqual([r.kind for r in rows], ['State', 'State', 'State', 'Log', 'Log', 'Log', 'Log'])
        self.assertEqual((rows[0].message, rows[2].message), ('ADB blocked : false', 'SF counter : 1'))
        self.assertEqual((rows[3].time_text, rows[3].tag, rows[3].message), ('2026-03-12 07:31:44', 'action', 'android.intent.action.TIMEZONE_CHANGED'))
        self.assertEqual(rows[4].tag, 'android.intent.action.BOOT_COMPLETED')
        self.assertEqual(rows[5].message, 'Refreshed token: AbCd1234')
        self.assertEqual(rows[6].time_text, '1970-01-01 00:00:00')
        self.assertEqual(table(scan_text(fixture.build_report('old')), 'ss_knox_log'), [])

    def test_guard_log_with_process_and_thread_ids(self):
        rows = table(scan_text(service_text('knoxguard_service', A13_GUARD)), 'ss_knox_log')
        self.assertEqual([(r.kind, r.time_text, r.tag, r.message) for r in rows],
                         [('Log', '2026-03-12 07:31:44', '', '4100|4100 : first example message: x? y, [a.b.c'),
                          ('Log', '2026-03-12 07:31:45', 'ExampleTag', '4100|4122 : [ExampleTag] second example : k_v n: 9 p: f')])

    def test_custom_state(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_knox_custom')
        self.assertEqual([(r.manager, r.name, r.value) for r in rows],
                         [('ProKioskManager', '', 'false'), ('ProKioskManager', 'ExitUI', 'null:null'),
                          ('SystemManager', 'BatteryLevelColour', 'null'), ('SystemManager', 'InfraredState', 'false'),
                          ('SystemManager', 'LockScreenShortcuts', 'com.example.dialer/.Dial, com.example.camera/.Cam'),
                          ('SettingsManager', 'SettingsHiddenState', '0x00000000')])
        self.assertEqual(rows[2].text, 'SystemManager:BatteryLevelColour is null')


class StorageTests(unittest.TestCase):
    def test_df(self):
        report = scan_text(fixture.build_report('new'))
        rows = table(report, 'ss_df')
        self.assertEqual([r.mount for r in rows], ['/', '/dev', '/data', '/apex/com.example.tzdata@300100200', '/overflow'])
        self.assertEqual((rows[0].blocks, rows[0].used, rows[0].available, rows[0].use_percent), (3120400, 3120400, 0, '100%'))
        self.assertEqual(rows[4].blocks, '99999999999999999999')        # larger than SQLite holds: printed text
        self.assertTrue([w for w in report.warnings if 'six columns' in w])

    def test_inodes_are_kept_as_printed(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_df_inodes')
        self.assertEqual((rows[0].inodes, rows[0].free, rows[0].mount), ('18446744073709551615', '18446744073709546495', '/'))
        self.assertEqual(rows[2].inodes, '3815424')
        self.assertEqual(table(scan_text(fixture.build_report('old')), 'ss_df_inodes'), [])

    def test_mount_points(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_mounts')
        self.assertEqual([(r.device, r.mount_point, r.fs_type) for r in rows],
                         [('/dev/block/dm-8', '/', 'erofs'), ('tmpfs', '/dev', 'tmpfs'), ('/dev/block/sdc30', '/metadata', 'ext4')])
        self.assertIn('nr_inodes=375050', rows[1].options)

    def test_volumes(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_volumes')
        self.assertEqual([(r.kind, r.volume_id) for r in rows],
                         [('Storage volume', 'emulated;0'), ('Volume', 'emulated;0'), ('Volume', 'private')])
        first, second, third = rows[0], rows[1], rows[2]
        self.assertEqual((first.state, first.path, first.description, first.primary, first.removable, first.emulated),
                         ('mounted', '/storage/emulated/0', 'Internal shared storage', 'true', 'false', 'true'))
        self.assertIn('mSubSystem=fuse', first.other)
        self.assertEqual((second.state, second.path, second.internal_path, second.mount_flags, second.mount_user, second.volume_type),
                         ('MOUNTED', '/storage/emulated', '/data/media', 'PRIMARY|VISIBLE_FOR_WRITE', '0', 'EMULATED'))
        self.assertEqual((third.fs_type, third.fs_uuid, third.fs_label, third.volume_type), ('ext4', '0000-ffff', 'example', 'PRIVATE'))

    def test_a_disk_entry(self):
        text = service_text('mount', 'Disks:\n  DiskInfo{disk:179,64}:\n    flags=SD size=1000 label=example\n\nVolumes:\n')
        rows = table(scan_text(text), 'ss_volumes')
        self.assertEqual([(r.kind, r.volume_id) for r in rows], [('Disk', 'disk:179,64')])
        self.assertEqual(rows[0].other, 'flags=SD; size=1000; label=example')

    def test_vold_log(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_vold')
        self.assertEqual(len(rows), 5)
        self.assertEqual((rows[0].time_text, rows[0].pid, rows[0].tid, rows[0].component, rows[0].message, rows[0].buffer),
                         ('2026/10/04-03:07:07(GMT)', 412, 9021, 'vold', 'Starting trim of /mnt/vendor/example', 'BUF#0'))
        self.assertEqual((rows[3].time_text, rows[3].component, rows[3].message), ('2026/10/04-03:12:12(UTC)', 'vold', 'idle maintenance completed'))
        self.assertEqual((rows[4].time_text, rows[4].message), ('', 'continuation without a time'))

    def test_storage_io(self):
        report = scan_text(fixture.build_report('new'))
        rows = table(report, 'ss_storage_io')
        self.assertEqual([r.name for r in rows], ['com.example.chat', 'shared:android.uid.example', 'com.example.huge'])
        self.assertEqual(rows[0].values, (9120344, 412008, 51200000, 1310720, 880001200, 44001300, 7700000000,
                                          91000000, 12, 3400))
        self.assertEqual(rows[2].values[0], '99999999999999999999')
        history = [(r.item, r.value) for r in table(report, 'ss_disk_items') if r.section == 'storaged -u -p']
        self.assertEqual(history, [('I/O perf history (KB/s, most recent first): last 24 hours', '4410 9120 12050'),
                                   ('I/O perf history (KB/s, most recent first): last 7 days', '8800 9100 9350')])

    def test_disk_statistics_and_package_sizes(self):
        report = scan_text(fixture.build_report('new'))
        items = {(r.section, r.item): r.value for r in table(report, 'ss_disk_items')}
        self.assertEqual(items[('diskstats', 'Latency')], '1ms [512B Data Write]')
        self.assertEqual(items[('diskstats', 'Recent Disk Write Speed (kB/s)')], '20450')
        self.assertEqual(items[('diskstats', 'Data-Free')], '18010020K / 61000700K total = 29% free')
        self.assertEqual(items[('diskstats', 'App Size')], '12100200000')
        self.assertEqual(items[('mount', 'Internal storage (null) total size')], '68719476736 (65536 MiB)')
        self.assertEqual(items[('mount', 'CE unlocked users')], '[0]')
        self.assertNotIn(('diskstats', 'Package Names'), items)
        sizes = table(report, 'ss_package_sizes')
        self.assertEqual([(s.index, s.package, s.app_size, s.data_size, s.cache_size) for s in sizes][1:3],
                         [(1, 'com.example.pkg01', 120832, 18432, 8192), (2, 'com.example.pkg02', 9400320, 250880, 20480)])
        self.assertEqual(len(sizes), 4)

    def test_lists_of_different_lengths_use_the_shortest_and_say_so(self):
        report = scan_text(fixture.build_report('old'))
        self.assertEqual(len(table(report, 'ss_package_sizes')), 2)
        self.assertTrue([w for w in report.warnings if 'different lengths' in w])

    def test_a_list_cut_by_the_line_limit_gives_its_complete_items(self):
        names = ','.join('"com.example.pkg%05d"' % number for number in range(5000))          # 130,000 characters
        numbers_ = ','.join(str(number) for number in range(5000))
        body = 'Package Names: [%s]\nApp Sizes: [%s]\n' % (names, numbers_)
        report = scan_text(service_text('diskstats', body))
        sizes = table(report, 'ss_package_sizes')
        self.assertGreater(len(sizes), 1000)
        self.assertLess(len(sizes), 5000)
        self.assertEqual(sizes[0].package, 'com.example.pkg00000')
        self.assertTrue([w for w in report.warnings if 'could not be read in full' in w])
        self.assertTrue([w for w in report.warnings if 'different lengths' in w])


class DbInfoTests(unittest.TestCase):
    def test_pools(self):
        report = scan_text(fixture.build_report('new'))
        pools = table(report, 'ss_db_pools')
        self.assertEqual(len(pools), 2)
        first, second = pools[0], pools[1]
        self.assertEqual((first.pid, first.process, first.open, first.max_connections, first.total_time, first.total_statements,
                          first.average_time, first.read_only, first.secure, first.wal, first.connections, first.operations),
                         (4321, 'com.example.settings', 'true', 4, 31, 84, 0, 'false', 'false', 'yes', 2, 8))
        self.assertTrue(first.path.endswith('/example-db-v1'))
        self.assertIn('journalMode=WAL', first.configuration)
        self.assertEqual(first.other, '')
        self.assertEqual((second.pid, second.process, second.open, second.read_only, second.total_statements, second.wal, second.other),
                         (4400, 'com.example.second', 'false', 'true', '', '', 'Lookaside config: sz=0 cnt=0'))

    def test_files(self):
        files = table(scan_text(fixture.build_report('new')), 'ss_db_files')
        self.assertEqual([(f.pid, f.name, f.size) for f in files],
                         [(4321, 'example-db-v1', 8192), (4321, 'example-db-v1-wal', 524288), (4321, 'odd name.db', 0)])
        self.assertEqual(files[0].directory, '/data/user_de/0/com.example.settings/databases')
        self.assertEqual((files[0].ctime, files[0].mtime, files[0].atime),
                         ('2026-05-17T08:12:09.114233Z', '2026-05-17T08:12:09.114233Z', '2026-05-17T08:12:09.109233Z'))
        self.assertEqual(files[2].atime, '1970-01-01T00:00:00Z')

    def test_operations(self):
        ops = table(scan_text(fixture.build_report('new')), 'ss_db_ops')
        self.assertEqual(len(ops), 8)
        self.assertEqual([op.index for op in ops[:6]], [0, 1, 2, 3, 4, 5])
        first = ops[0]
        self.assertEqual((first.pid, first.connection, first.listing, first.time_text, first.operation, first.took_ms, first.status),
                         (4321, 0, 'Most recently executed operations', '11-01 14:22:31.250', 'execute', 1, 'succeeded'))
        self.assertEqual(first.sql, 'CREATE TEMP TABLE IF NOT EXISTS example_log (id INTEGER PRIMARY KEY)')
        self.assertEqual(first.sql_length, len(first.sql))
        self.assertTrue(first.details.startswith('path=/data/user_de/'))
        self.assertEqual(ops[1].sql, "SELECT 'a, b' FROM t WHERE x = 1")
        self.assertTrue(ops[1].details.endswith('filledRows=3'))
        self.assertEqual((ops[2].operation, ops[2].sql, ops[2].sql_length), ('open', '', 0))
        self.assertEqual((ops[3].operation, ops[3].sql, ops[3].details.endswith('result=2')), ('TRANSACTION-IMMEDIATE', '', True))
        self.assertEqual((ops[4].status, ops[4].took_ms), ('failed', 3))
        slow = [op for op in ops if op.listing == 'Operations exceeding 2000ms']
        self.assertEqual([(op.operation, op.took_ms) for op in slow], [('TRANSACTION-EXCLUSIVE', 2310)])
        self.assertEqual(ops[6].connection, 0)
        self.assertEqual(ops[7].connection, 1)

    def test_old_layout_full_dates(self):
        report = scan_text(fixture.build_report('old'))
        pool = table(report, 'ss_db_pools')[0]
        self.assertEqual((pool.total_time, pool.total_statements, pool.process), (1420, '', 'com.example.settings'))
        ops = table(report, 'ss_db_ops')
        self.assertEqual([op.time_text for op in ops], ['2026-11-02 08:19:03.552', '2026-11-02 08:19:02.904'])
        self.assertEqual(len(table(report, 'ss_db_files')), 1)

    def test_sql_with_quotes_and_the_path_marker_inside(self):
        body = ('** Database info for pid 1 [p] **\nConnection pool for /d/x.db:\n  Open: true\n  Available primary connection:\n'
                '    Connection #0:\n      Most recently executed operations:\n'
                '        0: [11-01 14:22:31.250] [Pid:(1)]execute took 1ms - succeeded, sql="SELECT \\"a\\", path=\\"b\\" FROM t", path=/d/x.db\n')
        ops = table(scan_text(service_text('dbinfo', body)), 'ss_db_ops')
        self.assertEqual(ops[0].sql, 'SELECT \\"a\\", path=\\"b\\" FROM t')
        self.assertEqual(ops[0].details, 'path=/d/x.db')

    def test_a_long_statement_is_cut_and_its_length_kept(self):
        body = ('** Database info for pid 1 [p] **\nConnection pool for /d/x.db:\n  Available primary connection:\n    Connection #0:\n'
                '      Most recently executed operations:\n        0: [11-01 14:22:31.250] execute took 1ms - succeeded, sql="'
                + 'x' * 5000 + '", path=/d/x.db\n')
        op = table(scan_text(service_text('dbinfo', body)), 'ss_db_ops')[0]
        self.assertEqual((len(op.sql), op.sql_length), (storage.SQL_CAP, 5000))
        self.assertEqual(op.pid, 1)


class FlagTests(unittest.TestCase):
    def test_device_config(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_device_config')
        self.assertEqual([(r.namespace, r.flag, r.value) for r in rows],
                         [('accessibility', 'com.example.flags.example_flag_one', 'true'), ('adservices', 'example_period_ms', '3600000'),
                          ('test', 'empty_value', ''), ('messaging', 'example_app_list', 'com.example.one, com.example.two, com.example.three')])
        self.assertEqual(table(scan_text(fixture.build_report('old')), 'ss_device_config'), [])

    def test_a_long_device_config_value_is_cut(self):
        body = 'DeviceConfig flags:\nns/flag=' + 'v' * 3000 + '\nns/next=1\n'
        rows = table(scan_text(service_text('device_config', body)), 'ss_device_config')
        self.assertEqual((len(rows[0].value), rows[1].value), (1000, '1'))

    def test_platform_compat(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_compat')
        self.assertEqual([(r.change_id, r.name, r.since_sdk, r.after_sdk, r.disabled, r.logging_only, r.overridable, r.other) for r in rows],
                         [(100200301, 'EXAMPLE_DOWNSCALE_65', '', '', 'yes', '', 'yes', ''),
                          (100200302, 'EXAMPLE_FEATURE', 35, '', '', '', '', ''),
                          (111, 'EXAMPLE_LOG_ONLY', '', '', '', 'yes', '', ''),
                          (222, 'EXAMPLE_AFTER', '', 30, '', '', '', 'futureFlag')])

    def test_release_flags(self):
        report = scan_text(fixture.build_report('new'))
        flags = table(report, 'ss_release_flags')
        self.assertEqual([(f.partition, f.name) for f in flags],
                         [('system', 'RELEASE_EXAMPLE_ONE'), ('system', 'RELEASE_EXAMPLE_TWO'), ('system', 'RELEASE_EXAMPLE_THREE'),
                          ('product', 'RELEASE_EXAMPLE_TWO')])
        one, two, three, product = flags[0], flags[1], flags[2], flags[3]
        self.assertEqual((one.declared_type, one.declared_value, one.value_type, one.value, one.workflow, one.containers),
                         ('UnspecifiedValue', 'false', 'BoolValue', 'true', 1, 'product, system'))
        self.assertEqual((two.declared_value, two.value, two.workflow), ('READ_WRITE', 'READ_ONLY', 3))
        self.assertEqual((three.value_type, three.value, three.containers), ('', '', ''))
        self.assertEqual(product.namespace, 'example_team')
        self.assertTrue([w for w in report.warnings if 'VENDOR BUILD-TIME RELEASE FLAGS' in w and 'not complete JSON' in w])

    def test_release_flags_that_are_not_a_list_are_ignored(self):
        for text in ('[]', '{"flags": 5}', '{"flags": [1, {"a": 1}, {"flag_declaration": 3}]}', '{}'):
            report = scan_text(command_text('SYSTEM BUILD-TIME RELEASE FLAGS', text + '\n'))
            self.assertEqual(table(report, 'ss_release_flags'), [], text)

    def test_sdk_extensions(self):
        rows = table(scan_text(fixture.build_report('new')), 'ss_sdk')
        self.assertEqual([(r.group, r.name, r.value) for r in rows][:4],
                         [('system properties', 'build.version.extensions.ad_services', '23'),
                          ('system properties', 'build.version.extensions.c', '<not set>'),
                          ('system properties', 'ro.build.version.sdk', '36'), ('apex module versions', 'AD_SERVICES', '23')])
        self.assertEqual(rows[-1].group, 'last 3 version requirements')
        self.assertEqual((rows[-2].name, rows[-2].value), ('23', 'ART AD_SERVICES'))


class BoundTests(unittest.TestCase):
    def test_rows_are_bounded_and_the_cap_is_reported(self):
        body = 'DeviceConfig flags:\n' + ''.join('ns/flag%d=1\n' % number for number in range(10))
        with mock.patch.object(reader, 'MAX_ROWS', 4):
            report = scan_text(service_text('device_config', body))
        self.assertEqual(len(table(report, 'ss_device_config')), 4)
        self.assertTrue([w for w in report.warnings if 'ss_device_config' in w and 'more than 4 rows' in w])

    def test_a_section_without_its_end_marker_is_still_read(self):
        text = '== dumpstate: 2026-06-01 10:00:00\n\nDUMP OF SERVICE adb:\nADB MANAGER STATE (dumpsys adb):\n{\n  a={\n    b=1\n  }\n}\n'
        self.assertEqual([r.path for r in table(scan_text(text), 'ss_adb')], ['a.b'])

    def test_crlf_text(self):
        report = scan_text(fixture.build_report('new', newline='\r\n'))
        self.assertEqual(len(table(report, 'ss_dp_admins')), 2)
        self.assertEqual(len(table(report, 'ss_db_ops')), 8)
        self.assertEqual(table(report, 'ss_lock_users')[0].credential_type, 'PIN')

    def test_damaged_text_does_not_raise(self):
        text = fixture.build_report('new').encode('utf-8')
        damaged = bytes(bytearray(text[:40000] + bytes(range(256)) * 20 + text[40000:]))
        scan_text(damaged)
        scan_text(fixture.build_report('new').replace('User 0', 'User \u00b2'))
        scan_text(fixture.build_report('new').replace('(id=0,', '(id=\u00b2,'))
        scan_text(fixture.build_report('new').replace('took 1ms', 'took \u00b2ms'))


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

    FUNCTIONS = tuple(getattr(art, name) for name in sorted(vars(art)) if name.startswith('bugreport_'))

    def test_every_artifact_is_declared_and_found(self):
        declared = set(art.__artifacts_v2__)
        found = {function.__name__ for function in self.FUNCTIONS}
        self.assertEqual(declared, found)
        self.assertEqual(len(declared), 30)
        for key, info in art.__artifacts_v2__.items():
            self.assertTrue(info['category'].startswith('Android Bug Report - '))
            self.assertEqual(info['paths'], ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'), key)

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new'))
        old = self.stage('Dump/bugreport-example-EXOLD.txt', fixture.build_report('old'))
        for function in self.FUNCTIONS:
            headers, rows, source_path = self.run_artifact(function, path, old)
            self.assertTrue(rows, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
            self.assertEqual(source_path, '\n'.join(sorted([str(path), str(old)])))
            self.assertEqual(len(set(map(str, headers))), len(headers), function.__name__)       # no repeated column name

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows, source_path = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)
            self.assertEqual(source_path, str(path))

    def test_a_text_without_these_sections_gives_no_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.base.BANNER.format(report='2026-11-02 10:15:30'))
        for function in self.FUNCTIONS:
            self.assertEqual(self.run_artifact(function, path)[1], [], function.__name__)

    def test_time_columns(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new', zone='Europe/Paris'))
        _headers, rows, _source = self.run_artifact(art.bugreport_lock_settings_users, path)
        self.assertEqual(rows[0][:3], (utc(2026, 6, 9, 16, 42, 5), '2026-06-09 18:42:05', ''))
        _headers, rows, _source = self.run_artifact(art.bugreport_lock_settings_files, path)
        self.assertEqual(rows[0][:3], (utc(2026, 6, 9, 16, 42, 7), '2026-06-09 18:42:07', ''))
        _headers, rows, _source = self.run_artifact(art.bugreport_lock_settings_log, path)
        self.assertEqual(rows[1][:4], (utc(2026, 6, 9, 16, 42, 5, 127000), '2026-06-09 18:42:05.127', '', 'Enroll'))
        _headers, rows, _source = self.run_artifact(art.bugreport_trust_events, path)
        self.assertEqual(rows[0][:3], (utc(2026, 10, 29, 10, 2, 14, 250000), '10-29 11:02:14.250', ''))
        _headers, rows, _source = self.run_artifact(art.bugreport_vendor_guard_log, path)
        self.assertEqual([row[0] for row in rows][:4], [None, None, None, utc(2026, 3, 12, 6, 31, 44)])
        self.assertEqual(rows[-1][:3], (None, '1970-01-01 00:00:00', reader.NOTE_UNSET))
        _headers, rows, _source = self.run_artifact(art.bugreport_vold_log, path)
        self.assertEqual(rows[0][:2], (utc(2026, 10, 4, 3, 7, 7), '2026/10/04-03:07:07(GMT)'))      # printed as GMT: the zone does not matter
        self.assertEqual(rows[3][:2], (utc(2026, 10, 4, 3, 12, 12), '2026/10/04-03:12:12(UTC)'))
        self.assertIsNone(rows[4][0])
        _headers, rows, _source = self.run_artifact(art.bugreport_database_files, path)
        self.assertEqual(rows[0][:6], (utc(2026, 5, 17, 8, 12, 9, 114233), '2026-05-17T08:12:09.114233Z',
                                       utc(2026, 5, 17, 8, 12, 9, 114233), '2026-05-17T08:12:09.114233Z',
                                       utc(2026, 5, 17, 8, 12, 9, 109233), '2026-05-17T08:12:09.109233Z'))
        self.assertEqual(rows[2][4:6], (utc(1970, 1, 1), '1970-01-01T00:00:00Z'))
        _headers, rows, _source = self.run_artifact(art.bugreport_database_operations, path)
        self.assertEqual(rows[0][:3], (utc(2026, 11, 1, 13, 22, 31, 250000), '11-01 14:22:31.250', ''))
        self.assertEqual(rows[5][:2], (utc(2025, 12, 31, 22, 59, 59, 999000), '12-31 23:59:59.999'))      # after the report: last year

    def test_android_13_time_columns(self):
        path = self.stage('Dump/dumpstate.txt', zoned_service_text('lock_settings', A13_LOCK))
        _headers, rows, _source = self.run_artifact(art.bugreport_lock_settings_log, path)
        self.assertEqual([row[:3] for row in rows][:2], [(utc(2026, 3, 14, 8, 26, 53, 589000), '03-14 09:26:53.589', ''),
                                                         (utc(2026, 3, 14, 8, 26, 53, 600000), '03-14 09:26:53.600', '')])
        _headers, rows, _source = self.run_artifact(art.bugreport_lock_settings_users, path)
        self.assertEqual(rows[0][:3], (None, '1970-01-01 00:00:00 (0)', reader.NOTE_UNSET))      # not set: no UTC value
        path = self.stage('Dump/dumpstate.txt', zoned_service_text('knoxguard_service', A13_GUARD))
        _headers, rows, _source = self.run_artifact(art.bugreport_vendor_guard_log, path)
        self.assertEqual(rows[1][:6], (utc(2026, 3, 12, 6, 31, 45), '2026-03-12 07:31:45', '', 'Log', 'ExampleTag',
                                       '4100|4122 : [ExampleTag] second example : k_v n: 9 p: f'))

    def test_no_zone_gives_a_note_and_no_utc(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new', zone=''))
        for function in (art.bugreport_lock_settings_users, art.bugreport_lock_settings_files, art.bugreport_lock_settings_log,
                         art.bugreport_trust_events):
            _headers, rows, _source = self.run_artifact(function, path)
            self.assertTrue(rows)
            self.assertTrue(all(row[0] is None and row[2] == reader.NOTE_NO_ZONE for row in rows), function.__name__)

    def test_column_content(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new'))
        headers, rows, _source = self.run_artifact(art.bugreport_storage_io, path)
        self.assertEqual(headers[:3], ('Name/UID', 'fg_rchar', 'fg_wchar'))
        self.assertEqual(rows[0][:3], ('com.example.chat', 9120344, 412008))
        _headers, rows, _source = self.run_artifact(art.bugreport_biometric_statistics, path)
        self.assertEqual(rows[0][:7], ('fingerprint', 0, 'FingerprintProvider', 'FingerprintProvider/default', 0, 2, 3))
        self.assertEqual(rows[1][-3], 'future=7')
        _headers, rows, _source = self.run_artifact(art.bugreport_device_policy_admins, path)
        self.assertEqual([row[0] for row in rows], [0, 10])
        _headers, rows, _source = self.run_artifact(art.bugreport_storage_volumes, path)
        self.assertEqual(rows[0][:3], ('Storage volume', 'emulated;0', 'mounted'))
        _headers, rows, _source = self.run_artifact(art.bugreport_build_release_flags, path)
        self.assertEqual(rows[0][:2], ('system', 'RELEASE_EXAMPLE_ONE'))

    def test_a_dump_cut_by_the_platform_is_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new', cut=True))
        messages = []
        with mock.patch.object(art, 'logfunc', messages.append):
            for function in (art.bugreport_vendor_guard_log, art.bugreport_open_databases, art.bugreport_database_files,
                             art.bugreport_database_operations):
                self.run_artifact(function, path)
                self.run_artifact(function, path)
        cut = [message for message in messages if 'was cut by a 10000 ms timeout' in message]
        self.assertEqual(sorted(cut), sorted([
            'Bug report Dump/dumpstate.txt: the dbinfo service dump was cut by a 10000 ms timeout, the rows from it may be partial',
            'Bug report Dump/dumpstate.txt: the knoxguard_service service dump was cut by a 10000 ms timeout, the rows from it may be partial']))
        rows = self.run_artifact(art.bugreport_vendor_guard_log, path)[1]
        self.assertEqual(len(rows), 7)                       # the rows read before the timeout line are kept

    def test_an_uncut_dump_logs_nothing(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new'))
        messages = []
        with mock.patch.object(art, 'logfunc', messages.append):
            for function in self.FUNCTIONS:
                self.run_artifact(function, path)
        self.assertFalse([message for message in messages if 'was cut' in message])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('new'))
        second = self.stage('Dump2/bugreport-example-EXOLD.txt', fixture.build_report('old'))
        alone = len(self.run_artifact(art.bugreport_file_systems, first)[1])
        both = self.run_artifact(art.bugreport_file_systems, first, second)[1]
        self.assertGreater(len(both), alone)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example-EXOLD.txt'})

    def test_warnings_reach_the_log(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('new'))
        messages = []
        with mock.patch.object(art, 'logfunc', messages.append):
            self.run_artifact(art.bugreport_file_systems, path)
            self.run_artifact(art.bugreport_build_release_flags, path)
        self.assertIn('Bug report dumpstate.txt: FILESYSTEMS & FREE SPACE: 1 lines did not have the six columns and were not read',
                      messages)
        self.assertIn('Bug report dumpstate.txt: VENDOR BUILD-TIME RELEASE FLAGS: the text is not complete JSON and was not read',
                      messages)


if __name__ == '__main__':
    unittest.main()
