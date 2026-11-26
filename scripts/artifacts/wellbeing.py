__artifacts_v2__ = {
    "get_wellbeing": {
        "name": "Digital Wellbeing - Events",
        "description": "Parses Digital Wellbeing events",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-02-02",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Device Activity",
        "notes": (
            "Event Type shows the UsageEvents.Event constant whose value matches the stored numeric 'type' field; the names shown are those for values 1, 2, 12, 18, 19, 20, 23, 26 and 27; any other value is shown as stored, whether or not a constant exists for it. Constant names are reported as defined by Android; a keyguard or screen-state constant does not by itself establish a user action. Reference: Google, 'UsageEvents.Event', https://developer.android.com/reference/android/app/usage/UsageEvents.Event, for all names except NOTIFICATION_INTERRUPTION (12), which is a hidden constant defined in AOSP UsageEvents.java, https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/core/java/android/app/usage/UsageEvents.java#200. That the Wellbeing events table stores these values is not documented in either source. Every app_usage database found is read once. Copies of one store under another storage path (data/data, data/user/0, data_mirror) are read as one store. A rollback snapshot that is byte identical to the live store is not read again. The rows of all stores are reported together. A store that cannot be opened or read is named in the log and gives no rows, and the other stores are still read. Android User is the user the store's path denotes: 0 for data/data and userdata/data, and the number in the path for data/user/<n>, data/user_de/<n>, the userdata forms of both, and data_mirror. It is blank for any other path, which includes a rollback snapshot under misc_ce or misc_de. On the images run only 0 and 10 occur. No column other than Android User separates two stores. Of the 39 images run, 19 held a store for user 10 as well as user 0. On 3 of them the user 10 store held no events. The other 16 gave 6,691 user 10 rows, summed per image. 14 of those images are successive captures of one emulator and repeat the same records, so the sum counts some records more than once. Timestamp is events.timestamp read as Unix milliseconds, UTC. That reading is not documented in the sources cited here. A stored value of 0 is shown blank."
        ),
        "paths": ('*/com.google.android.apps.wellbeing/databases/app_usage*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.wellbeing vc 839927 | 4556 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.wellbeing vc 762847 | 18070 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.wellbeing vc 550467 | 44715 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.wellbeing vc 495937 | 15960 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.wellbeing vc 668567 | 1723 rows",
        },
    },
    "get_wellbeing_url": {
        "name": "Digital Wellbeing - Component Events",
        "description": "Parses Digital Wellbeing events recorded against a package component",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-02-02",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Device Activity",
        "notes": (
            "Component Name is the components.component_name value stored for the event. Event shows ACTIVITY_RESUMED for a stored type of 1 and ACTIVITY_PAUSED for 2, the UsageEvents.Event constants with those values; any other value is shown as stored. None of the listed images produced rows, so this artifact is not exercised by the listed data. Constant names are reported as defined by Android. Reference: Google, 'UsageEvents.Event', https://developer.android.com/reference/android/app/usage/UsageEvents.Event. That the Wellbeing component_events table stores these values is not documented in that source. Every app_usage database found that has a component_events table is read once. Copies of one store under another storage path are read as one store. The rows of all stores are reported together. A store that cannot be opened or read is named in the log and gives no rows, and the other stores are still read. On the images run no store gave rows, so reading more than one store is not exercised here. Android User is the user the store's path denotes: 0 for data/data and userdata/data, and the number in the path for data/user/<n>, data/user_de/<n>, the userdata forms of both, and data_mirror. It is blank for any other path, which includes a rollback snapshot under misc_ce or misc_de. No column other than Android User separates two stores. Timestamp is component_events.timestamp read as Unix milliseconds, UTC. That reading is not documented in the sources cited here. A stored value of 0 is shown blank."
        ),
        "paths": ('*/com.google.android.apps.wellbeing/databases/app_usage*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.wellbeing vc 839927 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.wellbeing vc 762847 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.wellbeing vc 550467 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.wellbeing vc 495937 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.wellbeing vc 668567 | 0 rows",
        },
    }
}

import datetime
import sqlite3

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _app_usage_dbs(context):
    """Each app_usage database, one per Android user, with duplicate storage views collapsed."""
    return [str(path) for path in unique_files(context) if str(path).endswith('app_usage')]


def _rows(source_path, sql):
    """The query's rows from one store, or None when the store cannot be opened or read. The failure
    is logged and the other stores are still read."""
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        logfunc(f'Digital Wellbeing: could not open {source_path}')
        return None
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error as exc:
        logfunc(f'Digital Wellbeing: could not read {source_path}: {exc}')
        return None
    finally:
        db.close()


@artifact_processor
def get_wellbeing(context):
    data_list = []
    source_paths = []
    for source_path in _app_usage_dbs(context):
        user = android_user(context.get_relative_path(source_path))
        all_rows = _rows(source_path, '''
            SELECT
            events.timestamp,
            packages.package_name,
            case
                when events.type = 1 THEN 'ACTIVITY_RESUMED'
                when events.type = 2 THEN 'ACTIVITY_PAUSED'
                when events.type = 12 THEN 'NOTIFICATION_INTERRUPTION'
                when events.type = 18 THEN 'KEYGUARD_HIDDEN'
                when events.type = 19 THEN 'FOREGROUND_SERVICE_START'
                when events.type = 20 THEN 'FOREGROUND_SERVICE_STOP'
                when events.type = 23 THEN 'ACTIVITY_STOPPED'
                when events.type = 26 THEN 'DEVICE_SHUTDOWN'
                when events.type = 27 THEN 'DEVICE_STARTUP'
                else events.type
            END as eventtype
            FROM events INNER JOIN packages ON events.package_id=packages._id
        ''')
        if all_rows is None:
            continue
        source_paths.append(source_path)
        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], user))

    data_headers = (('Timestamp', 'datetime'), 'Package Name', 'Event Type', 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_wellbeing_url(context):
    data_list = []
    source_paths = []
    # Older app_usage generations have no component_events table
    # (community report, PR #633).
    for source_path in _app_usage_dbs(context):
        if not does_table_exist_in_db(source_path, 'component_events'):
            continue
        user = android_user(context.get_relative_path(source_path))
        all_rows = _rows(source_path, '''
            SELECT
            component_events.timestamp,
            component_events._id,
            components.package_id,
            packages.package_name,
            components.component_name,
            CASE
                when component_events.type=1 THEN 'ACTIVITY_RESUMED'
                when component_events.type=2 THEN 'ACTIVITY_PAUSED'
                else component_events.type
            END as eventType
            FROM component_events
            INNER JOIN components ON component_events.component_id=components._id
            INNER JOIN packages ON components.package_id=packages._id
            ORDER BY component_events.timestamp
        ''')
        if all_rows is None:
            continue
        source_paths.append(source_path)
        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], user))

    data_headers = (
        ('Timestamp', 'datetime'), 'Event ID', 'Package ID', 'Package Name', 'Component Name', 'Event',
        'Android User')
    return data_headers, data_list, '\n'.join(source_paths)
