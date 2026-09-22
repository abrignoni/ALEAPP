__artifacts_v2__ = {
    "samsungBixbyRoutinesUserRoutines": {
        "name": "Samsung Bixby Routines - User Routines",
        "description": (
            "Parses the `routine` table of com.samsung.android.app.routines/"
            "databases/routine.db, which holds the named Bixby Routines "
            "automations stored on the device. "
            "The trigger and action wiring for each routine is held in the "
            "sibling condition_instance and action_instance tables, reported by "
            "the Routine Conditions and Routine Actions artifacts and joined on "
            "Routine ID."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "The `routine` table carries a unique per-row name and the "
            "presentation fields an automation is configured with; the "
            "sibling `condition` and `action` tables are the app-shipped "
            "catalog of available trigger and action building blocks, "
            "carrying resource ids and provider class names rather than user "
            "data, and are not parsed here. Toggle Time is stored in epoch "
            "milliseconds: two of the eight tested extractions carried a "
            "non-zero value, both 13 digits and out of representable range if "
            "read as seconds, and the other six stored zero, which is "
            "reported blank. is_favorite_routine is absent from the oldest "
            "tested release, where it is reported empty rather than failing "
            "the whole query and returning nothing. routine_extra is a TEXT "
            "column of this table, not a separate table, and is not decoded "
            "here. The store held fifteen tables across the tested "
            "extractions and each is accounted for: routine, "
            "routine_running_history, condition_instance, action_instance, "
            "location_history, routine_history and preference are the seven "
            "this module parses; condition and action are the app-shipped "
            "catalog described above; recommend holds condition and action "
            "pairings the app generated for itself, with an accuracy score "
            "and a recommend_source, which is not a record of anything the "
            "user did and is not reported; action_snap, condition_snap and "
            "suggestion_routine_history were present on some releases and "
            "empty in every extraction tested; android_metadata and "
            "sqlite_sequence are SQLite and Android bookkeeping. A zero-row "
            "result means no routine was present in this table at "
            "acquisition; it is not a finding that Bixby Routines was never "
            "configured, since a deleted routine would not appear here."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "zap",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 1 row",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 0 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 1 row",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 1 row",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 1 row",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 1 row",
        },
    },
    "samsungBixbyRoutinesRunHistory": {
        "name": "Samsung Bixby Routines - Routine Run History",
        "description": (
            "Parses the routine_running_history table of com.samsung.android."
            "app.routines/databases/routine.db, which records a named routine "
            "against a timestamp."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "This table carries routine_name alongside routine_id, so a row "
            "names the routine it refers to without depending on the routine "
            "still existing in the `routine` table. running_type and "
            "recover_type are undocumented integers and are reported as "
            "stored. Timestamp is decoded on the same magnitude basis as the "
            "other timestamps in this database. Three of the eight tested "
            "extractions held rows here, 12, 3 and 1 respectively; the table "
            "is absent from the oldest tested release, where the artifact "
            "reports nothing rather than failing. A zero-row result is a "
            "checked absence for that extraction, not a finding about whether "
            "any routine ran."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "play-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 12 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 0 rows (table not in this release)",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 3 rows",
        },
    },
    "samsungBixbyRoutinesConditions": {
        "name": "Samsung Bixby Routines - Routine Conditions",
        "description": (
            "Parses the condition_instance table of com.samsung.android.app."
            "routines/databases/routine.db, the per-routine trigger wiring: "
            "which condition tag, from which package, with which stored "
            "parameters, is attached to which routine."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "Rows are joined to the `routine` table on routine_id to carry "
            "the routine name where one is present; Routine Name is blank "
            "when the join finds nothing. intent_param, label_params and "
            "bundle_data hold app-defined parameter text and are reported as "
            "stored rather than decoded, since their structure varies by "
            "condition tag. is_negative marks a condition the app stores in "
            "its inverted form; valid_state is an undocumented integer "
            "reported as stored. Six of the eight tested extractions held "
            "rows here, one or two each, and each row joined to a routine."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "git-branch",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 2 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 0 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 1 row",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 1 row",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 1 row",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 1 row",
        },
    },
    "samsungBixbyRoutinesActions": {
        "name": "Samsung Bixby Routines - Routine Actions",
        "description": (
            "Parses the action_instance table of com.samsung.android.app."
            "routines/databases/routine.db, the per-routine action wiring: "
            "which action tag, from which package, with which stored "
            "parameters, is attached to which routine."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "Rows are joined to the `routine` table on routine_id to carry "
            "the routine name where one is present; Routine Name is blank "
            "when the join finds nothing. intent_param and label_params hold "
            "app-defined parameter text and are reported as stored rather "
            "than decoded, since their structure varies by action tag. "
            "valid_state is an undocumented integer reported as stored. Six "
            "of the eight tested extractions held rows here, one or two each, "
            "and each row joined to a routine."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "zap-off",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 2 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 0 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 2 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 1 row",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 2 rows",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 2 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 2 rows",
        },
    },
    "samsungBixbyRoutinesPlaces": {
        "name": "Samsung Bixby Routines - Saved Places",
        "description": (
            "Parses the location_history table of com.samsung.android.app."
            "routines/databases/routine.db, which stores a coordinate pair "
            "with an address, locality and keyword label."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "The table definition pairs latitude and longitude with an "
            "address, locality and keyword, and an update_time. `type` is an "
            "undocumented integer reported as stored. KML output is produced "
            "for rows carrying both coordinates. A row records a place the "
            "app held at acquisition; it is not a record that the device was "
            "at that place, and the update_time is the row's own recorded "
            "time rather than a visit time. location_history was present in "
            "four of the eight tested extractions and held no rows in any of "
            "them, and the artifact reports nothing where the table is "
            "absent, so this artifact is code-present and unexercised: the "
            "column meanings were derived from the table definition rather "
            "than from decoded rows."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": ['html', 'tsv', 'timeline', 'lava', 'kml'],
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 0 rows (table not in this release)",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 0 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 0 rows (table not in this release)",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 0 rows (table not in this release)",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 0 rows (table not in this release)",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 0 rows",
        },
    },
    "samsungBixbyRoutinesServiceLog": {
        "name": "Samsung Bixby Routines - Service Log",
        "description": (
            "Parses the routine_history table of com.samsung.android.app."
            "routines/databases/routine.db, an internal timestamped log "
            "kept by the Routines background service (job scheduling, "
            "metaloader and catalog-update events, widget provider callbacks)."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "This is service telemetry rather than a record of a specific "
            "routine firing. No tested extraction carried a per-routine value "
            "here: the two oldest stored routine_id = -1 and is_running = 1 "
            "on every row, and the six newer ones left routine_id, is_running "
            "and service_status null on every row, with Log Message text "
            "naming internal service events and no user routine. The "
            "routine_id join to the `routine` table is kept for a device that "
            "does record a real id, and Linked Routine Name is blank where "
            "the join finds nothing. Routine Run History is the table that "
            "names a routine against a time; use that artifact for that "
            "question. This table is a rolling buffer, holding 50 rows in the "
            "two oldest tested releases and 300 in the six newer ones, with "
            "the autoincrement counter ahead of the live row count in all "
            "eight, so older rows are trimmed and the window the artifact "
            "covers is set by how much the service has written since, not by "
            "the acquisition period. That window ran from 0.9 to 21.2 days "
            "across the eight. The module reads the database with its "
            "write-ahead log applied, which is the state at acquisition; in "
            "one extraction the main database file read without its log held "
            "6 rows since trimmed and lacked the 3 most recent, so a copy of "
            "the .db alone is a different row set rather than a smaller one."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 300 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 50 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 50 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 300 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 300 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 300 rows",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 300 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 300 rows",
        },
    },
    "samsungBixbyRoutinesPreferences": {
        "name": "Samsung Bixby Routines - App Preferences",
        "description": (
            "Parses the key/value preference table of com.samsung.android."
            "app.routines/databases/routine.db, which holds app-level "
            "settings and state such as first-run and metadata-loading times "
            "and recommendation counters."
        ),
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-27",
        "requirements": "none",
        "category": "Samsung Bixby Routines",
        "notes": (
            (
            (
            "Values are reported as stored (the column is TEXT, so "
            "numeric-looking values are strings). Five keys observed across "
            "the tested extractions to hold epoch-millisecond values "
            "(app_active_device_send_time, init_time, latest_time, "
            "sleep_expired_time, update_noti_time) are decoded into a "
            "Converted Timestamp column; any other key is left blank in that "
            "column rather than converted on a guess. Only init_time appeared "
            "in all eight extractions, so which of the five a report shows "
            "depends on the release. One further key, seen on one extraction "
            "under a composite name ending tip_notify_mode_in_quick_panel, "
            "carried a value in the epoch range and is left unconverted, "
            "since one observation does not establish what it records. "
            "init_time is the earliest time recorded in this table and was "
            "not cross-checked against a package-manager install record, so "
            "it is indicative of install era rather than a confirmed install "
            "time. In one extraction update_noti_time fell 359 ms after the "
            "newest routine_history row, two values written by different code "
            "paths agreeing on when the service last ran. This table is app "
            "configuration rather than user content: it does not carry what "
            "routines existed."
        )
        )
        ),
        "paths": ('*/com.samsung.android.app.routines/databases/routine.db*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.routines vc 480221000 | 44 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.routines vc 312108000 | 15 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.app.routines vc 262506000 | 8 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 17 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.routines vc 460105000 | 19 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.routines vc 420052000 | 17 rows",
            "sharon_a13": "Android 13 | com.samsung.android.app.routines vc 400071000 | 22 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.routines vc 450054000 | 41 rows",
        },
    },
}

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
    null_absent_columns,
)

# Keys in the `preference` table observed across the tested extractions to hold
# epoch-millisecond timestamps. Any other key is reported with a blank Converted
# Timestamp rather than a guessed conversion.
_TIMESTAMP_PREFERENCE_KEYS = {
    "app_active_device_send_time",
    "init_time",
    "latest_time",
    "sleep_expired_time",
    "update_noti_time",
}


def _target_dbs(context):
    """(path, evidence relative path) for each routine.db the glob matched.

    unique_files collapses the duplicate storage views a full file system
    extraction carries for one app directory (data/data, data/user/<n>,
    data_mirror/...), so a database is read once per Android user rather than
    once per spelling. The glob also matches the SQLite sidecars, which are
    read through the database handle and are skipped here.
    """
    targets = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        targets.append((file_found, context.get_relative_path(file_found)))
    return targets


def _collect(context, table, query, data_headers, row_builder):
    """Run one query across every container and return (headers, rows, sources).

    A device with more than one Android user yields more than one container, so
    the rows carry a Source Path column in that case and the returned source
    path names every container rather than whichever one happened to be read
    last.
    """
    targets = [t for t in _target_dbs(context) if does_table_exist_in_db(t[0], table)]
    multiple = len(targets) > 1
    if multiple:
        data_headers = tuple(data_headers) + ('Source Path',)

    data_list = []
    sources = []
    for file_found, rel_path in targets:
        sources.append(rel_path)
        count = 0
        # Columns come and go between app releases, so a query written against a
        # newer store names columns an older one lacks and the whole statement
        # fails with "no such column", which reports zero rows rather than an
        # error. Resolved per container because the releases can differ.
        for row in get_sqlite_db_records(file_found, null_absent_columns(file_found, query)):
            built = row_builder(row)
            data_list.append((built + (rel_path,)) if multiple else built)
            count += 1
        logfunc(f"Samsung Bixby Routines: {count} {table} row(s) in {rel_path}")

    return data_headers, data_list, '\n'.join(sources)


def _ts(value):
    """The stored value as a UTC datetime, or None when it is absent or zero."""
    return convert_unix_ts_to_utc(value) if value else None


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
        'Icon Resource ID (as stored)',
        'Color (as stored)',
    )
    query = '''
    SELECT _id, name, is_running, is_manual_routine, is_favorite_routine,
           is_show_notification, toggle_time, tag, icon, color
    FROM routine
    ORDER BY _id
    '''

    def build(row):
        (routine_id, name, is_running, is_manual, is_favorite,
         is_show_notification, toggle_time, tag, icon, color) = row
        return (routine_id, name, is_running, is_manual, is_favorite,
                is_show_notification, _ts(toggle_time), tag, icon, color)

    return _collect(context, 'routine', query, data_headers, build)


@artifact_processor
def samsungBixbyRoutinesRunHistory(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Routine Name',
        'Routine ID',
        'Running Type (as stored)',
        'Recover Type (as stored)',
        'Invalid Action Instance ID',
        'Unknown Action Instance ID',
    )
    query = '''
    SELECT timestamp, routine_name, routine_id, running_type, recover_type,
           invalid_action_instance_id, unknown_action_instance_id
    FROM routine_running_history
    ORDER BY timestamp
    '''

    def build(row):
        (timestamp, routine_name, routine_id, running_type, recover_type,
         invalid_action, unknown_action) = row
        return (_ts(timestamp), routine_name, routine_id, running_type,
                recover_type, invalid_action, unknown_action)

    return _collect(context, 'routine_running_history', query, data_headers, build)


@artifact_processor
def samsungBixbyRoutinesConditions(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Routine Name',
        'Routine ID',
        'Condition Tag',
        'Package',
        'Is Enabled',
        'Is Negative',
        'Label Params',
        'Intent Params',
        'Bundle Data',
        'Previous Params',
        'Valid State (as stored)',
    )
    query = '''
    SELECT ci.timestamp, r.name, ci.routine_id, ci.condition_tag, ci.package,
           ci.is_enabled, ci.is_negative, ci.label_params, ci.intent_param,
           ci.bundle_data, ci.prev_param, ci.valid_state
    FROM condition_instance ci
    LEFT JOIN routine r ON ci.routine_id = r._id
    ORDER BY ci.routine_id, ci._id
    '''

    def build(row):
        return (_ts(row[0]), row[1] if row[1] else '') + tuple(row[2:])

    return _collect(context, 'condition_instance', query, data_headers, build)


@artifact_processor
def samsungBixbyRoutinesActions(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Routine Name',
        'Routine ID',
        'Action Tag',
        'Package',
        'Is Negative',
        'Label Params',
        'Intent Params',
        'Previous Params',
        'Valid State (as stored)',
    )
    query = '''
    SELECT ai.timestamp, r.name, ai.routine_id, ai.action_tag, ai.package,
           ai.is_negative, ai.label_params, ai.intent_param, ai.prev_param,
           ai.valid_state
    FROM action_instance ai
    LEFT JOIN routine r ON ai.routine_id = r._id
    ORDER BY ai.routine_id, ai._id
    '''

    def build(row):
        return (_ts(row[0]), row[1] if row[1] else '') + tuple(row[2:])

    return _collect(context, 'action_instance', query, data_headers, build)


@artifact_processor
def samsungBixbyRoutinesPlaces(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Keyword',
        'Address',
        'Locality',
        'Latitude',
        'Longitude',
        'Type (as stored)',
    )
    query = '''
    SELECT update_time, keyword, address, locality, latitude, longitude, type
    FROM location_history
    ORDER BY update_time
    '''

    def build(row):
        return (_ts(row[0]),) + tuple(row[1:])

    return _collect(context, 'location_history', query, data_headers, build)


@artifact_processor
def samsungBixbyRoutinesServiceLog(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Routine ID (raw)',
        'Linked Routine Name',
        'Is Running',
        'Service Status (as stored)',
        'Log Message',
    )
    query = '''
    SELECT rh.timestamp, rh.routine_id, r.name, rh.is_running,
           rh.service_status, rh.name
    FROM routine_history rh
    LEFT JOIN routine r ON rh.routine_id = r._id
    ORDER BY rh.timestamp
    '''

    def build(row):
        (timestamp, routine_id, linked_name, is_running,
         service_status, log_message) = row
        return (_ts(timestamp), routine_id, linked_name if linked_name else '',
                is_running, service_status, log_message)

    return _collect(context, 'routine_history', query, data_headers, build)


@artifact_processor
def samsungBixbyRoutinesPreferences(context):
    data_headers = (
        'Key',
        'Value',
        ('Converted Timestamp', 'datetime'),
    )
    query = 'SELECT key, value FROM preference ORDER BY key'

    def build(row):
        key, value = row
        converted = None
        if key in _TIMESTAMP_PREFERENCE_KEYS and value:
            try:
                converted = convert_unix_ts_to_utc(int(value))
            except (TypeError, ValueError):
                converted = None
        return (key, value, converted)

    return _collect(context, 'preference', query, data_headers, build)
