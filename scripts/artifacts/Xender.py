# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_Xender": {
        "name": "Xender - Contacts",
        "description": "",
        "author": "",
        "creation_date": "2020-12-24",
        "last_update_date": "2020-12-24",
        "requirements": "none",
        "category": "File Transfer",
        "notes": "",
        "paths": ('*/cn.xender/databases/trans-history-db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
    },
    "get_Xender_messages": {
        "name": "Xender - Messages",
        "description": "",
        "author": "",
        "creation_date": "2020-12-24",
        "last_update_date": "2020-12-24",
        "requirements": "none",
        "category": "File Transfer",
        "notes": "",
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
def get_Xender(files_found, report_folder, seeker, wrap_text):
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
def get_Xender_messages(files_found, report_folder, seeker, wrap_text):
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
            from_id = ''
            to_id = ''
            if row[4] == 1:
                direction = 'Outgoing'
                to_id = row[6]
            else:
                direction = 'Incoming'
                from_id = row[6]
            createtime = datetime.datetime.fromtimestamp(int(row[3]) / 1000, datetime.timezone.utc) if row[3] else ''
            data_list.append((row[0], row[1], row[2], createtime, direction, to_id, from_id, row[5], row[6], row[7], row[8], row[9]))

    data_headers = ('file_path', 'file_display_name', 'file_size', ('timestamp', 'datetime'), 'direction', 'to_id',
                    'from_id', 'session_id', 'sender_name', 'sender_device_id', 'recipient_name', 'recipient_device_id')
    return data_headers, data_list, source_path
