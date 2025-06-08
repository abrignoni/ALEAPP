__artifacts_v2__ = {
    
    "duckduckgo_history": {
        "name": "DuckDuckGo Web Browser History",
        "description": "Parses DuckDuckGo Web Browsing History",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-05-21",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.237.0 (June, 3rd 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/history.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    }
}
   
import sqlite3
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, get_sqlite_db_records

@artifact_processor
def duckduckgo_history(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break
            
    query = '''
        SELECT  
            visits_list.rowid,
            history_entries.url,
            history_entries.title, 
            REPLACE(visits_list.timestamp, 'T', ' ') AS 'Visit Date (Local)',
            CASE history_entries.isSerp 
                WHEN 1 THEN 'DuckDuckGo Search'
                WHEN 0 THEN 'Web Page Visit' 
            END AS 'History Type', 
            history_entries.query
        FROM visits_list 
        LEFT JOIN history_entries ON visits_list.historyEntryId = history_entries.id;
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

    data_headers = ('Visit ID','URL','Title','Visit Date (Local)','History Type','Search Query') 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path