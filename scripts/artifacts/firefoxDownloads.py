import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefoxDownloads(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'mozac_downloads_database': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        file_name AS FileName,
        url AS URL,
        content_type AS MimeType,
        content_length AS FileSize,
        CASE status
            WHEN 3 THEN 'Paused'
            WHEN 4 THEN 'Canceled'
            WHEN 5 THEN 'Failed'
            WHEN 6 THEN 'Finished'
        END AS Status,
        destination_directory AS DestDir
        FROM downloads
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Downloads')
            report.start_artifact_report(report_folder, 'Firefox - Downloads')
            report.add_script()
            data_headers = ('Created Timestamp','File Name','URL','MIME Type','File Size (Bytes)','Status','Destination Directory') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Downloads'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Downloads data available')
        
        db.close()
    
__artifacts__ = {
        "FirefoxDownloads": (
                "Firefox",
                ('*/org.mozilla.firefox/databases/mozac_downloads_database*'),
                get_firefoxDownloads)
}