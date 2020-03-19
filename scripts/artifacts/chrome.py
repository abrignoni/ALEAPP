import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_chrome(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
        url,
        title,
        visit_count,
        datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch"),
        hidden
    from urls  
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Browser History')
        report.start_artifact_report(report_folder, 'Browser History')
        report.add_script()
        data_headers = ('URL','Title','Visit Count','Last Visit Time','Hidden' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((textwrap.fill(row[0], width=100),row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No browser history data available')
    
    db.close()
    return