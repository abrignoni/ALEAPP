__artifacts_v2__ = {
    "SimpleStorage_applaunch": {
        "name": "SimpleStorage - App Launch",
        "description": "Parses SimpleStorage for application launch",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "creation_date": "2022-12-13",
        "last_updated": "2025-09-12",
        "requirements": "none",
        "category": "Android System Intelligence",
        "notes": "Much thanks to Josh Hickman (@josh_hickman1) for the research, testing and query",
        "paths": ('*/com.google.android.as/databases/SimpleStorage*'),
        "output_types": "standard",
        "artifact_icon": "loader",
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_ts_human_to_utc, convert_utc_human_to_timezone

@artifact_processor
def SimpleStorage_applaunch(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    source_path = get_file_path(files_found, "SimpleStorage")
    
    query = '''
    SELECT DISTINCT
    datetime(EchoAppLaunchMetricsEvents.timestampMillis/1000,'unixepoch') AS "Time App Launched",
    EchoAppLaunchMetricsEvents.packageName AS "App",
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
        data_list.append((time_launched,record[1],record[2], source_path))
 
    data_headers = (('App Launched Timestamp','datetime'),'App Name','Launched From', 'Source File')
    return data_headers, data_list, 'See source file(s) below'