import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_chromeTopSites(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    url,
    url_rank,
    title,
    redirects
    FROM
    top_sites ORDER by url_rank asc
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Chrome Top Sites')
        report.start_artifact_report(report_folder, 'Top Sites')
        report.add_script()
        data_headers = ('URL','Rank','Title','Redirects')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Chrome Top Sites data available')
    
    db.close()
    return

