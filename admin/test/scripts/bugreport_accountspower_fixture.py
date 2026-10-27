"""Builds the synthetic Android bug report texts used by the Accounts, Sync, Backup, Users, Battery, Power, Process and Memory test cases.

Every value is invented: accounts are under example.test, packages under example.*, ids, times and numbers are made up.
Only the structure is taken from real bug reports: the dumpsys service sections (account, content, backup, user, battery,
batterystats, power, deviceidle, thermalservice, procstats, meminfo) and the ps command section with the section trailers
the platform prints. Two layouts are built, as in ``bugreport_fixture``:

* ``a16``: the layout of Android 14 and later (battery history with a printed date and time on every record, the Daily
  stats and per UID blocks of batterystats, the PowerHistorian lists of the power dump, the Total PSS and RSS lists of meminfo);
* ``a10``: the layout of Android 10 (battery history with offsets from a clock record, a wrapped details line at column 0, a
  shorter power dump, thermalservice, a user dump without Type and Flags lines, meminfo blocks without the Rss columns).

Usage: python bugreport_accountspower_fixture.py <output folder>
Writes one zip per test case into the folder, each holding a synthetic extraction (files under a ``Dump`` folder).
"""
import os
import sys

from admin.test.scripts import bugreport_fixture as base

TRAILER = '--------- 0.100s was the duration of dumpsys %s, ending at: 2026-11-02 10:15:20\n\n'
NOW = '2026-11-02 10:15:30'


def pad_table(headers, rows):
    """Left-aligned columns, each as wide as its longest cell plus two spaces (as the platform prints its tables)."""
    widths = [max(len(str(row[number])) for row in [headers] + rows) + 2 for number in range(len(headers))]
    lines = [''.join(str(cell).ljust(width) for cell, width in zip(row, widths)).rstrip() for row in [headers] + rows]
    return lines, widths


# ------------------------------------------------------------------------------------------
# account
# ------------------------------------------------------------------------------------------
ACCOUNTS = (('person.one@example.test', 'com.example.auth'), ('Example Chat', 'com.example.chat'),
            ('person.two@example.test', 'com.example.auth'), ('My application', 'com.example.sync'))
ACCOUNT_HISTORY = (
    (-1, 'action_called_account_add', '2026-03-01 09:00:00', 10100, 0), (1, 'action_account_add', '2026-03-01 09:00:05', 10101, 1),
    (1, 'action_set_password', '2026-03-01 09:00:05', 10101, 2), (2, 'action_account_add', '2026-03-02 18:30:10', 10102, 3),
    (2, 'action_called_account_remove', '2026-08-15 07:45:00', 10102, 4), (2, 'action_account_remove', '2026-08-15 07:45:00', 1000, 5),
    (3, 'action_account_add', '2026-08-15 07:45:09', 10102, 6))


def account_service(layout, users):
    text = ['DUMP OF SERVICE account:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 11, 22, 33']
    for user in users:
        accounts = ACCOUNTS if user == 0 else ACCOUNTS[:1]
        text += ['User UserInfo{%d:%s:%s}:' % (user, 'Example Owner' if user == 0 else 'Work Profile', '4c13' if user == 0 else '8671931'),
                 '  Accounts: %d' % len(accounts)]
        text += ['    Account {name=%s, type=%s}' % pair for pair in accounts]
        text += ['  ', '  AccountId, Action_Type, timestamp, UID, TableName, Key', '  Accounts History']
        history = ACCOUNT_HISTORY if user == 0 else ACCOUNT_HISTORY[:2]
        text += ['  %d,%s,%s,%d,accounts,%d' % row for row in history]
        text += ['  ', '  Active Sessions: 0', '  ', '  RegisteredServicesCache: 2 services']
        suffix = ', lastUpdateTime -1' if layout == 'a16' else ''
        text += ['    ServiceInfo: AuthenticatorDescription {type=com.example.auth}, ComponentInfo{com.example.accounts/'
                 'com.example.accounts.AuthService}, uid 10101' + suffix,
                 '    ServiceInfo: AuthenticatorDescription {type=com.example.chat}, ComponentInfo{com.example.chat/'
                 'com.example.chat.AccountService}, uid 10102' + suffix, '  ', '  Account visibility:',
                 '    person.one@example.test', '      com.example.maps, 2', '      com.example.mail, 2', '    Example Chat',
                 '      com.example.chat, 1', '  ']
    text += ['Account event dump: ', '  description=validateAccountsInternal 0 isCeDatabaseAttached=true date=2026/11/02 03:05:26 ', '']
    return '\n'.join(text) + '\n' + TRAILER % 'account'


# ------------------------------------------------------------------------------------------
# content
# ------------------------------------------------------------------------------------------
def content_service(layout):
    acct = 'person.one@example.test'
    kind = 'com.example.auth'
    text = ['DUMP OF SERVICE content:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 11, 22',
            'Data connected: true', 'Battery saver: false', 'Auto sync: u0=true ', 'Clock valid: true', 'Accounts: 4',
            'Now: 293662481 (2026-11-02 10:12:56)', 'Uptime: 1d02h03m04s', 'Time spent syncing: 37s, sync not in progress', '',
            'Active Syncs: 0', '', 'Pending Syncs: 1',
            'JobId=429 %s/%s u0 [example.mail] OTHER ExpectedIn=-6h49m44s Reason=10267 Owner={u0a267 com.example.mail [20]} '
            '[sync_reason=7 ]' % (acct, kind), '', 'Periodic Syncs: 2']
    if layout == 'a16':
        text += ['JobId=21 %s/%s u0 [example.calendar] PERIODIC Reason=Periodic (period=1d00h00m00s flex=57m36s) '
                 'Owner={u0a251 com.example.calendar [5]}' % (acct, kind),
                 'JobId=22 Example Chat/com.example.chat u10 [example.contacts] PERIODIC Reason=Periodic (period=1h00m00s flex=2m24s) '
                 'Owner={u10a102 com.example.chat [10] [ACTIVE]} [periodic_sync=true ]']
    else:
        text += ['JobId=105655 %s/ u0 (%s u0 [example.calendar] PERIODIC Reason=Periodic (period=1d00h00m00s flex=57m36s) '
                 'Owner={u0a169 com.example.calendar [10]}' % (acct, kind),
                 'JobId=100462 Example Chat/ u0 (com.example.chat u0 [example.contacts] PERIODIC Reason=Periodic '
                 '(period=1h00m00s flex=2m24s) Owner={u0a194 com.example.chat [10] [ACTIVE]} [periodic_sync=true ]']
    text += ['', 'Sync Status']
    headers = ['Authority', 'Syncable', 'Enabled', 'Stats', 'Loc', 'Poll', 'Per', 'Feed', 'User', 'Othr', 'Tot', 'Fail', 'Can',
               'Time', 'Last Sync', 'Backoff']
    rows = [
        ['example.calendar', '1', 'true', 'Total', '1', '0', '405', '1', '8', '359', '774', '81', '91', '2h20m07s', 'OTHER SUCCESS', ''],
        ['', '', '', 'Today', '', '', '', '', '', '', '', '', '', '0s', '2026-11-01 22:48:43', ''],
        ['', '', '', 'Yestr', '', '', '1', '', '1', '2', '', '', '', '7s', '', ''],
        ['example.contacts', '1', 'true', 'Total', '2387', '0', '106', '3', '1', '25', '2522', '47', '19', '50m24s', 'PERIODIC FAILURE', ''],
        ['', '', '', 'Today', '1', '', '', '', '', '', '2', '', '', '23s', '2026-11-02 06:43:33', ''],
        ['', '', '', 'Yestr', '', '', '', '', '', '', '', '', '', '0s', 'io-error', ''],
        ['example.notes', '0', 'false', 'Total', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0s', '', '']]
    lines, _widths = pad_table(headers, rows)
    text += ['Account %s u0 %s' % (acct, kind), '=' * 71, lines[0], '-' * len(lines[0])] + lines[1:]
    text += ['Account Example Chat u0 com.example.chat', '=' * 71, 'Authority  Syncable  Enabled  Stats  Loc  Poll  Per  Feed  User  Othr  '
             'Tot  Fail  Can  Time  Last Sync  Backoff', '-' * 109, '']
    text += ['Detailed Statistics (Recent history):  3 (# of times) 23s (sync time)', '-' * 40,
             '  example.contacts                   : 2/66%      23s/99%    ', '    ' + acct + '                : 2/66%', '-' * 40, '',
             'Recent Sync History', '(SERVER is now split up to FEED and OTHER)']
    history = [
        (1, '2026-11-02 06:43:18', 'FEED', 15.8, '', '%s/%s u0' % (acct, kind), 'example.contacts', 'com.example.accounts', ''),
        (2, '2026-11-02 06:43:10', 'LOCAL', 7.2, '7', 'Example Chat/com.example.chat u0', 'example.contacts', 'android.uid.shared:10011', ''),
        (3, '2026-11-02 06:39:36', 'USER', 0.2, '01:50:34', '%s/%s u0' % (acct, kind), 'example.calendar.longname', 'Periodic', 'canceled')]
    for index, when, source, seconds, extra, who, authority, reason, message in history:
        text.append('  #%-3d: %s %9s %4.1fs%10s  %s  %s  %s' % (index, when, source, seconds, extra, who.ljust(36), authority.ljust(26), reason))
        if message:
            text.append('    mesg=%s' % message)
    text += ['', 'Recent Sync History Extras', '(SERVER is now split up to FEED and OTHER)',
             '  #1  : 2026-11-02 06:43:18     FEED   %s/%s u0  example.contacts  Bundle[{feed=contacts/%s}]' % (acct, kind, acct),
             '  #2  : 2026-11-02 06:43:10    LOCAL   Example Chat/com.example.chat u0  example.contacts  Bundle[{upload=true}]', '',
             'Sync Statistics', '  Today:  Success (5 for 23.5s avg=4.7s) Failure (0)', '  Day-1:  Success (21 for 68.2s avg=3.2s) Failure (1 for 1.0s avg=1.0s)',
             '', 'Per Adapter History', '(SERVER is now split up to FEED and OTHER)', '  %s/%s u0 [example.calendar]' % (acct, kind),
             '    Per source last syncs:', '         OTHER  Success: 2026-11-01 22:48:43  Failure: N/A', '    Last syncs:',
             '      2026-11-01 22:48:43 success Source=OTHER Elapsed=0s Reason=10169 Extras=[sync_default=true feed_internal=%s ]' % acct,
             '      2026-11-01 22:48:36 canceled Source=PERIODIC Elapsed=6s Reason=Periodic Exemption=fg Extras=[]',
             '      this line has an unreadable shape', '  Example Chat/com.example.chat u0 [example.contacts]', '    Last syncs:',
             '      2026-10-30 08:00:00 success Source=LOCAL Elapsed=1s Reason=android.uid.shared:10011 Extras=[upload=true ]', '',
             'SyncManager Config:', '  mInitialSyncRetryTimeInSeconds=30', '', 'Observer tree:',
             '  settings/global: pid=1234 uid=1000 user=0 target=2f92ba', '']
    return '\n'.join(text) + '\n' + TRAILER % 'content'


# ------------------------------------------------------------------------------------------
# backup
# ------------------------------------------------------------------------------------------
def backup_service():
    now = base.epoch_ms('2026-11-02 10:12:00')
    text = ['DUMP OF SERVICE backup:', 'Service host process PID: 1234', 'Threads in use: 1/32', 'Client PIDs: 11, 22',
            'Backup Manager is enabled / setup complete / not pending init', 'Auto-restore is enabled', 'No backups running',
            'Framework scheduling is enabled', 'Last backup pass started: 0 (now = %d)' % now,
            '  next scheduled: %d' % (now + 33000000), 'Transport whitelist:', '    com.example.localtransport/.LocalTransportService',
            '    com.example.cloud/.BackupTransportService', 'Available transports:', '    com.example.localtransport/.LocalTransport',
            '       destination: Backing up to a private cache', '       intent: null',
            '  * com.example.cloud/.BackupTransportService', '       destination: person.one@example.test',
            '       intent: Intent { cmp=com.example.cloud/.SetBackupAccountActivity }', '       @pm@ - 7565 state bytes',
            '       com.example.chat - 88 state bytes', '       com.example.maps - 0 state bytes',
            'Transport clients created: 4', 'Current transport clients: 0', 'Pending init: 0', 'Ancestral: 0', 'Current:   21c53c20b328bc21',
            'Participants:', '  uid: 1000', '    com.example.settings', '    android', '  uid: 10101', '    com.example.accounts',
            'Ancestral packages: none', 'Ever backed up: 2', 'Pending key/value backup: 2', '    BackupRequest{pkg=com.example.maps}',
            '    BackupRequest{pkg=android}', 'Full backup queue:3', '    0 : com.example.never', '    %d : com.example.chat' % (now - 86400000 * 3),
            '    %d : com.example.maps' % (now - 3600000), 'Agent timeouts:', '    Fullbackup timeout: 300000', '']
    return '\n'.join(text) + '\n' + TRAILER % 'backup'


# ------------------------------------------------------------------------------------------
# user
# ------------------------------------------------------------------------------------------
def user_service(layout):
    if layout == 'a10':
        text = ['DUMP OF SERVICE user:', 'Users:', '  UserInfo{0:Example Owner:13} serialNo=0', '    State: RUNNING_UNLOCKED', '    Created: <unknown>',
                '    Last logged in: +59m42s780ms ago', '    Start time: +59m53s886ms ago', '    Unlock time: +59m42s841ms ago',
                '    Has profile owner: false', '    Restrictions:', '      none', '    Device policy global restrictions:', '      null',
                '    Effective restrictions:', '      none', '', '  Device owner id:-10000', '', '  Guest restrictions:', '    no_sms',
                '    no_outgoing_calls', '', '  Device managed: false', '  Started users state: {0=3}', '', '  Max users: 4', '']
    else:
        text = ['DUMP OF SERVICE user:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 11, 22', 'Current user: 0', '',
                'Users:', '  UserInfo{0:Example Owner:4c13} serialNo=0 isPrimary=true', '    Type: android.os.usertype.full.SYSTEM',
                '    Flags: 19475 (ADMIN|FULL|INITIALIZED|MAIN|PRIMARY|SYSTEM)', '    State: RUNNING_UNLOCKED', '    Created: <unknown>',
                '    Last logged in: +6h14m45s255ms ago', '    Start time: +7h30m43s338ms ago', '    Unlock time: +6h14m45s791ms ago',
                '    Last entered foreground: +7h30m43s339ms ago', '    Has profile owner: false', '    Restrictions:', '      none',
                '    Effective restrictions:', '      none', '    UserProperties:', '        mShowInLauncher=0',
                '  UserInfo{10:Work Profile:8671931} serialNo=10 isPrimary=false parentId=0', '    Type: example.usertype.profile.WORK',
                '    Flags: 84822976 (INITIALIZED|PROFILE)', '    State: RUNNING_LOCKED', '    Created: +572d20h23m57s488ms ago',
                '    Last logged in: +516d16h44m52s630ms ago', '    Start time: +7h30m37s304ms ago', '    Unlock time: <unknown>',
                '    Last entered foreground: <unknown>', '    Has profile owner: true', '    Restrictions:', '      no_bluetooth_sharing',
                '      no_wallpaper', '    Effective restrictions:', '      no_bluetooth_sharing', '      no_wallpaper', '',
                '  Device owner id:-10000', '  Device managed: false', '  Started users state: {0=3, 10=1}', '  Max users: 4', '']
    return '\n'.join(text) + '\n' + TRAILER % 'user'


# ------------------------------------------------------------------------------------------
# battery, thermal
# ------------------------------------------------------------------------------------------
def battery_service():
    text = ['DUMP OF SERVICE battery:', 'Service host process PID: 1234', 'Threads in use: 1/32', 'Client PIDs: 466',
            'Current Battery Service state:', '  AC powered: false', '  USB powered: false', '  Max charging current: 0',
            '  Charge counter: 1960000', '  status: 3', '  health: 2', '  present: true', '  level: 15', '  scale: 100',
            '  voltage: 3794', '  temperature: 358', '  technology: Li-ion',
            ' Time when the latest updated value of the voltage was sent via battery changed broadcast: 0', 'EXAMPLE_FEATURE: true', '']
    return '\n'.join(text) + '\n' + TRAILER % 'battery'


def thermal_service():
    text = ['DUMP OF SERVICE thermalservice:', 'Service host process PID: 1234', 'IsStatusOverride: false', 'ThermalEventListeners:',
            '\tcallbacks: 4', '\tkilled: false', 'Thermal Status: 0', 'Cached temperatures:',
            '\tTemperature{mValue=38.0, mType=1, mName=gpu, mStatus=0}', '\tTemperature{mValue=32.0, mType=2, mName=Battery, mStatus=0}',
            'HAL Ready: true', 'HAL connection:', '\tThermalHAL 2.0 connected: yes', 'Current temperatures from HAL:',
            '\tTemperature{mValue=44.0, mType=0, mName=cluster1, mStatus=0}', 'Current cooling devices from HAL:',
            '\tCoolingDevice{mValue=0, mType=2, mName=cluster0}', 'Temperature static thresholds from HAL:',
            '\tTemperatureThreshold{mType=0, mName=CPU, mHotThrottlingThresholds=[NaN, 85.0, 90.0], mColdThrottlingThresholds=[NaN, NaN, NaN]}',
            'Temperature headroom thresholds:', '[NaN, NaN, 1.1666666, 1.3333334]', '']
    return '\n'.join(text) + '\n' + TRAILER % 'thermalservice'


# ------------------------------------------------------------------------------------------
# batterystats
# ------------------------------------------------------------------------------------------
def history_f2():
    return [
        'Battery History [Format: 2] (26% used, 1091KB used of 4096KB, 1622 strings using 87KB):',
        '  11-01 21:00:00.033 RESET:TIME: 2026-11-01-21-00-00-033',
        '  11-01 21:00:00.033 100 c4900011 status=discharging health=good plug=none temp=390 volt=4432 +running +wake_lock +screen',
        '                 Stats: duration=618 bluetooth=rx: 0 tx: 0 idle: 0',
        '  11-01 21:00:00.066 100 c4900011',
        '                    u0a114: top: 0',
        '  11-01 21:05:12.400 099 c4900011 +top=u0a300:"com.example.user.chat" volt=4401',
        '  11-01 21:06:40.000 098 c0900011 -top=u0a300:"com.example.user.chat" +wake_lock=1001:"*example-radio*" -screen',
        '  11-01 21:06:41.250 098 80900011 -wake_lock=1001:"*example-radio*"',
        '  11-02 03:30:00.000 090 c0800011 +job=u0a301:"com.example.user.sideloaded/.SyncJob" stats=0:"dump"',
        '  11-02 10:15:20.500 TIME: 2026-11-02-10-15-20-500',
        '  11-02 10:15:21.000 SHUTDOWN',
        '  11-02 10:15:22.000 START',
    ]


def history_f1():
    return [
        'Battery History (7% used, 315KB used of 4096KB, 811 strings using 88KB):',
        '                    0 (14) RESET:TIME: 2026-11-01-21-00-00',
        '                    0 (2) 096 c0100010 status=discharging health=good plug=none temp=360 volt=4328 +running +wake_lock +screen',
        '                    0 (2) 096 c0100010 user=0:"0"',
        '                +6ms (3) 096 c0000010 -screen stats=0:"wakelock-change"',
        '               +884ms (2) 096 c0000010 volt=4267',
        '        +8h08m38s434ms (25) TIME: 2026-11-02-05-08-18',
        '                 Details: cpu=872918u+0bb7f0s',
        '                          /proc/stat=173680 usr, 119850 sys',
        ', SubsystemPowerState SubsystemPowerState subsystem_1 name=DefaultEntity state_1 name=Active time=1 count=2',
        '        +8h08m39s000ms (3) 095 c8000008 +wake_lock=1000:"*alarm*:TIME_TICK" +top=u0a300:"com.example.user.chat"',
        '       +13h15m04s479ms (12) SHUTDOWN',
        '       +13h15m04s480ms (12) START',
        '       +13h15m04s480ms (14) TIME: 2026-11-02-10-15-04',
        '       +13h15m10s000ms (2) 089 c0000008 stats=0:"dump"',
    ]


def daily_stats():
    return [
        'Daily stats:', '  Current start time: 2026-11-02-03-00-00', '  Next min deadline: 2026-11-03-01-00-00',
        '  Current daily discharge step durations:', '    #0: +14m40s151ms to 15 (power-save-off, device-idle-off)',
        '    #1: +9m38s732ms to 16 (screen-on, power-save-off, device-idle-off)',
        '      Discharge total time: 1d 16h 50m 34s 500ms  (from 2 steps)',
        '  Current daily charge step durations:', '    #0: +1m11s684ms to 18 (power-save-off, device-idle-off)',
        '      Charge total time: 41m 36s 0ms  (from 1 steps)',
        '  Daily from 2026-11-01-02-13-28 to 2026-11-02-03-00-00:', '    Discharge step durations:',
        '      #0: +15m56s757ms to 49 (power-save-on)', '      #1: +12m21s257ms to 50 (power-save-on)',
        '      #2: +1m10s349ms to 51 (screen-on, power-save-off)', '        Discharge total time: 9h 50m 23s 100ms  (from 3 steps)',
        '        Discharge screen on time: 3h 11m 8s 400ms  (from 1 steps)', '    Charge step durations:',
        '      #0: +2m0s762ms to 39 (screen-on, power-save-off, device-idle-off)', '        Charge total time: 2m 0s 762ms  (from 1 steps)',
        '    Package changes:', '      Update com.example.chat vers=5120', '      Update com.example.chat vers=5120',
        '      Uninstall com.example.gone', '  Daily from 2026-10-31-01-00-00 to 2026-11-01-02-13-28:', '    Discharge step durations:',
        '      #0: +1h13m15s200ms to 19 (screen-off, power-save-off, device-idle-on)']


def stats_since_charge(layout):
    text = ['Statistics since last charge:', '  System starts: 1, currently on battery: true', '  Screen on: 8h 42m 19s 519ms (52.3%) 269x', '',
            '  Device battery use since last full charge', '    Amount discharged (lower bound): 114', '',
            '  Estimated power use (mAh):', '    Capacity: 4860, Computed drain: 5460, actual drain: 5460']
    if layout == 'a16':
        text += ['    Global', '    screen: 1271 apps: 1271', '    cpu: 41870 apps: 41272 duration: 8d 11h 32m 45s 422ms ',
                 '      (on battery, screen on)', '      screen: 1271 apps: 1271',
                 '  UID 1000: 8816 bg: 8816', '      cpu=8784 cpu:bg=8784 audio=0.837 (1m 56s 723ms)',
                 '      (on battery, screen on) cpu=1135 cpu:bg=1135',
                 '  UID u0a300: 7542 fg: 346 (6h 29m 26s 160ms) bg: 6418 (7h 39m 30s 113ms) fgs: 44.9 (1h 24m 27s 968ms) cached: 28.5',
                 '      screen=705 cpu=6615 cpu:fg=227', '  UID u0a301: 12.5 bg: 12.5']
    else:
        text += ['    Unaccounted: 3157 ( ) Including smearing: 0 ( ) Excluded from smearing', '    Screen: 575 Excluded from smearing',
                 '    Uid 1000: 27.4 ( cpu=20.1 wake=0.259 wifi=3.53 ) Excluded from smearing',
                 '    Uid u0a300: 23.3 ( cpu=1.41 wake=1.07 ) Including smearing: 24.1 ( proportional=0.818 )', '    Idle: 15.6 Excluded from smearing']
    text += ['', '  All kernel wake locks:', '  Kernel Wake lock PowerManagerService.WakeLocks: 55m 24s 16ms (1254 times) realtime',
             '  Kernel Wake lock Active resource: example_wakelock: 4d 11h 26m 40s 329ms (1292017 times) realtime', '',
             '  All partial wake locks:', '  Wake lock u0a300 *job*/example: 12m 32s 527ms (41 times) max=30496 actual=1035679 realtime', '',
             '  u0a300:', '    Mobile network: 508.75MB received, 14.21MB sent (packets 769059 received, 866872 sent)',
             '    Wake lock NotificationManagerService:post:com.example.user.chat realtime',
             '    Wake lock *alarm*: 14ms partial (4 times) max=8 actual=27, 27ms background partial (4 times) max=8 realtime',
             '    Wake lock WindowManager/displayId:0: 3h 7m 3s 919ms full (497 times) realtime',
             '    TOTAL wake: 3h 7m 3s 919ms full, 1m 8s 15ms blamed partial realtime',
             '    Apk com.example.user.chat:', '      Service com.example.user.chat.Sync:', '        Starts: 0, launches: 2341',
             '    Apk com.example.user.chat.lite:', '  1000:', '    Wake lock Prevent Sleep: 2s 5ms partial (3 times) max=900 realtime',
             '    Apk android:', '  u0a301:', '    Wake lock lonely-lock: 1ms partial (1 times) max=1 realtime', '',
             'Per process state tracking available: true']
    return text


def batterystats_service(layout):
    text = ['DUMP OF SERVICE batterystats:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 17594, 18570']
    text += history_f2() if layout == 'a16' else history_f1()
    text += ['', 'Per-PID Stats:', '  PID 1852 wake time: +162ms', '', 'Discharge step durations:', '  #0: +14m40s151ms to 15 (power-save-off)', '']
    text += daily_stats() + stats_since_charge(layout)
    return '\n'.join(text) + '\n' + TRAILER % 'batterystats'


# ------------------------------------------------------------------------------------------
# power, deviceidle
# ------------------------------------------------------------------------------------------
def power_service(layout):
    text = ['DUMP OF SERVICE CRITICAL power:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 20544', 'POWER MANAGER (dumpsys power)', '',
            'Power Manager State:', '  Settings power_manager_constants:', '    no_cached_wake_locks=true', '  mDirty=0x0', '  mWakefulness=Awake',
            '  mIsPowered=false', '  mBatteryLevel=15', '  mLastWakeTime=85435552 (315377 ms ago)', '', 'Settings and Configuration:',
            '  mDreamsSupportedConfig=true', '  mScreenOffTimeoutSetting=60000']
    if layout == 'a16':
        text += ['  mLastWakeUpReason: 1', '  SEC_FEATURE_EXAMPLE: false']
    text += ['', 'Attentive timeout: -1 ms', 'Screen off timeout: 60000 ms', '', 'UID states (changing=false changed=false):', '  UID 1000:   ACTIVE  count=0 state=0']
    if layout == 'a16':
        text += ['', 'Wake Locks: size=2',
                 "  PARTIAL_WAKE_LOCK                 'wake:com.example.user.chat.Holder' ACQ=-936ms (uid=10300 pid=19915 displayId=0 lock=57fbc17)",
                 "  PARTIAL_WAKE_LOCK                 'AudioIn' ACQ=-7mf4sc8dms LONG (uid=1041 isFrozen=false ws=WorkSource{ chains=WorkChain{(10349), (1041)}} "
                 'displayId=-1 lock=7d8a703)', '', 'Suspend Blockers: size=1', '  PowerManagerService.Booting: ref count=0 []', '', 'PowerHistorian:',
                 '  WakeLock Release History:',
                 "  [1]   11-01 21:05:51.977 +4m46s348ms       SCREEN_BRIGHT_WAKE_LOCK           'WindowManager/displayId:0' ON_AFTER_RELEASE DISABLED "
                 '(uid=1000 pid=2682 ws=WorkSource{10300 com.example.user.chat} displayId=0 lock=4751e0)', '  DisplayGroup History:', '',
                 '  WakeUp History:', '   No   Timestamp          UID   ID ST  Reason                         Foreground Package             Caller (Op Package)',
                 '  [1]   11-01 21:05:38.650 1000  0  OFF timeout                        com.example.settings           ',
                 '  [2]   11-01 21:05:52.136 10064 0  ON  application                    com.example.launcher           android',
                 '  [3]   11-02 03:30:00.001 1001  0  ON  unknown                        com.example.dialer             com.example.incallui',
                 '  [4]   short line', '', '  AutomaticBrightness History:', '  [1]   11-01 13:08:31.222 updateAutoBrightness : 335(1.31)', '']
    else:
        text += ['', 'Wake Locks: size=1', "  mLock:168935231 SCREEN_BRIGHT_WAKE_LOCK        'WindowManager' ON_AFTER_RELEASE ACQ=-1s775ms (uid=1000 pid=8107 ws=WorkSource{1000})",
                 '', 'Suspend Blockers: size=1', '  PowerManagerService.WakeLocks: ref count=1', '']
    return '\n'.join(text) + '\n' + TRAILER % 'power'


def deviceidle_service():
    text = ['DUMP OF SERVICE deviceidle:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 9526, 2333', '  Settings:',
            '    flex_time_short=+1m0s0ms', '    light_idle_to=+15m0s0ms', '    wait_for_unlock=true', '  Idling history:',
            '     light-idle: -7h28m15s23ms', '    light-maint: -7h12m14s687ms', '         normal: -6h17m7s310ms (motion)',
            '      deep-idle: -3h50m49s292ms', '  Whitelist (except idle) system apps:', '    com.example.system', '  Whitelist all app ids:', '    10281',
            '    10288', '  mLightEnabled=true  mDeepEnabled=true', '  mForceIdle=false',
            '  mUseMotionSensor=true mMotionSensor={Sensor name="significant", vendor="example", version=1, type=17}', '  mScreenOn=true',
            '  mMotionListener.activatedTimeElapsed=82380012', '  0 stationary listeners registered', '  mState=ACTIVE mLightState=ACTIVE',
            '  mNextLightIdleDelay=+15m0s0ms (flex=+1m0s0ms)', '']
    return '\n'.join(text) + '\n' + TRAILER % 'deviceidle'


# ------------------------------------------------------------------------------------------
# procstats
# ------------------------------------------------------------------------------------------
def procstats_service():
    text = ['DUMP OF SERVICE procstats:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 22526, 797',
            'COMMITTED STATS FROM 2026-11-01-06-05-25:',
            '  * com.example.systemui / u0a385 / v35:', '         TOTAL: 100% (0.00-0.00-0.00/0.00-0.00-0.00/234MB-266MB-322MB over 3)',
            '    Persistent: 92% (0.00-0.00-0.00/0.00-0.00-0.00/234MB-266MB-322MB over 3)', '       Bnd Fgs: 7.7%',
            '  * com.example.user.chat:sync / u10a300 / v5120:', '         TOTAL: 100% (11MB-13MB-16MB/2.8MB-5.4MB-8.4MB/64MB-67MB-73MB over 13)',
            '        (Home): 1.1% (0.00-0.00-0.00/0.00-0.00-0.00/210MB-210MB-210MB over 1)', '  * system / 1000 / v35:', '         TOTAL: 100%',
            '         a line that is not a state', 'Run time Stats:', '  SOff/Norm: +7m47s206ms', '      TOTAL: +1h30m2s419ms', '',
            'Memory usage:', '  Kernel : 734MB (8 samples)', '', 'CURRENT STATS:', 'System memory usage:', '  SOn/Norm: 1', 'Per-Package Stats:',
            '  * com.example.perpackage / u0a1 / v1:', '         TOTAL: 100%', 'Per-UID Stats:', '  * 1000 (3 entries):', '         SOn/Norm/       Top: +1m6s239ms (running)',
            'Process summary:', '  * com.example.summary / u0a300 / v7:', '         TOTAL: 100% (0.00-24MB-49MB/0.00-6.3MB-13MB/119MB-115MB-119MB over 2)',
            '       Bnd Top: 0.06%', 'Run time Stats:', '  SOff/Norm: +1m', 'AGGREGATED OVER LAST 24 HOURS:', 'Per-Package Stats:', '  * com.example.skipped / u0a1 / v1:',
            '         TOTAL: 100%', 'Process summary:', '  * com.example.aggregated / u0a2 / v3:', '         TOTAL: 100% (1.0MB-2.0MB-3.0MB/1MB-1MB-1MB/9MB-9MB-9MB over 4)', '']
    return '\n'.join(text) + '\n' + TRAILER % 'procstats'


# ------------------------------------------------------------------------------------------
# ps
# ------------------------------------------------------------------------------------------
def ps_section():
    text = ['------ PROCESSES AND THREADS (ps -A -T -Z -O pri,nice,rtprio,sched,pcy,time) ------',
            'LABEL                          USER           PID   TID  PPID        VSZ    RSS WCHAN            ADDR S PRI  NI RTPRIO SCH PCY     TIME CMD            ',
            'u:r:init:s0                    root             1     1     0    1814339   7786 0                   0 S  19   0      -   0  fg 00:11:53 init',
            'u:r:init:s0                    root             1   320     0    1814339   7786 do_epoll_wait     0 S  39 -20      -   0  fg 00:00:01 init',
            'u:r:untrusted_app:s0:c168,c256,c512,c768 u0_a168 49555 31831   686 6428896 213352 0                0 S  19   0      -   0  bg 00:00:00 Binder:49555_4',
            'u:r:untrusted_app:s0:c168,c256,c512,c768 u0_a168 49555 31832   686 6428896 213352 0                0 R  19   0      -   0  bg 00:00:05 Signal Catcher',
            'u:r:dumpstate:s0               shell        49177 49177 49641   42321   6472 0                   0 R  39 -20      -   0  fg 00:00:00 ps',
            'too short a line', "------ 0.200s was the duration of 'PROCESSES AND THREADS' ------", '']
    return '\n'.join(text) + '\n'


# ------------------------------------------------------------------------------------------
# meminfo
# ------------------------------------------------------------------------------------------
def meminfo_service(layout, cut):
    text = ['DUMP OF SERVICE HIGH meminfo:', 'Service host process PID: 1234', 'Threads in use: 0/32', 'Client PIDs: 797',
            'Applications Memory Usage (in Kilobytes):', 'Uptime: 88359925 Realtime: 17712157', '']
    if layout == 'a16':
        text += ['Total RSS by process:', '    513,003K: com.example.user.chat (pid 18300 / activities)', '    310,960K: system (pid 8107)', '',
                 'Total RSS by OOM adjustment:', '    693,884K: Native', '         96,912K: com.example.nested (pid 31536)', '',
                 'Total PSS by process:', '    687,382K: com.example.user.chat (pid 18300 / activities)               (  255,444K in swap)',
                 '     84,821K: vendor.example.camera-service_64 (pid 1138)(   81,312K in swap)', '', 'Total PSS by OOM adjustment:', '']
        header = ['** MEMINFO in pid 22526 [com.example.settings] **',
                  '                   Pss      Pss   Shared  Private   Shared  Private  SwapPss      Rss     Heap     Heap     Heap',
                  '                 Total    Clean    Dirty    Dirty    Clean    Clean    Dirty    Total     Size    Alloc     Free',
                  '                ------   ------   ------   ------   ------   ------   ------   ------   ------   ------   ------',
                  '  Native Heap    13693        0     8330    10863       28      592     1790    49615    37363    10455    45198',
                  '  Dalvik Heap    84126        0     8238    84815      168      116      531    80317    73251    82656    47054',
                  ' Dalvik Other     2359        0      464     2248        4       28       24     1790                           ',
                  '     .so mmap     8300       28     1632      208    43637       28       20    79549                           ',
                  '        TOTAL   883131     9166    18337   896580   824732     2784     7523   178716   895276    79652    69763',
                  ' ', ' Dalvik Details', '        .Heap    82917        0        0    82917        0        0        0    82917                           ', ' ',
                  ' App Summary', '                       Pss(KB)                        Rss(KB)', '                        ------                         ------',
                  '           Java Heap:    20476                          39452', '         Native Heap:    10863                          49615',
                  '                Code:     6780                         135736', '               Stack:      964                            988',
                  '            Graphics:    62614                          62614', '       Private Other:     4100', '              System:    18485',
                  '             Unknown:                                    7240', ' ',
                  '           TOTAL PSS:   883131            TOTAL RSS:   178716       TOTAL SWAP PSS:     7523', ' ', ' Objects',
                  '               Views:      440         ViewRootImpl:        3', '         AppContexts:       16           Activities:        4',
                  ' ', ' SQL', '         MEMORY_USED:     2220', '']
    else:
        header = ['** MEMINFO in pid 29945 [com.example.user.chat] **',
                  '                   Pss      Pss   Shared  Private   Shared  Private  SwapPss     Heap     Heap     Heap',
                  '                 Total    Clean    Dirty    Dirty    Clean    Clean    Dirty     Size    Alloc     Free',
                  '                ------   ------   ------   ------   ------   ------   ------   ------   ------   ------',
                  '  Native Heap    89807        0       64    11744        0        0    70344   891932    69103    74474',
                  '  Dalvik Heap     4904        0       32     4904        0        0    85153    46927    81308    81308',
                  '        TOTAL   186447    99337    81421    74443   847794    95917    25946   884400    97752    32093', ' ',
                  ' App Summary', '                       Pss(KB)', '                        ------', '           Java Heap:    11244',
                  '         Native Heap:    11744', '                Code:    81764', '               Stack:       32', '            Graphics:    31376',
                  '       Private Other:     4184', '              System:   102915', ' ', '               TOTAL:   186447       TOTAL SWAP PSS:    25946', ' ',
                  ' Objects', '               Views:     1086         ViewRootImpl:        2', '         AppContexts:       10           Activities:        2', '']
    text += header
    text += ['** MEMINFO in pid 1736 [com.example.keyboard] **', 'no table follows', '']
    if layout == 'a16':
        text += ['Total RAM: 3,725,764K (status moderate)', ' Free RAM:   728,284K (  305,764K cached pss +   338,428K cached kernel +    84,092K free)',
                 '      GPU:   559,584K (  144,592K dmabuf +   414,992K private)', ' Used RAM: 4,412,606K (3,098,582K used pss + 1,314,024K kernel)', '']
    if cut:
        return '\n'.join(text) + "\n*** SERVICE 'meminfo' DUMP TIMEOUT (60000ms) EXPIRED ***\n\n"
    return '\n'.join(text) + '\n' + TRAILER % 'meminfo'


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='a16', zone='Europe/Paris', users=(0, 10), report=NOW, cut=False, newline='\n'):
    text = base.BANNER.format(report=report) + '\n' + base.HEADER[layout] + '\n'
    text += base.properties(layout, zone, 'reboot,userrequested,%d' % base.epoch_s('2026-10-30 07:00:00'))
    text += ps_section()
    text += '------ DUMPSYS CRITICAL (/system/bin/dumpsys) ------\n' + power_service(layout) + "------ 0.500s was the duration of 'DUMPSYS CRITICAL' ------\n\n"
    text += '------ DUMPSYS HIGH (/system/bin/dumpsys) ------\n' + meminfo_service(layout, cut) + "------ 0.500s was the duration of 'DUMPSYS HIGH' ------\n\n"
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    text += account_service(layout, users) + backup_service() + battery_service() + batterystats_service(layout) + content_service(layout)
    text += deviceidle_service() + procstats_service()
    text += thermal_service() + user_service(layout)
    text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n== dumpstate: done (id 1)\n"
    return text.replace('\n', newline)


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16').encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt', build_report('a10', users=(0,), newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_two_reports'] = [('Dump1/dumpstate.txt', build_report('a16', zone='Asia/Kolkata').encode('utf-8')),
                                    ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                                     build_report('a10', zone='America/Sao_Paulo', users=(0,)).encode('utf-8'))]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report=NOW) + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\nDUMP OF SERVICE account:\nUser UserInfo{0:x:1}:\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_accountspower_fixture_out')
