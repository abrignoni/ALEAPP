import sqlite3
import textwrap
import binascii

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_chromeLoginData(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    username_value,
    password_value,
    CASE
            date_created 
            WHEN
                "0" 
            THEN
                "0" 
            ELSE
                datetime(date_created / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "date_created", 
    origin_url,
    blacklisted_by_user
    FROM logins
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Chrome Login Data')
        report.start_artifact_report(report_folder, 'Login Data')
        report.add_script()
        data_headers = ('Username','Password','Created Time','Origin URL','Blacklisted by User' ) 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],(row[1].decode("utf-8", 'replace')),row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Chrome Login Data available')
    
    db.close()
    return

