import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows, get_next_unused_name

def get_chromeDownloads(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History': # skip -journal and other files
            continue
        browser_name = 'Chrome'
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

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
                "" 
            ELSE
                datetime(start_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "Start Time", 
        CASE
            end_time 
            WHEN
                "0" 
            THEN
                "" 
            ELSE
                datetime(end_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "End Time", 
        CASE
            last_access_time 
            WHEN
                "0" 
            THEN
                "" 
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
            report = ArtifactHtmlReport(f'{browser_name} Downloads')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Downloads.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('URL','Start Time','End Time','Last Access Time','Target Path','State','Opened?','Received Bytes','Total Bytes')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
        else:
            logfunc(f'No {browser_name} download data available')
        
        db.close()
