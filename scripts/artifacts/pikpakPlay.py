import sqlite3
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_pikpakPlay(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('greendao.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(last_play_timestamp/1000, 'unixepoch'),
    duration,
    played_time,
    max_played_time,
    name
    from VIDEO_PLAY_RECORD
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        description = 'PikPak Play'
        report = ArtifactHtmlReport('PikPak Play')
        report.start_artifact_report(report_folder, 'PikPak Play', description)
        report.add_script()
        data_headers = ('Last Play Timestamp', 'Duration','Played Time', 'Max Played Time', 'Name')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Thumbnail Link'])
        report.end_artifact_report()
        
        tsvname = 'PikPak Play'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'PikPak Play'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No PikPak Play data available')
    
__artifacts__ = {
        "PikPak Play": (
                "PikPak",
                ('*/com.pikcloud.pikpak/databases/greendao.db*'),
                get_pikpakPlay)
}