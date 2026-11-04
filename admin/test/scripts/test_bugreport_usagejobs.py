"""Android bug report text: usage intervals, standby buckets, scheduled jobs, alarms and notifications."""
# pylint: disable=protected-access,unbalanced-tuple-unpacking
import io
import os
import random
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as base
from admin.test.scripts import bugreport_usagejobs_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts import dumpstate_usagejobs as usagejobs
from scripts.artifacts import bugreportUsageJobs as artifacts


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


def service_text(name, body, banner=True):
    """A minimal text with one dumpsys service section."""
    return (('== dumpstate: 2026-11-02 10:15:30\n\n' if banner else '') + '------ DUMPSYS (/system/bin/dumpsys) ------\n'
            'DUMP OF SERVICE %s:\n' % name + body)


class HelperTests(unittest.TestCase):
    def test_durations(self):
        self.assertEqual(usagejobs.duration_ms('+22m30s0ms'), 1350000)
        self.assertEqual(usagejobs.duration_ms('-1h7m31s759ms'), -4051759)
        self.assertEqual(usagejobs.duration_ms('+1d0h0m0s0ms'), 86400000)
        self.assertEqual(usagejobs.duration_ms('-9m47s378ms'), -587378)
        self.assertEqual(usagejobs.duration_ms('+100ms'), 100)
        self.assertEqual(usagejobs.duration_ms('+5m'), 300000)
        self.assertEqual(usagejobs.duration_ms('0'), 0)
        for text in ('--', '', 'x', '+', '<uninitialized>', '+1x', '5 m'):
            self.assertIsNone(usagejobs.duration_ms(text), text)

    def test_clock_texts_and_amounts(self):
        self.assertEqual(usagejobs.clock_text_ms('01:20'), 80000)
        self.assertEqual(usagejobs.clock_text_ms('4:21:41'), 15701000)
        self.assertIsNone(usagejobs.clock_text_ms('1:2:3:4'))
        self.assertIsNone(usagejobs.clock_text_ms('aa:bb'))
        self.assertEqual(usagejobs.time_amount_ms('81989'), 81989)
        self.assertEqual(usagejobs.time_amount_ms('00:02'), 2000)
        self.assertIsNone(usagejobs.time_amount_ms('²'))
        self.assertIsNone(usagejobs.time_amount_ms(''))

    def test_uid_users(self):
        self.assertEqual(usagejobs.uid_user('u0a123'), 0)
        self.assertEqual(usagejobs.uid_user('u11a283'), 11)
        self.assertEqual(usagejobs.uid_user('1000'), 0)
        self.assertEqual(usagejobs.uid_user('1110306'), 11)
        self.assertIsNone(usagejobs.uid_user('system'))
        self.assertIsNone(usagejobs.uid_user(''))

    def test_readers_are_registered_once_in_the_shared_pass(self):
        for cls in usagejobs.READERS:
            self.assertEqual(reader.READERS.count(cls), 1, cls)
        usagejobs.register()
        for cls in usagejobs.READERS:
            self.assertEqual(reader.READERS.count(cls), 1, cls)
        self.assertEqual(reader.READ_BY[('service', 'jobscheduler')], 'Scheduled Jobs')
        self.assertIn(usagejobs.UsageIntervalCheckinReader, reader.readers_by_section()[('command', 'CHECKIN USAGESTATS')])
        self.assertIn(reader.UsageCheckinReader, reader.readers_by_section()[('command', 'CHECKIN USAGESTATS')])


class UsageTests(unittest.TestCase):
    def test_checkin_form_intervals(self):
        report = scan_text(fixture.build_report('a16'))
        rows = [row for row in usagejobs.table(report, 'uj_intervals')]
        self.assertEqual({row.section for row in rows}, {'CHECKIN USAGESTATS'})
        self.assertEqual({row.user for row in rows}, {0, 10})
        daily = [row for row in rows if row.user == 0 and row.interval == 'daily']
        self.assertEqual([row.package for row in daily],
                         ['com.example.user.chat', 'com.example.user.service', 'com.example.user.video'])   # idle is not listed
        chat = daily[0]
        self.assertEqual((chat.total_used, chat.total_visible, chat.launches, chat.total_fs), ('80000', '83000', 3, '0'))
        self.assertEqual(chat.last_used, str(fixture.ms_at(-600)))
        self.assertEqual(report.usage_time(chat.last_used), utc(2026, 11, 2, 9, 5, 20))
        self.assertEqual(report.usage_time(chat.begin), utc(2026, 11, 1, 22, 8, 40))
        self.assertEqual(report.usage_time(chat.end), utc(2026, 11, 2, 9, 15, 20))
        self.assertEqual(chat.range_text, '')
        only_component = daily[1]
        self.assertEqual((only_component.last_used, only_component.last_component), ('0', str(fixture.ms_at(-7200))))
        self.assertEqual({row.interval for row in rows}, {'daily', 'weekly', 'monthly', 'yearly'})
        self.assertEqual(usagejobs.counts(report)[('interval_skipped', 'CHECKIN USAGESTATS')], 8)       # 4 intervals x 2 users

    def test_service_form_intervals_are_clock_text(self):
        report = scan_text(fixture.build_report('a10', zone='Europe/Paris'))
        self.assertEqual({row.section for row in usagejobs.table(report, 'uj_intervals')}, {'DUMP OF SERVICE usagestats', 'CHECKIN USAGESTATS'})
        plain = [row for row in usagejobs.table(report, 'uj_intervals') if row.section.startswith('DUMP') and row.user == 0 and row.interval == 'daily']
        chat = plain[0]
        self.assertEqual((chat.total_used, chat.total_visible), ('01:20', '01:23'))
        self.assertEqual(chat.range_text, '11/01/2026, 21:00 \u2013 11/02/2026, 10:15')
        self.assertEqual((chat.begin, chat.end), ('', ''))
        self.assertEqual(chat.last_used, fixture.wall_at(-600))
        self.assertEqual(report.usage_time(chat.last_used), utc(2026, 11, 2, 9, 5, 20))      # Paris is UTC+1 on this date
        unset = plain[1]
        self.assertEqual((unset.last_used, unset.last_component), ('1970-01-01 00:00:00', fixture.wall_at(-7200)))
        self.assertIsNone(report.usage_time(unset.last_used))

    def test_event_aggregations(self):
        report = scan_text(fixture.build_report('a16'))
        events = [row for row in usagejobs.table(report, 'uj_interval_events') if row.user == 0 and row.interval == 'daily']
        self.assertEqual([(e.event, e.count, e.total, e.tail) for e in events],
                         [('screen-interactive', 12, '150000', '(now running, started at )'),
                          ('screen-non-interactive', 12, '230000', ''), ('keyguard-shown', 5, '1000', ''),
                          ('keyguard-hidden', 5, '61000', '(now running, started at )')])
        plain = scan_text(fixture.build_report('a10'))
        first = [row for row in usagejobs.table(plain, 'uj_interval_events') if row.section.startswith('DUMP')][0]
        self.assertEqual((first.event, first.total), ('screen-interactive', '02:30'))

    def test_standby_states_both_layouts(self):
        report = scan_text(fixture.build_report('a16'))
        rows = [row for row in usagejobs.table(report, 'uj_standby') if row.user == 0]
        self.assertEqual([row.package for row in rows], [item[0] for item in fixture.STANDBY])
        chat = rows[0]
        self.assertEqual((chat.bucket, chat.reason, chat.used, chat.used_scr, chat.expiry, chat.last_informed, chat.next_launch,
                          chat.idle, chat.other),
                         ('10', 'u-si', '+1m5s0ms', '+3d0h0m0s0ms', '(10:+1h0m0s0ms,20:+1d0h0m0s0ms)', '10', '+2d1h0m0s0ms', 'n', ''))
        self.assertEqual(rows[1].used, '<uninitialized>')
        self.assertEqual({row.user for row in usagejobs.table(report, 'uj_standby')}, {0, 10})
        old = scan_text(fixture.build_report('a10'))
        old_rows = [row for row in usagejobs.table(old, 'uj_standby') if row.section.startswith('DUMP') and row.user == 0]
        self.assertEqual(len(old_rows), len(fixture.STANDBY))
        self.assertEqual(old_rows[0].other, 'activeLeft=-386d10h41m19s637ms wsLeft=-386d10h41m19s637ms')
        self.assertEqual((old_rows[0].used_by_user, old_rows[0].expiry, old_rows[0].last_informed), ('', '', ''))
        copy = [row for row in usagejobs.table(old, 'uj_standby') if row.section == 'CHECKIN USAGESTATS' and row.user == 0]
        self.assertEqual([row.package for row in copy], [row.package for row in old_rows])

    def test_lines_after_the_standby_list_are_not_standby_rows(self):
        report = scan_text(fixture.build_report('a16'))
        self.assertEqual(len(usagejobs.table(report, 'uj_standby')), 2 * len(fixture.STANDBY))             # two users, no totals lines
        self.assertFalse([row for row in usagejobs.table(report, 'uj_standby') if row.package == ''])

    def test_existing_usage_events_are_unchanged(self):
        report = scan_text(fixture.build_report('a16'))
        self.assertEqual(len(report.usage_events), len(base.USAGE_EVENTS) + len(base.USAGE_EVENTS[:1]))

    def test_cut_checkin_output_is_counted(self):
        report = scan_text(fixture.build_report('a16', cut=True))
        self.assertEqual(usagejobs.counts(report)[('cut', 'CHECKIN USAGESTATS')], 1)
        self.assertTrue(usagejobs.table(report, 'uj_intervals'))

    def test_nonnumeric_user_does_not_stop_the_pass(self):
        text = fixture.build_report('a16').replace('user=0 ', 'user=² ', 1)
        report = scan_text(text)
        self.assertTrue(usagejobs.table(report, 'uj_jobs'))


class JobTests(unittest.TestCase):
    def test_registered_and_completed_jobs(self):
        report = scan_text(fixture.build_report('a16'))
        jobs = usagejobs.table(report, 'uj_jobs')
        self.assertEqual([job.listing for job in jobs], ['Registered'] * len(fixture.JOBS) + ['Recently completed'] * 2)
        chat, sync, plain, work = jobs[:4]
        self.assertEqual((chat.package, chat.user, chat.uid_label, chat.job_id, chat.namespace), ('com.example.user.chat', 0, 'u0a300', 11, ''))
        self.assertEqual(chat.service, 'com.example.user.chat/.sync.SyncJob')
        self.assertEqual((chat.persisted, chat.min_latency, chat.max_delay, chat.extras),
                         ('yes', '+1h0m0s0ms', '+2h0m0s0ms', '{sync_key=example-value-1}'))
        self.assertIn('Capabilities: INTERNET', chat.network)
        self.assertEqual((chat.required, chat.satisfied, chat.unsatisfied), (
            'TIMING_DELAY DEADLINE IDLE', 'BATTERY_NOT_LOW DEVICE_NOT_DOZING', 'IDLE'))
        self.assertEqual((chat.bucket, chat.enqueue, chat.run_earliest, chat.run_latest),
                         ('WORKING_SET', '-9h26m40s0ms', '-7h46m40s0ms', '+2h0m0s0ms'))
        self.assertEqual((chat.last_success, chat.last_failure, chat.restricted), ('2026-11-02 08:30:00', '2026-10-30 01:02:03', 'none.'))
        self.assertEqual((sync.namespace, sync.uid_label, sync.package, sync.job_type), (
            'SyncManager', '1000', 'com.example.sync', 'PERIODIC: interval=+1d0h0m0s0ms flex=+2h0m0s0ms'))
        self.assertEqual((sync.priority, sync.last_success), ('300 [DEFAULT]', '1970-01-01 00:00:00'))
        self.assertEqual((plain.requires, plain.package), ('charging=false batteryNotLow=false deviceIdle=true', 'android'))
        self.assertEqual((work.namespace, work.user, work.job_id, work.restricted), (
            'androidx.work.systemjobscheduler', 10, -4, 'background restricted.'))
        done = jobs[len(fixture.JOBS):]
        self.assertEqual([(job.completed, job.package, job.job_id, job.bucket) for job in done],
                         [('-38s227ms', 'com.example.user.chat', 11, 'ACTIVE'),
                          ('-50m12s500ms', 'com.example.user.notes', 8802, 'FREQUENT')])
        self.assertEqual(done[1].namespace, 'androidx.work.systemjobscheduler')
        self.assertEqual(done[1].ready, '')
        self.assertEqual(report.warnings, [])

    def test_android_10_layout(self):
        report = scan_text(fixture.build_report('a10'))
        self.assertEqual([job.listing for job in usagejobs.table(report, 'uj_jobs')], ['Registered', 'Registered'])
        self.assertEqual({job.namespace for job in usagejobs.table(report, 'uj_jobs')}, {''})
        self.assertEqual({job.restricted for job in usagejobs.table(report, 'uj_jobs')}, {''})
        self.assertEqual(usagejobs.table(report, 'uj_jobs')[0].job_id, 11)

    def test_entry_count_mismatch_is_warned_about(self):
        text = fixture.build_report('a16').replace('Registered 4 jobs:', 'Registered 9 jobs:')
        self.assertTrue([w for w in scan_text(text).warnings if 'the dump says 9 registered jobs, 4 were read' in w])

    def test_long_extras_are_cut(self):
        body = ('Registered 1 jobs:\n  JOB #u0a1/5: abc123 com.example/.J\n    1000 tag=*job*/com.example/.J\n'
                '    Source: uid=u0a1 user=0 pkg=com.example\n    JobInfo:\n      Service: com.example/.J\n'
                '      Extras: ' + 'x' * 5000 + '\n')
        job = usagejobs.table(scan_text(service_text('jobscheduler', body)), 'uj_jobs')[0]
        self.assertEqual(len(job.extras), usagejobs.MAX_TEXT)

    def test_cut_dump_is_marked(self):
        report = scan_text(fixture.build_report('a16', cut=True))
        section = [s for s in report.sections if s.name == 'jobscheduler'][0]
        self.assertEqual(section.timeout_ms, 10000)
        self.assertEqual(usagejobs.table(report, 'uj_jobs'), [])


class AlarmTests(unittest.TestCase):
    def test_pending_alarms_android_16(self):
        report = scan_text(fixture.build_report('a16'))
        alarms = [row for row in usagejobs.table(report, 'uj_alarms') if row.listing == 'Pending alarms']
        self.assertEqual(usagejobs.anchor(report), (fixture.NOW_MS, fixture.wall_at(0, True)))
        self.assertEqual([(a.alarm_type, a.package, a.index) for a in alarms],
                         [('ELAPSED', 'android', 1), ('ELAPSED_WAKEUP', 'com.example.user.chat', 2), ('RTC_WAKEUP', 'com.example.user.clock', 3)])
        first, second, third = alarms
        self.assertEqual((first.tag, first.when, first.max_when, first.window, first.repeat, first.count, first.flags, first.exact_reason),
                         ('*alarm*:TIME_TICK', '+39s940ms', '+39s940ms', '0', '0', 0, '0x9', 'allow-listed'))
        self.assertEqual(first.listener, 'com.android.server.alarm.Demo$2@6f0c1d4')
        self.assertEqual(second.tag, '*walarm*:com.example.user.chat.action.SYNC TICK')                      # a tag with a space
        self.assertEqual((second.window, second.repeat), ('+22m30s0ms', '1800000'))
        self.assertTrue(second.operation.startswith('PendingIntent{3c1a2b9'))
        self.assertEqual(third.orig_when, '2026-11-02 15:48:40.000')
        self.assertEqual(first.anchor_ms, fixture.NOW_MS)
        self.assertEqual(usagejobs.duration_ms(second.when), 600500)

    def test_alarm_with_an_original_type_is_read(self):
        report = scan_text(fixture.build_report('a16'))
        self.assertIn(2, [a.index for a in usagejobs.table(report, 'uj_alarms') if a.listing == 'Pending alarms'])

    def test_next_alarm_clock(self):
        report = scan_text(fixture.build_report('a16'))
        clock = [row for row in usagejobs.table(report, 'uj_alarms') if row.listing == 'Next alarm clock']
        self.assertEqual(len(clock), 1)
        self.assertEqual((clock[0].clock_ms, clock[0].when, clock[0].clock_text, clock[0].alarm_type),
                         (fixture.ms_at(20000), str(fixture.ms_at(20000)), fixture.wall_at(20000, True), 'user 0'))
        self.assertEqual(usagejobs.table(scan_text(fixture.build_report('a10')), 'uj_alarms')[0].listing, 'Pending alarms')

    def test_android_10_batches(self):
        report = scan_text(fixture.build_report('a10'))
        self.assertEqual([(a.batch, a.index, a.alarm_type, a.when) for a in usagejobs.table(report, 'uj_alarms')],
                         [('7a1b3c0', 0, 'ELAPSED', '+39s940ms'), ('7a1b3c1', 1, 'ELAPSED_WAKEUP', '+10m0s500ms'),
                          ('7a1b3c2', 2, 'RTC_WAKEUP', '+5h33m20s0ms')])
        self.assertEqual(usagejobs.table(report, 'uj_alarms')[1].max_when, '+40m0s250ms')
        self.assertEqual(usagejobs.table(report, 'uj_alarms')[0].window, '0')

    def test_histories_android_16(self):
        report = scan_text(fixture.build_report('a16'))
        history = usagejobs.table(report, 'uj_alarm_history')
        by_list = {}
        for row in history:
            by_list.setdefault(row.history, []).append(row)
        self.assertEqual({key: len(rows) for key, rows in by_list.items()},
                         {'App alarm history': 5, 'Allow while idle': 1, 'Removal': 3, 'Addition': 2, 'Delivery': 1,
                          'Wakeup (screen off)': 2})
        removal = by_list['Removal']
        self.assertEqual((removal[0].uid_label, removal[0].alarm_type, removal[0].tag, removal[0].reason, removal[0].user),
                         ('1000', 'ELAPSED_WAKEUP', '*walarm*:Demo Scan Timeout', 'alarm_cancelled', 0))
        self.assertEqual((removal[0].rtc_text, removal[0].offset), (fixture.wall_at(-178.016, True), '-2m58s16ms'))
        self.assertEqual((removal[2].uid_label, removal[2].reason), ('u0a300', 'alarm_expired'))
        addition = by_list['Addition']
        self.assertEqual(addition[0].tag, '*walarm*:Demo Added Alarm')
        self.assertTrue(addition[0].detail.startswith('T=2 F=0 AC=false H=L:b6c7d80 OW='))
        self.assertNotIn('rtc=', addition[0].detail)
        self.assertEqual(addition[1].tag, '*alarm*:com.example.user.chat.action.SYNC')
        self.assertEqual(by_list['Delivery'][0].tag, '*alarm*:TIME_TICK')
        app = by_list['App alarm history']
        self.assertEqual([(row.package, row.user, row.offset) for row in app],
                         [('com.example.user.chat', 0, '-6m12s603ms'), ('com.example.user.chat', 0, '-12m36s636ms'),
                          ('com.example.user.chat', 0, '-16m48s707ms'), ('com.example.user.clock', 0, '-1h13m20s0ms'),
                          ('com.example.user.chat', 10, '-30s500ms')])
        self.assertEqual([row.user for row in by_list['Wakeup (screen off)']], [0, 0])
        self.assertEqual(by_list['Wakeup (screen off)'][0].uid_label, '10077')

    def test_android_10_has_only_the_per_app_history(self):
        history = usagejobs.table(scan_text(fixture.build_report('a10')), 'uj_alarm_history')
        self.assertEqual({row.history for row in history}, {'App alarm history'})
        self.assertEqual(len(history), 5)

    def test_expiration_and_stats_lists_are_not_rows(self):
        report = scan_text(fixture.build_report('a16'))
        self.assertFalse([row for row in usagejobs.table(report, 'uj_alarm_history') if row.history.startswith(('Expiration', 'Top', 'Alarm'))])
        self.assertEqual(len([row for row in usagejobs.table(report, 'uj_alarms') if row.listing == 'Pending alarms']), len(fixture.ALARMS))

    def test_a_dump_without_nowrtc_has_no_anchor(self):
        text = fixture.build_report('a16').replace('nowRTC=', 'nowXYZ=')
        report = scan_text(text)
        self.assertIsNone(usagejobs.table(report, 'uj_alarms')[0].anchor_ms)


class NotificationTests(unittest.TestCase):
    def test_records_android_16(self):
        report = scan_text(fixture.build_report('a16'))
        records = [row for row in usagejobs.table(report, 'uj_notifications') if row.listing == 'Notification list']
        self.assertEqual([(r.package, r.user, r.uid, r.notification_id) for r in records],
                         [('com.example.user.chat', 0, 10300, 23), ('com.example.user.chat', 0, 10300, 1), ('android', -1, 1000, 45)])
        first, split, system = records
        self.assertEqual((first.tag, first.channel, first.importance, first.importance_note, first.flags, first.category),
                         ('null', 'chat_messages', 4, 'app', 'ONLY_ALERT_ONCE|AUTO_CANCEL', 'msg'))
        self.assertEqual((first.ticker, first.seen, first.group_key), ('Demo me...', 'true', '0|com.example.user.chat|g'))
        created = fixture.ms_at(-3000)
        self.assertEqual(first.created, '%d(%s+0000)' % (created, datetime.fromtimestamp(created / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
        self.assertEqual(split.tag, 'tagwith=')                          # the line break that ends the tag is dropped with the white space
        self.assertEqual((split.notification_id, split.importance, split.ticker), (1, 3, 'sent yo...'))
        self.assertEqual(split.key, '0|com.example.user.chat|1|tagwith=|10300')
        self.assertEqual(system.channel, 'NETWORK_ALERTS')

    def test_android_10_times_are_plain_numbers(self):
        report = scan_text(fixture.build_report('a10'))
        first = [row for row in usagejobs.table(report, 'uj_notifications') if row.listing == 'Notification list'][0]
        self.assertEqual(first.created, str(fixture.ms_at(-3000)))
        self.assertEqual(first.flags, '0x3a')
        self.assertEqual(first.ticker, 'Demo me...')

    def test_records_survive_odd_bytes(self):
        text = fixture.build_report('a16').replace('Demo me...', 'Demo\rme\x0c...')
        record = [row for row in usagejobs.table(scan_text(text), 'uj_notifications') if row.listing == 'Notification list'][0]
        self.assertEqual(record.ticker, 'Demo me ...')

    def test_archive_and_its_total(self):
        report = scan_text(fixture.build_report('a16'))
        archive = [row for row in usagejobs.table(report, 'uj_notifications') if row.listing == 'Archive']
        self.assertEqual([(r.package, r.notification_id, r.channel, r.flags) for r in archive],
                         [('com.example.user.chat', 41, 'chat_messages', 'ONLY_ALERT_ONCE'),
                          ('android', 40, 'FOREGROUND_SERVICE', 'FOREGROUND_SERVICE'),
                          ('com.example.user.chat', 1, 'chat_messages', 'AUTO_CANCEL')])
        self.assertEqual((archive[0].created, archive[0].uid, archive[0].importance), ('', None, None))
        self.assertEqual((archive[2].tag, archive[2].key), ('Zm9vYmFy=', '0|com.example.user.chat|1|Zm9vYmFy= |10300'))
        counts = usagejobs.counts(report)
        totals = [key for key in counts if key[0] == 'archive_total']
        self.assertEqual(len(totals), 1)
        self.assertEqual((counts[totals[0]], counts[('archive_listed', totals[0][1])]), (78, 3))
        self.assertIn(('archive_cut', totals[0][1]), counts)

    def test_snoozed_listeners_without_a_user_heading(self):
        report = scan_text(fixture.build_report('a10'))
        snoozed = [row for row in usagejobs.table(report, 'uj_listeners') if row.listing == 'Snoozed']
        self.assertEqual([(row.component, row.user, row.detail) for row in snoozed],
                         [('com.example.user.chat/com.example.user.chat.Listener', None, '')])
        self.assertEqual(len(usagejobs.table(report, 'uj_listeners')), 10)

    def test_listeners(self):
        report = scan_text(fixture.build_report('a16'))
        rows = [(r.role, r.listing, r.component, r.package, r.user, r.detail) for r in usagejobs.table(report, 'uj_listeners')]
        self.assertIn(('Listener', 'Allowed', 'com.example.user.chat/com.example.user.chat.Listener', 'com.example.user.chat', 0, 'isPrimary: true'), rows)
        self.assertIn(('Listener', 'Allowed', 'com.example.launcher/com.example.launcher.NotificationListener', 'com.example.launcher', 0,
                       'isPrimary: true'), rows)
        self.assertIn(('Listener', 'Enabled for current profiles', 'com.example.launcher/com.example.launcher.NotificationListener',
                       'com.example.launcher', None, ''), rows)
        self.assertIn(('Listener', 'Live', 'android/com.android.server.Demo$NotificationListener', 'android', -1, 'SYSTEM'), rows)
        self.assertIn(('Listener', 'Live', 'com.example.launcher/com.example.launcher.NotificationListener', 'com.example.launcher', 0, ''), rows)
        self.assertIn(('Listener', 'Live', 'com.example.guest/com.example.guest.Assistant', 'com.example.guest', 10, 'GUEST'), rows)
        self.assertIn(('Listener', 'Snoozed', 'com.example.user.chat/com.example.user.chat.Listener', 'com.example.user.chat', 0,
                       '(META_DATA_DEFAULT_AUTOBIND=false)'), rows)
        self.assertIn(('Assistant', 'Allowed', 'com.example.guest/com.example.guest.Assistant', 'com.example.guest', 0,
                       'isPrimary: true isUserChanged: false'), rows)
        self.assertIn(('Assistant', 'Enabled for current profiles', 'com.example.guest/com.example.guest.Assistant',
                       'com.example.guest', None, ''), rows)
        self.assertEqual(len(rows), 10)

    def test_channels(self):
        report = scan_text(fixture.build_report('a16'))
        rows = usagejobs.table(report, 'uj_channels')
        self.assertEqual(len(rows), 4)
        chat, old, silent, system = rows
        self.assertEqual((chat.package, chat.uid, chat.app_settings, chat.channel_id, chat.name, chat.importance, chat.deleted, chat.deleted_ms),
                         ('com.example.user.chat', 10300, 'importance=DEFAULT userSet=true', 'chat_messages', 'Mes...', '4', 'false', '-1'))
        self.assertEqual((chat.sound, chat.lights, chat.badge, chat.vibration, chat.group, chat.locked_fields),
                         ('content://settings/system/notification_sound', 'true', 'true', 'false', 'null', '0'))
        self.assertEqual((old.channel_id, old.deleted, old.deleted_ms, old.group, old.bypass_dnd), ('chat_old', 'true', '1792000000000', 'old_group', 'false'))
        self.assertEqual((silent.package, silent.channel_id, silent.app_settings), ('com.example.user.silent', '', 'importance=NONE userSet=false'))
        self.assertEqual((system.package, system.uid, system.channel_id), ('android', 1000, 'NETWORK_ALERTS'))
        self.assertFalse([row for row in rows if row.package == 'com.example.user.plain'])      # no settings and no channel: nothing to list

    def test_channel_field_reader_on_odd_text(self):
        fields = usagejobs.channel_fields("NotificationChannel{mId='a, b', mName=N..., mDescription=, mImportance=3, mGroup='x'}")
        self.assertEqual((fields['mId'], fields['mName'], fields['mImportance'], fields['mGroup']), ('a, b', 'N...', '3', 'x'))
        self.assertEqual(usagejobs.channel_fields('NotificationChannel{}'), {})

    def test_unreadable_header_is_warned_about(self):
        body = '  Notification List:\n    NotificationRecord(0x1: broken header\n      uid=1 userId=0\n'
        report = scan_text(service_text('notification', body))
        self.assertEqual(usagejobs.table(report, 'uj_notifications'), [])
        self.assertTrue([w for w in report.warnings if 'unreadable record header' in w])


class BoundedAndOddTextTests(unittest.TestCase):
    def test_row_cap_is_reported(self):
        with mock.patch.object(reader, 'MAX_ROWS', 3):
            report = scan_text(fixture.build_report('a16'))
        self.assertEqual(len(usagejobs.table(report, 'uj_standby')), 3)
        self.assertTrue([w for w in report.warnings if 'uj_standby: more than 3 rows' in w])

    def test_sections_without_rows(self):
        for name in ('jobscheduler', 'alarm', 'notification', 'usagestats'):
            report = scan_text(service_text(name, '  nothing here\n'))
            for table in ('uj_intervals', 'uj_standby', 'uj_jobs', 'uj_alarms', 'uj_alarm_history', 'uj_notifications',
                          'uj_listeners', 'uj_channels'):
                self.assertEqual(getattr(report, table), [], (name, table))

    def test_random_lines_do_not_stop_the_pass(self):
        rng = random.Random(1234)
        pieces = ['  ', '    ', '      ', 'package=', 'user=', 'JOB #', 'Alarm{', 'NotificationRecord(', 'StatusBarNotification(',
                  'AppSettings: ', 'NotificationChannel{', 'ELAPSED #1: ', 'Batch{', '(user: ', 'ComponentInfo{', '[tag=', 'rtc=',
                  'In-memory daily stats', 'App Standby States:', 'Registered 3 jobs:', 'Recently completed jobs:',
                  'mArchive=Archive (', 'Notification List:', '\x00', '\xe9', '=', ':', '"', '}', ')']
        for name in ('usagestats', 'jobscheduler', 'alarm', 'notification'):
            lines = []
            for _ in range(400):
                lines.append(''.join(rng.choice(pieces) for _ in range(rng.randint(1, 6))))
            scan_text(service_text(name, '\n'.join(lines) + '\n'))
            scan_text(('== dumpstate: x\n\n------ CHECKIN USAGESTATS (/system/bin/dumpsys -T 30000 usagestats -c) ------\n'
                       + '\n'.join(lines) + '\n'))

    def test_a_very_long_line_is_cut(self):
        body = '  Notification List:\n    NotificationRecord(0x1: pkg=a user=UserHandle{0} id=1 tag=' + 't' * 90000 + \
               ' importance=2 key=k: Notification(channel=c))\n      uid=1 userId=0\n'
        report = scan_text(service_text('notification', body))
        self.assertLessEqual(len(report.warnings), 1)

    def test_entries_that_never_end_are_bounded(self):
        archive = ('  mArchive=Archive (1 notifications)\n    StatusBarNotification(pkg=a user=UserHandle{0} id=1 tag=x\n'
                   + ' continuation line without an end\n' * 5000)
        report = scan_text(service_text('notification', archive))
        self.assertEqual(usagejobs.table(report, 'uj_notifications'), [])
        self.assertTrue([w for w in report.warnings if 'unreadable archive entry' in w])
        header = '  Notification List:\n    NotificationRecord(0x1: pkg=a user=UserHandle{0} id=1 tag=x\n' + 'y\n' * 20000
        self.assertTrue([w for w in scan_text(service_text('notification', header)).warnings if 'unreadable record header' in w])
        lines = ['  Pending alarm batches: 1', 'Batch{abc num=1 start=1 end=1}:',
                 '    ELAPSED #0: Alarm{abc type 3 when 1 android}'] + ['      key%d=v' % number for number in range(1000)]
        alarm = usagejobs.table(scan_text(service_text('alarm', 'Current Alarm Manager state:\n' + '\n'.join(lines) + '\n')), 'uj_alarms')
        self.assertEqual(len(alarm), 1)

    def test_pass_stays_single(self):
        reads = []
        original = reader.iter_lines
        with mock.patch.object(reader, 'iter_lines', side_effect=lambda stream: reads.append(1) or original(stream)):
            scan_text(fixture.build_report('a16'))
        self.assertEqual(len(reads), 1)


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

    FUNCTIONS = (artifacts.bugreport_usage_intervals, artifacts.bugreport_usage_interval_events, artifacts.bugreport_standby_buckets,
                 artifacts.bugreport_scheduled_jobs, artifacts.bugreport_pending_alarms, artifacts.bugreport_alarm_history,
                 artifacts.bugreport_notification_records, artifacts.bugreport_notification_listeners,
                 artifacts.bugreport_notification_channels)

    def test_row_width_matches_the_headers_for_both_layouts(self):
        for layout in ('a16', 'a10'):
            reader.clear_cache()
            path = self.stage('Dump/dumpstate_%s.txt' % layout, fixture.build_report(layout))
            for function in self.FUNCTIONS:
                headers, rows, source_path = self.run_artifact(function, path)
                self.assertTrue(rows, (layout, function.__name__))
                self.assertTrue(all(len(row) == len(headers) for row in rows))
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

    def test_the_existing_artifacts_still_see_their_rows(self):
        from scripts.artifacts import bugreportActivity  # pylint: disable=import-outside-toplevel
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        rows = self.run_artifact(bugreportActivity.bugreport_usage_events, path)[1]
        self.assertEqual(len(rows), len(base.USAGE_EVENTS) + 1)

    def test_usage_interval_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_usage_intervals, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        row = [r for r in rows if r[names.index('User')] == 0 and r[names.index('Interval')] == 'daily'][0]
        self.assertEqual(row[names.index('Package')], 'com.example.user.chat')
        self.assertEqual(row[names.index('Last Time Used (UTC)')], utc(2026, 11, 2, 9, 5, 20))
        self.assertEqual(row[names.index('Interval Begin (UTC)')], utc(2026, 11, 1, 22, 8, 40))
        self.assertEqual(row[names.index('Total Time Used (ms)')], 80000)
        self.assertEqual(row[names.index('App Launch Count')], 3)
        self.assertEqual(row[names.index('Time Note')], '')
        component_only = [r for r in rows if r[names.index('Package')] == 'com.example.user.service'][0]
        self.assertIsNone(component_only[names.index('Last Time Used (UTC)')])
        self.assertEqual(component_only[names.index('Last Time Used As Printed')], '0')
        self.assertEqual(component_only[names.index('Last Time Component Used (UTC)')], utc(2026, 11, 2, 7, 15, 20))
        self.assertEqual(len(rows), 24)

    def test_service_form_wall_clock_uses_the_zone_and_notes_a_missing_one(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a10', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_usage_intervals, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        plain = [r for r in rows if r[names.index('Source Section')].startswith('DUMP')][0]
        self.assertEqual(plain[names.index('Last Time Used (UTC)')], utc(2026, 11, 2, 9, 5, 20))
        self.assertEqual(plain[names.index('Total Time Used (ms)')], 80000)
        self.assertEqual(plain[names.index('Interval As Printed')], '11/01/2026, 21:00 \u2013 11/02/2026, 10:15')
        reader.clear_cache()
        path = self.stage('Dump/dumpstate_nozone.txt', fixture.build_report('a10', zone=''))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_usage_intervals, path)
        service = [r for r in rows if r[names.index('Source Section')].startswith('DUMP')]
        checkin = [r for r in rows if r[names.index('Source Section')] == 'CHECKIN USAGESTATS']
        self.assertTrue(all(r[names.index('Last Time Used (UTC)')] is None for r in service))
        self.assertEqual({r[names.index('Time Note')] for r in service}, {reader.NOTE_NO_ZONE})
        self.assertEqual(checkin[0][names.index('Last Time Used (UTC)')], utc(2026, 11, 2, 9, 5, 20))      # epoch milliseconds need no zone
        self.assertEqual({r[names.index('Time Note')] for r in checkin}, {''})

    def test_event_count_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_usage_interval_events, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        row = rows[0]
        self.assertEqual((row[names.index('Event')], row[names.index('Count')], row[names.index('Total Time (ms)')]),
                         ('screen-interactive', 12, 150000))
        self.assertEqual(row[names.index('Interval End (UTC)')], utc(2026, 11, 2, 9, 15, 20))

    def test_standby_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_standby_buckets, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        self.assertEqual([r[names.index('Bucket Name')] for r in rows if r[names.index('User')] == 0],
                         ['ACTIVE', 'NEVER', 'EXEMPTED', 'RARE'])
        self.assertEqual(artifacts.BUCKET_NAMES['20'], 'WORKING_SET')
        unknown = scan_text(fixture.build_report('a16').replace('bucket=10 reason=u-si', 'bucket=33 reason=u-si', 1))
        self.assertEqual(usagejobs.table(unknown, 'uj_standby')[0].bucket, '33')

    def test_job_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_scheduled_jobs, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        chat = rows[0]
        self.assertEqual(chat[names.index('Last Successful Run (UTC)')], utc(2026, 11, 2, 7, 30, 0))
        self.assertEqual(chat[names.index('Last Successful Run As Printed')], '2026-11-02 08:30:00')
        self.assertEqual(chat[names.index('Last Failed Run (UTC)')], utc(2026, 10, 30, 0, 2, 3))
        sync = rows[1]
        self.assertIsNone(sync[names.index('Last Successful Run (UTC)')])
        self.assertEqual(sync[names.index('Time Note')], reader.NOTE_UNSET)
        self.assertEqual(len(rows), 6)
        reader.clear_cache()
        path = self.stage('Dump/dumpstate_nozone.txt', fixture.build_report('a16', zone=''))
        rows = self.run_artifact(artifacts.bugreport_scheduled_jobs, path)[1]
        self.assertEqual(rows[0][names.index('Time Note')], reader.NOTE_NO_ZONE)
        self.assertIsNone(rows[0][names.index('Last Successful Run (UTC)')])

    def test_pending_alarm_times_come_from_the_anchor_not_the_zone(self):
        for zone in ('Europe/Paris', 'Asia/Kolkata', ''):
            reader.clear_cache()
            path = self.stage('Dump/dumpstate_%s.txt' % (zone.replace('/', '_') or 'none'), fixture.build_report('a16', zone=zone))
            headers, rows, _source = self.run_artifact(artifacts.bugreport_pending_alarms, path)
            names = [h if isinstance(h, str) else h[0] for h in headers]
            pending = [r for r in rows if r[names.index('List')] == 'Pending alarms']
            self.assertEqual(pending[0][names.index('Trigger Time (UTC)')], utc(2026, 11, 2, 9, 15, 59, 940000), zone)
            self.assertEqual(pending[0][names.index('Time Note')], '')
            self.assertEqual(pending[1][names.index('Latest Trigger Time (UTC)')], utc(2026, 11, 2, 9, 55, 20, 250000))
            clock = [r for r in rows if r[names.index('List')] == 'Next alarm clock'][0]
            self.assertEqual(clock[names.index('Trigger Time (UTC)')], utc(2026, 11, 2, 14, 48, 40))
            self.assertIn(fixture.wall_at(20000, True), clock[names.index('Trigger As Printed')])

    def test_pending_alarm_without_an_anchor_is_noted(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16').replace('nowRTC=', 'nowXYZ='))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_pending_alarms, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        pending = [r for r in rows if r[names.index('List')] == 'Pending alarms']
        self.assertIsNone(pending[0][names.index('Trigger Time (UTC)')])
        self.assertEqual(pending[0][names.index('Time Note')], artifacts.NOTE_NO_ANCHOR)

    def test_alarm_history_times(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_alarm_history, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        removal = [r for r in rows if r[names.index('History')] == 'Removal'][0]
        self.assertEqual(removal[names.index('Time (UTC)')], utc(2026, 11, 2, 9, 12, 21, 984000))
        per_app = [r for r in rows if r[names.index('History')] == 'App alarm history'][0]
        self.assertEqual(per_app[names.index('Time (UTC)')], utc(2026, 11, 2, 9, 9, 7, 397000))
        self.assertEqual(per_app[names.index('Time As Printed')], '')
        reader.clear_cache()
        path = self.stage('Dump/dumpstate_nozone.txt', fixture.build_report('a16', zone=''))
        rows = self.run_artifact(artifacts.bugreport_alarm_history, path)[1]
        removal = [r for r in rows if r[names.index('History')] == 'Removal'][0]
        self.assertEqual(removal[names.index('Time (UTC)')], utc(2026, 11, 2, 9, 12, 21, 984000))      # from nowRTC plus the offset

    def test_notification_record_times(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_notification_records, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        first = rows[0]
        self.assertEqual(first[names.index('Created (UTC)')], utc(2026, 11, 2, 8, 25, 20))
        self.assertEqual(first[names.index('Updated (UTC)')], utc(2026, 11, 2, 8, 26, 20))
        self.assertEqual(first[names.index('Visible Since (UTC)')], utc(2026, 11, 2, 8, 25, 25))
        archive = [r for r in rows if r[names.index('List')] == 'Archive']
        self.assertEqual(len(archive), 3)
        self.assertIsNone(archive[0][names.index('Created (UTC)')])

    def test_channel_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_notification_channels, path)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        old = [r for r in rows if r[names.index('Channel ID')] == 'chat_old'][0]
        self.assertEqual(old[names.index('Deleted Time (UTC)')], utc(2026, 10, 14, 17, 46, 40))
        self.assertEqual(old[names.index('User')], 0)
        chat = [r for r in rows if r[names.index('Channel ID')] == 'chat_messages'][0]
        self.assertIsNone(chat[names.index('Deleted Time (UTC)')])
        self.assertEqual(chat[names.index('Deleted Time As Printed')], '-1')

    def test_dumps_cut_by_the_platform_are_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_scheduled_jobs, path)
            self.run_artifact(artifacts.bugreport_pending_alarms, path)
            self.run_artifact(artifacts.bugreport_alarm_history, path)
            self.run_artifact(artifacts.bugreport_notification_records, path)
            self.run_artifact(artifacts.bugreport_notification_listeners, path)
            self.run_artifact(artifacts.bugreport_usage_intervals, path)
            self.run_artifact(artifacts.bugreport_usage_interval_events, path)
        for service in ('jobscheduler', 'alarm', 'notification'):
            cut = [m for m in messages if 'the %s service dump was cut by a 10000 ms timeout' % service in m]
            self.assertEqual(len(cut), 1, service)
        self.assertEqual(len([m for m in messages if 'CHECKIN USAGESTATS output carries a dump timeout marker' in m]), 1)

    def test_partial_archive_is_logged_with_its_total(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_notification_records, path)
        self.assertTrue([m for m in messages if 'the notification archive holds 78 notifications and the dump lists 3' in m])

    def test_unlisted_interval_rows_are_logged(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a10'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_usage_intervals, path)
        self.assertEqual(len([m for m in messages if 'were counted and not listed' in m]), 2)       # one per section

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10'))
        for function in self.FUNCTIONS:
            reader.clear_cache()
            alone = len(self.run_artifact(function, first)[1])
            both = self.run_artifact(function, first, second)[1]
            self.assertGreater(len(both), alone, function.__name__)
            self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})

    def test_artifacts_do_not_read_the_evidence_for_writing(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        before = (path.read_bytes(), path.stat().st_mtime_ns)
        for function in self.FUNCTIONS:
            self.run_artifact(function, path)
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)


if __name__ == '__main__':
    unittest.main()
