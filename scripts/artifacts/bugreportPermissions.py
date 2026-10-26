__artifacts_v2__ = {
    "bugreport_package_permissions": {
        "name": "Bug Report - Package Permissions",
        "description": "The install permission and runtime permission lines of each package, hidden system package and shared "
                       "user in the package service dump of an Android bug report text, with the granted value and flags as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Permissions and App Ops",
        "notes": "One row per permission line under an install permissions: heading (Permission Type install) or under a runtime "
                 "permissions: heading of a User line (Permission Type runtime) in the Packages, Hidden system packages and "
                 "Shared users blocks of the package service dump. Package Or Shared User and Holder Type say which entry the "
                 "line is printed under (Package, Hidden system package or Shared user); App ID is the appId= or userId= value "
                 "printed for that entry. Granted is the text after granted= and Flags (as printed) is the text inside flags=[ ], "
                 "both exactly as printed and not decoded. User is the number of the User line above a runtime permissions: "
                 "heading; on install rows it is empty unless the line prints a userId= value (190 rows of the Motorola "
                 "report), which is then shown there. The meaning of that suffix is not established here. A runtime permissions: "
                 "heading that follows an overlay paths: list is read as belonging to the User line before the list (417 rows "
                 "of the Transsion-brand report print the heading one level deeper than the other reports do).\n"
                 "In the five tested reports a package that prints a sharedUser= line has no permission lines of its own: they "
                 "are printed under its Shared user entry (153, 181, 85, 74 and 61 such packages), so look there for them. A "
                 "package that has a hidden system copy has rows under both Package and Hidden system package. A row says what "
                 "the dump printed for that entry; it does not say when or how the state was reached, whether the app asked "
                 "for the permission in its manifest, or whether it used it (see Bug Report - App Ops Accesses for printed access "
                 "times). A permission that is not listed says nothing about the package. The declared permissions: lists of "
                 "the packages are not read here (see Bug Report - Permission Definitions) and neither are the "
                 "AppOp Permissions: and Service permissions: lists of the same dump.\n"
                 "The Samsung A-series report's package dump ends with a 10,000 ms DUMP TIMEOUT marker inside the Dexopt state "
                 "part, after the Shared users block, so its permission lines were all printed; a report cut earlier would lose "
                 "the rest, and the log says so when a cut dump is read.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and "
                 "a Transsion-brand phone on Android 10, Motorola on Android 15): 14,995, 19,976, 7,697, 3,579 and 13,133 rows, "
                 "each equal to the rows of an independent parser (an indentation tree over the raw text) on every field "
                 "including the source line. Flags is empty on the install rows of the Huawei and Transsion-brand reports and on "
                 "all but 63, 62 and 105 install rows of the other three. Not examined: Android 11 to 14, other vendors, a "
                 "granted= value other than true or false, a report with more than two Android users. Run together, the five "
                 "tested reports gave 59,380 rows, above the 50,000-row limit the report builder sets for an HTML page, so "
                 "the page left the table out; the TSV and LAVA outputs hold the rows.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "key"
    },
    "bugreport_permission_definitions": {
        "name": "Bug Report - Permission Definitions",
        "description": "The Permissions: table of the package service dump of an Android bug report text, with the source package, "
                       "uid, group ids, type, protection text and flags of each permission as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Permissions and App Ops",
        "notes": "One row per Permission [name] entry of the Permissions: heading of the package service dump. Source Package is "
                 "sourcePackage=, Source Uid and Gids (as printed) are uid= and gids=, Type (as stored) is type= and Protection "
                 "(as printed) is the text after prot= (for example signature|privileged), all as printed and not decoded. Flags "
                 "(as stored) is flags= (a hexadecimal text); the Huawei and Transsion-brand reports (Android 10) print no flags= "
                 "line, so it is empty on 2,192 of the 2,212 and 870 of the 890 rows there. Gids is null where the dump prints "
                 "null, which the Android 10 reports do. The table lists permissions that packages define, system and "
                 "application ones; a row says that the dump listed the permission with that source package, not that the "
                 "permission is held by anything (see Bug Report - Package Permissions) and not what an app does with it.\n"
                 "The Permission groups: and Permission trees: lists that the permissionmgr dump prints, the declared "
                 "permissions: list of each package and the AppOp Permissions: list are not read. The same permissions are "
                 "printed again by the permissionmgr service on the Android 15 and 16 reports; this table reads the package "
                 "dump because all five tested reports print it.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and "
                 "a Transsion-brand phone on Android 10, Motorola on Android 15): 3,141, 3,631, 2,212, 890 and 2,302 rows, each "
                 "equal to the rows of an independent parser on every field including the source line. Type held the single "
                 "value 0 on all rows of the three Android 15 and 16 reports and the values 0, 1 and 2 on the Android 10 "
                 "reports. Not examined: Android 11 to 14 and other vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "list"
    },
    "bugreport_appops_modes": {
        "name": "Bug Report - App Ops Modes",
        "description": "The uid-level modes and the per-package op lines of the appops service dump of an Android bug report text, "
                       "with the mode, the switch text, the uid state and the capability as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Permissions and App Ops",
        "notes": "Rows come from the Uid N: blocks of the appops service dump. Scope Uid: the uid-level lines OP: mode=X of a "
                 "block, with one row for each distinct Mode value of that uid; Ops lists the ops of those lines in the order "
                 "printed and Op Count is their number, so the 32,633, 42,419, 152, 120 and 89,199 uid-level lines of the five "
                 "tested reports are 806, 1,270, 138, 107 and 2,357 rows (the Op Count of the rows adds up to the lines "
                 "counted in the raw text on every report). Scope Package: one row for each OP (mode): line under a Package "
                 "heading of the block; Ops holds the op name, Op Count is 1, Mode is the text in the brackets before any "
                 "' / switch ' and Switch is the text after it (for example COARSE_LOCATION=allow), as printed. Uid (as "
                 "printed) is the heading text (a number such as 1000, or u0a100 for an application uid); Numeric Uid is that "
                 "number, or user * 100000 + 10000 + n for u<user>a<n> and user * 100000 + n for u<user>s<n>, and is empty "
                 "for an isolated shape such as u0i1. For the Package rows of the five tested reports the Numeric Uid agreed "
                 "with the app id of the same package in the package service dump for 1,084 of the 1,085 u<user>a<n> "
                 "pairs (the other pair is a package that the package list gives a different app id) and for all 13 u<user>s<n> "
                 "pairs; a package listed under a numeric uid that is not its own app id (for example under Uid 0) is shown as printed. Uid State and Capability are "
                 "the state= and capability= lines of the block, as printed and describing the dump time; the Android 10 "
                 "reports print no capability= line, so it is empty on every row of the Huawei and Transsion-brand reports.\n"
                 "Mode values seen: allow, default, deny, foreground and ignore, as printed and not decoded. On the three "
                 "Android 15 and 16 reports ignore is 99.7, 99.1 and 99.8 percent of the uid-level lines (it is the Mode of 753, "
                 "973 and 2,250 uid rows, one for almost every uid); a row says what the dump printed for that uid or package "
                 "and does not say whether any app used the op (see Bug Report - App Ops Accesses), and an op that has no line "
                 "says nothing about its mode.\n"
                 "Not read: the Op mode watchers, Package mode watchers and the active, started and noted watcher lists, the "
                 "restrictions, foregroundOps and startNesting lines of a uid, and the Uid State Changes Event Log that the "
                 "Android 15 and 16 dumps end with. The Samsung S-series report also prints a History table (pipe separated, "
                 "last hour of location, microphone and camera ops); no other tested report does, so it is not read.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and "
                 "a Transsion-brand phone on Android 10, Motorola on Android 15): 3,001, 5,592, 639, 709 and 4,261 rows, each equal "
                 "to the rows of an independent parser (an indentation tree) on every field including the source line. The "
                 "Motorola report prints uid headings of users 0 and 11. Not examined: Android 11 to 14, other vendors, and a "
                 "dump with a package heading under a uid that also prints uid-level modes after it.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "shield"
    },
    "bugreport_appops_accesses": {
        "name": "Bug Report - App Ops Accesses",
        "description": "The Access and Reject lines printed under each op of each package in the appops service dump of an Android "
                       "bug report text, with the time, uid state, flags, duration and proxy text as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Permissions and App Ops",
        "notes": "One row per Access: or Reject: line under an OP (mode): line of a Package heading in a Uid N: block of the "
                 "appops service dump (Kind Access or Reject), and one row of Kind Running for each Running start at: line. "
                 "Uid (as printed), Numeric Uid and Package are those of the block and heading (see Bug Report - App Ops Modes "
                 "for how Numeric Uid is made); Op is the op name and Op Mode the mode in the brackets of the op line, which is "
                 "the mode at the dump time and not the mode at the time of the access. Attribution Tag is the tag line the "
                 "access is printed under, as printed, with null where the dump prints null (the Android 10 reports print "
                 "no tag lines, so it is empty on every row there). The square brackets of the line, for example [top-s], are "
                 "split at the first hyphen into Uid State (top) and Op Flags (s) and are shown as printed, not decoded. "
                 "Time As Printed is the date and time of the line (device wall-clock text with milliseconds) and Time (UTC) "
                 "converts it with the zone shown in Bug Report - Device Facts; Time Note says why Time (UTC) is empty (no "
                 "zone in the report, a time that cannot be converted) and was empty on every row of the five tested reports. "
                 "Offset From Dump As Printed is the text in the round brackets after the time, for example -5s250ms. On "
                 "every row of every tested report the time minus that offset gave one and the same instant for all rows of a "
                 "report, within the second of the footer time of the appops section (the dump time). Duration As Printed is the text after "
                 "duration= and Duration (ms) is that text converted (units d, h, m, s, ms). Proxy Uid, Proxy Package and "
                 "Proxy Attribution Tag are the proxy[uid=, pkg=, attributionTag=] text. In the tested reports it appears "
                 "only on lines whose flags are tpd or upd; every such line of the three Android 15 and 16 reports carries it "
                 "(25, 41 and 50 lines), and the 146 and 134 such lines of the two Android 10 reports print none. "
                 "Running Start As Printed and Start Nesting are the Running start at: text and the startNesting= line that "
                 "follows it (printed after 1 of 7, 4 of 21, 5 of 5, 6 of 6 and 2 of 14 running lines); a Running row has no "
                 "time.\n"
                 "The dump keeps a few lines per op and package, not a log: the printed times reach back 283, 1,029, 2,277, "
                 "432 and 959 days from the dump time on the tested reports, and an access that is not listed says nothing about "
                 "whether it happened. A row says that the service noted an access or a rejection of that op for that "
                 "package at that time; it does not say what the app did, who started it, or whether a person was present. A "
                 "package listed under a uid is as printed (some tested reports list a package under Uid 0 although its app id is another number).\n"
                 "Not read: the watcher lists, the restrictions, the Uid State Changes Event Log of the Android 15 and 16 dumps "
                 "and the History table of the Samsung S-series report (the only tested report that prints it), and the "
                 "uid-level modes (see Bug Report - App Ops Modes).\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and "
                 "a Transsion-brand phone on Android 10, Motorola on Android 15): 2,883, 5,721, 1,146, 1,373 and 4,128 rows "
                 "(Access 1,830, 3,393, 1,031, 1,137, 2,548; Reject 1,046, 2,307, 110, 230, 1,566; Running 7, 21, 5, 6, 14), "
                 "each equal to the rows of an independent parser (an indentation tree) on every field including the source "
                 "line, with the times and durations read from the printed text. All five reports record a UTC+0 zone without "
                 "daylight saving, so the conversion to UTC was the identity on every real row; other offsets and daylight "
                 "saving were tested on constructed text only. Not examined: Android 11 to 14, other vendors, and a "
                 "dump that prints an access line outside an op line.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "clock"
    },
    "bugreport_role_holders": {
        "name": "Bug Report - Role Holders",
        "description": "The roles and the holders= text of each user in the role service dump of an Android bug report text, "
                       "with the fallback_enabled value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Permissions and App Ops",
        "notes": "One row per name= entry of the roles list of each user_id= block in the role service dump (ROLE MANAGER STATE "
                 "on Android 10, ROLE STATE on Android 15). Role is the name (for example android.app.role.HOME), Holders (as "
                 "printed) is the text after holders= and is empty where the entry prints no holders= line, which is what the "
                 "dump shows for a role without a holder and not a statement about the device. Fallback Enabled is the text "
                 "after fallback_enabled=; the Android 10 reports print no such line, so it is empty on all their rows. No "
                 "tested report prints more than one holder in a holders= line, so the text is kept whole and not split; the "
                 "packages_hash= and version= lines of a user are not listed.\n"
                 "The Samsung A-series and S-series reports (Android 16) print no role service section, so they have no rows, "
                 "which says nothing about the roles on those devices.\n"
                 "Evidence tiers. Data-proven on three real bug reports: 8 rows on the Huawei and the Transsion-brand phone "
                 "(Android 10, user 0) and 76 rows on the Motorola phone (Android 15, users 0 and 11, 37 of the rows without a "
                 "holder), each equal to the rows of an independent regular expression parser on every field. Not examined: "
                 "Android 11 to 14, other vendors, a holders= line with several holders.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "user-check"
    },
    "bugreport_permission_grants": {
        "name": "Bug Report - Permission Manager Grants",
        "description": "The permission lines of each app id and user in the permissionmgr service dump of an Android bug report "
                       "text, with the granted value and flags as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Permissions and App Ops",
        "notes": "One row per permission line under a Permissions: heading of a User: block of an App ID: block in the "
                 "permissionmgr service dump. App ID and User are the numbers of those headings, Permission is the name, "
                 "Granted the text after granted= and Flags (as printed) the text inside flags=[ ], as printed and not "
                 "decoded (flags such as INSTALL_GRANTED, RUNTIME_GRANTED or USER_SENSITIVE_WHEN_GRANTED are the dump's own "
                 "words). The lines are per app id, so every package that shares an app id has the same rows; a row does not "
                 "name a package. Flags is empty on 215 rows of the Samsung S-series report and 93 rows of the Motorola "
                 "report.\n"
                 "Only the Android 15 and 16 reports print this section (the Huawei and Transsion-brand reports on Android 10 "
                 "have none, which says nothing about their permissions: see Bug Report - Package Permissions). Not read: the "
                 "Permissions:, Permission groups: and Permission trees: lists at the start of the dump (the permission "
                 "definitions are in Bug Report - Permission Definitions, from the package dump that all tested reports "
                 "print), and the Package: / version= / App ops: parts under each user (the App ops: lists, 151, 1,691 and 979 "
                 "lines on the Samsung A-series, Samsung S-series and Motorola reports).\n"
                 "Evidence tiers. Data-proven on three real bug reports: 14,531 rows (Samsung A-series, Android 16), 19,361 "
                 "(Samsung S-series, Android 16) and 21,149 (Motorola, Android 15, users 0 and 11), each equal to the rows of an "
                 "independent parser (an indentation tree) on every field including the source line. User held the single "
                 "value 0 on all rows of the two Samsung reports. Run together, the three reports gave 55,041 rows, above the "
                 "50,000-row limit the report builder sets for an HTML page, so the page left the table out; the TSV and LAVA "
                 "outputs hold the rows. Not examined: Android 11 to 14 and other vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "key"
    },
}

from scripts import dumpstate_permissions, dumpstate_reader
from scripts.ilapfuncs import artifact_processor, logfunc


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_service(label, report, service, rows):
    """Say so when the report has no dump of ``service``, or when the platform cut the dump that holds the rows."""
    if service not in report.sections_seen:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: no {service} service dump in this report')
        return
    lines = [row.line for row in rows]
    cut = [section for section in report.sections if section.kind == 'service' and section.name == service and section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {service} service dump was cut by a {cut[0].timeout_ms} ms '
                                           f'timeout, the rows from it may be partial')


def _access_time(report, text):
    """``(UTC datetime or None, note)`` for the date and time printed on an Access or Reject line."""
    if not text:
        return None, ''
    value = dumpstate_reader.normal_wall_text(text)
    if not value:
        return None, dumpstate_reader.NOTE_NOT_A_TIME
    if value in dumpstate_reader.UNSET_WALL_TIMES:
        return None, dumpstate_reader.NOTE_UNSET
    if not report.clock.known:
        return None, dumpstate_reader.NOTE_NO_ZONE
    moment = report.clock.to_utc(text)
    return moment, '' if moment is not None else dumpstate_reader.NOTE_NONEXISTENT


@artifact_processor
def bugreport_package_permissions(context):
    headers = ('Package Or Shared User', 'Holder Type', 'App ID', 'Permission Type', 'User', 'Permission', 'Granted',
               'Flags (as printed)', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_permissions.rows_of(report, 'package_permissions')
        _log_service(label, report, 'package', items)
        for item in items:
            rows.append((item.holder, item.holder_type, item.app_id, item.kind, item.user, item.permission, item.granted,
                         item.flags, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_permission_definitions(context):
    headers = ('Permission', 'Source Package', 'Source Uid', 'Gids (as printed)', 'Type (as stored)',
               'Protection (as printed)', 'Flags (as stored)', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_permissions.rows_of(report, 'permission_definitions')
        _log_service(label, report, 'package', items)
        for item in items:
            rows.append((item.permission, item.source_package, item.uid, item.gids, item.perm_type, item.protection,
                         item.flags, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_appops_modes(context):
    headers = ('Scope', 'Uid (as printed)', 'Numeric Uid', 'Package', 'Mode (as printed)', 'Op Count', 'Ops',
               'Switch (as printed)', 'Uid State (as printed)', 'Capability (as printed)', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_permissions.rows_of(report, 'appop_modes')
        _log_service(label, report, 'appops', items)
        for item in items:
            rows.append((item.scope, item.uid, dumpstate_permissions.uid_number(item.uid), item.package, item.mode,
                         item.op_count, item.ops, item.switch, item.uid_state, item.capability, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_appops_accesses(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Kind', 'Uid (as printed)', 'Numeric Uid', 'Package',
               'Op', 'Op Mode (as printed)', 'Attribution Tag', 'Uid State (as printed)', 'Op Flags (as printed)',
               'Duration As Printed', 'Duration (ms)', 'Offset From Dump As Printed', 'Proxy Uid', 'Proxy Package',
               'Proxy Attribution Tag', 'Running Start As Printed', 'Start Nesting', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_permissions.rows_of(report, 'appop_accesses')
        _log_service(label, report, 'appops', items)
        for item in items:
            moment, note = _access_time(report, item.time_text)
            rows.append((moment, item.time_text, note, item.kind, item.uid, dumpstate_permissions.uid_number(item.uid),
                         item.package, item.op, item.op_mode, item.tag, item.uid_state, item.op_flags, item.duration_text,
                         item.duration_ms, item.offset, item.proxy_uid, item.proxy_package, item.proxy_tag,
                         item.running_start, item.start_nesting, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_role_holders(context):
    headers = ('User', 'Role', 'Holders (as printed)', 'Fallback Enabled (as printed)', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_permissions.rows_of(report, 'role_holders')
        _log_service(label, report, 'role', items)
        for item in items:
            rows.append((item.user, item.role, item.holders, item.fallback, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_permission_grants(context):
    headers = ('App ID', 'User', 'Permission', 'Granted', 'Flags (as printed)', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_permissions.rows_of(report, 'permission_grants')
        _log_service(label, report, 'permissionmgr', items)
        for item in items:
            rows.append((item.app_id, item.user, item.permission, item.granted, item.flags, item.line, label))
    return headers, rows, _source_path(context, reports)
