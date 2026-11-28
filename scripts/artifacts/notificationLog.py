__artifacts_v2__ = {
    "notification_log_db": {
        "name": "Notification Log (notification_log.db)",
        "description": "Notification post, click, remove and dismiss events from the log table of "
                       "system/notification_log.db.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Device Activity",
        "notes": (
            "Reads the log table of system/notification_log.db. The table and its columns match the "
            "SQLiteLog class of AOSP NotificationUsageStats.java on the android11-release branch (commit "
            "8551ec363dcd7c2d7c82c45e89db4922156766ab, "
            "services/core/java/com/android/server/notification/NotificationUsageStats.java:1059-1190, "
            "database version 7), and the meanings below are that class's. The class is absent from the "
            "android12-release and android13-release versions of the file; what writes the database on "
            "Android 12 or later was not established. On a version upgrade the class drops the log table "
            "and creates it again (NotificationUsageStats.java:1200-1205). Version 5 databases, written "
            "by the android10-release version of the class, lack the undecorated column, which is then "
            "blank. Event Type is event_type with the name of the class's constant "
            "(NotificationUsageStats.java:1096-1099): 1 POST, written by registerPostedByApp and "
            "registerUpdatedByApp; 2 CLICK, by registerClickedByUser; 3 REMOVE, by registerRemovedByApp; "
            "4 DISMISS, by registerDismissedByUser (NotificationUsageStats.java:143-213); any other value "
            "is shown as stored. What calls those methods is outside this file and was not traced. Event "
            "Time is event_time_ms: for a POST row the notification's post time, for the other types the "
            "time the event was written (NotificationUsageStats.java:1142-1154), read as Unix "
            "milliseconds. Notification ID, Tag, Flags, Importance Requested, Importance Final, Demoted, "
            "Noisy, Muted, Category and Action Count are written on POST rows only "
            "(putNotificationDetails, NotificationUsageStats.java:1331-1355); Tag and Category are "
            "written only when the notification has one. Muted is 1 when the notification was noisy and "
            "its final importance was below IMPORTANCE_HIGH, Demoted when the final importance was below "
            "the requested one. Time Since Post (ms), Airtime (ms), Expansion Count, Expanded Airtime "
            "(ms) and First Expansion After (ms) are posttime_ms, airtime_ms, expansion_count, "
            "expansion_airtime_ms and first_expansion_time_ms, written on the other event types only "
            "(putPosttimeVisibility, NotificationUsageStats.java:1357-1363), as stored; a First Expansion "
            "After of -1 means the notification was never visibly expanded "
            "(NotificationUsageStats.java:845-848). Flags and the importance values are as stored. "
            "Android User is event_user_id. The class deletes rows older than one week when it writes a "
            "new row, at most once per 6 hours or 1,024 writes (NotificationUsageStats.java:1063-1067 and "
            "1308-1322), so a database that is no longer written to keeps the rows it held at its last "
            "write. A write-ahead log beside the database is applied; a database with no log beside it is "
            "read alone. Source File names the database when several are read."),
        "paths": ('*/system/notification_log.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "cookbook_a11": "Android 11 | 110 rows (99 POST, 11 REMOVE), database version 7",
            "galaxys10_a10": "Android 10 | 1251 rows (1091 POST, 4 CLICK, 155 REMOVE, 1 DISMISS), "
                             "database version 5",
        },
    },
}

import os
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, is_sqlite_sidecar, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
# NotificationUsageStats.SQLiteLog EVENT_TYPE_* (android11-release, lines 1096-1099).
EVENT_TYPES = {1: 'POST', 2: 'CLICK', 3: 'REMOVE', 4: 'DISMISS'}
# The columns read, in report order; a column the database lacks is read as NULL.
COLUMNS = ('event_time_ms', 'event_type', 'pkg', 'nid', 'tag', 'key', 'event_user_id',
           'category', 'flags', 'importance_request', 'importance_final', 'demoted', 'noisy',
           'muted', 'action_count', 'posttime_ms', 'airtime_ms', 'expansion_count',
           'expansion_airtime_ms', 'first_expansion_time_ms', 'undecorated', '_id')


def _ms_to_utc(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        return ''


def _rows(path, query):
    try:
        return list(get_sqlite_db_records(path, query))
    except sqlite3.DatabaseError as error:
        logfunc(f'Notification Log: could not read {path}: {error}')
        return []


def _blank(value):
    return '' if value is None else value


@artifact_processor
def notification_log_db(context):
    data_list = []
    sources = []
    databases = [str(f) for f in unique_files(context)
                 if os.path.basename(str(f)) == 'notification_log.db' and not is_sqlite_sidecar(str(f))]
    for path in databases:
        present = {row[1] for row in _rows(path, 'PRAGMA table_info(log)')}
        if not present:
            continue
        sources.append(path)
        select = ', '.join(column if column in present else 'NULL' for column in COLUMNS)
        relative = context.get_relative_path(path)
        for row in _rows(path, f'SELECT {select} FROM log ORDER BY event_time_ms'):
            values = dict(zip(COLUMNS, row))
            event_type = values['event_type']
            out = (
                _ms_to_utc(values['event_time_ms']),
                EVENT_TYPES.get(event_type, _blank(event_type)),
                _blank(values['pkg']), _blank(values['nid']),
                _blank(values['tag']), _blank(values['key']), _blank(values['event_user_id']),
                _blank(values['category']), _blank(values['flags']),
                _blank(values['importance_request']), _blank(values['importance_final']),
                _blank(values['demoted']), _blank(values['noisy']), _blank(values['muted']),
                _blank(values['action_count']), _blank(values['posttime_ms']),
                _blank(values['airtime_ms']), _blank(values['expansion_count']),
                _blank(values['expansion_airtime_ms']), _blank(values['first_expansion_time_ms']),
                _blank(values['undecorated']), _blank(values['_id']))
            data_list.append(out + ((relative,) if len(databases) > 1 else ()))
    data_headers = (
        ('Event Time', 'datetime'), 'Event Type', 'Package', 'Notification ID', 'Tag', 'Key',
        'Android User', 'Category', 'Flags (as stored)',
        'Importance Requested', 'Importance Final', 'Demoted', 'Noisy', 'Muted', 'Action Count',
        'Time Since Post (ms)', 'Airtime (ms)', 'Expansion Count', 'Expanded Airtime (ms)',
        'First Expansion After (ms)', 'Undecorated', 'Row ID')
    if len(databases) > 1:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sources)
