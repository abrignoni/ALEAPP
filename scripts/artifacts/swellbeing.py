__artifacts_v2__ = {
    "samsung_wellbeing": {
        "name": "Samsung Digital Wellbeing",
        "description": "Parses Samsung Digital Wellbeing app usage events (timestamp, event ID, package and event type) from dwbCommon.db.",
        "author": "@abrignoni",
        "creation_date": "2020-05-21",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": (
            "Event-type labels were established through testing against Samsung Digital "
            "Wellbeing data; Samsung's implementation is not documented and its codes are "
            "not verified to match the AOSP UsageEvents.Event constants used by the "
            "usagestats artifact. An event type with no matching label is shown as stored. "
            "A label names a recorded transition and does not by itself establish a user "
            "action."
        ),
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.forest | 2410 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.forest | 11382 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.forest | 6921 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.forest | 554 rows",
            "sharon_a14": "Android 14 | com.samsung.android.forest vc 510200008 | 3187 rows",
        },
    },
    "samsung_wellbeing_timezone": {
        "name": "Samsung Digital Wellbeing - Timezone Changes",
        "description": "Parses Samsung Digital Wellbeing timezone changes from dwbCommon.db.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": (),
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "galaxys10_a10": "1 row",
            "sharon_a14": "1 row",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_unix_ts_to_utc, get_sqlite_db_records, get_file_path


@artifact_processor
def samsung_wellbeing(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('dwbCommon.db'):
            continue  # Skip all other files

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        # event types pulled from:
        # https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/app/usage/UsageEvents.java
        cursor.execute('''
        SELECT
        usageEvents.timeStamp,
        usageEvents.eventId,
        foundPackages.name,
        usageEvents.eventType,
        CASE
        when usageEvents.eventType=1 THEN 'ACTIVITY_RESUMED / MOVE_TO_FOREGROUND'
        when usageEvents.eventType=2 THEN 'ACTIVITY_PAUSED / MOVE_TO_BACKGROUD'
		when usageEvents.eventType=3 THEN 'END_OF_DAY'
		when usageEvents.eventType=4 THEN 'CONTINUE_PREVIOUS_DAY'
        when usageEvents.eventType=5 THEN 'CONFIGURATION_CHANGE'
		when usageEvents.eventType=6 THEN 'SYSTEM_INTERACTION'
        when usageEvents.eventType=7 THEN 'USER_INTERACTION'
		when usageEvents.eventType=8 THEN 'SHORTCUT_INVOCATION'
		when usageEvents.eventType=9 THEN 'CHOOSER_ACTION'
        when usageEvents.eventType=10 THEN 'NOTIFICATION_SEEN'
        when usageEvents.eventType=11 THEN 'STANDBY_BUCKET_CHANGED'
        when usageEvents.eventType=12 THEN 'NOTIFICATION_INTERRUPTION'
		when usageEvents.eventType=13 THEN 'SLICE_PINNED_PRIV'
		when usageEvents.eventType=14 THEN 'SLICE_PINNED'
        when usageEvents.eventType=15 THEN 'SCREEN_INTERACTIVE'
        when usageEvents.eventType=16 THEN 'SCREEN_NON_INTERACTIVE'
        when usageEvents.eventType=17 THEN 'KEYGUARD_SHOWN'
        when usageEvents.eventType=18 THEN 'KEYGUARD_HIDDEN'
        when usageEvents.eventType=19 THEN 'FOREGROUND_SERVICE START'
        when usageEvents.eventType=20 THEN 'FOREGROUND_SERVICE_STOP'
		when usageEvents.eventType=21 THEN 'CONTINUING_FOREGROUND_SERVICE'
		when usageEvents.eventType=22 THEN 'ROLLOVER_FOREGROUND_SERVICE'
        when usageEvents.eventType=23 THEN 'ACTIVITY_STOPPED'
		when usageEvents.eventType=24 THEN 'ACTIVITY_DESTROYED'
		when usageEvents.eventType=25 THEN 'FLUSH_TO_DISK'
        when usageEvents.eventType=26 THEN 'DEVICE_SHUTDOWN'
        when usageEvents.eventType=27 THEN 'DEVICE_STARTUP'
        when usageEvents.eventType=28 THEN 'USER_UNLOCKED'
		when usageEvents.eventType=29 THEN 'USER_STOPPED'
		when usageEvents.eventType=30 THEN 'LOCUS_ID_SET'
		when usageEvents.eventType=31 THEN 'APP_COMPONENT_USED'
        else usageEvents.eventType
        END as eventTypeDescription
        FROM usageEvents
        INNER JOIN foundPackages ON usageEvents.pkgId=foundPackages.pkgId
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4]))

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Event Type', 'Event Type Description')
    return data_headers, data_list, source_path

@artifact_processor
def samsung_wellbeing_timezone(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = get_file_path(files_found, "dwbCommon.db")
    
    query  = '''
    SELECT
    timeStamp,
    Value
    from Logging
    where key like '%UsageDataManager::timeZoneChanged()%'
    '''
    
    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        time = convert_unix_ts_to_utc(record[0])
        pre_timezone = record[1].split(', ')[0].replace('prevTimezone( ','')[:-1]
        new_timezone = record[1].split(', ')[1].replace('newTimezone( ','')[:-1]
        
        data_list.append((time, pre_timezone, new_timezone))
                            
    data_headers = (('Timestamp', 'datetime'),'Previous Timezone','New Timezone')
    return data_headers, data_list, source_path