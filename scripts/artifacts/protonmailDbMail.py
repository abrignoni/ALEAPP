"""Proton Mail Android 'db-mail' Room store (MailX generation).

Between the old *-MessagesDatabase.db store (parsed by protonmail.py) and the
current uniffi Inbox store (parsed by protonmailInbox.py), Proton Mail for
Android shipped a Room database named db-mail whose tables are the *Entity
classes (MessageEntity, MessageBodyEntity, ConversationEntity, ...).

In the tested image the message subjects, sender and recipient addresses,
contacts and account details are stored in clear text. The message body is kept
PGP-encrypted in MessageBodyEntity.body, so no body is shown. Attachment rows
are metadata only: the files are not held in an app cache directory here.

Timestamps are Unix seconds, except UserEntity.createdAtUtc which is Unix
milliseconds. Recipient columns hold JSON, decoded here to 'Name <address>'.
"""
__artifacts_v2__ = {
    "protonmailDbMailMessages": {
        "name": "ProtonMail - MailX Messages",
        "description": "Messages from the Proton Mail Android db-mail (MailX) Room store, including subject, sender, recipients and conversation id",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Reads the db-mail Room store used by an intermediate Proton Mail for Android "
                 "generation, separate from the older *-MessagesDatabase.db store and the newer "
                 "uniffi Inbox cache. In the tested image the subject, sender and recipient values "
                 "are stored in clear text; the message body is kept PGP-encrypted in "
                 "MessageBodyEntity and is not shown. A cached row reflects what the app had synced "
                 "locally, not necessarily the full mailbox.",
        "paths": ('*/ch.protonmail.android/databases/db-mail*',),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Proton Mail (MailX) | 12 rows",
        }
    },
    "protonmailDbMailAttachments": {
        "name": "ProtonMail - MailX Attachments",
        "description": "Attachment metadata from the Proton Mail Android db-mail (MailX) Room store",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Attachment metadata from the db-mail Room store. Rows are metadata only: the files are not "
                 "held in an app cache directory in this store. When an attachment was saved, "
                 "MessageAttachmentMetadataEntity records the destination content URI.",
        "paths": ('*/ch.protonmail.android/databases/db-mail*',),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Proton Mail (MailX) | 86 rows",
        }
    },
    "protonmailDbMailContacts": {
        "name": "ProtonMail - MailX Contacts",
        "description": "Contact email addresses from the Proton Mail Android db-mail (MailX) Room store",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Contact email rows from the db-mail Room store.",
        "paths": ('*/ch.protonmail.android/databases/db-mail*',),
        "output_types": "standard",
        "artifact_icon": "address-book",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Proton Mail (MailX) | 2 rows",
        }
    },
    "protonmailDbMailAccount": {
        "name": "ProtonMail - MailX Account",
        "description": "Signed-in Proton account details from the Proton Mail Android db-mail (MailX) Room store",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "ProtonMail",
        "notes": "Account and user rows from the db-mail Room store. Used and maximum space are bytes "
                 "as stored. createdAtUtc is Unix milliseconds.",
        "paths": ('*/ch.protonmail.android/databases/db-mail*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Proton Mail (MailX) | 1 row",
        }
    }
}

import json

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               does_table_exist_in_db, convert_unix_ts_to_utc)


def _is_dbmail(file_found):
    return does_table_exist_in_db(file_found, 'MessageEntity')


def _format_addresses(raw):
    """Decode a Proton recipient JSON value to a 'Name <address>' string."""
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


def _sender(address, name):
    return f'{name} <{address}>'.strip() if name else (address or '')


@artifact_processor
def protonmailDbMailMessages(context):
    data_headers = (
        ('Time', 'datetime'),
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
        'Conversation ID',
        'Message ID',
        'Source File')
    data_list = []
    sources = []

    query = '''
        SELECT time, subject, sender_address, sender_name, toList, ccList, bccList,
               unread, isReplied, isForwarded, numAttachments, size, conversationId, messageId
        FROM MessageEntity
    '''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('db-mail') or not _is_dbmail(file_found):
            continue
        rel_path = context.get_relative_path(file_found)
        rows_seen = False
        for row in get_sqlite_db_records(file_found, query):
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                row[1],
                _sender(row[2], row[3]),
                _format_addresses(row[4]),
                _format_addresses(row[5]),
                _format_addresses(row[6]),
                'No' if row[7] else 'Yes',   # unread inverted to Read
                'Yes' if row[8] else 'No',
                'Yes' if row[9] else 'No',
                row[10],
                row[11],
                row[12],
                row[13],
                rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonmailDbMailAttachments(context):
    data_headers = (
        'Filename',
        'Size',
        'MIME Type',
        'Disposition',
        'Saved To (URI)',
        'Message ID',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('db-mail') or not _is_dbmail(file_found):
            continue
        if not does_table_exist_in_db(file_found, 'MessageAttachmentEntity'):
            continue
        rel_path = context.get_relative_path(file_found)

        saved = {}
        if does_table_exist_in_db(file_found, 'MessageAttachmentMetadataEntity'):
            saved = {(row[0], row[1]): row[2] for row in get_sqlite_db_records(
                file_found,
                'SELECT messageId, attachmentId, uri FROM MessageAttachmentMetadataEntity')}

        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT messageId, attachmentId, name, size, mimeType, disposition FROM MessageAttachmentEntity'):
            message_id, attachment_id, name, size, mime_type, disposition = row
            data_list.append((name, size, mime_type, disposition,
                              saved.get((message_id, attachment_id), ''),
                              message_id, rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonmailDbMailContacts(context):
    data_headers = (
        'Name',
        'Email',
        'Is Proton',
        'Contact ID',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('db-mail') or not _is_dbmail(file_found):
            continue
        if not does_table_exist_in_db(file_found, 'ContactEmailEntity'):
            continue
        rel_path = context.get_relative_path(file_found)
        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT name, email, isProton, contactId FROM ContactEmailEntity'):
            name, email, is_proton, contact_id = row
            data_list.append((name, email, 'Yes' if is_proton else 'No', contact_id, rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def protonmailDbMailAccount(context):
    data_headers = (
        'Username',
        'Email',
        'Name',
        'Display Name',
        ('Created', 'datetime'),
        'Used Space',
        'Max Space',
        'State',
        'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('db-mail') or not _is_dbmail(file_found):
            continue
        if not does_table_exist_in_db(file_found, 'UserEntity'):
            continue
        rel_path = context.get_relative_path(file_found)

        states = {}
        if does_table_exist_in_db(file_found, 'AccountEntity'):
            states = {row[0]: (row[1], row[2]) for row in get_sqlite_db_records(
                file_found, 'SELECT userId, username, state FROM AccountEntity')}

        rows_seen = False
        for row in get_sqlite_db_records(
                file_found,
                'SELECT userId, email, name, displayName, createdAtUtc, usedSpace, maxSpace FROM UserEntity'):
            user_id, email, name, display_name, created, used_space, max_space = row
            username, state = states.get(user_id, ('', ''))
            data_list.append((username, email, name, display_name,
                              convert_unix_ts_to_utc(created),
                              used_space, max_space, state, rel_path))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
