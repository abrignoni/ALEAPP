import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefoxCookies(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'cookies.sqlite': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(lastAccessed/1000000,'unixepoch') AS LastAccessedDate,
        datetime(creationTime/1000000,'unixepoch') AS CreationDate,
        host AS Host,
        name AS Name,
        value AS Value,
        datetime(expiry,'unixepoch') AS ExpirationDate,
        path AS Path
        from moz_cookies
        ORDER BY lastAccessedDate ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Cookies')
            report.start_artifact_report(report_folder, 'Firefox - Cookies')
            report.add_script()
            data_headers = ('Last Accessed Timestamp','Created Timestamp','Host','Name','Value','Expiration Timestamp','Path') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Cookies'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Cookies'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Cookies data available')
        
        db.close()
    
__artifacts__ = {
        "FirefoxCookies": (
                "Firefox",
                ('*/org.mozilla.firefox/files/mozilla/*.default/cookies.sqlite*'),
                get_firefoxCookies)
}