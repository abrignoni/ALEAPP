import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitWalk(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime("TIMESTAMP"/1000, 'unixepoch'),
    STEPS_COUNT,
    METS_COUNT,
    datetime("TIME_CREATED"/1000, 'unixepoch'),
    datetime("TIME_UPDATED"/1000, 'unixepoch')
    FROM PEDOMETER_MINUTE_DATA
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Fitbit Steps')
        report.start_artifact_report(report_folder, 'Fitbit Steps')
        report.add_script()
        data_headers = ('Timestamp','Steps Count','Mets Count','Time Created','Time Updated') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Steps'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Fitbit Steps'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Fitbit Steps data available')
        
    db.close()

__artifacts__ = {
        "FitbitWalk": (
                "Fitbit",
                ('*/com.fitbit.FitbitMobile/databases/mobile_track_db*'),
                get_fitbitWalk)
}