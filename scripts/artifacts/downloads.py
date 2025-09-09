__artifacts_v2__ = {
    "downloads": {
        "name": "Native Downloads",
        "description": "Parses native downloads database",
        "author": "@KevinPagano3",
        "creation_date": "2023-01-09",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "Downloads",
        "notes": "",
        "paths": ('*/data/com.android.providers.downloads/databases/downloads.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

@artifact_processor
def downloads(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('downloads.db'):
            db = open_sqlite_db_readonly(file_found)
            #Get file downloads
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(lastmod/1000,'unixepoch') as "Modified/Downloaded Timestamp",
            title,
            description,
            uri,
            _data,
            mimetype,
            notificationpackage,
            current_bytes,
            total_bytes,
            status,
            errorMsg,
            etag,
            case is_visible_in_downloads_ui
                when 0 then 'No'
                when 1 then 'Yes'
            end,
            case deleted
                when 0 then ''
                when 1 then 'Yes'
            end
            from downloads
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
                
                    data_list.append((last_mod_date,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],file_found))
            db.close()
                    
        else:
            continue
        
    data_headers = (('Modified/Downloaded Timestamp','datetime'),'Title','Description','Provider URI','Save Location','Mime Type','App Provider Package','Current Bytes','Total Bytes','Status','Error Message','ETAG','Visible in Downloads UI','Deleted','Source File')    
    return data_headers, data_list, 'See source file(s) below'