# pylint: disable=W0718
__artifacts_v2__ = {
    "get_shareit": {
        "name": "shareit",
        "description": "Parses SHAREit file transfer history (timestamp, the stored history_type and device_id, device name, description and file path) from the SHAREit history.db.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("history_type and device_id are the history table columns of those names, "
                  "reported as stored. What each history_type value means, and whether device_id "
                  "names the sending or the receiving device, is not established here, so no "
                  "direction label is assigned. timestamp is the stored value read as Unix "
                  "milliseconds and shown in UTC. Only history rows whose content_id matches an "
                  "item row are reported."),
        "paths": ('*/com.lenovo.anyshare.gps/databases/history.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_shareit(context):
    files_found = context.get_files_found()

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
                SELECT timestamp/1000 as timestamp, history_type, device_id,
                       device_name, description, file_path
                                        FROM history
                                        JOIN item where history.content_id = item.item_id
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4], row[5]))

    data_headers = (('timestamp', 'datetime'), 'history_type', 'device_id', 'device_name', 'description', 'file_path')
    return data_headers, data_list, source_path
