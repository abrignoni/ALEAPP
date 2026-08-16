__artifacts_v2__ = {
    "get_calendar": {
        "name": "Calendar - Events",
        "description": "Parses provider calendar events",
        "author": "@KevinPagano3",
        "creation_date": "2023-01-06",
        "last_update_date": "2023-01-06",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('*/com.android.providers.calendar/databases/calendar.db*',),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.calendar | 0 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.calendar | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.calendar | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.calendar | 62 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.calendar | 0 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.calendar | 0 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.calendar | 1 row",
            "sharon_a14": "Android 14 | com.android.providers.calendar | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.calendar | 79 rows",
            "userb2_a13": "Android 13 | com.android.providers.calendar | 0 rows",
        },
    },
    "get_calendar_calendars": {
        "name": "Calendar - Calendars",
        "description": "Parses provider calendars",
        "author": "@KevinPagano3",
        "creation_date": "2023-01-06",
        "last_update_date": "2023-01-06",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('*/com.android.providers.calendar/databases/calendar.db*',),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.calendar | 4 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.calendar | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.calendar | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.calendar | 4 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.calendar | 1 row",
            "samsunga53_a14": "Android 14 | com.android.providers.calendar | 5 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.calendar | 3 rows",
            "sharon_a14": "Android 14 | com.android.providers.calendar | 4 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.calendar | 3 rows",
            "userb2_a13": "Android 13 | com.android.providers.calendar | 1 row",
        },
    },
    "googleCalendarAppEvents": {
        "name": "Google Calendar App Events",
        "description": "Events from the Google Calendar app's own store (cal_v2a, Events "
                       "table), kept separately from the calendar provider "
                       "database: start and end, title, description, the calendar and "
                       "account they belong to and the event web link, decoded from each "
                       "event's protobuf record.",
        "author": "@stark4n6",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Calendar",
        "notes": "Created and Updated are protobuf fields 4 and 5 of the event record. The "
                 "event type is stored as a raw integer and is reported as-is.",
        "paths": ('*/com.google.android.calendar/databases/cal_v2a*',),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.calendar | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.calendar | 190 rows",
            "pixel7a_a14": "Android 14 | com.google.android.calendar | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.calendar | 96 rows",
            "userb2_a13": "Android 13 | com.google.android.calendar | 0 rows",
        },
    },
}

import datetime
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, \
    get_sqlite_db_records, convert_unix_ts_to_utc, decode_protobuf, does_column_exist_in_db


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _calendar_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('calendar.db'):
            return file_found
    return ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_calendar(context):
    files_found = context.get_files_found()
    source_path = _calendar_db(files_found)
    rows = _run(source_path, '''
        SELECT Events.dtstart, Events.dtend, Events.eventTimezone, Events.title, Events.description,
        Events.eventLocation, Events._sync_id, Events.organizer, Calendars.calendar_displayName,
        CASE Events.allDay WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE Events.hasAlarm WHEN 0 THEN '' WHEN 1 THEN 'Yes' END
        FROM Events LEFT JOIN Calendars ON Calendars._id = Events.calendar_id
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10])
                 for r in rows]
    data_headers = (
        ('Event Start Timestamp', 'datetime'), ('Event End Timestamp', 'datetime'), 'Event Timezone',
        'Title', 'Description', 'Event Location', 'Sync ID', 'Organizer', 'Calendar Display Name',
        'All Day Event', 'Has Alarm')
    return data_headers, data_list, source_path


@artifact_processor
def get_calendar_calendars(context):
    files_found = context.get_files_found()
    source_path = _calendar_db(files_found)
    rows = _run(source_path, '''
        SELECT cal_sync8, name, calendar_displayName, account_name, account_type,
        CASE visible WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        calendar_location, calendar_timezone, ownerAccount,
        CASE isPrimary WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        calendar_color, calendar_color_index
        FROM Calendars
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11])
                 for r in rows]
    data_headers = (
        ('Created Timestamp', 'datetime'), 'Calendar Name', 'Calendar Display Name', 'Account Name',
        'Account Type', 'Visible', 'Calendar Location', 'Timezone', 'Owner Account', 'Is Primary',
        'Color', 'Color Index')
    return data_headers, data_list, source_path


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -wal/-shm sidecars and without the
    duplicates extractions carry for the same file (data_mirror, and /data/data next
    to /data/user/0).

    The dedupe key is the evidence-relative path, not the extracted path: the report's own
    data folder ends in /data, so a raw-path replace can rewrite the harness boundary
    instead of the evidence path on archives whose members start with data/.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


def _pb_get(node, *path):
    '''Defensively walk a blackboxprotobuf dict.'''
    cur = node
    for key in path:
        if isinstance(cur, list):
            cur = cur[0] if cur else None
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _pb_str(node, *path):
    value = _pb_get(node, *path)
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    return ''


def _pb_ts(node, *path):
    value = _pb_get(node, *path)
    if isinstance(value, int) and value > 0:
        return convert_unix_ts_to_utc(value)
    return ''


@artifact_processor
def googleCalendarAppEvents(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'cal_v2a'):
        # older Google Calendar versions do not have the EventType column
        event_type_column = 'e.EventType' if does_column_exist_in_db(
            file_found, 'Events', 'EventType') else "''"
        db_records = get_sqlite_db_records(file_found, f'''
            SELECT e.Proto, e.EventId, {event_type_column}, e.ToBeRemoved,
                   a.PlatformAccountName
            FROM Events AS e
            LEFT JOIN Accounts AS a ON a.AccountId = e.AccountId
            ORDER BY e.StartDayUtc DESC
        ''')

        for row in db_records:
            source_path = file_found
            title = description = link = ical_uid = ''
            calendar_id = calendar_name = ''
            start = end = created = updated = ''
            try:
                event, _ = decode_protobuf(row[0])
                title = _pb_str(event, '6')
                description = _pb_str(event, '7')
                link = _pb_str(event, '3')
                ical_uid = _pb_str(event, '19')
                calendar_id = _pb_str(event, '10', '1') or _pb_str(event, '35', '1')
                calendar_name = _pb_str(event, '10', '2') or _pb_str(event, '35', '2')
                start = _pb_ts(event, '36', '1')
                end = _pb_ts(event, '37', '1')
                created = _pb_ts(event, '4')
                updated = _pb_ts(event, '5')
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # unparseable protobuf; keep the row with the table columns only
            data_list.append((
                start,
                end,
                title,
                description,
                row[4],
                calendar_name,
                calendar_id,
                created,
                updated,
                row[2],
                row[3],
                link,
                ical_uid,
                row[1],
            ))

    data_headers = (
        ('Start', 'datetime'),
        ('End', 'datetime'),
        'Title',
        'Description',
        'Account',
        'Calendar Name',
        'Calendar ID',
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Event Type',
        'To Be Removed',
        'Event Web Link',
        'iCal UID',
        'Event ID',
    )
    return data_headers, data_list, source_path
