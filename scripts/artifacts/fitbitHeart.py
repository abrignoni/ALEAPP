import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitHeart(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime("DATE_TIME"/1000, 'unixepoch'),
    AVERAGE_HEART_RATE,
    RESTING_HEART_RATE
    FROM HEART_RATE_DAILY_SUMMARY
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Fitbit Heart Rate Summary')
        report.start_artifact_report(report_folder, 'Fitbit Heart Rate Summary')
        report.add_script()
        data_headers = ('Timestamp','Avg. Heart Rate','Resting Heart Rate') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Heart Rate Summary'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Fitbit Heart Rate Summary'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Fitbit Heart Rate Summary data available')
        
    db.close()

    