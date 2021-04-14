import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly

def get_googlePhotos(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(utc_timestamp/1000, 'unixepoch'),
    filename,
    filepath,
    datetime(capture_timestamp/1000, 'unixepoch'),
    timezone_offset/3600000,
    width,
    height,
    size_bytes,
    duration,
    latitude,
    longitude,
    folder_name,
    media_store_id,
    case trash_timestamp
        when NULL then ''
        else datetime(trash_timestamp/1000, 'unixepoch')
    end,
    case purge_timestamp
        when NULL then ''
        else datetime(purge_timestamp/1000, 'unixepoch')
    end
    from local_media
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Photos - Local Media')
        report.start_artifact_report(report_folder, 'Google Photos - Local Media')
        report.add_script()
        data_headers = ('Timestamp','File Name','File Path','Captured Timestamp (Local)','Timezone Offset','Width','Height','Size','Duration','Latitude','Longitude','Folder Name','Media Store ID','Trashed Timestamp','Purge Timestamp') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Local Media'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Photos - Local Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Google Photos - Local Media'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)
        
    else:
        logfunc('No Google Photos - Local Media data available')
        
    cursor.execute('''
    select
    datetime(utc_timestamp/1000, 'unixepoch'),
    filename,
    replace(remote_url,'=s0-d',''),
    datetime(capture_timestamp/1000, 'unixepoch'),
    timezone_offset/3600000,
    duration,
    latitude,
    longitude,
    inferred_latitude,
    inferred_longitude,
    upload_status
    from remote_media
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Photos - Remote Media')
        report.start_artifact_report(report_folder, 'Google Photos - Remote Media')
        report.add_script()
        data_headers = ('Timestamp','File Name','Remote URL','Captured Timestamp (Local)','Timezone Offset','Duration','Latitude','Longitude','Inferred Latitude','Inferred Longitude','Upload Status %') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Remote Media'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Photos - Remote Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Google Photos - Remote Media'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)
        
    else:
        logfunc('No Google Photos - Remote Media data available')
    
    cursor.execute('''
    select
    datetime(utc_timestamp/1000, 'unixepoch') as "Timestamp (UTC)",
    filename,
    replace(remote_url,'=s0-d',''),
    size_bytes,
    datetime(capture_timestamp/1000, 'unixepoch') as "Capture Local Timestamp",
    timezone_offset/3600000,
    upload_status
    from shared_media
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Photos - Shared Media')
        report.start_artifact_report(report_folder, 'Google Photos - Shared Media')
        report.add_script()
        data_headers = ('Timestamp','File Name','Remote URL','Size','Captured Timestamp (Local)','Timezone Offset','Upload Status %')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Shared Media'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Photos - Shared Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Photos - Shared Media data available')
    
    db.close()
    return
