import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_wellbeingURLs(files_found, report_folder, seeker):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('app_usage'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
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
            report = ArtifactHtmlReport('Wellbeing URL events')
            report.start_artifact_report(report_folder, 'URL Events')
            report.add_script()
            data_headers = ('Timestamp', 'Event ID', 'Package ID', 'Package Name', 'Website', 'Event')
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'wellbeing - URL events'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Wellbeing - URL Events'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Wellbeing URL event data available')
        
        db.close()
        return