# pylint: disable=W0613
__artifacts_v2__ = {
    "get_burnerMessages": {
        "name": "Burner - Messages",
        "description": "Parses Burner Messages",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!)",
        "version": "0.0.1",
        "creation_date": "2024-02-15",
        "last_update_date": "2026-07-02",
        "requirements": "none",
        "category": "Burner",
        "notes": "",
        "paths": ('*/data/com.adhoclabs.burner/databases/burnerDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Contact",
                "conversationLabelColumn": "Contact",
                "textColumn": "Message Text",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Contact",
                "sentMessageStaticLabel": "Local User"
            }
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_burnerMessages(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('burnerDatabase.db'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT
            json_extract(MessageEntity.value, '$.dateCreated') as Date_Created,
            json_extract(MessageEntity.value, '$.contactPhoneNumber') as Contact,
            json_extract(MessageEntity.value, '$.message') as Message,
            CASE json_extract(MessageEntity.value, '$.direction')
                WHEN 1 THEN 'Incoming'
                WHEN 2 THEN 'Outgoing'
                ELSE 'Unknown'
            END as Direction,
            CASE json_extract(MessageEntity.value, '$.read')
                WHEN 1 THEN 'True'
                WHEN 0 THEN 'False'
                ELSE 'Unknown'
            END as Read
            FROM MessageEntity
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            created = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((created, row[1], row[2], row[3], row[4]))

    data_headers = (('Timestamp', 'datetime'), ('Contact', 'phonenumber'), 'Message Text', 'Direction', 'Read Status')
    return data_headers, data_list, source_path
