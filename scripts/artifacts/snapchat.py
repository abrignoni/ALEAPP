# pylint: disable=W0718
__artifacts_v2__ = {
    "get_snapchat_feeds": {
        "name": "Snapchat - Feeds",
        "description": "Snapchat feed (last interaction per conversation)",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "rss",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 0 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_friends": {
        "name": "Snapchat - Friends",
        "description": "Snapchat friends / contacts",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 4 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 6 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 5 rows",
        },
    },
    "get_snapchat_messages": {
        "name": "Snapchat - Messages",
        "description": "Snapchat chat messages",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 0 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_arroyo_messages": {
        "name": "Snapchat - Messages (arroyo.db)",
        "description": "Chat message records from the conversation_message table in arroyo.db, "
                       "both the rows a normal read returns and rows that are present only before "
                       "the write-ahead log is applied, distinguished by the Record Origin column. "
                       "Sender and participant UUIDs are resolved against the Friend table in "
                       "main.db, and message text is decoded from the message_content protobuf on "
                       "rows where content_type is 1. WAL frames are not parsed, so absence of a "
                       "message here is not evidence it did not exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07", "last_update_date": "2026-08-07",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Newer Snapchat builds store conversations in arroyo.db. The Snapchat - Messages "
                 "artifact reads main.db and tcspahn.db and returns no rows against those builds.\n"
                 "READ THE RECORD ORIGIN COLUMN. This table holds two kinds of row. Record Origin "
                 "'Live' means the row is returned by a normal read of the database with its "
                 "write-ahead log applied. Record Origin 'Recovered' means the row is NOT returned "
                 "by that read: it is present in the database file as of its last checkpoint and "
                 "absent once the log is applied. Recovery Method names the technique and Recovery "
                 "Location says where in the evidence the row came from; both are empty on Live "
                 "rows. The two sets cannot overlap, because a row is only reported as Recovered "
                 "when its (client_conversation_id, client_message_id) primary key is absent from "
                 "the live read.\n"
                 "Why a Recovered row is not in the live read is NOT established by this artifact. "
                 "Removal by the application, a server re-sync rewriting those pages, and deletion "
                 "are all consistent with the same result. On the tested image most Recovered rows "
                 "carried Team Snapchat broadcast content, which is consistent with a re-sync, and "
                 "that is an observation about one image rather than a general property.\n"
                 "Method: arroyo.db is opened twice through SQLite, once with immutable=1, which "
                 "ignores the log and yields the file as of its last checkpoint, and once with "
                 "mode=ro, which applies it. Both sides are consistent SQLite reads of the same "
                 "bytes, so column names, type affinity and overflow pages are handled by SQLite "
                 "rather than by a hand-written page parser. The comparison is on primary key, not "
                 "row count: on the tested image counting flagged 2 of 30 tables in arroyo.db as "
                 "diverging while comparing keys flagged 6, because four tables held the same "
                 "number of rows under different keys.\n"
                 "This is NOT deleted-record carving. It does not read freelist pages, unallocated "
                 "space or freeblocks, and it does not parse WAL frames, so records that only ever "
                 "existed inside the log are not recovered. It also compares keys rather than full "
                 "row content, so a row whose key survives while its content changed is not "
                 "reported. It yields no Recovered rows when no -wal file accompanies the "
                 "database, verified by removing the sidecar and confirming both reads agreed at "
                 "11 rows.\n"
                 "The glob keeps the -wal and -shm sidecars, because the write-ahead log carries "
                 "much of the live state. On the tested image the database file read on its own "
                 "(immutable=1) yielded 11 conversation_message rows, while the same file read with "
                 "its WAL applied yielded 8.\n"
                 "Message text is taken from the message_content protobuf at nested field path "
                 "4 > 4 > 2 > 1. That path is derived from the structure observed in the tested "
                 "image, not from a published schema. The decode is cross-checked against the SQL "
                 "columns of the same row: protobuf 2 > 1 matches sender_id, 3 > 1 > 1 > 1 matches "
                 "client_conversation_id, 4 > 2 matches content_type, and 6 > 1 and 6 > 2 match "
                 "creation_timestamp and read_timestamp.\n"
                 "In the tested image 6 of the 16 rows with content_type 1 carried a UTF-8 string "
                 "at that path, 3 Live and 3 Recovered. Rows with content_type 0, 2 and 3 carried "
                 "media and sticker file names, CDN URLs, media dimensions and encryption key and "
                 "IV fields, but no plaintext body; this artifact does not decrypt media payloads. "
                 "Values of content_type other than 1 are reported as the stored integer with no "
                 "label, because no source documenting the enum has been verified.\n"
                 "Message Direction compares sender_id against the local account id, which is taken "
                 "from LAST_LOGGED_IN_USERNAME in identity_persistent_store.xml resolved through "
                 "Friend.userId in main.db, and failing that from the single distinct sender_id "
                 "among rows where created_on_device is set (the schema comments in arroyo.db "
                 "define that column as set when the message was created on this device). Both "
                 "paths agreed on the tested image. The column is left blank when neither resolves.\n"
                 "WHAT THIS DOES NOT RECOVER, measured rather than assumed. This artifact does not "
                 "parse WAL frames. On the tested image a one-off frame parser written during "
                 "development read a further 29 conversation_message rows that neither view "
                 "reports, across 10 conversations, 9 of which appear in neither view of the "
                 "conversation table; creation timestamps were readable for 21 of those 29 and "
                 "span 2025-11-18 to 2026-07-24. ABSENCE OF A MESSAGE FROM THIS ARTIFACT IS NOT "
                 "EVIDENCE THAT THE MESSAGE DID NOT EXIST. A shared SQLite recovery capability "
                 "covering WAL frames is being built separately. The run log records how many "
                 "frames the write-ahead log of the image being processed actually holds, which "
                 "is the per-device measure of what is left uncovered.\n"
                 "To re-derive a Recovered row without this tool, query the database with its log "
                 "ignored and confirm the same row is absent from a normal read, for example: "
                 "sqlite3 \"file:arroyo.db?immutable=1\" \"SELECT * FROM conversation_message "
                 "WHERE client_message_id = 962\"\n"
                 "Not covered: media files on disk are not linked to message rows, and reactions, "
                 "message_state history and Kraken epoch encrypted content are not parsed.",
        "paths": ('*/com.snapchat.android/databases/arroyo.db*',
                  '*/com.snapchat.android/databases/main.db*',
                  '*/com.snapchat.android/shared_prefs/identity_persistent_store.xml'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 16 rows "
                                "(8 Live, 8 Recovered)",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Creation Timestamp",
                "senderColumn": "Sender Username",
            }
        },
    },
    "get_snapchat_arroyo_conversations": {
        "name": "Snapchat - Conversations (arroyo.db)",
        "description": "Conversation records from the conversation and feed_entry tables in "
                       "arroyo.db, both the rows a normal read returns and rows that are present "
                       "only before the write-ahead log is applied, distinguished by the Record "
                       "Origin column. Participant UUIDs are decoded from the conversation_metadata "
                       "protobuf and resolved against the Friend table in main.db. WAL frames are "
                       "not parsed, so absence of a conversation here is not evidence it did not "
                       "exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07", "last_update_date": "2026-08-07",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "READ THE RECORD ORIGIN COLUMN. Record Origin 'Live' means the row is returned by "
                 "a normal read of the database with its write-ahead log applied. Record Origin "
                 "'Recovered' means the client_conversation_id is present in conversation or "
                 "feed_entry as of the last checkpoint and in neither table once the log is "
                 "applied. Recovery Method and Recovery Location are empty on Live rows. Method and "
                 "limits are the same as Snapchat - Messages (arroyo.db); see that artifact's "
                 "notes, including that why a Recovered row is absent is not established.\n"
                 "Comparing row counts alone would not find these: on the tested image "
                 "conversation, conversation_identifier and feed_entry each held 4 rows in both "
                 "reads, and only comparing primary keys showed one identifier had been replaced "
                 "by a different one.\n"
                 "For Recovered rows the participants, message count and title are read from the "
                 "same pre-checkpoint view, so they describe the conversation as it stood at that "
                 "point. A participant absent from the Friend table in main.db is reported as a "
                 "bare UUID; that is an unresolved identifier, not a finding about the account.\n"
                 "Rows are the union of client_conversation_id in the conversation and feed_entry "
                 "tables, so a conversation present in only one of the two is still reported.\n"
                 "Participant IDs are read from the conversation_metadata protobuf, at repeated "
                 "field 3, sub-path 1 > 1, as 16 raw bytes formatted as a UUID. On the tested image "
                 "this agreed for each of the 4 conversations with the feed_entry.participants "
                 "column, which stores the same UUIDs as a plain concatenation of 16-byte values, "
                 "and each of the 4 distinct sender_id values in conversation_message appeared in "
                 "a resolved participant list.\n"
                 "Conversation Type is reported as the stored integer with no label, because no "
                 "source documenting the enum has been verified. Tombstoned At Timestamp is the "
                 "conversation.tombstoned_at_timestamp column, which the schema comments in "
                 "arroyo.db describe as when the conversation was locally left by the user.\n"
                 "Message Count is a count of conversation_message rows carrying that "
                 "client_conversation_id in the matching view, which is not necessarily the number "
                 "of messages exchanged in the conversation.\n"
                 "WHAT THIS DOES NOT RECOVER, measured rather than assumed. This artifact does not "
                 "parse WAL frames. On the tested image a one-off frame parser written during "
                 "development read conversation_message rows belonging to 9 conversations that "
                 "appear in neither view of the conversation table and are therefore absent from "
                 "this artifact entirely. ABSENCE OF A CONVERSATION HERE IS NOT EVIDENCE THAT IT "
                 "DID NOT EXIST. A shared SQLite recovery capability covering WAL frames is being "
                 "built separately.",
        "paths": ('*/com.snapchat.android/databases/arroyo.db*',
                  '*/com.snapchat.android/databases/main.db*'),
        "output_types": "standard", "artifact_icon": "messages",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 5 rows "
                                "(4 Live, 1 Recovered)",
        },
    },
    "get_snapchat_memories": {
        "name": "Snapchat - Memories",
        "description": "Snapchat memories entries",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "standard", "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_meo": {
        "name": "Snapchat - MEO My Eyes Only",
        "description": "Snapchat My Eyes Only confidential data; recovers the 4-digit passcode via bcrypt",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat",
        "notes": "Passcode recovery brute-forces the 4-digit MEO code (bcrypt); can be slow.",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "standard", "artifact_icon": "eye-off",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 1 row",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_snap_media": {
        "name": "Snapchat - Snap Media",
        "description": "Snapchat memories snap media (incl. geolocation)",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "all", "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 5 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_identity": {
        "name": "Snapchat - Identity Persistent Store",
        "description": "Snapchat identity_persistent_store.xml",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/shared_prefs/identity_persistent_store.xml',),
        "output_types": "standard", "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 12 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 10 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 12 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 13 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 12 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 12 rows",
        },
    },
    "get_snapchat_login_signup": {
        "name": "Snapchat - Login Signup Store",
        "description": "Snapchat LoginSignupStore.xml",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/shared_prefs/LoginSignupStore.xml',),
        "output_types": "standard", "artifact_icon": "login-2",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 2 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 3 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 2 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 3 rows",
        },
    }
}

import datetime
import os
import sqlite3
import struct
import xml.etree.ElementTree as ET

import bcrypt

from scripts.ilapfuncs import artifact_processor, decode_protobuf, get_sqlite_db_path, \
    logfunc, open_sqlite_db_readonly

_MEO_CODES = {}
_XML_UNIX_KEYS = {'INSTALL_ON_DEVICE_TIMESTAMP', 'LONG_CLIENT_ID_DEVICE_TIMESTAMP',
                  'FIRST_LOGGED_IN_ON_DEVICE_TIMESTAMP'}
# blackboxprotobuf raises these when a blob does not decode as protobuf.
_PB_ERRORS = (ValueError, TypeError, IndexError, KeyError, AttributeError)


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(files_found, *suffixes):
    for f in files_found:
        f = str(f)
        if f.endswith(suffixes):
            return f
    return ''


def _rows(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _text_from_blob(blob, start_byte, len_byte, type_=None):
    if type_ is not None and type_ != 'text':
        return ''
    try:
        length = blob[len_byte]
        return blob[start_byte:start_byte + length].decode('utf-8', 'replace')
    except (TypeError, IndexError, AttributeError):
        return ''


def _decrypt_meo_code(hashed):
    if hashed in _MEO_CODES:
        return _MEO_CODES[hashed]
    try:
        hash_bytes = hashed.encode()
    except (AttributeError, UnicodeEncodeError):
        return ''
    for code in range(10000):  # 4-digit numeric passcode, O(10^4)
        psw = f'{code:04d}'
        try:
            if bcrypt.checkpw(psw.encode(), hash_bytes):
                _MEO_CODES[hashed] = psw
                return psw
        except (ValueError, TypeError):
            return ''
    return 'Could not find any passcode'


@artifact_processor
def get_snapchat_feeds(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT lastInteractionTimestamp, key, displayInteractionType, lastReadTimestamp, lastReader,
               lastWriteTimestamp, lastWriter, lastWriteType FROM Feed
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], _ms_to_utc(r[3]), r[4], _ms_to_utc(r[5]), r[6], r[7])
                 for r in rows]
    data_headers = (('Last Interaction Timestamp', 'datetime'), 'Key', 'Display Interaction Type',
                    ('Last Read Timestamp', 'datetime'), 'Last Reader',
                    ('Last Write Timestamp', 'datetime'), 'Last Writer', 'Last Write Type')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_friends(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT addedTimestamp, username, userId, displayName, phone, birthday
        FROM Friend WHERE addedTimestamp IS NOT NULL
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Added Timestamp', 'datetime'), 'Username', 'User ID', 'Display Name',
                    'Phone Nr', 'Birthday')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_messages(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT timestamp, seenTimestamp, senderId, username, displayName, type, content
        FROM Message JOIN Friend on senderId = Friend._id
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5],
                  _text_from_blob(r[6], 0x2c, 0x28, r[5])) for r in rows]
    data_headers = (('Creation Timestamp', 'datetime'), ('Seen Timestamp', 'datetime'), 'Sender ID',
                    'Sender Username', 'Sender Display Name', 'Message Type', 'Text')
    return data_headers, data_list, source_path


def _pb_get(node, key):
    '''Read one field out of a blackboxprotobuf dict.

    blackboxprotobuf splits a field whose repeats decode to different typedefs into
    'N-1', 'N-2' keys, so fall back to the first such variant when the plain key is absent.
    '''
    if not isinstance(node, dict):
        return None
    if key in node:
        return node[key]
    for name in sorted(node):
        if name.startswith(f'{key}-'):
            return node[name]
    return None


def _pb_walk(node, *path):
    '''Walk a blackboxprotobuf dict, taking the first element of any repeated field.'''
    current = node
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        current = _pb_get(current, key)
    if isinstance(current, list):
        current = current[0] if current else None
    return current


def _pb_text(node, *path):
    value = _pb_walk(node, *path)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    return ''


def _uuid_from_bytes(value):
    '''Format a 16-byte protobuf value as a canonical UUID string.'''
    if not isinstance(value, (bytes, bytearray)) or len(value) != 16:
        return ''
    digits = bytes(value).hex()
    return (f'{digits[0:8]}-{digits[8:12]}-{digits[12:16]}-'
            f'{digits[16:20]}-{digits[20:32]}')


def _decode(blob):
    if not blob:
        return None
    try:
        values, _typedef = decode_protobuf(bytes(blob))
    except _PB_ERRORS:
        return None
    return values if isinstance(values, dict) else None


def _friends(main_db_path):
    '''Map Friend.userId to (username, displayName) from main.db.'''
    friends = {}
    for user_id, username, display_name in _rows(
            main_db_path, 'SELECT userId, username, displayName FROM Friend'):
        if user_id:
            friends[user_id] = (username or '', display_name or '')
    return friends


def _friend_name(friends, user_id, index=0):
    return friends.get(user_id, ('', ''))[index]


def _rows_pre_wal(source_path, sql):
    '''Run sql against the database file as of its last checkpoint, ignoring the WAL.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered. Path handling goes through the same
    get_sqlite_db_path() that open_sqlite_db_readonly() uses, so Windows long paths and
    URI-special characters behave identically.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _superseded(source_path, sql, key_indexes):
    '''Rows present at the last checkpoint and absent once the write-ahead log is applied.

    Both sides are consistent SQLite views of the same file, one ignoring the WAL and one
    applying it, compared on the columns at key_indexes. Comparing row counts is not enough:
    on the tested image counting flagged 2 of 30 tables in arroyo.db while comparing primary
    keys flagged 6, because four tables held the same number of rows with different keys.

    Empty when the file has no WAL alongside it. Why a row did not survive into the
    committed state is not established here.
    '''
    def key(row):
        return tuple(row[index] for index in key_indexes)

    committed = {key(row) for row in _rows(source_path, sql)}
    return [row for row in _rows_pre_wal(source_path, sql) if key(row) not in committed]


def _participants(arroyo_path, friends, reader=_rows):
    '''Map client_conversation_id to (participant ids, participant usernames).'''
    participants = {}
    for conversation_id, blob in reader(
            arroyo_path, 'SELECT client_conversation_id, conversation_metadata FROM conversation'):
        entries = _pb_get(_decode(blob), '3')
        if isinstance(entries, dict):
            entries = [entries]
        ids = []
        for entry in entries if isinstance(entries, list) else []:
            user_id = _uuid_from_bytes(_pb_walk(entry, '1', '1'))
            if user_id and user_id not in ids:
                ids.append(user_id)
        names = [_friend_name(friends, user_id) or user_id for user_id in ids]
        participants[conversation_id] = (', '.join(ids), ', '.join(names))
    return participants


def _local_user_id(files_found, arroyo_path, friends):
    '''The signed-in account's user id, or '' when it cannot be established.

    Preferred source is LAST_LOGGED_IN_USERNAME in identity_persistent_store.xml resolved
    through Friend.userId. Failing that, the single distinct sender of the messages the
    arroyo.db schema comments describe as created on this device.
    '''
    username = ''
    for key, value in _parse_xml_rows(_find(files_found, 'identity_persistent_store.xml')):
        if key == 'LAST_LOGGED_IN_USERNAME' and value:
            username = value
    if username:
        for user_id, (friend_username, _display) in friends.items():
            if friend_username == username:
                return user_id
    senders = {row[0] for row in _rows(
        arroyo_path,
        'SELECT DISTINCT sender_id FROM conversation_message WHERE created_on_device = 1') if row[0]}
    return senders.pop() if len(senders) == 1 else ''


def _yes_no(value):
    return 'YES' if value else 'NO'


_MESSAGE_SQL = '''
    SELECT creation_timestamp, read_timestamp, sender_id, content_type, message_content,
           message_state_type, is_saved, is_viewed_by_user, created_on_device,
           remote_media_count, replies_count, quoted_server_message_id,
           client_conversation_id, client_message_id, server_message_id
    FROM conversation_message ORDER BY creation_timestamp
'''
# conversation_message primary key (client_conversation_id, client_message_id), as offsets
# into the columns selected above.
_MESSAGE_KEY = (12, 13)

_MESSAGE_HEADERS = (('Creation Timestamp', 'datetime'), ('Read Timestamp', 'datetime'),
                    'Record Origin',
                    'Sender Username', 'Sender Display Name', 'Sender ID', 'Message Direction',
                    'Conversation Participants', 'Message Text', 'Content Type (as stored)',
                    'Message State Type', 'Is Saved', 'Is Viewed By User', 'Created On Device',
                    'Remote Media Count', 'Replies Count', 'Quoted Server Message ID',
                    'Conversation ID', 'Client Message ID', 'Server Message ID',
                    'Recovery Method', 'Recovery Location')

_CONVERSATION_HEADERS = (('Creation Timestamp', 'datetime'), ('Last Updated Timestamp', 'datetime'),
                         ('Display Timestamp', 'datetime'), ('Tombstoned At Timestamp', 'datetime'),
                         ('Streak Expiration Timestamp', 'datetime'),
                         'Record Origin',
                         'Conversation Title',
                         'Participants', 'Participant IDs', 'Message Count', 'Streak Count',
                         'Conversation Type (as stored)', 'Send State Type', 'Feed Item Creator',
                         'Feed Item Creator ID', 'Last Chat Sender', 'Last Chat Sender ID',
                         'Tombstoned', 'Conversation ID',
                         'Recovery Method', 'Recovery Location')

# Provenance vocabulary. Record Origin is a closed two-value set so a viewer can branch on it;
# Recovery Method names the technique and is empty on live rows; Recovery Location says where in
# the evidence the row came from. Keep these strings stable, they are read by people and may be
# read by LAVA.
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_DIFF = 'WAL diff'


def _provenance(source_path, origin):
    '''The three provenance values for a row, as (origin, method, location).'''
    if origin == _ORIGIN_LIVE:
        return (_ORIGIN_LIVE, '', '')
    name = os.path.basename(source_path) if source_path else 'database'
    return (_ORIGIN_RECOVERED, _METHOD_WAL_DIFF, f'{name} (pre-checkpoint)')


def _log_wal_extent(files_found):
    '''Log how much write-ahead log this artifact leaves unparsed, per image.

    Reads the WAL header and the 24-byte frame headers only; no page images are loaded.
    A frame whose salt pair does not match the WAL header belongs to a previous log
    generation that the current one has cycled past, so it holds older content still on
    disk. Reporting both counts gives the examiner the size of what is not covered here.
    '''
    wal_path = _find(files_found, 'arroyo.db-wal')
    if not wal_path:
        return
    try:
        with open(wal_path, 'rb') as handle:
            header = handle.read(32)
            if len(header) < 32:
                return
            magic, page_size = struct.unpack('>I', header[:4])[0], struct.unpack('>I', header[8:12])[0]
            if magic not in (0x377F0682, 0x377F0683) or page_size < 512:
                return
            salts = struct.unpack('>2I', header[16:24])
            frame_size = 24 + page_size
            total = max(0, (os.path.getsize(wal_path) - 32) // frame_size)
            current = 0
            for index in range(total):
                handle.seek(32 + index * frame_size)
                frame_header = handle.read(24)
                if len(frame_header) < 24:
                    total = index
                    break
                if struct.unpack('>2I', frame_header[8:16]) == salts:
                    current += 1
    except (OSError, struct.error, ValueError):
        return
    logfunc(f'Snapchat arroyo.db-wal holds {total} frames of {page_size} bytes '
            f'({current} in the current log generation, {total - current} from previous '
            f'generations). This artifact does not parse WAL frames, so records held only in '
            f'them are not reported and absence of a message from the Snapchat arroyo.db '
            f'artifacts is not evidence that it did not exist.')


def _by_creation(row):
    '''Sort key on the first column, tolerating rows whose timestamp is blank.

    The blank flag comes first so a datetime is never compared against a string.
    '''
    return (row[0] == '', row[0])


def _message_rows(rows, friends, participants, local_user_id, provenance):
    origin, method, location = provenance
    data_list = []
    for row in rows:
        (created, read, sender_id, content_type, blob, state, saved, viewed, on_device,
         media_count, replies, quoted_id, conversation_id, client_message_id, server_message_id) = row
        text = _pb_text(_decode(blob), '4', '4', '2', '1') if content_type == 1 else ''
        if not local_user_id or not sender_id:
            direction = ''
        else:
            direction = 'Outgoing' if sender_id == local_user_id else 'Incoming'
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(read), origin,
            _friend_name(friends, sender_id), _friend_name(friends, sender_id, 1), sender_id,
            direction, participants.get(conversation_id, ('', ''))[1], text, content_type, state,
            _yes_no(saved), _yes_no(viewed), _yes_no(on_device), media_count, replies, quoted_id,
            conversation_id, client_message_id, server_message_id, method, location))
    return data_list


def _conversation_rows(source_path, friends, reader, provenance, only_ids=None):
    participants = _participants(source_path, friends, reader)
    conversations = {row[0]: row[1:] for row in reader(source_path, '''
        SELECT client_conversation_id, creation_timestamp, tombstoned_at_timestamp, send_state_type
        FROM conversation
    ''')}
    feeds = {row[0]: row[1:] for row in reader(source_path, '''
        SELECT client_conversation_id, last_updated_timestamp, display_timestamp,
               streak_expiration_timestamp_ms, conversation_title, conversation_type, streak_count,
               feedItemCreator, last_chat_sender, tombstoned
        FROM feed_entry
    ''')}
    counts = dict(reader(source_path, '''
        SELECT client_conversation_id, COUNT(*) FROM conversation_message
        GROUP BY client_conversation_id
    '''))

    origin, method, location = provenance
    wanted = set(conversations) | set(feeds)
    if only_ids is not None:
        wanted &= set(only_ids)

    data_list = []
    for conversation_id in sorted(wanted):
        created, tombstoned_at, send_state = conversations.get(conversation_id, (None, None, ''))
        (updated, displayed, streak_expiry, title, conversation_type, streak, creator,
         last_sender, tombstoned) = feeds.get(conversation_id, (None,) * 9)
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(updated), _ms_to_utc(displayed),
            _ms_to_utc(tombstoned_at), _ms_to_utc(streak_expiry), origin, title,
            participants.get(conversation_id, ('', ''))[1],
            participants.get(conversation_id, ('', ''))[0],
            counts.get(conversation_id, 0), streak, conversation_type, send_state,
            _friend_name(friends, creator), creator, _friend_name(friends, last_sender), last_sender,
            _yes_no(tombstoned), conversation_id, method, location))
    return data_list


def _superseded_conversation_ids(source_path):
    '''client_conversation_id values that the WAL removes from conversation or feed_entry.'''
    pre, committed = set(), set()
    for sql in ('SELECT client_conversation_id FROM conversation',
                'SELECT client_conversation_id FROM feed_entry'):
        pre |= {row[0] for row in _rows_pre_wal(source_path, sql)}
        committed |= {row[0] for row in _rows(source_path, sql)}
    return pre - committed


@artifact_processor
def get_snapchat_arroyo_messages(context):
    '''Live conversation_message rows, plus rows the write-ahead log removes.

    Both sets are in one table so the recovered rows sit in chronological context. They are
    disjoint by construction: _superseded only returns primary keys absent from the live read.
    '''
    files_found = context.get_files_found()
    source_path = _find(files_found, 'arroyo.db')
    friends = _friends(_find(files_found, 'main.db'))
    local_user_id = _local_user_id(files_found, source_path, friends)
    _log_wal_extent(files_found)

    data_list = _message_rows(
        _rows(source_path, _MESSAGE_SQL), friends, _participants(source_path, friends),
        local_user_id, _provenance(source_path, _ORIGIN_LIVE))
    data_list += _message_rows(
        _superseded(source_path, _MESSAGE_SQL, _MESSAGE_KEY), friends,
        _participants(source_path, friends, _rows_pre_wal), local_user_id,
        _provenance(source_path, _ORIGIN_RECOVERED))
    data_list.sort(key=_by_creation)
    return _MESSAGE_HEADERS, data_list, source_path


@artifact_processor
def get_snapchat_arroyo_conversations(context):
    '''Live conversation and feed_entry rows, plus rows the write-ahead log removes.'''
    files_found = context.get_files_found()
    source_path = _find(files_found, 'arroyo.db')
    friends = _friends(_find(files_found, 'main.db'))

    data_list = _conversation_rows(source_path, friends, _rows,
                                   _provenance(source_path, _ORIGIN_LIVE))
    data_list += _conversation_rows(source_path, friends, _rows_pre_wal,
                                    _provenance(source_path, _ORIGIN_RECOVERED),
                                    _superseded_conversation_ids(source_path))
    data_list.sort(key=_by_creation)
    return _CONVERSATION_HEADERS, data_list, source_path


@artifact_processor
def get_snapchat_memories(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path, '''
        SELECT create_time, _id, snap_ids, CASE is_private WHEN 1 THEN 'YES' ELSE 'NO' END,
               cached_servlet_media_formats FROM memories_entry
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], _text_from_blob(r[2], 0x20, 0x1c), r[3],
                  _text_from_blob(r[4], 0x20, 0x1c)) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Memory ID', 'Snap ID', 'Is Private', 'Media Format')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_meo(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path,
                 'SELECT user_id, hashed_passcode, master_key, master_key_iv FROM memories_meo_confidential')
    data_list = [(r[0], r[1], _decrypt_meo_code(r[1]), r[2], r[3]) for r in rows]
    data_headers = ('User ID', 'Hashed Passcode', 'Passcode', 'Master Key', 'Master Key IV')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_snap_media(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path, '''
        SELECT create_time, memories_snap._id, media_id, memories_entry_id, time_zone_id, format,
               width, height, duration,
               CASE has_overlay_image WHEN 1 THEN 'YES' ELSE 'NO' END,
               overlay_size, overlay_redirect_info,
               CASE front_facing WHEN 1 THEN 'YES' ELSE 'NO' END, size,
               CASE has_location WHEN 1 THEN 'YES' ELSE 'NO' END, latitude, longitude,
               snap_create_user_agent, thumbnail_size, thumbnail_redirect_info
        FROM memories_snap JOIN memories_media ON memories_media._id = media_id
    ''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Create Time', 'datetime'), 'ID', 'Media ID', 'Memories Entry ID', 'Time Zone ID',
                    'Format', 'Width', 'Height', 'Duration', 'Has Overlay', 'Overlay Size',
                    'Overlay Info', 'Front Facing', 'Size', 'Has Location Info', 'Latitude',
                    'Longitude', 'Snap User Agent', 'Thumbnail Size', 'Thumbnail Info')
    return data_headers, data_list, source_path


def _parse_xml_rows(xml_file):
    data_list = []
    if not xml_file:
        return data_list
    try:
        root = ET.parse(xml_file).getroot()
    except (ET.ParseError, OSError, ValueError):
        return data_list
    for node in root:
        name = node.attrib.get('name', '')
        value = node.attrib.get('value', node.text)
        if name in _XML_UNIX_KEYS and value:
            try:
                value = datetime.datetime.fromtimestamp(
                    int(value) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            except (ValueError, TypeError, OverflowError, OSError):
                pass
        data_list.append((name, value))
    return data_list


@artifact_processor
def get_snapchat_identity(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'identity_persistent_store.xml')
    return ('Key', 'Value'), _parse_xml_rows(source_path), source_path


@artifact_processor
def get_snapchat_login_signup(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'LoginSignupStore.xml')
    return ('Key', 'Value'), _parse_xml_rows(source_path), source_path
