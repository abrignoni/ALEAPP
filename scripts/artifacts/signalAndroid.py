__artifacts_v2__ = {
    "get_signalMessages": {
        "name": "Signal - Messages",
        "description": "Parses messages from the encrypted Signal database, including sender, recipient, direction and body.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json, produced by the extraction tool. Without it the database cannot be read. Signal stores expires_in in milliseconds, so the disappearing-message timer is divided by 1000 and reported in seconds. Direction and status are decoded from the MessageTypes base type, the low five bits of the message type column. Reference: Signal-Android, 'MessageTable.kt (expires_in stored in milliseconds)', https://github.com/signalapp/Signal-Android/blob/main/app/src/main/java/org/thoughtcrime/securesms/database/MessageTable.kt. Reference: Signal-Android, 'MessageTypes.java and CallTable.kt', https://github.com/signalapp/Signal-Android/blob/main/app/src/main/java/org/thoughtcrime/securesms/database/MessageTypes.java",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_pixel8pro_a16": "20 rows",
            "pixel7a_a14": "34 rows",
            "russell_pixel6a_a13": "61 rows",
            "sharon_a14": "45 rows",
        },
    },
    "get_signalCalls": {
        "name": "Signal - Calls",
        "description": "Parses the Signal call log, including call type, direction and outcome.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json. Call type, direction and outcome are the Type, Direction and Event values defined by CallTable, which lists call types 0 Audio, 1 Video, 3 Group and 4 Ad hoc with no type 2; codes outside those sets are reported with their raw value. Reference: Signal-Android, 'MessageTypes.java and CallTable.kt', https://github.com/signalapp/Signal-Android/blob/main/app/src/main/java/org/thoughtcrime/securesms/database/MessageTypes.java",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "hc_pixel8pro_a16": "3 rows",
            "pixel7a_a14": "4 rows",
            "russell_pixel6a_a13": "0 rows",
            "sharon_a14": "3 rows",
        },
    },
    "get_signalContacts": {
        "name": "Signal - Contacts",
        "description": "Parses Signal recipients, including phone numbers, ACI/PNI identifiers, usernames and profile names.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json.",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "4 rows",
            "pixel7a_a14": "15 rows",
            "russell_pixel6a_a13": "6 rows",
            "sharon_a14": "25 rows",
        },
    },
    "get_signalGroups": {
        "name": "Signal - Groups",
        "description": "Parses Signal groups and their membership, including group title, member names and creation time.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the SQLCipher key from extra/Secrets/secrets.json.",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "russell_pixel6a_a13": "0 rows",
            "sharon_a14": "1 row",
        },
    },
    "get_signalAttachments": {
        "name": "Signal - Attachments",
        "description": "Parses metadata for attachments referenced by Signal messages.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Signal",
        "notes": "Attachment files are decrypted with the modernKey from secrets.json and each attachment's data_random. The stored file format is detected from its content, which can differ from the content type recorded in the database. The Direction column is decoded from the MessageTypes base type of the message the attachment belongs to. Attachments are read from the attachment table where a release has one and from the part table otherwise, whose equivalent columns are mid, ct and _data; both are joined to the message table on the message id, so each attachment carries the date, thread, sender and direction of the message it belongs to. The part schema has no transfer_state column, so Transfer State is empty for databases using it. Reference: Signal-Android, 'MessageTypes.java and CallTable.kt', https://github.com/signalapp/Signal-Android/blob/main/app/src/main/java/org/thoughtcrime/securesms/database/MessageTypes.java",
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',
                  '*/org.thoughtcrime.securesms/app_parts/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "hc_pixel8pro_a16": "7 rows",
            "pixel7a_a14": "9 rows",
            "russell_pixel6a_a13": "8 rows",
            "sharon_a14": "10 rows",
        },
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


def _modern_key(context):
    """Return the raw attachment key, or None when it is unavailable."""
    _, attachment_key = _signal_secrets(context)
    if not attachment_key:
        return None
    try:
        return base64.b64decode(attachment_key + '==')
    except (ValueError, TypeError):
        logfunc('Signal: the attachment modernKey is not valid base64')
        return None


# Older Signal releases keep attachments in a "part" table with a different
# column vocabulary. Both generations are read by resolving the table and the
# column names per database, the same way the recipient and message columns are.
ATTACHMENT_TABLE_NAMES = ('attachment', 'part')
LEGACY_ATTACHMENT_COLUMNS = {
    'message_id': 'mid',
    'content_type': 'ct',
    'data_file': '_data',
}


def _attachment_table(connection):
    """Return (table name, columns) for whichever attachment store exists."""
    for table in ATTACHMENT_TABLE_NAMES:
        columns = _table_columns(connection, table)
        if columns:
            return table, columns
    return '', set()


def _attachment_name(columns, name):
    """Return the column this schema uses for a modern attachment column."""
    for candidate in (name, LEGACY_ATTACHMENT_COLUMNS.get(name)):
        if candidate and candidate in columns:
            return candidate
    return ''


def _attachment_column(columns, table, name):
    """Qualified attachment column for this schema, or NULL when absent."""
    resolved = _attachment_name(columns, name)
    return f'{table}.{resolved}' if resolved else 'NULL'


def _attachment_select(columns, table, names):
    """SELECT expressions for attachment columns across both schemas."""
    return ', '.join(_attachment_column(columns, table, name) for name in names)


def _checked_in_attachments(connection, modern_key, stored_files):
    """Decrypt every attachment and group the media references by message.

    check_in_embedded_media keys media on a hash of the content, so decrypting
    the same attachment for both the message and the attachment artifact
    registers it once and returns the same reference.

    Returns (references_by_message_id, detected_type_by_attachment_id,
    thumbnail_reference_by_attachment_id).
    """
    references = {}
    detected_types = {}
    thumbnails = {}
    if not modern_key:
        return references, detected_types, thumbnails

    attachment_table, attachment_columns = _attachment_table(connection)
    if not attachment_table or not all(
            _attachment_name(attachment_columns, name) for name in ('data_file', 'data_random')):
        return references, detected_types, thumbnails

    cursor = connection.cursor()
    cursor.execute(f'''
    SELECT {_attachment_select(attachment_columns, attachment_table,
                               ['_id', 'message_id', 'data_file', 'data_random',
                                'content_type', 'file_name', 'thumbnail_file',
                                'thumbnail_random'])}
    FROM {attachment_table}
    ''')
    for row in cursor:
        (attachment_id, message_id, data_file, data_random,
         content_type, file_name, thumbnail_file, thumbnail_random) = row

        # Signal stores a separate, smaller copy for some attachments. It uses the
        # same per-file scheme with its own random, and can outlive the full file.
        for blob_name, blob_random, is_thumbnail in (
                (data_file, data_random, False),
                (thumbnail_file, thumbnail_random, True)):
            if not blob_name or not blob_random:
                continue
            path = stored_files.get(os.path.basename(blob_name))
            if not path:
                continue
            try:
                with open(path, 'rb') as blob_file:
                    plaintext = _decrypt_attachment(modern_key, blob_random, blob_file.read())
                extension, mime = _detect_format(plaintext, content_type)
                label = 'thumbnail' if is_thumbnail else 'attachment'
                default_name = f'signal_{label}_{attachment_id}.{extension}'
                name = default_name if is_thumbnail else (file_name or default_name)
                reference = check_in_embedded_media(
                    path, plaintext, name=name, force_type=mime, force_extension=extension)
            except Exception as error:  # pylint: disable=broad-except
                logfunc(f'Signal: could not decrypt {os.path.basename(blob_name)}: {error}')
                continue

            if is_thumbnail:
                thumbnails[attachment_id] = reference
            else:
                detected_types[attachment_id] = mime or 'unknown'
                if reference and message_id is not None:
                    references.setdefault(message_id, []).append(reference)
    return references, detected_types, thumbnails


def _table_columns(connection, table):
    return {row[1] for row in connection.execute(f'PRAGMA table_info({table})')}


def _expires_in_seconds(value):
    """Signal writes expires_in in milliseconds, so report the timer in seconds."""
    if not value:
        return ''
    try:
        milliseconds = int(value)
    except (TypeError, ValueError):
        return value
    return milliseconds // 1000 if milliseconds % 1000 == 0 else milliseconds / 1000


# Signal renames recipient columns between releases. Older schemas store the
# phone number in "phone" and the contact name in "system_display_name", where
# newer ones use "e164" and "system_joined_name". Resolve per database rather
# than pinning to one release, the same way _select_list already does for the
# message table.
RECIPIENT_COLUMN_ALIASES = {
    'e164': ('e164', 'phone'),
    'system_joined_name': ('system_joined_name', 'system_display_name'),
}


def _recipient_column(available, table_alias, column):
    """Return the qualified column this Signal version actually has, or NULL."""
    for candidate in RECIPIENT_COLUMN_ALIASES.get(column, (column,)):
        if candidate in available:
            return f'{table_alias}.{candidate}'
    return 'NULL'


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
    modern_key = _modern_key(context)
    stored_files = _attachment_files(context) if modern_key else {}

    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        attachments_by_message, _, _ = _checked_in_attachments(
            connection, modern_key, stored_files)

        # Signal stores the quoted message's send time in quote_id, so the
        # original can be resolved back to its own row
        original_by_sent_time = {}
        for sent, message_id in connection.execute(
                'SELECT date_sent, _id FROM message WHERE date_sent IS NOT NULL'):
            original_by_sent_time.setdefault(sent, message_id)

        cursor = connection.cursor()
        message_columns = _table_columns(connection, 'message')
        cursor.execute(f'''
        SELECT
            {_select_list(message_columns, 'message',
                          ['date_sent', 'date_received', 'thread_id', 'type', 'body', '_id'])},
            {_recipient_column(recipient_columns, 'sender', 'e164')}, {_recipient_column(recipient_columns, 'sender', 'profile_joined_name')}, {_recipient_column(recipient_columns, 'sender', 'system_joined_name')}, {_recipient_column(recipient_columns, 'sender', 'username')},
            {_recipient_column(recipient_columns, 'receiver', 'e164')}, {_recipient_column(recipient_columns, 'receiver', 'profile_joined_name')}, {_recipient_column(recipient_columns, 'receiver', 'system_joined_name')}, {_recipient_column(recipient_columns, 'receiver', 'username')},
            {_select_list(message_columns, 'message',
                          ['read', 'remote_deleted', 'view_once', 'quote_body', 'expires_in',
                           'quote_id', 'quote_missing'])},
            COALESCE(NULLIF({_recipient_column(recipient_columns, 'quoted', 'profile_joined_name')}, ''),
                     NULLIF({_recipient_column(recipient_columns, 'quoted', 'system_joined_name')}, ''),
                     NULLIF({_recipient_column(recipient_columns, 'quoted', 'e164')}, ''), NULLIF({_recipient_column(recipient_columns, 'quoted', 'username')}, ''), '')
        FROM message
        LEFT JOIN recipient AS sender ON message.from_recipient_id = sender._id
        LEFT JOIN recipient AS receiver ON message.to_recipient_id = receiver._id
        LEFT JOIN recipient AS quoted ON message.quote_author = quoted._id
        ORDER BY message.date_sent
        ''')
        for row in cursor:
            base_type = row[3] & MESSAGE_BASE_TYPE_MASK if row[3] is not None else None
            # A message can carry several attachments, so the media cell takes a list
            attachments = attachments_by_message.get(row[5], [])
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                row[2],
                MESSAGE_DIRECTIONS.get(base_type, 'Unknown'),
                MESSAGE_STATUS.get(base_type, ''),
                _display_name(row[7], row[8], row[6], row[9]),
                row[6] or '',
                _display_name(row[11], row[12], row[10], row[13]),
                row[10] or '',
                row[4] or '',
                attachments,
                len(attachments),
                'Yes' if row[14] else 'No',
                'Yes' if row[15] else 'No',
                'Yes' if row[16] else 'No',
                row[17] or '',
                row[21] or '',
                convert_unix_ts_to_utc(row[19]) if row[19] else '',
                original_by_sent_time.get(row[19], '') if row[19] else '',
                'Yes' if row[20] else 'No',
                _expires_in_seconds(row[18]),
                row[5],
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
        ('Attachments', 'media'),
        'Attachment Count',
        'Read',
        'Remote Deleted',
        'View Once',
        'Quoted Message',
        'Quoted Author',
        ('Quoted Message Sent', 'datetime'),
        'Quoted Message ID',
        'Quoted Original Missing',
        'Disappearing Timer (Seconds)',
        'Message ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalCalls(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        cursor = connection.cursor()
        call_columns = _table_columns(connection, 'call')
        cursor.execute(f'''
        SELECT
            {_select_list(call_columns, 'call',
                          ['timestamp', 'call_id', 'type', 'direction', 'event'])},
            {_recipient_column(recipient_columns, 'peer', 'e164')}, {_recipient_column(recipient_columns, 'peer', 'profile_joined_name')}, {_recipient_column(recipient_columns, 'peer', 'system_joined_name')}, {_recipient_column(recipient_columns, 'peer', 'username')},
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
def get_signalGroups(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        group_columns = _table_columns(connection, 'groups')
        if not group_columns:
            connection.close()
            continue

        # Membership lives in its own table, keyed by the textual group id
        members_by_group = {}
        if _table_columns(connection, 'group_membership'):
            for group_id, name in connection.execute(f'''
                SELECT group_membership.group_id,
                       COALESCE(NULLIF({_recipient_column(recipient_columns, 'recipient', 'profile_joined_name')}, ''),
                                NULLIF({_recipient_column(recipient_columns, 'recipient', 'system_joined_name')}, ''),
                                NULLIF({_recipient_column(recipient_columns, 'recipient', 'e164')}, ''),
                                NULLIF({_recipient_column(recipient_columns, 'recipient', 'username')}, ''))
                FROM group_membership
                LEFT JOIN recipient ON group_membership.recipient_id = recipient._id
            '''):
                members_by_group.setdefault(group_id, []).append(name or 'Unknown')

        cursor = connection.cursor()
        cursor.execute(f'''
        SELECT {_select_list(group_columns, 'groups',
                             ['_id', 'group_id', 'title', 'timestamp', 'active', 'mms',
                              'revision', 'last_force_update_timestamp'])},
               COALESCE(NULLIF({_recipient_column(recipient_columns, 'recipient', 'profile_joined_name')}, ''),
                        NULLIF({_recipient_column(recipient_columns, 'recipient', 'system_joined_name')}, ''), '')
        FROM groups
        LEFT JOIN recipient ON groups.recipient_id = recipient._id
        ORDER BY groups.timestamp
        ''')
        for row in cursor:
            members = members_by_group.get(row[1], [])
            data_list.append((
                convert_unix_ts_to_utc(row[3]) if row[3] else '',
                row[2] or row[8] or '',
                len(members),
                ', '.join(members),
                'Yes' if row[4] else 'No',
                'Yes' if row[5] else 'No',
                row[6],
                convert_unix_ts_to_utc(row[7]) if row[7] else '',
                row[1] or '',
            ))
        connection.close()

    data_headers = (
        ('Created Timestamp', 'datetime'),
        'Group Title',
        'Member Count',
        'Members',
        'Active',
        'MMS Group',
        'Revision',
        ('Last Forced Update', 'datetime'),
        'Group ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalContacts(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
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
    modern_key = _modern_key(context)
    if not modern_key:
        logfunc('Signal: no attachment modernKey available, reporting metadata only')
    stored_files = _attachment_files(context) if modern_key else {}
    decrypted_count = 0

    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        references, detected_types, thumbnails = _checked_in_attachments(
            connection, modern_key, stored_files)
        decrypted_count += len(detected_types)

        cursor = connection.cursor()
        attachment_table, attachment_columns = _attachment_table(connection)
        if not attachment_table:
            logfunc(f'Signal: {source_path} carries no attachment table, so no '
                    'attachments are reported for it')
            connection.close()
            continue
        message_id_column = _attachment_column(
            attachment_columns, attachment_table, 'message_id')
        cursor.execute(f'''
        SELECT
            message.date_sent,
            {_attachment_select(attachment_columns, attachment_table,
                                ['_id', 'file_name', 'content_type', 'data_size', 'data_file',
                                 'transfer_state', 'voice_note', 'video_gif', 'width', 'height',
                                 'caption', 'upload_timestamp', 'message_id'])},
            message.thread_id, message.type,
            {_recipient_column(recipient_columns, 'sender', 'e164')}, {_recipient_column(recipient_columns, 'sender', 'profile_joined_name')}, {_recipient_column(recipient_columns, 'sender', 'system_joined_name')}, {_recipient_column(recipient_columns, 'sender', 'username')}
        FROM {attachment_table}
        LEFT JOIN message ON {message_id_column} = message._id
        LEFT JOIN recipient AS sender ON message.from_recipient_id = sender._id
        ORDER BY message.date_sent
        ''')
        for row in cursor:
            attachment_id = row[1]
            message_id = row[13]
            base_type = row[15] & MESSAGE_BASE_TYPE_MASK if row[15] is not None else None
            # Same media reference the message row uses, so both views point at one copy
            media = [ref for ref in references.get(message_id, [])] if message_id is not None else []
            own_media = media[0] if len(media) == 1 else media

            data_list.append((
                convert_unix_ts_to_utc(row[0]) if row[0] else '',
                own_media,
                thumbnails.get(attachment_id, ''),
                row[2] or '',
                row[3] or '',
                detected_types.get(attachment_id, ''),
                row[4] or '',
                row[5] or '',
                row[6],
                'Yes' if row[7] else 'No',
                'Yes' if row[8] else 'No',
                f'{row[9]}x{row[10]}' if row[9] and row[10] else '',
                row[11] or '',
                convert_unix_ts_to_utc(row[12]) if row[12] else '',
                _display_name(row[17], row[18], row[16], row[19]),
                MESSAGE_DIRECTIONS.get(base_type, ''),
                row[14],
                message_id,
            ))
        connection.close()

    if decrypted_count:
        logfunc(f'Signal: decrypted {decrypted_count} attachment'
                f'{"s" if decrypted_count > 1 else ""}')

    data_headers = (
        ('Message Date Sent', 'datetime'),
        ('Attachment', 'media'),
        ('Thumbnail', 'media'),
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
        'Sender',
        'Direction',
        'Thread ID',
        'Message ID',
    )
    return data_headers, data_list, source_path
