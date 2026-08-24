"""Proton Mail Android 'Inbox' local cache (uniffi store).

Proton Mail for Android (the 'Inbox' rewrite, uniffi/Rust core) keeps a local
SQLite cache under the app's databases directory, separate from the older
ch.protonmail.android *-MessagesDatabase.db store that scripts/artifacts/
protonmail.py parses. The same store ships on iOS as group.me.proton.mail
(iLEAPP protonMailInbox.py); this is the Android sibling.

Two databases are read, dispatched by the tables they carry:
  - databases/account.db        -> core_accounts -> account artifact
  - databases/<base64 id>.db    -> messages, contacts, attachments, labels

In the tested image the subjects, sender and recipient addresses, contacts and
account details are stored in clear text, and attachments are written to disk
under cache/mail-cache/attachments/ (present and decrypted). Unlike the iOS
store, the message body is kept PGP-encrypted in raw_message_body on the tested
Android version, so no message body is shown here.

Timestamps are Unix seconds. Folder names come from the app's own labels table.
Address columns hold JSON, decoded here to 'Name <address>' strings.
"""
__artifacts_v2__ = {
    "protonmailInboxMessages": {
        "name": "ProtonMail - Inbox Messages",
        "description": "Messages cached by the Proton Mail Android Inbox app, including subject, sender, recipients and folder",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Reads the uniffi Inbox cache used by current Proton Mail for Android, separate from "
                 "the older *-MessagesDatabase.db store. In the tested image the subject, sender and "
                 "recipient values are stored in clear text; the message body is kept PGP-encrypted in "
                 "raw_message_body and is not shown. Folder is resolved from the app's own labels "
                 "table. A cached row reflects what the app had synced locally, not necessarily the "
                 "full mailbox.",
        "paths": ('*/ch.protonmail.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | Proton Mail (Inbox) | 3 rows",
            "hc_pixel8pro_a17": "Android 17 | Proton Mail (Inbox) | 3 rows",
        }
    },
    "protonmailInboxAttachments": {
        "name": "ProtonMail - Inbox Attachments",
        "description": "Attachments cached on disk by the Proton Mail Android Inbox app",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Attachment metadata from the Inbox cache joined to the files the app wrote under "
                 "cache/mail-cache/attachments/<attachment id>/. In the tested image those files are "
                 "decrypted images. The media column shows a file only when it is present in the "
                 "extraction.",
        "paths": ('*/ch.protonmail.android/databases/*.db*',
                  '*/ch.protonmail.android/cache/mail-cache/attachments/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | Proton Mail (Inbox) | 15 rows",
            "hc_pixel8pro_a17": "Android 17 | Proton Mail (Inbox) | 15 rows",
        }
    },
    "protonmailInboxContacts": {
        "name": "ProtonMail - Inbox Contacts",
        "description": "Contact email addresses cached by the Proton Mail Android Inbox app",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Contact email rows from the Inbox cache. A proton-autosave uid marks a contact the "
                 "app created automatically from a sent or received message rather than one the user "
                 "saved.",
        "paths": ('*/ch.protonmail.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "address-book",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | Proton Mail (Inbox) | 1 row",
            "hc_pixel8pro_a17": "Android 17 | Proton Mail (Inbox) | 1 row",
        }
    },
    "protonmailInboxAccount": {
        "name": "ProtonMail - Inbox Account",
        "description": "Signed-in Proton account details cached by the Proton Mail Android Inbox app",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Account and user rows from databases/account.db and the mail cache. Used and maximum "
                 "space are bytes as stored.",
        "paths": ('*/ch.protonmail.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | Proton Mail (Inbox) | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | Proton Mail (Inbox) | 2 rows",
        }
    }
}

import json
import re

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               does_table_exist_in_db, convert_unix_ts_to_utc,
                               check_in_media)

_ATTACHMENT_ID_RE = re.compile(r'/mail-cache/attachments/(\d+)/')


def _is_mail_cache(file_found):
    return does_table_exist_in_db(file_found, 'messages') and \
        does_table_exist_in_db(file_found, 'labels')


def _is_account_db(file_found):
    return does_table_exist_in_db(file_found, 'core_accounts')


def _format_addresses(raw):
    """Decode a Proton address JSON value to a 'Name <address>' string.

    Accepts a single object or a list of them. Anything that does not decode is
    returned unchanged so a format change surfaces rather than being dropped.
    """
    if not raw:
        return ''
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return str(raw)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return str(raw)
    parts = []
    for item in data:
        if not isinstance(item, dict):
            continue
        address = item.get('address', '')
        name = item.get('name', '')
        parts.append(f'{name} <{address}>'.strip() if name else address)
    return '; '.join(p for p in parts if p)


def _labels_by_message(file_found):
    """message local_id -> sorted folder names, from labels + message_labels."""
    names = {row[0]: row[1] for row in
             get_sqlite_db_records(file_found, 'SELECT local_id, name FROM labels')}
    out = {}
    for message_id, label_id in get_sqlite_db_records(
            file_found, 'SELECT local_message_id, local_label_id FROM message_labels'):
        name = names.get(label_id)
        if name:
            out.setdefault(message_id, set()).add(name)
    return {mid: ', '.join(sorted(labels)) for mid, labels in out.items()}


@artifact_processor
def protonmailInboxMessages(context):
    data_headers = (
        ('Time', 'datetime'),
        'Folder',
        'Subject',
        'From',
        'To',
        'CC',
        'BCC',
        'Read',
        'Replied',
        'Forwarded',
        'Attachments',
        'Size',
        'Deleted',
        'Source File')
    data_list = []
    sources = []

    query = '''
        SELECT time, subject, sender, to_list, cc_list, bcc_list,
               unread, is_replied, is_forwarded, num_attachments, size, deleted, local_id
        FROM messages
    '''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db') or not _is_mail_cache(file_found):
            continue
        rel_path = context.get_relative_path(file_found)
        folders = _labels_by_message(file_found)
        rows_seen = False
        for row in get_sqlite_db_records(file_found, query):
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                folders.get(row[12], ''),
                row[1],
                _format_addresses(row[2]),
                _format_addresses(row[3]),
                _format_addresses(row[4]),
                _format_addresses(row[5]),
                'No' if row[6] else 'Yes',   # unread flag inverted to Read
                'Yes' if row[7] else 'No',
                'Yes' if row[8] else 'No',
                row[9],
                row[10],
                'Yes' if row[11] else 'No',
                rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonmailInboxAttachments(context):
    data_headers = (
        'Filename',
        ('Attachment', 'media'),
        'Size',
        'MIME Type',
        'Cached Path',
        'Remote Message ID',
        'Source File')
    data_list = []
    sources = []

    # Map the attachment id embedded in each on-disk cache path to its extracted
    # file, so the media can be checked in even though the database records the
    # /data/user/0 symlink form of the path rather than the extracted location.
    found_by_id = {}
    db_files = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        match = _ATTACHMENT_ID_RE.search(file_found.replace('\\', '/'))
        if match:
            found_by_id[int(match.group(1))] = file_found
        elif file_found.endswith('.db'):
            db_files.append(file_found)

    for file_found in db_files:
        if not _is_mail_cache(file_found) or not does_table_exist_in_db(file_found, 'attachments'):
            continue
        rel_path = context.get_relative_path(file_found)

        cache_paths = {}
        if does_table_exist_in_db(file_found, 'attachment_cache'):
            cache_paths = {row[0]: row[1] for row in get_sqlite_db_records(
                file_found, 'SELECT attachment_id, path FROM attachment_cache')}

        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT local_id, filename, size, mime_type, remote_message_id FROM attachments'):
            local_id, filename, size, mime_type, remote_message_id = row
            media_ref = ''
            found_path = found_by_id.get(local_id)
            if found_path:
                media_ref = check_in_media(found_path, filename) or ''
            data_list.append((filename, media_ref, size, mime_type,
                              cache_paths.get(local_id, ''), remote_message_id, rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonmailInboxContacts(context):
    data_headers = (
        'Name',
        'Email',
        ('Last Used', 'datetime'),
        'Is Proton',
        'Contact UID',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db') or not _is_mail_cache(file_found):
            continue
        if not does_table_exist_in_db(file_found, 'contact_emails'):
            continue
        rel_path = context.get_relative_path(file_found)

        uids = {}
        if does_table_exist_in_db(file_found, 'contacts'):
            uids = {row[0]: row[1] for row in get_sqlite_db_records(
                file_found, 'SELECT local_id, uid FROM contacts')}

        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT name, email, last_used_time, is_proton, local_contact_id FROM contact_emails'):
            name, email, last_used, is_proton, local_contact_id = row
            data_list.append((name, email, convert_unix_ts_to_utc(last_used),
                              'Yes' if is_proton else 'No',
                              uids.get(local_contact_id, ''), rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonmailInboxAccount(context):
    data_headers = (
        'Username',
        'Display Name',
        'Email',
        ('Create Time', 'datetime'),
        'Used Space',
        'Max Space',
        'Ready',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue
        rel_path = context.get_relative_path(file_found)

        if _is_mail_cache(file_found) and does_table_exist_in_db(file_found, 'users'):
            for row in get_sqlite_db_records(
                    file_found,
                    'SELECT name, display_name, email, create_time, used_space, max_space FROM users'):
                name, display_name, email, create_time, used_space, max_space = row
                data_list.append((name, display_name, email,
                                  convert_unix_ts_to_utc(create_time),
                                  used_space, max_space, '', rel_path))
            if data_list:
                sources.append(rel_path)
        elif _is_account_db(file_found):
            for row in get_sqlite_db_records(
                    file_found,
                    'SELECT username, name_or_addr, is_ready FROM core_accounts'):
                username, name_or_addr, is_ready = row
                data_list.append((username, '', name_or_addr, '', '', '',
                                  'Yes' if is_ready else 'No', rel_path))
            if data_list:
                sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
