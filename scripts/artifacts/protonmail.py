__artifacts_v2__ = {
    "get_protonmail_messages": {
        "name": "ProtonMail - Messages",
        "description": "Parses ProtonMail messages (timestamp, subject, sender, message type, unread flag, size, AccessTime, location, attachments and recipient lists; a message with several attachments has one row per attachment) from the ProtonMail messages database.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2023-04-26",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Message Type shows messagev3.Type under the name the app's "
                 "MessageType enum gives it: 0 INBOX, 1 DRAFT, 2 SENT, 3 "
                 "INBOX_AND_SENT; any other value is shown as stored. "
                 "Reference: ProtonMail Android, Message.kt, "
                 "https://github.com/ProtonMail/proton-mail-android/blob/"
                 "0b178613c96d47e9060dcc3ca3db904dfdd1f391/app/src/main/java/"
                 "ch/protonmail/android/data/local/model/Message.kt#L127 "
                 "and "
                 "https://github.com/ProtonMail/proton-mail-android/blob/"
                 "0b178613c96d47e9060dcc3ca3db904dfdd1f391/app/src/main/java/"
                 "ch/protonmail/android/data/local/model/Message.kt#L600-L602 "
                 "Unread shows the stored Unread flag (0 No, 1 Yes); it is the "
                 "app's flag and does not establish that a person read the "
                 "message. "
                 "Location shows messagev3.Location under the name the app's "
                 "MessageLocationType enum gives it: -1 INVALID, 0 INBOX, 1 "
                 "ALL_DRAFT, 2 ALL_SENT, 3 TRASH, 4 SPAM, 5 ALL_MAIL, 6 ARCHIVE, "
                 "7 SENT, 8 DRAFT, 9 OUTBOX, 10 STARRED, 12 ALL_SCHEDULED, 77 "
                 "LABEL, 99 SEARCH, 999 LABEL_FOLDER; any other value is shown "
                 "as stored. "
                 "Reference: ProtonMail Android, Constants.kt, "
                 "https://github.com/ProtonMail/proton-mail-android/blob/"
                 "0b178613c96d47e9060dcc3ca3db904dfdd1f391/app/src/main/java/"
                 "ch/protonmail/android/core/Constants.kt#L165-L181 "
                 "On pixel3_a11 and pixel3_a12 the stored Type values were 0 and "
                 "2 and the stored Location values 0 and 7, and every Location 7 "
                 "message had Type 2; the other names come from the source and "
                 "were not exercised. "
                 "Message Timestamp reads Time as Unix seconds; on those two "
                 "images the values fall in 2020 and 2021 read that way. "
                 "AccessTime is read as Unix milliseconds and is blank when the "
                 "stored value is 0. The one place found that sets it in the "
                 "app's source is the job that marks messages read, which stores "
                 "the current time in milliseconds; the job is queued by a swipe "
                 "action, by the message repository's mark read call and by the "
                 "compose screen's repository, so the value does not by itself "
                 "establish that a person opened the message. "
                 "Reference: ProtonMail Android, PostReadJob.java, "
                 "https://github.com/ProtonMail/proton-mail-android/blob/"
                 "0b178613c96d47e9060dcc3ca3db904dfdd1f391/app/src/main/java/"
                 "ch/protonmail/android/jobs/PostReadJob.java#L57 "
                 "On pixel3_a11 it was set on 1 of 4 messages. On pixel3_a12 it "
                 "was set on 3 of 8 messages in the data/data copy of the "
                 "database; the data_mirror copy held 6 messages, none with it "
                 "set. "
                 "The row count is not a message count: a message with several "
                 "attachments has one row per attachment. "
                 "The source was read at that commit only; other app versions "
                 "were not checked.",
        "paths": ('*/ch.protonmail.android/databases/*-MessagesDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "mail",
    },
    "get_protonmail_contacts": {
        "name": "ProtonMail - Contacts",
        "description": "Parses ProtonMail contacts (creation and modified times read as Unix seconds, name and email) from the ProtonMail contacts database, one row per contact email address.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
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
                WHEN 0 THEN 'INBOX'
                WHEN 1 THEN 'DRAFT'
                WHEN 2 THEN 'SENT'
                WHEN 3 THEN 'INBOX_AND_SENT'
                ELSE messagev3.Type
            END AS 'Message Type',
            CASE messagev3.Unread
                WHEN 0 THEN 'No'
                WHEN 1 THEN 'Yes'
                ELSE messagev3.Unread
            END AS 'Unread',
            messagev3.Size AS 'Message Size',
            CASE messagev3.AccessTime
                WHEN 0 THEN ''
                ELSE datetime(messagev3.AccessTime/1000,'unixepoch')
            END AS 'AccessTime',
            CASE messagev3.Location
                WHEN -1 THEN 'INVALID'
                WHEN 0 THEN 'INBOX'
                WHEN 1 THEN 'ALL_DRAFT'
                WHEN 2 THEN 'ALL_SENT'
                WHEN 3 THEN 'TRASH'
                WHEN 4 THEN 'SPAM'
                WHEN 5 THEN 'ALL_MAIL'
                WHEN 6 THEN 'ARCHIVE'
                WHEN 7 THEN 'SENT'
                WHEN 8 THEN 'DRAFT'
                WHEN 9 THEN 'OUTBOX'
                WHEN 10 THEN 'STARRED'
                WHEN 12 THEN 'ALL_SCHEDULED'
                WHEN 77 THEN 'LABEL'
                WHEN 99 THEN 'SEARCH'
                WHEN 999 THEN 'LABEL_FOLDER'
                ELSE messagev3.Location
            END AS 'Location',
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
        'Message Type',
        'Unread',
        'Message Size',
        ('AccessTime', 'datetime'),
        'Location',
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
