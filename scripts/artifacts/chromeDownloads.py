import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, does_column_exist_in_db, open_sqlite_db_readonly

def get_chromeDownloads(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History': # skip -journal and other files
            continue
        browser_name = 'Chrome'
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        # check for last_access_time column, an older version of chrome db (32) does not have it
        if does_column_exist_in_db(db, 'downloads', 'last_access_time') == True:
            last_access_time_query = '''
            CASE last_access_time 
                WHEN "0" 
                THEN "" 
                ELSE datetime(last_access_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "Last Access Time"'''
        else:
            last_access_time_query = "'' as last_access_query"

        cursor.execute(f'''
        SELECT 
        CASE start_time  
            WHEN "0" 
            THEN "" 
            ELSE datetime(start_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "Start Time", 
        CASE end_time 
            WHEN "0" 
            THEN "" 
            ELSE datetime(end_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "End Time", 
        {last_access_time_query},
        tab_url, 
        target_path, state, opened, received_bytes, total_bytes
        FROM downloads
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
            data_headers = ('Start Time','End Time','Last Access Time','URL','Target Path','State','Opened?','Received Bytes','Total Bytes')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Downloads'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} download data available')
        
        db.close()
