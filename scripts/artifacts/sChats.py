# pylint: disable=W0613,W0631
__artifacts_v2__ = {
    "get_schats": {
        "name": "Sideline Chats and Calls",
        "description": "Parses Sideline's textfree database",
        "author": "Matt Beers",
        "creation_date": "2024-02-08",
        "last_update_date": "2024-02-08",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/data/com.sideline.phone.number/databases/textfree*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_schats(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('textfree'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(conversation_item.timestamp / 1000, 'unixepoch', 'localtime') AS TIMESTAMP,
            contact_address.native_first_name,
            contact_address.native_last_name,
            CASE conversation_item.method
            WHEN '1' THEN 'Text'
            WHEN '3' THEN 'Call'
            WHEN '8' THEN 'Voicemail'
            ELSE 'Unknown'
            END AS method,
            conversation_item.message_text,
            conversation_item.duration,
            conversation_item.address
            FROM
            contact_address
            JOIN
            conversation_item ON contact_address.address_e164 = conversation_item.address
            ORDER BY
            conversation_item.timestamp DESC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
            db.close()

        else:
            continue

    data_headers = (
        ('Timestamp', 'datetime'),
        'First Name',
        'Last Name',
        'Method',
        'Message Text',
        'Duration',
        ('Phone Number', 'phonenumber'),
    )
    return data_headers, data_list, source_path
