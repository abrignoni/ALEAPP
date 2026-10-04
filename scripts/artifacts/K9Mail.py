# pylint: disable=W0718
__artifacts_v2__ = {
    "get_k9mail_accounts": {
        "name": "K-9 Mail - Accounts",
        "description": "Account information from the K-9 Mail App",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-05-04",
        "last_update_date": "2024-05-04",
        "requirements": "none",
        "category": "K-9 Mail",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/05/app-k-9-mail-for-android.html",
        "paths": ('*/com.fsck.k9/databases/*',),
        "output_types": "standard",
        "artifact_icon": "mail",
    },
    "get_k9mail_messages": {
        "name": "K-9 Mail - Messages",
        "description": "E-Mails from the K-9 Mail App. Content is one stored text part of each message, not the whole message.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-05-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "K-9 Mail",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/05/app-k-9-mail-for-android.html"
                 ". Date is the messages.date column and Internal Date is the "
                 "messages.internal_date column, both read as Unix milliseconds and shown in UTC. "
                 "The cited post does not describe those two columns. In the app's source at commit "
                 "9aee4a9, date is the time parsed from the message's Date header and internal_date "
                 "is the internal date the mail server reported for the message (the IMAP "
                 "INTERNALDATE item), and each one is the time the app saved the message when that "
                 "value was missing. The columns are reported under their stored names for that "
                 "reason. Source versions before that commit were not read. References: "
                 "https://github.com/thunderbird/thunderbird-android/blob/9aee4a9adcb44ca084ca4e13ee3da564286b0af1/legacy/core/src/main/java/com/fsck/k9/mailstore/SaveMessageDataCreator.kt#L22-L24 , "
                 "https://github.com/thunderbird/thunderbird-android/blob/9aee4a9adcb44ca084ca4e13ee3da564286b0af1/mail/common/src/main/java/com/fsck/k9/mail/internet/MimeMessage.java#L144-L158 , "
                 "https://github.com/thunderbird/thunderbird-android/blob/9aee4a9adcb44ca084ca4e13ee3da564286b0af1/mail/protocols/imap/src/main/java/com/fsck/k9/mail/store/imap/RealImapFolder.kt#L797-L798 . "
                 "Content is the data of the first part under the message, in the stored seq "
                 "order starting at the root part (seq 0), whose mime_type begins with text/ and "
                 "whose data column is filled. No other part is reported. In the same source the app keeps a "
                 "part's body in the data column when it is 16 KiB or smaller and writes a larger "
                 "body to a file, which this artifact does not read "
                 "(https://github.com/thunderbird/thunderbird-android/blob/9aee4a9adcb44ca084ca4e13ee3da564286b0af1/legacy/storage/src/main/java/com/fsck/k9/storage/messages/SaveMessageOperations.kt#L266-L276 ). "
                 "Content is decoded when the part's encoding is base64 and is otherwise reported "
                 "as stored. No registered corpus holds a K-9 Mail database (44 Android corpora "
                 "listed on 2026-10-04), so the query was exercised only on a database built from "
                 "the app's schema.",
        "paths": ('*/com.fsck.k9/databases/*',),
        "output_types": "standard",
        "artifact_icon": "mail",
    }
}

import base64
import datetime
import json

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _prefs_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('preferences_storage'):
            return file_found
    return ''


def _account_uuids(cursor):
    cursor.execute("SELECT value FROM preferences_storage WHERE primkey = 'accountUuids'")
    rows = cursor.fetchall()
    return rows[0][0].split(',') if rows and rows[0][0] else []


@artifact_processor
def get_k9mail_accounts(context):
    files_found = context.get_files_found()
    source_path = _prefs_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        for uuid in _account_uuids(cursor):
            cursor.execute("SELECT primkey, value FROM preferences_storage WHERE primkey LIKE ?", (uuid + '%',))
            mail = name = username = password = server_in = server_out = server_in_settings = server_out_settings = ''
            last_sync = ''
            for key, value in cursor.fetchall():
                if 'email.0' in key:
                    mail = value
                elif 'name.0' in key:
                    name = value
                elif 'lastSyncTime' in key:
                    last_sync = value
                elif 'incomingServerSettings' in key:
                    server_in_settings = value
                    j = json.loads(value)
                    username = j.get('username', '')
                    password = j.get('password', '')
                    server_in = f"{j.get('host')}:{j.get('port')}"
                elif 'outgoingServerSettings' in key:
                    server_out_settings = value
                    j = json.loads(value)
                    server_out = f"{j.get('host')}:{j.get('port')}"
            data_list.append((uuid, mail, name, username, password, _ms_to_utc(last_sync), server_in, server_out, server_in_settings, server_out_settings))
        db.close()

    data_headers = ('Internal Account UUID', 'Mail-Address', 'Name', 'Username', 'Password', ('Last Sync Time', 'datetime'), 'Incoming Server', 'Outgoing Server', 'Incoming Server Settings', 'Outgoing Server Settings')
    return data_headers, data_list, source_path


def _account_emails(files_found):
    '''Map account UUID -> primary email address (from preferences_storage).'''
    prefs = _prefs_db(files_found)
    emails = {}
    if prefs:
        db = open_sqlite_db_readonly(prefs)
        cursor = db.cursor()
        for uuid in _account_uuids(cursor):
            cursor.execute("SELECT value FROM preferences_storage WHERE primkey LIKE ?", (uuid + '.email.0%',))
            row = cursor.fetchone()
            emails[uuid] = row[0] if row else ''
        db.close()
    return emails


@artifact_processor
def get_k9mail_messages(context):
    files_found = context.get_files_found()
    emails = _account_emails(files_found)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('preferences_storage') or not file_found.endswith('db'):
            continue
        uuid = next((u for u in emails if u in file_found), None)
        account = emails.get(uuid, '')

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT deleted, subject, date, sender_list, to_list, cc_list, bcc_list, reply_to_list,
                attachment_count, internal_date, preview, read, flagged, answered, forwarded, name, root, header,
                (SELECT encoding FROM message_parts M_INNER WHERE M_INNER.root = M_OUTER.ROOT
                    AND M_INNER.data IS NOT NULL AND M_INNER.mime_type LIKE 'text/%' ORDER BY M_INNER.seq LIMIT 1) AS encoding,
                (SELECT data FROM message_parts M_INNER WHERE M_INNER.root = M_OUTER.ROOT
                    AND M_INNER.data IS NOT NULL AND M_INNER.mime_type LIKE 'text/%' ORDER BY M_INNER.seq LIMIT 1) AS data,
                data_location
                FROM message_parts M_OUTER
                JOIN messages ON messages.message_part_id = M_OUTER.root
                JOIN folders ON folders.id = messages.folder_id
                WHERE seq = 0
            ''')
            rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            rows = []
        db.close()

        if rows:
            source_path = file_found
        for row in rows:
            header = row[17].decode('UTF-8', 'replace') if isinstance(row[17], bytes) else (row[17] or '')
            content = ''
            try:
                if row[18] == 'base64' and row[19]:
                    content = base64.b64decode(row[19]).decode('UTF-8', 'replace')
                elif row[19]:
                    content = row[19].decode('UTF-8', 'replace') if isinstance(row[19], bytes) else row[19]
            except (ValueError, TypeError):
                content = str(row[19])
            data_list.append((
                account, _ms_to_utc(row[2]), row[15], row[1], row[10], row[3], row[4], row[5], row[6], row[7],
                row[8], content, _ms_to_utc(row[9]),
                'Yes' if row[0] == 1 else 'No', 'Yes' if row[11] == 1 else 'No', 'Yes' if row[12] == 1 else 'No',
                'Yes' if row[13] == 1 else 'No', 'Yes' if row[14] == 1 else 'No', header))

    data_headers = ('Account', ('Date', 'datetime'), 'Folder', 'Subject', 'Message Preview', 'From Address', 'To Address', 'CC', 'BCC', 'Reply To', '# of Attachments', 'Content', ('Internal Date', 'datetime'), 'Deleted', 'Read', 'Flagged', 'Answered', 'Forwarded', 'Header')
    return data_headers, data_list, source_path
