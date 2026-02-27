# Samsung Android History Log
# Author:  Alexis Brignoni (linqapp.com/abrignoni)


__artifacts_v2__ = {
    
    "history_log": {
        "name": "Samsung Knox History Log",
        "description": "Samsung Knox History Log",
        "author": "Alexis Brignoni {linqapp.com/abrignoni}",
        "version": "0.0.1",
        "creation_date": "2026-02-27",
        "last_update_date": "2025-02-27",
        "requirements": "sqlite",
        "category": "Samsung History Log",
        "notes": "",
        "paths": ('*/com.samsung.knox.securefolder/databases/history_log_database'),
        "output_types": ["standard"],
        "artifact_icon": "inbox"
    }
}
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

@artifact_processor
def history_log(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
     
    query = ('''
        SELECT 
        timestamp,
        id,
        tag,
        message
        FROM HistoryLog
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []

    for row in db_records:
        timestamp_str = row[0]
        # Parse as UTC
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        unix_timestamp = int(dt.timestamp())
        idd = row[1]
        tag = row[2]
        message = row[3]
        
        data_list.append(( unix_timestamp, idd, tag, message))

    data_headers = ( ('Timestamp', 'datetime'), 'ID', 'Tag', 'Message')

    return data_headers, data_list, files_found[0]


