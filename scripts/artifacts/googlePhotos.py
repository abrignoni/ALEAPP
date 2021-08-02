import sqlite3
import io
import json
import os
import shutil

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly

def get_googlePhotos(files_found, report_folder, seeker, wrap_text):
    
    source_file_photos = ''
    source_file_cache = ''
    source_file_trash = ''
    gphotos_photos_db = ''
    gphotos_cache_db = ''
    gphotos_trash_db = ''
    
    for file_found in files_found:
    
        file_name = str(file_found)
        if file_name.lower().endswith('gphotos0.db'):
           gphotos_photos_db = str(file_found)
           source_file_photos = file_found.replace(seeker.directory, '')

        if file_name.lower().endswith('disk_cache'):
           gphotos_cache_db = str(file_found)
           source_file_cache = file_found.replace(seeker.directory, '')
           
        if file_name.lower().endswith('local_trash.db'):
           gphotos_trash_db = str(file_found)
           source_file_trash = file_found.replace(seeker.directory, '')
    
    db = open_sqlite_db_readonly(gphotos_photos_db)
    cursor = db.cursor()
    
    columns = [i[1] for i in cursor.execute('PRAGMA table_info(local_media)')]
    
    if 'purge_timestamp' not in columns:
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
        case duration
            when 0 then ''
            else strftime('%H:%M:%S', duration/1000, 'unixepoch')
        end,
        latitude,
        longitude,
        folder_name,
        media_store_id,
        case trash_timestamp
            when NULL then ''
            else datetime(trash_timestamp/1000, 'unixepoch')
        end
        from local_media
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Photos - Local Media')
            report.start_artifact_report(report_folder, 'Google Photos - Local Media')
            report.add_script()
            data_headers = ('Timestamp','File Name','File Path','Captured Timestamp (Local)','Timezone Offset','Width','Height','Size','Duration','Latitude','Longitude','Folder Name','Media Store ID','Trashed Timestamp')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Photos - Local Media'
            tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
            
            tlactivity = f'Google Photos - Local Media'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'Google Photos - Local Media'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
            
        else:
            logfunc('No Google Photos - Local Media data available')
    
    else:
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
        case duration
            when 0 then ''
            else strftime('%H:%M:%S', duration/1000, 'unixepoch')
        end,
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
            tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
            
            tlactivity = f'Google Photos - Local Media'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'Google Photos - Local Media'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
            
        else:
            logfunc('No Google Photos - Local Media data available')
       
    columns2 = [i[1] for i in cursor.execute('PRAGMA table_info(remote_media)')]
    
    if 'inferred_latitude' not in columns2:
        cursor.execute('''
        select
        datetime(utc_timestamp/1000, 'unixepoch'),
        filename,
        replace(remote_url,'=s0-d',''),
        datetime(capture_timestamp/1000, 'unixepoch'),
        timezone_offset/3600000,
        strftime('%H:%M:%S', duration/1000, 'unixepoch'),
        latitude,
        longitude,
        upload_status
        from remote_media
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Photos - Remote Media')
            report.start_artifact_report(report_folder, 'Google Photos - Remote Media')
            report.add_script()
            data_headers = ('Timestamp','File Name','Remote URL','Captured Timestamp (Local)','Timezone Offset','Duration','Latitude','Longitude','Upload Status %') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Photos - Remote Media'
            tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
            
            tlactivity = f'Google Photos - Remote Media'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'Google Photos - Remote Media'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
            
        else:
            logfunc('No Google Photos - Remote Media data available')
         
    else:
        cursor.execute('''
        select
        datetime(utc_timestamp/1000, 'unixepoch'),
        filename,
        replace(remote_url,'=s0-d',''),
        datetime(capture_timestamp/1000, 'unixepoch'),
        timezone_offset/3600000,
        strftime('%H:%M:%S', duration/1000, 'unixepoch'),
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
            tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
            
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
        tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
        
        tlactivity = f'Google Photos - Shared Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Photos - Shared Media data available')
    
    cursor.execute('''
    select 
    DISTINCT(local_media.bucket_id),
    local_media.folder_name,
    rtrim(local_media.filepath, replace(local_media.filepath, '/', ''))
    from local_media, backup_folders
    where local_media.bucket_id = backup_folders.bucket_id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Photos - Backed Up Folders')
        report.start_artifact_report(report_folder, 'Google Photos - Backed Up Folders')
        report.add_script()
        data_headers = ('Bucket ID','Backed Up Folder Name','Backed Up Folder Path',)
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Backed Up Folders'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
        
        tlactivity = f'Google Photos - Backed Up Folders'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Photos - Backed Up Folders data available')
    
    db.close()
    
    db = open_sqlite_db_readonly(gphotos_cache_db)
    cursor = db.cursor()
    
    cursor.execute('''
    select
    datetime(last_modified_time/1000, 'unixepoch'),
    key,
    size,
    case pending_delete
        when 0 then ''
        when 1 then 'Yes'
    end
    from journal
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
        
            fileNameKey = row[1]
            thumb = ''
            
            for match in files_found:
                if fileNameKey in match:
                    shutil.copy2(match, report_folder)
                    data_file_name = os.path.basename(match)
                    thumb = f'<img src="{report_folder}/{data_file_name}" width="300"></img>'
                
            data_list.append((row[0],row[1],thumb,row[2],row[3]))
    
        report = ArtifactHtmlReport('Google Photos - Cache')
        report.start_artifact_report(report_folder, 'Google Photos - Cache')
        report.add_script()
        data_headers = ('Timestamp','Key','Image','Size','Pending Deletion')
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Image'])
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Cache'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_cache)
        
        tlactivity = f'Google Photos - Cache'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Photos - Cache data available')
    
    db.close()
    
    db = open_sqlite_db_readonly(gphotos_trash_db)
    cursor = db.cursor()
    
    cursor.execute('''
    select
    datetime(deleted_time/1000, 'unixepoch'),
    local_path,
    content_uri,
    trash_file_name,
    case is_video
        when 0 then ''
        when 1 then 'Yes'
    end,
    media_store_id
    from local
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
        
            fileNameKey = row[3]
            thumb = ''
            
            for match in files_found:
                if fileNameKey in match:
                    shutil.copy2(match, report_folder)
                    data_file_name = os.path.basename(match)
                    thumb = f'<img src="{report_folder}/{data_file_name}" width="300"></img>'
                
            data_list.append((row[0],row[1],row[2],row[3],thumb,row[4],row[5]))
    
        report = ArtifactHtmlReport('Google Photos - Local Trash')
        report.start_artifact_report(report_folder, 'Google Photos - Local Trash')
        report.add_script()
        data_headers = ('Timestamp','Original Path','Content URI','File Name','Image','Is Video','Media Store ID')
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Image'])
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Local Trash'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Photos - Local Trash'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Photos - Local Trash data available')
    
    db.close()
    return
