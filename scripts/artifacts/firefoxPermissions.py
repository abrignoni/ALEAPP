import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefoxPermissions(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'permissions.sqlite': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(modificationTime/1000,'unixepoch') AS ModDate,
        origin AS Origin,
        type AS PermType,
        CASE permission
            WHEN 1 THEN 'Allow'
            WHEN 2 THEN 'Block'
        END AS PermState,
        CASE expireTime
            WHEN 0 THEN ''
            else datetime(expireTime/1000,'unixepoch')
        END AS ExpireDate
        FROM moz_perms
        ORDER BY ModDate ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Permissions')
            report.start_artifact_report(report_folder, 'Firefox - Permissions')
            report.add_script()
            data_headers = ('Modification Timestamp','Origin Site','Permission Type','Status','Expiration Timestamp') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Permissions'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Permissions'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Permissions data available')
        
        db.close()
    
__artifacts__ = {
        "FirefoxPermissions": (
                "Firefox",
                ('*/org.mozilla.firefox/files/mozilla/*.default/permissions.sqlite*'),
                get_firefoxPermissions)
}