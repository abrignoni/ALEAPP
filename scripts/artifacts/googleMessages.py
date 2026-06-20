# pylint: disable=W0613
__artifacts_v2__ = {
    "get_googleMessages": {
        "name": "GoogleMessages",
        "description": "Google Messages",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-01-30",
        "last_update_date": "2021-01-30",
        "requirements": "None",
        "category": "Google Messages",
        "notes": "",
        "paths": ('*/com.google.android.apps.messaging/databases/bugle_db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_googleMessages(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('bugle_db'):
            continue  # Skip all other files

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        parts.timestamp,
        parts.content_type AS "Message Type",
        conversations.name AS "Other Participant/Conversation Name",
        participants.display_destination AS "Message Sender",
        parts.text AS "Message",
        CASE
        WHEN parts.file_size_bytes=-1 THEN "N/A"
        ELSE parts.file_size_bytes
        END AS "Attachment Byte Size",
        parts.local_cache_path AS "Attachment Location"
        FROM
        parts
        JOIN messages ON messages._id=parts.message_id
        JOIN participants ON participants._id=messages.sender_id
        JOIN conversations ON conversations._id=parts.conversation_id
        ORDER BY parts.timestamp ASC
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4], row[5], row[6]))

    data_headers = (('Message Timestamp', 'datetime'), 'Message Type', 'Other Participant/Conversation Name', ('Message Sender', 'phonenumber'), 'Message', 'Attachment Byte Size', 'Attachment Location')
    return data_headers, data_list, source_path
