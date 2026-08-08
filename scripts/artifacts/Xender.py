# pylint: disable=W0718
__artifacts_v2__ = {
    "get_Xender": {
        "name": "Xender - Contacts",
        "description": "Parses Xender contact profiles (device ID and nickname) from the Xender trans-history database.",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("The query returns only profile rows where connect_times = 0, so profiles with a "
                  "recorded connection count are not listed here."),
        "paths": ('*/cn.xender/databases/trans-history-db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
    },
    "get_Xender_messages": {
        "name": "Xender - Messages",
        "description": "Parses Xender file transfer history (file path, name, size, timestamp, direction and sender and recipient details) from the Xender trans-history database.",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("Direction is decoded from the new_history 'c_direction' column. Direction/status "
                  "value mappings were established through testing; unrecognized values are "
                  "reported as stored.\n"
                  "to_id and from_id carry the recipient and sender device IDs recorded on the same "
                  "row (r_device_id and s_device_id) and are left blank when the database does not "
                  "hold them. The sender and recipient name columns are names, not identifiers."),
        "paths": ('*/cn.xender/databases/trans-history-db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _xender_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('-db'):
            return file_found
    return ''


@artifact_processor
def get_Xender(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _xender_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('SELECT device_id, nick_name FROM profile WHERE connect_times = 0')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        for row in all_rows:
            data_list.append((row[0], row[1]))

    data_headers = ('device_id', 'nick_name')
    return data_headers, data_list, source_path


@artifact_processor
def get_Xender_messages(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _xender_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT f_path, f_display_name, f_size_str, c_start_time, c_direction, c_session_id, s_name,
                       s_device_id, r_name, r_device_id
                FROM new_history
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            # Only c_direction = 1 is identified; any other value is reported as stored.
            direction = {1: 'Outgoing'}.get(row[4], '' if row[4] is None else row[4])
            # The parties come from the row's own device ID columns rather than being
            # inferred from the direction value; s_name/r_name are names, not IDs.
            from_id = row[7] if row[7] else ''
            to_id = row[9] if row[9] else ''
            createtime = datetime.datetime.fromtimestamp(int(row[3]) / 1000, datetime.timezone.utc) if row[3] else ''
            data_list.append((row[0], row[1], row[2], createtime, direction, to_id, from_id, row[5], row[6], row[7], row[8], row[9]))

    data_headers = ('file_path', 'file_display_name', 'file_size', ('timestamp', 'datetime'), 'direction', 'to_id',
                    'from_id', 'session_id', 'sender_name', 'sender_device_id', 'recipient_name', 'recipient_device_id')
    return data_headers, data_list, source_path
