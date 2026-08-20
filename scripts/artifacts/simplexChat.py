__artifacts_v2__ = {
    "simplex_messages": {
        "name": "SimpleX Chat - Messages",
        "description": "Parses the messages held in the SimpleX Chat Android encrypted "
                       "database, with the direction, the contact and the message text.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "SimpleX Chat",
        "notes": "One row per chat item. The app keeps its database encrypted with "
                 "SQLCipher, and this artifact reads it only when the extraction also "
                 "carries the key: the passphrase is taken from the SimpleX entry of a "
                 "Secrets/secrets.json produced during acquisition, and without that file "
                 "nothing is reported. Decryption uses the SQLCipher 4 defaults, a 4096 byte "
                 "page with 256,000 PBKDF2 iterations and HMAC-SHA512, and the reader "
                 "verifies the HMAC of every page: on the tested sample all 531 pages "
                 "verified, so the decryption is checked rather than assumed. Direction "
                 "comes from the item's own sent flag, 1 for sent and 0 for received, which "
                 "covered every row. Timestamps are stored as text with nanosecond "
                 "precision and the fraction is trimmed to microseconds before parsing, "
                 "because releases before 3.11 accept only three or six digits. Deleted and "
                 "Edited are the flags the row carries, so a message the account holder "
                 "deleted is still reported and marked rather than dropped. Item Content is "
                 "the record's own structured content, as stored, and is carried because a "
                 "row with no text can still be a call, a file or a member event. Field "
                 "mapping was done against two private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": (
            '*/chat.simplex.app/files_chat.db',
            '*/Secrets/secrets.json',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "data_views": {
            "conversation": {
                "directionSentValue": "Sent",
                "conversationDiscriminatorColumn": "Contact",
                "conversationLabelColumn": "Contact",
                "directionColumn": "Direction",
                "senderColumn": "Sender",
                "textColumn": "Message",
                "timeColumn": "Timestamp",
            }
        },
        "artifact_icon": "message-circle"
    },
    "simplex_contacts": {
        "name": "SimpleX Chat - Contacts",
        "description": "Parses the contacts held in the SimpleX Chat Android encrypted "
                       "database, with the display name and the last chat time.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "SimpleX Chat",
        "notes": "One row per contact. Read from the same encrypted database as the "
                 "messages and subject to the same requirement that the extraction carries "
                 "the key. Local Alias is a name the account holder set for the contact and "
                 "is separate from the name the contact published, so both are reported. "
                 "Incognito, Favourite and Deleted are the flags the record carries. Contact "
                 "Link is the connection address the record holds, as stored. Field mapping "
                 "was done against two private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/chat.simplex.app/files_chat.db',
            '*/Secrets/secrets.json',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
    "simplex_files": {
        "name": "SimpleX Chat - Files",
        "description": "Parses the file transfers recorded in the SimpleX Chat Android "
                       "encrypted database, and whether the stored file is present.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "SimpleX Chat",
        "notes": "One row per file record. File Present states whether a file of that name "
                 "is in the extraction beside the database; on the tested sample 15 of the "
                 "20 records had one. The stored files are themselves encrypted and this "
                 "artifact does not decrypt them, so no media column is offered. What was "
                 "established about that encryption is worth recording: each record carries "
                 "a 32 byte key and a 24 byte nonce as raw values, and every stored file is "
                 "exactly 16 bytes larger than the size the record states, which is "
                 "consistent with a Poly1305 tag on an XSalsa20-Poly1305 box. Six "
                 "combinations of keystream offset and tag position were tried against the "
                 "sample and none produced a recognisable image or video header, so the "
                 "scheme is not established here and the key and nonce are reported as "
                 "stored so the work can be picked up. Field mapping was done against two "
                 "private samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/chat.simplex.app/files_chat.db',
            '*/chat.simplex.app/files/app_files/*',
            '*/Secrets/secrets.json',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file"
    },
    "simplex_message_edits": {
        "name": "SimpleX Chat - Message Edits",
        "description": "Parses the earlier versions of edited SimpleX Chat messages, which "
                       "record what a message said before it was changed.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "SimpleX Chat",
        "notes": "One row per stored version of a message. The app keeps the previous "
                 "content of an edited message, so these rows are what a message said "
                 "before it was changed and are reported alongside the message they belong "
                 "to. Version Time is when that version was current. Content is the stored "
                 "structured content, as stored. Field mapping was done against two private "
                 "samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/chat.simplex.app/files_chat.db',
            '*/Secrets/secrets.json',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "edit"
    },
    "simplex_reactions": {
        "name": "SimpleX Chat - Reactions",
        "description": "Parses the reactions recorded against SimpleX Chat messages, with "
                       "the reaction and whether the account holder sent it.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "SimpleX Chat",
        "notes": "One row per reaction. Sent is the flag the record carries and separates a "
                 "reaction the account holder made from one made to their message. Reaction "
                 "is the stored value, as stored, which the app writes as a structured "
                 "value rather than a bare character. Field mapping was done against two "
                 "private samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/chat.simplex.app/files_chat.db',
            '*/Secrets/secrets.json',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "smile"
    },
}

import hashlib
import json
import os
import re
import sqlite3
import tempfile
from datetime import datetime

from scripts.artifacts.storagePathViews import unique_files
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.ilapfuncs import artifact_processor, logfunc

_PACKAGE = 'chat.simplex.app'
_DATABASE = 'files_chat.db'
_SECRETS = 'secrets.json'
_PAYLOAD_KEY = 'databasePassword'

# SQLCipher 4 defaults. The app does not override them, and every page of the tested
# sample verified its HMAC under these values, which is what confirms them.
_PAGE_SIZE = 4096
_KDF_ITERATIONS = 256000
_HMAC = 'sha512'

_FRACTION = re.compile(r'^(.*\.)(\d+)(.*)$')


def _timestamp(value):
    '''A stored timestamp as a datetime, or '' when it does not parse.

    The app writes a nanosecond fraction. Releases before 3.11 accept only three or six
    digits, so the fraction is trimmed to six rather than relying on a newer parser.
    '''
    if not value or not isinstance(value, str):
        return ''
    text = value.strip().replace('Z', '+00:00')
    match = _FRACTION.match(text)
    if match:
        text = f'{match.group(1)}{match.group(2)[:6]:0<6}{match.group(3)}'
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return ''


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _passphrase(files_found):
    '''The database passphrase from the acquisition's secrets file, or None.

    The key is not in the app's own storage. Without the secrets file the database cannot
    be opened, and this artifact reports nothing rather than guessing.
    '''
    for path in files_found:
        if os.path.basename(str(path)) != _SECRETS:
            continue
        try:
            with open(str(path), 'r', encoding='utf-8') as handle:
                secrets = json.load(handle)
        except (OSError, ValueError) as error:
            logfunc(f'SimpleX Chat: could not read {_SECRETS}: {error}')
            continue
        if not isinstance(secrets, list):
            continue
        for entry in secrets:
            if not isinstance(entry, dict) or entry.get('app') != _PACKAGE:
                continue
            for item in entry.get('script_output') or []:
                payload = item.get('payload') if isinstance(item, dict) else None
                if isinstance(payload, dict) and payload.get(_PAYLOAD_KEY):
                    return str(payload[_PAYLOAD_KEY])
    return None


def _open_decrypted(database_path, passphrase):
    '''The decrypted database, or None when it cannot be opened.

    The decrypted copy is written under a per-file name in the system temporary
    directory, so two databases in one extraction cannot overwrite each other.
    '''
    digest = hashlib.sha1(str(database_path).encode()).hexdigest()[:16]
    folder = os.path.join(tempfile.gettempdir(), 'aleapp_simplex')
    os.makedirs(folder, exist_ok=True)
    output = os.path.join(folder, f'simplex_{digest}.db')
    try:
        pages, verified = decrypt_sqlcipher_db(
            database_path, passphrase, output, page_size=_PAGE_SIZE,
            kdf_iterations=_KDF_ITERATIONS, hmac_algorithm=_HMAC, kdf_algorithm=_HMAC)
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'SimpleX Chat: decryption failed for {os.path.basename(database_path)}: {error}')
        return None
    if verified < pages:
        logfunc(f'SimpleX Chat: {pages - verified} of {pages} pages did not verify their '
                f'HMAC in {os.path.basename(database_path)}')
    try:
        return sqlite3.connect(f'file:{output}?mode=ro', uri=True)
    except sqlite3.Error as error:
        logfunc(f'SimpleX Chat: could not open the decrypted database: {error}')
        return None


def _databases(context):
    '''[(relative path, open decrypted database)] for each store in the extraction.'''
    # The dedupe collapses the /data/data and /data/user/0 spellings of one file while
    # keeping a second Android user's copy, so a device with both is not counted twice.
    files = [str(f) for f in unique_files(context)]
    passphrase = _passphrase(files)
    stores = [f for f in files if os.path.basename(f) == _DATABASE]
    if stores and not passphrase:
        logfunc('SimpleX Chat: the database is present but no key was found in a '
                'Secrets/secrets.json, so nothing could be decrypted')
        return []
    opened = []
    for path in stores:
        connection = _open_decrypted(path, passphrase)
        if connection is not None:
            opened.append((context.get_relative_path(path), connection))
    return opened


def _rows(connection, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    try:
        cursor = connection.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as error:
        logfunc(f'SimpleX Chat: could not read from the database: {error}')
        return []


def _contact_names(connection):
    '''{contact id: display name} for the contacts in one database.'''
    names = {}
    for contact_id, local_name, display_name in _rows(connection, '''
            SELECT c.contact_id, c.local_display_name, p.display_name
            FROM contacts c
            LEFT JOIN contact_profiles p ON p.contact_profile_id = c.contact_profile_id'''):
        names[contact_id] = _text(display_name) or _text(local_name)
    return names


@artifact_processor
def simplex_messages(context):
    data_list = []
    source_files = []

    for relative, connection in _databases(context):
        names = _contact_names(connection)
        for row in _rows(connection, '''
                SELECT item_ts, created_at, updated_at, item_sent, contact_id, group_id,
                       item_text, item_content, item_status, item_deleted, item_edited,
                       item_deleted_ts, quoted_content, quoted_sent, item_live, timed_ttl,
                       timed_delete_at, user_mention, chat_item_id
                FROM chat_items'''):
            (item_ts, created_at, updated_at, item_sent, contact_id, group_id, item_text,
             item_content, item_status, item_deleted, item_edited, item_deleted_ts,
             quoted_content, quoted_sent, item_live, timed_ttl, timed_delete_at,
             user_mention, chat_item_id) = row
            contact = names.get(contact_id, _text(contact_id))
            direction = 'Sent' if item_sent else 'Received'
            source_files.append(relative)
            data_list.append((
                _timestamp(item_ts),
                _timestamp(created_at),
                _timestamp(updated_at),
                _timestamp(item_deleted_ts),
                direction,
                'Account Holder' if item_sent else contact,
                contact,
                _text(item_text),
                _text(item_status),
                _text(item_deleted),
                _text(item_edited),
                _text(quoted_content),
                _text(quoted_sent),
                _text(item_live),
                _text(timed_ttl),
                _timestamp(timed_delete_at) or _text(timed_delete_at),
                _text(user_mention),
                _text(group_id),
                _text(item_content),
                _text(chat_item_id),
                relative,
            ))
        connection.close()

    data_list.sort(key=lambda r: (str(r[0]), str(r[19])), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        ('Deleted At', 'datetime'),
        'Direction',
        'Sender',
        'Contact',
        'Message',
        'Status (as stored)',
        'Deleted (as stored)',
        'Edited (as stored)',
        'Quoted Content (as stored)',
        'Quoted Sent (as stored)',
        'Live (as stored)',
        'Disappearing TTL (as stored)',
        'Disappears At',
        'User Mention (as stored)',
        'Group ID',
        'Item Content (as stored)',
        'Chat Item ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def simplex_contacts(context):
    data_list = []
    source_files = []

    for relative, connection in _databases(context):
        for row in _rows(connection, '''
                SELECT c.created_at, c.updated_at, c.chat_ts, c.contact_id,
                       c.local_display_name, p.display_name, p.full_name, p.local_alias,
                       p.incognito, p.contact_link, p.short_descr, c.favorite, c.deleted,
                       c.contact_status, c.unread_chat, c.contact_used, c.enable_ntfs
                FROM contacts c
                LEFT JOIN contact_profiles p ON p.contact_profile_id = c.contact_profile_id'''):
            (created_at, updated_at, chat_ts, contact_id, local_name, display_name,
             full_name, alias, incognito, contact_link, short_descr, favourite, deleted,
             status, unread, used, notifications) = row
            source_files.append(relative)
            data_list.append((
                _timestamp(chat_ts),
                _timestamp(created_at),
                _timestamp(updated_at),
                _text(display_name) or _text(local_name),
                _text(full_name),
                _text(alias),
                _text(short_descr),
                _text(incognito),
                _text(favourite),
                _text(deleted),
                _text(status),
                _text(unread),
                _text(used),
                _text(notifications),
                _text(contact_link),
                _text(contact_id),
                relative,
            ))
        connection.close()

    data_list.sort(key=lambda r: (str(r[0]), str(r[15])), reverse=True)

    data_headers = (
        ('Last Chat', 'datetime'),
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Display Name',
        'Full Name',
        'Local Alias',
        'Short Description',
        'Incognito (as stored)',
        'Favourite (as stored)',
        'Deleted (as stored)',
        'Status (as stored)',
        'Unread Chat (as stored)',
        'Contact Used (as stored)',
        'Notifications (as stored)',
        'Contact Link',
        'Contact ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def simplex_files(context):
    data_list = []
    source_files = []

    present = {os.path.basename(str(f)) for f in unique_files(context)
               if '/app_files/' in str(f).replace('\\', '/')}

    for relative, connection in _databases(context):
        names = _contact_names(connection)
        for row in _rows(connection, '''
                SELECT created_at, updated_at, file_name, file_path, file_size,
                       ci_file_status, contact_id, group_id, protocol, cancelled,
                       file_crypto_key, file_crypto_nonce, chat_item_id, file_id
                FROM files'''):
            (created_at, updated_at, file_name, file_path, file_size, status, contact_id,
             group_id, protocol, cancelled, crypto_key, crypto_nonce, chat_item_id,
             file_id) = row
            stored_name = os.path.basename(_text(file_path)) or _text(file_name)
            source_files.append(relative)
            data_list.append((
                _timestamp(created_at),
                _timestamp(updated_at),
                _text(file_name),
                'Yes' if stored_name and stored_name in present else 'No',
                _text(file_size),
                _text(status),
                names.get(contact_id, _text(contact_id)),
                _text(protocol),
                _text(cancelled),
                'Yes' if crypto_key else 'No',
                len(crypto_key) if crypto_key else '',
                len(crypto_nonce) if crypto_nonce else '',
                _text(file_path),
                _text(group_id),
                _text(chat_item_id),
                _text(file_id),
                relative,
            ))
        connection.close()

    data_list.sort(key=lambda r: (str(r[0]), str(r[15])), reverse=True)

    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'File Name',
        'File Present',
        'File Size (as stored)',
        'Transfer Status (as stored)',
        'Contact',
        'Protocol (as stored)',
        'Cancelled (as stored)',
        'Stored Encrypted',
        'Key Length',
        'Nonce Length',
        'File Path (as stored)',
        'Group ID',
        'Chat Item ID',
        'File ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def simplex_message_edits(context):
    data_list = []
    source_files = []

    for relative, connection in _databases(context):
        for row in _rows(connection, '''
                SELECT v.item_version_ts, v.created_at, v.updated_at, v.msg_content,
                       i.item_text, i.item_sent, v.chat_item_id, v.chat_item_version_id
                FROM chat_item_versions v
                LEFT JOIN chat_items i ON i.chat_item_id = v.chat_item_id'''):
            (version_ts, created_at, updated_at, content, current_text, item_sent,
             chat_item_id, version_id) = row
            source_files.append(relative)
            data_list.append((
                _timestamp(version_ts),
                _timestamp(created_at),
                _timestamp(updated_at),
                'Sent' if item_sent else 'Received',
                _text(content),
                _text(current_text),
                _text(chat_item_id),
                _text(version_id),
                relative,
            ))
        connection.close()

    data_list.sort(key=lambda r: (str(r[0]), str(r[7])), reverse=True)

    data_headers = (
        ('Version Time', 'datetime'),
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Direction',
        'Earlier Content (as stored)',
        'Current Message Text',
        'Chat Item ID',
        'Version ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def simplex_reactions(context):
    data_list = []
    source_files = []

    for relative, connection in _databases(context):
        names = _contact_names(connection)
        for row in _rows(connection, '''
                SELECT reaction_ts, created_at, updated_at, reaction, reaction_sent,
                       contact_id, group_id, shared_msg_id, chat_item_reaction_id
                FROM chat_item_reactions'''):
            (reaction_ts, created_at, updated_at, reaction, sent, contact_id, group_id,
             shared_msg_id, reaction_id) = row
            source_files.append(relative)
            data_list.append((
                _timestamp(reaction_ts),
                _timestamp(created_at),
                _timestamp(updated_at),
                'Sent' if sent else 'Received',
                _text(reaction),
                names.get(contact_id, _text(contact_id)),
                _text(group_id),
                _text(shared_msg_id),
                _text(reaction_id),
                relative,
            ))
        connection.close()

    data_list.sort(key=lambda r: (str(r[0]), str(r[8])), reverse=True)

    data_headers = (
        ('Reaction Time', 'datetime'),
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Direction',
        'Reaction (as stored)',
        'Contact',
        'Group ID',
        'Shared Message ID',
        'Reaction ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
