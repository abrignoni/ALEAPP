# pylint: disable=W0613
__artifacts_v2__ = {
    "get_lgRCS": {
        "name": "LG RCS Chats",
        "description": "RCS chat messages from LG phones (mmssms.db)",
        "author": "",
        "creation_date": "2021-01-06",
        "last_update_date": "2021-01-06",
        "requirements": "none",
        "category": "RCS Chats",
        "notes": "",
        "paths": ('*/mmssms.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db


def _ms_to_utc(value):
    if not value or int(value) <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _rcs_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != 'mmssms.db':  # skip -journal and other files
            continue
        if '.magisk' in file_found and 'mirror' in file_found:
            continue  # skip sbin/.magisk/mirror duplicate data
        return file_found
    return ''


@artifact_processor
def get_lgRCS(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _rcs_db(files_found)
    data_headers = (('Date', 'datetime'), 'Address', 'Body', 'Read?', 'Thread ID', 'Is File?',
                    'Filename', 'File Path', 'File Size', 'Thumb File Path', 'Thumb File Size',
                    'File XML Path')

    if source_path and does_table_exist_in_db(source_path, 'message'):
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT date, address, body, read, message.thread_id, is_file, file_name, file_path,
                       file_size, thumb_file_path, thumb_file_size, file_xml_path
                FROM message
                LEFT JOIN file_info ON message.message_id = file_info.message_id
                ORDER BY date
            ''')
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
        db.close()
        for r in rows:
            data_list.append((_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
                              r[9], r[10], r[11]))

    return data_headers, data_list, source_path
