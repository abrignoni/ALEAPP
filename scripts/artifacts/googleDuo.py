# pylint: disable=W0613
__artifacts_v2__ = {
    "get_googleDuo": {
        "name": "Google Duo - Call History",
        "description": "Google Duo / Meet call history",
        "author": "",
        "creation_date": "2021-07-28",
        "last_update_date": "2021-07-28",
        "requirements": "none",
        "category": "Google Duo",
        "notes": "",
        "paths": ('*/com.google.android.apps.tachyon/databases/tachyon.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    },
    "get_googleDuo_contacts": {
        "name": "Google Duo - Contacts",
        "description": "Google Duo / Meet contacts",
        "author": "",
        "creation_date": "2021-07-28",
        "last_update_date": "2021-07-28",
        "requirements": "none",
        "category": "Google Duo",
        "notes": "",
        "paths": ('*/com.google.android.apps.tachyon/databases/tachyon.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_googleDuo_notes": {
        "name": "Google Duo - Notes",
        "description": "Google Duo / Meet notes (media messages)",
        "author": "",
        "creation_date": "2021-07-28",
        "last_update_date": "2021-07-28",
        "requirements": "none",
        "category": "Google Duo",
        "notes": "",
        "paths": ('*/com.google.android.apps.tachyon/databases/tachyon.db*',
                  '*/com.google.android.apps.tachyon/files/media/*.*'),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _us_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _tachyon_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('tachyon.db'):
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


@artifact_processor
def get_googleDuo(files_found, report_folder, seeker, wrap_text):
    source_path = _tachyon_db(files_found)
    rows = _run(source_path, '''
        SELECT timestamp_usec, substr(self_id, 0, instr(self_id, '|')),
        substr(other_id, 0, instr(other_id, '|')), duo_users.contact_display_name,
        CASE activity_type WHEN 1 THEN 'Call' WHEN 2 THEN 'Note' WHEN 4 THEN 'Reaction' END,
        CASE call_state WHEN 0 THEN 'Left Message' WHEN 1 THEN 'Missed Call' WHEN 2 THEN 'Answered' WHEN 4 THEN '' END,
        CASE outgoing WHEN 0 THEN 'Incoming' WHEN 1 THEN 'Outgoing' END
        FROM activity_history
        LEFT JOIN duo_users ON duo_users.user_id = substr(other_id, 0, instr(other_id, '|'))
    ''')
    data_list = [(_us_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Local User', 'Remote User', 'Contact Name',
                    'Activity Type', 'Call Status', 'Direction')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleDuo_contacts(files_found, report_folder, seeker, wrap_text):
    source_path = _tachyon_db(files_found)
    rows = _run(source_path, '''
        SELECT system_contact_last_update_millis, contact_display_name, user_id,
        contact_phone_type_custom, contact_id
        FROM duo_users ORDER BY contact_id
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4]) for r in rows]
    data_headers = (('Last Updated Timestamp', 'datetime'), 'Contact Name', 'Contact Info',
                    'Contact Label', 'Contact ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleDuo_notes(files_found, report_folder, seeker, wrap_text):
    source_path = _tachyon_db(files_found)
    rows = _run(source_path, '''
        SELECT sent_timestamp_millis, received_timestamp_millis, seen_timestamp_millis,
        sender_id, recipient_id, content_uri,
        replace(content_uri, rtrim(content_uri, replace(content_uri, '/', '')), ''),
        content_size_bytes,
        CASE saved_status WHEN 0 THEN '' WHEN 1 THEN 'Yes' END
        FROM messages
    ''')
    data_list = []
    for r in rows:
        file_name = r[6]
        content = ''
        if file_name:
            match = next((str(f) for f in files_found if file_name in str(f)
                          and not str(f).endswith('.db')), None)
            if match:
                content = check_in_media(match, os.path.basename(match))
        data_list.append((_ms_to_utc(r[0]), _ms_to_utc(r[1]), _ms_to_utc(r[2]), r[3], r[4], content, r[7], r[8]))

    data_headers = (('Sent Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    ('Viewed Timestamp', 'datetime'), 'Sender', 'Recipient', ('Content', 'media'),
                    'Size', 'File Saved')
    return data_headers, data_list, source_path
