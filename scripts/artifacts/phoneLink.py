__artifacts_v2__ = {
    "phonelink_content_access": {
        "name": "Phone Link - Content Access Events",
        "description": "Rows from the content_access_event table of the app's eventstore, each "
                       "recording that content of a stored type was accessed through the link "
                       "and for how long",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Phone Link",
        "notes": "com.microsoft.appmanager is the phone side of Microsoft Phone Link, which "
                 "pairs a phone with a Windows PC. content_access_event is the only table in "
                 "this package holding a dated user-driven event on the corpora below. "
                 "start_time is Unix milliseconds and duration is stored alongside it without a "
                 "recorded unit, so Duration (as stored) is reported unconverted. Content Type "
                 "(as stored) and Access Was Useful (as stored) are the schema's own integer "
                 "columns; no source for their code lists was located, so they are not expanded "
                 "into labels. Content Type was 22 on every row of four of the five corpora "
                 "below and carried fifteen different values on the fifth. The table is a "
                 "rolling buffer the app trims, so the database and its write-ahead log hold "
                 "different row sets: this artifact reads both and reports their union, with "
                 "Reading naming where each row was found. Rows marked as recovered from the "
                 "pre-log database are ones the current state no longer carries, and on the "
                 "corpora below that recovered 16 of 17 rows on one image and 5 of 14 on "
                 "another, while on a third every row was in the current state and none was "
                 "recovered. The same eventstore holds FcmNotificationEvent and "
                 "agent_service_event, which held at most 1 and 3 rows on a single corpus and "
                 "have no artifact here.",
        "paths": ('*/com.microsoft.appmanager/databases/eventstore*',),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "s20fe_a13": "Android 13 | com.microsoft.appmanager | 28 rows",
            "samsunga53_a14": "Android 14 | com.microsoft.appmanager | 17 rows",
            "sharon_a14": "Android 14 | com.microsoft.appmanager | 14 rows",
            "kevin_pocox7_a15": "Android 15 | com.microsoft.appmanager | 10 rows",
            "anne_a15": "Android 15 | com.microsoft.appmanager | 3 rows",
        },
    },
    "phonelink_phone_apps": {
        "name": "Phone Link - Linked Phone Apps",
        "description": "Rows from the phoneAppsTable of PhoneAppsDatabase, the inventory of "
                       "applications the phone reported to the paired PC, with each one's "
                       "package name and version",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Phone Link",
        "notes": "PhoneAppsDatabase is the list of installed applications the phone side sends "
                 "to the paired PC so they can be launched from it, so it is a record of what "
                 "was installed built by a different subsystem than the package manager and can "
                 "be compared against it. Last Updated is Unix milliseconds and held the same "
                 "value on all 75 rows of the corpus below, so it dates the inventory as a "
                 "whole rather than each application; it is kept because that is the time the "
                 "inventory was written. Favorite Rank was 0 on every row there, so no "
                 "application had been pinned in the app, and the column is kept because a "
                 "non-zero value would identify one that had been. The same database holds "
                 "browserHistoryTable, whose columns include a web address and a favicon, and "
                 "recentAppsTable, whose columns include a task id and an intent action; both "
                 "were present and empty on every corpus below and neither has an artifact "
                 "here, so their absence is a checked result rather than an omission. A corpus "
                 "with rows in browserHistoryTable would close a real gap, since that table is "
                 "where the phone's browsing reaches the PC. content.db in the same package "
                 "holds a content_view table, 183 rows on the corpus below, carrying only a "
                 "content type, an id, two sequence numbers and a checksum; it is the sync "
                 "bookkeeping behind the tables above and names nothing an examiner could act "
                 "on, so it is not reported.",
        "paths": ('*/com.microsoft.appmanager/databases/PhoneAppsDatabase*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.microsoft.appmanager | 75 rows",
            "cookbook_a11": "Android 11 | com.microsoft.appmanager | 0 rows",
        },
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_sqlite_db_path,
    get_sqlite_db_records,
    logfunc,
)

import sqlite3

SIDECARS = ('-wal', '-shm', '-journal')

CURRENT_STATE = 'Current state'
PRE_LOG_ONLY = 'Recovered from the database without its log'


def _stores(context, name):
    """The named database files, storage views collapsed and sidecars dropped."""
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if os.path.basename(file_found) == name:
            found.append(file_found)
    return found


def _read_both_ways(db_path, query, key_index):
    """Rows from the database with its log applied, plus rows only the file holds.

    The table this reads is a rolling buffer the application trims, so the write
    ahead log can carry deletions: the file alone then holds rows the current state
    no longer has, and the current state holds rows not yet written back. Reading
    only one of the two loses whichever set that reading drops, so both are read and
    keyed on the table's own primary key. Which reading a row came from is reported
    rather than hidden, because a row absent from the current state is a different
    claim than one present in it.
    """
    rows = {}
    for uri_suffix, label in (('mode=ro', CURRENT_STATE), ('immutable=1', PRE_LOG_ONLY)):
        try:
            connection = sqlite3.connect(
                f'file:{get_sqlite_db_path(db_path)}?{uri_suffix}', uri=True)
            for row in connection.cursor().execute(query):
                rows.setdefault(row[key_index], (row, label))
            connection.close()
        except sqlite3.Error as error:
            logfunc(f'Phone Link: could not read {os.path.basename(db_path)} '
                    f'({uri_suffix}): {error}')
    return rows


@artifact_processor
def phonelink_content_access(context):
    data_list = []
    source_paths = []
    query = ('SELECT uid, start_time, duration, content_type, access_was_useful '
             'FROM content_access_event')

    for db_path in _stores(context, 'eventstore'):
        rows = _read_both_ways(db_path, query, 0)
        if not rows:
            continue
        source_paths.append(context.get_relative_path(db_path))
        for uid, (row, label) in sorted(rows.items(), key=lambda item: item[1][0][1] or 0):
            _, start_time, duration, content_type, useful = row
            data_list.append((
                convert_unix_ts_to_utc(start_time / 1000) if start_time else '',
                duration if duration is not None else '',
                content_type if content_type is not None else '',
                useful if useful is not None else '',
                label,
                uid,
            ))

    data_headers = (
        ('Access Time', 'datetime'),
        'Duration (as stored)',
        'Content Type (as stored)',
        'Access Was Useful (as stored)',
        'Reading',
        'Event ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def phonelink_phone_apps(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context, 'PhoneAppsDatabase'):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT lastUpdatedTime, appName, appPackageName, appVersion, favoriteRank, id
            FROM phoneAppsTable ORDER BY appName
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for updated, app_name, package, version, favorite, app_id in rows:
            data_list.append((
                convert_unix_ts_to_utc(updated / 1000) if updated else '',
                app_name or '',
                package or '',
                version or '',
                favorite if favorite is not None else '',
                app_id if app_id is not None else '',
            ))

    data_headers = (
        ('Last Updated', 'datetime'),
        'App Name',
        'Package Name',
        'App Version',
        'Favorite Rank',
        'App ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
