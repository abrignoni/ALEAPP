import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_wellbeing(files_found, report_folder, seeker):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('app_usage'):
            continue # Skip all other files
        
        db = sqlite3.connect(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT 
                events._id, 
                datetime(events.timestamp /1000, 'UNIXEPOCH') as timestamps, 
                packages.package_name,
                events.type,
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
            report = ArtifactHtmlReport('Wellbeing events')
            report.start_artifact_report(report_folder, 'Events')
            report.add_script()
            data_headers = ('Timestamp', 'Package ID', 'Event Type')
            data_list = []
            for row in all_rows:
                data_list.append((row[1], row[2], row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'wellbeing - events'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc('No Wellbeing event data available')
        
        db.close()
        return