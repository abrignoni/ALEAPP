import sqlite3
import textwrap
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_libretorrent(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        if file_found.endswith('libretorrent.db'):
            break # Skip all other files
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        id,
        name,
        downloadPath,
        dateAdded,
        error,
        manuallyPaused,
        magnet,
        downloadingMetadata,
        visibility
        FROM Torrent
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Libre Torrent - Torrents')
        report.start_artifact_report(report_folder, 'Libre Torrent - Torrents')
        report.add_script()
        data_headers = ('Timestamp','ID','Name','Download Path','Error','Manually Paused','Magnet','Downloading Metadata','Visibility')
        data_list = []
        for row in all_rows:
            timestamp = datetime.utcfromtimestamp(row[3]/1000)
            data_list.append((timestamp,row[0],row[1],row[2],row[4],row[5],row[6],row[7],row[8]))
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Libre Torrent - Torrents'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Libre Torrent - Torrents'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Libre Torrents data available')
        
    db.close()

__artifacts__ = {
        "Libretorrent": (
                "Libre Torrent",
                ('*/data/com.houseoflife.bitlord/databases/libretorrent.db*','*/libretorrent.db*'),
                get_libretorrent)
}
