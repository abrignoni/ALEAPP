"""Builds the synthetic Android bug report texts used by the Android Bug Report test cases.

Every value is invented: package names are under example.*, the device, build and time
values are made up, the user ids and times are fixed. Only the structure is taken from
real bug reports: the banner, the header lines, the SYSTEM PROPERTIES command section,
and the dumpsys service sections (package, usagestats, activity, settings) with the
section trailers the platform prints. Two layouts are built:

* ``a16``: the layout of Android 14 and later (appId, per-user firstInstallTime, the
  installer fields on every package, usage events as epoch milliseconds in the checkin
  section, a settings dump with a History block under each setting, exit info);
* ``a10``: the layout of Android 10 (userId, package-level firstInstallTime, installer
  lines only when set, usage events as wall-clock text in the service dump, a plain
  settings dump, no exit info).

Usage: python bugreport_fixture.py <output folder>
Writes one zip per test case into the folder, each holding a synthetic extraction
(files under a ``Dump`` folder), and prints their names and sizes.
"""
import io
import os
import sys
import zipfile
from datetime import datetime, timedelta, timezone

ZIP_TIME = (2026, 11, 2, 0, 0, 0)
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

BANNER = ('========================================================\n'
          '== dumpstate: {report}\n'
          '========================================================\n')

HEADER = {
    'a16': ('Build: EXAMPLE.260101.001.A1\n'
            "Build fingerprint: 'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys'\n"
            'Bootloader: EXAMPLEBL1\n'
            'Radio: EXAMPLERADIO1\n'
            'Network: ExampleNet,ExampleNet2\n'
            'Module Metadata version: 473318123\n'
            'Android SDK version: 36\n'
            'SDK extensions: [ad_services=23, b=23, c=<not set>]\n'
            'Kernel: Linux version 6.12.0-example (builder@example-host) #1 SMP PREEMPT Mon Jan 5 10:00:00 UTC 2026\n'
            'Command line: console=ttynull androidboot.serialno=SYNTH0000EXAMPLE androidboot.hardware=example\n'
            'Bootconfig: androidboot.hardware = "example"\n'
            'androidboot.serialno = "SYNTH0000EXAMPLE"\n'
            'Uptime: up 0 weeks, 1 days, 2 hours, 3 minutes,  load average: 1.00, 1.00, 1.00\n'
            'Bugreport format version: 2.0\n'
            'Dumpstate info: id=1 pid=4242 dry_run=0 args=/system/bin/dumpstate -d -p -z -o /data/user_de/0/com.android.shell/files/bugreports/bugreport\n'),
    'a10': ('Build: EXAMPLE-OLD-10.0.1\n'
            "Build fingerprint: 'Example/EXOLD/exold:10/QP1A.190711.020/1001:user/release-keys'\n"
            'Bootloader: unknown\n'
            'Radio: EXAMPLERADIO0\n'
            'Network: ExampleNet\n'
            'Module Metadata version: 133990923\n'
            'Kernel: Linux version 4.14.0-example (builder@example-host) #1 SMP PREEMPT\n'
            'Command line: loglevel=1 androidboot.serialno=SYNTH0001EXAMPLE\n'
            'Uptime: up 0 weeks, 0 days, 3 hours, 1 minutes\n'
            'Bugreport format version: 2.0\n'
            'Dumpstate info: id=1 pid=4243 dry_run=0 args=/system/bin/dumpstate -d -p -z -B\n'),
}


def epoch_ms(text):
    moment = datetime.strptime(text, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    return int((moment - EPOCH).total_seconds() * 1000)


def epoch_s(text):
    return epoch_ms(text) // 1000


def add_seconds(text, seconds):
    return (datetime.strptime(text, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S')


# ------------------------------------------------------------------------------------------
# properties
# ------------------------------------------------------------------------------------------
def properties(layout, zone, boot_history, extra=()):
    lines = [
        '[dalvik.vm.isa.arm64.variant]: [generic]',
        '[init.svc.adbd]: [running]',
        '[persist.sys.boot.reason]: []',
        '[persist.sys.boot.reason.history]: [%s]' % boot_history,
        '[persist.sys.locale]: [en-US]',
    ]
    if zone:
        lines.append('[persist.sys.timezone]: [%s]' % zone)
    lines += [
        '[ro.adb.secure]: [1]',
        '[ro.boot.bootreason]: [reboot]',
        '[ro.boot.serialno]: [SYNTH0000EXAMPLE]',
        '[ro.boot.verifiedbootstate]: [green]',
        '[ro.build.characteristics]: [default]',
        '[ro.build.fingerprint]: [example/examplephone/examplephone:%s/EXAMPLE.260101.001/1001:user/release-keys]'
        % ('16' if layout == 'a16' else '10'),
        '[ro.build.type]: [user]',
        '[ro.build.version.release]: [%s]' % ('16' if layout == 'a16' else '10'),
        '[ro.build.version.sdk]: [%s]' % ('36' if layout == 'a16' else '29'),
        '[ro.build.version.security_patch]: [2026-01-05]',
        '[ro.debuggable]: [0]',
        '[ro.product.manufacturer]: [Example]',
        '[ro.product.model]: [Example Phone 1]',
        '[ro.serialno]: [SYNTH0000EXAMPLE]',
        '[sys.boot.reason]: [reboot,userrequested]',
        '[sys.boot.reason.last]: [reboot,userrequested]',
        '[sys.reset_reason]: []',
        '[gsm.sim.imei.example]: [000000000000000]',
    ]
    lines += extra
    return ('------ SYSTEM PROPERTIES (getprop) ------\n' + '\n'.join(lines) + '\n'
            "------ 0.050s was the duration of 'SYSTEM PROPERTIES' ------\n\n")


# ------------------------------------------------------------------------------------------
# package service
# ------------------------------------------------------------------------------------------
class Package:
    def __init__(self, name, code_path, first, update, stamp, installer=None, flags='SYSTEM HAS_CODE', shared=None,
                 app_id=10100, version_code=1, version_name='1.0', users=((0, True),), hidden_copy=False):
        self.name, self.code_path, self.first, self.update, self.stamp = name, code_path, first, update, stamp
        self.installer, self.flags, self.shared, self.app_id = installer, flags, shared, app_id
        self.version_code, self.version_name, self.users, self.hidden_copy = version_code, version_name, users, hidden_copy


def package_block(pkg, layout):
    lines = ['  Package [%s] (%08x):' % (pkg.name, abs(hash_text(pkg.name)) & 0xffffffff)]
    lines.append('    %s=%d' % ('appId' if layout == 'a16' else 'userId', pkg.app_id))
    if pkg.shared:
        lines.append('    sharedUser=SharedUserSetting{abc123 %s}' % pkg.shared)
    lines += ['    pkg=Package{def456 %s}' % pkg.name,
              '    codePath=%s' % pkg.code_path,
              '    resourcePath=%s' % pkg.code_path,
              '    primaryCpuAbi=arm64-v8a',
              '    versionCode=%d minSdk=29 targetSdk=%s' % (pkg.version_code, '35' if layout == 'a16' else '29'),
              '    versionName=%s' % pkg.version_name,
              '    flags=[ %s ]' % pkg.flags]
    if layout == 'a16':
        lines.append('    timeStamp=%s' % pkg.stamp)
        if pkg.update:
            lines.append('    lastUpdateTime=%s' % pkg.update)
        lines.append('    installerPackageName=%s' % (pkg.installer or 'null'))
        lines.append('    installerPackageUid=-1')
        lines.append('    initiatingPackageName=%s' % (pkg.installer or 'null'))
        lines.append('    originatingPackageName=null')
        lines.append('    packageSource=%d' % (2 if pkg.installer else 0))
    else:
        lines.append('    timeStamp=%s' % pkg.stamp)
        lines.append('    firstInstallTime=%s' % pkg.first)
        lines.append('    lastUpdateTime=%s' % (pkg.update or pkg.first))
        if pkg.installer:
            lines.append('    installerPackageName=%s' % pkg.installer)
    lines.append('    pkgFlags=[ %s ]' % pkg.flags)
    lines.append('    install permissions:')
    lines.append('      android.permission.INTERNET: granted=true')
    for user, installed in pkg.users:
        lines.append('    User %d: ceDataInode=%d installed=%s hidden=false suspended=false stopped=false '
                     'notLaunched=false enabled=0 instant=false virtual=false'
                     % (user, 1000 + user, 'true' if installed else 'false'))
        if layout == 'a16':
            lines.append('      installReason=0')
            lines.append('      firstInstallTime=%s' % (pkg.first if installed else '1970-01-01 00:00:00'))
        lines.append('      runtime permissions:')
        lines.append('        android.permission.CAMERA: granted=false, flags=[ USER_SENSITIVE_WHEN_GRANTED]')
    return '\n'.join(lines) + '\n'


def hash_text(text):
    value = 7
    for char in text:
        value = (value * 31 + ord(char)) & 0xffffffff
    return value


def device_packages(layout, users, stamp_count=22, bulk_count=22):
    """The invented package list: image packages carrying factory stamps, user apps, edge cases."""
    packages = []
    first_scan = ['2010-01-01 00:01:23', '2010-01-01 00:01:24', '2010-01-01 00:01:25', '2010-01-01 00:01:27']
    if layout == 'a10':
        first_scan = ['2009-01-01 00:00:00'] * 4
    image_stamp = '2022-01-01 00:00:00' if layout == 'a16' else '2009-01-01 00:00:00'
    for number in range(stamp_count):
        stamp = first_scan[number % len(first_scan)]
        packages.append(Package('com.example.system.app%02d' % number, '/system/app/ExampleApp%02d' % number,
                                stamp, stamp, image_stamp, flags='SYSTEM HAS_CODE ALLOW_CLEAR_USER_DATA',
                                app_id=10100 + number, users=tuple((u, True) for u in users)))
    packages.append(Package('com.example.system.shared', '/system/priv-app/ExampleShared', '2010-01-01 00:01:23',
                            '2010-01-01 00:01:23', image_stamp, shared='example.uid.shared/1001', app_id=1001,
                            flags='SYSTEM HAS_CODE PERSISTENT', version_code=33, version_name='16-example'))
    packages.append(Package('com.example.updated.one', '/data/app/~~Zm9vYmFy==/com.example.updated.one-YmF6==',
                            '2010-01-01 00:01:24', '2026-09-14 08:30:11', '2026-09-14 08:30:11',
                            installer='com.example.store', flags='SYSTEM HAS_CODE UPDATED_SYSTEM_APP',
                            app_id=10200, version_code=210, version_name='2.1.0', users=tuple((u, True) for u in users)))
    store = 'com.example.store'
    packages.append(Package('com.example.user.chat', '/data/app/~~YWJj==/com.example.user.chat-ZGVm==',
                            '2026-03-02 21:14:05', '2026-10-30 07:45:00', '2026-10-30 07:45:00', installer=store,
                            flags='HAS_CODE ALLOW_CLEAR_USER_DATA', app_id=10300, version_code=5120,
                            version_name='5.12', users=tuple((u, u == 0) for u in users)))
    packages.append(Package('com.example.user.sideloaded', '/data/app/~~Z2hp==/com.example.user.sideloaded-amts==',
                            '2026-06-17 10:02:44', '2026-06-17 10:02:44', '2026-06-17 10:02:44',
                            flags='HAS_CODE', app_id=10301, users=tuple((u, True) for u in users)))
    packages.append(Package('com.example.user.notime', '/data/app/~~bm9wZQ==/com.example.user.notime-dGlt==',
                            '1970-01-01 00:00:00', '1970-01-01 00:00:00', '1970-01-01 00:00:00', flags='HAS_CODE',
                            app_id=10302, users=tuple((u, True) for u in users)))
    packages.append(Package('com.example.user.minusone', '/data/app/~~bWludXM=/com.example.user.minusone-b25l==',
                            '1969-12-31 23:59:59', '1969-12-31 23:59:59', '1969-12-31 23:59:59', flags='HAS_CODE',
                            app_id=10303, users=tuple((u, True) for u in users)))
    packages.append(Package('com.example.user.winter', '/data/app/~~d2ludGVy==/com.example.user.winter-c25v==',
                            '2026-01-12 09:00:00', '2026-07-04 23:30:00', '2026-07-04 23:30:00', installer=store,
                            flags='HAS_CODE', app_id=10304, users=tuple((u, True) for u in users)))
    for number in range(bulk_count):
        stamp = add_seconds('2026-10-01 07:00:00', number // 8)
        packages.append(Package('com.example.bulk.app%02d' % number,
                                '/data/app/~~YnVsaw==/com.example.bulk.app%02d-eHl6==' % number, '2026-05-01 12:00:00',
                                stamp, stamp, installer=store, flags='HAS_CODE', app_id=10400 + number,
                                users=tuple((u, True) for u in users)))
    return packages


def package_service(layout, users, packages=None, cut=False, stamp_count=22, bulk_count=22):
    packages = packages if packages is not None else device_packages(layout, users, stamp_count, bulk_count)
    visible = [p for p in packages if not p.hidden_copy]
    text = ['DUMP OF SERVICE package:', 'Service host process PID: 2682', 'Threads in use: 1/32',
            'Database versions:', '  Internal:', '    sdkVersion=%s databaseVersion=3' % ('36' if layout == 'a16' else '29'),
            '', 'Packages:']
    body = '\n'.join(text) + '\n' + ''.join(package_block(p, layout) for p in visible)
    hidden = [p for p in visible if 'UPDATED_SYSTEM_APP' in p.flags]
    body += '\nHidden system packages:\n'
    for pkg in hidden:
        shadow = Package(pkg.name, '/system/app/ExampleUpdated', pkg.first, pkg.first, '2022-01-01 00:00:00'
                         if layout == 'a16' else '2009-01-01 00:00:00', flags='SYSTEM HAS_CODE', app_id=pkg.app_id,
                         version_code=100, version_name='1.0.0', users=pkg.users)
        body += package_block(shadow, layout)
    body += '\nShared users:\n  SharedUser [example.uid.shared] (cafe0001):\n    userId=1001\n'
    if cut:
        body += "*** SERVICE 'package' DUMP TIMEOUT (10000ms) EXPIRED ***\n"
        return body + '\n'
    return body + '\n--------- 0.321s was the duration of dumpsys package, ending at: 2026-11-02 10:15:12\n\n'


# ------------------------------------------------------------------------------------------
# usage events
# ------------------------------------------------------------------------------------------
USAGE_EVENTS = (
    ('2026-11-01 21:05:10', 'SCREEN_INTERACTIVE', 'android', '', 'flags=0x0'),
    ('2026-11-01 21:05:12', 'ACTIVITY_RESUMED', 'com.example.user.chat', 'com.example.user.chat.Main',
     'instanceId=11 taskRootPackage=com.example.user.chat taskRootClass=com.example.user.chat.Main flags=0x0'),
    ('2026-11-01 21:06:40', 'ACTIVITY_PAUSED', 'com.example.user.chat', 'com.example.user.chat.Main',
     'instanceId=11 taskRootPackage=com.example.user.chat taskRootClass=com.example.user.chat.Main flags=0x0'),
    ('2026-11-01 21:06:41', 'STANDBY_BUCKET_CHANGED', 'com.example.user.chat', '', 'standbyBucket=10 reason=u-si flags=0x0'),
    ('2026-11-01 21:06:45', 'SCREEN_NON_INTERACTIVE', 'android', '', 'flags=0x0'),
    ('2026-11-02 03:30:00', 'FOREGROUND_SERVICE_START', 'com.example.user.sideloaded', 'com.example.user.sideloaded.Sync', 'flags=0x0'),
    ('2026-11-02 03:30:07', 'FOREGROUND_SERVICE_STOP', 'com.example.user.sideloaded', 'com.example.user.sideloaded.Sync', 'flags=0x0'),
    ('2026-11-02 09:59:59', 'NOTIFICATION_INTERRUPTION', 'com.example.user.chat', '', 'channelId=messages flags=0x0'),
)


PENDING_EVENTS = ('  Pending events: count=2\n'
                  '    time="1970-01-01 07:04:12" type=SYSTEM_INTERACTION package=com.example.user.chat flags=0x0 \n'
                  '    time="1970-01-01 07:06:08" type=STANDBY_BUCKET_CHANGED package=com.example.user.chat standbyBucket=10 '
                  'reason=u-si flags=0x0 \n')


def usage_event_line(event, form):
    stamp, kind, package, class_name, extra = event
    shown = 'time="%s"' % stamp if form == 'plain' else 'time=%d' % epoch_ms(stamp)
    parts = [shown, 'type=%s' % kind, 'package=%s' % package]
    if class_name:
        parts.append('class=%s' % class_name)
    parts.append(extra)
    return '    ' + ' '.join(parts) + ' '


def usage_plain(users):
    text = 'DUMP OF SERVICE usagestats:\n'
    for user in users:
        text += 'user=%d \n' % user
        text += '  Last 24 hour events (timeRange="01/11/2026, 21:00 – 02/11/2026, 10:15" )\n'
        for event in (USAGE_EVENTS if user == 0 else USAGE_EVENTS[:2]):
            text += usage_event_line(event, 'plain') + '\n'
        text += PENDING_EVENTS if user == 0 else ''
        text += ('  In-memory daily stats\n  timeRange="02/11/2026, 00:00–10:15" \n    packages\n'
                 '      package=com.example.user.chat totalTimeUsed="01:20" lastTimeUsed="2026-11-02 09:59:59" '
                 'totalTimeVisible="01:21" lastTimeVisible="2026-11-02 09:59:59" totalTimeFS="00:00" '
                 'lastTimeFS="1970-01-01 00:00:00" appLaunchCount=3 \n'
                 '      package=com.example.user.notime totalTimeUsed="00:00" lastTimeUsed="1973-08-29 05:00:27" '
                 'totalTimeVisible="00:00" lastTimeVisible="1973-08-29 05:00:27" totalTimeFS="00:00" '
                 'lastTimeFS="1973-08-29 05:00:27" appLaunchCount=0 \n'
                 '  App Standby States:\n'
                 '    package=com.example.user.chat u=%d bucket=10 reason=u-si used=+1m5s0ms usedScr=+1m5s0ms '
                 'lastPred=+0ms activeLeft=+1h0m0s0ms wsLeft=+1d0h0m0s0ms lastJob=-1d0h0m0s0ms idle=n\n' % user)
    return text + '\n--------- 0.044s was the duration of dumpsys usagestats, ending at: 2026-11-02 10:15:14\n\n'


def usage_checkin(users, begin='2026-11-01 10:15:30'):
    text = ('------ CHECKIN USAGESTATS (/system/bin/dumpsys -T 30000 usagestats -c) ------\n'
            'Flags:\n    android.app.usage.use_parceled_list: true\n')
    for user in users:
        text += 'user=%d \n' % user
        text += '  Last 24 hour events (beginTime=%d endTime=%d )\n' % (epoch_ms(begin), epoch_ms(begin) + 86400000)
        for event in (USAGE_EVENTS if user == 0 else USAGE_EVENTS[:2]):
            text += usage_event_line(event, 'checkin') + '\n'
        text += '    time=1000 type=ACTIVITY_RESUMED package=com.example.user.chat class=com.example.user.chat.Main flags=0x0 \n'
        text += PENDING_EVENTS if user == 0 else ''
    return text + "------ 0.346s was the duration of 'CHECKIN USAGESTATS' ------\n\n"


# ------------------------------------------------------------------------------------------
# activity service (process exit info)
# ------------------------------------------------------------------------------------------
EXITS = (
    ('2026-11-01 22:41:03.120', 4321, 10300, 'com.example.user.chat', '2 (SIGNALED)', '0 (UNKNOWN)', '9', 230, 'null'),
    ('2026-10-29 06:12:45.007', 3987, 10300, 'com.example.user.chat:sync', '10 (USER_REQUESTED)', '0 (UNKNOWN)', '0', 400, 'remove task'),
    ('2026-10-11 02:03:04.999', 2222, 1010300, 'com.example.user.chat', '3 (LOW_MEMORY)', '0 (UNKNOWN)', '9', 500, 'null'),
    ('2026-10-20 18:00:00.500', 1234, 10301, 'com.example.user.sideloaded', '4 (APP CRASH(NATIVE))', '0 (UNKNOWN)', '6', 100, 'crash'),
)


def activity_service():
    text = ['DUMP OF SERVICE activity:', 'ACTIVITY MANAGER SETTINGS (dumpsys activity settings)', '  max_cached_processes=32',
            '', 'ACTIVITY MANAGER PROCESS EXIT INFO (dumpsys activity exit-info)',
            'Last Timestamp of Persistence Into Persistent Storage: 2026-11-02 09:00:00.000']
    package_now, uid_now, index = '', None, 0
    for stamp, pid, uid, process, reason, sub, status, importance, description in EXITS:
        package = process.split(':')[0]
        if package != package_now:
            package_now, uid_now = package, None
            text.append('  package: %s' % package)
        if uid != uid_now:
            uid_now, index = uid, 0
            text.append('    Historical Process Exit for uid=%d' % uid)
        text += ['        ApplicationExitInfo #%d:' % index,
                 '          timestamp=%s pid=%d realUid=%d packageUid=%d definingUid=%d user=%d'
                 % (stamp, pid, uid, uid, uid, uid // 100000),
                 '          process=%s reason=%s subreason=%s status=%s' % (process, reason, sub, status),
                 '          importance=%d pss=0.00 rss=0.00 description=%s state=empty trace=null' % (importance, description)]
        index += 1
    text += ['', 'ACTIVITY MANAGER OTHER (dumpsys activity other)', '  nothing to see']
    return '\n'.join(text) + '\n\n--------- 0.500s was the duration of dumpsys activity, ending at: 2026-11-02 10:15:16\n\n'


# ------------------------------------------------------------------------------------------
# settings
# ------------------------------------------------------------------------------------------
def settings_service(layout, users):
    text = ['DUMP OF SERVICE settings:', 'Service host process PID: 2682', 'Threads in use: 0/32', 'Client PIDs: 466',
            'Unknown argument: -a; use -h for help']
    for user in users:
        if layout == 'a16':
            text += ['CONFIG SETTINGS (user %d)' % user, 'version: 5',
                     '_id:1 name:example/flag_one pkg:android value:true default:false',
                     '  History (example/flag_one)',
                     '    time:09-01 10:00:00.100 mode:insert oldValue:null newValue:true package:android', '']
        text += ['GLOBAL SETTINGS (user %d)' % user, 'version: 12']
        entries = [
            ('_id:11 name:adb_enabled pkg:android value:0 default:0 defaultSystemSet:true', ('adb_enabled', [
                ('10-02 08:00:00.000', 'update', '1', '0', 'com.example.settings'), ('11-01 20:00:00.250', 'update', '0', '1', 'com.example.settings')])),
            ('_id:12 name:device_name pkg:com.example.settings value:Example Phone default:Example defaultSystemSet:true', ('device_name', [
                ('02-14 12:30:00.000', 'insert', 'null', 'Example Phone', 'com.example.settings')])),
            ('_id:13 name:empty_value pkg:android value: default: defaultSystemSet:true', ('empty_value', [])),
            ('_id:14 name:no_value pkg:android value:{null} default:{null}', ('no_value', [])),
        ]
        for line, (key, history) in entries:
            if layout == 'a16':
                line += ' isValuePreservedInRestore:true'
            text.append(line)
            if layout == 'a16' and history:
                text.append('  History (%s)' % key)
                for stamp, mode, old, new, package in history:
                    text.append('    time:%s mode:%s oldValue:%s newValue:%s package:%s' % (stamp, mode, old, new, package))
                text.append('')
        text += ['SECURE SETTINGS (user %d)' % user, 'version: 8',
                 '_id:21 name:enabled_notification_listeners pkg:android value:com.example.user.chat/com.example.user.chat.Listener:com.example.other/.L',
                 '_id:22 name:long_value pkg:android value:' + 'QUJD' * 20 + '\n  ' + 'REVG' * 10 + ' default:',
                 'SYSTEM SETTINGS (user %d)' % user, 'version: 3',
                 '_id:31 name:screen_off_timeout pkg:android value:30000 default:60000 defaultSystemSet:true',
                 'GENERATION REGISTRY', '  Generation:1', '']
    return '\n'.join(text) + '\n--------- 0.080s was the duration of dumpsys settings, ending at: 2026-11-02 10:15:17\n\n'


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='a16', zone='Europe/Paris', users=(0,), report='2026-11-02 10:15:30', cut=False,
                 stamp_count=22, bulk_count=22, newline='\n', with_banner=True, boot_history=None,
                 extra_properties=()):
    if boot_history is None:
        boot_history = 'reboot,userrequested,%d\ncold,powerkey,%d\nreboot,ota,%d' % (
            epoch_s('2026-10-30 07:00:00'), epoch_s('2026-09-12 05:20:01'), epoch_s('2026-08-03 22:10:09'))
    text = (BANNER.format(report=report) if with_banner else '') + '\n' + HEADER[layout] + '\n'
    text += properties(layout, zone, boot_history, extra_properties)
    text += '------ DUMPSYS CRITICAL (/system/bin/dumpsys) ------\n'
    text += '-------------------------------------------------------------------------------\n'
    text += package_service(layout, users, cut=cut, stamp_count=stamp_count, bulk_count=bulk_count)
    if cut:
        return text.replace('\n', newline)
    text += "------ 0.500s was the duration of 'DUMPSYS CRITICAL' ------\n\n"
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    text += settings_service(layout, users)
    if layout == 'a16':
        text += activity_service()
        text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"
        text += usage_checkin(users)
    else:
        text += usage_plain(users)
        text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"
        text += usage_checkin(users)       # Android 10 builds print the checkin form as well
    text += '== dumpstate: done (id 1)\n'
    return text.replace('\n', newline)


# ------------------------------------------------------------------------------------------
# cases
# ------------------------------------------------------------------------------------------
# Invented identifier properties of the device facts case: one line per name on the identifier list, plus a name that is not on it.
IDENTIFIER_LINES = (
    '[ro.vendor.boot.serialno]: [SYNTH0002EXAMPLE]',
    '[ro.boot.ap_serial]: [SYNTH0003EXAMPLE]',
    '[ro.ril.oem.sno]: [SYNTH0004EXAMPLE]',
    '[ro.ril.oem.psno]: [SYNTH0005EXAMPLE]',
    '[ro.ril.oem.imei]: [000000000000001]',
    '[ro.ril.oem.imei1]: [000000000000002]',
    '[ro.ril.oem.imei2]: [000000000000003]',
    '[ro.ril.oem.meid]: [00000000000004]',
    '[ro.product.imeisv]: [00]',
    '[ro.vendor.radio.imei.sv]: [00]',
    '[persist.radio.sim.iccid]: [00000000000000000001,00000000000000000002]',
    '[gsm.sim.preiccid_0]: [0000001]',
    '[gsm.sim.preiccid_1]: [0000002]',
    '[odm.gsm.sim.preiccid_0]: [0000003]',
    '[odm.gsm.sim.preiccid_1]: [0000004]',
    '[persist.odm.radio.preiccid_0]: [0000005]',
    '[persist.odm.radio.preiccid_1]: [0000006]',
    '[persist.vendor.radio.ss.hashed_last_iccid1]: [0123456789abcdef0123456789abcdef]',
    '[ro.boot.btmacaddr]: [00:00:5e:00:53:01]',
    '[ro.boot.wifimacaddr]: [00:00:5e:00:53:02,00:00:5e:00:53:03]',
    '[persist.sys.nearby.uuid]: [00000000-0000-4000-8000-000000000000]',
    '[ro.quick_start.device_id]: [ex-0001]',
    '[sys.fingerprint.deviceId]: [7]',
    '[ro.serialno.not.on.the.list]: [SYNTH0009EXAMPLE]',
)


def zip_info(name):
    info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
    info.external_attr = 0o600 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def write_zip(path, members):
    """members: iterable of (name, bytes)."""
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            archive.writestr(zip_info(name), data)


def bug_report_zip(layout, **kwargs):
    """The zip a device keeps: main_entry.txt naming the main text, the text, a side log and a version file."""
    main_text = 'bugreport-example-%s-2026-11-02-10-15-30.txt' % ('EXAMPLE' if layout == 'a16' else 'EXOLD')
    buffer = io.BytesIO()
    write_zip(buffer, [('main_entry.txt', main_text.encode()), (main_text, build_report(layout, **kwargs).encode('utf-8')),
                       ('dumpstate_log.txt', b'dumpstate log of an invented device\n'), ('version.txt', b'2.0')])
    return buffer.getvalue()


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16', users=(0, 10)).encode('utf-8'))]
    out['synthetic_identifiers'] = [('Dump/dumpstate.txt', build_report('a16', extra_properties=IDENTIFIER_LINES).encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                             build_report('a10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_zip_on_device'] = [
        ('Dump/data/user_de/0/com.android.shell/files/bugreports/bugreport-example-2026-11-02-10-15-30.zip',
         bug_report_zip('a16', zone='Asia/Kolkata', report='2026-11-02 15:45:30'))]
    out['synthetic_two_reports'] = [('Dump1/dumpstate.txt', build_report('a16', zone='Asia/Kolkata').encode('utf-8')),
                                    ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                                     build_report('a10', zone='America/Sao_Paulo').encode('utf-8'))]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (BANNER.format(report='2026-11-02 10:15:30') + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\nDUMP OF SERVICE package:\n  Package [x] (1):\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    odd = build_report('a16', zone='', stamp_count=21).encode('utf-8')
    odd = b'\xef\xbb\xbf' + odd.replace(b'versionName=1.0', b'versionName=1.0\xff\xfe', 1).replace(
        b'Example Phone', b'Example \xe9 Phone\x00', 1).replace(b'Bootloader: EXAMPLEBL1', b'Bootloader: EX\rAMPLE\x0cBL1', 1)
    out['synthetic_odd_bytes'] = [('Dump/dumpstate.txt', odd)]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_fixture_out')
