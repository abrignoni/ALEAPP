import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_sbrowserDownloads(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    tab_url,
    CASE
        start_time  
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(start_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    END AS "Start Time", 
    CASE
        end_time 
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(end_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    END AS "End Time", 
    CASE
        last_access_time 
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(last_access_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    END AS "Last Access Time", 
    target_path,
    state,
    opened,
    received_bytes,
    total_bytes
    FROM
    downloads
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Browser Downloads')
        report.start_artifact_report(report_folder, 'Browser Downloads')
        report.add_script()
        data_headers = ('URL','Start Time','End Time','Last Access Time','Target Path','State','Opened?','Received Bytes','Total Bytes' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Browser download data available')
    
    db.close()
    return

