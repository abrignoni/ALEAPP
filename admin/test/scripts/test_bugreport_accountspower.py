"""Android bug report text: accounts, sync, backup, users, battery, power, device idle, thermal, process and memory sections."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_accountspower_fixture as fixture
from scripts import dumpstate_accountspower as ap
from scripts import dumpstate_reader as reader
from scripts.artifacts import bugreportAccountsPower as artifacts


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


def service(name, body, trailer=True):
    """A small report text with one dumpsys service section."""
    text = '== dumpstate: 2026-11-02 10:15:30\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE %s:\n%s' % (name, body)
    if trailer:
        text += '--------- 0.1s was the duration of dumpsys %s, ending at: 2026-11-02 10:15:31\n' % name
    return text


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


A16 = scan_text(fixture.build_report('a16'))
A10 = scan_text(fixture.build_report('a10', users=(0,)))


class HelperTests(unittest.TestCase):
    def test_dash_time(self):
        self.assertEqual(ap.dash_time('2026-10-24-08-06-15'), '2026-10-24 08:06:15')
        self.assertEqual(ap.dash_time('2026-10-24-09-09-43-033'), '2026-10-24 09:09:43.033')
        self.assertEqual(ap.dash_time('1970-01-01-00-00-16'), '1970-01-01 00:00:16')
        self.assertEqual(ap.dash_time('2026-10-24 08:06:15'), '')
        self.assertEqual(ap.dash_time(''), '')

    def test_duration_ms(self):
        self.assertEqual(ap.duration_ms('+1d04h32m55s844ms'), ((24 + 4) * 3600 + 32 * 60 + 55) * 1000 + 844)
        self.assertEqual(ap.duration_ms('+61ms'), 61)
        self.assertEqual(ap.duration_ms('-7h28m15s23ms'), ((7 * 60 + 28) * 60 + 15) * 1000 + 23)
        self.assertIsNone(ap.duration_ms('none'))

    def test_to_float(self):
        self.assertEqual(ap.to_float('1271'), 1271.0)
        self.assertIsNone(ap.to_float('nan'))
        self.assertIsNone(ap.to_float('x'))


class AccountTests(unittest.TestCase):
    def test_accounts_and_users(self):
        accounts = ap.rows(A16, 'accounts')
        self.assertEqual([a.user for a in accounts], [0, 0, 0, 0, 10])
        self.assertEqual(accounts[1].name, 'Example Chat')
        self.assertEqual(accounts[1].account_type, 'com.example.chat')
        self.assertEqual((accounts[4].user_name, accounts[4].user_flags), ('Work Profile', '8671931'))
        self.assertEqual(A16.warnings, [])

    def test_header_count_difference_is_a_warning(self):
        text = service('account', 'User UserInfo{0:Name:13}:\n  Accounts: 3\n    Account {name=a, type=t}\n    Account {name=b, type=t}\n  \n')
        report = scan_text(text)
        self.assertEqual(len(ap.rows(report, 'accounts')), 2)
        self.assertTrue([w for w in report.warnings if 'lists 2 accounts and the header says 3' in w])

    def test_history_rows_and_unread_lines(self):
        history = ap.rows(A16, 'account_history')
        self.assertEqual(len(history), 9)
        self.assertEqual((history[0].account_id, history[0].action, history[0].uid, history[0].key), (-1, 'action_called_account_add', 10100, 0))
        text = service('account', 'User UserInfo{0:N:13}:\n  Accounts History\n  1,action_account_add,2026-01-01 00:00:00,1,accounts,0\n'
                                  '  not a history row\n  Active Sessions: 0\n')
        report = scan_text(text)
        self.assertEqual(len(ap.rows(report, 'account_history')), 1)
        self.assertEqual(ap.tables(report).counts['account_history_unread'], 1)

    def test_authenticators_and_visibility(self):
        self.assertEqual([a.updated for a in ap.rows(A16, 'authenticators')], ['-1'] * 4)
        self.assertEqual([a.updated for a in ap.rows(A10, 'authenticators')], [''] * 2)
        found = ap.rows(A16, 'account_visibility')[2]
        self.assertEqual((found.account, found.package, found.value), ('Example Chat', 'com.example.chat', '1'))


class ContentTests(unittest.TestCase):
    def test_status_table_with_multi_line_cells(self):
        rows = ap.rows(A16, 'sync_status')
        self.assertEqual([r.authority for r in rows], ['example.calendar', 'example.contacts', 'example.notes'])
        calendar, contacts, notes = rows
        self.assertEqual((calendar.syncable, calendar.enabled, calendar.loc, calendar.per, calendar.total, calendar.cancel), (1, 'true', 1, 405, 774, 91))
        self.assertEqual((calendar.success_source, calendar.success_time, calendar.failure_source), ('OTHER', '2026-11-01 22:48:43', ''))
        self.assertEqual((contacts.failure_source, contacts.failure_time, contacts.failure_message), ('PERIODIC', '2026-11-02 06:43:33', 'io-error'))
        self.assertEqual((contacts.success_source, contacts.success_time), ('', ''))
        self.assertEqual((notes.success_time, notes.failure_time, notes.time), ('', '', '0s'))

    def test_locked_account_block_keeps_its_own_rows(self):
        body = ('Sync Status\nAccount a@example.test u0 type.one\n' + '=' * 20 + '\nAuthority  Syncable  Enabled  Stats  Loc  Time  Last Sync  Backoff\n' + '-' * 60 +
                '\nauth.one    1         true     Total  1    1s    USER SUCCESS\n' + ' ' * 40 + 'Today' + ' ' * 18 + '2026-11-01 01:02:03\n'
                'Account b@example.test u11 type.two (locked)\n' + '=' * 20 + '\nAuthority  Syncable  Enabled  Stats  Loc  Time  Last Sync  Backoff\n' + '-' * 60 +
                '\nauth.two    1         false    Total  2    2s\n')
        report = scan_text(service('content', body))
        rows = ap.rows(report, 'sync_status')
        self.assertEqual([(r.user, r.account, r.account_state, r.authority) for r in rows],
                         [(0, 'a@example.test', '', 'auth.one'), (11, 'b@example.test', 'locked', 'auth.two')])
        self.assertEqual(rows[1].success_time, '')

    def test_recent_history_columns(self):
        rows = ap.rows(A16, 'sync_history')
        self.assertEqual([r.index for r in rows], [1, 2, 3])
        self.assertEqual((rows[0].source, rows[0].duration, rows[0].extra, rows[0].user, rows[0].authority, rows[0].reason),
                         ('FEED', '15.8', '', 0, 'example.contacts', 'com.example.accounts'))
        self.assertEqual((rows[1].extra, rows[1].account), ('7', 'Example Chat'))
        self.assertEqual((rows[2].extra, rows[2].message, rows[2].extras), ('01:50:34', 'canceled', ''))
        self.assertEqual(rows[0].extras, 'Bundle[{feed=contacts/person.one@example.test}]')

    def test_last_syncs_and_unreadable_line(self):
        rows = ap.rows(A16, 'sync_last')
        self.assertEqual(len(rows), 3)
        self.assertEqual((rows[1].result, rows[1].source, rows[1].exemption, rows[1].extras), ('canceled', 'PERIODIC', 'fg', '[]'))
        self.assertEqual(ap.tables(A16).counts['sync_last_unread'], 1)

    def test_jobs_in_both_shapes(self):
        new_shape = ap.rows(A16, 'sync_jobs')
        self.assertEqual([(r.kind, r.job_id, r.user, r.account, r.authority, r.source) for r in new_shape],
                         [('Pending', 429, 0, 'person.one@example.test', 'example.mail', 'OTHER'),
                          ('Periodic', 21, 0, 'person.one@example.test', 'example.calendar', 'PERIODIC'),
                          ('Periodic', 22, 10, 'Example Chat', 'example.contacts', 'PERIODIC')])
        old_shape = ap.rows(A10, 'sync_jobs')
        self.assertEqual([(r.kind, r.account, r.account_type, r.authority) for r in old_shape[1:]],
                         [('Periodic', 'person.one@example.test', 'com.example.auth', 'example.calendar'),
                          ('Periodic', 'Example Chat', 'com.example.chat', 'example.contacts')])

    def test_state_lines(self):
        facts = {f.name: f.value for f in ap.rows(A16, 'sync_facts')}
        self.assertEqual(facts['Accounts'], '4')
        self.assertEqual(facts['Pending Syncs'], '1')
        self.assertIn('Success (5 for 23.5s', facts['Sync Statistics: Today'])
        self.assertNotIn('Client PIDs', facts)


class BackupAndUserTests(unittest.TestCase):
    def test_backup_state_transports_queues(self):
        facts = {f.name: f.value for f in ap.rows(A16, 'backup_facts')}
        self.assertEqual(facts['Last backup pass started'], '0')
        self.assertEqual(facts['now (in the Last backup pass started line)'], str(fixture.base.epoch_ms('2026-11-02 10:12:00')))
        transports = ap.rows(A16, 'backup_transports')
        self.assertEqual([(t.kind, t.current) for t in transports], [('Whitelist', False), ('Whitelist', False), ('Available', False), ('Available', True)])
        self.assertEqual(transports[3].destination, 'person.one@example.test')
        states = ap.rows(A16, 'backup_package_state')
        self.assertEqual([(s.package, s.state_bytes) for s in states], [('@pm@', 7565), ('com.example.chat', 88), ('com.example.maps', 0)])
        self.assertEqual([(p.uid, p.package) for p in ap.rows(A16, 'backup_participants')],
                         [(1000, 'com.example.settings'), (1000, 'android'), (10101, 'com.example.accounts')])
        queues = ap.rows(A16, 'backup_queues')
        self.assertEqual([(q.queue, q.package) for q in queues[:3]], [('Pending key/value backup', 'com.example.maps'),
                                                                         ('Pending key/value backup', 'android'), ('Full backup queue', 'com.example.never')])
        self.assertEqual(queues[2].value, '0')

    def test_users_in_both_layouts(self):
        users = ap.rows(A16, 'users')
        self.assertEqual([(u.user_id, u.name, u.flags_hex, u.serial, u.primary, u.parent) for u in users],
                         [(0, 'Example Owner', '4c13', 0, 'true', None), (10, 'Work Profile', '8671931', 10, 'false', 0)])
        self.assertEqual(users[1].restrictions, 'no_bluetooth_sharing, no_wallpaper')
        self.assertEqual(users[0].state, 'RUNNING_UNLOCKED')
        old = ap.rows(A10, 'users')[0]
        self.assertEqual((old.user_type, old.flags, old.primary, old.last_foreground, old.state), ('', '', '', '', 'RUNNING_UNLOCKED'))
        facts = {f.name: f.value for f in ap.rows(A16, 'user_facts')}
        self.assertEqual(facts['Started users state'], '{0=3, 10=1}')
        self.assertNotIn('Client PIDs', facts)
        guest = {f.name: f.value for f in ap.rows(A10, 'user_facts')}
        self.assertEqual(guest['Guest restrictions'], 'no_sms, no_outgoing_calls')


class BatteryTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def test_history_format_2_has_a_time_on_every_record(self):
        events = ap.rows(A16, 'battery_history')
        self.assertEqual(len(events), 10)
        self.assertEqual((events[0].marker, events[0].level, events[0].state), ('Reset', None, ''))
        self.assertEqual((events[1].level, events[1].state), (100, 'c4900011'))
        self.assertEqual(events[3].changes, '+top=u0a300:"com.example.user.chat" volt=4401')
        self.assertEqual([e.marker for e in events[-3:]], ['Clock', 'Shutdown', 'Start'])
        self.assertEqual(events[2].changes, '')

    def test_history_format_1_offsets_and_wrapped_lines(self):
        events = ap.rows(A10, 'battery_history')
        self.assertEqual(len(events), 11)        # the Details lines and the wrapped line are not records
        self.assertEqual((events[3].time_text, events[3].anchor, events[3].delta_ms), ('+6ms', '2026-11-01 21:00:00', 6))
        clock = events[5]
        self.assertEqual((clock.marker, clock.anchor, clock.delta_ms), ('Clock', '2026-11-02 05:08:18', 0))
        self.assertEqual((events[7].anchor, events[7].delta_ms), ('2026-11-02 05:08:18', ((13 * 60 + 15) * 60 + 4) * 1000 + 479 - ((8 * 60 + 8) * 60 + 38) * 1000 - 434))

    def test_history_times_in_utc(self):
        rows = artifacts.bugreport_battery_history.__wrapped__(self._context('a16'))[1]
        self.assertEqual(rows[1][0], utc(2026, 11, 1, 20, 0, 0, 33000))          # Europe/Paris is one hour ahead in November
        self.assertEqual(rows[1][1], '11-01 21:00:00.033')
        rows = artifacts.bugreport_battery_history.__wrapped__(self._context('a10'))[1]
        self.assertEqual(rows[3][0], utc(2026, 11, 1, 20, 0, 0, 6000))
        self.assertEqual(rows[6][0], utc(2026, 11, 2, 4, 8, 18, 566000))          # after the clock record of 05:08:18 local
        self.assertEqual(rows[3][2], '2026-11-01 21:00:00')

    def _context(self, layout):
        path = Path(self.work) / ('Dump-' + layout) / 'dumpstate.txt'
        path.parent.mkdir(parents=True)
        path.write_text(fixture.build_report(layout, users=(0,) if layout == 'a10' else (0, 10)), encoding='utf-8')
        return Context(self.work, [path])

    def test_daily_periods_and_package_changes(self):
        periods = ap.rows(A16, 'battery_daily')
        self.assertEqual([(p.kind, p.start, p.end, p.discharge_steps, p.charge_steps, p.package_changes) for p in periods],
                         [('Current', '2026-11-02-03-00-00', '', 2, 1, 0),
                          ('Daily', '2026-11-01-02-13-28', '2026-11-02-03-00-00', 3, 1, 3),
                          ('Daily', '2026-10-31-01-00-00', '2026-11-01-02-13-28', 1, 0, 0)])
        self.assertIn('Discharge total time: 9h 50m 23s 100ms  (from 3 steps)', periods[1].totals)
        self.assertIn('Discharge screen on time', periods[1].totals)
        changes = ap.rows(A16, 'battery_packages')
        self.assertEqual([(c.change, c.package, c.version) for c in changes],
                         [('Update', 'com.example.chat', 5120), ('Update', 'com.example.chat', 5120), ('Uninstall', 'com.example.gone', None)])

    def test_power_use_layouts(self):
        newer = ap.rows(A16, 'battery_power')
        self.assertEqual([(r.kind, r.name, r.context, r.total) for r in newer],
                         [('Item', 'Capacity', '', 4860.0), ('Item', 'screen', '', 1271.0), ('Item', 'cpu', '', 41870.0),
                          ('Item', 'screen', '(on battery, screen on)', 1271.0), ('UID', '1000', '', 8816.0), ('UID', 'u0a300', '', 7542.0),
                          ('UID', 'u0a301', '', 12.5)])
        self.assertIn('fgs: 44.9', newer[5].detail)
        self.assertIn('screen=705', newer[5].detail)
        older = ap.rows(A10, 'battery_power')
        self.assertEqual([(r.kind, r.name) for r in older], [('Item', 'Capacity'), ('Item', 'Unaccounted'), ('Item', 'Screen'), ('UID', '1000'),
                                                           ('UID', 'u0a300'), ('Item', 'Idle')])

    def test_wake_locks_and_packages_in_uid_blocks(self):
        locks = ap.rows(A16, 'battery_wake_locks')
        self.assertEqual([(w.kind, w.uid, w.name) for w in locks if w.kind == 'Kernel'],
                         [('Kernel', '', 'PowerManagerService.WakeLocks'), ('Kernel', '', 'Active resource: example_wakelock')])
        mine = [w for w in locks if w.uid == 'u0a300']
        self.assertEqual([w.name for w in mine], ['NotificationManagerService:post:com.example.user.chat', '*alarm*', 'WindowManager/displayId:0'])
        self.assertEqual(mine[0].usage, '')
        self.assertTrue(mine[1].usage.startswith('14ms partial (4 times)'))
        self.assertEqual(ap.tables(A16).uid_packages['u0a300'], ['com.example.user.chat', 'com.example.user.chat.lite'])
        self.assertEqual(ap.tables(A16).uid_packages['1000'], ['android'])
        self.assertNotIn('u0a301', ap.tables(A16).uid_packages)
        self.assertEqual(len([w for w in locks if 'job' in w.name]), 0)      # the All partial wake locks list is not read

    def test_battery_service_and_thermal(self):
        facts = {f.name: f.value for f in ap.rows(A16, 'battery_facts')}
        self.assertEqual((facts['level'], facts['status'], facts['technology']), ('15', '3', 'Li-ion'))
        thermal = ap.rows(A16, 'thermal')
        self.assertEqual([(t.group, t.kind, t.name, t.item_type, t.value, t.status) for t in thermal if t.kind == 'Temperature'],
                         [('Cached temperatures', 'Temperature', 'gpu', '1', '38.0', '0'), ('Cached temperatures', 'Temperature', 'Battery', '2', '32.0', '0'),
                          ('Current temperatures from HAL', 'Temperature', 'cluster1', '0', '44.0', '0')])
        threshold = [t for t in thermal if t.kind == 'Threshold'][0]
        self.assertTrue(threshold.detail.startswith('mHotThrottlingThresholds=[NaN, 85.0, 90.0]'))
        self.assertEqual([t.value for t in thermal if t.name == 'Values'], ['[NaN, NaN, 1.1666666, 1.3333334]'])


class PowerIdleTests(unittest.TestCase):
    def test_power_facts_and_timeouts(self):
        facts = {(f.block, f.name): f.value for f in ap.rows(A16, 'power_facts')}
        self.assertEqual(facts[('Power Manager State', 'mBatteryLevel')], '15')
        self.assertEqual(facts[('Power Manager State', 'Settings power_manager_constants.no_cached_wake_locks')], 'true')
        self.assertEqual(facts[('Settings and Configuration', 'mLastWakeUpReason')], '1')
        self.assertEqual(facts[('Timeouts', 'Screen off timeout')], '60000 ms')
        self.assertNotIn(('Power Manager State', 'UID 1000'), facts)

    def test_wake_locks_in_both_shapes(self):
        new = ap.rows(A16, 'power_wake_locks')
        self.assertEqual((new[0].level, new[0].tag, new[0].held, new[0].uid, new[0].pid), ('PARTIAL_WAKE_LOCK', 'wake:com.example.user.chat.Holder', '-936ms', 10300, 19915))
        self.assertEqual((new[1].flags, new[1].pid, new[1].uid), ('LONG', None, 1041))
        old = ap.rows(A10, 'power_wake_locks')
        self.assertEqual((old[0].level, old[0].tag, old[0].flags, old[0].held, old[0].uid), ('SCREEN_BRIGHT_WAKE_LOCK', 'WindowManager', 'ON_AFTER_RELEASE', '-1s775ms', 1000))

    def test_power_events(self):
        events = ap.rows(A16, 'power_events')
        self.assertEqual([(e.kind, e.index) for e in events], [('WakeLock Release', 1), ('WakeUp', 1), ('WakeUp', 2), ('WakeUp', 3)])
        release, off, on_row, _third = events
        self.assertEqual((release.uid, release.held, release.level, release.tag), (1000, '+4m46s348ms', 'SCREEN_BRIGHT_WAKE_LOCK', 'WindowManager/displayId:0'))
        self.assertEqual((off.uid, off.display, off.state, off.reason, off.foreground, off.caller), (1000, '0', 'OFF', 'timeout', 'com.example.settings', ''))
        self.assertEqual((on_row.state, on_row.reason, on_row.caller), ('ON', 'application', 'android'))
        self.assertEqual(ap.tables(A16).counts['power_event_unread'], 1)
        self.assertEqual(ap.rows(A10, 'power_events'), [])

    def test_device_idle(self):
        facts = {(f.block, f.name): f.value for f in ap.rows(A16, 'idle_facts')}
        self.assertEqual(facts[('Settings', 'light_idle_to')], '+15m0s0ms')
        self.assertEqual(facts[('State', 'mLightEnabled')], 'true')
        self.assertEqual(facts[('State', 'mDeepEnabled')], 'true')
        self.assertTrue(facts[('State', 'mMotionSensor')].startswith('{Sensor name="significant"'))
        self.assertEqual(facts[('State', 'mState')], 'ACTIVE')
        self.assertNotIn(('State', 'name'), facts)
        history = ap.rows(A16, 'idle_history')
        self.assertEqual([(h.position, h.state, h.ago, h.reason) for h in history],
                         [(0, 'light-idle', '-7h28m15s23ms', ''), (1, 'light-maint', '-7h12m14s687ms', ''),
                          (2, 'normal', '-6h17m7s310ms', 'motion'), (3, 'deep-idle', '-3h50m49s292ms', '')])


class ProcessAndMemoryTests(unittest.TestCase):
    def test_process_stats_periods(self):
        stats = ap.rows(A16, 'procstats')
        self.assertEqual(len(stats), 9)
        first = stats[0]
        self.assertEqual((first.period, first.period_start, first.process, first.uid, first.version, first.state, first.share),
                         ('COMMITTED STATS FROM 2026-11-01-06-05-25', '2026-11-01-06-05-25', 'com.example.systemui', 'u0a385', '35', 'TOTAL', '100%'))
        self.assertEqual(stats[2].measures, '')
        self.assertEqual([s.state for s in stats if s.process == 'com.example.user.chat:sync'], ['TOTAL', '(Home)'])
        self.assertEqual({s.period for s in stats[6:]}, {'CURRENT STATS', 'AGGREGATED OVER LAST 24 HOURS'})
        self.assertFalse([s for s in stats if s.process in ('com.example.perpackage', 'com.example.skipped')])
        self.assertEqual(ap.tables(A16).counts['procstats_unread'], 1)

    def test_ps_threads(self):
        threads = ap.rows(A16, 'ps')
        self.assertEqual(len(threads), 5)
        self.assertEqual((threads[1].pid, threads[1].tid, threads[1].wchan, threads[1].nice), (1, 320, 'do_epoll_wait', -20))
        self.assertEqual(threads[3].command, 'Signal Catcher')
        self.assertEqual(threads[2].label, 'u:r:untrusted_app:s0:c168,c256,c512,c768')
        self.assertEqual((threads[2].user, threads[2].vsz, threads[2].rss, threads[2].cpu_time), ('u0_a168', 6428896, 213352, '00:00:00'))
        self.assertEqual(ap.tables(A16).counts['ps_unread'], 1)

    def test_ps_with_an_unknown_header_reads_nothing(self):
        text = '== dumpstate: 2026-11-02 10:15:30\n\n------ PROCESSES AND THREADS (ps) ------\nA B C\n1 2 3\n'
        report = scan_text(text)
        self.assertEqual(ap.rows(report, 'ps'), [])
        self.assertTrue([w for w in report.warnings if 'header line was not recognised' in w])

    def test_memory_lists_blocks_and_totals(self):
        entries = ap.rows(A16, 'memory_entries')
        self.assertEqual([(e.basis, e.kilobytes, e.process, e.pid, e.note, e.swap_kilobytes) for e in entries],
                         [('RSS', 513003, 'com.example.user.chat', 18300, 'activities', None), ('RSS', 310960, 'system', 8107, '', None),
                          ('PSS', 687382, 'com.example.user.chat', 18300, 'activities', 255444),
                          ('PSS', 84821, 'vendor.example.camera-service_64', 1138, '', 81312)])
        block = ap.rows(A16, 'memory_processes')
        self.assertEqual(len(block), 1)           # the second block prints no table
        self.assertEqual(ap.tables(A16).counts['meminfo_blocks_unread'], 1)
        row = block[0]
        self.assertEqual((row.pid, row.process, row.pss_total, row.private_dirty, row.rss_total, row.heap_size), (22526, 'com.example.settings', 883131, 896580, 178716, 895276))
        self.assertEqual((row.native_heap_pss, row.dalvik_heap_pss, row.java_heap, row.graphics, row.system, row.views, row.activities),
                         (13693, 84126, 20476, 62614, 18485, 440, 4))
        facts = {f.name: f.value for f in ap.rows(A16, 'memory_facts')}
        self.assertEqual((facts['Uptime'], facts['Realtime']), ('88359925', '17712157'))
        self.assertEqual(facts['Total RAM'], '3,725,764K (status moderate)')

    def test_memory_blocks_without_rss_columns(self):
        row = ap.rows(A10, 'memory_processes')[0]
        self.assertEqual((row.pid, row.pss_total, row.rss_total, row.heap_size, row.swap_pss), (29945, 186447, None, 884400, 25946))
        self.assertEqual(ap.rows(A10, 'memory_entries'), [])

    def test_user_suffix_and_wide_names_in_the_lists(self):
        body = ('Applications Memory Usage (in Kilobytes):\nTotal PSS by process:\n'
                '     21,833K: com.example.one (pid 19492)                             (user 11)(   10,208K in swap)\n'
                '     11,498K: com.example.two (pid 3512 / activities)   (user 11)\n'
                '     not a list line\n     5,000K: com.example.three (pid 5)\n\nTotal PSS by OOM adjustment:\n    1,049K: Native\n')
        report = scan_text(service('meminfo', body))
        entries = ap.rows(report, 'memory_entries')
        self.assertEqual([(e.process, e.user, e.swap_kilobytes, e.note) for e in entries],
                         [('com.example.one', 11, 10208, ''), ('com.example.two', 11, None, 'activities'), ('com.example.three', None, None, '')])
        self.assertEqual(ap.tables(report).counts['memory_entry_unread'], 1)


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

    FUNCTIONS = [getattr(artifacts, name) for name in sorted(artifacts.__artifacts_v2__)]

    def test_every_artifact_is_declared_with_its_function(self):
        self.assertEqual(len(self.FUNCTIONS), 33)
        for name, block in artifacts.__artifacts_v2__.items():
            self.assertTrue(block['category'].startswith('Android Bug Report - '))
            self.assertEqual(block['paths'], ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'))
            self.assertTrue(callable(getattr(artifacts, name)))
        names = [block['name'] for block in artifacts.__artifacts_v2__.values()]
        self.assertEqual(len(names), len(set(names)))

    def test_read_by_names_are_artifact_names(self):
        names = {block['name'].replace('Bug Report - ', '') for block in artifacts.__artifacts_v2__.values()}
        mentioned = {part.strip() for text in ap.READ_BY.values() for part in text.split(';')}
        self.assertEqual(mentioned, names)
        self.assertEqual({(reader_class.kind, reader_class.name) for reader_class in ap.READERS}, set(ap.READ_BY))
        self.assertTrue(set(ap.READ_BY) <= set(reader.READ_BY))

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        for function in self.FUNCTIONS:
            headers, rows, source_path = self.run_artifact(function, path)
            self.assertTrue(rows, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
            self.assertEqual(source_path, str(path))

    def test_the_older_layout_gives_rows_too(self):
        path = self.stage('Dump/bugreport-x.txt', fixture.build_report('a10', users=(0,), newline='\r\n'))
        empty = {'bugreport_power_events', 'bugreport_memory_by_process'}
        for function in self.FUNCTIONS:
            _headers, rows, _source = self.run_artifact(function, path)
            if function.__name__ in empty:
                self.assertEqual(rows, [], function.__name__)
            else:
                self.assertTrue(rows, function.__name__)

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)

    def test_a_text_without_these_sections_gives_no_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.base.BANNER.format(report='2026-11-02 10:15:30'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            for function in self.FUNCTIONS:
                self.assertEqual(self.run_artifact(function, path)[1], [])
        self.assertTrue([m for m in messages if 'no account section was found' in m])

    def test_times_are_converted_with_the_report_zone(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Asia/Kolkata'))
        rows = self.run_artifact(artifacts.bugreport_account_history, path)[1]
        self.assertEqual(rows[0][0], utc(2026, 3, 1, 3, 30))
        self.assertEqual(rows[0][1], '2026-03-01 09:00:00')
        rows = self.run_artifact(artifacts.bugreport_sync_recent_history, path)[1]
        self.assertEqual(rows[0][0], utc(2026, 11, 2, 1, 13, 18))
        rows = self.run_artifact(artifacts.bugreport_power_events, path)[1]
        self.assertEqual(rows[1][0], utc(2026, 11, 1, 15, 35, 38, 650000))
        rows = self.run_artifact(artifacts.bugreport_sync_adapter_status, path)[1]
        self.assertEqual((rows[0][0], rows[1][1], rows[2][0]), (utc(2026, 11, 1, 17, 18, 43), utc(2026, 11, 2, 1, 13, 33), None))
        rows = self.run_artifact(artifacts.bugreport_battery_daily_summary, path)[1]
        self.assertEqual((rows[0][0], rows[0][1], rows[1][0]), (utc(2026, 11, 1, 21, 30), None, utc(2026, 10, 31, 20, 43, 28)))

    def test_no_zone_gives_no_utc(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone=''))
        self.assertTrue(all(row[0] is None for row in self.run_artifact(artifacts.bugreport_account_history, path)[1]))
        self.assertTrue(all(row[0] is None for row in self.run_artifact(artifacts.bugreport_battery_history, path)[1]))
        self.assertTrue(all(row[7] is None for row in self.run_artifact(artifacts.bugreport_process_stats, path)[1]))

    def test_unset_battery_period_end_gets_no_utc(self):
        text = fixture.build_report('a16').replace('Daily from 2026-10-31-01-00-00 to 2026-11-01-02-13-28:', 'Daily from 2026-10-31-01-00-00 to 1970-01-01-00-00-16:')
        path = self.stage('Dump/dumpstate.txt', text)
        rows = self.run_artifact(artifacts.bugreport_battery_daily_summary, path)[1]
        self.assertEqual((rows[2][1], rows[2][4]), (None, '1970-01-01-00-00-16'))
        self.assertIsNotNone(rows[2][0])

    def test_backup_epoch_times(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        rows = self.run_artifact(artifacts.bugreport_backup_state, path)[1]
        times = {row[0]: row[2] for row in rows if row[2] is not None}
        self.assertEqual(times, {'now (in the Last backup pass started line)': utc(2026, 11, 2, 10, 12), 'next scheduled': utc(2026, 11, 2, 19, 22)})
        rows = self.run_artifact(artifacts.bugreport_backup_queues, path)[1]
        self.assertEqual([row[3] for row in rows], [None, None, None, utc(2026, 10, 30, 10, 12), utc(2026, 11, 2, 9, 12)])

    def test_sync_state_now_time(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        rows = self.run_artifact(artifacts.bugreport_sync_state, path)[1]
        self.assertEqual([row[2] for row in rows if row[2] is not None], [utc(2026, 11, 2, 9, 12, 56)])

    def test_uid_packages_are_filled_for_wake_locks(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        rows = self.run_artifact(artifacts.bugreport_battery_wake_locks, path)[1]
        self.assertEqual({row[3]: row[2] for row in rows if row[1] == 'u0a300'}['*alarm*'], 'com.example.user.chat, com.example.user.chat.lite')

    def test_a_cut_meminfo_dump_is_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_memory_by_process, path)
            self.run_artifact(artifacts.bugreport_memory_process_detail, path)
            self.run_artifact(artifacts.bugreport_memory_summary, path)
        cut = [m for m in messages if 'meminfo service dump was cut by a 60000 ms timeout' in m]
        self.assertEqual(len(cut), 1)
        self.assertEqual(len(self.run_artifact(artifacts.bugreport_memory_process_detail, path)[1]), 1)

    def test_lines_not_read_are_logged(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_process_threads, path)
            self.run_artifact(artifacts.bugreport_sync_adapter_last_syncs, path)
        self.assertTrue([m for m in messages if '(ps)' in m])
        self.assertTrue([m for m in messages if '(sync_last)' in m])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10', users=(0,)))
        both = self.run_artifact(artifacts.bugreport_accounts, first, second)[1]
        alone = self.run_artifact(artifacts.bugreport_accounts, first)[1]
        self.assertEqual(len(both), len(alone) + 4)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})

    def test_report_inside_a_zip(self):
        member = 'bugreport-example-EXAMPLE-2026-11-02-10-15-30.txt'
        path = Path(self.work) / 'Dump' / 'bugreport-example.zip'
        path.parent.mkdir(parents=True)
        fixture.base.write_zip(str(path), [('main_entry.txt', member.encode()), (member, fixture.build_report('a16').encode('utf-8'))])
        rows = self.run_artifact(artifacts.bugreport_accounts, path)[1]
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0][-1], 'Dump/bugreport-example.zip!/' + member)

    def test_row_limit_is_reported(self):
        text = service('account', 'User UserInfo{0:N:13}:\n  Accounts: 5\n' + ''.join('    Account {name=n%d, type=t}\n' % n for n in range(5)))
        with mock.patch.object(reader, 'MAX_ROWS', 3):
            report = scan_text(text)
        self.assertEqual(len(ap.rows(report, 'accounts')), 3)
        self.assertTrue([w for w in report.warnings if 'accounts: more than 3 rows' in w])

    def test_odd_bytes_do_not_stop_the_reader(self):
        text = fixture.build_report('a16').encode('utf-8')
        text = text.replace(b'Example Owner', b'Example \xe9 Own\x00er', 1).replace(b'person.two@example.test', b'person.two\r@example.test', 1)
        report = scan_text(text)
        rows = ap.rows(report, 'accounts')
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0].user_name, 'Example \ufffd Own er')
        self.assertTrue('\r' not in rows[2].name)

    def test_long_lines_are_cut(self):
        long_value = 'x' * 70000
        text = service('battery', 'Current Battery Service state:\n  level: 5\n  ' + long_value + ': 1\n')
        report = scan_text(text)
        self.assertEqual([f.value for f in ap.rows(report, 'battery_facts') if f.name == 'level'], ['5'])
        self.assertTrue(all(len(f.name) <= 200 and len(f.value) <= ap.VALUE_CHARS for f in ap.rows(report, 'battery_facts')))


if __name__ == '__main__':
    unittest.main()
