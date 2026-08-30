__artifacts_v2__ = {
    "elementx_log_identifiers": {
        "name": "Element X - Identifiers in Logs",
        "description": "Parses the Matrix identifiers recorded in the Element X Android app's own log files.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Element X",
        "notes": "One row per distinct identifier found in the app's own log files under cache/logs. "
                 "Element X is a Matrix client whose stored data is encrypted (see the Sessions and "
                 "Stores artifact), but the log files it writes are plain text and they carry Matrix "
                 "identifiers. Three kinds are reported, each recognised by the form Matrix defines for "
                 "it: a User ID begins with @, a Room ID begins with !, and both are followed by the "
                 "homeserver name, which is why the homeserver is broken out into its own column. A "
                 "Device ID is read from the device_id=\"...\" field the Rust SDK logs beside a user. "
                 "Rows are aggregated, so each identifier appears once with First Seen, Last Seen and "
                 "the number of lines it appeared on, rather than one row per log line; the log is "
                 "mostly HTTP client debug output and enumerating it would bury these. Timestamps are "
                 "the ISO 8601 values at the start of each log line, which carry a Z suffix and are "
                 "reported as UTC. A Room ID here is the server-side identifier for a room this client "
                 "was working with, not the room's name, which is not in the log; the room's name, "
                 "members and messages are in the encrypted stores. The log file name carries the date "
                 "and hour it covers and these files sit in the cache directory, so the window they "
                 "cover depends on what the device retained and is not a complete account history. On "
                 "the tested device the log held the signed-in user, that account's device, and two "
                 "room identifiers, and the room count agreed with the room_info table of the encrypted "
                 "state store.",
        "paths": ('*/io.element.android.x/cache/logs/*.log',),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "elementx_sessions": {
        "name": "Element X - Sessions and Stores",
        "description": "Reports the Element X Android app's session stores and their encryption state.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Element X",
        "notes": "One row per Matrix SDK store found for a session. Element X keeps one directory per "
                 "signed-in session under files/sessions, named with a session identifier, and a "
                 "matching cache directory; Session ID is that directory name. Store is the database "
                 "file, and Rows is the number of rows in the named Table. These stores are ordinary "
                 "SQLite files, so the tables and row counts are readable, but the values are not: on "
                 "the tested device every identifier column held a 32 byte keyed hash rather than a "
                 "readable id, and every data column held a MessagePack map with version and ciphertext "
                 "members. The counts are therefore reported as a measure of how much the client held, "
                 "which bounds the scale of activity, and not as content. The content cannot be "
                 "recovered from a logical extraction: the app generates its database secret with "
                 "SecureRandom and writes it to an AndroidX EncryptedFile "
                 "(RandomDatabaseSecretProvider.kt), and that file's Tink keyset is encrypted with a "
                 "master key held in the Android Keystore (EncryptedFile.kt, both at "
                 "element-hq/element-x-android c47446bfb974bb5abce9f2938fafd71a52a1a5b6); the observed "
                 "device matched this, holding an AesGcmHkdfStreamingKey keyset in shared_prefs and an "
                 "88 byte session_database.key beside an unreadable session_database.db. A Keystore key "
                 "is not exported by a logical extraction, so message text, room names and member lists "
                 "stay encrypted. This was confirmed on the tested device by writing a known message and "
                 "then searching the whole app directory for it, which returned nothing. Identifiers "
                 "that are readable come from the app's log files instead and are covered by the "
                 "Identifiers in Logs artifact. The state store holds room and member records, the "
                 "event cache holds timeline events, the crypto store holds device and room key "
                 "records, and the media store holds cached media; tables that were empty on the tested "
                 "device are still reported so an absence is visible.",
        "paths": (
            '*/io.element.android.x/files/sessions/*/matrix-sdk-*.sqlite3*',
            '*/io.element.android.x/cache/*/matrix-sdk-*.sqlite3*',
        ),
        "output_types": "standard",
        "artifact_icon": "database",
    }
}

import os
import re

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

# Matrix identifier grammar: a user id starts with @ and a room id with !, each
# followed by a localpart and ":<homeserver>".
USER_RE = re.compile(r'@[A-Za-z0-9._=/+-]+:[A-Za-z0-9.-]+')
ROOM_RE = re.compile(r'![A-Za-z0-9._=/+-]+:[A-Za-z0-9.-]+')
DEVICE_RE = re.compile(r'device_id="([A-Za-z0-9]+)"')
# Log lines begin with an ISO 8601 UTC timestamp carrying a Z suffix.
TS_RE = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)Z')

# The tables worth counting in each Matrix SDK store.
STORE_TABLES = {
    'matrix-sdk-state': ('room_info', 'member', 'profile', 'state_event',
                         'receipt', 'display_name', 'send_queue_events'),
    'matrix-sdk-event-cache': ('events', 'linked_chunks', 'event_chunks'),
    'matrix-sdk-crypto': ('device', 'identity', 'tracked_user',
                          'inbound_group_session', 'outbound_group_session', 'session'),
    'matrix-sdk-media': ('media',),
}


def _files(context, predicate):
    out = []
    for f in unique_files(context):
        p = str(f).replace('\\', '/')
        if predicate(p):
            out.append(p)
    return out


def _iso(value):
    if not value:
        return ''
    return value.replace('T', ' ') + '+00:00'


def _split_id(identifier):
    localpart, _, homeserver = identifier.partition(':')
    return localpart, homeserver


@artifact_processor
def elementx_log_identifiers(context):
    seen = {}
    sources = []
    for log_path in _files(context, lambda p: p.endswith('.log') and '/cache/logs/' in p):
        rel = context.get_relative_path(log_path)
        try:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as handle:
                lines = handle.readlines()
        except (OSError, ValueError):
            continue
        if log_path not in sources:
            sources.append(log_path)
        for line in lines:
            stamp_match = TS_RE.match(line)
            stamp = stamp_match.group(1) if stamp_match else ''
            found = [('User ID', m) for m in USER_RE.findall(line)]
            found += [('Room ID', m) for m in ROOM_RE.findall(line)]
            found += [('Device ID', m) for m in DEVICE_RE.findall(line)]
            for kind, value in found:
                key = (kind, value, rel)
                entry = seen.get(key)
                if entry is None:
                    seen[key] = [stamp, stamp, 1]
                else:
                    if stamp and (not entry[0] or stamp < entry[0]):
                        entry[0] = stamp
                    if stamp and stamp > entry[1]:
                        entry[1] = stamp
                    entry[2] += 1

    data_list = []
    for (kind, value, rel), (first, last, count) in seen.items():
        localpart, homeserver = _split_id(value) if kind != 'Device ID' else (value, '')
        data_list.append((_iso(first), _iso(last), kind, value, localpart,
                          homeserver, count, rel))
    data_list.sort(key=lambda row: (row[2], row[3]))

    data_headers = (
        ('First Seen', 'datetime'), ('Last Seen', 'datetime'), 'Identifier Type',
        'Identifier', 'Local Part', 'Homeserver', 'Log Lines', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def elementx_sessions(context):
    data_list = []
    sources = []
    for db_path in _files(context, lambda p: p.endswith('.sqlite3')
                          and '/matrix-sdk-' in p):
        store = os.path.basename(db_path).replace('.sqlite3', '')
        tables = STORE_TABLES.get(store)
        if not tables:
            continue
        session_id = os.path.basename(os.path.dirname(db_path))
        rel = context.get_relative_path(db_path)
        counted = False
        for table in tables:
            records = get_sqlite_db_records(db_path, f'SELECT count(*) FROM "{table}"')
            for record in records:
                counted = True
                data_list.append((session_id, store, table, record[0], rel))
        if counted and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Session ID', 'Store', 'Table', 'Rows', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
