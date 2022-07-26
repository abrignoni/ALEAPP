import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitSleep(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime("DATE_TIME"/1000, 'unixepoch'),
    SECONDS,
    LEVEL_STRING,
    LOG_ID
    FROM SLEEP_LEVEL_DATA
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Fitbit Sleep Detail')
        report.start_artifact_report(report_folder, 'Fitbit Sleep Detail')
        report.add_script()
        data_headers = ('Timestamp','Seconds','Level','Log ID') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Sleep Detail'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Fitbit Sleep Detail'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Fitbit Sleep data available')
    
    
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime("DATE_OF_SLEEP"/1000, 'unixepoch'),
    datetime("START_TIME"/1000, 'unixepoch'),
    SYNC_STATUS_STRING,
    DURATION,
    DURATION/60000,
    MINUTES_AFTER_WAKEUP,
    MINUTES_ASLEEP,
    MINUTES_AWAKE,
    MINUTES_TO_FALL_ASLEEP,
    LOG_ID
    FROM
    SLEEP_LOG
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Fitbit Sleep Summary')
        report.start_artifact_report(report_folder, 'Fitbit Sleep Summary')
        report.add_script()
        data_headers = ('Timestamp','Start Time','Sync Status','Duration in Milliseconds','Duration in Minutes', 'Minutes After Wakeup', 'Minutes Asleep', 'Minutes Awake', 'Minutes to Fall Asleep', 'Log ID') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Sleep Summary'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Fitbit Sleep Summary data available')
        
    db.close()

__artifacts__ = {
        "fitbitSleep": (
                "Fitbit",
                ('*/data/data/com.fitbit.FitbitMobile/databases/sleep*'),
                get_fitbitSleep)
}