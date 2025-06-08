__artifacts_v2__ = {
    
    "duckduckgo_opentabs": {
        "name": "DuckDuckGo Open Tabs",
        "description": "Parses DuckDuckGo Open Tab Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-05-21",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.237.0 (June, 3rd 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "book-open"
    }
}
   
import sqlite3
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_column_exist_in_db, get_sqlite_db_records, get_file_path

@artifact_processor
def duckduckgo_opentabs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = get_file_path(files_found, 'app.db')

    if does_column_exist_in_db(source_path, 'tabs', 'lastAccessTime'):
        query = '''
            SELECT  
                tabs.tabid,
                CASE 
                    WHEN tab_selection.tabid IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS 'Current Tab',
                tabs.title,
                tabs.url,
                tabs.tabPreviewFile,
                DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch','localtime') AS 'Cached Tab Preview Time (Local)',
                REPLACE(tabs.lastAccessTime, 'T', ' ') AS 'Tab Last Accessed (Local)'
            FROM tabs
            LEFT JOIN tab_selection ON tabs.tabid = tab_selection.tabid;
        '''
    else:
        query = '''
            SELECT  
                tabs.tabid,
                CASE 
                    WHEN tab_selection.tabid IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS 'Current Tab',
                tabs.title,
                tabs.url,
                tabs.tabPreviewFile,
                DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch','localtime') AS 'Cached Tab Preview Time (Local)',
                'Unavailable' AS 'Tab Last Accessed (Local)'
            FROM tabs
            LEFT JOIN tab_selection ON tabs.tabid = tab_selection.tabid;
        '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        data_list.append((
            row[0],  # Tab ID
            row[1],  # Current Tab
            row[2],  # Title
            row[3],  # URL
            row[6],  # Tab Last Accessed (Local)
            row[4],  # Cached Tab Filename
            row[5],  # Cached Tab Preview Time (Local)
        ))

    data_headers = (
        'Tab ID',
        'Current Tab',
        'Title',
        'URL',
        'Tab Last Accessed (Local)',
        'Cached Tab Filename',
        'Cached Tab Preview Time (Local)',
    )

    return data_headers, data_list, source_path

