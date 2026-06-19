# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_shareit": {
        "name": "shareit",
        "description": "",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "File Transfer",
        "notes": "",
        "paths": ('*/com.lenovo.anyshare.gps/databases/history.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_shareit(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('history.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT case history_type when 1 then "Incoming" else "Outgoing" end direction,
                       case history_type when 1 then device_id else null end from_id,
                       case history_type when 1 then null else device_id end to_id,
                       device_name, description, timestamp/1000 as timestamp, file_path
                                        FROM history
                                        JOIN item where history.content_id = item.item_id
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[5]), datetime.timezone.utc) if row[5] else ''
            data_list.append((row[0], row[1], row[2], row[3], row[4], timestamp, row[6]))

    data_headers = ('direction', 'from_id', 'to_id', 'device_name', 'description', ('timestamp', 'datetime'), 'file_path')
    return data_headers, data_list, source_path
