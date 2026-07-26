__artifacts_v2__ = {
    "get_signalMessages": {
        "name": "Signal - Messages",
        "description": "Parses messages from the encrypted Signal database, including sender, recipient, direction and body.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json, produced by the extraction tool. Without it the database cannot be read.",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
    "get_signalCalls": {
        "name": "Signal - Calls",
        "description": "Parses the Signal call log, including call type, direction and outcome.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json.",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "phone",
    },
    "get_signalContacts": {
        "name": "Signal - Contacts",
        "description": "Parses Signal recipients, including phone numbers, ACI/PNI identifiers, usernames and profile names.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json.",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_signalAttachments": {
        "name": "Signal - Attachments",
        "description": "Parses metadata for attachments referenced by Signal messages.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Signal",
        "notes": "Attachment files are decrypted with the modernKey from secrets.json and each attachment's data_random. The stored file format is detected from its content, which can differ from the content type recorded in the database.",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',
                  '*/org.thoughtcrime.securesms/app_parts/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
}

import base64
import hashlib
import hmac
import json
import mimetypes
import os
import sqlite3
import tempfile

from Crypto.Cipher import AES
from Crypto.Util import Counter

from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.ilapfuncs import (artifact_processor, logfunc, convert_unix_ts_to_utc,
                               check_in_embedded_media)

SECRETS_GLOB = '*/Secrets/secrets.json'
SIGNAL_PACKAGE = 'org.thoughtcrime.securesms'

# Signal keys the database with the hex string as a passphrase and skips key
# stretching (kdf_iter = 1) because the stored key is already random.
SIGNAL_KDF_ITERATIONS = 1
SIGNAL_PAGE_SIZE = 4096
SIGNAL_HMAC = 'sha1'

# MessageTypes.java base types (type & 0x1F)
MESSAGE_BASE_TYPE_MASK = 0x1F
MESSAGE_DIRECTIONS = {
    20: 'Incoming',
    21: 'Outgoing',
    22: 'Outgoing',
    23: 'Outgoing',
    24: 'Outgoing',
    27: 'Draft',
}
MESSAGE_STATUS = {21: 'Outbox', 22: 'Sending', 23: 'Sent', 24: 'Failed', 27: 'Draft'}

RECIPIENT_TYPES = {0: 'Individual', 1: 'MMS', 2: 'Group', 3: 'Distribution list', 4: 'Call link'}
CALL_TYPES = {0: 'Audio', 1: 'Video', 3: 'Group', 4: 'Ad hoc'}
CALL_DIRECTIONS = {0: 'Incoming', 1: 'Outgoing'}
CALL_EVENTS = {
    0: 'Ongoing', 1: 'Accepted', 2: 'Not accepted', 3: 'Missed', 4: 'Deleted',
    5: 'Generic group call', 6: 'Joined', 7: 'Ringing', 8: 'Declined',
    9: 'Outgoing ring', 10: 'Missed (notification profile)',
}

# One decryption per database per run, shared by the artifacts in this module
_decrypted_cache = {}
_secrets_cache = {}


def _read_signal_keys(secrets_path):
    """Return (database_key, attachment_key) from an extraction secrets.json."""
    database_key = attachment_key = None
    try:
        with open(secrets_path, 'r', encoding='utf-8') as secrets_file:
            secrets = json.load(secrets_file)
    except (OSError, ValueError) as error:
        logfunc(f'Signal: could not read {secrets_path}: {error}')
        return None, None

    if not isinstance(secrets, list):
        return None, None
    for entry in secrets:
        if not isinstance(entry, dict) or entry.get('app') != SIGNAL_PACKAGE:
            continue
        for item in entry.get('script_output', []):
            payload = item.get('payload') if isinstance(item, dict) else None
            if not isinstance(payload, dict):
                continue
            if payload.get('sqlite db key'):
                database_key = payload['sqlite db key']
            attachment = payload.get('signal attachment key')
            if isinstance(attachment, dict) and attachment.get('modernKey'):
                attachment_key = attachment['modernKey']
    return database_key, attachment_key


def _signal_secrets(context):
    """Find and cache Signal's keys from the extraction's secrets.json."""
    if 'keys' in _secrets_cache:
        return _secrets_cache['keys']

    _secrets_cache['keys'] = (None, None)
    seeker = context.get_seeker()
    secrets_files = [str(path) for path in seeker.search(SECRETS_GLOB)
                     if os.path.basename(str(path)) == 'secrets.json']
    if not secrets_files:
        logfunc('Signal: no Secrets/secrets.json found, the data stays encrypted')
        return _secrets_cache['keys']

    for secrets_path in secrets_files:
        database_key, attachment_key = _read_signal_keys(secrets_path)
        if database_key or attachment_key:
            _secrets_cache['keys'] = (database_key, attachment_key)
            break
    return _secrets_cache['keys']


def _decrypted_database(context, database_path):
    """Decrypt the Signal database once per run; return a path or None."""
    if database_path in _decrypted_cache:
        return _decrypted_cache[database_path]

    _decrypted_cache[database_path] = None  # avoid retrying on later artifacts

    database_key, _ = _signal_secrets(context)
    if not database_key:
        logfunc('Signal: secrets.json has no "sqlite db key" entry for Signal')
        return None

    digest = hashlib.sha1(database_path.encode('utf-8', 'replace')).hexdigest()[:12]
    output_path = os.path.join(tempfile.gettempdir(), 'aleapp_signal', f'signal_{digest}.db')
    try:
        pages, verified = decrypt_sqlcipher_db(
            database_path, database_key, output_path,
            page_size=SIGNAL_PAGE_SIZE, kdf_iterations=SIGNAL_KDF_ITERATIONS,
            hmac_algorithm=SIGNAL_HMAC, kdf_algorithm=SIGNAL_HMAC)
    except Exception as error:  # pylint: disable=broad-except
        logfunc(f'Signal: decryption failed for {database_path}: {error}')
        return None

    if not pages or not verified:
        logfunc('Signal: the key did not authenticate the database, it may belong to another '
                'extraction or the app data was updated after the key was captured')
        return None
    if verified != pages:
        logfunc(f'Signal: {pages - verified} of {pages} decrypted pages failed HMAC '
                'verification, the recovered data may be incomplete')

    _decrypted_cache[database_path] = output_path
    return output_path


def _open_signal_database(context):
    """Yield (connection, source_path) for each decryptable Signal database."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'signal.db':
            continue
        decrypted = _decrypted_database(context, file_found)
        if not decrypted:
            continue
        yield sqlite3.connect(decrypted), file_found


def _display_name(profile_name, system_name, phone_number, username):
    return profile_name or system_name or phone_number or username or ''


def _decrypt_attachment(modern_key, data_random, blob):
    """Decrypt a Signal attachment blob.

    Signal derives a per-file key with HMAC-SHA256(modernKey, data_random) and
    encrypts with AES-CTR from a zero counter, so the stored file is exactly the
    size of the plaintext.
    """
    key = hmac.new(modern_key, data_random, hashlib.sha256).digest()
    counter = Counter.new(128, initial_value=0)
    return AES.new(key, AES.MODE_CTR, counter=counter).decrypt(blob)


def _detect_format(data, recorded_type=None):
    """Return (extension, mime) for decrypted attachment bytes.

    The format is sniffed from the content because Signal's recorded
    content_type does not always match what is stored. Where the bytes are not
    conclusive, such as the ZIP container shared by Office documents, the
    recorded type fills in the detail.
    """
    for magic, extension, mime in (
            (b'\xff\xd8\xff', 'jpg', 'image/jpeg'),
            (b'\x89PNG\r\n\x1a\n', 'png', 'image/png'),
            (b'GIF8', 'gif', 'image/gif'),
            (b'OggS', 'ogg', 'audio/ogg'),
            (b'%PDF', 'pdf', 'application/pdf'),
            (b'\x1aE\xdf\xa3', 'webm', 'video/webm'),
            (b'ID3', 'mp3', 'audio/mpeg'),
    ):
        if data.startswith(magic):
            return extension, mime
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp', 'image/webp'
    if data[4:8] == b'ftyp':
        return 'mp4', 'video/mp4'

    # ZIP container: Office documents and similar, so trust the recorded type
    if data[:4] in (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'):
        extension = mimetypes.guess_extension(recorded_type or '') if recorded_type else None
        return (extension or '.zip').lstrip('.'), recorded_type or 'application/zip'

    if recorded_type:
        extension = mimetypes.guess_extension(recorded_type)
        if extension:
            return extension.lstrip('.'), recorded_type
    return 'bin', None


def _attachment_files(context):
    """Map app_parts file names to their extracted paths."""
    seeker = context.get_seeker()
    found = {}
    for path in seeker.search(f'*/{SIGNAL_PACKAGE}/app_parts/*'):
        path = str(path)
        if os.path.isfile(path):
            found[os.path.basename(path)] = path
    return found


def _table_columns(connection, table):
    return {row[1] for row in connection.execute(f'PRAGMA table_info({table})')}


def _select_list(available, table_alias, columns):
    """Build SELECT expressions, substituting NULL for columns this Signal version lacks.

    Signal's schema changes between releases, so a query pinned to one version's
    columns fails outright on another.
    """
    expressions = []
    for column in columns:
        if column in available:
            expressions.append(f'{table_alias}.{column}')
        else:
            expressions.append('NULL')
    return ', '.join(expressions)


@artifact_processor
def get_signalMessages(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        cursor = connection.cursor()
        message_columns = _table_columns(connection, 'message')
        cursor.execute(f'''
        SELECT
            {_select_list(message_columns, 'message',
                          ['date_sent', 'date_received', 'thread_id', 'type', 'body'])},
            sender.e164, sender.profile_joined_name, sender.system_joined_name, sender.username,
            receiver.e164, receiver.profile_joined_name, receiver.system_joined_name, receiver.username,
            {_select_list(message_columns, 'message',
                          ['read', 'remote_deleted', 'view_once', 'quote_body', 'expires_in'])}
        FROM message
        LEFT JOIN recipient AS sender ON message.from_recipient_id = sender._id
        LEFT JOIN recipient AS receiver ON message.to_recipient_id = receiver._id
        ORDER BY message.date_sent
        ''')
        for row in cursor:
            base_type = row[3] & MESSAGE_BASE_TYPE_MASK if row[3] is not None else None
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                row[2],
                MESSAGE_DIRECTIONS.get(base_type, 'Unknown'),
                MESSAGE_STATUS.get(base_type, ''),
                _display_name(row[6], row[7], row[5], row[8]),
                row[5] or '',
                _display_name(row[10], row[11], row[9], row[12]),
                row[9] or '',
                row[4] or '',
                'Yes' if row[13] else 'No',
                'Yes' if row[14] else 'No',
                'Yes' if row[15] else 'No',
                row[16] or '',
                row[17] or '',
            ))
        connection.close()

    data_headers = (
        ('Date Sent', 'datetime'),
        ('Date Received', 'datetime'),
        'Thread ID',
        'Direction',
        'Status',
        'Sender',
        'Sender Phone Number',
        'Recipient',
        'Recipient Phone Number',
        'Message',
        'Read',
        'Remote Deleted',
        'View Once',
        'Quoted Message',
        'Disappearing Timer (Seconds)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalCalls(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        cursor = connection.cursor()
        call_columns = _table_columns(connection, 'call')
        cursor.execute(f'''
        SELECT
            {_select_list(call_columns, 'call',
                          ['timestamp', 'call_id', 'type', 'direction', 'event'])},
            peer.e164, peer.profile_joined_name, peer.system_joined_name, peer.username,
            {_select_list(call_columns, 'call', ['read', 'deletion_timestamp'])}
        FROM call
        LEFT JOIN recipient AS peer ON call.peer = peer._id
        ORDER BY call.timestamp
        ''')
        for row in cursor:
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                _display_name(row[6], row[7], row[5], row[8]),
                row[5] or '',
                CALL_TYPES.get(row[2], f'Unknown ({row[2]})'),
                CALL_DIRECTIONS.get(row[3], f'Unknown ({row[3]})'),
                CALL_EVENTS.get(row[4], f'Unknown ({row[4]})'),
                'Yes' if row[9] else 'No',
                convert_unix_ts_to_utc(row[10]) if row[10] else '',
                row[1],
            ))
        connection.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Contact',
        'Phone Number',
        'Call Type',
        'Direction',
        'Outcome',
        'Read',
        ('Deleted Timestamp', 'datetime'),
        'Call ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalContacts(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        cursor = connection.cursor()
        recipient_columns = _table_columns(connection, 'recipient')
        cursor.execute(f'''
        SELECT
            {_select_list(recipient_columns, 'recipient',
                          ['_id', 'type', 'e164', 'username', 'aci', 'pni',
                           'profile_joined_name', 'system_joined_name', 'profile_given_name',
                           'profile_family_name', 'registered', 'blocked', 'hidden', 'about',
                           'note', 'last_profile_fetch'])}
        FROM recipient
        ORDER BY recipient._id
        ''')
        for row in cursor:
            data_list.append((
                _display_name(row[6], row[7], row[2], row[3]),
                row[2] or '',
                row[3] or '',
                RECIPIENT_TYPES.get(row[1], f'Unknown ({row[1]})'),
                row[4] or '',
                row[5] or '',
                'Yes' if row[11] else 'No',
                'Yes' if row[12] else 'No',
                row[13] or '',
                row[14] or '',
                convert_unix_ts_to_utc(row[15]) if row[15] else '',
                row[0],
            ))
        connection.close()

    data_headers = (
        'Name',
        'Phone Number',
        'Username',
        'Recipient Type',
        'ACI',
        'PNI',
        'Blocked',
        'Hidden',
        'About',
        'Note',
        ('Last Profile Fetch', 'datetime'),
        'Recipient ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalAttachments(context):
    data_list = []
    source_path = ''
    _, attachment_key = _signal_secrets(context)
    modern_key = None
    if attachment_key:
        try:
            modern_key = base64.b64decode(attachment_key + '==')
        except (ValueError, TypeError):
            logfunc('Signal: the attachment modernKey is not valid base64')
    if not modern_key:
        logfunc('Signal: no attachment modernKey available, reporting metadata only')

    stored_files = _attachment_files(context) if modern_key else {}
    decrypted_count = 0

    for connection, source_path in _open_signal_database(context):
        cursor = connection.cursor()
        attachment_columns = _table_columns(connection, 'attachment')
        cursor.execute(f'''
        SELECT
            message.date_sent,
            {_select_list(attachment_columns, 'attachment',
                          ['file_name', 'content_type', 'data_size', 'data_file',
                           'transfer_state', 'voice_note', 'video_gif', 'width', 'height',
                           'caption', 'upload_timestamp', 'message_id', 'data_random'])}
        FROM attachment
        LEFT JOIN message ON attachment.message_id = message._id
        ORDER BY message.date_sent
        ''')
        for row in cursor:
            media_reference = ''
            detected_type = ''
            stored_path = row[4] or ''
            data_random = row[13]
            file_on_disk = stored_files.get(os.path.basename(stored_path)) if stored_path else None

            if modern_key and data_random and file_on_disk:
                try:
                    with open(file_on_disk, 'rb') as blob_file:
                        plaintext = _decrypt_attachment(modern_key, data_random, blob_file.read())
                    extension, mime = _detect_format(plaintext, row[2])
                    detected_type = mime or 'unknown'
                    name = row[1] or f'signal_attachment_{row[12]}.{extension}'
                    media_reference = check_in_embedded_media(
                        file_on_disk, plaintext, name=name,
                        force_type=mime, force_extension=extension)
                    decrypted_count += 1
                except Exception as error:  # pylint: disable=broad-except
                    logfunc(f'Signal: could not decrypt {os.path.basename(stored_path)}: {error}')

            data_list.append((
                convert_unix_ts_to_utc(row[0]) if row[0] else '',
                media_reference,
                row[1] or '',
                row[2] or '',
                detected_type,
                row[3] or '',
                stored_path,
                row[5],
                'Yes' if row[6] else 'No',
                'Yes' if row[7] else 'No',
                f'{row[8]}x{row[9]}' if row[8] and row[9] else '',
                row[10] or '',
                convert_unix_ts_to_utc(row[11]) if row[11] else '',
                row[12],
            ))
        connection.close()

    if decrypted_count:
        logfunc(f'Signal: decrypted {decrypted_count} attachment'
                f'{"s" if decrypted_count > 1 else ""}')

    data_headers = (
        ('Message Date Sent', 'datetime'),
        ('Attachment', 'media'),
        'File Name',
        'Recorded Content Type',
        'Detected Content Type',
        'Size (Bytes)',
        'Stored File',
        'Transfer State',
        'Voice Note',
        'Video GIF',
        'Dimensions',
        'Caption',
        ('Upload Timestamp', 'datetime'),
        'Message ID',
    )
    return data_headers, data_list, source_path
