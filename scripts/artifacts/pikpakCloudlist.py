import sqlite3
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_pikpakCloudlist(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    create_time,
    modify_time,
    delete_time,
    datetime(local_update_time/1000, 'unixepoch' ),
    user_id,
    name,
    kind,
    url,
    thumbnail_link
    FROM xpan_files
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            link = f'<a href="{row[8]}" target="_blank">{row[8]}</a>'
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],link))

        description = 'PikPak Cloud List links are clickable!!!!! If connected to the internet and pressed the browser will try to open them in a new tab.'
        report = ArtifactHtmlReport('PikPak Cloud List')
        report.start_artifact_report(report_folder, 'PikPak Cloud List', description)
        report.add_script()
        data_headers = ('Create Time', 'Modify Time','Delete Time', 'Local Update Time', 'User ID', 'Name', 'Kind', 'URL','Thumbnail Link')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Thumbnail Link'])
        report.end_artifact_report()
        
        tsvname = 'PikPak Cloud List'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'PikPak Cloud List'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No PikPak Cloud List data available')
    
__artifacts__ = {
        "PikPak Cloud List": (
                "PikPak",
                ('*/com.pikcloud.pikpak/databases/pikpak_files_*.db*'),
                get_pikpakCloudlist)
}