__artifacts_v2__ = {
    "get_wellbeing": {
        "name": "Digital Wellbeing - Events",
        "description": "Parses Digital Wellbeing events",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-02-02",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": (
            "Event Type shows the UsageEvents.Event constant whose value matches the stored "
            "numeric 'type' field; a value with no matching constant is shown as stored. "
            "Constant names are reported as defined by AOSP; a keyguard or screen-state "
            "constant does not by itself establish a user action. "
            "Reference: Google, 'UsageEvents.Event constants', "
            "https://developer.android.com/reference/android/app/usage/UsageEvents.Event"
        ),
        "paths": ('*/com.google.android.apps.wellbeing/databases/app_usage*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.wellbeing vc 839927 | 4556 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.wellbeing vc 762847 | 18070 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.wellbeing vc 550467 | 44715 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.wellbeing vc 495937 | 11663 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.wellbeing vc 668567 | 1723 rows",
        },
    },
    "get_wellbeing_url": {
        "name": "Digital Wellbeing - Component Events",
        "description": "Parses Digital Wellbeing events recorded against a package component",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-02-02",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": (
            "Component Name is the components.component_name value stored for the event. "
            "Event Type shows the UsageEvents.Event constant whose value matches the stored "
            "numeric 'type' field; a value with no matching constant is shown as stored. "
            "Constant names are reported as defined by AOSP; a keyguard or screen-state "
            "constant does not by itself establish a user action. "
            "Reference: Google, 'UsageEvents.Event constants', "
            "https://developer.android.com/reference/android/app/usage/UsageEvents.Event"
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

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _app_usage_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('app_usage'):
            return file_found
    return ''


@artifact_processor
def get_wellbeing(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _app_usage_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
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
        all_rows = cursor.fetchall()
        db.close()
        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2]))

    data_headers = (('Timestamp', 'datetime'), 'Package Name', 'Event Type')
    return data_headers, data_list, source_path


@artifact_processor
def get_wellbeing_url(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _app_usage_db(files_found)
    # Older app_usage generations have no component_events table
    # (community report, PR #633).
    if source_path and does_table_exist_in_db(source_path, 'component_events'):
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
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
        all_rows = cursor.fetchall()
        db.close()
        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5]))

    data_headers = (
        ('Timestamp', 'datetime'), 'Event ID', 'Package ID', 'Package Name', 'Component Name', 'Event')
    return data_headers, data_list, source_path
