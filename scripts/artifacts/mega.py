__artifacts_v2__ = {
    "get_mega": {
        "name": "mega",
        "description": "Rows of the history table of MEGA's karere database, with the sender's email where the contacts table has it, the message type and the attachment name",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2021-01-31",
        "last_update_date": "2026-10-09",
        "requirements": "None",
        "category": "Mega",
        "notes": ""
                 "Message Type is labelled from the stored history.type using MEGAchat's message "
                 "type constants "
                 "(https://github.com/meganz/MEGAchat/blob/e5168cf8adead1bd7f2c505275d827face02f3d3/src/chatdMsg.h#L588-L609): "
                 "1 kMsgNormal is shown as Chat Message, 2 kMsgAlterParticipants as Participants "
                 "Changed, 6 kMsgCallEnd as Call Ended, 7 kMsgCallStarted as Call Started and 101 "
                 "kMsgAttachment as Attachment. Which change of participants a type 2 row records "
                 "is not decoded. Any other stored type is shown blank in Message Type. Type (As "
                 "Stored) holds history.type as the database returns it on every row.",
        "paths": ('*/mega.privacy.android.app/karere-*.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | mega.privacy.android.app vc 261630858 | 20 rows",
            "pixel7a_a14": "Android 14 | mega.privacy.android.app vc 241780257 | 83 rows",
        },
    }
}

# MEGA
# Author:  Kevin Pagano (@stark4n6)
# Website: stark4n6.com
# Date 2021-01-31
# Version: 0.1
# Requirements:  None

import json

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def get_mega(context):
    files_found = unique_files(context)
    data_list = []
    source_paths = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue  # Skip all other files

        source_paths.append(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(history.ts,'unixepoch'),
        contacts.email,
        CASE history.type
            WHEN 1 THEN 'Chat Message'
            WHEN 2 THEN 'Participants Changed'
            WHEN 6 THEN 'Call Ended'
            WHEN 7 THEN 'Call Started'
            WHEN 101 THEN 'Attachment'
        END AS Type,
        history.data,
        history.type
        FROM history
        LEFT JOIN contacts ON contacts.userid = history.userid
        ORDER BY history.ts ASC
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            attachment_name = ''
            chat_message = ''
            if row[2] == 'Chat Message':
                chat_contents = row[3]
                chat_message = chat_contents[0:]
                chat_message = (str(chat_message)[2:-1])

                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],chat_message,attachment_name,row[4]))

            elif row[2] == 'Attachment':
                json_contents = row[3]
                json_string = json_contents[2:]
                json_string = (str(json_string)[2:-1])

                json_export = json.loads(json_string)

                attachment_name = json_export[0]['name']

                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],chat_message,attachment_name,row[4]))
            else:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],chat_message,attachment_name,row[4]))

        db.close()

    data_headers = (
        ('Message Timestamp', 'datetime'),
        'Sender',
        'Message Type',
        'Chat Message',
        'Attachment Name',
        'Type (As Stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)
