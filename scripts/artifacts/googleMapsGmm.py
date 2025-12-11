__artifacts_v2__ = {
    "Google Maps GMM": {
        "name": "Google Maps GMM",
        "description": "Parse Google Maps GMM db files",
        "author": "@AlexisBrignoni",  
        "version": "0.0.3",  
        "date": "2022-12-30",  
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Updated 2023-12-12 by @segumarc, wrong file_found was wrote in the 'located at' field in the html report",
        "paths": ('*/com.google.android.apps.maps/databases/gmm_myplaces.db','*/com.google.android.apps.maps/databases/gmm_storage.db'),
        "function": "get_googleMapsGmm"
    }
}

import os
import sqlite3
import struct
from datetime import *
import blackboxprotobuf
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly, convert_utc_human_to_timezone

def get_googleMapsGmm(files_found, report_folder, seeker, wrap_text):
    
    data_list_storage = []
    data_list_myplaces = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('gmm_storage.db'):
            db = open_sqlite_db_readonly(file_found)
            file_found_storage = file_found
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
                    data_list_storage.append((directions, fromlat, fromlon, tolat, tolon, id, keypri))
            db.close()

        if file_found.endswith('gmm_myplaces.db'):
            db = open_sqlite_db_readonly(file_found)
            file_found_myplaces = file_found
            cursor = db.cursor()
            cursor.execute('''
            select 
            rowid,
            key_string,
            round(latitude*.000001,6),
            round(longitude*.000001,6),
            sync_item,
            timestamp         
            from sync_item 
            ''')
            all_rows = cursor.fetchall()

            for row in all_rows:
                id = row[0]
                keystring = row[1]
                latitude = row[2]
                longitude = row[3]
                syncitem = row[4]
                timestamp = row[5]
                pb = blackboxprotobuf.decode_message(syncitem, 'None')

                if keystring == "0:0":
                    label = "Home"
                elif keystring == "1:0":
                    label = "Work"
                else:
                    label = pb[0].get('6', {}).get('7', b'').decode('utf-8')

                address = pb[0].get('6', {}).get('2', b'').decode('utf-8')
                url = pb[0].get('6', {}).get('6', b'').decode('utf-8')
                url = f'<a href="{url}" style = "color:blue" target="_blank">{url}</a>'
                timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
                timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')
                data_list_myplaces.append((timestamp,label,latitude,longitude,address,url))
            db.close()
        else:
            continue
        
    if data_list_storage:
        report = ArtifactHtmlReport('Google Search History Maps')
        report.start_artifact_report(report_folder, 'Google Search History Maps')
        report.add_script()
        data_headers = ('Directions', 'Latitude', 'Longitude', 'To Latitude', 'To Longitude', 'Row ID', 'Type')
        report.write_artifact_data_table(data_headers, data_list_storage, file_found_storage, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Google Search History Maps'
        tsv(report_folder, data_headers, data_list_storage, tsvname)
    else:
        logfunc('No Google Search History Maps data available')

    if data_list_myplaces:
        report = ArtifactHtmlReport('Google Maps Label Places')
        report.start_artifact_report(report_folder, 'Google Maps Label Places')
        report.add_script()
        data_headers = ('Timestamp','Label', 'Latitude', 'Longitude', 'Address', 'URL')
        report.write_artifact_data_table(data_headers, data_list_myplaces, file_found_myplaces, html_escape=False)
        report.end_artifact_report()
       
        tsvname = f'Google Maps Label Places'
        tsv(report_folder, data_headers, data_list_myplaces, tsvname)

        tlactivity = f'Google Maps Label Places'
        timeline(report_folder, tlactivity, data_list_myplaces, data_headers)
    else:
        logfunc('No Google Maps Label Places data available')