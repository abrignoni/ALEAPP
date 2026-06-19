# pylint: disable=W0613
__artifacts_v2__ = {
    "get_mega": {
        "name": "mega",
        "description": "MEGA",
        "author": "Kevin Pagano (@KevinPagano3)",
        "creation_date": "2021-01-31",
        "last_update_date": "2021-01-31",
        "requirements": "None",
        "category": "Mega",
        "notes": "",
        "paths": ('*/mega.privacy.android.app/karere-*.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

# MEGA
# Author:  Kevin Pagano (@KevinPagano3)
# Website: stark4n6.com
# Date 2021-01-31
# Version: 0.1
# Requirements:  None

import json

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_mega(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue  # Skip all other files

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(history.ts,'unixepoch'),
        contacts.email,
        CASE history.type
            WHEN 1 THEN 'Chat Message'
            WHEN 2 THEN 'Joined the group chat'
            WHEN 6 THEN 'Group Call Ended'
            WHEN 7 THEN 'Group Call Started'
            WHEN 101 THEN 'Attachment'
        END AS Type,
        history.data
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

                data_list.append((row[0],row[1],row[2],chat_message,attachment_name))

            elif row[2] == 'Attachment':
                json_contents = row[3]
                json_string = json_contents[2:]
                json_string = (str(json_string)[2:-1])

                json_export = json.loads(json_string)

                attachment_name = json_export[0]['name']

                data_list.append((row[0],row[1],row[2],chat_message,attachment_name))
            else:
                data_list.append((row[0],row[1],row[2],chat_message,attachment_name))

        db.close()

    data_headers = (
        ('Message Timestamp', 'datetime'),
        'Sender',
        'Message Type',
        'Chat Message',
        'Attachment Name',
    )
    return data_headers, data_list, source_path
