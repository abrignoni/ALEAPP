__artifacts_v2__ = {
    "samsung_wellbeing": {
        "name": "Samsung Digital Wellbeing",
        "description": "Parses Samsung Digital Wellbeing app usage events (timestamp, event ID, package and event type) from dwbCommon.db.",
        "author": "@abrignoni, @Adam-Hachem",
        "creation_date": "2020-05-21",
        "last_update_date": "2026-10-15",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": (
            "Event-type labels are taken from the AOSP UsageEvents.Event constant names "
            "(reference: AOSP, UsageEvents.java at tag android-14.0.0_r1, "
            "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/core/java/android/app/usage/UsageEvents.java#104) "
            "and applied to the stored codes. The labels for codes 1 and 2 each show two constant "
            "names, which that file defines with the same value. "
            "Samsung's implementation is not documented and its codes are not verified to match "
            "those constants, so the labels are unverified. An event type with no matching label "
            "is shown as stored. Package Name is read from the pkgName column of usageEvents where "
            "the database has one, and otherwise joined from foundPackages on pkgId. The pkgName "
            "column was described in a report from @Adam-Hachem of a Samsung Android 16 "
            "extraction that is not in the corpus; no database with it has been examined here. No registered image has "
            "it, so that path was run only against a copy of the anne_a15 (Android 15) database "
            "with pkgId renamed to pkgName and filled with the package names from foundPackages. "
            "An event whose package id has no row in "
            "foundPackages is reported with a blank Package Name; no event on the five tested "
            "images was in that state. A database present under several storage paths "
            "(data/data, data/user/0, data_mirror) is read once. "
            "A label names a recorded transition and does not by itself establish a user "
            "action."
        ),
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.forest | 2410 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.forest | 11382 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.forest | 2307 rows",
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

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_unix_ts_to_utc, get_sqlite_db_records, get_file_path, logfunc
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def samsung_wellbeing(context):
    data_list = []
    source_paths = []
    # unique_files collapses the data/data, data/user/0 and data_mirror views of one
    # database, which otherwise report every event once per view.
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('dwbCommon.db'):
            continue  # Skip all other files

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        cursor = db.cursor()
        columns = {row[1] for row in cursor.execute('PRAGMA table_info(usageEvents)')}
        if 'pkgName' in columns:
            # A user report describes a build that stores the package name on the event row.
            package_column = 'usageEvents.pkgName'
            package_join = ''
        elif 'pkgId' in columns:
            package_column = 'foundPackages.name'
            package_join = 'LEFT JOIN foundPackages ON usageEvents.pkgId=foundPackages.pkgId'
        else:
            logfunc(f'samsung_wellbeing: usageEvents has neither pkgName nor pkgId in {file_found}')
            db.close()
            continue
        # event types pulled from:
        # https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/core/java/android/app/usage/UsageEvents.java#104
        cursor.execute(f'''
        SELECT
        usageEvents.timeStamp,
        usageEvents.eventId,
        {package_column},
        usageEvents.eventType,
        CASE
        when usageEvents.eventType=1 THEN 'ACTIVITY_RESUMED / MOVE_TO_FOREGROUND'
        when usageEvents.eventType=2 THEN 'ACTIVITY_PAUSED / MOVE_TO_BACKGROUND'
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
        when usageEvents.eventType=19 THEN 'FOREGROUND_SERVICE_START'
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
        {package_join}
        ''')
        all_rows = cursor.fetchall()
        db.close()
        source_paths.append(file_found)

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4]))

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Event Type', 'Event Type Description')
    return data_headers, data_list, '\n'.join(source_paths)

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