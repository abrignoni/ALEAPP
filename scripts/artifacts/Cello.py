__artifacts_v2__ = {
    "Cello": {
        "name": "Cello",
        "description": "Parses the Cello db for Google Drive metadata",
        "author": "@KevinPagano3",
        "version": "0.0.2",
        "date": "2020-12-21",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "",
        "paths": ('*/com.google.android.apps.docs/app_cello/*/cello.db*', '*/com.google.android.apps.docs/files/shiny_blobs/blobs/*'),
        "function": "get_Cello"
    }
}

import os
import shutil
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, get_next_unused_name, convert_ts_human_to_utc, convert_utc_human_to_timezone

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/'

def get_offline_path(files_found, blob_name):
    
    for file_found in files_found:
        if file_found.endswith(blob_name):
            file_found = str(file_found)
            return file_found
    return ''

def get_Cello(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    tsv_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??
        
        elif file_found.endswith('cello.db'):
            cello_db = file_found            
            db = open_sqlite_db_readonly(cello_db)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
                case created_date
                    when 0 then ''
                    else datetime(created_date/1000, 'unixepoch')
                end as created_date,
                title,
                case modified_date
                    when 0 then ''
                    else datetime(modified_date/1000, 'unixepoch')
                end as modified_date,
                case shared_with_me_date
                    when 0 then ''
                    else datetime(shared_with_me_date/1000, 'unixepoch')
                end as shared_with_me_date,
                case modified_by_me_date
                    when 0 then ''
                    else datetime(modified_by_me_date/1000, 'unixepoch')
                end as modified_by_me_date,
                case viewed_by_me_date
                    when 0 then ''
                    else datetime(viewed_by_me_date/1000, 'unixepoch')
                end as viewed_by_me_date,
                mime_type,
                Quota_bytes,
                case is_folder
                    when 0 then ''
                    when 1 then 'Yes'
                end as is_folder,
                case is_owner
                    when 0 then ''
                    when 1 then 'Yes'
                end as is_owner,
                case trashed
                    when 0 then ''
                    when 1 then 'Yes'
                end as trashed,
                (SELECT value from item_properties where key='offlineStatus' and item_stable_id=stable_id) as offline_status,
                (SELECT json_extract(value, '$.blobKey') from item_properties where key LIKE 'com.google.android.apps.docs:content_metadata%' and item_stable_id=stable_id) as content_metadata
            FROM items
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    doc_name = row[1]
                    offline_status = "No"
                    if row[11] == 1: # file is offline
                        offline_status = "Yes"
                        offline_path_name = row[12]
                        if offline_path_name not in (None, ''):
                            offline_path = get_offline_path(files_found, offline_path_name)
                            if offline_path:
                                destination_path = get_next_unused_name(os.path.join(report_folder, doc_name))
                                shutil.copy2(offline_path, destination_path)
                                dest_name = os.path.basename(destination_path)
                                doc_name = f"<a href=\"{folder_name}/{dest_name}\" target=\"_blank\" style=\"color:green; font-weight:bolder\">{doc_name}</a>"
                            else:
                                logfunc(f'File {doc_name} not present offline!')
                        else:
                            logfunc(f'File {doc_name} not present offline!')
                    if row[8] == "Yes":
                        doc_name = '<i data-feather="folder"></i> ' + doc_name
                    else:
                        if doc_name.startswith('<a href'):
                            doc_name = '<i data-feather="file" stroke="green"></i> ' + doc_name
                        else:
                            doc_name = '<i data-feather="file"></i> ' + doc_name
                            
                    created_date = row[0]
                    if created_date in (None, ''):
                        pass
                    else:
                        created_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(created_date),'UTC')
                    
                    modified_date = row[2]
                    if modified_date in (None, ''):
                        pass
                    else:
                        modified_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(modified_date),'UTC')
                        
                    shared_with_me_date = row[3]
                    if shared_with_me_date in (None, ''):
                        pass
                    else:
                        shared_with_me_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(shared_with_me_date),'UTC')
                    
                    modified_by_me_date = row[4]
                    if modified_by_me_date in (None, ''):
                        pass
                    else:
                        modified_by_me_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(modified_by_me_date),'UTC')
                    
                    viewed_by_me_date = row[5]
                    if viewed_by_me_date in (None, ''):
                        pass
                    else:
                        viewed_by_me_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(viewed_by_me_date),'UTC')
                    
                    data_list.append((created_date,doc_name,modified_date,shared_with_me_date,modified_by_me_date,viewed_by_me_date,row[6],offline_status,row[7],row[8],row[9],row[10],cello_db))
                    tsv_list.append((created_date,row[1],modified_date,shared_with_me_date,modified_by_me_date,viewed_by_me_date,row[6],offline_status,row[7],row[8],row[9],row[10],cello_db))
            db.close()
        
        else:
            continue # skip -journal and other files

        if report_folder[-1] == slash: 
            folder_name = os.path.basename(report_folder[:-1])
        else:
            folder_name = os.path.basename(report_folder)

    if data_list:
        account_name = os.path.basename(os.path.dirname(cello_db))
            
        report = ArtifactHtmlReport(f'Cello - {account_name}')
        report.start_artifact_report(report_folder, f'Cello - {account_name}')
        report.add_script()
        data_headers = ('Created Date','File Name','Modified Date','Shared with User Date','Modified by User Date','Viewed by User Date','Mime Type', \
                        'Offline','Quota Size','Folder','User is Owner','Deleted','Source File')

        report.write_artifact_data_table(data_headers, data_list, cello_db, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Google Drive - Cello - {account_name}'
        tsv(report_folder, data_headers, tsv_list, tsvname)
        
        tlactivity = f'Google Drive - Cello - {account_name}'
        timeline(report_folder, tlactivity, tsv_list, data_headers)
    else:
        logfunc('No Google Drive - Cello data available')