import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefoxRecentlyClosedTabs(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'recently_closed_tabs': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        title as Title,
        url as URL
        FROM recently_closed_tabs
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Recently Closed Tabs')
            report.start_artifact_report(report_folder, 'Firefox - Recently Closed Tabs')
            report.add_script()
            data_headers = ('Timestamp','Title','URL')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Recently Closed Tabs'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Recently Closed Tabs'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Recently Closed Tabs data available')
        
        db.close()

__artifacts__ = {
        "FirefoxRecentlyClosedTabs": (
                "Firefox",
                ('*/org.mozilla.firefox/databases/recently_closed_tabs*'),
                get_firefoxRecentlyClosedTabs)
}