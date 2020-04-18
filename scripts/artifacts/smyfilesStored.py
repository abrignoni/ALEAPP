import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_smyfilesStored(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    storage,
    path,
    size,
    datetime(date / 1000, "unixepoch"),
    datetime(latest /1000, "unixepoch")
    from FileCache
    where path is not NULL 
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Stored Files')
        report.start_artifact_report(report_folder, 'My Files DB - Stored Files')
        report.add_script()
        data_headers = ('Storage','Path','Size','Timestamp','Latest' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No My Files DB Stored data available')
    
    db.close()
    return