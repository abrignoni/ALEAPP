import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_emulatedSmeta(files_found, report_folder, seeker, wrap_text, time_offset):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('external.db'):
            continue # Skip all other files
            
        if 'media.module' in file_found:
            db = open_sqlite_db_readonly(file_found)
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
                report = ArtifactHtmlReport('Emulated Storage Metadata - Downloads')
                report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Downloads')
                report.add_script()
                data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Owner Package Name','Bucket Display Name','Referer URI','Download URI','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?','XMP')
                data_list = []
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                    
                    if isinstance(row[15], bytes):
                        xmp = str(row[15])[2:-1]
                    else:
                        xmp = row[15]
                    
                    data_list.append((keytime, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], xmp))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Emulated Storage Metadata - Downloads'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Emulated Storage Metadata - Downloads'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Emulated Storage Metadata - Downloads data available')
            
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
                report = ArtifactHtmlReport('Emulated Storage Metadata - Images')
                report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Images')
                report.add_script()
                data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Owner Package Name','Bucket Display Name','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?')
                data_list = []
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                    data_list.append((keytime, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Emulated Storage Metadata - Images'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Emulated Storage Metadata - Images'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Emulated Storage Metadata - Images data available')
            
            
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
                report = ArtifactHtmlReport('Emulated Storage Metadata - Files')
                report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Files')
                report.add_script()
                data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Owner Package Name','Bucket Display Name','Referer URI','Download URI','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?')
                data_list = []
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                    data_list.append((keytime, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Emulated Storage Metadata - Files'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Emulated Storage Metadata - Files'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Emulated Storage Metadata - Files data available')

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
                report = ArtifactHtmlReport('Emulated Storage Metadata - Videos')
                report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Videos')
                report.add_script()
                data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Owner Package Name','Bucket Display Name','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?')
                data_list = []
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                    data_list.append((keytime, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Emulated Storage Metadata - Videos'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Emulated Storage Metadata - Videos'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Emulated Storage Metadata - Videos data available')

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
                report = ArtifactHtmlReport('Emulated Storage Metadata - Audio')
                report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Audio')
                report.add_script()
                data_headers = ('Key Timestamp','Date Added','Date Modified','Date Taken','Path','Title','Display Name','Size','Owner Package Name','Bucket Display Name','Relative Path','Is Downloaded?','Is Favorited?','Is Trashed?')
                data_list = []
                for row in all_rows:
                    if bool(row[0]):
                        keytime = row[0]
                    else:
                        keytime = row[1]
                    data_list.append((keytime, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Emulated Storage Metadata - Audio'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Emulated Storage Metadata - Audio'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Emulated Storage Metadata - Audio data available')

            db.close()
            
        else:
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
                report = ArtifactHtmlReport('Emulated Storage Metadata - Files')
                report.start_artifact_report(report_folder, 'Emulated Storage Metadata - Files')
                report.add_script()
                data_headers = ('Timestamp Added','Timestamp Modified','Timestamp Taken','Path','Title','Display Name','Size','Latitude','Longitude','Orientation','Bucket Display Name','Parent Path','Width','Height','ID')
                data_list = []
                parent = ''
                for row in all_rows:
                    
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Emulated Storage Metadata - Files'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Emulated Storage Metadata - Files'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Emulated Storage Metadata - Files data available')

__artifacts__ = {
        "EmulatedSmeta": (
                "Emulated Storage Metadata",
                ('*/com.google.android.providers.media.module/databases/external.db*','*/com.android.providers.media/databases/external.db*'),
                get_emulatedSmeta)
}