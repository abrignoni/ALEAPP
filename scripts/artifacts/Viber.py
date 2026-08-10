# pylint: disable=W0718
__artifacts_v2__ = {
    "get_Viber": {
        "name": "Viber - Call Logs",
        "description": "Parses Viber call logs (timestamp, phone number, direction, duration and call type) from the Viber databases.",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Viber",
        "notes": ("Call Direction is decoded from the calls table 'type' column. Direction/status "
                  "value mappings were established through testing; unrecognized values are "
                  "reported as stored, so a value the mapping does not cover (a missed, rejected or "
                  "unanswered call, for example) appears as the stored number rather than as a "
                  "direction.\n"
                  "Call End Time is not stored by the app: it is start time plus the duration "
                  "column, which is treated as whole seconds."),
        "paths": ('*/com.viber.voip/databases/*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.viber.voip vc 1281010 | 0 rows",
            "pixel7a_a14": "Android 14 | com.viber.voip vc 1231070 | 0 rows",
            "sharon_a14": "Android 14 | com.viber.voip vc 1233020 | 0 rows",
        },
    },
    "get_Viber_contacts": {
        "name": "Viber - Contacts",
        "description": "Parses Viber contacts (display name and phone number) from the Viber databases.",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2020-12-24",
        "requirements": "none",
        "category": "Viber",
        "notes": "",
        "paths": ('*/com.viber.voip/databases/*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.viber.voip vc 1281010 | 0 rows",
            "pixel7a_a14": "Android 14 | com.viber.voip vc 1231070 | 0 rows",
            "sharon_a14": "Android 14 | com.viber.voip vc 1233020 | 0 rows",
        },
    },
    "get_Viber_messages": {
        "name": "Viber - Messages",
        "description": "Parses Viber messages (date, sender and recipients, thread, content, direction, unread flag and attachments) from the Viber databases.",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Viber",
        "notes": ("Direction is decoded from the messages table 'send_type' column. Direction/status "
                  "value mappings were established through testing; unrecognized values are reported "
                  "as stored.\n"
                  "In the conversation view only rows labelled Outgoing are shown as sent by the "
                  "device owner; a row whose direction value is blank or unrecognized is not "
                  "attributed to the owner.\n"
                  "Unread carries the messages table 'unread' column as stored; it is not a "
                  "read flag."),
        "paths": ('*/com.viber.voip/databases/*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.viber.voip vc 1281010 | 17 rows",
            "pixel7a_a14": "Android 14 | com.viber.voip vc 1231070 | 34 rows",
            "sharon_a14": "Android 14 | com.viber.voip vc 1233020 | 5051 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Date",
                "senderColumn": "From Phone Number"
            }
        },
    },
    "get_Viber_additional": {
        "name": "Viber - Additional",
        "description": "Hidden chat PIN (brute-forced from the stored hash)",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2020-12-24",
        "requirements": "none",
        "category": "Viber",
        "notes": "",
        "paths": ('*/com.viber.voip/databases/*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "lock",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.viber.voip vc 1281010 | 0 rows",
            "pixel7a_a14": "Android 14 | com.viber.voip vc 1231070 | 0 rows",
            "sharon_a14": "Android 14 | com.viber.voip vc 1233020 | 0 rows",
        },
    }
}

import datetime
import os
from hashlib import sha256

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _viber_dbs(files_found):
    """Pick the three Viber stores by exact name.

    The glob returns every file in the databases directory, and matching on a
    suffix is not selective enough: viberpay_data and viber_unicode_emoji_data
    also end in "_data", so the last one seen won and the queries ran against
    the wrong store.
    """
    wanted = {'viber_data': '', 'viber_messages': '', 'viber_prefs': ''}
    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name in wanted and not wanted[name]:
            wanted[name] = file_found
    return wanted['viber_data'], wanted['viber_messages'], wanted['viber_prefs']


@artifact_processor
def get_Viber(context):
    files_found = context.get_files_found()
    data_db, _, _ = _viber_dbs(files_found)
    data_list = []
    if data_db:
        db = open_sqlite_db_readonly(data_db)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT date, canonized_number,
                case type when 1 then "Incoming" when 2 then "Outgoing" else type end AS direction,
                duration,
                case viber_call_type when 1 then "Audio Call" when 4 then "Video Call" else "Unknown" end AS viber_call_type
                FROM calls
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        for r in all_rows:
            start = _ms_to_utc(r[0])
            end = _ms_to_utc(int(r[0]) + int(r[3]) * 1000) if r[0] else ''
            data_list.append((start, r[1], r[2], end, r[4]))

    data_headers = (('Call Start Time', 'datetime'), ('Phone Number', 'phonenumber'), 'Call Direction', ('Call End Time (computed: start + duration)', 'datetime'), 'Call Type')
    return data_headers, data_list, data_db


@artifact_processor
def get_Viber_contacts(context):
    files_found = context.get_files_found()
    data_db, _, _ = _viber_dbs(files_found)
    data_list = []
    if data_db:
        db = open_sqlite_db_readonly(data_db)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT C.display_name, coalesce(D.data2, D.data1, D.data3) as phone_number
                FROM phonebookcontact AS C
                JOIN phonebookdata AS D ON C._id = D.contact_id
            ''')
            data_list = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
        db.close()

    data_headers = ('Display Name', ('Phone Number', 'phonenumber'))
    return data_headers, data_list, data_db


@artifact_processor
def get_Viber_messages(context):
    files_found = context.get_files_found()
    _, messages_db, _ = _viber_dbs(files_found)
    data_list = []
    if messages_db:
        db = open_sqlite_db_readonly(messages_db)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT M.msg_date, convo_participants.from_number AS from_number,
                convo_participants.recipients AS recipients, M.conversation_id AS thread_id, M.body AS msg_content,
                case M.send_type when 0 then "Incoming" when 1 then "Outgoing" else M.send_type end AS direction,
                M.unread read_status, M.extra_uri AS file_attachment
                FROM   (SELECT *, group_concat(TO_RESULT.number) AS recipients
                        FROM   (SELECT P._id AS FROM_ID, P.conversation_id, PI.number AS FROM_NUMBER
                                FROM   participants AS P JOIN participants_info AS PI ON P.participant_info_id = PI._id) AS FROM_RESULT
                               JOIN (SELECT P._id AS TO_ID, P.conversation_id, PI.number
                                     FROM   participants AS P JOIN participants_info AS PI ON P.participant_info_id = PI._id) AS TO_RESULT
                                 ON FROM_RESULT.from_id != TO_RESULT.to_id AND FROM_RESULT.conversation_id = TO_RESULT.conversation_id
                        GROUP  BY FROM_RESULT.from_id) AS convo_participants
                       JOIN messages AS M ON M.participant_id = convo_participants.from_id AND M.conversation_id = convo_participants.conversation_id
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        for r in all_rows:
            data_list.append((_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7]))

    data_headers = (('Message Date', 'datetime'), ('From Phone Number', 'phonenumber'), 'Recipients', 'Thread ID', 'Message', 'Direction', 'Unread', 'File Attachment')
    return data_headers, data_list, messages_db


@artifact_processor
def get_Viber_additional(context):
    files_found = context.get_files_found()
    _, _, prefs_db = _viber_dbs(files_found)
    data_list = []
    if prefs_db:
        db = open_sqlite_db_readonly(prefs_db)
        cursor = db.cursor()
        try:
            cursor.execute("SELECT key, value from kvdata WHERE key='key_hidden_chats_pin'")
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        if all_rows:
            userPINHash = all_rows[0][1]
            currentPIN = 'Not recovered'
            for i in range(0, 10000):
                candidate = ('{0:04}'.format(i)).encode('utf-8')
                if sha256(candidate + "Shawl9_Valid_Yeastv".encode("utf-8")).hexdigest() == userPINHash:
                    currentPIN = candidate.decode("utf-8")
                    break
            data_list = [(userPINHash, currentPIN)]

    data_headers = ('User PIN Hash', 'User PIN')
    return data_headers, data_list, prefs_db
