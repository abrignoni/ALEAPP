"""Builds the synthetic Android bug report texts used by the usage statistics, job scheduler, alarm and
notification test cases of the Android Bug Report artifacts.

Every value is invented: package names are under example.*, accounts, tags, channel ids and times are made up,
the user ids are fixed. Only the structure is taken from real bug reports: the section headers and trailers the
platform prints and the line layout of the usagestats, jobscheduler, alarm and notification dumps. Two layouts:

* ``a16``: the layout of Android 14 and later (usage statistics in the CHECKIN USAGESTATS command section as epoch
  milliseconds and ``User N App Standby States``; jobs with a namespace and a recently completed list; ``N pending
  alarms`` with removal, addition, delivery and wakeup histories; notification channels with a deletion time);
* ``a10``: the layout of Android 10 (usage statistics in the dumpsys service as formatted wall-clock text and an
  indented ``App Standby States``; jobs without a namespace; alarm batches; no histories but the app alarm history).

Usage: python bugreport_usagejobs_fixture.py <output folder>
Writes one zip per test case into the folder, each holding a synthetic extraction (files under a ``Dump`` folder).
"""
import os
import sys
from datetime import datetime, timedelta, timezone

from admin.test.scripts import bugreport_fixture as base

NOW_UTC = '2026-11-02 09:15:20'        # the moment the services are dumped, UTC
NOW_PARIS = '2026-11-02 10:15:20'      # the same moment on the device wall clock (Europe/Paris, UTC+1)
NOW_MS = base.epoch_ms(NOW_UTC)
NOW_ELAPSED = 5000000


def ms_at(offset_seconds):
    """Epoch milliseconds of the dump moment plus an offset in seconds."""
    return NOW_MS + int(offset_seconds * 1000)


def wall_at(offset_seconds, with_millis=False):
    """The device (Paris) wall-clock text of the dump moment plus an offset in seconds."""
    moment = datetime.strptime(NOW_PARIS, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=offset_seconds)
    return moment.strftime('%Y-%m-%d %H:%M:%S') + ('.%03d' % (moment.microsecond // 1000) if with_millis else '')


def duration(seconds):
    """A duration the way the dumps print it: ``+1h2m3s0ms`` or ``-4m5s6ms`` (milliseconds kept)."""
    sign = '-' if seconds < 0 else '+'
    total = abs(int(round(seconds * 1000)))
    millis = total % 1000
    total //= 1000
    secs = total % 60
    total //= 60
    mins = total % 60
    total //= 60
    hours = total % 24
    days = total // 24
    text = ''
    if days:
        text += '%dd' % days
    if days or hours:
        text += '%dh' % hours
    if days or hours or mins:
        text += '%dm' % mins
    return '%s%s%ds%dms' % (sign, text, secs, millis)


# ------------------------------------------------------------------------------------------
# usagestats
# ------------------------------------------------------------------------------------------
# package, total used (s), last used (s from the dump), total visible (s), last visible, last component, launches
INTERVAL_PACKAGES = (
    ('com.example.user.chat', 80, -600, 83, -600, -1200, 3),
    ('com.example.user.idle', 0, None, 0, None, None, 0),
    ('com.example.user.service', 0, None, 0, None, -7200, 0),
    ('com.example.user.video', 3725, -86000, 3700, -86000, None, 11),
)
# package, bucket, reason, used, used by user, used screen, last predicted, expiry, last job, informed, next launch, idle
STANDBY = (
    ('com.example.user.chat', 10, 'u-si', '+1m5s0ms', '+1m5s0ms', '+3d0h0m0s0ms', '+0ms', '(10:+1h0m0s0ms,20:+1d0h0m0s0ms)',
     '-1d0h0m0s0ms', 10, '+2d1h0m0s0ms', 'n'),
    ('com.example.user.idle', 50, 't', '<uninitialized>', '<uninitialized>', '<uninitialized>', '<uninitialized>', '<none>',
     '-24855d3h14m7s500ms', 50, '', 'y'),
    ('com.example.user.service', 5, 'd', '<uninitialized>', '<uninitialized>', '<uninitialized>', '<uninitialized>', '<none>',
     '+4h0m0s0ms', 5, '', 'n'),
    ('com.example.user.video', 40, 'p', '+10d0h0m0s0ms', '+10d0h0m0s0ms', '+12d0h0m0s0ms', '+9d0h0m0s0ms', '<none>',
     '+1d0h0m0s0ms', 40, '', 'n'),
)
EVENT_AGGREGATIONS = (('screen-interactive', 12, 150000, True), ('screen-non-interactive', 12, 230000, False),
                      ('keyguard-shown', 5, 1000, False), ('keyguard-hidden', 5, 61000, True))


def clock_text(milliseconds):
    seconds = milliseconds // 1000
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return '%d:%02d:%02d' % (hours, minutes, secs) if hours else '%02d:%02d' % (minutes, secs)


def _interval_lines(form, interval):
    """The text of one In-memory ... stats block."""
    begin = ms_at(-40000 if interval == 'daily' else -400000)
    end = ms_at(0)
    lines = ['  In-memory %s stats' % interval]
    if form == 'checkin':
        lines.append('  beginTime=%d endTime=%d ' % (begin, end))
    else:
        lines.append('  timeRange="11/01/2026, 21:00 – 11/02/2026, 10:15" ')
    lines.append('    packages')
    for package, used, last_used, visible, last_visible, last_component, launches in INTERVAL_PACKAGES:
        def point(offset):
            if form == 'checkin':
                return str(ms_at(offset)) if offset is not None else '0'
            return '"%s"' % wall_at(offset) if offset is not None else '"1970-01-01 00:00:00"'

        def span(seconds):
            if form == 'checkin':
                return str(seconds * 1000)
            return '"%s"' % clock_text(seconds * 1000)
        lines.append('      package=%s totalTimeUsed=%s lastTimeUsed=%s totalTimeVisible=%s lastTimeVisible=%s '
                     'lastTimeComponentUsed=%s totalTimeFS=%s lastTimeFS=%s appLaunchCount=%d '
                     % (package, span(used), point(last_used), span(visible), point(last_visible), point(last_component),
                        span(0), point(None), launches))
    lines += ['    ', '    ChooserCounts', '      ', '    configurations',
              '      config=en-rUS-ldltr-sw360dp-w360dp-h740dp-normal-long-notround-port-v29 totalTime=1000 lastTime=%d count=1 '
              % ms_at(-100)]
    lines.append('    event aggregations')
    for name, number, milliseconds, running in EVENT_AGGREGATIONS:
        shown = str(milliseconds) if form == 'checkin' else '"%s"' % clock_text(milliseconds)
        lines.append('      %s: %dx for %s%s' % (name, number, shown, ' (now running, started at )' if running else ''))
    return lines


def _standby_lines(layout, user):
    indent = '    ' if layout == 'a10' else '  '
    lines = []
    for package, bucket, reason, used, used_user, used_scr, predicted, expiry, last_job, informed, launch, idle in STANDBY:
        text = ('%spackage=%s u=%d bucket=%d reason=%s used=%s usedByUser=%s usedScr=%s lastPred=%s expiryTimes=%s lastJob=%s'
                % (indent, package, user, bucket, reason, used, used_user, used_scr, predicted, expiry, last_job))
        if layout == 'a10':
            text = ('%spackage=%s u=%d bucket=%d reason=%s used=%s usedScr=%s lastPred=%s activeLeft=-386d10h41m19s637ms '
                    'wsLeft=-386d10h41m19s637ms lastJob=%s idle=%s' % (indent, package, user, bucket, reason, used, used_scr,
                                                                       predicted, last_job, idle))
        else:
            text += ' lastInformedBucket=%d' % informed
            if launch:
                text += ' nextEstimatedLaunchTime=%s' % launch
            text += ' idle=%s' % idle
        lines.append(text)
    return lines


def usagestats_body(layout, form, users, events):
    """The body shared by the usagestats service (``service`` form) and the CHECKIN USAGESTATS command (``checkin`` form).

    ``layout`` decides where the standby states are printed: indented under each user on Android 10 (in both forms) and
    under their own ``User N App Standby States`` heading on Android 14 and later.
    """
    lines = []
    for user in users:
        lines.append('user=%d ' % user)
        if form == 'service':
            lines.append('  Last 24 hour events (timeRange="11/01/2026, 21:00 – 11/02/2026, 10:15" )')
        else:
            lines.append('  Last 24 hour events (beginTime=%d endTime=%d )' % (ms_at(-86400), ms_at(0)))
        for event in events if user == 0 else events[:1]:
            lines.append(event)
        if form == 'checkin':
            lines.append('  mDumpInitLastTimeSaved=1 mDumpInitEndTime=2')
        for interval in ('daily', 'weekly', 'monthly', 'yearly'):
            lines += _interval_lines(form, interval)
        lines += ['  UsageStatsDatabase:', '    Obfuscated Packages Mappings:', '      Counter: 2',
                  '      Token 1: [com.example.user.chat]']
        if layout == 'a10':
            lines += ['  App Standby States:'] + _standby_lines(layout, user)
        else:
            lines += ['  Database Summary:', '    daily stats files: 1, sorted list of files:',
                      '      %d="%s" ' % (ms_at(-90000), wall_at(-90000))]
    if layout == 'a16':
        lines += ['Usage Source=CURRENT_ACTIVITY ', '  App Time Limits', ' Currently Active:com.example.user.chat,',
                  ' Observed Entities:', 'Broadcast response stats:', '  Broadcast events:', '    User 0:',
                  '      com.example.user.chat:', '        <empty>', '']
        for user in users:
            lines += ['User %d App Standby States:' % user] + _standby_lines(layout, user)
            lines += ['  ', '  totalElapsedTime=+301d4h12m9s118ms', '  totalScreenOnTime=+104d7h31m2s64ms']
    lines += ['Carrier privileged apps (have=true): []', 'Settings:', '  mCheckIdleIntervalMillis=+1h0m0s0ms',
              '  mStrongUsageTimeoutMillis=+1m0s0ms']
    return '\n'.join(lines) + '\n'


def usagestats_service(layout, users, cut=False):
    if layout != 'a10':
        return ''
    events = [base.usage_event_line(event, 'plain') for event in base.USAGE_EVENTS]
    text = 'DUMP OF SERVICE usagestats:\n' + usagestats_body(layout, 'service', users, events)
    if cut:
        text += "*** SERVICE 'usagestats' DUMP TIMEOUT (10000ms) EXPIRED ***\n"
    return text + '\n--------- 0.044s was the duration of dumpsys usagestats, ending at: %s\n\n' % wall_at(2)


def usagestats_checkin(layout, users, cut=False):
    events = [base.usage_event_line(event, 'checkin') for event in base.USAGE_EVENTS]
    text = ('------ CHECKIN USAGESTATS (/system/bin/dumpsys -T 30000 usagestats -c) ------\n'
            'Flags:\n    android.app.usage.use_parceled_list: true\n')
    text += usagestats_body(layout, 'checkin', users, events)
    if cut:
        text += "*** SERVICE 'usagestats' DUMP TIMEOUT (30000ms) EXPIRED ***\n"
    return text + "------ 0.346s was the duration of 'CHECKIN USAGESTATS' ------\n\n"


# ------------------------------------------------------------------------------------------
# jobscheduler
# ------------------------------------------------------------------------------------------
# (namespace, uid label, user, package, job id, service, extra info lines, bucket, last success, last failure, restricted)
JOBS = (
    ('', 'u0a300', 0, 'com.example.user.chat', 11, 'com.example.user.chat/.sync.SyncJob',
     ['PERSISTED', 'Requires: charging=false batteryNotLow=true deviceIdle=false',
      'Network type: NetworkRequest [ NONE id=0, [ Capabilities: INTERNET&NOT_RESTRICTED Uid: 10300] ]',
      'Minimum latency: +1h0m0s0ms', 'Max execution delay: +2h0m0s0ms', 'Extras: {sync_key=example-value-1}'],
     'WORKING_SET', '2026-11-02 08:30:00', '2026-10-30 01:02:03', 'none.'),
    ('SyncManager', '1000', 0, 'com.example.sync', 12, 'android/com.android.server.content.SyncJobService',
     ['PERIODIC: interval=+1d0h0m0s0ms flex=+2h0m0s0ms', 'PERSISTED', 'Priority: 300 [DEFAULT]',
      'Requires: charging=true batteryNotLow=false deviceIdle=false'],
     'EXEMPTED', '1970-01-01 00:00:00', '', 'none.'),
    ('', '1000', 0, 'android', 3, 'android/com.android.server.DemoIdleJob', ['Requires: charging=false batteryNotLow=false deviceIdle=true'],
     'ACTIVE', '', '', 'none.'),
    ('androidx.work.systemjobscheduler', 'u10a301', 10, 'com.example.user.video', -4,
     'com.example.user.video/androidx.work.impl.background.systemjob.SystemJobService',
     ['Priority: 400 [HIGH]', 'Flags: 2'], 'RARE', '', '', 'background restricted.'),
)
COMPLETED_JOBS = (
    (-38.227, '', 'u0a300', 0, 'com.example.user.chat', 11, 'com.example.user.chat/.sync.SyncJob', 'ACTIVE'),
    (-3012.5, 'androidx.work.systemjobscheduler', 'u0a302', 0, 'com.example.user.notes', 8802,
     'com.example.user.notes/androidx.work.impl.background.systemjob.SystemJobService', 'FREQUENT'),
)


def _job_block(layout, namespace, uid, user, package, job_id, service, info, bucket, success, failure, restricted, indent=2,
               listed=True, hash_text='a1b2c3d'):
    """One registered job (indent 2) or one recently completed job (indent 6)."""
    pad = ' ' * indent
    inner = pad + '  '
    tag_service = ('@%s@%s' % (namespace, service)) if namespace and layout == 'a16' else service
    if listed:
        if layout == 'a16':
            head = '%sJOB %s:%s/%d: %s %s' % (pad, namespace, uid, job_id, hash_text, tag_service) if namespace else \
                '%sJOB #%s/%d: %s %s' % (pad, uid, job_id, hash_text, tag_service)
        else:
            head = '%sJOB #%s/%d: %s %s' % (pad, uid, job_id, hash_text, service)
    else:
        spec = ('%s {%s} #%s/%d %s' % (hash_text, namespace, uid, job_id, tag_service)) if namespace else \
            ('%s #%s/%d %s' % (hash_text, uid, job_id, tag_service))
        head = pad + spec
    lines = [head, '%s%s tag=*job*/%s' % (inner if listed else pad, uid, tag_service),
             '%sSource: uid=%s user=%d pkg=%s' % (inner if listed else pad, uid, user, package), '%sJobInfo:' % (inner if listed else pad)]
    child = (inner if listed else pad) + '  '
    lines.append('%sService: %s' % (child, service))
    lines += [child + text for text in info]
    lines.append('%sBackoff: policy=1 initial=+30s0ms' % child)
    attr = inner if listed else pad
    lines += ['%sRequired constraints: TIMING_DELAY DEADLINE IDLE [0xa0100003]' % attr,
              '%sSatisfied constraints: BATTERY_NOT_LOW DEVICE_NOT_DOZING [0x2500001]' % attr,
              '%sUnsatisfied constraints: IDLE [0x8]' % attr]
    if layout == 'a16':
        lines += ['%sConstraint history:' % attr, '%s  -2h56m29s468ms = BATTERY_NOT_LOW TIMING_DELAY [0x91400001]' % attr]
    lines += ['%sUid: active' % attr, '%sStandby bucket: %s' % (attr, bucket),
              '%sEnqueue time: %s' % (attr, duration(-34000)),
              '%sRun time: earliest=%s, latest=%s, original latest=%s' % (attr, duration(-28000), duration(7200), duration(7200))]
    if success:
        lines.append('%sLast successful run: %s' % (attr, success))
    if failure:
        lines.append('%sLast failed run: %s' % (attr, failure))
    if layout == 'a16':
        lines.append('%sRestricted due to: %s' % (attr, restricted))
    if listed:
        lines.append('%sReady: false (job=false user=true !pending=true !active=true comp=true)' % attr)
    return lines


def jobscheduler_service(layout, cut=False):
    lines = ['DUMP OF SERVICE jobscheduler:']
    if layout == 'a16':
        lines += ['Service host process PID: 3150', 'Threads in use: 0/32', 'Client PIDs: 7101, 7102']
    lines += ['Settings:', '  min_ready_non_active_jobs_count=5', '  max_cpu_only_job_batch_delay_ms=1800000',
              'Started users: [0, 10]']
    if cut:
        lines.append("*** SERVICE 'jobscheduler' DUMP TIMEOUT (10000ms) EXPIRED ***")
        return '\n'.join(lines) + '\n\n--------- 0.231s was the duration of dumpsys jobscheduler, ending at: %s\n\n' % wall_at(8)
    jobs = [job for job in JOBS if layout == 'a16' or not job[0]]
    lines.append('Registered %d jobs:' % len(jobs))
    for number, (namespace, uid, user, package, job_id, service, info, bucket, success, failure, restricted) in enumerate(jobs):
        lines += _job_block(layout, namespace, uid, user, package, job_id, service, info, bucket, success, failure, restricted,
                            hash_text='%x' % (0xa1b2c3d + number))
    lines += ['  ', 'ConnectivityController:', '  Tracking 1 jobs']
    lines += ['', 'Pending queue:', '  None', '', 'Active jobs:', '  N/A', '']
    if layout == 'a16':
        lines.append('Recently completed jobs:')
        for number, (seconds, namespace, uid, user, package, job_id, service, bucket) in enumerate(COMPLETED_JOBS):
            lines.append('  ' + duration(seconds))
            lines += _job_block('a16', namespace, uid, user, package, job_id, service, ['Priority: 300 [DEFAULT]'], bucket, '', '',
                                'none.', indent=6, listed=False, hash_text='%x' % (0xd4e5f60 + number))
        lines.append('')
    lines += ['mReadyToRock=true', 'mReportedActive=false', '', 'Concurrency:', '  Configuration:',
              '    concurrency_limit=16 ', 'PersistStats: FirstLoad: 1/2/3 LastSave: 4/5/6']
    return '\n'.join(lines) + '\n\n--------- 0.231s was the duration of dumpsys jobscheduler, ending at: %s\n\n' % wall_at(8)


# ------------------------------------------------------------------------------------------
# alarm
# ------------------------------------------------------------------------------------------
# (type name, type number, package, tag, when offset s, latest offset s, window, repeat, flags, operation or listener)
ALARMS = (
    ('ELAPSED', 3, 'android', '*alarm*:TIME_TICK', 39.94, 39.94, '0', '0', '0x9', 'listener=com.android.server.alarm.Demo$2@6f0c1d4'),
    ('ELAPSED_WAKEUP', 2, 'com.example.user.chat', '*walarm*:com.example.user.chat.action.SYNC TICK', 600.5, 2400.25, '+22m30s0ms',
     '1800000', '0x1',
     'operation=PendingIntent{3c1a2b9: PendingIntentRecord{9d8e7f1 com.example.user.chat broadcastIntent}}'),
    ('RTC_WAKEUP', 0, 'com.example.user.clock', '*walarm*:com.example.user.clock.ALERT', 20000.0, 20000.0, '0', '0', '0x3',
     'operation=PendingIntent{aa11b22: PendingIntentRecord{cc33d44 com.example.user.clock broadcastIntent}}'),
)
REMOVALS = (
    ('1000', 'alarm_cancelled', -178.016, 'ELAPSED_WAKEUP', '*walarm*:Demo Scan Timeout '),
    ('1000', 'alarm_cancelled', -195.767, 'ELAPSED_WAKEUP', '*walarm*:Demo.timeoutForUser '),
    ('u0a300', 'alarm_expired', -2000.5, 'RTC_WAKEUP', '*walarm*:com.example.user.chat.action.SYNC TICK '),
)
APP_ALARM_HISTORY = (('com.example.user.chat', 0, (-372.603, -756.636, -1008.707)), ('com.example.user.clock', 0, (-4400.0,)),
                     ('com.example.user.chat', 10, (-30.5,)))


def alarm_service(layout, cut=False):
    lines = ['DUMP OF SERVICE alarm:']
    if layout == 'a16':
        lines += ['Service host process PID: 3150', 'Threads in use: 0/32', 'Client PIDs: 7101, 7102']
    lines += ['Current Alarm Manager state:', '  Settings:', '    min_futurity=+5s0ms', '  ',
              '  nowRTC=%d=%s nowELAPSED=%d' % (NOW_MS, wall_at(0, True), NOW_ELAPSED),
              '  mLastTimeChangeClockTime=0=1970-01-01 00:00:00.000', '  mLastTimeChangeRealtime=0',
              '  Next non-wakeup alarm: %s = %d = %s' % (duration(39.94), NOW_ELAPSED + 39940, wall_at(39.94, True)), '    set at -15s911ms',
              '  Next alarm clock information: ']
    if layout == 'a16':
        lines.append('    user:0 pendingSend:false time:%d = %s = %s' % (ms_at(20000), wall_at(20000, True), duration(20000)))
    lines += ['  ']
    if cut:
        lines += ['  3 pending alarms: ', "*** SERVICE 'alarm' DUMP TIMEOUT (10000ms) EXPIRED ***"]
        return '\n'.join(lines) + '\n\n--------- 0.095s was the duration of dumpsys alarm, ending at: %s\n\n' % wall_at(9)
    if layout == 'a16':
        lines.append('  %d pending alarms: ' % len(ALARMS))
        for index, (kind, number, package, tag, when, latest, window, repeat, flags, tail) in enumerate(ALARMS, 1):
            if kind.startswith('RTC'):
                orig = '2026-11-02 15:48:40.000'
            else:
                orig = duration(when - 0.001)
            extra = ' exactAllowReason=allow-listed' if index == 1 else ''
            origin = ' origType 2' if index == 2 else ''
            lines += ['    %s #%d: Alarm{1e2d3c%d type %d%s origWhen %d whenElapsed %d %s}' % (
                kind, index, index, number, origin, NOW_ELAPSED + int(when * 1000), NOW_ELAPSED + int(when * 1000), package),
                '      tag=%s' % tag,
                '      type=%s origWhen=%s window=%s%s repeatInterval=%s count=0 flags=%s' % (kind, orig, window, extra, repeat, flags),
                '      policyWhenElapsed: requester=%s app_standby=-29m47s88ms device_idle=-- battery_saver=--' % duration(when),
                '      whenElapsed=%s maxWhenElapsed=%s' % (duration(when), duration(latest)),
                '      %s' % tail]
        lines += ['  LazyAlarmStore stats:', '    GET_COUNT: count=0, total=0.0ms', '  ', '  Pending user blocked background alarms: ',
                  '    none', '  ', '  App Alarm history:']
    else:
        lines.append('  Pending alarm batches: %d' % len(ALARMS))
        for index, (kind, number, package, tag, when, latest, window, repeat, flags, tail) in enumerate(ALARMS):
            lines += ['Batch{7a1b3c%d num=1 start=357485 end=357485 flgs=0x1}:' % index,
                      '    %s #%d: Alarm{4b2c9e%d type %d when %d %s}' % (kind, index, index, number, NOW_ELAPSED + int(when * 1000), package),
                      '      tag=%s' % tag,
                      '      type=%d expectedWhenElapsed=%s expectedMaxWhenElapsed=%s whenElapsed=%s maxWhenElapsed=%s when=%s' % (
                          number, duration(when), duration(latest), duration(when), duration(latest), duration(when)),
                      '      window=%s repeatInterval=%s count=0 flags=%s' % (window, repeat, flags),
                      '      %s' % tail]
        lines += ['  Pending user blocked background alarms: ', '    none', '  ', '  App Alarm history:']
    for package, user, offsets in APP_ALARM_HISTORY:
        lines.append('    %s, u%d: %s, ' % (package, user, ', '.join(duration(offset) for offset in offsets)))
    lines += ['  ', '  Past-due non-wakeup alarms: (none)']
    if layout == 'a16':
        lines += ['  ', '  Allow while idle history:', '    com.example.user.clock, u0: %s, ' % duration(-3600.0), '  ',
                  '  Removal history:']
        current = None
        for number, (uid, reason, offset, kind, tag) in enumerate(REMOVALS, 1):
            if uid != current:
                lines.append('    %s:' % uid)
                current = uid
            lines += ['      #%d: Reason=%s elapsed=%s rtc=%s' % (number, reason, duration(offset), wall_at(offset, True)),
                      '        Snapshot:', '          type=%s tag=%s' % (kind, tag),
                      '          policyWhenElapsed: requester=-1m30s500ms app_standby=-2m10s250ms device_idle=-- battery_saver=--']
        lines += ['  ', '  Addition history: ', '    1000:',
                  '      [tag=*walarm*:Demo Added Alarm T=2 F=0 AC=false H=L:b6c7d80 OW=%d WL=1800000 elapsed=%d rtc=%s]' % (
                      NOW_ELAPSED + 90000, NOW_ELAPSED - 120000, wall_at(-120, True)),
                  '    u0a300:',
                  '      [tag=*alarm*:com.example.user.chat.action.SYNC T=3 F=0 AC=false H=PI:d9e0f12 OW=2026-11-02 11:00:00.000 WL=3600000 '
                  'elapsed=%d rtc=%s]' % (NOW_ELAPSED - 300000, wall_at(-300, True)),
                  '  ', '  Delivery history: ', '    1000:',
                  '      [tag=*alarm*:TIME_TICK origWhen=4660210 H=L:a1b2c33 elapsed=%d rtc=%s]' % (NOW_ELAPSED - 20000, wall_at(-20, True)),
                  '  ', '  Expiration history: ', '    [flag=8 wakeup=1 non-wakeup=2 elapsed=3 rtc=%s]' % wall_at(-60, True), '  ',
                  '  Wakeup Alarm history(screen off): ',
                  '    rtc=%s uid=10077 tag=*walarm*:com.example.user.chat.KEYGUARD ' % wall_at(-7200, True),
                  '    rtc=%s uid=1000 tag=*walarm*:Demo Wakeup ' % wall_at(-3600, True)]
    lines += ['  ', '  Top Alarms:', '    +6s48ms running, 1 wakeups, 1 alarms: u0a300:com.example.user.chat',
              '      *walarm*:com.example.user.chat.action.SYNC TICK', '  ', '  Alarm Stats:']
    return '\n'.join(lines) + '\n\n--------- 0.095s was the duration of dumpsys alarm, ending at: %s\n\n' % wall_at(9)


# ------------------------------------------------------------------------------------------
# notification
# ------------------------------------------------------------------------------------------
def _record(layout, number, package, uid, user, notification_id, tag, channel, importance, created, ticker, split_tag=False):
    """One NotificationRecord of the notification list."""
    flags = '0x3a' if layout == 'a10' else 'ONLY_ALERT_ONCE|AUTO_CANCEL'
    key = '%d|%s|%d|%s|%d' % (user, package, notification_id, tag, uid)
    if split_tag:
        head = ('    NotificationRecord(0x0b1c2d3%d: pkg=%s user=UserHandle{%d} id=%d tag=%s\n importance=%d key=%s\n|%d: '
                'Notification(channel=%s shortcut=null contentView=null vibrate=null sound=null defaults=0 flags=%s category=msg '
                'groupKey=g vis=PRIVATE))' % (number, package, user, notification_id, tag, importance,
                                              key.rsplit('|', 1)[0], uid, channel, flags))
    else:
        head = ('    NotificationRecord(0x0b1c2d3%d: pkg=%s user=UserHandle{%d} id=%d tag=%s importance=%d key=%s: '
                'Notification(channel=%s pri=0 contentView=null vibrate=null sound=null defaults=0x0 flags=%s category=msg '
                'groupKey=g vis=PRIVATE))' % (number, package, user, notification_id, tag, importance, key, channel, flags))
    shown = lambda ms: ('%d(%s+0000)' % (ms, datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                        if layout == 'a16' else str(ms))
    lines = [head, '      uid=%d userId=%d' % (uid, user), '      opPkg=%s' % package, '      flags=%s' % flags, '      pri=0',
             '      key=%s' % key, '      seen=true', '      groupKey=%d|%s|g' % (user, package)]
    if layout == 'a16':
        lines += ['      notification=', '            number=0', '            tickerText=%s' % ticker, '            color=0xff102030',
                  '      publicNotification=', '            tickerText=null']
    else:
        lines += ['      number=1', '      tickerText=%s' % ticker, '      color=0xff304050',
                  '      extras={', '          android.title=String', '      }']
    lines += ['      mImportance=HIGH', '      mImportanceExplanation=app',
              '      mRankingTimeMs=%d' % created, '      mCreationTimeMs=%s' % shown(created),
              '      mVisibleSinceMs=%s' % shown(created + 5000), '      mUpdateTimeMs=%s' % shown(created + 60000),
              '      mInterruptionTimeMs=%s' % shown(created + 1000),
              "      effectiveNotificationChannel=NotificationChannel{mId='%s', mName=Dem..., mDescription=, mImportance=%d}" % (channel, importance)]
    return lines


def notification_critical(layout):
    lines = ['DUMP OF SERVICE CRITICAL notification:']
    if layout == 'a16':
        lines += ['Service host process PID: 3150', 'Threads in use: 0/32', 'Client PIDs: 7101, 7102']
    lines.append('  Notification List:')
    lines += _record(layout, 1, 'com.example.user.chat', 10300, 0, 23, 'null', 'chat_messages', 4, ms_at(-3000), 'Demo me...')
    lines += _record(layout, 2, 'com.example.user.chat', 10300, 0, 1, 'tagwith=', 'chat_messages', 3, ms_at(-2000), 'sent yo...',
                     split_tag=True)
    lines += _record(layout, 3, 'android', 1000, -1, 45, 'NetworkPolicy:123:45', 'NETWORK_ALERTS', 4, ms_at(-9000), 'High mob...')
    lines += ['  ']
    return '\n'.join(lines) + '\n--------- 0.295s was the duration of dumpsys notification, ending at: %s\n\n' % wall_at(3)


ARCHIVE = (
    ('com.example.user.chat', 0, 41, 'null', 'chat_messages', 'ONLY_ALERT_ONCE'),
    ('android', 0, 40, 'null', 'FOREGROUND_SERVICE', 'FOREGROUND_SERVICE'),
)
CHANNEL_APPS = (
    ('com.example.user.chat', 10300, 'importance=DEFAULT userSet=true', (
        ("chat_messages", 'Mes...', 4, 'false', 'content://settings/system/notification_sound', 'true', 'false', -1, 'null'),
        ("chat_old", 'Old...', 2, 'false', 'null', 'false', 'true', 1792000000000, 'old_group'))),
    ('com.example.user.silent', 10301, 'importance=NONE userSet=false', ()),
    ('com.example.user.plain', 10302, '', ()),
    ('android', 1000, 'fixedImportance=true', (
        ("NETWORK_ALERTS", 'Net...', 4, 'false', 'content://settings/system/notification_sound', 'true', 'false', -1, 'null'),)),
)


def notification_service(layout, cut=False):
    lines = ['DUMP OF SERVICE notification:']
    if layout == 'a16':
        lines += ['Service host process PID: 3150', 'Threads in use: 0/32', 'Client PIDs: 7101, 7102']
    lines += ['Current Notification Manager state:', '  mMaxPackageEnqueueRate=0.0', '  mArchive=Archive (%d notifications)' % (78 if layout == 'a16' else len(ARCHIVE) + 1)]
    for package, user, notification_id, tag, channel, flags in ARCHIVE:
        lines.append('    StatusBarNotification(pkg=%s user=UserHandle{%d} id=%d tag=%s key=%d|%s|%d|%s|10300: '
                     'Notification(channel=%s pri=0 contentView=null vibrate=null sound=null defaults=0x0 flags=%s category=msg '
                     'vis=PRIVATE))' % (package, user, notification_id, tag, user, package, notification_id, tag, channel, flags))
    lines.append('    StatusBarNotification(pkg=com.example.user.chat user=UserHandle{0} id=1 tag=Zm9vYmFy=')
    lines.append(' key=0|com.example.user.chat|1|Zm9vYmFy=')
    lines.append('|10300: Notification(channel=chat_messages pri=0 contentView=null vibrate=null sound=null flags=AUTO_CANCEL '
                 'vis=PRIVATE))')
    if layout == 'a16':
        lines.append('    ...')
    lines += ['', '  Snoozed notifications:', '', ' Notification Preferences:', '    per-package config version: 4', 'PackagePreferences:']
    for package, uid, settings, channels in CHANNEL_APPS:
        lines.append('      AppSettings: %s (%d)%s' % (package, uid, (' ' + settings) if settings else ''))
        for channel_id, name, importance, bypass, sound, lights, deleted, deleted_ms, group in channels:
            lines.append("        NotificationChannel{mId='%s', mName=%s, mDescription=, mImportance=%d, mBypassDnd=%s, "
                         "mLockscreenVisibility=-1000, mSound=%s, mLights=%s, mLightColor=0, mVibrationPattern=null, "
                         "mUserLockedFields=0, mVibrationEnabled=false, mShowBadge=true, mDeleted=%s, mDeletedTimeMs=%d, mGroup='%s', "
                         "mAudioAttributes=AudioAttributes: usage=USAGE_NOTIFICATION}" % (
                             channel_id, name, importance, bypass, sound, lights, deleted, deleted_ms, group))
        if channels:
            lines.append("        NotificationChannelGroup{mId='g1', mName=Demo, mDescription=, mBlocked=false, mChannels=[]}")
    lines += ['Restored without uid:', '  Notification listeners:', '    Allowed notification listeners:',
              '      com.example.user.chat/com.example.user.chat.Listener:com.example.launcher/com.example.launcher.NotificationListener '
              '(user: 0 isPrimary: true)', '    Has user set:', '      userId=0 value={a, b}',
              '    All notification listeners (2) enabled for current profiles:',
              '      ComponentInfo{com.example.launcher/com.example.launcher.NotificationListener}',
              '      ComponentInfo{com.example.user.chat/com.example.user.chat.Listener}',
              '    Live notification listeners (3):',
              '      ComponentInfo{android/com.android.server.Demo$NotificationListener} (user -1): '
              'android.service.notification.NotificationListenerService$NotificationListenerWrapper@3a4b5c6 SYSTEM',
              '      ComponentInfo{com.example.launcher/com.example.launcher.NotificationListener} (user 0): '
              'android.service.notification.INotificationListener$Stub$Proxy@7d8e9f0',
              '      ComponentInfo{com.example.guest/com.example.guest.Assistant} (user 10): '
              'android.service.notification.INotificationListener$Stub$Proxy@2e3f4a5 GUEST',
              '    Snoozed notification listeners (1):'] + (
                  ['      User: 0', '        com.example.user.chat/com.example.user.chat.Listener (META_DATA_DEFAULT_AUTOBIND=false)']
                  if layout == 'a16' else ['      com.example.user.chat/com.example.user.chat.Listener']) + [
              '    mListenerHints: 0', '', '  Notification assistant services:', '    Allowed notification assistants:',
              '      com.example.guest/com.example.guest.Assistant (user: 0 isPrimary: true isUserChanged: false)',
              '    All notification assistants (1) enabled for current profiles:',
              '      ComponentInfo{com.example.guest/com.example.guest.Assistant}',
              '    Live notification assistants (0):', '  Zen Mode:', '    mZenMode=ZEN_MODE_OFF',
              '  Group summaries:', '    0|com.example.user.chat|g:x -> 0|com.example.user.chat|1|null|10300', '']
    if cut:
        lines.append("*** SERVICE 'notification' DUMP TIMEOUT (10000ms) EXPIRED ***")
    return '\n'.join(lines) + '\n--------- 1.015s was the duration of dumpsys notification, ending at: %s\n\n' % wall_at(4)


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='a16', zone='Europe/Paris', users=(0, 10), report='2026-11-02 10:15:30', cut=False, newline='\n',
                 with_banner=True, only=None):
    """A bug report text. ``only`` limits the services to a subset of ('usagestats', 'jobscheduler', 'alarm', 'notification')."""
    wanted = only or ('usagestats', 'jobscheduler', 'alarm', 'notification')
    text = (base.BANNER.format(report=report) if with_banner else '') + '\n' + base.HEADER[layout] + '\n'
    text += base.properties(layout, zone, 'reboot,userrequested,%d' % base.epoch_s('2026-10-30 07:00:00'))
    text += '------ DUMPSYS CRITICAL (/system/bin/dumpsys) ------\n'
    text += '-------------------------------------------------------------------------------\n'
    if 'notification' in wanted:
        text += notification_critical(layout)
    text += "------ 0.500s was the duration of 'DUMPSYS CRITICAL' ------\n\n"
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    if 'alarm' in wanted:
        text += alarm_service(layout, cut)
    if 'jobscheduler' in wanted:
        text += jobscheduler_service(layout, cut)
    if 'notification' in wanted:
        text += notification_service(layout, cut)
    if 'usagestats' in wanted:
        text += usagestats_service(layout, users, cut)
    text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"
    if 'usagestats' in wanted:
        text += usagestats_checkin(layout, users, cut)
    text += '== dumpstate: done (id 1)\n'
    return text.replace('\n', newline)


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16').encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                             build_report('a10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_zip_on_device'] = [
        ('Dump/data/user_de/0/com.android.shell/files/bugreports/bugreport-example-2026-11-02-10-15-30.zip',
         _zip_on_device())]
    out['synthetic_two_reports'] = [('Dump1/dumpstate.txt', build_report('a16', zone='Asia/Kolkata').encode('utf-8')),
                                    ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                                     build_report('a10', zone='America/Sao_Paulo').encode('utf-8'))]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_no_zone'] = [('Dump/dumpstate.txt', build_report('a10', zone='').encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report='2026-11-02 10:15:30') + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\nDUMP OF SERVICE alarm:\n  nowRTC=1=x\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    odd = b'\xef\xbb\xbf' + build_report('a16', zone='').encode('utf-8').replace(
        b'com.example.user.chat.action.SYNC TICK', b'com.example.user.chat.action.SYNC\xff\xfe\x00TICK', 1).replace(
        b'Demo me...', b'Demo\rme\x0c...', 1)
    out['synthetic_odd_bytes'] = [('Dump/dumpstate.txt', odd)]
    return out


def _zip_on_device():
    import io
    main_text = 'bugreport-example-EXAMPLE-2026-11-02-10-15-30.txt'
    buffer = io.BytesIO()
    base.write_zip(buffer, [('main_entry.txt', main_text.encode()),
                            (main_text, build_report('a16', zone='Asia/Kolkata', report='2026-11-02 15:45:30').encode('utf-8')),
                            ('dumpstate_log.txt', b'dumpstate log of an invented device\n'), ('version.txt', b'2.0')])
    return buffer.getvalue()


MODULE = 'bugreportUsageJobs'
ARTIFACTS = ('bugreport_usage_intervals', 'bugreport_usage_interval_events', 'bugreport_standby_buckets',
             'bugreport_scheduled_jobs', 'bugreport_pending_alarms', 'bugreport_alarm_history',
             'bugreport_notification_records', 'bugreport_notification_listeners', 'bugreport_notification_channels')
PATTERNS = ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip')
DESCRIPTIONS = {
    'synthetic_a16': 'Synthetic Android 16 style bug report text (dumpstate.txt) with two Android users: usage statistics in the '
                     'CHECKIN USAGESTATS section as epoch milliseconds with a User N App Standby States list, jobs with namespaces '
                     'and a recently completed list, N pending alarms with the next alarm clock and the removal, addition, delivery '
                     'and wakeup histories, notification records with readable times (one with a line break in its tag), an archive '
                     'cut after three entries, listeners, assistants and channels. Device zone Europe/Paris. Invented values, '
                     'contains no real evidence.',
    'synthetic_a10': 'Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings): usage statistics in the service '
                     'form (formatted wall-clock text, indented App Standby States) and the checkin form, jobs without namespaces, '
                     'alarm batches, the per-app alarm history and notification records with plain millisecond times. Device zone '
                     'Europe/Paris. Invented values, contains no real evidence.',
    'synthetic_zip_on_device': 'Synthetic bug report zip as the Shell app keeps it on the device (data/user_de/0/com.android.shell/'
                               'files/bugreports), holding an Android 16 style text in the Asia/Kolkata zone. Invented values, '
                               'contains no real evidence.',
    'synthetic_two_reports': 'Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in '
                             'America/Sao_Paulo). Invented values, contains no real evidence.',
    'synthetic_cut': 'Synthetic Android 16 style bug report text whose usagestats, jobscheduler, alarm and notification dumps end '
                     'with the DUMP TIMEOUT marker. Invented values, contains no real evidence.',
    'synthetic_no_zone': 'Synthetic Android 10 style bug report text that records no time zone: wall-clock texts get no UTC value and '
                         'a note, offsets from the alarm dump still give UTC. Invented values, contains no real evidence.',
    'synthetic_empty': 'Synthetic bug report text with the banner and no sections. Invented values, contains no real evidence.',
    'synthetic_not_a_report': 'Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary '
                              'bytes). Invented values, contains no real evidence.',
    'synthetic_odd_bytes': 'Synthetic bug report text with a byte order mark, invalid UTF-8 bytes, a NUL, a lone carriage return and '
                           'a form feed inside alarm tags and notification text, and no time zone. Invented values, contains no real '
                           'evidence.',
}


def write_cases(repo_root):
    """Write the case zips (one per artifact and case) and the case file under ``repo_root``; returns the case names."""
    import fnmatch  # pylint: disable=import-outside-toplevel
    import json  # pylint: disable=import-outside-toplevel
    data_dir = os.path.join(repo_root, 'admin', 'test', 'cases', 'data', MODULE)
    os.makedirs(data_dir, exist_ok=True)
    document = {}
    for case, members in cases().items():
        matched = sum(1 for name, _data in members if any(fnmatch.fnmatchcase('root/' + name, pattern) for pattern in PATTERNS))
        for artifact in ARTIFACTS:
            base.write_zip(os.path.join(data_dir, 'testdata.%s.%s.case%s.zip' % (MODULE, artifact, case)), members)
        document['case' + case] = {
            'description': DESCRIPTIONS[case],
            'maker': 'synthetic',
            'make_data': {'input_data_path': case + '.zip', 'os': 'synthetic', 'timestamp': '2026-10-26T00:00:00',
                          'last_commit': {'hash': 'Uncommitted', 'author_name': 'N/A', 'author_email': 'N/A',
                                          'date': '2026-10-26T00:00:00', 'message': 'File not yet committed to git'}},
            'artifacts': {artifact: {'search_patterns': list(PATTERNS), 'file_count': matched,
                                     'expected_output': {'headers': [], 'data': []}} for artifact in ARTIFACTS}}
    path = os.path.join(repo_root, 'admin', 'test', 'cases', 'testdata.%s.json' % MODULE)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(document, handle, indent=2)
        handle.write('\n')
    return list(document)


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_usagejobs_fixture_out')
