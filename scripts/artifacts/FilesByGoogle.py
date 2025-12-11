__artifacts_v2__ = {
    "fbg_master": {
        "name": "Files By Google - Files Master",
        "description": "Parses the master files list from the Files by Google application",
        "author": "@KevinPagano3",
        "creation_date": "2021-01-18",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "Files By Google",
        "notes": "",
        "paths": ('*/com.google.android.apps.nbu.files/databases/files_master_database*'),
        "output_types": "standard",
        "artifact_icon": "file"
    },
    "fbg_searchhistory": {
        "name": "Files By Google - Search History",
        "description": "Parses the Files by Google application search history",
        "author": "@KevinPagano3",
        "date": "2021-01-18",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "Files By Google",
        "notes": "",
        "paths": ('*/com.google.android.apps.nbu.files/databases/search_history_database*'),
        "output_types": "standard",
        "artifact_icon": "search"
    },
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

@artifact_processor
def fbg_master(files_found, report_folder, seeker, wrap_text):
    data_list_master = []

    for file_found in files_found:
        file_found = str(file_found)
        
        # Master list
        if file_found.endswith('files_master_database'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
                case file_date_modified_ms
                    when 0 then ''
                    else datetime(file_date_modified_ms/1000,'unixepoch')
                end as file_date_modified_ms,
                root_path,
                root_relative_file_path,
                file_name,
                size,
                mime_type,
                case media_type
                    when 0 then 'App/Data'
                    when 1 then 'Picture'
                    when 2 then 'Audio'
                    when 3 then 'Video'
                    when 6 then 'Text'
                end as media_type,
                uri,
                case is_hidden
                    when 0 then ''
                    when 1 then 'Yes'
                end as is_hidden,
                title,
                parent_folder_name
            from files_master_table
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    last_mod_date = row[0]
                    if last_mod_date is None:
                        pass
                    else:
                        last_mod_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_mod_date),'UTC')
                
                    data_list_master.append((last_mod_date,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],file_found))
            db.close()
            
    data_headers = (('Date Modified','datetime'),'Root Path','Root Relative Path','File Name','Size','Mime Type','Media Type','URI','Hidden','Title','Parent Folder','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
    return data_headers, data_list_master, 'See source file(s) below'
            
@artifact_processor
def fbg_searchhistory(files_found, report_folder, seeker, wrap_text):
    data_list_search = []
    
    for file_found in files_found:
        file_found = str(file_found)

        # Search History
        if file_found.endswith('search_history_database'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
                case timestamp
                    when 0 then ''
                    else datetime(timestamp/1000,'unixepoch')
                end as timestamp,
                searched_term
            from search_history_content
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = row[0]
                    if timestamp is None:
                        pass
                    else:
                        timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(timestamp),'UTC')
                    data_list_search.append((timestamp,row[1],file_found))
            db.close()
            
        else:
            continue # Skip all other files
            
    data_headers = (('Timestamp','datetime'),'Search Term','Source File') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
    return data_headers, data_list_search, 'See source file(s) below'