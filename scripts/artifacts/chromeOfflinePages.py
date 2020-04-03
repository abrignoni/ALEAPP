import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_chromeOfflinePages(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(creation_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch") as creation_time,
    datetime(last_access_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch") as last_access_time,
    online_url,
    file_path,
    title,
    access_count,
    file_size
    from offlinepages_v1
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Offline Pages')
        report.start_artifact_report(report_folder, 'Offline Pages')
        report.add_script()
        data_headers = ('Creation Time','Last Access Time', 'Online URL', 'File Path', 'Title', 'Access Count', 'File Size' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],(textwrap.fill(row[2], width=75)),row[3],row[4],row[5],row[6]))
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Chrome Offline Pages data available')
    
    db.close()
    return