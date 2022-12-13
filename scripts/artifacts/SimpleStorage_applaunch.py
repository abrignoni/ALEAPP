# Module Description: Parses SimpleStorage for application launch
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2022-12-13
# Artifact version: 0.0.1
# Much thanks to Josh Hickman (@josh_hickman1) for the research, testing and query

import os
import sqlite3
import textwrap

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_SimpleStorage_applaunch(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if not os.path.basename(file_name) == 'SimpleStorage': # skip -journal and other files
            continue
          
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
            description = ''
            report = ArtifactHtmlReport('SimpleStorage - App Launch')
            report.start_artifact_report(report_folder, 'SimpleStorage - App Launch')
            report.add_script()
            data_headers = ('App Launched Timestamp','App Name','Launched From')
            data_list = []
            data_list_stripped = []
            for row in all_rows:
                
                data_list.append((row[0],row[1],row[2]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'SimpleStorage - App Launch'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'SimpleStorage - App Launch'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('SimpleStorage - App Launch data available') 

        db.close()

__artifacts__ = {
        "SimpleStorage_applaunch": (
                "Android System Intelligence",
                ('*/com.google.android.as/databases/SimpleStorage*'),
                get_SimpleStorage_applaunch)
}
