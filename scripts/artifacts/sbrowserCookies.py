import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_sbrowserCookies(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    host_key,
    name,
    value,
    CASE
        last_access_utc 
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(last_access_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    END AS "last_access_utc", 
    CASE
        creation_utc 
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(creation_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    END AS "creation_utc", 
    CASE
        expires_utc 
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(expires_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    END AS "expires_utc", 
    path
    FROM
    cookies
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Browser Cookies')
        report.start_artifact_report(report_folder, 'Browser Cookies')
        report.add_script()
        data_headers = ('Host','Name','Value','Last Access Date','Created Date','Expiration Date','Path' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],(textwrap.fill(row[2], width=50)),row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Browser cookies data available')
    
    db.close()
    return

