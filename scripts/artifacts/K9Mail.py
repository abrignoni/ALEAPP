# pylint: disable=W0718
__artifacts_v2__ = {
    "get_k9mail_accounts": {
        "name": "K-9 Mail - Accounts",
        "description": "Account information from the K-9 Mail App",
        "author": "Marco Neumann {kalinko@be-binary.de}",
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
        "description": "E-Mails from the K-9 Mail App",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-05-04",
        "last_update_date": "2024-05-04",
        "requirements": "none",
        "category": "K-9 Mail",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/05/app-k-9-mail-for-android.html",
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
                (SELECT encoding FROM message_parts M_INNER WHERE M_INNER.root = M_OUTER.ROOT AND seq = 1) AS encoding,
                (SELECT data FROM message_parts M_INNER WHERE M_INNER.root = M_OUTER.ROOT AND seq = 1) AS data,
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

    data_headers = ('Account', ('Date Sent', 'datetime'), 'Folder', 'Subject', 'Message Preview', 'From Address', 'To Address', 'CC', 'BCC', 'Reply To', '# of Attachments', 'Content', ('Date Received', 'datetime'), 'Deleted', 'Read', 'Flagged', 'Answered', 'Forwarded', 'Header')
    return data_headers, data_list, source_path
