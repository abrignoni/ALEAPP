import sqlite3
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_vlcMedia(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('vlc_media.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(insertion_date, 'unixepoch'),
    datetime(last_played_date,'unixepoch'),
    filename,
    path,
    is_favorite
    from Media
    left join Folder
    on Media.folder_id = Folder.id_folder
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4]))

        description = 'VLC Media List'
        report = ArtifactHtmlReport('VLC Media List')
        report.start_artifact_report(report_folder, 'VLC Media List', description)
        report.add_script()
        data_headers = ('Insertion Date', 'Last Played Date', 'Filename', 'Path', 'Is Favorite?' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'VLC Media'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'VLC Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No VLC Media data available')
    
__artifacts__ = {
        "VLC": (
                "VLC",
                ('*vlc_media.db*'),
                get_vlcMedia)
}