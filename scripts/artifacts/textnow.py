# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_textnow_call_logs": {
        "name": "Text Now - Call Logs",
        "description": "Parses TextNow call logs (start and end time, participant IDs and direction) from the TextNow textnow_data.db.",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Text Now",
        "notes": "",
        "paths": ('*/com.enflick.android.TextNow/databases/textnow_data.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    },
    "get_textnow_messages": {
        "name": "Text Now - Messages",
        "description": "Parses TextNow messages (timestamp, sender and recipient IDs, direction, message, read state and attachments) from the TextNow textnow_data.db.",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Text Now",
        "notes": "",
        "paths": ('*/com.enflick.android.TextNow/databases/textnow_data.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
    },
    "get_textnow_contacts": {
        "name": "Text Now - Contacts",
        "description": "Parses TextNow contacts (number and name) from the TextNow textnow_data.db.",
        "author": "",
        "creation_date": "2021-03-15",
        "last_update_date": "2021-03-15",
        "requirements": "none",
        "category": "Text Now",
        "notes": "",
        "paths": ('*/com.enflick.android.TextNow/databases/textnow_data.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_textnow_call_logs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('textnow_data.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            try:
                cursor.execute('''
                    SELECT contact_value     AS num,
                           case message_direction when 2 then "Outgoing" else "Incoming" end AS direction,
                            date/1000 + message_text      AS duration,
                            date/1000              AS datetime
                      FROM  messages AS M
                     WHERE  message_type IN ( 100, 102 )
                ''')
                all_rows = cursor.fetchall()
            except:
                all_rows = []

            for row in all_rows:
                phone_number_from = None
                phone_number_to = None
                if row[1] == "Outgoing":
                    phone_number_to = row[0]
                else:
                    phone_number_from = row[0]
                starttime = datetime.datetime.fromtimestamp(int(row[3]), datetime.timezone.utc)
                endtime = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)
                data_list.append((starttime, endtime, phone_number_from, phone_number_to, row[1]))

            db.close()

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        ('From ID', 'phonenumber'),
        ('To ID', 'phonenumber'),
        'Call Direction',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_textnow_messages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('textnow_data.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            try:
                cursor.execute('''
                    SELECT CASE
                             WHEN messages.message_direction == 2 THEN NULL
                             WHEN contact_book_w_groups.to_addresses IS NULL THEN
                             messages.contact_value
                           END from_address,
                           CASE
                             WHEN messages.message_direction == 1 THEN NULL
                             WHEN contact_book_w_groups.to_addresses IS NULL THEN
                             messages.contact_value
                             ELSE contact_book_w_groups.to_addresses
                           END to_address,
                           CASE messages.message_direction
                             WHEN 1 THEN "Incoming"
                             ELSE "Outgoing"
                           END message_direction,
                           messages.message_text,
                           messages.READ,
                           messages.DATE/1000,
                           messages.attach,
                           thread_id
                    FROM   (SELECT GM.contact_value,
                                   Group_concat(GM.member_contact_value) AS to_addresses,
                                   G.contact_value                       AS thread_id
                            FROM   group_members AS GM
                                   join GROUPS AS G
                                     ON G.contact_value = GM.contact_value
                            GROUP  BY GM.contact_value
                            UNION
                            SELECT contact_value,
                                   NULL,
                                   NULL
                            FROM   contacts) AS contact_book_w_groups
                           join messages
                             ON messages.contact_value = contact_book_w_groups.contact_value
                    WHERE  message_type NOT IN ( 102, 100 )
                ''')
                all_rows = cursor.fetchall()
            except:
                all_rows = []

            for row in all_rows:
                sendtime = datetime.datetime.fromtimestamp(int(row[5]), datetime.timezone.utc)

                data_list.append((sendtime, row[7], row[0], row[1], row[2], row[3], row[4],  row[6]))

            db.close()

    data_headers = (
        ('Send Timestamp', 'datetime'),
        'Message ID',
        'From ID',
        'To ID',
        'Direction',
        'Message',
        'Read',
        'Attachment',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_textnow_contacts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('textnow_data.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            try:
                cursor.execute('''
                     SELECT C.contact_value AS number,
                            CASE
                              WHEN contact_name IS NULL THEN contact_value
                              WHEN contact_name == "" THEN contact_value
                              ELSE contact_name
                            END             name
                     FROM   contacts AS C        ''')
                all_rows = cursor.fetchall()
            except:
                all_rows = []

            for row in all_rows:
                data_list.append((row[0], row[1]))

            db.close()

    data_headers = (('number', 'phonenumber'), 'name')
    return data_headers, data_list, source_path
