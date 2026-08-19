__artifacts_v2__ = {
    "samsungBixbyRoutinesUserRoutines": {
        "name": "Samsung Bixby Routines - User Routines",
        "description": (
            "Parses created by user Bixby Routines automations from the `routine` "
            "table of com.samsung.android.app.routines/databases/routine.db. "
            "Each row is a routine the device owner named and configured "
            "(condition/action wiring itself lives in routine_extra, an "
            "app-internal blob that is not decoded here)."
        ),
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Bixby Routines",
        "notes": (
            "The `routine` table is the only table in routine.db that holds "
            "user-authored automations; the sibling `condition` and `action` "
            "tables are Samsung's app-shipped catalog of available trigger/"
            "action building blocks (identical row shape on every device "
            "running the same app build) and are not parsed here since they "
            "are not user data. Toggle Time is reported as stored (epoch "
            "milliseconds, converted to UTC); it was not independently "
            "confirmed against a known reference event in testing, so treat "
            "it as 'last time this row's is_running flag changed' rather "
            "than a fully verified semantic. routine_extra is not decoded: "
            "in the one device tested against, the table held zero rows, so "
            "the blob's structure could not be inspected. A zero-row result "
            "means no routine existed in this table at acquisition time; it "
            "is not evidence Bixby Routines was never configured, since a "
            "deleted or never-synced routine would not appear here."
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "zap",
         "sample_data": {
            "samsung_s21ultra_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 0 rows",
        },
    },
    "samsungBixbyRoutinesServiceLog": {
        "name": "Samsung Bixby Routines - Service Log",
        "description": (
            "Parses the routine_history table of com.samsung.android.app."
            "routines/databases/routine.db, an internal timestamped log "
            "kept by the Routines background service (job scheduling, "
            "metaloader/catalog-update events, widget provider callbacks)."
        ),
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Bixby Routines",
        "notes": (
            "This is service telemetry, not a record of a specific routine "
            "firing: in the device tested, all 50 rows carried routine_id "
            "= -1 and Log Message text such as '[RoutineService] D2 "
            "time=...', 'JobSchedule request - true', and "
            "'Metaloader-notifyRoutineUpdate' -- none named a user routine. "
            "The parser still resolves routine_id against the `routine` "
            "table (LEFT JOIN) in case a future or different device does "
            "record a real routine_id, but Linked Routine Name will be "
            "blank whenever that join finds nothing, which was true for "
            "every tested row. Treat this artifact as evidence the "
            "Routines app process was alive and scheduling work at these "
            "timestamps -- useful for corroborating general device "
            "activity/uptime in a period -- and not as evidence of what "
            "automation, if any, ran."
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
         "sample_data": {
            "samsung_s21ultra_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 50 rows",
        },
        
    },
    "samsungBixbyRoutinesPreferences": {
        "name": "Samsung Bixby Routines - App Preferences",
        "description": (
            "Parses the key/value preference table of com.samsung.android."
            "app.routines/databases/routine.db, which holds app-level "
            "settings and state such as first-run/install time and Bixby "
            "'sleep' feature usage counters."
        ),
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Bixby Routines",
        "notes": (
            "Values are reported as stored (TEXT column, so numeric-looking "
            "values are strings). A fixed set of keys observed in testing "
            "to hold epoch-millisecond timestamps (init_time, latest_time, "
            "sleep_expired_time, update_noti_time) are additionally decoded "
            "into a Converted Timestamp column; every other key is left "
            "blank in that column rather than guessed at. init_time in the "
            "tested device matched the general install-era timeframe "
            "implied elsewhere in the extraction, but was not cross-"
            "verified against a package-manager install-time record, so "
            "treat it as indicative rather than confirmed. This table is "
            "app configuration, not user content -- it will not show what "
            "routines existed, only whether/when the feature was used."
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
        "samsung_s21ultra_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 15 rows",
        },
     },
}

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
)

# Keys in the `preference` table observed (in the one device tested against)
# to hold epoch-millisecond timestamps. Any other key is reported with a
# blank Converted Timestamp rather than a guessed conversion.
_TIMESTAMP_PREFERENCE_KEYS = {
    "init_time",
    "latest_time",
    "sleep_expired_time",
    "update_noti_time",
}


def _iter_target_dbs(context):
    """Yield (file_found, source_path) for each routine.db found, skipping
    SQLite sidecar files that the glob also matches."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        yield file_found, context.get_relative_path(file_found)


@artifact_processor
def samsungBixbyRoutinesUserRoutines(context):
    data_headers = (
        'Routine ID',
        'Name',
        'Is Running',
        'Is Manual Routine',
        'Is Favorite Routine',
        'Is Show Notification',
        ('Toggle Time', 'datetime'),
        'Tag',
        'Icon Resource ID',
        'Color',
    )
    data_list = []
    source_path = ""

    query = '''
    SELECT _id, name, is_running, is_manual_routine, is_favorite_routine,
           is_show_notification, toggle_time, tag, icon, color
    FROM routine
    ORDER BY _id
    '''

    for file_found, rel_path in _iter_target_dbs(context):
        if not does_table_exist_in_db(file_found, 'routine'):
            continue
        db_records = get_sqlite_db_records(file_found, query)
        if db_records is None:
            continue
        source_path = rel_path
        count = 0
        for row in db_records:
            (routine_id, name, is_running, is_manual, is_favorite,
             is_show_notification, toggle_time, tag, icon, color) = row
            data_list.append((
                routine_id,
                name,
                is_running,
                is_manual,
                is_favorite,
                is_show_notification,
                convert_unix_ts_to_utc(toggle_time) if toggle_time else None,
                tag,
                icon,
                color,
            ))
            count += 1
        logfunc(f"Samsung Bixby Routines: {count} user routine(s) in {rel_path}")

    return data_headers, data_list, source_path


@artifact_processor
def samsungBixbyRoutinesServiceLog(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Routine ID (raw)',
        'Linked Routine Name',
        'Is Running',
        'Service Status',
        'Log Message',
    )
    data_list = []
    source_path = ""

    query = '''
    SELECT rh.timestamp, rh.routine_id, r.name, rh.is_running,
           rh.service_status, rh.name
    FROM routine_history rh
    LEFT JOIN routine r ON rh.routine_id = r._id
    ORDER BY rh.timestamp
    '''

    for file_found, rel_path in _iter_target_dbs(context):
        if not does_table_exist_in_db(file_found, 'routine_history'):
            continue
        db_records = get_sqlite_db_records(file_found, query)
        if db_records is None:
            continue
        source_path = rel_path
        count = 0
        for row in db_records:
            (timestamp, routine_id, linked_name, is_running,
             service_status, log_message) = row
            data_list.append((
                convert_unix_ts_to_utc(timestamp) if timestamp else None,
                routine_id,
                linked_name if linked_name else "",
                is_running,
                service_status,
                log_message,
            ))
            count += 1
        logfunc(f"Samsung Bixby Routines: {count} service log record(s) in {rel_path}")

    return data_headers, data_list, source_path


@artifact_processor
def samsungBixbyRoutinesPreferences(context):
    data_headers = (
        'Key',
        'Value',
        ('Converted Timestamp', 'datetime'),
    )
    data_list = []
    source_path = ""

    query = 'SELECT key, value FROM preference ORDER BY key'

    for file_found, rel_path in _iter_target_dbs(context):
        if not does_table_exist_in_db(file_found, 'preference'):
            continue
        db_records = get_sqlite_db_records(file_found, query)
        if db_records is None:
            continue
        source_path = rel_path
        count = 0
        for key, value in db_records:
            converted = None
            if key in _TIMESTAMP_PREFERENCE_KEYS and value:
                try:
                    converted = convert_unix_ts_to_utc(int(value))
                except (TypeError, ValueError):
                    converted = None
            data_list.append((key, value, converted))
            count += 1
        logfunc(f"Samsung Bixby Routines: {count} preference row(s) in {rel_path}")

    return data_headers, data_list, source_path