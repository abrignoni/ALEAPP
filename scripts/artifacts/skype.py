# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_skype_call_logs": {
        "name": "Skype - Call Logs",
        "description": "",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Skype",
        "notes": "",
        "paths": ('*/com.skype.raider/databases/live*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    },
    "get_skype_messages": {
        "name": "Skype - Messages",
        "description": "",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Skype",
        "notes": "",
        "paths": ('*/com.skype.raider/databases/live*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Send Time",
                "senderColumn": "From ID"
            }
        },
    },
    "get_skype_contacts": {
        "name": "Skype - Contacts",
        "description": "",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Skype",
        "notes": "",
        "paths": ('*/com.skype.raider/databases/live*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _skype_db(files_found):
    for file_found in files_found:
        file_name = str(file_found)
        if ('live' in file_name.lower()) and ('db-journal' not in file_name.lower()):
            return str(file_found)
    return None


@artifact_processor
def get_skype_call_logs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _skype_db(files_found) or ''
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                    SELECT
                           contact_book_w_groups.conversation_id,
                           contact_book_w_groups.participant_ids,
                           messages.time/1000 as start_date,
                           messages.time/1000 + messages.duration as end_date,
                           case messages.is_sender_me when 0 then "Incoming" else "Outgoing"
                           end is_sender_me,
                           messages.person_id AS sender_id
                    FROM   (SELECT conversation_id,
                                   Group_concat(person_id) AS participant_ids
                            FROM   particiapnt
                            GROUP  BY conversation_id
                            UNION
                            SELECT entry_id AS conversation_id,
                                   NULL
                            FROM   person) AS contact_book_w_groups
                           join chatitem AS messages
                             ON messages.conversation_link = contact_book_w_groups.conversation_id
                    WHERE  message_type == 3
            ''')
            all_rows = cursor.fetchall()
        except:
            all_rows = []

        for row in all_rows:
            to_id = None
            if row[4] == "Outgoing":
                if ',' in row[1]:
                    to_id = row[1]
                else:
                    to_id = row[0]
            starttime = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)
            endtime = datetime.datetime.fromtimestamp(int(row[3]), datetime.timezone.utc)
            data_list.append((starttime, endtime, row[5], to_id, row[4]))
        db.close()

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'From ID', 'To ID', 'Call Direction')
    return data_headers, data_list, source_path


@artifact_processor
def get_skype_messages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _skype_db(files_found) or ''
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                    SELECT contact_book_w_groups.conversation_id,
                           contact_book_w_groups.participant_ids,
                           messages.time/1000,
                           messages.content,
                           messages.device_gallery_path,
                           case messages.is_sender_me when 0 then "Incoming" else "Outgoing"
                           end is_sender_me,
                           messages.person_id
                           FROM   (SELECT conversation_id,
                                   Group_concat(person_id) AS participant_ids
                            FROM   particiapnt
                            GROUP  BY conversation_id
                            UNION
                            SELECT entry_id as conversation_id,
                                   NULL
                            FROM   person) AS contact_book_w_groups
                           JOIN chatitem AS messages
                             ON messages.conversation_link = contact_book_w_groups.conversation_id
                    WHERE message_type != 3
            ''')
            all_rows = cursor.fetchall()
        except:
            all_rows = []

        for row in all_rows:
            thread_id = None
            if row[1] is None:
                thread_id = row[0]
            to_id = None
            if row[5] == "Outgoing":
                if row[1] is None:
                    to_id = None
                elif ',' in row[1]:
                    to_id = row[1]
                else:
                    to_id = row[0]
            sendtime = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)

            data_list.append((sendtime, thread_id,  row[3], row[5], row[6], to_id, row[4]))
        db.close()

    data_headers = (('Send Time', 'datetime'), 'Thread ID', 'Content', 'Direction', 'From ID', 'To ID', 'Attachment')
    return data_headers, data_list, source_path


@artifact_processor
def get_skype_contacts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _skype_db(files_found) or ''
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                    SELECT entry_id,
                           CASE
                             WHEN Ifnull(first_name, "") == "" AND Ifnull(last_name, "") == "" THEN entry_id
                             WHEN first_name is NULL THEN replace(last_name, ",", "")
                             WHEN last_name is NULL THEN replace(first_name, ",", "")
                             ELSE replace(first_name, ",", "") || " " || replace(last_name, ",", "")
                           END AS name
                    FROM   person
            ''')
            all_rows = cursor.fetchall()
        except:
            all_rows = []

        for row in all_rows:
            data_list.append((row[0], row[1]))
        db.close()

    data_headers = ('Entry ID', 'Name')
    return data_headers, data_list, source_path
