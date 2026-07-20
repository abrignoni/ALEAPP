# pylint: disable=W0718
__artifacts_v2__ = {
    "get_line": {
        "name": "Line - Contacts",
        "description": "Parses LINE contacts (user ID and name) from the LINE databases.",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Line",
        "notes": "",
        "paths": ('*/jp.naver.line.android/databases/**',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | jp.naver.line.android vc 141220285 | 0 rows",
        },
    },
    "get_line_messages": {
        "name": "Line - Messages",
        "description": "Parses LINE messages (time, sender and recipient IDs, direction, thread, message and attachments) from the LINE databases.",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Line",
        "notes": "",
        "paths": ('*/jp.naver.line.android/databases/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | jp.naver.line.android vc 141220285 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Start Time",
                "senderColumn": "From ID"
            }
        },
    },
    "get_line_calls": {
        "name": "Line - Call Logs",
        "description": "Parses LINE call logs (start and end time, participant IDs, direction and call type) from the LINE databases.",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Line",
        "notes": "",
        "paths": ('*/jp.naver.line.android/databases/**',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "pixel7a_a14": "Android 14 | jp.naver.line.android vc 141220285 | 0 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


def _line_dbs(files_found):
    msg_db = call_db = ''
    for file_found in files_found:
        file_name = str(file_found).lower()
        if file_name.endswith('naver_line'):
            msg_db = str(file_found)
        elif file_name.endswith('call_history'):
            call_db = str(file_found)
    return msg_db, call_db


@artifact_processor
def get_line(context):
    files_found = context.get_files_found()
    msg_db, _ = _line_dbs(files_found)
    data_list = []
    if msg_db:
        db = open_sqlite_db_readonly(msg_db)
        cursor = db.cursor()
        try:
            cursor.execute('SELECT m_id, server_name FROM contacts')
            data_list = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
        db.close()

    data_headers = ('user_id', 'user_name')
    return data_headers, data_list, msg_db


@artifact_processor
def get_line_messages(context):
    files_found = context.get_files_found()
    msg_db, _ = _line_dbs(files_found)
    data_list = []
    if msg_db:
        db = open_sqlite_db_readonly(msg_db)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT contact_book_w_groups.id, contact_book_w_groups.members, messages.from_mid,
                       messages.content, messages.created_time/1000, messages.attachement_type,
                       messages.attachement_local_uri,
                       case messages.status when 1 then "Incoming" else "Outgoing" end status
                FROM   (SELECT id, Group_concat(M.m_id) AS members
                        FROM   membership AS M GROUP BY id
                        UNION
                        SELECT m_id, NULL FROM contacts) AS contact_book_w_groups
                       JOIN chat_history AS messages ON messages.chat_id = contact_book_w_groups.id
                WHERE  attachement_type != 6
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            thread_id = row[0] if row[1] is None else None
            to_id = None
            if row[7] == "Outgoing":
                if row[1] and ',' in row[1]:
                    to_id = row[1]
                else:
                    to_id = row[0]
            attachment = row[6]
            if attachment is None or 'content' in attachment:
                attachment = None
            created_time = _sec_to_utc(row[4])
            data_list.append((created_time, row[2], to_id, row[7], thread_id, row[3], attachment))

    data_headers = (('Start Time', 'datetime'), 'From ID', 'To ID', 'Direction', 'Thread ID', 'Message', 'Attachments')
    return data_headers, data_list, msg_db


@artifact_processor
def get_line_calls(context):
    files_found = context.get_files_found()
    msg_db, call_db = _line_dbs(files_found)
    data_list = []
    if call_db and msg_db:
        db = open_sqlite_db_readonly(call_db)
        cursor = db.cursor()
        cursor.execute('attach database "' + msg_db + '" as naver_line ')
        try:
            cursor.execute('''
                SELECT case Substr(calls.call_type, -1) when "O" then "Outgoing" else "Incoming" end AS direction,
                       calls.start_time/1000 AS start_time, calls.end_time/1000 AS end_time,
                       case when Substr(calls.call_type, -1) = "O" then contact_book_w_groups.members else null end AS group_members,
                       calls.caller_mid,
                       case calls.voip_type when "V" then "Video" when "A" then "Audio" when "G" then calls.voip_gc_media_type end AS call_type
                FROM   (SELECT id, Group_concat(M.m_id) AS members
                        FROM   membership AS M GROUP BY id
                        UNION
                        SELECT m_id, NULL FROM naver_line.contacts) AS contact_book_w_groups
                       JOIN call_history AS calls ON calls.caller_mid = contact_book_w_groups.id
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            data_list.append((_sec_to_utc(row[1]), _sec_to_utc(row[2]), row[3], row[4], row[0], row[5]))

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'To ID', 'From ID', 'Direction', 'Call Type')
    return data_headers, data_list, call_db
