__artifacts_v2__ = {
    "EmulatedSmeta": {
        "name": "Emulated Storage Metadata",
        "description": "Parses emulated storage metadata from external.db",
        "author": "@AlexisBrignoni",
        "version": "0.0.2",
        "date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "2023-02-10 - Updated by @KevinPagano3",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*','*/com.android.providers.media/databases/external.db*'),
        "function": "get_emulatedSmeta"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_emulatedSmeta(files_found, report_folder, seeker, wrap_text):

    data_list_downloads = []
    data_list_images = []
    data_list_files = []
    data_list_videos = []    
    data_list_audio = []
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('external.db'):
            continue # Skip all other files
            
        if 'media.module' in file_found:
            db = open_sqlite_db_readonly(file_found)
            # Downloads
            cursor = db.cursor()
            cursor.execute('''
            SELECT
                datetime(date_added,  'unixepoch'),
                datetime(date_modified, 'unixepoch'),
                datetime(datetaken, 'unixepoch'),
                _data,
                title,
                _display_name,
                _size,
                owner_package_name,
                bucket_display_name,
                referer_uri,
                download_uri,
                relative_path,
                case is_download
                    when 0 then ''
                    when 1 then 'Yes'
                end,
                case is_favorite
                    when 0 then ''
                    when 1 then 'Yes'
                end,
                case is_trashed
                    when 0 then ''
                    when 1 then 'Yes'
                end,
                xmp
            FROM downloads
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                    if isinstance(row[15], bytes):
                        xmp = str(row[15])[2:-1]
                    else:
                        xmp = row[15]
                    
                    if keytime is None:
                        pass
                    else:
                        keytime = convert_utc_human_to_timezone(convert_ts_human_to_utc(keytime),'UTC')
                        
                    date_added = row[0]
                    if date_added is None:
                        pass
                    else:
                        date_added = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_added),'UTC')
                    
                    date_modified = row[1]
                    if date_modified is None:
                        pass
                    else:
                        date_modified = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_modified),'UTC')
                        
                    date_taken = row[2] 
                    if date_taken is None:
                        pass
                    else:
                        date_taken = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_taken),'UTC')
                    
                    data_list_downloads.append((keytime, date_added, date_modified, date_taken, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], xmp, file_found))
            
            # Images
            cursor.execute('''
            SELECT
            datetime(date_added,  'unixepoch'),
            datetime(date_modified, 'unixepoch'),
            datetime(datetaken, 'unixepoch'),
            _data,
            title,
            _display_name,
            _size,
            latitude,
            longitude,
            case orientation
                when 0 then 'Horizontal'
                else 'Vertical'
            end,
            owner_package_name,
            bucket_display_name,
            relative_path,
            case is_download
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_favorite
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_trashed
                when 0 then ''
                when 1 then 'Yes'
            end
            from images
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                        
                    if keytime is None:
                        pass
                    else:
                        keytime = convert_utc_human_to_timezone(convert_ts_human_to_utc(keytime),'UTC')
                        
                    date_added = row[0]
                    if date_added is None:
                        pass
                    else:
                        date_added = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_added),'UTC')
                    
                    date_modified = row[1]
                    if date_modified is None:
                        pass
                    else:
                        date_modified = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_modified),'UTC')
                        
                    date_taken = row[2] 
                    if date_taken is None:
                        pass
                    else:
                        date_taken = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_taken),'UTC')
                    
                    data_list_images.append((keytime, date_added, date_modified, date_taken, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], file_found))

            # Files (newer version)
            cursor.execute('''
            SELECT
            datetime(date_added,  'unixepoch'),
            datetime(date_modified, 'unixepoch'),
            datetime(datetaken, 'unixepoch'),
            _data,
            title,
            _display_name,
            _size,
            latitude,
            longitude,
            case orientation
                when 0 then 'Horizontal'
                else 'Vertical'
            end,
            owner_package_name,
            bucket_display_name,
            referer_uri,
            download_uri,
            relative_path,
            case is_download
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_favorite
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_trashed
                when 0 then ''
                when 1 then 'Yes'
            end
            from files
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                        
                    if keytime is None:
                        pass
                    else:
                        keytime = convert_utc_human_to_timezone(convert_ts_human_to_utc(keytime),'UTC')
                        
                    date_added = row[0]
                    if date_added is None:
                        pass
                    else:
                        date_added = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_added),'UTC')
                    
                    date_modified = row[1]
                    if date_modified is None:
                        pass
                    else:
                        date_modified = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_modified),'UTC')
                        
                    date_taken = row[2] 
                    if date_taken is None:
                        pass
                    else:
                        date_taken = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_taken),'UTC')
                    
                    data_list_files.append((keytime, date_added, date_modified, date_taken, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], file_found))

            # Videos
            cursor.execute('''
            SELECT
            datetime(date_added,  'unixepoch'),
            datetime(date_modified, 'unixepoch'),
            datetime(datetaken, 'unixepoch'),
            _data,
            title,
            _display_name,
            _size,
            latitude,
            longitude,
            case orientation
                when 0 then 'Horizontal'
                else 'Vertical'
            end,
            owner_package_name,
            bucket_display_name,
            relative_path,
            case is_download
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_favorite
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_trashed
                when 0 then ''
                when 1 then 'Yes'
            end
            from video
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                        
                    if keytime is None:
                        pass
                    else:
                        keytime = convert_utc_human_to_timezone(convert_ts_human_to_utc(keytime),'UTC')
                        
                    date_added = row[0]
                    if date_added is None:
                        pass
                    else:
                        date_added = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_added),'UTC')
                    
                    date_modified = row[1]
                    if date_modified is None:
                        pass
                    else:
                        date_modified = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_modified),'UTC')
                        
                    date_taken = row[2] 
                    if date_taken is None:
                        pass
                    else:
                        date_taken = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_taken),'UTC')
                    
                    data_list_videos.append((keytime, date_added, date_modified, date_taken, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], file_found))

            # Audio
            cursor.execute('''
            SELECT
            datetime(date_added,  'unixepoch'),
            datetime(date_modified, 'unixepoch'),
            datetime(datetaken, 'unixepoch'),
            _data,
            title,
            _display_name,
            _size,
            owner_package_name,
            bucket_display_name,
            relative_path,
            case is_download
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_favorite
                when 0 then ''
                when 1 then 'Yes'
            end,
            case is_trashed
                when 0 then ''
                when 1 then 'Yes'
            end
            from audio
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                        
                    if keytime is None:
                        pass
                    else:
                        keytime = convert_utc_human_to_timezone(convert_ts_human_to_utc(keytime),'UTC')
                        
                    date_added = row[0]
                    if date_added is None:
                        pass
                    else:
                        date_added = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_added),'UTC')
                    
                    date_modified = row[1]
                    if date_modified is None:
                        pass
                    else:
                        date_modified = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_modified),'UTC')
                        
                    date_taken = row[2] 
                    if date_taken is None:
                        pass
                    else:
                        date_taken = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_taken),'UTC')
                    
                    data_list_audio.append((keytime, date_added, date_modified, date_taken, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], file_found))

            db.close()
            
        else:
            # Files (older version)
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(date_added,  'unixepoch') as "Timestamp Added",
            datetime(date_modified, 'unixepoch') as "Timestamp Modified",
            datetime(datetaken, 'unixepoch') as "Timestamp Taken",
            _data,
            title,
            _display_name,
            _size,
            latitude,
            longitude,
            case orientation
                when 0 then 'Horizontal'
                else 'Vertical'
            end,
            bucket_display_name,
            width,
            height,
            _id
            from files
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    date_added = row[0]
                    if date_added is None:
                        pass
                    else:
                        date_added = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_added),'UTC')
                    
                    date_modified = row[1]
                    if date_modified is None:
                        pass
                    else:
                        date_modified = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_modified),'UTC')
                        
                    date_taken = row[2] 
                    if date_taken is None:
                        pass
                    else:
                        date_taken = convert_utc_human_to_timezone(convert_ts_human_to_utc(date_taken),'UTC')
                
                    data_list.append((date_added, date_modified, date_taken, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], file_found))

            db.close()                
                
    # Downloads Report            
    if data_list_downloads:
        report = ArtifactHtmlReport('Emulated Storage Metadata - Downloads')
        report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Downloads')
        report.add_script()
        data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Owner Package Name','Bucket Display Name','Referer URI','Download URI','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?','XMP','Source')
        
        report.write_artifact_data_table(data_headers, data_list_downloads, file_found)
        report.end_artifact_report()
        
        tsvname = f'Emulated Storage Metadata - Downloads'
        tsv(report_folder, data_headers, data_list_downloads, tsvname)
        
        tlactivity = f'Emulated Storage Metadata - Downloads'
        timeline(report_folder, tlactivity, data_list_downloads, data_headers)
    else:
        logfunc('No Emulated Storage Metadata - Downloads data available')
    
    # Images Report    
    if data_list_images:
        report = ArtifactHtmlReport('Emulated Storage Metadata - Images')
        report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Images')
        report.add_script()
        data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Owner Package Name','Bucket Display Name','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?','Source')

        report.write_artifact_data_table(data_headers, data_list_images, file_found)
        report.end_artifact_report()
        
        tsvname = f'Emulated Storage Metadata - Images'
        tsv(report_folder, data_headers, data_list_images, tsvname)
        
        tlactivity = f'Emulated Storage Metadata - Images'
        timeline(report_folder, tlactivity, data_list_images, data_headers)
    else:
        logfunc('No Emulated Storage Metadata - Images data available')
    
    # Files (newer version) Report
    if data_list_files:
        report = ArtifactHtmlReport('Emulated Storage Metadata - Files')
        report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Files')
        report.add_script()
        data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Owner Package Name','Bucket Display Name','Referer URI','Download URI','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?','Source')

        report.write_artifact_data_table(data_headers, data_list_files, file_found)
        report.end_artifact_report()
        
        tsvname = f'Emulated Storage Metadata - Files'
        tsv(report_folder, data_headers, data_list_files, tsvname)
        
        tlactivity = f'Emulated Storage Metadata - Files'
        timeline(report_folder, tlactivity, data_list_files, data_headers)
    else:
        logfunc('No Emulated Storage Metadata - Files data available')
    
    # Videos Report
    if data_list_videos:  
        report = ArtifactHtmlReport('Emulated Storage Metadata - Videos')
        report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Videos')
        report.add_script()
        data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Owner Package Name','Bucket Display Name','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?','Source')

        report.write_artifact_data_table(data_headers, data_list_videos, file_found)
        report.end_artifact_report()
        
        tsvname = f'Emulated Storage Metadata - Videos'
        tsv(report_folder, data_headers, data_list_videos, tsvname)
        
        tlactivity = f'Emulated Storage Metadata - Videos'
        timeline(report_folder, tlactivity, data_list_videos, data_headers)
    else:
        logfunc('No Emulated Storage Metadata - Videos data available')
        
    # Audio Report
    if data_list_audio:
        report = ArtifactHtmlReport('Emulated Storage Metadata - Audio')
        report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Audio')
        report.add_script()
        data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Owner Package Name','Bucket Display Name','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?','Source')

        report.write_artifact_data_table(data_headers, data_list_audio, file_found)
        report.end_artifact_report()
        
        tsvname = f'Emulated Storage Metadata - Audio'
        tsv(report_folder, data_headers, data_list_audio, tsvname)
        
        tlactivity = f'Emulated Storage Metadata - Audio'
        timeline(report_folder, tlactivity, data_list_audio, data_headers)
    else:
        logfunc('No Emulated Storage Metadata - Audio data available')
        
    # Files (older version)
    if data_list:
        report = ArtifactHtmlReport('Emulated Storage Metadata - Files')
        report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Files')
        report.add_script()
        data_headers = ('Timestamp Added','Timestamp Modified','Timestamp Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Bucket Display Name','Parent Path','Width','Height','ID')
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Emulated Storage Metadata - Files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Emulated Storage Metadata - Files'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Emulated Storage Metadata - Files data available')  