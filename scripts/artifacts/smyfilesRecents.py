import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_smyfilesRecents(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(date / 1000, "unixepoch"),
    name,
    size,
    _data,
    ext,
    _source,
    _description,
    datetime(recent_date / 1000, "unixepoch")
    from recent_files 
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Recent Files')
        report.start_artifact_report(report_folder, 'My Files DB - Recent Files')
        report.add_script()
        data_headers = ('Timestamp','Name','Size','Data','Ext.', 'Source', 'Description', 'Recent Timestamp' ) 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'my files db - recent files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Recent Files'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Recents data available')
    
    db.close()
    return