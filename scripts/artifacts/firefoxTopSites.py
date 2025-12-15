import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefoxTopSites(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'top_sites': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        title AS Title,
        url AS URL,
        CASE is_default
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END as IsDefault
        FROM top_sites
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Top Sites')
            report.start_artifact_report(report_folder, 'Firefox - Top Sites')
            report.add_script()
            data_headers = ('Created Timestamp','Title','URL','Is Default') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Top Sites'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Top Sites'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Top Sites data available')
        
        db.close()
    
__artifacts__ = {
        "FirefoxTopSites": (
                "Firefox",
                ('*/org.mozilla.firefox/databases/top_sites*'),
                get_firefoxTopSites)
}