__artifacts_v2__ = {
    "bugreport_usage_events": {
        "name": "Bug Report - Usage Events",
        "description": "The Last 24 hour events list of each user in the usagestats dump of an Android bug report text, "
                       "with event type, package, class and the remaining key=value pairs as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per event line of the Last 24 hour events list of each Android user, in the usagestats service dump "
                 "(DUMP OF SERVICE usagestats) and in the CHECKIN USAGESTATS command section. Source Section says which one "
                 "printed the row. Event Type, Package and Class are as printed, Flags (as stored) is the flags value (a "
                 "hexadecimal text, not decoded) and Extras holds the other key=value pairs of the line in the order printed "
                 "(for example the instance and task of an activity, a standby bucket and its reason, a notification channel id, "
                 "a shortcut id). Extras carries app-defined text such as channel and shortcut ids exactly as the platform "
                 "printed it. Time As Printed is the text of time=. The Android 16 reports tested print epoch milliseconds, "
                 "which are read as UTC; the Android 10 reports and the Android 15 report print device wall-clock text without a "
                 "zone, which is converted with the zone shown in Bug Report - Device Facts, and a number outside 2009 to 2100 or "
                 "a wall-clock text before 2009 (the platform prints 1970-01-01 and, on some Android 10 builds, "
                 "1973-08-29 05:00:27 for a time that was never set) gets no UTC value and keeps its printed text.\n"
                 "The list is what the device kept: it is headed Last 24 hour events and spanned 17 to 24 hours in the tested "
                 "reports, so an event that is not listed says nothing about earlier use. An event row records that the usage statistics service noted that event "
                 "type for that package at that time; it does not say what caused the event or whether a person did. The "
                 "Huawei, Transsion-brand and Motorola reports print the list in both sections: 3,075 and 3,079 rows (Huawei), "
                 "4,920 and 4,921 (Transsion-brand) and 7,073 and 7,074 (Motorola), so an event printed in both appears twice "
                 "here; Source Section tells the copies apart. The two Samsung reports (Android 16) have no usagestats service "
                 "section and print only the CHECKIN USAGESTATS list (15,043 and 4,114 rows). A list headed Pending events (74 "
                 "lines on the Motorola report, printed with times that start at 1970-01-01), the interval statistics (daily, "
                 "weekly, monthly, yearly) and the app standby states that the same dump holds are not read.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 15,043, 4,114, 6,154, 9,841 and 14,147 rows, each "
                 "equal to a count made from the raw text and to an independent parser, field by field and in UTC. All five "
                 "reports record a UTC+0 time zone without daylight saving, so the conversion of wall-clock text to "
                 "UTC was the identity on every real row; offsets and daylight saving were tested on constructed text only. Only "
                 "user 0 had events in the tested reports, so User held one value, 0, on all rows of every tested report; a "
                 "second user's list was built on constructed text. Source Section held one value, CHECKIN USAGESTATS, on all "
                 "rows of the two Samsung reports, and Flags held one value, 0x0, on all rows of the Huawei and Transsion-brand "
                 "reports.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "bugreport_process_exits": {
        "name": "Bug Report - Process Exit Info",
        "description": "The ApplicationExitInfo entries of the activity dump in an Android bug report text, with the "
                       "time, process, uid, reason, sub-reason, status and importance as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per ApplicationExitInfo entry in the ACTIVITY MANAGER PROCESS EXIT INFO part of the activity service "
                 "dump. Package is the package: heading the entry is listed under. Process, PID, Real UID, Package UID, User, "
                 "Status and Importance are the values printed on the entry; Reason and Sub-reason are the number and the name "
                 "the dump prints after reason= and subreason= (for example 2 (SIGNALED)), not decoded further; Status is the "
                 "printed number; Description is the free text after description=, empty where null was printed. Time As Printed "
                 "is the timestamp= text (a device wall-clock time with milliseconds); Time (UTC) converts it with the zone shown "
                 "in Bug Report - Device Facts, and is empty for a time before 2009 or where the report records no zone. Entry is "
                 "the number after ApplicationExitInfo #.\n"
                 "The entries are the history the platform kept, not a log of the last day: the tested reports held entries that "
                 "span about six months (Samsung A-series), two and a half years (Samsung S-series) and two years (Motorola), and the "
                 "number kept for a package is the platform's, so an exit that is not listed says nothing about whether it "
                 "happened. A row says that the platform recorded that a process of the package ended with the printed reason "
                 "and status; it does not say who or what ended it, and the reason name is the dump's own wording. The Motorola "
                 "report lists entries for two Android users (0 and 11); User is the user value of the entry, and it held one value, 0, "
                 "on all rows of the two Samsung reports. The activity "
                 "service is dumped twice in the tested reports and the entries are in the longer dump (the first dump of the "
                 "Samsung A-series report ends with a 500 ms timeout marker and holds none). The Android 10 reports (Huawei and "
                 "the Transsion-brand phone) print no exit information, so the table is empty for them, which says nothing "
                 "about the device.\n"
                 "Evidence tiers. Data-proven on three real bug reports: a Samsung A-series phone (5,154 rows) and a Samsung "
                 "S-series phone (7,170 rows) on Android 16 and a Motorola phone (6,187 rows) on Android 15, each equal to a "
                 "count of ApplicationExitInfo lines in the raw text and to an independent parser, field by field and in UTC; "
                 "none on the two Android 10 reports, which print none. As the tested reports are in a UTC+0 zone, "
                 "the conversion to UTC was checked on constructed text for other zones. Not examined: Android 11 to 13 and other "
                 "vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip'),
        "output_types": "standard",
        "artifact_icon": "power"
    },
    "bugreport_settings": {
        "name": "Bug Report - Settings",
        "description": "The global, secure and system settings tables of each user in the settings dump of an Android "
                       "bug report text, with the value, the default and the package that wrote the entry as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per _id: entry of the GLOBAL SETTINGS, SECURE SETTINGS and SYSTEM SETTINGS tables of each Android user "
                 "in the settings service dump. Name is name:, Written By is pkg:, Setting ID is _id:. Value is the text after "
                 "value: up to the first trailing token (default:, defaultSystemSet:, isValuePreservedInRestore: or "
                 "notPreservedInRestore), shown up to 2,000 characters; Value Length is the number of characters of the whole "
                 "value, 0 for {null}, which is the dump's own marker and is shown as printed, as is a {null} default. A value "
                 "with line breaks is joined with one space where the breaks were (3 entries in the tested reports; the "
                 "trailing tokens are on its last line). Default is the text after default:; Default System Set and Value "
                 "Preserved In Restore are defaultSystemSet: and isValuePreservedInRestore: as printed (false for "
                 "notPreservedInRestore). Default System Set is empty where the entry prints no default (128 to 182 rows of each "
                 "tested report). Value Preserved In Restore is empty on all rows of the Huawei, Motorola and Transsion-brand "
                 "reports, whose builds do not print it, and on one row of the Samsung S-series report. The values are those the "
                 "provider held when the dump ran and include text such as device and Bluetooth names, so they are shown as "
                 "printed; a row says nothing about when or by whom the value was set (see Bug Report - Settings Changes for "
                 "the history Android 16 prints) and a missing setting is not evidence of a default.\n"
                 "The CONFIG SETTINGS table (651 to 2,013 entries in the tested reports, server-pushed feature flags) is counted "
                 "in the log and not listed, nor are the generation registry and the history of its entries.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1,057, 1,290, 938, 439 and 647 rows, each equal "
                 "to a count of _id: lines outside the CONFIG table in the raw text and to an independent parser, field by "
                 "field except the 3 multi-line values, which are read differently on purpose. The Motorola report lists two "
                 "Android users (0 with 501 rows and 11 with 146); User held one value, 0, on all rows of the other four reports. Not examined: Android 11 to 13, other vendors, and a value "
                 "that itself contains the words default: or defaultSystemSet: on a single line, which would be cut there.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "bugreport_settings_changes": {
        "name": "Bug Report - Settings Changes",
        "description": "The History entries printed under each setting in the settings dump of an Android bug report "
                       "text, with the change time, mode, old and new value and the package as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per time: entry under a History (name) line of the global, secure and system tables in the settings "
                 "service dump. Mode, Old Value (oldValue:), New Value (newValue:), Package (package:) and Caller (caller:, "
                 "cut at 200 characters) are as printed, the values cut at 400 characters. An update row can carry the same "
                 "old and new value (the setting was written again with the value it had). Only the Android 16 reports tested "
                 "print this history (1,807 rows on the Samsung A-series report and 1,109 on the S-series one); the Android 10 "
                 "and Android 15 reports print none, so the table is empty for them, which says nothing about the device. The "
                 "history of the CONFIG SETTINGS table (3,782 and 4,336 entries in the two reports) is counted in the log and "
                 "not listed.\n"
                 "Time As Printed is month, day and clock time without a year. The year is not in the dump: Time (UTC) uses the "
                 "latest year, the one of the report or the one before, that does not put the change more than a day after the "
                 "report time, and then converts with the zone shown in Bug Report - Device Facts. A change made more than a year "
                 "before the report would therefore be given a year too late; the changes of the tested reports span 362 and 297 "
                 "days. The time is empty where the report has no time or no zone.\n"
                 "A row records that the settings provider noted the change; it does not say what a person did, and the entries "
                 "kept per setting are the provider's own limited history. User held one value, 0, on all rows of both "
                 "reports.\n"
                 "Evidence tiers. Data-proven on two real Android 16 bug reports (Samsung A-series and S-series): 1,807 and "
                 "1,109 rows, equal to a count of time: lines outside the CONFIG table in the raw text and to an independent "
                 "parser, field by field and in UTC. As both are in a UTC+0 zone the conversion to UTC was "
                 "checked on constructed text for other zones. Not examined: other Android versions and vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip'),
        "output_types": "standard",
        "artifact_icon": "history"
    },
    "bugreport_boot_reasons": {
        "name": "Bug Report - Boot Reasons",
        "description": "The boot reason properties and the entries of persist.sys.boot.reason.history in the system "
                       "properties of an Android bug report text, with the start time of each entry.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per line of the persist.sys.boot.reason.history property in the SYSTEM PROPERTIES (getprop) section, "
                 "in the order printed with Position 0 for the first one printed. Entry is the line, Reason the first word, "
                 "Sub-reason the words between the first and the last, and the last number is the entry's time in seconds since "
                 "the Unix epoch, shown as Time As Printed and, when it falls between 2009 and 2100, as Time (UTC). An entry "
                 "whose last item is not a number has no time. The reason words are the platform's own and are not decoded or "
                 "explained here, and an entry says that the platform recorded a start with that reason at that time, not why it "
                 "happened. The platform keeps a short list: the tested reports printed 2 to 4 entries. A report without the "
                 "property has no rows, which says nothing about the device. The properties sys.boot.reason, "
                 "sys.boot.reason.last, ro.boot.bootreason, persist.sys.boot.reason and sys.reset_reason, which the report "
                 "prints when it has them, are rows of Bug Report - Device Facts. The kernel command line, which can carry a "
                 "serial number, is not read.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 4, 4, 3, 2 and 4 rows, equal to the history "
                 "lines in the raw text and to an independent parser, field by field and in UTC. Not examined: other Android "
                 "versions and vendors, and a history longer than the 4 entries seen (at most 500 are read).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip'),
        "output_types": "standard",
        "artifact_icon": "power"
    },
}

from scripts import dumpstate_reader
from scripts.ilapfuncs import artifact_processor, logfunc


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_cuts(label, report, service, lines):
    """Say so when the platform cut a dump of ``service`` that holds the rows (or when it cut one and there are no rows)."""
    cut = [section for section in report.sections if section.kind == 'service' and section.name == service and section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {service} service dump was cut by a {cut[0].timeout_ms} ms '
                                           f'timeout, the rows from it may be partial')


@artifact_processor
def bugreport_usage_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'User', 'Event Type', 'Package', 'Class',
               'Flags (as stored)', 'Extras', 'Source Section', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_cuts(label, report, 'usagestats', [event.line for event in report.usage_events if event.section.startswith('DUMP')])
        for event in report.usage_events:
            rows.append((report.usage_time(event.time_text), event.time_text, event.user, event.event_type,
                         event.package, event.class_name, event.flags, event.extras, event.section, event.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_process_exits(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Package', 'Process', 'PID', 'Real UID', 'Package UID',
               'User', 'Reason', 'Sub-reason', 'Status', 'Importance', 'Description', 'Entry', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_cuts(label, report, 'activity', [item.line for item in report.process_exits])
        for item in report.process_exits:
            rows.append((report.exit_time(item.stamp), item.stamp, item.package, item.process, item.pid, item.real_uid,
                         item.package_uid, item.user, item.reason, item.sub_reason, item.status, item.importance,
                         item.description, item.entry, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_settings(context):
    headers = ('User', 'Namespace', 'Name', 'Value', 'Value Length', 'Written By', 'Default', 'Default System Set',
               'Value Preserved In Restore', 'Setting ID', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_cuts(label, report, 'settings', [item.line for item in report.settings])
        for user, (entries, history) in sorted(report.config_settings.items(), key=lambda item: str(item[0])):
            logfunc(f'Bug report {label}: the CONFIG SETTINGS table of user {user} ({entries} entries, {history} history '
                    f'entries) is counted and not listed')
        for item in report.settings:
            rows.append((item.user, item.namespace, item.name, item.value, item.value_length, item.writer, item.default,
                         item.default_system_set, item.preserved, item.setting_id, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_settings_changes(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'User', 'Namespace', 'Name', 'Mode', 'Old Value',
               'New Value', 'Package', 'Caller', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_cuts(label, report, 'settings', [item.line for item in report.setting_changes])
        for item in report.setting_changes:
            _full, moment = report.setting_change_time(item.time_text)
            rows.append((moment, item.time_text, item.user, item.namespace, item.name, item.mode, item.old_value,
                         item.new_value, item.package, item.caller, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_boot_reasons(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Entry', 'Reason', 'Sub-reason', 'Position', 'Source Line',
               'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        for item in report.boot_entries:
            moment = None
            if item.epoch_text.isdigit() and dumpstate_reader.plausible_epoch_ms(int(item.epoch_text) * 1000):
                moment = dumpstate_reader.epoch_s_to_utc(int(item.epoch_text))
            rows.append((moment, item.epoch_text, item.entry, item.reason, item.sub_reason, item.position, item.line, label))
    return headers, rows, _source_path(context, reports)
