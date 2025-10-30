import sqlite3
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_pikpakDownloads(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(create_time/1000, 'unixepoch'),
    datetime(lastmod/1000, 'unixepoch'),
    title,
    _data,
    uri
    from xl_downloads
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        description = 'PikPak Downloads'
        report = ArtifactHtmlReport('PikPak Downloads')
        report.start_artifact_report(report_folder, 'PikPak Downloads', description)
        report.add_script()
        data_headers = ('Create Time', 'Modify Time','Title', 'Local Storage', 'URL')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'PikPak Downloads'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'PikPak Downloads'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No PikPak Downloads data available')
    
__artifacts__ = {
        "PikPak Downloads": (
                "PikPak",
                ('*/com.pikcloud.pikpak/databases/pikpak_downloads.db*'),
                get_pikpakDownloads)
}