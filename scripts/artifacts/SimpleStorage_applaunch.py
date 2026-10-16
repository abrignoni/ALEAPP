__artifacts_v2__ = {
    "SimpleStorage_applaunch": {
        "name": "SimpleStorage - App Launch",
        "description": "Parses the EchoAppLaunchMetricsEvents table of the SimpleStorage database (com.google.android.as): timestamp, package name and launch location id",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2022-12-13",
        "last_update_date": "2026-10-06",
        "last_updated": "2025-09-12",
        "requirements": "none",
        "category": "Android System Intelligence",
        "notes": "The query and the Launched From names for launchLocationId values 1, 2, 4, 7, 8, "
                 "12 and 1000 come from Josh Hickman's (@josh_hickman1) research and testing. No "
                 "published reference for them is cited here. Any other value is shown as stored. "
                 "Every selected source row is retained, including repeated events. Raw Timestamp "
                 "Millis and Launch Location ID preserve the source values beside the converted "
                 "timestamp and credited label; the label meanings remain unverified here. Other "
                 "sample counts predate duplicate retention and have not been remeasured.",
        "paths": ('*/com.google.android.as/databases/SimpleStorage*'),
        "output_types": "standard",
        "artifact_icon": "loader",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.as vc 14926349 | 30 rows",
            "pixel7a_a14": "Android 14 | com.google.android.as vc 10790541 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.as vc 8828817 | 38 rows",
            "userb2_a13": "Android 13 | com.google.android.as vc 8997612 | 0 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_ts_human_to_utc, convert_utc_human_to_timezone
from scripts.context import Context

@artifact_processor
def SimpleStorage_applaunch(context):
    files_found = context.get_files_found()
    data_list = []
    
    source_path = get_file_path(files_found, "SimpleStorage")
    
    query = '''
    SELECT
    datetime(EchoAppLaunchMetricsEvents.timestampMillis/1000,'unixepoch') AS "Time App Launched",
    EchoAppLaunchMetricsEvents.timestampMillis,
    EchoAppLaunchMetricsEvents.packageName AS "App",
    EchoAppLaunchMetricsEvents.launchLocationId,
    CASE
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=1 THEN "Home Screen"
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=2 THEN "Suggested Apps (Home Screen)"
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=4 THEN "App Drawer"
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=7 THEN "Suggested Apps (App Drawer)"
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=8 THEN "Search (Top of App Drawer/GSB)"
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=12 THEN "Recent Apps/Multi-Tasking Menu"
        WHEN EchoAppLaunchMetricsEvents.launchLocationId=1000 THEN "Notification"
        ELSE EchoAppLaunchMetricsEvents.launchLocationId
    END AS "Launched From"
    FROM EchoAppLaunchMetricsEvents
    '''
    
    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        time_launched = record[0]
        if time_launched is None:
            pass
        else:
            time_launched = convert_utc_human_to_timezone(convert_ts_human_to_utc(time_launched),'UTC')
        data_list.append((time_launched,record[1],record[2],record[3],record[4], Context.get_relative_path(source_path)))
 
    data_headers = (('App Launched Timestamp','datetime'),'Raw Timestamp Millis','App Name',
                    'Launch Location ID (as stored)','Launched From', 'Source File')
    return data_headers, data_list, source_path
