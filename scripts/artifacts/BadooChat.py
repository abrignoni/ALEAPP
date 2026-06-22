# pylint: disable=W0613
__artifacts_v2__ = {
    "get_badoo_chat": {
        "name": "Badoo - Users",
        "description": "Badoo matched users / conversations (com.badoo.mobile)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-05-03",
        "last_update_date": "2023-05-03",
        "requirements": "none",
        "category": "Badoo",
        "notes": "",
        "paths": ('*com.badoo.mobile/databases/ChatComDatabase*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_badoo_messages": {
        "name": "Badoo - Messages",
        "description": "Badoo chat messages (com.badoo.mobile)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-05-03",
        "last_update_date": "2023-05-03",
        "requirements": "none",
        "category": "Badoo",
        "notes": "",
        "paths": ('*com.badoo.mobile/databases/ChatComDatabase*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime
import json
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_GENDER = {0: 'Male', 1: 'Female'}


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if 'ChatComDatabase' in file_found and not file_found.endswith('-journal'):
            return file_found
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


def _photo_urls(raw):
    try:
        photos = json.loads(raw)
    except (ValueError, TypeError):
        return ''
    if not isinstance(photos, list):
        return ''
    return '\n'.join(p.get('url', '') for p in photos if isinstance(p, dict))


def _msg_text(ptype, raw):
    try:
        text = json.loads(raw)
    except (ValueError, TypeError):
        return raw if isinstance(raw, str) else ''
    if not isinstance(text, dict):
        return str(text)
    if ptype == 'TEXT':
        return text.get('text', '')
    if ptype == 'QUESTION_GAME':
        msg = text.get('text', '')
        if 'answer_own' in text:
            msg += ';Own Answer:' + str(text['answer_own'])
        if 'answer_other' in text:
            msg += ';Other Answer:' + str(text['answer_other'])
        return msg
    if ptype in ('INSTANT_VIDEO', 'AUDIO', 'IMAGE'):
        return text.get('url', '')
    # unknown type: best-effort (the original left message_text undefined here)
    return text.get('text') or text.get('url') or json.dumps(text, ensure_ascii=False)


@artifact_processor
def get_badoo_chat(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT user_id, gender, user_name, user_image_url, age, user_photos, work, education,
               encrypted_user_id
        FROM conversation_info
    ''')
    data_list = []
    for r in rows:
        data_list.append((r[0], _GENDER.get(r[1], 'Other'), r[2], r[3], r[4], _photo_urls(r[5]),
                          r[6], r[7], r[8]))
    data_headers = ('User ID', 'Gender', 'User Name', 'User Image URL', 'Age', 'User Photos',
                    'Work', 'Education', 'Encrypted User ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_badoo_messages(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    users = {r[0]: r[1] for r in
             _run(source_path, 'SELECT encrypted_user_id, user_name FROM conversation_info')}
    data_list = []
    for r in _run(source_path,
                  'SELECT sender_id, recipient_id, created_timestamp, payload, payload_type FROM message'):
        partner = users.get(r[0]) or users.get(r[1]) or ''
        data_list.append((_ms_to_utc(r[2]), partner, r[0], r[1], r[4], _msg_text(r[4], r[3])))
    data_headers = (('Timestamp', 'datetime'), 'Conversation With', 'Sender ID', 'Recipient ID',
                    'Type', 'Message')
    return data_headers, data_list, source_path
