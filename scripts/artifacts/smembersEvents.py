import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_smembersEvents(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select 
    type, 
    value, 
    datetime(created_at /1000, "unixepoch"), 
    in_snapshot
    FROM device_events
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Members - Events')
        report.start_artifact_report(report_folder, 'Samsung Members - Events')
        report.add_script()
        data_headers = ('Type','Value','Created At','Snapshot?' )
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Samsung Members - Events data available')
    
    db.close()
    return