# pylint: disable=W0613
__artifacts_v2__ = {
    "get_likee": {
        "name": "LIKEE - User Location",
        "description": "Address/location text recovered from LIKEE *_location.kv files",
        "author": "",
        "creation_date": "2024-05-20",
        "last_update_date": "2024-05-20",
        "requirements": "none",
        "category": "LIKEE",
        "notes": "",
        "paths": ('*/video.like/files/*/*location.kv',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "get_likee_users": {
        "name": "LIKEE - Users",
        "description": "LIKEE user search history (like_pub.db)",
        "author": "",
        "creation_date": "2024-05-20",
        "last_update_date": "2024-05-20",
        "requirements": "none",
        "category": "LIKEE",
        "notes": "",
        "paths": ('*/video.like/databases/like_pub.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_likee_messages": {
        "name": "LIKEE - Messages",
        "description": "LIKEE messages (message_u*.db)",
        "author": "",
        "creation_date": "2024-05-20",
        "last_update_date": "2024-05-20",
        "requirements": "none",
        "category": "LIKEE",
        "notes": "",
        "paths": ('*/video.like/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime
import itertools
import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_CONTROL_RE = re.compile('[%s]' % re.escape(
    ''.join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0))))))


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_likee(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_location.kv'):
            continue
        source_path = file_found
        location_text = ''
        try:
            with open(file_found, 'r', errors='ignore', encoding='utf-8') as handle:
                for line in handle:
                    if 'address' in line:
                        cleaned = line[:line.find('address', 0, 6)].replace('\uFFFD\u2660', ' ')
                        location_text += _CONTROL_RE.sub('', cleaned)
        except OSError:
            pass
        data_list.append((os.path.basename(file_found), location_text, file_found))

    data_headers = ('File', 'Location Data', 'Source')
    return data_headers, data_list, source_path


@artifact_processor
def get_likee_users(files_found, report_folder, seeker, wrap_text):
    source_path = next((str(f) for f in files_found if 'like_pub.db' in str(f)
                        and not str(f).endswith(('-wal', '-shm'))), '')
    rows = _run(source_path, '''
        SELECT history_user_name, history_user_bigo_id, history_user_uid FROM user_search_history
    ''')
    data_headers = ('Users', 'Username', 'User ID')
    return data_headers, [tuple(r) for r in rows], source_path


@artifact_processor
def get_likee_messages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'message_u' not in file_found or file_found.endswith(('-wal', '-shm')):
            continue
        source_path = file_found
        for row in _run(file_found, 'SELECT uid, content, time FROM messages'):
            data_list.append((row[0], row[1], _ms_to_utc(row[2])))

    data_headers = ('User ID', 'Message Content', ('Timestamp', 'datetime'))
    return data_headers, data_list, source_path
