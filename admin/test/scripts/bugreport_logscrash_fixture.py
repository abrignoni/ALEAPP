"""Builds the synthetic Android bug report texts used by the Bug Report logs and crash test cases.

Every value is invented: package names are under example.*, the device, build and time values are made up, the
user ids and times are fixed, the protobuf tombstones are encoded here from invented values. Only the structure is
taken from real bug reports: the logcat, kernel, thread dump, dropbox, reset history and vendor service sections as
the platform prints them. Two layouts are built:

* ``l16``: the layout of Android 14 and later (logcat with a uid column and nanosecond dump times with an offset,
  kernel lines with a task tag, dropbox listings and ``dumpsys dropbox -p`` prints, the Samsung reset history files
  and Samsung vendor services);
* ``l10``: the layout of Android 10 (logcat without a uid column, dump times without an offset, kernel lines with a cpu
  prefix, no reset history and no vendor services).

Usage: python bugreport_logscrash_fixture.py <output folder>
Writes one zip per test case into the folder and prints their names and sizes.
"""
import io
import os
import sys

from admin.test.scripts import bugreport_fixture as base

LONG_WORDS = 'word ' * 20


# ------------------------------------------------------------------------------------------
# logcat
# ------------------------------------------------------------------------------------------
def system_log(layout, odd=False):
    if layout == 'l16':
        lines = [
            '--------- beginning of crash',
            '11-01 21:05:01.100  1000  1117  1117 I ExampleBoot: invented line of the crash buffer',
            '--------- beginning of system',
            '11-01 21:05:02.250 10201  2201  2260 D ExampleChat: invented message one',
            '11-01 21:05:02.250  root   501   501 W init    : padded tag line',
            '11-01 21:05:03.000 shell   600   600 E ExampleDaemon: error with a colon: inside the message',
            '    a continuation line of the message above',
            '11-01 21:05:03.500 10201  2201  2260 I ExampleChat: message with trailing text   ',
            '11-01 21:05:04.000 10202  2301  2301 V Tag With Spaces: message after a tag with spaces',
            '11-01 21:05:04.100 10202  2301  2301 F EmptyMessage:',
            '--------- beginning of main',
            '11-01 21:05:05.001 10203  2401  2402 S ExampleMain: silent level line',
            '11-02 09:15:00.000  1000  1117  1190 D ExampleLate: line a few seconds before the report time',
            '11-03 00:00:00.000  1000  1117  1190 D ExampleFuture: line less than a day after the report time',
            '11-04 01:00:00.000  1000  1117  1190 D ExampleOlder: line more than a day after the report time',
            '11-01 21:05:06.000 10201  2201  2260 I ExampleLong: ' + LONG_WORDS,
        ]
        if odd:
            lines.append('11-01 21:05:07.000 10201  2201  2260 I ExampleOdd: control\x01 char and � replacement')
    else:
        lines = [
            '--------- beginning of system',
            '11-01 21:05:02.250  2201  2260 D ExampleChat: invented message one',
            '11-01 21:05:02.250   501   501 W init    : padded tag line',
            '--------- beginning of main',
            '11-01 21:05:05.001  2401  2402 I ExampleMain: plain threadtime line without a uid column',
        ]
    head = '------ SYSTEM LOG (logcat -v threadtime -v printable -v uid -d *:v) ------\n'
    return head + '\n'.join(lines) + "\n------ 1.000s was the duration of 'SYSTEM LOG' ------\n\n"


def system_log_after_done():
    return ('------ SYSTEM LOG AFTER DONE (logcat -v threadtime -v printable -v uid -d *:v -T 2026-11-02 10:15:31.000) ------\n'
            '--------- beginning of system\n'
            '11-02 10:15:31.500  1000  1117  1190 D ExampleAfter: line printed after the dump finished\n'
            "------ 0.100s was the duration of 'SYSTEM LOG AFTER DONE' ------\n\n")


def event_log(layout):
    uid = '  1000' if layout == 'l16' else ''
    lines = [
        '11-01 21:05:10.100%s  1500  1520 I am_proc_bound: [0,4321,com.example.user.chat]' % uid,
        '11-01 21:05:10.200%s  1500  1520 I notification_enqueue: [10300,1,com.example.user.chat,1,invented-key' % uid,
        ',0,Notification(channel=invented-channel flags=ONLY_ALERT_ONCE)]',
        '11-01 21:05:11.000%s  1500  1520 I power_partial_wake_state: [REL,408,*job*r/@example]' % uid,
    ]
    head = '------ EVENT LOG (logcat -b events -v threadtime -v printable -v uid -d *:v) ------\n'
    if layout == 'l16':
        head += '--------- beginning of events\n'
    return head + '\n'.join(lines) + "\n------ 0.100s was the duration of 'EVENT LOG' ------\n\n"


# ------------------------------------------------------------------------------------------
# kernel
# ------------------------------------------------------------------------------------------
def kernel_log(layout):
    if layout == 'l16':
        lines = ['<6>[    0.000000] Booting Linux on physical CPU 0x0',
                 '<6>[12345.678901][T21461] invented_driver: input id(0) value(1)',
                 '<6>[12345.678950][ T9474] [wlan] invented line with a space in the task tag',
                 '<4>[12346.000001][C1] invented line with a cpu tag',
                 '<6>[12347.123456] [ 2:  kworker/u16:2:   86] invented line with cpu, comm and pid',
                 'a line without a stamp',
                 '',
                 '<6>[12348.000000]',
                 "Skipping '/system/xbin/example tool' on user build."]
    else:
        lines = ['<6>[    0.000000] c0 Booting Linux on physical CPU 0x0',
                 '<5>[    1.500000] c1 invented line with a cpu prefix',
                 '<6>[    2.000000] plain invented line']
    return '------ KERNEL LOG (dmesg) ------\n' + '\n'.join(lines) + '\n\n'


def last_kmsg(layout):
    if layout == 'l16':
        lines = [' 0.785203]  [ 2:  kworker/u16:2:   86] invented first line cut by the ring buffer',
                 '[    0.785860]  [ 2:  kworker/u16:2:   86] invented message',
                 '[   62.000001][    T1] invented line with a task tag']
    else:
        lines = ['[    0.782045] c0 invented card line<1>', '[62513.614625] c0 reboot: Restarting system with command']
    return '------ LAST KMSG (/proc/last_kmsg) ------\n' + '\n'.join(lines) + '\n\n'


# ------------------------------------------------------------------------------------------
# thread dumps
# ------------------------------------------------------------------------------------------
def traces_just_now(layout):
    if layout == 'l16':
        stamp1, stamp2 = '2026-11-02 10:15:00.123456789+0000', '2026-11-02 10:15:01.000000001+0100'
        text = (
            '------ VM TRACES JUST NOW (/data/log/dumptrace_EXAMPLE: 2026-11-02 10:15:30) ------\n\n\n'
            '----- pid 1099 at %s -----\n' % stamp1 +
            'Cmd line: /apex/com.example.runtime/bin/exampled\n'
            "ABI: 'arm64'\n\n"
            '"binder:1099_2" sysTid=1099\n'
            '    #00 pc 3456789abc23229a  /apex/com.example.runtime/lib64/libc.so (__epoll_pwait+8) (BuildId: 0000)\n'
            '    #01 pc 5678901234804320  /apex/com.example.runtime/bin/exampled (Looper::pollOnce+488) (BuildId: 0000)\n\n'
            '"exampled.writer" sysTid=1104\n'
            '    #00 pc 3456789abc232cd6  /apex/com.example.runtime/lib64/libc.so (__ppoll+4) (BuildId: 0000)\n\n'
            '----- end 1099 -----\n\n'
            '----- pid 2201 at %s -----\n' % stamp2 +
            'Cmd line: com.example.user.chat\n'
            "Build fingerprint: 'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys'\n"
            'DALVIK THREADS (3):\n'
            '"main" prio=5 tid=1 Native\n'
            '  | group="main" sCount=1 ucsCount=0 flags=1 obj=0x70000010 self=0xb400000000001000\n'
            '  | sysTid=2201 nice=-10 cgrp=top-app sched=0/0 handle=0x7000000001\n'
            '  | state=S schedstat=( 111111111 222222222 333 ) utm=17 stm=9 core=3 HZ=100\n'
            '  | stack=0x6fb3102abc-0x6fb310cabc stackSize=8188KB\n'
            '  | held mutexes=\n'
            '  native: #00 pc 34abaa12  /apex/com.example.runtime/lib64/libc.so (__epoll_pwait+8) (BuildId: 0000)\n'
            '  at android.os.MessageQueue.nativePollOnce(Native method)\n'
            '  at android.os.Looper.loop(Looper.java:363)\n'
            'DumpLatencyMs: 13.7521\n\n'
            '"ReferenceQueueDaemon" daemon prio=5 tid=6 Waiting\n'
            '  | group="system" sCount=1 ucsCount=0 flags=1 obj=0x2000210 self=0xa8567875ef611812\n'
            '  | sysTid=2206 nice=4 cgrp=background sched=0/0 handle=0x1f961cb93c\n'
            '  | state=S schedstat=( 127683573 821600306 217 ) utm=11 stm=10 core=1 HZ=100\n'
            '  | held mutexes=\n'
            '  at java.lang.Object.wait(Native method)\n'
            '  - waiting on <0x36b392b4> (a java.lang.Class<java.lang.ref.ReferenceQueue>)\n'
            '  at java.lang.Daemons$Daemon.run(Daemons.java:135)\n\n'
            '"NativeHelper" prio=5 (not attached)\n'
            '  | sysTid=2210 nice=0 cgrp=foreground\n'
            '  native: #00 pc 34abaa12  /apex/com.example.runtime/lib64/libc.so (syscall+28) (BuildId: 0000)\n\n'
            '----- end 2201 -----\n\n'
            '----- Waiting Channels: pid 2201 at %s -----\n' % stamp2 +
            'sysTid=2201     wchan=futex_wait_queue\n'
            '"not a thread" lines inside a waiting channels block are ignored\n'
            '----- end 2201 -----\n\n'
            "------ 0.500s was the duration of 'VM TRACES JUST NOW' ------\n\n")
    else:
        text = (
            '------ VM TRACES JUST NOW (/data/anr/traces.txt.bugreport: 2026-11-02 10:15:30) ------\n'
            '\n----- pid 2201 at 2026-11-02 10:15:00 -----\n'
            'Cmd line: com.example.user.chat\n'
            'DALVIK THREADS (1):\n'
            '"main" prio=5 tid=1 Native\n'
            '  | sysTid=2201 nice=-1 cgrp=default sched=0/0 handle=0x7e9b2f2d48\n'
            '  | state=S schedstat=( 120 340 5 ) utm=1 stm=2 core=0 HZ=100\n'
            '  native: #00 pc 000000000007f1e4  /system/lib64/libc.so (__epoll_pwait+8)\n'
            '  at android.os.MessageQueue.nativePollOnce(Native method)\n\n'
            '----- end 2201 -----\n\n')
    return text


def traces_at_last_anr(layout):
    if layout != 'l16':
        return ''
    return (
        '------ VM TRACES AT LAST ANR (/data/anr/anr_2026-10-30-12-00-00-000: 2026-10-30 12:00:00) ------\n'
        'Subject: Input dispatching timed out (example.user.chat/.Main)\n'
        'RssHwmKb: 1000\n\n'
        '----- pid 2201 at 2026-10-30 11:59:58.000000000+0000 -----\n'
        'Cmd line: com.example.user.chat\n'
        '"main" prio=5 tid=1 Blocked\n'
        '  | sysTid=2201 nice=0 cgrp=top-app sched=0/0 handle=0x7000000001\n'
        '  | state=S schedstat=( 1 2 3 ) utm=5 stm=6 core=2 HZ=100\n'
        '  at example.user.chat.Main.onCreate(Main.java:10)\n'
        '  - waiting to lock <0x01020304> (a java.lang.Object) held by thread 12\n\n'
        '----- end 2201 -----\n\n')


# ------------------------------------------------------------------------------------------
# dropbox
# ------------------------------------------------------------------------------------------
DROP_NOTE = ('Drop box contents: 5 entries\nMax entries: 1000\nLow priority rate limit period: 2000 ms\n'
             'Low priority tags: {data_app_wtf, keymaster}\n')


def dropbox_service(layout):
    lines = ['Service host process PID: 1500', 'Threads in use: 0/32', 'Client PIDs: 4321, 466']
    if layout == 'l16':
        lines.append('Unknown argument: -a')
    lines += DROP_NOTE.rstrip('\n').split('\n')
    lines += ['',
              '2026-11-01 20:00:00 system_app_crash (text, 1885 bytes)',
              '    Process: com.example.user.chat/PID: 4321/UID: 10300/Flags: 0x1 ...',
              '2026-11-01 20:01:00 keymaster (contents lost)',
              '2026-11-01 20:02:00 storage_trim (text, 15 bytes)',
              '    example 0 1234',
              '2026-11-01 20:03:00 SYSTEM_RESTART (compressed text, 514 bytes)',
              '    isPrevious: true/Build: example/examplephone ...',
              '2026-11-01 20:04:00 system_server_wtf (data, 20 bytes)']
    return ('DUMP OF SERVICE dropbox:\n' + '\n'.join(lines) +
            '\n--------- 0.126s was the duration of dumpsys dropbox, ending at: 2026-11-02 10:15:20\n'
            '-------------------------------------------------------------------------------\n')


def dropbox_print(title, tag, entries):
    head = '------ %s (/system/bin/dumpsys -T 30000 dropbox -p %s) ------\n' % (title, tag) + DROP_NOTE + 'Searching for: %s\n\n' % tag
    if not entries:
        return head + '(No entries found.)\n------ 0.020s was the duration of \'%s\' ------\n' % title
    body = ''
    for stamp, kind, headers, first in entries:
        body += '=' * 40 + '\n%s %s (%s)\n' % (stamp, tag, kind)
        body += '\n'.join(headers) + ('\n' if headers else '')
        body += '\n' + first + '\n    at example.user.chat.Main.run(Main.java:1)\n\n'
    body += '=' * 40 + '\n'
    return head + body + "------ 0.020s was the duration of '%s' ------\n" % title


def dropbox_sections(layout):
    app = dropbox_print('DROPBOX SYSTEM APP CRASHES', 'system_app_crash', [
        ('2026-11-01 20:00:00', 'text, 1885 bytes',
         ['Process: com.example.user.chat', 'PID: 4321', 'UID: 10300', 'Flags: 0x841e63d3',
          'Package: com.example.user.chat v12 (1.2.3)', 'Package: com.example.user.helper v3 (0.3)', 'Foreground: No',
          'Build: example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys'],
         'java.lang.IllegalStateException: invented crash message'),
        ('2026-11-01 20:30:00', 'text, 900 bytes', ['Process: com.example.user.chat:sync', 'PID: 4400', 'UID: 10300',
                                                    'Foreground: Yes', 'Subject: invented subject line'],
         'java.lang.RuntimeException: second invented crash')])
    server = dropbox_print('DROPBOX SYSTEM SERVER CRASHES', 'system_server_crash', [])
    out = server + app
    if layout == 'l16':
        out += dropbox_print('DROPBOX SYSTEM WATCHDOG CRASHES', 'system_server_watchdog', [])
    return out


# ------------------------------------------------------------------------------------------
# reset history (Samsung)
# ------------------------------------------------------------------------------------------
def reset_sections():
    ap = ('------ AP RESET INFO EXTEND (/data/system/users/service/data/eRR.p: 2026-11-02 10:15:30) ------\r\n'
          'LOGM�\x00\x00\r\n\r\n'
          '2026-02-03 10:11:12+0700 |    ON    | RP    | EXAMPLEBUILD1 [13]\r\n'
          '2026-02-03 10:12:13+0700 | SHUTDOWN |       | REASON: [FactoryTest] invented reset [13] ,1\r\n'
          '2010-01-01 00:00:12+0000 |          | RP    | [14] / 3956mV (52%) \r\n'
          '2010-01-01 00:00:12+0000 |   LPM    |       |\r\n'
          '2026-04-27 14:15:37+0000 |  REBOOT  |       | REASON: invented reason (ACR) [15]\r\n'
          '2026-05-23 04:31:33+0000 | PLATFORM | PF_SR | EXAMPLEBUILD1 / Invented restart [31]\r\n'
          '2026-10-30 07:00:00-0330 |    ON    | NP    | EXAMPLEBUILD2 / apex_updated \r\n'
          "------ 0.003s was the duration of 'AP RESET INFO EXTEND' ------\r\n\r\n")
    power = ('------ POWER OFF RESET REASON (/data/log/power_off_reset_reason.txt: 2026-11-02 10:15:30) ------\n'
             '26/09/20 02:12:41\n'
             'reason : no power\n'
             'java.lang.Exception: It is not an exception!! just save the trace ShutdownThread.shutdown\n'
             '\tat com.example.server.power.ShutdownThread.shutdownInner(example:212)\n'
             '\tat com.example.server.power.ShutdownThread.systemShutdown(example:34)\n'
             '\tat com.example.server.BatteryService$16.run(example:160)\n'
             '\tat android.os.Handler.handleCallback(Handler.java:995)\n'
             '\tat android.os.Handler.dispatchMessage(Handler.java:103)\n'
             '\tat android.os.Looper.loop(Looper.java:363)\n'
             '02:12:51  2026-09-20 02:12:51+0000 | SHUTDOWN |       | REASON: no power [64]\n'
             '02:12:51  terminating init service start\n'
             '2026-09-20 06:14:37+0000 |          | RP    | [65] / 3600mV (2%) \n\n'
             '26/09/22 16:03:21\n'
             'reason : invented-low-memory\n'
             'java.lang.Exception: It is not an exception!! ShutdownThread.shutdown\n'
             '\tat com.example.server.power.ShutdownThread.shutdownInner(example:212)\n'
             '\tat com.example.server.power.ShutdownThread.reboot(example:50)\n'
             '\tat com.example.server.power.PowerManagerService$4.run(example:43)\n'
             '2026-09-17 15:03:10+0000 |    ON    | RP    | EXAMPLEBUILD1 [67]\n'
             "------ 0.015s was the duration of 'POWER OFF RESET REASON' ------\n\n")
    backup = ('------ POWER OFF RESET REASON BACKUP (/data/log/power_off_reset_reason_backup.txt: 2026-09-14 04:19:35) ------\n'
              '26/08/30 21:39:13\n'
              'reason : userrequested\n'
              'java.lang.Exception: It is not an exception!! ShutdownThread.shutdown\n'
              '\tat com.example.server.power.ShutdownThread.shutdownInner(example:212)\n'
              "------ 0.008s was the duration of 'POWER OFF RESET REASON BACKUP' ------\n\n")
    return ap + power + backup


# ------------------------------------------------------------------------------------------
# vendor services
# ------------------------------------------------------------------------------------------
def vendor_services(cut=False):
    head = 'Service host process PID: 1500\nThreads in use: 1/32\nClient PIDs: 466\n'
    knox = ('DUMP OF SERVICE knoxguard_service:\n' + head +
            'KG30.KnoxGuard30Service state: \n'
            'ADB blocked : false\n'
            '2026-02-03 10:13:14 : [action] android.intent.action.TIMEZONE_CHANGED\n'
            '2026-02-03 10:14:15 : [action] kgState : Prenormal | isNetworkConnected : false\n')
    if cut:
        knox += "*** SERVICE 'knoxguard_service' DUMP TIMEOUT (10000ms) EXPIRED ***\n"
    sve = ('DUMP OF SERVICE SveService:\n' + head + '\nDump of SecVideoEngineImpl:\n'
           '  02/03/2026 03:05:06.789   > Created (pid: 3333, binary: EXAMPLEBUILD1)\n'
           '  05/09/2026 14:16:16.768   > Created (pid: 2222, binary: EXAMPLEBUILD1)\n')
    ims = ('DUMP OF SERVICE secims:\n' + head + 'EventLog(ImsServiceStub):\n'
           '  02/03/*026 02:54:29.863   > Created (pid: *489, binary: EXAMPLEBUILD1)\n'
           '  02/03/*026 09:54:11.369   Link to Phone Binder Death\n')
    loc = ('DUMP OF SERVICE sec_location:\n' + head + 'SLocation ver : 1.0.0.1\n'
           ' ***** C-Loc history ***** \n'
           '[2026-10-30 08:15:30.111] L/ab12/example.user.chat/0/10300/Bg/{Prm:Fn/Bg}/AcLmt:true\n'
           '[2026-10-30 08:15:33.222] L/ab12/example.user.chat/REM\n')
    wifi = ('DUMP OF SERVICE sem_wifi:\n' + head + 'Wi-Fi api call history:\n[]\n'
            'Wi-Fi control history from provider:\n'
            'lastControlTime: 2026/08/14 18:20:30 , packageName: example.user.chat, lastControl: true\n')
    if cut:
        wifi += "*** SERVICE 'sem_wifi' DUMP TIMEOUT (10000ms) EXPIRED ***\n"
    nfc = ('DUMP OF SERVICE nfc SamsungExtension:\nExample NCI Version: Major 0x09 Minor 0x09\n'
           + 'QmFzZTY0TG9va2luZ0V4YW1wbGVQYXlsb2FkQmFzZTY0TG9va2luZ0V4YW1wbGVQYXlsb2FkMDEyMzQ1Njc4OQ==\n' * 3 +
           'DEBUG LOG START\n05-09 08:41:12.345 D [NFC_SE]SamsungExtension invented state line\n'
           '11-20 12:58:59.973 D [NFC_SE]SamsungExtension a line of the previous year\n'
           '--------- 0.251s was the duration of dumpsys samsungnfc, ending at: 2026-11-02 10:15:20\n'
           + '-' * 60 + '\n')
    persona = 'DUMP OF SERVICE persona:\n' + head + 'Last removed user:\n====================\n UID : 1000\n2010.01.01.00.01.22\n'
    other = 'DUMP OF SERVICE HqmManagerService:\n' + head + 'HW Paramlist - Count: Sm20\n  | AP | SYSC | 0.0 |  | Alarm 24H |\n'
    tail = '--------- 0.140s was the duration of dumpsys %s, ending at: 2026-11-02 10:15:20\n'
    out = ''
    for text, name in ((knox, 'knoxguard_service'), (sve, 'SveService'), (ims, 'secims'), (loc, 'sec_location'),
                       (wifi, 'sem_wifi'), (nfc, 'nfc SamsungExtension'), (persona, 'persona'), (other, 'HqmManagerService')):
        out += text + (tail % name) + '-' * 79 + '\n'
    return out


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='l16', zone='Europe/Paris', report='2026-11-02 10:15:30', cut=False, odd=False, newline='\n',
                 with_banner=True):
    kind = 'a16' if layout == 'l16' else 'a10'
    text = (base.BANNER.format(report=report) if with_banner else '') + '\n' + base.HEADER[kind] + '\n'
    text += base.properties(kind, zone, 'reboot,userrequested,%d' % base.epoch_s('2026-10-30 07:00:00'))
    text += system_log(layout, odd)
    if layout == 'l16':
        text += system_log_after_done()
    text += event_log(layout)
    text += kernel_log(layout)
    text += last_kmsg(layout)
    text += traces_just_now(layout) + traces_at_last_anr(layout)
    if layout == 'l16':
        text += reset_sections()
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    text += dropbox_service(layout)
    if layout == 'l16':
        text += vendor_services(cut)
    text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"
    text += dropbox_sections(layout)
    text += '== dumpstate: done (id 1)\n'
    return text.replace('\n', newline)


CUT_MARK = '11-01 21:05:06.000 10201  2201  2260 I ExampleLong:'
CUT_LINE = "*** command '/system/bin/logcat -d' timed out after 60.001s (killing pid 99)\n"


def build_cut_report():
    """The text with a command stopped by a time limit inside the system log and two cut vendor service dumps."""
    return build_report('l16', cut=True).replace(CUT_MARK, CUT_LINE + CUT_MARK, 1)


# ------------------------------------------------------------------------------------------
# tombstones and anr files inside the zip
# ------------------------------------------------------------------------------------------
def _varint(value):
    out = bytearray()
    while True:
        part = value & 0x7f
        value >>= 7
        if value:
            out.append(part | 0x80)
        else:
            out.append(part)
            return bytes(out)


def _field(number, wire, payload):
    return _varint((number << 3) | wire) + payload


def _text_field(number, text):
    data = text.encode('utf-8')
    return _field(number, 2, _varint(len(data)) + data)


def _int_field(number, value):
    if value < 0:
        value += 1 << 64
    return _field(number, 0, _varint(value))


def tombstone_proto(with_headers=False):
    """An invented debuggerd Tombstone message (and, when asked, the wrapper that carries headers)."""
    signal = _int_field(1, 6) + _text_field(2, 'SIGABRT') + _int_field(3, -1) + _text_field(4, 'SI_QUEUE')
    message = (_text_field(2, 'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys') +
               _text_field(4, '2026-10-09 18:07:22.123456789+0000') + _int_field(5, 5001) + _int_field(6, 5002) +
               _int_field(7, 1055) + _text_field(9, 'com.example.user.nfc') + _text_field(9, '--arg') +
               _field(10, 2, _varint(len(signal)) + signal) + _text_field(14, 'invented abort message') +
               _int_field(20, 5551))
    if with_headers:
        return _field(1, 2, _varint(len(message)) + message) + _int_field(2, 0)
    return message


def tombstone_text(stamp='2026-10-09 18:07:22.123456789+0000', process='com.example.user.nfc'):
    return ("*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***\n"
            "Build fingerprint: 'example/examplephone/examplephone:16/EXAMPLE.260101.001/1001:user/release-keys'\n"
            "Revision: '4'\nABI: 'arm64'\nTimestamp: %s\nProcess uptime: 5551s\nCmdline: %s\n"
            "pid: 5001, tid: 5002, name: exampleThread  >>> %s <<<\nuid: 1055\n"
            "signal 6 (SIGABRT), code -1 (SI_QUEUE), fault addr --------\n"
            "Abort message: 'invented abort message'\n\n14 total frames\nbacktrace:\n"
            "      #00 pc 3456789abcd01e6e  /apex/com.example.runtime/lib64/libc.so (abort+156)\n"
            % (stamp, process, process))


def anr_file():
    return ('Subject: No response to onStopJob, (1234567, com.example.user.chat)\nRssHwmKb: 1000\n\n\n'
            '--- CriticalEventLog ---\ncapacity: 20\n\n'
            '----- dumping pid: 4321 at 855776163\n\n'
            '----- pid 4321 at 2026-10-14 04:22:59.123456789+0000 -----\n'
            'Cmd line: com.example.user.chat\nDALVIK THREADS (2):\n'
            '"main" prio=5 tid=1 Native\n'
            '  | sysTid=4321 nice=0 cgrp=background sched=0/0 handle=0x7000000001\n'
            '  | state=S schedstat=( 111111111 222222222 333 ) utm=17 stm=9 core=0 HZ=100\n'
            '  native: #00 pc 34abaa12  /apex/com.example.runtime/lib64/libc.so (__epoll_pwait+8)\n'
            '  at android.os.MessageQueue.nativePollOnce(Native method)\n\n'
            '"androidx.work-1" prio=5 tid=56 Sleeping\n'
            '  | sysTid=4400 nice=0 cgrp=background sched=0/0 handle=0x1a5d03193c\n'
            '  | state=S schedstat=( 3136403181 4823267837 24038 ) utm=112 stm=539 core=0 HZ=100\n'
            '  at java.lang.Thread.sleep(Native method)\n\n'
            '----- end 4321 -----\n')


def bug_report_zip(layout='l16', members=True, **kwargs):
    """The zip a device keeps: main_entry.txt, the main text, and the files of the data folder a bug report carries."""
    main_text = 'bugreport-example-%s-2026-11-02-10-15-30.txt' % ('EXAMPLE' if layout == 'l16' else 'EXOLD')
    files = [('main_entry.txt', main_text.encode()), (main_text, build_report(layout, **kwargs).encode('utf-8')),
             ('dumpstate_log.txt', b'dumpstate log of an invented device\n'), ('version.txt', b'2.0')]
    if members:
        files += [('FS/data/anr/anr_2026-10-14-04-23-05-111', anr_file().encode('utf-8')),
                  ('FS/data/anr/trace_00', b''),
                  ('FS/data/tombstones/tombstone_00', tombstone_text().encode('utf-8')),
                  ('FS/data/tombstones/tombstone_00.pb', tombstone_proto()),
                  ('FS/data/tombstones/tombstone_01', b''),
                  ('FS/data/tombstones/tombstone_02', tombstone_text('2026-10-08 10:00:00.000000000-0500',
                                                                      'com.example.user.chat').encode('utf-8')),
                  ('FS/data/tombstones/tombstone_02.pb', tombstone_proto(with_headers=True)),
                  ('FS/data/tombstones/tombstone_03.pb', b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'),
                  ('FS/data/tombstones/notes.txt', b'not a tombstone member\n'),
                  ('FS/data/anr/readme', b'not an anr member\n')]
    buffer = io.BytesIO()
    base.write_zip(buffer, files)
    return buffer.getvalue()


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_l16'] = [('Dump/dumpstate.txt', build_report('l16').encode('utf-8'))]
    out['synthetic_l10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                             build_report('l10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_zip_on_device'] = [
        ('Dump/data/user_de/0/com.android.shell/files/bugreports/bugreport-example-2026-11-02-10-15-30.zip',
         bug_report_zip('l16', zone='Asia/Kolkata', report='2026-11-02 15:45:30'))]
    out['synthetic_two_reports'] = [
        ('Dump1/bugreport-example-EXAMPLE-2026-11-02-10-15-30.zip', bug_report_zip('l16', zone='Asia/Kolkata')),
        ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt', build_report('l10', zone='America/Sao_Paulo').encode('utf-8'))]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_cut_report().encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report='2026-11-02 10:15:30') + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\n------ SYSTEM LOG (logcat) ------\n'
                                                             b'11-01 21:05:02.250  1000  1  1 I x: y\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    odd = build_report('l16', zone='', odd=True).encode('utf-8')
    odd = b'\xef\xbb\xbf' + odd.replace(b'invented message one', b'invented \xe9 message\x00 one', 1).replace(
        b'padded tag line', b'padded\rtag\x0cline', 1) + b'\xff\xfe\n'
    out['synthetic_odd_bytes'] = [('Dump/dumpstate.txt', odd)]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_logscrash_fixture_out')
