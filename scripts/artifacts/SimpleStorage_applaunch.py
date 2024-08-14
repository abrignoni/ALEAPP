__artifacts_v2__ = {
    "SimpleStorage_applaunch": {
        "name": "SimpleStorage",
        "description": "Parses SimpleStorage for application launch",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2022-12-13",
        "requirements": "none",
        "category": "Android System Intelligence",
        "notes": "Much thanks to Josh Hickman (@josh_hickman1) for the research, testing and query",
        "paths": ('*/com.google.android.as/databases/SimpleStorage*',),
        "function": "get_SimpleStorage_applaunch"
    }
}

import os
import sqlite3
import textwrap

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_SimpleStorage_applaunch(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_name.endswith('SimpleStorage'):
          
            db = open_sqlite_db_readonly(file_name)
            cursor = db.cursor()
            cursor.execute('''
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
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    time_launched = row[0]
                    if time_launched is None:
                        pass
                    else:
                        time_launched = convert_utc_human_to_timezone(convert_ts_human_to_utc(time_launched),time_offset)
                    data_list.append((time_launched,row[1],row[2], file_found))
            db.close()
        
        else:
            continue # Skip all other files
    
    if data_list:
        description = ''
        report = ArtifactHtmlReport('SimpleStorage - App Launch')
        report.start_artifact_report(report_folder, 'SimpleStorage - App Launch')
        report.add_script()
        data_headers = ('App Launched Timestamp','App Name','Launched From', 'Source File')
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'SimpleStorage - App Launch'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'SimpleStorage - App Launch'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('SimpleStorage - App Launch data available')