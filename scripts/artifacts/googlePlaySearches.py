import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googlePlaySearches(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(date / 1000, "unixepoch"),
    display1,
    query
    from suggestions
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Play Searches')
        report.start_artifact_report(report_folder, 'Google Play Searches')
        report.add_script()
        data_headers = ('Timestamp','Display','query' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'google play searches'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Play Searches'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Play Searches data available')
    
    db.close()
    return

