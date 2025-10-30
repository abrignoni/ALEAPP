import sqlite3
import json
import datetime
import textwrap
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen, media_to_html

def get_galleryTrash(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        
        if filename.endswith('local.db'):
            
            db = open_sqlite_db_readonly(file_found)
            
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(__deleteTime/1000,'unixepoch'),
            __Title,
            __absPath,
            __originTitle,
            __originPath,
            __expiredPeriod,
            __restoreExtra
            FROM trash
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    extendeddata = row[6]
                    extendeddata = json.loads(extendeddata)
                    datetaken = (extendeddata['__dateTaken'])
                    datetaken = (datetime.datetime.utcfromtimestamp(datetaken/1000).strftime('%Y-%m-%d %H:%M:%S'))
                    latitude = (extendeddata.get('latitude', ''))
                    longitude = (extendeddata.get('longitude', ''))
                    
                    thumb = media_to_html(row[1], files_found, report_folder)
                    
                    extendedout = ''
                    for x, y in extendeddata.items():
                        extendedout = extendedout + f'<br> {x}: {y}'
                        
                    data_list.append((datetaken, row[0], thumb, row[1], row[3], row[2], row[4], extendedout.strip(), latitude, longitude ))
                
                report = ArtifactHtmlReport('Gallery Trash Files')
                report.start_artifact_report(report_folder, 'Gallery Trash Files')
                report.add_script()
                data_headers = ('Timestamp','Date Deleted','Deleted Media','Trash Title','Original Title','Trash Path','Orginal Path','Extra Data','Latitude','Longitude') 
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = f'Gallery Trash Files'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Gallery Trash Files'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
            else:
                logfunc('No Gallery Trash Files data available')

__artifacts__ = {
        "Gallery Trash": (
                "Gallery Trash",
                ('*/data/com.sec.android.gallery3d/databases/local.db*','*/data/com.sec.android.gallery3d/files/.Trash/**'),
                get_galleryTrash)
}