import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_scontextLog(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    CASE WHEN timestamp>0 THEN datetime(timestamp /1000, 'UNIXEPOCH')
         ELSE ""
    END as date1,
    time_zone,
    app_id,
    app_sub_id,
    CASE WHEN starttime>0 THEN datetime(starttime /1000, 'UNIXEPOCH')
         ELSE ""
    END as date2,
    CASE WHEN stoptime>0 THEN datetime(stoptime /1000, 'UNIXEPOCH')
         ELSE ""
    END as date3,
    duration,
    duration/1000 as duraton_in_secs
    from use_app
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Context Log')
        report.start_artifact_report(report_folder, 'Samsung Context Log')
        report.add_script()
        data_headers = ('Timestamp','Timezone', 'App ID', 'APP Sub ID', 'Start Time', 'Stop Time', 'Duration', 'Duration in Secs')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'samsung contextlog'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Samsung Context Log data available')
    
    db.close()
    return