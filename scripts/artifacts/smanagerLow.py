import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_smanagerLow(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    id,
    package_name,
    datetime(start_time /1000, "unixepoch"),
    datetime(end_time /1000, "unixepoch"),
    uploaded,
    datetime(created_at /1000, "unixepoch"),
    datetime(modified_at /1000, "unixepoch")
    from usage_log
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Smart Manager - Usage')
        report.start_artifact_report(report_folder, 'Samsung Smart Manager - Usage')
        report.add_script()
        data_headers = ('ID','Package Name','Start Time','End Time', 'Uploaded?', 'Created', 'Modified' )
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'samsung smart manager - usage'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Samsung Smart Manager - Usage data available')
    
    db.close()
    return