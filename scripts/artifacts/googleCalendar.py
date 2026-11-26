__artifacts_v2__ = {
    "get_calendar": {
        "name": "Calendar - Events",
        "description": "Parses provider calendar events",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2023-01-06",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Productivity",
        "notes": "Every calendar.db found is read once per Android user, and Android User names the "
                 "user whose app folder holds it. Taking the first match instead returned no rows on a "
                 "One UI 8 (Android 16) extraction whose Secure Folder user's copy sorted first and held "
                 "no events while the owner's copy held three."
                 " On the four tested Android 16 extractions Android User held one value (0) on every row, because the Secure Folder user's copy held no events. Event Location had no value on any of the 111 rows of one extraction and on any of the 3 rows of another. On those 3 rows Description and All Day Event had no value, and Event Timezone, Organizer, Calendar Display Name and Has Alarm each held one value. On the corpus images in sample_data that hold a second Android user's database, the row count equals the sum of the rows in each user's table, counted without ALEAPP."
                 " A calendar.db that ALEX (Android Logical Extractor) rebuilt from content provider queries, recognised by user_version 0 and Events._id declared TEXT, is read with the same queries as a device copy, except that rows with _id 0 are left out of Events and their number is written to the log. ALEX from v0.6 to commit 9ef34bf0 (prosch88/ALEX, 2026-11-21) writes such a row, filled with its default values, when the provider returned no rows; commit 8f27e7a (2026-11-25) stopped that. ALEX from v0.6 to 8f27e7a also writes one when a text value held 'Row: <number>': that value is cut there and the columns after it go to the _id 0 row. From v0.6 to 8f27e7a its parsing of the query output can also trim text and store an empty value as NULL. From v0.6 to ed3d41eb it stores the text NULL as NULL, and can cut a text value at ', <column name>=' and move the rest into that column. From v0.6 to ed3d41eb ALEX declares every column TEXT; on the three known data backups every stored value is text or NULL. The rebuilt database is a new file written by ALEX, so it carries no free pages or write-ahead log from the device database. A time stored as the text 0 is shown blank, as a stored 0 is. No real event row from an ALEX rebuild was available to test this. On the known data emu_a15_alex_prfs_empty_20261125 and emu_a15_alex_prfs_sms_20261125 (ALEX backups of an Android 15 emulator, ALEAPP #2076) this left out one default Events row each time, so no rows were reported, where the version before this change reported 1 event dated 1970-01-01."
                 " On emu_a15_alex_prfs_fixed_20261125 (ALEX at ed3d41eb, the same emulator and messages) ALEX wrote no _id 0 row and stored the 6 synthetic message bodies as inserted, nothing was left out, and this artifact reported 0 rows. ALEX's source at ed3d41eb can still write an _id 0 row when a text value holds a line break followed by 'Row: <number> <column name>='; that case was not on the emulator.",
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
            "cookbook_a11": "Android 11 | com.android.providers.calendar | 1 row",
            "russell_a14": "Android 14 | com.android.providers.calendar | 235 rows",
            "emu_a15_alex_prfs_empty_20261125": "Android 15 | ALEX PRFS backup of an emulator (known data) | 0 rows",
            "emu_a15_alex_prfs_sms_20261125": "Android 15 | ALEX PRFS backup of an emulator (known data) | 0 rows",
            "emu_a15_alex_prfs_fixed_20261125": "Android 15 | ALEX PRFS backup of an emulator (known data) | 0 rows",
        },
    },
    "get_calendar_calendars": {
        "name": "Calendar - Calendars",
        "description": "Calendars table of the calendar provider database.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2023-01-06",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Productivity",
        "notes": "Every calendar.db found is read once per Android user, and Android User names the "
                 "user whose app folder holds it. The first column, cal_sync8 (Read As Unix "
                 "Milliseconds), is the cal_sync8 value read as Unix milliseconds and shown in UTC; the cal_sync8 (As Stored) column is the "
                 "same value as stored. Android documents cal_sync8 as a generic column for use by sync "
                 "adapters, type TEXT "
                 "(https://android.googlesource.com/platform/frameworks/base/+/"
                 "299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/"
                 "CalendarContract.java#326), "
                 "and the provider's upgrade from version 304 to 305 renamed the Calendars _sync_time "
                 "column to it "
                 "(https://android.googlesource.com/platform/packages/providers/CalendarProvider/+/"
                 "94405b4ad2ca9ddec5fcad85d42cd308229b61f0/src/com/android/providers/calendar/"
                 "CalendarDatabaseHelper.java#1724). "
                 "What a sync adapter stores there is the adapter's choice. What the value marks is "
                 "not established, and the reading as Unix milliseconds rests on the size of the "
                 "stored values, not on a source. On the twelve listed images every Calendars row with "
                 "account type com.google stored a 13 digit text value and every row with another "
                 "account type (LOCAL, com.osp.app.signin, com.xiaomi) stored NULL. A stored value "
                 "that is not a whole number leaves the first column blank and appears only in the "
                 "cal_sync8 (As Stored) column."
                 " On the four tested Android 16 extractions Calendar Location had no value on any row, and Android User held one value (0) on every row of the one extraction that holds a single user's calendars. On two of them cal_sync8 (Read As Unix Milliseconds) had no value on any of 5 rows, and Timezone, Is Primary and Color Index had no value on any row, Account Name and Owner Account were identical on all 5 rows, and on one of them Visible held one value (Yes). On the corpus images in sample_data that hold a second Android user's database, the row count equals the sum of the rows in each user's table, counted without ALEAPP."
                 " A calendar.db that ALEX (Android Logical Extractor) rebuilt from content provider queries, recognised by user_version 0 and Events._id declared TEXT, is read with the same queries as a device copy, except that rows with _id 0 are left out of Calendars and their number is written to the log. ALEX from v0.6 to commit 9ef34bf0 (prosch88/ALEX, 2026-11-21) writes such a row, filled with its default values, when the provider returned no rows; commit 8f27e7a (2026-11-25) stopped that. ALEX from v0.6 to 8f27e7a also writes one when a text value held 'Row: <number>': that value is cut there and the columns after it go to the _id 0 row. From v0.6 to 8f27e7a its parsing of the query output can also trim text and store an empty value as NULL. From v0.6 to ed3d41eb it stores the text NULL as NULL, and can cut a text value at ', <column name>=' and move the rest into that column. From v0.6 to ed3d41eb ALEX declares every column TEXT; on the three known data backups every stored value is text or NULL. The rebuilt database is a new file written by ALEX, so it carries no free pages or write-ahead log from the device database. A time stored as the text 0 is shown blank, as a stored 0 is. No real calendar row from an ALEX rebuild was available to test this. On the known data emu_a15_alex_prfs_empty_20261125 and emu_a15_alex_prfs_sms_20261125 (ALEX backups of an Android 15 emulator, ALEAPP #2076) this left out one default Calendars row each time, so no rows were reported, where the version before this change reported 1 calendar."
                 " On emu_a15_alex_prfs_fixed_20261125 (ALEX at ed3d41eb, the same emulator and messages) ALEX wrote no _id 0 row and stored the 6 synthetic message bodies as inserted, nothing was left out, and this artifact reported 0 rows. ALEX's source at ed3d41eb can still write an _id 0 row when a text value holds a line break followed by 'Row: <number> <column name>='; that case was not on the emulator.",
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
            "samsungs20_a13": "Android 13 | com.android.providers.calendar | 4 rows",
            "sharon_a14": "Android 14 | com.android.providers.calendar | 4 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.calendar | 4 rows",
            "userb2_a13": "Android 13 | com.android.providers.calendar | 1 row",
            "cookbook_a11": "Android 11 | com.android.providers.calendar | 4 rows",
            "russell_a14": "Android 14 | com.android.providers.calendar | 4 rows",
            "emu_a15_alex_prfs_empty_20261125": "Android 15 | ALEX PRFS backup of an emulator (known data) | 0 rows",
            "emu_a15_alex_prfs_sms_20261125": "Android 15 | ALEX PRFS backup of an emulator (known data) | 0 rows",
            "emu_a15_alex_prfs_fixed_20261125": "Android 15 | ALEX PRFS backup of an emulator (known data) | 0 rows",
        },
    },
    "googleCalendarAppEvents": {
        "name": "Google Calendar App Events",
        "description": "Events from the Google Calendar app's own store (cal_v2a, Events "
                       "table), kept separately from the calendar provider "
                       "database: start and end, title, description, the calendar and "
                       "account they belong to and the event web link, decoded from each "
                       "event's protobuf record.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Productivity",
        "notes": "The fields are read from the event protobuf by number: link 3, Created "
                 "4, Updated 5, title 6, description 7, calendar id and name 10 (or 35), "
                 "iCal UID 19, start 36.1 and end 37.1. No source for these field numbers "
                 "is cited. Account is the PlatformAccountName of the Accounts table row "
                 "the event points to. The "
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

from scripts.artifacts.storagePathViews import user_files
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, \
    get_sqlite_db_records, convert_unix_ts_to_utc, decode_protobuf, does_column_exist_in_db, \
    alex_default_row_filter


def _ms_to_utc(value):
    # int() first: a database ALEX rebuilt stores every value as text, so 0 arrives as '0'
    try:
        number = int(value)
        return datetime.datetime.fromtimestamp(number / 1000, datetime.timezone.utc) if number else ''
    except (ValueError, OverflowError, OSError, TypeError):
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


def _run_all(stores, sql, table):
    """The rows of sql from every (database path, Android user) pair, each row followed by its user.
    sql holds {keep}, the condition that leaves out ALEX default rows of table."""
    rows = []
    for source_path, user in stores:
        query = sql.format(keep=alex_default_row_filter(source_path, table))
        rows.extend(tuple(row) + (user,) for row in _run(source_path, query))
    return rows


@artifact_processor
def get_calendar(context):
    stores = user_files(context, 'calendar.db')
    rows = _run_all(stores, '''
        SELECT Events.dtstart, Events.dtend, Events.eventTimezone, Events.title, Events.description,
        Events.eventLocation, Events._sync_id, Events.organizer, Calendars.calendar_displayName,
        CASE Events.allDay WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE Events.hasAlarm WHEN 0 THEN '' WHEN 1 THEN 'Yes' END
        FROM Events LEFT JOIN Calendars ON Calendars._id = Events.calendar_id
        WHERE {keep}
    ''', 'Events')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10],
                  r[11])
                 for r in rows]
    data_headers = (
        ('Event Start Timestamp', 'datetime'), ('Event End Timestamp', 'datetime'), 'Event Timezone',
        'Title', 'Description', 'Event Location', 'Sync ID', 'Organizer', 'Calendar Display Name',
        'All Day Event', 'Has Alarm', 'Android User')
    return data_headers, data_list, '\n'.join(path for path, _ in stores)


@artifact_processor
def get_calendar_calendars(context):
    stores = user_files(context, 'calendar.db')
    rows = _run_all(stores, '''
        SELECT cal_sync8, name, calendar_displayName, account_name, account_type,
        CASE visible WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        calendar_location, calendar_timezone, ownerAccount,
        CASE isPrimary WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        calendar_color, calendar_color_index
        FROM Calendars
        WHERE {keep}
    ''', 'Calendars')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11],
                  r[0], r[12])
                 for r in rows]
    data_headers = (
        ('cal_sync8 (Read As Unix Milliseconds)', 'datetime'), 'Calendar Name', 'Calendar Display Name', 'Account Name',
        'Account Type', 'Visible', 'Calendar Location', 'Timezone', 'Owner Account', 'Is Primary',
        'Color', 'Color Index', 'cal_sync8 (As Stored)', 'Android User')
    return data_headers, data_list, '\n'.join(path for path, _ in stores)


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
