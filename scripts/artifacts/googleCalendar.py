# pylint: disable=W0613
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
        },
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


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
def get_calendar(files_found, report_folder, seeker, wrap_text):
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
def get_calendar_calendars(files_found, report_folder, seeker, wrap_text):
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
