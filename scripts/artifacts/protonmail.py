__artifacts_v2__ = {
    "get_protonmail_messages": {
        "name": "ProtonMail - Messages",
        "description": "Parses ProtonMail messages (timestamp, subject, sender, message type, unread flag, size, location, attachments and recipient lists; a message with several attachments has one row per attachment) from the ProtonMail messages database.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Message Direction is this module's mapping of "
                 "messagev3.Type: 0 Incoming, 1 Draft, 2 Outgoing; any other "
                 "value is blank. The app's source defines Type as 0 INBOX, 1 "
                 "DRAFT, 2 SENT, 3 INBOX_AND_SENT, so a Type 3 message shows "
                 "a blank direction. Status is the Unread flag (0 Read, 1 "
                 "Unread); it is the app's flag and does not establish that a "
                 "person read the message. Folder maps messagev3.Location 0 "
                 "Inbox, 1 Drafts, 2 Sent, 3 Trash and 6 Archive and shows 7 "
                 "as '7 (TBD)'; any other value is blank, so a message in "
                 "Spam shows no folder. The app's MessageLocationType enum "
                 "names 1 ALL_DRAFT, 2 ALL_SENT, 4 SPAM, 5 ALL_MAIL, 7 SENT, "
                 "8 DRAFT, 9 OUTBOX and 10 STARRED. Time is read as Unix "
                 "seconds and AccessTime as Unix milliseconds; what "
                 "AccessTime marks is not established. The row count is not a "
                 "message count: a message with several attachments has one "
                 "row per attachment. References: ProtonMail Android, "
                 "Message.kt, "
                 "https://github.com/ProtonMail/proton-mail-android/blob/"
                 "0b178613c96d47e9060dcc3ca3db904dfdd1f391/app/src/main/java/"
                 "ch/protonmail/android/data/local/model/Message.kt#L127 "
                 "and Constants.kt, "
                 "https://github.com/ProtonMail/proton-mail-android/blob/"
                 "0b178613c96d47e9060dcc3ca3db904dfdd1f391/app/src/main/java/"
                 "ch/protonmail/android/core/Constants.kt#L165-L181. "
                 "The source was read at that commit only; other app versions "
                 "were not checked.",
        "paths": ('*/ch.protonmail.android/databases/*-MessagesDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "mail",
    },
    "get_protonmail_contacts": {
        "name": "ProtonMail - Contacts",
        "description": "Parses ProtonMail contacts (creation and modified times read as Unix seconds, name and email) from the ProtonMail contacts database, one row per contact email address.",
        "author": "Kevin Pagano (@stark4n6)",
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

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def get_protonmail_messages(context):
    files_found = unique_files(context)
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
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],convert_human_ts_to_utc(row[6]),row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

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
def get_protonmail_contacts(context):
    files_found = unique_files(context)
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
                data_list.append((convert_human_ts_to_utc(row[0]),convert_human_ts_to_utc(row[1]),row[2],row[3]))

            db.close()

    data_headers = (
        ('Creation Timestamp', 'datetime'),
        ('Modified Timestamp', 'datetime'),
        'Name',
        'Email',
    )
    return data_headers, data_list, source_path
