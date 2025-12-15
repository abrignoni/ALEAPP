__artifacts_v2__ = {
    "wellbeing": {
        "name": "Digital Wellbeing",
        "description": "Parses Digital Wellbeing events",
        "author": "@AlexisBrignoni",
        "version": "0.0.1",
        "date": "2020-02-2",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": "",
        "paths": ('*/com.google.android.apps.wellbeing/databases/app_usage*'),
        "function": "get_wellbeing"
    }
}

import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_wellbeing(files_found, report_folder, seeker, wrap_text):

    data_list = []
    data_list_url = []

    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('app_usage'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            events._id,
            datetime(events.timestamp/1000, 'UNIXEPOCH') as timestamps, 
            packages.package_name,
            case
                when events.type = 1 THEN 'ACTIVITY_RESUMED'
                when events.type = 2 THEN 'ACTIVITY_PAUSED'
                when events.type = 12 THEN 'NOTIFICATION'
                when events.type = 18 THEN 'KEYGUARD_HIDDEN & || Device Unlock'
                when events.type = 19 THEN 'FOREGROUND_SERVICE_START'
                when events.type = 20 THEN 'FOREGROUND_SERVICE_STOP' 
                when events.type = 23 THEN 'ACTIVITY_STOPPED'
                when events.type = 26 THEN 'DEVICE_SHUTDOWN'
                when events.type = 27 THEN 'DEVICE_STARTUP'
                else events.type
            END as eventtype
            FROM
            events INNER JOIN packages ON events.package_id=packages._id 
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    event_ts = row[1]
                    if event_ts is None:
                        pass
                    else:
                        event_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(event_ts),'UTC')
                
                    data_list.append((event_ts, row[2], row[3], file_found))
                    
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            datetime(component_events.timestamp/1000, "UNIXEPOCH") as timestamp,
            component_events._id,
            components.package_id, 
            packages.package_name, 
            components.component_name as website,
            CASE
            when component_events.type=1 THEN 'ACTIVITY_RESUMED'
            when component_events.type=2 THEN 'ACTIVITY_PAUSED'
            else component_events.type
            END as eventType
            FROM component_events
            INNER JOIN components ON component_events.component_id=components._id
            INNER JOIN packages ON components.package_id=packages._id
            ORDER BY timestamp
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    event_ts = row[0]
                    if event_ts is None:
                        pass
                    else:
                        event_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(event_ts),'UTC')
                    data_list_url.append((event_ts, row[1], row[2], row[3], row[4], row[5], file_found))
            db.close()
            
        else:
            continue # Skip all other files
        
    if data_list:
        report = ArtifactHtmlReport('Digital Wellbeing - Events')
        report.start_artifact_report(report_folder, 'Events')
        report.add_script()
        data_headers = ('Timestamp', 'Package ID', 'Event Type', 'Source File')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Digital Wellbeing - Events'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Digital Wellbeing - Events'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Digital Wellbeing - Events data available')
    
    if data_list_url:
        report = ArtifactHtmlReport('Digital Wellbeing - URL Events')
        report.start_artifact_report(report_folder, 'Digital Wellbeing - URL Events')
        report.add_script()
        data_headers = ('Timestamp', 'Event ID', 'Package ID', 'Package Name', 'Website', 'Event', 'Source File')
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Digital Wellbeing - URL Events'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Digital Wellbeing - URL Events'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Digital Wellbeing - URL Events data available')