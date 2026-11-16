__artifacts_v2__ = {
    "bugreport_shortcuts": {
        "name": "Bug Report - Shortcuts",
        "description": "The ShortcutInfo entries of each user in the shortcut service dump of an Android bug report text, with "
                       "the last change time, package, shortcut id, labels, kind, categories and intents.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Android Bug Report - App Usage",
        "notes": "One row per ShortcutInfo entry printed in the shortcut service dump (DUMP OF SERVICE shortcut), under the User: line of each Android user and the Package: line of each app. Shortcut ID, Short Label, Long Label, Categories (as printed), Activity, Intents (as printed) and Extras (as printed) are the values the dump prints for id=, shortLabel=, longLabel=, categories=, activity=, intents= and extras=. Activity is shown without the ComponentInfo{ } wrapper and the labels without the resId part that follows them. A value printed as null is shown empty. Shortcut ID, the labels and Activity are cut at 500 characters; Categories, Intents and Extras are cut at 1,000. A label with a line break is joined with one space.\nLast Changed (UTC) reads timestamp= as epoch milliseconds (kept in Timestamp (ms, as printed)); a value outside 2009 to 2100 leaves Last Changed empty. AOSP documents the value as the last time any of the shortcut's fields was updated (ShortcutInfo.getLastChangedTimestamp). In the AOSP source (android-16.0.0_r1) it is written when the app builds or updates the shortcut, and also by the platform when it re-ranks, disables or deletes it, rescans the app's package (shortcuts that use resources are restamped, and manifest shortcuts are rebuilt), or resolves its label strings. So it is the last time one of those steps stamped the shortcut; pinning and caching change its flags without writing it. It is not the time of a message, a call or a launch, and a row does not say who or what made the change.\nKind names bits of the printed hexadecimal flags value with the ShortcutInfo.FLAG_ constants of AOSP android-16.0.0_r1: manifest, dynamic, pinned, long lived, cached for notifications, cached for bubbles, cached for people tile, disabled, immutable and shadow, plus excluded from launcher when the printed letters carry Hid-L. The icon, string, key-fields-only and returned-by-service bits are not named; the whole value and the letters are in Flags (as printed). The letters the dump prints do not show the three cached bits, which is why Kind is read from the number. In the AOSP source the notification service sets cached for notifications when an app posts a notification that names a long-lived shortcut, and its comment says the shortcut is uncached once all the associated notifications are removed, unless the user changed the notification settings of that conversation; the bit does not count notifications or say when one was posted. Person Count is the number of entries of persons=: the dump prints each person only as an object reference (android.app.Person@ and a hash), so persons= holds no name; it is empty where null was printed and 0 for an empty list. Disabled Reason (as printed) is the text of disabledReason= without its brackets.\nNot read: the disabled message, locusId and the resource ids of each entry, the per-package Calls, Last known FG and Last reset lines, the launcher pin lists, the icon and bitmap path of each entry (no icon file was in the report examined), and the SHORTCUT MANAGER UID STATES and SHORTCUT MANAGER FILES parts at the end of the section. On a full file system extraction the shortcut service files are read by Shortcut Service - Shortcuts.\nEvidence tiers. Data-proven on one real bug report from a Motorola moto g play 2026 on Android 16: 105 rows from 35 packages, equal to the ShortcutInfo lines of its shortcut section and to an independent parser, field by field and in UTC. User held one value, 0, and Disabled Reason (as printed) one value, Not disabled, on all 105 rows; that report lists one Android user. On it, 30 rows carried long lived (9 packages), 20 cached for notifications, and one long lived and cached for notifications without dynamic; Long Label was empty on 59 rows, Categories on 70 and Extras on 95. The phone held known data made the same day, with the host time of each step recorded: a message sent in a new Zangi group at 17:29:47 UTC matches the Last Changed time of that group's shortcut to the second, and a Signal Note to Self message sent at 15:56:43 UTC is followed by a Signal shortcut change at 15:56:46. A Messenger shortcut changed at 17:30:25 UTC while the new group chat screens were open and no message was sent from the phone, so a change time alone does not show a sent message. One phone, one report. Source-verified, not exercised on a real report: pinned, disabled, shadow, cached for bubbles, cached for people tile, excluded from launcher, a second Android user, a label with a line break and the 500-character cut; most of these were run on constructed text only. The 1,000-character cut applied to one row. Not examined: other vendors and other Android versions.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {},
    },
}

from scripts import dumpstate_reader
from scripts import dumpstate_shortcuts
from scripts.ilapfuncs import artifact_processor, logfunc


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_service(label, report, rows):
    """Say so when the report has no shortcut service dump, or when the platform cut the dump that holds the rows."""
    if 'shortcut' not in report.sections_seen:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: no shortcut service dump in this report')
        return
    lines = [row.line for row in rows]
    cut = [section for section in report.sections
           if section.kind == 'service' and section.name == 'shortcut' and section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the shortcut service dump was cut by a '
                                           f'{cut[0].timeout_ms} ms timeout, the rows from it may be partial')


def _changed(text):
    """UTC time of the printed timestamp= value (epoch milliseconds), or None outside 2009 to 2100."""
    if dumpstate_reader.is_digits(text) and dumpstate_reader.plausible_epoch_ms(int(text)):
        return dumpstate_reader.epoch_ms_to_utc(int(text))
    return None


@artifact_processor
def bugreport_shortcuts(context):
    headers = (('Last Changed (UTC)', 'datetime'), 'Timestamp (ms, as printed)', 'User', 'Package', 'Shortcut ID',
               'Short Label', 'Long Label', 'Kind', 'Categories (as printed)', 'Person Count', 'Rank', 'Activity',
               'Intents (as printed)', 'Extras (as printed)', 'Disabled Reason (as printed)', 'Flags (as printed)',
               'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = dumpstate_shortcuts.rows_of(report)
        _log_service(label, report, items)
        unknown = sorted({item.unknown_letters for item in items if item.unknown_letters})
        if unknown:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: shortcut flag letters not in the AOSP list: '
                                               f'{", ".join(unknown)}')
        for item in items:
            flags = f'0x{item.flags_hex} [{item.flag_letters}]' if item.flags_hex else item.flag_letters
            rows.append((_changed(item.timestamp_text), item.timestamp_text, item.user, item.package, item.shortcut_id,
                         item.short_label, item.long_label, item.kinds, item.categories, item.person_count, item.rank,
                         item.activity, item.intents, item.extras, item.disabled_reason, flags, item.line, label))
    return headers, rows, _source_path(context, reports)
