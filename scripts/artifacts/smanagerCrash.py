import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_smanagerCrash(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    package_name,
    datetime(crash_time / 1000, "unixepoch")
    from crash_info
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Smart Manager - Crash')
        report.start_artifact_report(report_folder, 'Samsung Smart Manager - Crash')
        report.add_script()
        data_headers = ('Package Name','Timestamp')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Samsung Smart Manager - Crash data available')
    
    db.close()
    return