__artifacts_v2__ = {
    "get_signalMessages": {
        "name": "Signal - Messages",
        "description": ("Parses messages from the encrypted Signal database, including sender, "
                        "recipient, conversation, direction, body, attachments, reactions, story "
                        "rows and edit revisions."),
        "author": "Alexis Brignoni, @kalink0",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Requires the SQLCipher key from extra/Secrets/secrets.json; the write-ahead log "
                  "is replayed. Direction, Status and Event Type are decoded from the message type "
                  "after MessageTypes.java. Event Type names rows that record an event rather than "
                  "a message (calls, group updates, identity changes and similar). A call row has "
                  "no body; its Message shows the call's name in square brackets, written by this "
                  "parser. No call duration is stored. Conversation is the thread's recipient "
                  "(group title, story list name or person) and labels LAVA's conversation view. "
                  "Quoted Message ID is resolved from quote_id and quote_author, as Signal does; "
                  "several matches are all listed. Reactions shows emoji, reacting recipient and "
                  "time in UTC. Each revision of an edited message is its own row, linked by "
                  "Latest Revision ID and Original Message ID. Not read: signal-logs.db, the "
                  "encryption state, the sticker and emoji catalogues, mention and group_receipts. "
                  "On pixel7a_a14 Remote Deleted, View Once and Quoted Original Missing held 'No' "
                  "on all 34 rows, and Disappearing Timer (Seconds), Parent Story ID, Revision "
                  "Number, Latest Revision ID and Original Message ID had no value on any row. "
                  "Reference: Signal-Android, 'MessageTypes.java', "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/database/MessageTypes.java"),
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',
                  '*/org.thoughtcrime.securesms/app_parts/*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_pixel8pro_a16": "20 rows",
            "pixel7a_a14": "Signal 7.11.4 | 34 rows",
            "russell_pixel6a_a13": "61 rows",
            "sharon_a14": "45 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Date Sent",
                "senderColumn": "Sender",
                "mediaColumn": "Attachments",
            }
        },
    },
    "get_signalCalls": {
        "name": "Signal - Calls",
        "description": "Parses the Signal call log, including call type, direction and outcome.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Requires the SQLCipher key from extra/Secrets/secrets.json. Call type, "
                  "direction and outcome are the Type, Direction and Event values defined by "
                  "CallTable, which lists call types 0 Audio, 1 Video, 3 Group and 4 Ad hoc with "
                  "no type 2; codes outside those sets are reported with their raw value. "
                  "Reference: Signal-Android, 'CallTable.kt (Type, Direction and Event values)', "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/database/CallTable.kt"),
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
        "description": ("Parses Signal recipients, including phone numbers, ACI/PNI identifiers, "
                        "usernames and profile names."),
        "author": "Alexis Brignoni, @kalink0",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Requires the SQLCipher key from extra/Secrets/secrets.json. Recipient Type "
                  "names the stored type after RecipientType in RecipientTable.kt at commit "
                  "ad141bb6af88ef67aea05d3d0e55cf9760fe56eb (L5158-5164), which defines "
                  "INDIVIDUAL(0), MMS(1), GV1(2), GV2(3), DISTRIBUTION_LIST(4) and CALL_LINK(5): 0 "
                  "Individual, 1 MMS, 2 Group V1, 3 Group V2, 4 Distribution list, 5 Call link, "
                  "and Unknown with the stored number for any other value. That commit is one "
                  "version of the app's source; the app versions that wrote the tested databases "
                  "were not compared with it. On pixel7a_a14 (15 rows), hc_pixel8pro_a16 (4 rows) "
                  "and sharon_a14 (25 rows) the stored type was 0 on 14, 3 and 23 rows, 4 on one "
                  "row of each image, and 3 on one row of sharon_a14. No tested row stored 1, 2 or "
                  "5. On russell_pixel6a_a13 (6 rows) no type value was read and the column shows "
                  "Unknown (None). The rows of type 3 and 4 were not compared with the groups or "
                  "distribution list tables. Avatar and Sync Avatar are the pictures in "
                  "app_avatars named after the recipient _id and <_id>-sync, decrypted with the "
                  "attachment key; which one the app showed depends on a setting and is not "
                  "established here. On pixel7a_a14 Blocked and Hidden held 'No' on all 15 rows, "
                  "and Username, Note and Sync Avatar had no value on any row. Reference: "
                  "Signal-Android, RecipientTable.kt, "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/database/RecipientTable.kt#L5158-L5164. "
                  "Reference: Signal-Android, 'AvatarHelper.java', "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/profiles/AvatarHelper.java"),
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',
                  '*/org.thoughtcrime.securesms/app_avatars/*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "4 rows",
            "pixel7a_a14": "Signal 7.11.4 | 15 rows",
            "russell_pixel6a_a13": "6 rows",
            "sharon_a14": "25 rows",
        },
    },
    "get_signalGroups": {
        "name": "Signal - Groups",
        "description": ("Parses Signal groups and their membership, including group title, member "
                        "names and the time the group row was created on this device "
                        "(groups.timestamp, which GroupTable.kt create() sets from the device's "
                        "clock at L722 of commit ad141bb6af88ef67aea05d3d0e55cf9760fe56eb)."),
        "author": "Alexis Brignoni, @kalink0",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Requires the SQLCipher key from extra/Secrets/secrets.json. Avatar is the group "
                  "picture from app_avatars, matched by the group's recipient _id and decrypted "
                  "with the attachment key. No group was present on the public test image, so the "
                  "avatar column is unverified there. Reference: Signal-Android, "
                  "'AvatarHelper.java', "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/profiles/AvatarHelper.java"),
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',
                  '*/org.thoughtcrime.securesms/app_avatars/*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Signal 7.11.4 | 0 rows",
            "russell_pixel6a_a13": "0 rows",
            "sharon_a14": "1 row",
        },
    },
    "get_signalAttachments": {
        "name": "Signal - Attachments",
        "description": ("Parses metadata for attachments referenced by Signal messages, and lists "
                        "app_parts files no attachment record names."),
        "author": "Alexis Brignoni, @kalink0",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Attachment files are decrypted with the modernKey from secrets.json and each "
                  "attachment's data_random; the format is detected from the content. Rows come "
                  "from the attachment table, or the part table on older releases, joined to their "
                  "message. A file in app_parts that no record names is listed with Database "
                  "Record 'No'; it cannot be decrypted because its random is kept only in the "
                  "record. app_parts files of a data directory whose database was not read are not "
                  "listed. File Modified is the time the extraction recorded for the file. On "
                  "pixel7a_a14 Detected Content Type held 'image/jpeg', Transfer State '0', Voice "
                  "Note and Video GIF 'No' and Database Record 'Yes' on all 9 rows, and Thumbnail "
                  "and Caption had no value on any row. Reference: Signal-Android, "
                  "'MessageTypes.java', "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/database/MessageTypes.java"),
        "paths": ('*/org.thoughtcrime.securesms/databases/signal.db*',
                  '*/org.thoughtcrime.securesms/app_parts/*',),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "hc_pixel8pro_a16": "7 rows",
            "pixel7a_a14": "Signal 7.11.4 | 9 rows",
            "russell_pixel6a_a13": "8 rows",
            "sharon_a14": "10 rows",
        },
    },
    "get_signalAccount": {
        "name": "Signal - Account",
        "description": ("Account values and selected settings from Signal's key-value store "
                        "(signal-key-value.db)."),
        "author": "@kalink0",
        "creation_date": "2026-11-15",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Requires the SQLCipher key from extra/Secrets/secrets.json. One row per listed "
                  "key the store holds; an absent key is not listed and Signal uses its default. "
                  "Encryption keys stored there are not reported. PIN is the PIN as stored by "
                  "Signal. PIN Last Successful Entry is also written when Signal resets its PIN "
                  "reminders, so it does not on its own prove a PIN entry. Last Foreground Time is "
                  "set each time the app comes to the foreground. Server Time Offset (ms) is "
                  "device clock minus server time, measured at Server Time Offset Updated; "
                  "positive means the device clock was ahead. Linked Devices Present is reported "
                  "as stored; the key is not defined in the source cited, so its meaning is taken "
                  "from its name. Times are UTC; a stored 0 or -1 is shown with '(not set)'. "
                  "Reference: Signal-Android, keyvalue package, "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/keyvalue/AccountValues.kt"),
        "paths": ('*/org.thoughtcrime.securesms/databases/signal-key-value.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Signal 7.11.4 | 18 rows",
        },
    },
    "get_signalImageCache": {
        "name": "Signal - Image Cache",
        "description": ("Decrypts the images in Signal's Glide disk cache "
                        "(cache/image_manager_disk_cache)."),
        "author": "@kalink0",
        "creation_date": "2026-11-15",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Signal",
        "notes": ("Signal encrypts its Glide image cache with the attachment modernKey from "
                  "secrets.json. A file counts as Decrypted only when Signal's encrypted check "
                  "value matches; otherwise Status says why and the file is still listed. Without "
                  "the key nothing is listed. Cached images are not linked to a message or "
                  "contact: the file name is only the cache key and the journal is not read. File "
                  "Modified is the time the extraction recorded for the file. On pixel7a_a14 "
                  "Status held 'Decrypted' on all 85 rows. Reference: Signal-Android, "
                  "'EncryptedCoder.java', "
                  "https://github.com/signalapp/Signal-Android/blob/ad141bb6af88ef67aea05d3d0e55cf9760fe56eb/app/src/main/java/org/thoughtcrime/securesms/glide/cache/EncryptedCoder.java"),
        "paths": ('*/org.thoughtcrime.securesms/cache/image_manager_disk_cache/*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "pixel7a_a14": "Signal 7.11.4 | 85 rows",
        },
    },
}

import base64
import datetime
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
from scripts.artifacts.storagePathViews import canonical_path, unique_files
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
# Outgoing is every member of OUTGOING_MESSAGE_TYPES (MessageTypes.java L65-70 at
# ad141bb6), which includes the outgoing audio (2) and video (11) call types.
MESSAGE_DIRECTIONS = {
    2: 'Outgoing',
    11: 'Outgoing',
    20: 'Incoming',
    21: 'Outgoing',
    22: 'Outgoing',
    23: 'Outgoing',
    24: 'Outgoing',
    25: 'Outgoing',
    26: 'Outgoing',
    27: 'Draft',
    28: 'Outgoing',
}
MESSAGE_STATUS = {21: 'Outbox', 22: 'Sending', 23: 'Sent', 24: 'Failed', 27: 'Draft'}
# Call rows, from isCallLog (MessageTypes.java L293-301 at ad141bb6), which
# compares the whole type
CALL_MESSAGE_TYPES = {1, 2, 3, 8, 10, 11, 12}
# Incoming call rows, from isIncomingAudioCall and isIncomingVideoCall
# (MessageTypes.java L307-313 at ad141bb6), which compare the whole type.
INCOMING_CALL_TYPES = {1: 'Incoming', 10: 'Incoming'}

# Event rows, named after the MessageTypes.java constants at ad141bb6.
# Base types 1-18 (L36-53), compared on the base type.
MESSAGE_EVENT_BASE_TYPES = {
    1: 'Incoming audio call', 2: 'Outgoing audio call', 3: 'Missed audio call',
    4: 'Joined', 5: 'Unsupported message', 6: 'Invalid message', 7: 'Profile change',
    8: 'Missed video call', 9: 'GV1 migration', 10: 'Incoming video call',
    11: 'Outgoing video call', 12: 'Group call', 13: 'Bad decrypt', 14: 'Change number',
    15: 'Release channel donation request', 16: 'Thread merge', 17: 'SMS export',
    18: 'Session switchover',
}
# Flag bits (L80-111), each tested with (type & bit) != 0 as Signal does.
MESSAGE_EVENT_BITS = (
    (0x10000, 'Group update'),               # GROUP_UPDATE_BIT
    (0x40000, 'Expiration timer update'),    # EXPIRATION_TIMER_UPDATE_BIT
    (0x400000, 'End session'),               # END_SESSION_BIT
    (0x200, 'Identity update'),              # KEY_EXCHANGE_IDENTITY_UPDATE_BIT
    (0x4000, 'Identity verified'),           # KEY_EXCHANGE_IDENTITY_VERIFIED_BIT
    (0x2000, 'Identity default'),            # KEY_EXCHANGE_IDENTITY_DEFAULT_BIT
)
GROUP_LEAVE_BIT = 0x20000
GROUP_V2_BIT = 0x80000
# isChatSessionRefresh (L347-354) bundles these encryption error bits
CHAT_SESSION_REFRESH_BITS = 0x10000000 | 0x08000000 | 0x04000000 | 0x02000000
# Special types (L114-126), compared on (type & SPECIAL_TYPES_MASK)
SPECIAL_TYPES_MASK = 0xF00000000
MESSAGE_SPECIAL_TYPES = {
    0x100000000: 'Story reaction', 0x200000000: 'Gift badge',
    0x300000000: 'Payments notification', 0x400000000: 'Payments activate request',
    0x500000000: 'Reported spam', 0x600000000: 'Message request accepted',
    0x800000000: 'Payments activated', 0x900000000: 'Payments tombstone',
    0xA00000000: 'Blocked', 0xB00000000: 'Unblocked', 0xC00000000: 'Poll terminate',
    0xD00000000: 'Pinned message',
}
# StoryType.kt at ad141bb6 (L10-30)
STORY_TYPES = {1: 'Story with replies', 2: 'Story without replies',
               3: 'Text story with replies', 4: 'Text story without replies'}

# RecipientTable.kt RecipientType at ad141bb6 (L5158-5164)
RECIPIENT_TYPES = {0: 'Individual', 1: 'MMS', 2: 'Group V1', 3: 'Group V2',
                   4: 'Distribution list', 5: 'Call link'}
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
    """Find and cache Signal's keys from the extraction's secrets.json.

    The cache is keyed on the secrets files found, so a second case processed
    in the same process (the GUI) never reuses the first case's keys.
    """
    seeker = context.get_seeker()
    secrets_files = tuple(sorted(str(path) for path in seeker.search(SECRETS_GLOB)
                                 if os.path.basename(str(path)) == 'secrets.json'))
    if secrets_files in _secrets_cache:
        return _secrets_cache[secrets_files]

    _secrets_cache[secrets_files] = (None, None)
    if not secrets_files:
        logfunc('Signal: no Secrets/secrets.json found, the data stays encrypted')
        return _secrets_cache[secrets_files]

    for secrets_path in secrets_files:
        database_key, attachment_key = _read_signal_keys(secrets_path)
        if database_key or attachment_key:
            _secrets_cache[secrets_files] = (database_key, attachment_key)
            break
    return _secrets_cache[secrets_files]


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


def _open_signal_database(context, database_name='signal.db'):
    """Yield (connection, source_path) for each decryptable Signal database.

    The storage views of one database (/data/data, /data/user/0, /data_mirror)
    are read once; a second Android user's database is read on its own. Signal
    keys all of its databases with the same SQLCipher key.
    """
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.basename(file_found) != database_name:
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


def _container(context, path):
    """Key for the Signal data directory a file belongs to, or ''.

    Built from the storage-view independent form of the path, so /data/data,
    /data/user/0 and /data_mirror spellings of one directory share a key and a
    second Android user's directory does not. Matched on a whole path segment,
    so a decoy package whose name merely contains Signal's never counts.
    """
    key, _ = canonical_path(context.get_relative_path(path))
    parts = str(key).replace('\\', '/').split('/')
    if SIGNAL_PACKAGE not in parts:
        return ''
    return '/'.join(parts[:len(parts) - parts[::-1].index(SIGNAL_PACKAGE)])


def _attachment_files(context):
    """Map (container, app_parts file name) to the extracted path.

    Keyed on the container as well as the name, so the app_parts of a second
    user or profile are never joined to another container's database.
    """
    found = {}
    for path in context.get_seeker().search(f'*/{SIGNAL_PACKAGE}/app_parts/*'):
        path = str(path)
        if os.path.isfile(path):
            found[(_container(context, path), os.path.basename(path))] = path
    return found


def _avatar_files(context):
    """Map (container, app_avatars file name) to the extracted path.

    AvatarHelper names each file after the recipient's _id, with '-sync' appended
    for the copy taken from the system contacts.
    """
    found = {}
    for path in context.get_seeker().search(f'*/{SIGNAL_PACKAGE}/app_avatars/*'):
        path = str(path)
        if os.path.isfile(path):
            found[(_container(context, path), os.path.basename(path))] = path
    return found


def _avatar_references(modern_key, avatar_files, container):
    """Decrypt this container's avatars; map file name to a media reference.

    ModernEncryptingPartOutputStream.createFor with inline set writes its 32 byte
    random at the start of the file, then the AES-CTR ciphertext, keyed as an
    attachment is but with the random taken from the file instead of the database.
    """
    references = {}
    if not modern_key:
        return references
    for (avatar_container, name), path in avatar_files.items():
        if avatar_container != container or name.endswith('.tmp'):
            continue
        try:
            with open(path, 'rb') as avatar_file:
                stored = avatar_file.read()
            if len(stored) <= 32:
                continue
            plaintext = _decrypt_attachment(modern_key, stored[:32], stored[32:])
            extension, mime = _detect_format(plaintext)
            if mime is None:
                logfunc(f'Signal: avatar {name} did not decrypt to a known image format')
                continue
            references[name] = check_in_embedded_media(
                path, plaintext, name=f'signal_avatar_{name}.{extension}',
                force_type=mime, force_extension=extension)
        except (OSError, ValueError, TypeError) as error:
            logfunc(f'Signal: could not decrypt avatar {name}: {error}')
    return references


def _file_modified(context, path):
    """The modification time the extraction recorded for a file, as UTC, or ''."""
    info = context.get_seeker().file_infos.get(path)
    if not info or not info.modification_date:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(info.modification_date), datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


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


def _checked_in_attachments(connection, modern_key, stored_files, container):
    """Decrypt every attachment and group the media references by message.

    check_in_embedded_media keys media on a hash of the content, so decrypting
    the same attachment for both the message and the attachment artifact
    registers it once and returns the same reference.

    Returns (references_by_message_id, detected_type_by_attachment_id,
    thumbnail_reference_by_attachment_id, reference_by_attachment_id).
    """
    references = {}
    own_references = {}
    detected_types = {}
    thumbnails = {}
    if not modern_key:
        return references, detected_types, thumbnails, own_references

    attachment_table, attachment_columns = _attachment_table(connection)
    if not attachment_table or not all(
            _attachment_name(attachment_columns, name) for name in ('data_file', 'data_random')):
        return references, detected_types, thumbnails, own_references

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
            path = stored_files.get((container, os.path.basename(blob_name)))
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
                if reference:
                    own_references[attachment_id] = reference
                if reference and message_id is not None:
                    references.setdefault(message_id, []).append(reference)
    return references, detected_types, thumbnails, own_references


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


def _recipient_names(connection, recipient_columns):
    """Map recipient _id to its display name: profile, contact, number, username."""
    names = {}
    if not recipient_columns:
        return names
    for row in connection.execute(f'''
        SELECT recipient._id,
               {_recipient_column(recipient_columns, 'recipient', 'profile_joined_name')},
               {_recipient_column(recipient_columns, 'recipient', 'system_joined_name')},
               {_recipient_column(recipient_columns, 'recipient', 'e164')},
               {_recipient_column(recipient_columns, 'recipient', 'username')}
        FROM recipient'''):
        names[row[0]] = _display_name(row[1], row[2], row[3], row[4])
    return names


def _conversation_labels(connection, recipient_names):
    """Map thread _id to the name of the thread's recipient.

    A thread belongs to one recipient (thread.recipient_id): a person, a group or
    a story distribution list. A group is named by groups.title and a list by
    distribution_list.name, both as stored, and a person by their display name.
    """
    titles = {}
    for table, column in (('groups', 'title'), ('distribution_list', 'name')):
        columns = _table_columns(connection, table)
        if 'recipient_id' in columns and column in columns:
            for recipient_id, title in connection.execute(
                    f'SELECT recipient_id, {column} FROM {table}'):
                if title:
                    titles[recipient_id] = title

    labels = {}
    if 'recipient_id' not in _table_columns(connection, 'thread'):
        return labels
    for thread_id, recipient_id in connection.execute('SELECT _id, recipient_id FROM thread'):
        labels[thread_id] = titles.get(recipient_id) or recipient_names.get(recipient_id, '')
    return labels


def _reactions_by_message(connection, recipient_names):
    """Each message's reactions as 'emoji reactor (time)', in the order sent."""
    reactions = {}
    columns = _table_columns(connection, 'reaction')
    if not {'message_id', 'author_id', 'emoji'} <= columns:
        return reactions
    sent = 'date_sent' if 'date_sent' in columns else 'NULL'
    for message_id, author_id, emoji, date_sent in connection.execute(
            f'SELECT message_id, author_id, emoji, {sent} FROM reaction '
            f'ORDER BY message_id, {sent}'):
        entry = f'{emoji} {recipient_names.get(author_id, "") or author_id}'
        if date_sent:
            entry += f' ({convert_unix_ts_to_utc(date_sent):%Y-%m-%d %H:%M:%S} UTC)'
        reactions.setdefault(message_id, []).append(entry)
    return reactions


def _message_text(body, message_type):
    """The body as stored, or for a call row without one its name in square brackets.

    The name is written by this parser, never by Signal, and is taken from the
    row's own message type, so a call shows in the conversation instead of an
    empty message.
    """
    if body:
        return body
    if message_type not in CALL_MESSAGE_TYPES:
        return ''
    return f'[{MESSAGE_EVENT_BASE_TYPES[message_type]}]'


def _message_event(message_type):
    """Name the event a non-message row records, or '' for an ordinary message.

    Every name that applies is listed, comma separated, because the base type,
    the flag bits and the special type are independent parts of one value.
    """
    if message_type is None:
        return ''
    events = []
    base_type = message_type & MESSAGE_BASE_TYPE_MASK
    if base_type in MESSAGE_EVENT_BASE_TYPES:
        events.append(MESSAGE_EVENT_BASE_TYPES[base_type])
    for bit, name in MESSAGE_EVENT_BITS:
        if message_type & bit:
            events.append(name)
    if message_type & GROUP_LEAVE_BIT and not message_type & GROUP_V2_BIT:
        events.append('Group quit')
    if message_type & CHAT_SESSION_REFRESH_BITS:
        events.append('Chat session refresh')
    special = message_type & SPECIAL_TYPES_MASK
    if special:
        events.append(MESSAGE_SPECIAL_TYPES.get(special, f'Special type {special:#x}'))
    return ', '.join(events)


def _quoted_ids(message_ids):
    """One ID as stored, several as a comma separated list, none as empty."""
    if not message_ids:
        return ''
    if len(message_ids) == 1:
        return message_ids[0]
    return ', '.join(str(message_id) for message_id in message_ids)


@artifact_processor
def get_signalMessages(context):
    data_list = []
    source_path = ''
    modern_key = _modern_key(context)
    stored_files = _attachment_files(context) if modern_key else {}

    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        message_columns = _table_columns(connection, 'message')
        attachments_by_message, _, _, _ = _checked_in_attachments(
            connection, modern_key, stored_files, _container(context, source_path))
        recipient_names = _recipient_names(connection, recipient_columns)
        conversations = _conversation_labels(connection, recipient_names)
        reactions = _reactions_by_message(connection, recipient_names)

        # Signal stores the quoted message's send time in quote_id and its author
        # in quote_author, and finds the original by both (MessageTable.kt L5139
        # at ad141bb6). More than one message can still match, so every match is
        # kept.
        original_by_quote = {}
        for sent, author, message_id in connection.execute(
                'SELECT date_sent, from_recipient_id, _id FROM message '
                'WHERE date_sent IS NOT NULL ORDER BY _id'):
            original_by_quote.setdefault((sent, author), []).append(message_id)

        cursor = connection.cursor()
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
                     NULLIF({_recipient_column(recipient_columns, 'quoted', 'e164')}, ''), NULLIF({_recipient_column(recipient_columns, 'quoted', 'username')}, ''), ''),
            {_select_list(message_columns, 'message',
                          ['quote_author', 'date_server', 'story_type', 'parent_story_id',
                           'revision_number', 'latest_revision_id', 'original_message_id'])}
        FROM message
        LEFT JOIN recipient AS sender ON message.from_recipient_id = sender._id
        LEFT JOIN recipient AS receiver ON message.to_recipient_id = receiver._id
        LEFT JOIN recipient AS quoted ON message.quote_author = quoted._id
        ORDER BY message.date_sent
        ''')
        for row in cursor:
            message_type = row[3]
            base_type = message_type & MESSAGE_BASE_TYPE_MASK if message_type is not None else None
            direction = MESSAGE_DIRECTIONS.get(base_type) \
                or INCOMING_CALL_TYPES.get(message_type, 'Unknown')
            # A message can carry several attachments, so the media cell takes a list
            attachments = attachments_by_message.get(row[5], [])
            quote_id, quote_author = row[19], row[22]
            date_server = row[23]
            story_type, parent_story_id = row[24], row[25]
            revision_number, latest_revision_id, original_message_id = row[26], row[27], row[28]
            in_revision_chain = latest_revision_id is not None or original_message_id is not None
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                convert_unix_ts_to_utc(quote_id) if quote_id else '',
                convert_unix_ts_to_utc(date_server) if date_server and date_server > 0 else '',
                direction,
                _display_name(row[7], row[8], row[6], row[9]),
                conversations.get(row[2], ''),
                _message_text(row[4], message_type),
                attachments,
                row[2],
                MESSAGE_STATUS.get(base_type, ''),
                row[6] or '',
                _display_name(row[11], row[12], row[10], row[13]),
                row[10] or '',
                len(attachments),
                'Yes' if row[14] else 'No',
                'Yes' if row[15] else 'No',
                'Yes' if row[16] else 'No',
                row[17] or '',
                row[21] or '',
                _quoted_ids(original_by_quote.get((quote_id, quote_author))) if quote_id else '',
                'Yes' if row[20] else 'No',
                _expires_in_seconds(row[18]),
                row[5],
                _message_event(message_type),
                STORY_TYPES.get(story_type, f'Unknown ({story_type})') if story_type else '',
                parent_story_id if parent_story_id and parent_story_id > 0 else '',
                '\n'.join(reactions.get(row[5], [])),
                revision_number if in_revision_chain else '',
                latest_revision_id if latest_revision_id is not None else '',
                original_message_id if original_message_id is not None else '',
            ))
        connection.close()

    data_headers = (
        ('Date Sent', 'datetime'),
        ('Date Received', 'datetime'),
        ('Quoted Message Sent', 'datetime'),
        ('Date Server', 'datetime'),
        'Direction',
        'Sender',
        'Conversation',
        'Message',
        ('Attachments', 'media'),
        'Thread ID',
        'Status',
        'Sender Phone Number',
        'Recipient',
        'Recipient Phone Number',
        'Attachment Count',
        'Read',
        'Remote Deleted',
        'View Once',
        'Quoted Message',
        'Quoted Author',
        'Quoted Message ID',
        'Quoted Original Missing',
        'Disappearing Timer (Seconds)',
        'Message ID',
        'Event Type',
        'Story Type',
        'Parent Story ID',
        'Reactions',
        'Revision Number',
        'Latest Revision ID',
        'Original Message ID',
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
    modern_key = _modern_key(context)
    avatar_files = _avatar_files(context) if modern_key else {}
    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        group_columns = _table_columns(connection, 'groups')
        if not group_columns:
            connection.close()
            continue
        avatars = _avatar_references(
            modern_key, avatar_files, _container(context, source_path))

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
                              'revision', 'last_force_update_timestamp', 'recipient_id'])},
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
                row[2] or row[9] or '',
                len(members),
                ', '.join(members),
                'Yes' if row[4] else 'No',
                'Yes' if row[5] else 'No',
                row[6],
                convert_unix_ts_to_utc(row[7]) if row[7] else '',
                row[1] or '',
                avatars.get(str(row[8]), '') if row[8] is not None else '',
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
        ('Avatar', 'media'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalContacts(context):
    data_list = []
    source_path = ''
    modern_key = _modern_key(context)
    avatar_files = _avatar_files(context) if modern_key else {}
    for connection, source_path in _open_signal_database(context):
        avatars = _avatar_references(
            modern_key, avatar_files, _container(context, source_path))
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
                avatars.get(str(row[0]), ''),
                avatars.get(f'{row[0]}-sync', ''),
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
        ('Avatar', 'media'),
        ('Sync Avatar', 'media'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalAttachments(context):
    data_list = []
    source_path = ''
    modern_key = _modern_key(context)
    if not modern_key:
        logfunc('Signal: no attachment modernKey available, reporting metadata only')
    # Indexed whether or not the key is known, so files no record points at are
    # still listed
    stored_files = _attachment_files(context)
    decrypted_count = 0
    referenced = set()
    read_containers = set()

    for connection, source_path in _open_signal_database(context):
        recipient_columns = _table_columns(connection, 'recipient')
        container = _container(context, source_path)
        read_containers.add(container)
        _, detected_types, thumbnails, own_references = _checked_in_attachments(
            connection, modern_key, stored_files, container)
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
        for name in ('data_file', 'thumbnail_file'):
            column = _attachment_name(attachment_columns, name)
            if column:
                referenced.update(
                    (container, os.path.basename(stored)) for (stored,) in connection.execute(
                        f'SELECT {column} FROM {attachment_table} WHERE {column} IS NOT NULL'))
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
            # The row's own file. It is the same media reference the message row uses,
            # so both views point at one copy.
            own_media = own_references.get(attachment_id, '')
            stored_path = stored_files.get((container, os.path.basename(row[5]))) if row[5] else None

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
                'Yes',
                _file_modified(context, stored_path) if stored_path else '',
            ))
        connection.close()

    # Files in app_parts that no attachment record names. Their per-file random
    # is kept in the record, so without one they cannot be decrypted.
    unread = 0
    for (container, name), path in sorted(stored_files.items()):
        if (container, name) in referenced:
            continue
        if container not in read_containers:
            unread += 1
            continue
        if not source_path:
            source_path = path
        data_list.append((
            '', '', '', '', '', '', os.path.getsize(path),
            context.get_relative_path(path), '', '', '', '', '', '', '', '', '', '',
            'No', _file_modified(context, path),
        ))
    if unread:
        logfunc(f'Signal: {unread} app_parts file(s) belong to a data directory whose database '
                'was not read; they stay encrypted and are not listed')

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
        'Database Record',
        ('File Modified', 'datetime'),
    )
    return data_headers, data_list, source_path


# EncryptedCoder.java at ad141bb6 (L30-33): the magic Signal writes in clear
# before the random, and again as the first encrypted bytes
GLIDE_CACHE_MAGIC = bytes.fromhex('915e6db409a668bee5b11bd729e504cc')


def _decrypt_cache_file(modern_key, stored):
    """Return (plaintext, status) for one of Signal's encrypted Glide cache files.

    The file is magic, a 32 byte random, then AES-CTR over the magic and the
    data, keyed with HMAC-SHA256(modernKey, random). The encrypted magic is what
    Signal itself checks to tell the key is right.
    """
    if stored[:16] != GLIDE_CACHE_MAGIC or len(stored) < 64:
        return None, 'Not an encrypted cache file'
    if not modern_key:
        return None, 'Not decrypted, no key'
    plaintext = _decrypt_attachment(modern_key, stored[16:48], stored[48:])
    if plaintext[:16] != GLIDE_CACHE_MAGIC:
        return None, 'Not decrypted, key did not match'
    return plaintext[16:], 'Decrypted'


@artifact_processor
def get_signalImageCache(context):
    data_list = []
    source_path = ''
    modern_key = _modern_key(context)
    if not modern_key:
        logfunc('Signal: no attachment modernKey available, so the image cache stays encrypted '
                'and is not listed')
        return (('File Modified', 'datetime'), ('Image', 'media'), 'Detected Content Type',
                'Status', 'Size (Bytes)', 'Cache File', 'Source File'), [], ''
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not os.path.isfile(file_found) or os.path.basename(file_found) == 'journal':
            continue
        source_path = os.path.dirname(file_found)
        media, detected = '', ''
        try:
            with open(file_found, 'rb') as cache_file:
                stored = cache_file.read()
            plaintext, status = _decrypt_cache_file(modern_key, stored)
            if plaintext is not None:
                extension, mime = _detect_format(plaintext)
                detected = mime or 'unknown'
                media = check_in_embedded_media(
                    file_found, plaintext, name=f'signal_cache_{os.path.basename(file_found)}.{extension}',
                    force_type=mime, force_extension=extension)
        except (OSError, ValueError, TypeError) as error:
            status = f'Not decrypted: {error}'
        data_list.append((
            _file_modified(context, file_found),
            media,
            detected,
            status,
            os.path.getsize(file_found),
            os.path.basename(file_found),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('File Modified', 'datetime'),
        ('Image', 'media'),
        'Detected Content Type',
        'Status',
        'Size (Bytes)',
        'Cache File',
        'Source File',
    )
    return data_headers, data_list, context.get_relative_path(source_path) if source_path else ''


# SignalStore keys reported by Signal - Account, in report order: key, setting
# name, decoder. Names follow the constants in the keyvalue package at ad141bb6.
KEY_VALUE_TYPES = {0: 'blob', 1: 'boolean', 2: 'float', 3: 'integer', 4: 'long', 5: 'string'}
PHONE_NUMBER_SHARING = {0: 'Default', 1: 'Everybody', 2: 'Nobody'}
PHONE_NUMBER_DISCOVERABILITY = {0: 'Discoverable', 1: 'Not discoverable', 2: 'Undecided'}
ACCOUNT_KEYS = (
    ('account.e164', 'Phone Number', 'text'),
    ('account.username', 'Username', 'text'),
    ('account.aci', 'ACI', 'text'),
    ('account.pni', 'PNI', 'text'),
    ('account.is_registered', 'Registered', 'bool'),
    ('account.registered_at', 'Registered At', 'time'),
    ('registration.complete', 'Registration Complete', 'bool'),
    ('account.device_id', 'Device ID', 'text'),
    ('account.device_name', 'Device Name', 'text'),
    ('account.has_linked_devices', 'Has Linked Devices', 'bool'),
    ('misc.linked_devices_present', 'Linked Devices Present', 'bool'),
    ('account.fcm_enabled', 'FCM Enabled', 'bool'),
    ('kbs.pin', 'PIN', 'text'),
    ('kbs.opted_out', 'PIN Opted Out', 'bool'),
    ('kbs.v2_lock_enabled', 'Registration Lock Enabled', 'bool'),
    ('pin.last_successful_entry', 'PIN Last Successful Entry', 'time'),
    ('misc.last_foreground_time', 'Last Foreground Time', 'time'),
    ('misc.last_profile_refresh_time', 'Last Profile Refresh Time', 'time'),
    ('storage.last_sync_time', 'Storage Service Last Sync Time', 'time'),
    ('misc.server_time_offset', 'Server Time Offset (ms)', 'text'),
    ('misc.last_server_time_offset_update', 'Server Time Offset Updated', 'time'),
    ('phoneNumberPrivacy.sharingMode', 'Phone Number Sharing', PHONE_NUMBER_SHARING),
    ('phoneNumberPrivacy.listingMode', 'Phone Number Discoverability', PHONE_NUMBER_DISCOVERABILITY),
    ('settings.link_previews', 'Link Previews', 'bool'),
    ('stories.disable', 'Stories Disabled', 'bool'),
    ('stories.viewed.receipts', 'Story View Receipts', 'bool'),
)


def _account_value(value, decoder):
    """Render one stored key-value entry for the report."""
    if value is None:
        return ''
    if decoder == 'bool':
        return {1: 'Yes', 0: 'No', '1': 'Yes', '0': 'No'}.get(value, f'Unknown ({value})')
    if decoder == 'time':
        try:
            milliseconds = int(value)
        except (TypeError, ValueError):
            return str(value)
        if milliseconds <= 0:
            return f'{milliseconds} (not set)'
        return f'{convert_unix_ts_to_utc(milliseconds):%Y-%m-%d %H:%M:%S} UTC'
    if isinstance(decoder, dict):
        try:
            return decoder.get(int(value), f'Unknown ({value})')
        except (TypeError, ValueError):
            return f'Unknown ({value})'
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


@artifact_processor
def get_signalAccount(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context, 'signal-key-value.db'):
        if not {'key', 'value'} <= _table_columns(connection, 'key_value'):
            logfunc(f'Signal: {source_path} has no key_value table')
            connection.close()
            continue
        stored = {key: value for key, value in connection.execute('SELECT key, value FROM key_value')}
        connection.close()
        for key, setting, decoder in ACCOUNT_KEYS:
            if key in stored:
                data_list.append((setting, _account_value(stored[key], decoder), key,
                                  context.get_relative_path(source_path)))

    data_headers = ('Setting', 'Value', 'Key', 'Source File')
    return data_headers, data_list, source_path
