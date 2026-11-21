"""Builds the synthetic Android bug report texts used by the Android Bug Report permission test cases.

Every value is invented: package names are under example.*, the times and uids are made up.
Only the structure is taken from real bug reports: the banner and header lines (from
``bugreport_fixture``), the SYSTEM PROPERTIES section, and the package, appops, role and
permissionmgr service dumps with the section trailers the platform prints. Three layouts:

* ``a16``: Android 16 style. Attribution tag lines under the ops, proxy text, ``Capability``
  lines, a Shared users block, per-user runtime permissions, a permissionmgr dump, no role
  dump (as the Samsung reports of the tested set);
* ``a15``: Android 15 style with a second user (11), the ``ROLE STATE`` dump with
  fallback_enabled lines, install permission lines that end with ``userId=11``;
* ``a10``: Android 10 style. No tag lines, no capability lines, ``from uid=`` watchers,
  ``ROLE MANAGER STATE``, no permissionmgr dump, and a ``runtime permissions:`` heading
  printed one level deeper after an ``overlay paths:`` list.

Usage: python bugreport_permissions_fixture.py <output folder>
"""
import os
import sys
from datetime import datetime, timedelta

from admin.test.scripts import bugreport_fixture as base

NOW = '2026-11-02 10:15:12'
NOW_MS = 500          # the dump instant is NOW plus these milliseconds


def offset_text(milliseconds):
    """``-1m3s20ms`` style text of a number of milliseconds before the dump instant."""
    total = milliseconds
    parts = []
    for unit, size in (('d', 86400000), ('h', 3600000), ('m', 60000), ('s', 1000)):
        if total >= size:
            parts.append('%d%s' % (total // size, unit))
            total %= size
    parts.append('%dms' % total)
    return '-' + ''.join(parts)


def stamp(milliseconds_before):
    """``(wall time text, offset text)`` for an instant that many milliseconds before the dump instant."""
    now = datetime.strptime(NOW, '%Y-%m-%d %H:%M:%S') + timedelta(milliseconds=NOW_MS)
    moment = now - timedelta(milliseconds=milliseconds_before)
    return moment.strftime('%Y-%m-%d %H:%M:%S.') + '%03d' % (moment.microsecond // 1000), offset_text(milliseconds_before)


# ------------------------------------------------------------------------------------------
# package service
# ------------------------------------------------------------------------------------------
def permission_table(layout):
    rows = (('android.permission.EXAMPLE_SIGNATURE', 'android', 1000, '[]', 'signature|privileged', '0x0'),
            ('android.permission.EXAMPLE_DANGEROUS', 'android', 1000, '[]', 'dangerous', '0x0'),
            ('com.example.user.chat.permission.SYNC', 'com.example.user.chat', 10100, '[]', 'signature', '0x0'),
            ('android.permission.EXAMPLE_GROUPED', 'android', 1000, '[2001, 3003]', 'normal|instant', '0x20'))
    text = ['Permissions:']
    for name, source, uid, gids, prot, flags in rows:
        text.append('  Permission [%s] (%x):' % (name, base.hash_text(name)))
        text.append('    sourcePackage=%s' % source)
        text.append('    uid=%d gids=%s type=0 prot=%s' % (uid, gids if layout != 'a10' else 'null', prot))
        text.append('    perm=PermissionInfo{abc123 %s}' % name)
        if layout == 'a10':
            text.append('    packageSetting=PackageSetting{def456 %s/%d}' % (source, uid))
        else:
            text.append('    flags=%s' % flags)
    return '\n'.join(text) + '\n'


def package_entry(layout, name, app_id, install, users, shared=None):
    """One Package [..] block. ``install`` is a list of permission texts; ``users`` is {user: [permission texts]}."""
    lines = ['  Package [%s] (%x):' % (name, base.hash_text(name))]
    lines.append('    %s=%d' % ('appId' if layout != 'a10' else 'userId', app_id))
    if shared:
        lines.append('    sharedUser=SharedUserSetting{abc123 %s}' % shared)
    lines += ['    pkg=Package{def456 %s}' % name, '    codePath=/system/app/%s' % name.rsplit('.', 1)[-1],
              '    versionCode=1 minSdk=29 targetSdk=35', '    versionName=1.0', '    flags=[ SYSTEM HAS_CODE ]',
              '    declared permissions:', '      %s.permission.DECLARED: prot=signature' % name]
    if install:
        lines.append('    install permissions:')
        lines += ['      ' + text for text in install]
    for user, runtime in users.items():
        lines.append('    User %d: ceDataInode=%d installed=true hidden=false suspended=false stopped=false enabled=0'
                     % (user, 1000 + user))
        if layout == 'a10':
            # this layout prints the heading one level deeper after an overlay paths list
            lines += ['    overlay paths:', '      /product/overlay/Example.apk']
            if runtime:
                lines.append('      runtime permissions:')
        else:
            lines.append('      installReason=0')
            if runtime:
                lines.append('      runtime permissions:')
        lines += ['        ' + text for text in runtime]
    return '\n'.join(lines) + '\n'


def package_service(layout, cut=False):
    second = 11 if layout == 'a15' else 10
    chat_users = {0: ['android.permission.CAMERA: granted=false, flags=[ USER_SENSITIVE_WHEN_GRANTED]',
                      'android.permission.READ_CONTACTS: granted=true, flags=[ USER_SET|USER_SENSITIVE_WHEN_GRANTED]']}
    install = ['android.permission.INTERNET: granted=true', 'android.permission.EXAMPLE_PRIV: granted=false']
    if layout != 'a10':
        chat_users[second] = ['android.permission.CAMERA: granted=true, flags=[ USER_SET]']
        install.append('android.permission.SCHEDULE_EXACT_ALARM: granted=true, flags=[ GRANTED_BY_ROLE]')
    if layout == 'a15':
        install.append('android.permission.SYSTEM_ALERT_WINDOW: granted=false, userId=11')
    text = ['DUMP OF SERVICE package:', 'Service host process PID: 2682', 'Threads in use: 1/32',
            'Database versions:', '  Internal:', '    sdkVersion=%s databaseVersion=3' % ('36' if layout == 'a16' else '29'), '']
    text.append(permission_table(layout))
    text.append('Packages:')
    body = '\n'.join(text) + '\n'
    body += package_entry(layout, 'com.example.user.chat', 10100, install, chat_users)
    body += package_entry(layout, 'com.example.system.settings', 1000, [], {0: ['android.permission.POST_NOTIFICATIONS: granted=true, flags=[ GRANTED_BY_DEFAULT]']},
                          shared='android.uid.system/1000')
    body += package_entry(layout, 'com.example.system.empty', 10110, [], {0: []})
    body += '\nHidden system packages:\n'
    body += package_entry(layout, 'com.example.system.updated', 10120, ['android.permission.VIBRATE: granted=true'],
                          {0: ['android.permission.READ_CALENDAR: granted=false']})
    body += '\nQueries:\n  Queries via package name:\n    com.example.user.chat: android.permission.NOT_A_ROW: granted=true\n'
    body += '\nShared users:\n  SharedUser [android.uid.example] (cafe0001):\n    %s=1000\n' % ('appId' if layout != 'a10' else 'userId')
    body += '    Packages\n      PackageSetting{1 com.example.system.settings/1000}\n'
    body += '    install permissions:\n      android.permission.WRITE_SECURE_SETTINGS: granted=true\n'
    body += '      android.permission.MANAGE_EXAMPLE: granted=false\n'
    body += '    User 0: \n      runtime permissions:\n        android.permission.RECORD_AUDIO: granted=true, flags=[ SYSTEM_FIXED|PREGRANT]\n'
    body += '\nService permissions:\n    com.example.user.chat/.SyncService: android.permission.NOT_A_ROW_EITHER\n'
    if cut:
        return body + "*** SERVICE 'package' DUMP TIMEOUT (10000ms) EXPIRED ***\n\n"
    return body + '\n--------- 0.321s was the duration of dumpsys package, ending at: 2026-11-02 10:15:12\n\n'


# ------------------------------------------------------------------------------------------
# appops service
# ------------------------------------------------------------------------------------------
def access_lines():
    """The ops of the example application package under its uid: (op line, [access texts])."""
    t1, o1 = stamp(5000)
    t2, o2 = stamp(86400000 * 3 + 3600000 * 4 + 2000)
    t3, o3 = stamp(1250)
    t4, o4 = stamp(61000)
    t5, o5 = stamp(86400000 * 30)
    ops = [
        ('FINE_LOCATION (allow / switch COARSE_LOCATION=allow): ', [
            'Access: [top-s] %s (%s) duration=+1d2h3m4s5ms' % (t2, o2),
            'Reject: [bg-s]%s (%s)' % (t1, o1)]),
        ('CAMERA (foreground): ', ['Access: [fg-tpd] %s (%s) proxy[uid=10101, pkg=com.example.proxy, attributionTag=proxy_tag]' % (t3, o3),
                                  'Access: [cch-upd] %s (%s)' % (t4, o4)]),
        ('RECORD_AUDIO (ignore): ', ['Access: [fgsvcl-s] %s (%s) duration=+250ms' % (t5, o5)]),
        ('WAKE_LOCK (default): ', ['Access: [pers-s] %s (%s) duration=+12s34ms' % (t1, o1), 'Running start at: +12s34ms', 'startNesting=2']),
        ('NO_ACCESS_OP (deny): ', []),
    ]
    return ops


def appops_service(layout, cut=False):
    tagged = layout != 'a10'
    text = ['DUMP OF SERVICE appops:']
    if layout != 'a10':
        text += ['Service host process PID: 2682', 'Threads in use: 1/32', 'Client PIDs: 10, 11']
    text += ['Current AppOps Service state:', '  Settings:', '    top_state_settle_time=+5s0ms', '',
             '  Op mode watchers:', '    Op COARSE_LOCATION:']
    if tagged:
        text += ['      #0: ModeCallback{890596e watchinguid=-1 flags=0x1 op=FINE_LOCATION from uid=u0a100 pid=2306}']
    else:
        text += ['      #0: ModeCallback{890596e watchinguid=-1 flags=0x1 from uid=u0a100 pid=2306}']
        text += ['  All op active watchers:', '    f4fd975 ->', '        uid=10100 pkg=com.example.user.chat op=MONITOR_LOCATION']
    text += ['  All op started watchers:', '    ca9d438 ->', '      [CAMERA]', '']
    # a system uid: numeric heading, uid-level modes, a package with ops and no accesses
    text += ['  Uid 0:', '    state=cch']
    if tagged:
        text += ['    capability=--------', '    appWidgetVisible=false']
    text += ['      COARSE_LOCATION: mode=ignore', '      FINE_LOCATION: mode=ignore', '      CAMERA: mode=foreground',
             '      READ_SMS: mode=ignore', '    Package com.example.phone:', '      FINE_LOCATION (allow): ',
             '      MANAGE_IPSEC_TUNNELS (allow): ']
    # the example application uid
    text += ['  Uid u0a100:', '    state=fg']
    if tagged:
        text += ['    capability=LCMNFUAT', '    appWidgetVisible=false']
    else:
        text += ['    foregroundOps:', '      COARSE_LOCATION: WATCHER', '    hasForegroundWatchers=true',
                 '      COARSE_LOCATION: mode=foreground']
    text += ['      WRITE_SMS: mode=allow', '    Package com.example.user.chat:']
    for op_line, accesses in access_lines():
        text.append('      ' + op_line)
        if tagged and accesses:
            text.append('        null=[')
            for access in accesses:
                text.append('          ' + access)
            text.append('        ]')
        elif accesses:
            for access in accesses:
                text.append('          ' + access)
    if tagged:
        text += ['      MONITOR_LOCATION (allow / switch COARSE_LOCATION=allow): ', '        com.example.tag=[',
                 '          Access: [pers-s] %s (%s)' % stamp(777), '          Running start at: +2s2ms',
                 '          startNesting=1', '        ]', '        second_tag=[', '          Reject: [bg-s]%s (%s)' % stamp(888),
                 '        ]']
    # a second user's application uid and a system uid of that user, an isolated uid
    other = 11 if layout == 'a15' else 10
    text += ['  Uid u%da100:' % other, '    state=bg']
    if tagged:
        text += ['    capability=-------T', '    appWidgetVisible=false']
    text += ['      CAMERA: mode=ignore', '      RECORD_AUDIO: mode=ignore', '      READ_SMS: mode=foreground',
             '    Package com.example.user.chat:', '      CAMERA (ignore): ']
    if tagged:
        text += ['        null=[', '          Access: [cch-s] %s (%s) duration=+1s1ms' % stamp(9000), '        ]']
    else:
        text += ['          Access: [cch-s] %s (%s) duration=+1s1ms' % stamp(9000)]
    text += ['  Uid u0i1:', '    state=cch', '      CAMERA: mode=ignore', '    Package com.example.isolated:',
             '      CAMERA (default): ']
    if tagged:
        text += ['        null=[', '          Access: [cch-s] 1970-01-01 00:00:00.000 (-20759d10h15m12s500ms)', '        ]']
    text += ['  Uid u%ds1000:' % other, '    state=pers', '    Package com.example.system.settings:', '      VIBRATE (allow): ']
    text += ['', '  AppOps Restrictions.', '  User restrictions for token com.example.Token@6206b46:', '      Restricted ops:',
             '        user: 0 restricted ops: [COARSE_LOCATION, FINE_LOCATION]', '    Excluded packages:',
             '      user: 0 packages: ', '        com.example.ims[*]', '']
    if tagged:
        text += ['Uid State Changes Event Log:',
                 '%s EVAL_FOREGROUND_MODE  uid=10100    uidState=UID_STATE_FOREGROUND           capability=LCMNFUAT  code=CAMERA               result=allow'
                 % (NOW + '.100'),
                 '%s COMMIT_UID_STATE      uid=10100    uidState=UID_STATE_CACHED               capability=--------  appWidgetVisible=false'
                 % (NOW + '.200')]
    if cut:
        return '\n'.join(text) + "\n*** SERVICE 'appops' DUMP TIMEOUT (10000ms) EXPIRED ***\n\n"
    return '\n'.join(text) + '\n--------- 0.337s was the duration of dumpsys appops, ending at: 2026-11-02 10:15:13\n\n'


# ------------------------------------------------------------------------------------------
# role and permissionmgr services
# ------------------------------------------------------------------------------------------
def role_service(layout):
    if layout == 'a16':
        return ''
    if layout == 'a10':
        text = ['DUMP OF SERVICE role:', 'ROLE MANAGER STATE (dumpsys role):', '{', '  user_states={', '    user_id=0', '    version=-1',
                '    packages_hash=0000000000000000000000000000000000000000000000000000000000000000', '    roles=[']
        for name, holder in (('CALL_SCREENING', ''), ('SMS', 'com.example.sms'), ('HOME', 'com.example.launcher')):
            text += ['      {', '        name=android.app.role.%s' % name]
            if holder:
                text.append('        holders=%s' % holder)
            text.append('      }')
        text += ['    ]', '  }', '}']
    else:
        text = ['DUMP OF SERVICE role:', 'Service host process PID: 1852', 'Threads in use: 0/32', 'Client PIDs: 1, 2',
                'ROLE STATE (dumpsys role):', '{', '  user_states=[']
        for user, holders in ((0, {'SMS': 'com.example.sms', 'HOME': 'com.example.launcher', 'BROWSER': ''}),
                              (11, {'SMS': '', 'HOME': 'com.example.launcher2'})):
            text += ['    {', '      user_id=%d' % user, '      version=1',
                     '      packages_hash=1111111111111111111111111111111111111111111111111111111111111111', '      roles=[']
            for name, holder in holders.items():
                text += ['        {', '          name=android.app.role.%s' % name, '          fallback_enabled=true']
                if holder:
                    text.append('          holders=%s' % holder)
                text.append('        }')
            text += ['      ]', '    }']
        text += ['  ]', '}']
    return '\n'.join(text) + '\n--------- 0.051s was the duration of dumpsys role, ending at: 2026-11-02 10:15:14\n\n'


def permissionmgr_service(layout):
    if layout == 'a10':
        return ''
    second = 11 if layout == 'a15' else 10
    text = ['DUMP OF SERVICE permissionmgr:', 'Service host process PID: 2682', 'Threads in use: 0/32', 'Client PIDs: 3, 4',
            'Permissions:',
            '  android.permission.EXAMPLE_SIGNATURE: type=TYPE_MANIFEST, packageName=android, appId=1000, gids=[], protectionLevel=[signature], flags=[]',
            'Permission groups:', '  android.permission-group.EXAMPLE: packageName=android', 'Permission trees:',
            '  com.example.tree: packageName=com.example.user.chat, appId=10100',
            'App ID: 1000', '  User: 0', '    Permissions:',
            '      android.permission.EXAMPLE_SIGNATURE: granted=true, flags=[PROTECTION_GRANTED]',
            '      com.example.permission.OTHER: granted=false, flags=[INSTALL_REVOKED]',
            '    App ops:', '      android:legacy_storage: mode=ignore', '    Package: com.example.system.settings',
            '      version=17', '      App ops:',
            'App ID: 10100', '  User: 0', '    Permissions:',
            '      android.permission.CAMERA: granted=false, flags=[USER_SENSITIVE_WHEN_GRANTED]',
            '      android.permission.READ_CONTACTS: granted=true, flags=[RUNTIME_GRANTED|USER_SET]',
            '      android.permission.NO_FLAGS: granted=true',
            '  User: %d' % second, '    Permissions:',
            '      android.permission.CAMERA: granted=true, flags=[RUNTIME_GRANTED]']
    return '\n'.join(text) + '\n--------- 0.182s was the duration of dumpsys permissionmgr, ending at: 2026-11-02 10:15:15\n\n'


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='a16', zone='Europe/Paris', cut=False, newline='\n', with_banner=True):
    header_layout = 'a16' if layout in ('a16', 'a15') else 'a10'
    text = (base.BANNER.format(report='2026-11-02 10:15:30') if with_banner else '') + '\n' + base.HEADER[header_layout] + '\n'
    text += base.properties(header_layout, zone, 'reboot,userrequested,%d' % base.epoch_s('2026-10-30 07:00:00'))
    text += '------ DUMPSYS CRITICAL (/system/bin/dumpsys) ------\n'
    text += '-------------------------------------------------------------------------------\n'
    text += package_service(layout, cut=cut)
    text += "------ 0.500s was the duration of 'DUMPSYS CRITICAL' ------\n\n"
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    text += appops_service(layout, cut=cut)
    text += role_service(layout)
    text += permissionmgr_service(layout)
    text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"
    text += '== dumpstate: done (id 1)\n'
    return text.replace('\n', newline)


# ------------------------------------------------------------------------------------------
# cases
# ------------------------------------------------------------------------------------------
def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16').encode('utf-8'))]
    out['synthetic_a15'] = [('Dump/dumpstate.txt', build_report('a15').encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt', build_report('a10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_two_reports'] = [('Dump1/dumpstate.txt', build_report('a16', zone='Asia/Kolkata').encode('utf-8')),
                                    ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                                     build_report('a10', zone='America/Sao_Paulo').encode('utf-8'))]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_no_zone'] = [('Dump/dumpstate.txt', build_report('a16', zone='').encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report='2026-11-02 10:15:30') + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\nDUMP OF SERVICE appops:\n  Uid 0:\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    odd = build_report('a16', zone='UTC').encode('utf-8')
    odd = b'\xef\xbb\xbf' + odd.replace(b'com.example.system.empty', b'com.example.system.empty\xff\xfe', 1).replace(
        b'android.permission.INTERNET', b'android.permission.INTERNET\x00', 1).replace(
        b'android.permission.CAMERA: granted=false', b'android.permission.CAM\rERA: granted=false', 1)
    out['synthetic_odd_bytes'] = [('Dump/dumpstate.txt', odd)]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_permissions_fixture_out')
