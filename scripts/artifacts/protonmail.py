# pylint: disable=W0613
__artifacts_v2__ = {
    "get_protonmail_messages": {
        "name": "ProtonMail - Messages",
        "description": "",
        "author": "",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "",
        "paths": ('*/ch.protonmail.android/databases/*-MessagesDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "mail",
    },
    "get_protonmail_contacts": {
        "name": "ProtonMail - Contacts",
        "description": "",
        "author": "",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "",
        "paths": ('*/ch.protonmail.android/databases/*-ContactsDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "mail",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_protonmail_messages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)

        if file_name.lower().endswith(('-shm','-wal','-journal')):
            continue

        if file_name.endswith('-MessagesDatabase.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(messagev3.Time,'unixepoch') AS 'Message Timestamp',
            messagev3.Subject AS 'Subject',
            messagev3.Sender_SenderSerialized AS 'Sender',
            CASE messagev3.Type
                WHEN 0 THEN 'Incoming'
                WHEN 1 THEN 'Draft'
                WHEN 2 THEN 'Outgoing'
            END AS 'Message Direction',
            CASE messagev3.Unread
                WHEN 0 THEN 'Read'
                WHEN 1 THEN 'Unread'
            END AS 'Status',
            messagev3.Size AS 'Message Size',
            CASE messagev3.AccessTime
                WHEN 0 THEN ''
                ELSE datetime(messagev3.AccessTime/1000,'unixepoch')
            END AS 'Accessed Timestamp',
            CASE messagev3.Location
                WHEN 0 THEN 'Inbox'
                WHEN 1 THEN 'Drafts'
                WHEN 2 THEN 'Sent'
                WHEN 3 THEN 'Trash'
                WHEN 6 THEN 'Archive'
                WHEN 7 THEN '7 (TBD)'
            END AS 'Folder',
            CASE messagev3.Starred
                WHEN 0 THEN ''
                WHEN 1 THEN 'Yes'
            END AS 'Starred',
            messagev3.NumAttachments,
            attachmentv3.file_name AS 'Attachment Name',
            attachmentv3.file_size AS 'Attachment Size',
            messagev3.ToList AS 'To List',
            messagev3.ReplyTos AS 'Reply To',
            messagev3.CCList AS 'CC List',
            messagev3.BCCList AS 'BCC List',
            messagev3.Header AS 'Message Header'
            FROM messagev3
            LEFT JOIN attachmentv3 ON attachmentv3.message_id = messagev3.ID
            ORDER BY messagev3.Time ASC
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

            db.close()

    data_headers = (
        ('Message Timestamp', 'datetime'),
        'Subject',
        'Sender',
        'Message Direction',
        'Status',
        'Message Size',
        ('Accessed Timestamp', 'datetime'),
        'Folder',
        'Starred',
        'Number of Attachments',
        'Attachment Name',
        'Attachment Size',
        'To List',
        'Reply To',
        'CC List',
        'BCC List',
        'Message Header',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_protonmail_contacts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)

        if file_name.lower().endswith(('-shm','-wal','-journal')):
            continue

        if file_name.endswith('-ContactsDatabase.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(fullContactsDetails.CreateTime,'unixepoch') AS 'Creation Timestamp',
            datetime(fullContactsDetails.ModifyTIme,'unixepoch') AS 'Modified Timestamp',
            fullContactsDetails.Name AS 'Name',
            contact_emailsv3.Email AS 'Email'
            FROM fullContactsDetails
            LEFT JOIN contact_emailsv3 ON fullContactsDetails.ID = contact_emailsv3.ContactID
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            db.close()

    data_headers = (
        ('Creation Timestamp', 'datetime'),
        ('Modified Timestamp', 'datetime'),
        'Name',
        'Email',
    )
    return data_headers, data_list, source_path
