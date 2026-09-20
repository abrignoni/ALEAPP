__artifacts_v2__ = {
    "fossify_calendar_events": {
        "name": "Fossify Calendar - Events",
        "description": "Parses calendar events and tasks stored by the Fossify Calendar Android app and its Simple Mobile Tools predecessor.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Fossify Calendar",
        "notes": "One row per entry in the events table of databases/events.db, joined to event_types for "
                 "the calendar name. The table holds both calendar events and the app's tasks, told "
                 "apart by the Type column (0 an event, 1 a task, per TYPE_EVENT and TYPE_TASK in "
                 "Constants.kt at FossifyOrg/Calendar b269b99bb7152f126677278b486de24f6f1050ff). Title, "
                 "Location and Description carry the event's own text as stored, and Location and "
                 "Description were empty on the tested event. Start "
                 "and End come from start_ts and end_ts, which are Unix seconds; on the tested device a "
                 "2:00 PM local event stored 1788112800, which is 18:00 UTC and matches the device's "
                 "America/New_York zone, so they are reported as UTC and the event's own Time Zone is "
                 "carried in its column. All Day is the FLAG_ALL_DAY bit of the flags column; for an "
                 "all-day event the time of day is not meaningful and the stored value encodes the date, "
                 "so its UTC rendering can fall on the previous day, which is not exercised on the tested "
                 "data. Reminders lists the minutes-before values that are set (a value of -1 means that "
                 "reminder slot is off, per REMINDER_OFF). Repeats is Yes when the event has a non-zero "
                 "recurrence interval; the interval, rule and limit are stored but not decoded here. "
                 "Attendees is the app's stored attendee list as stored. Status is decoded from the "
                 "Android CalendarContract.Events values 0 tentative, 1 confirmed, 2 cancelled. Last "
                 "Updated comes from last_updated, which is Unix milliseconds. Source is the app's own "
                 "origin marker as stored, for example simple-calendar for an event created in the app, "
                 "imported-ics for an imported file, contact-birthday or contact-anniversary for an event "
                 "derived from a contact, or a caldav- value for a synced calendar. The tasks table holds "
                 "task-specific state keyed to these rows and is not parsed separately. The app is the "
                 "maintained successor to Simple Mobile Tools Calendar and uses the identical schema, so "
                 "the paths cover both org.fossify.calendar (tested) and "
                 "com.simplemobiletools.calendar.pro (same schema, from the shared source, not exercised "
                 "here).",
        "paths": (
            '*/org.fossify.calendar/databases/events.db*',
            '*/com.simplemobiletools.calendar.pro/databases/events.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | org.fossify.calendar vc 20 | 1 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/events.db'

# Constants.kt at FossifyOrg/Calendar b269b99bb7152f126677278b486de24f6f1050ff, and
# Android CalendarContract.Events for status.
FLAG_ALL_DAY = 1
EVENT_TYPES = {0: 'Event', 1: 'Task'}
STATUSES = {0: 'Tentative', 1: 'Confirmed', 2: 'Cancelled'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _secs(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (TypeError, ValueError):
        return ''


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _lookup(table, value):
    if value in table:
        return table[value]
    return f'{value} (as stored)'


def _reminders(r1, r2, r3):
    return ', '.join(str(m) for m in (r1, r2, r3) if m is not None and m >= 0)


@artifact_processor
def fossify_calendar_events(context):
    query = '''SELECT e.start_ts, e.end_ts, e.flags, e.title, e.location, e.description,
                      e.time_zone, e.reminder_1_minutes, e.reminder_2_minutes,
                      e.reminder_3_minutes, e.repeat_interval, e.attendees, e.status,
                      e.type, e.last_updated, e.source, t.title
               FROM events e
               LEFT JOIN event_types t ON t.id = e.event_type
               ORDER BY e.start_ts'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            all_day = 'Yes' if (r[2] or 0) & FLAG_ALL_DAY else 'No'
            repeats = 'Yes' if r[10] else 'No'
            data_list.append((
                _secs(r[0]), _secs(r[1]), all_day, r[3] or '', r[4] or '', r[5] or '',
                r[6] or '', _reminders(r[7], r[8], r[9]), repeats, r[11] or '',
                _lookup(STATUSES, r[12]), _lookup(EVENT_TYPES, r[13]), r[16] or '',
                _ms(r[14]), r[15] or '', context.get_relative_path(db_path),
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Start', 'datetime'), ('End', 'datetime'), 'All Day', 'Title', 'Location',
        'Description', 'Time Zone', 'Reminders (minutes)', 'Repeats', 'Attendees',
        'Status', 'Type', 'Calendar', ('Last Updated', 'datetime'), 'Source', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
