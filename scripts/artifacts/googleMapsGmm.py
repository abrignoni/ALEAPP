import os
import sqlite3
import struct
import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly

def get_googleMapsGmm(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('gmm_storage.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select 
        rowid, 
        _data,
        _key_pri
        from gmm_storage_table 
        ''')
        all_rows = cursor.fetchall()
        
        for row in all_rows:
            id = row[0]
            data = row[1]
            keypri = row[2]
            
            idx=data.find(b"/dir/")
            
            if (idx!=-1):
                length=struct.unpack("<B",data[idx-2:idx-1])[0]
                directions=data[idx:idx+length]
                fromlat=""
                fromlon=""
                tolon=""
                tolat=""
                timestamp=""
                
                try:
                    directions=directions.decode()
                except:
                    directions=str(directions)
                    
                fromlat=directions.split("/dir/")[1].split(",")[0]
                fromlon=directions.split(",")[1].split("/")[0]
                endidx=directions.rfind("!1d")
                dd=directions[endidx:]
                if (dd!=-1):
                    if len(dd.split("!1d"))>1 and len(dd.split("!2d"))>1:
                        tolon=dd.split("!1d")[1].split("!")[0]
                        tolat=dd.split("!2d")[1].split("!")[0]
                idx=data.find(b"\x4C\x00\x01\x67\x74\x00\x12\x4C\x6A\x61\x76\x61\x2F\x6C\x61\x6E\x67\x2F\x53\x74\x72\x69\x6E\x67\x3B\x78\x70")
                if (idx!=-1):
                    timestamp=struct.unpack(">Q",data[idx+0x1B:idx+0x1B+8])[0]
                
                if directions.startswith('b\''):
                    directions = directions.replace('b\'','', 1)
                    directions = directions[:-1]
                
                directions = ("https://google.com/maps"+directions)
                directions = f'<a href="{directions}" style = "color:blue" target="_blank">{directions}</a>'
                
                data_list.append((directions, fromlat, fromlon, tolat, tolon, id, keypri))
                    
        
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Search History Maps')
            report.start_artifact_report(report_folder, 'Google Search History Maps')
            report.add_script()
            data_headers = ('Directions', 'Latitude', 'Longitude', 'To Latitude', 'To Longitude', 'Row ID', 'Type')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = f'Google Search History Maps'
            tsv(report_folder, data_headers, data_list, tsvname)
        
        else:
            logfunc('No Google Search History Maps data available')
        
        db.close()

__artifacts__ = {
        "gmm_maps": (
                "GEO Location",
                ('*/data/com.google.android.apps.maps/databases/gmm_storage.db*'),
                get_googleMapsGmm)
}