__artifacts_v2__ = {
    "get_teleguard": {
        "name": "Teleguard - Messages",
        "description": "Teleguard messenger messages",
        "author": "@abrignoni",
        "creation_date": "2024-01-09",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Is Edited? held 0 on every message row of every tested extraction, so no message "
                 "in them had been edited. The column is reported so an edited message is visible "
                 "on an extraction that has one. Call events and membership events are rows of this "
                 "same table, of type CALL and SERVICE, and are also reported in full by "
                 "Teleguard - Calls and Teleguard - Chat Events.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',
                  '*/ch.swisscows.messenger.teleguardapp/cache/**'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 42 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 2 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Media"
            }
        },
    },
    "get_teleguard_posts": {
        "name": "Teleguard - Posts",
        "description": "Teleguard channel posts",
        "author": "@abrignoni",
        "creation_date": "2024-01-09",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_contacts": {
        "name": "Teleguard - Contacts",
        "description": "Teleguard contacts with avatars",
        "author": "@abrignoni",
        "creation_date": "2024-01-09",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Personal ID is an optional identifier separate from the Server ID the app issues. "
                 "The app's own binary labels it 'Personal TeleGuard ID', carries a 'Change personal "
                 "ID' action and a buyPersonalId endpoint, and adds the column to this table in a "
                 "migration, so a contact has one only where that feature was used. It was null on "
                 "every contact row of every tested extraction, meaning none of those contacts had "
                 "one recorded.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 5 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 2 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_channels": {
        "name": "Teleguard - Channels",
        "description": "Teleguard channels",
        "author": "@abrignoni",
        "creation_date": "2024-01-09",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "The channels table is read with 'SELECT *' and the first twelve columns are labelled "
                 "by position; the mapping was established against the app version this parser was "
                 "written for and may not hold on other versions. Any further columns are not reported.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "radio",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_calls": {
        "name": "Teleguard - Calls",
        "description": "Teleguard audio and video call events",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Call events are stored as rows of the messages table with type 'CALL', not in a "
                 "separate call log. Each row carries a JSON metadata object with the keys "
                 "isSuccessfull, subtext, membersText and callType; all call rows in the tested "
                 "extractions carried all four. Direction is derived by comparing the row's sender "
                 "with the local account's serverId from the service table, which agreed with the "
                 "app's own English event label on every call row in the tested extractions. "
                 "Duration and outcome are reported as stored: subtext is a localised display string "
                 "giving either a spelled out minutes and seconds count or a word for why the call "
                 "did not connect, not a numeric duration, and no numeric duration is "
                 "stored for these rows. The messages table's userTime column is not reported here "
                 "because it held exactly the same value as createDate on every call row of every "
                 "tested extraction, unlike the text rows of the same table where the two differ. "
                 "Connected and Chat ID each held one value across the tested Android extraction, "
                 "which reflects a device whose calls all connected and were all with one contact "
                 "rather than a column that cannot vary. The database also carries an empty sipcalls "
                 "table with number, name, duration, date and cost columns; it held no rows in any "
                 "tested extraction and is not reported.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_chat_events": {
        "name": "Teleguard - Chat Events",
        "description": "Teleguard invitation and group membership events",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Membership and invitation events are stored as rows of the messages table with "
                 "type 'SERVICE'. The event text is the app's own localised display string and is "
                 "reported as stored. These rows carry no sender in the tested extractions, so no "
                 "direction is derived for them. The messages table's userTime column is not "
                 "reported here because it was null on every service row of every tested extraction.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "users-plus",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_account": {
        "name": "Teleguard - Account",
        "description": "Teleguard local account identity",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "The local account is stored as the 'user' row of the service table, whose data "
                 "column is JSON. Server ID is the account identifier that appears in the sender, "
                 "receiver and chatId columns of the messages table. The same JSON carries an RSA "
                 "key pair in PEM form on some app versions. The key material itself is not written "
                 "to the report; the columns record whether each key was present and a SHA-256 "
                 "fingerprint of the DER body, which is enough to correlate the account across "
                 "extractions without copying a private key into report output. Fields absent from "
                 "an app version's JSON are left blank rather than reported as empty values. "
                 "Personal ID and Current Phone were empty on the tested extraction: TeleGuard "
                 "issues the Server ID itself and requires no telephone number, and a personal ID "
                 "is set by the account holder only if they choose one, so both columns being blank "
                 "is a result about the account rather than a column that is never populated. The "
                 "settings key holding the phone value was spelled '_currentPhone' on Android and "
                 "'currentPhone' on iOS in the tested extractions and both spellings are read.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "user-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 1 row; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_drafts": {
        "name": "Teleguard - Drafts",
        "description": "Teleguard unsent message drafts",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Drafts live in a second database, teleguard_temp.db, in the same directory as "
                 "teleguard_database.db. The draft table is keyed on the recipient's serverId, which "
                 "is resolved to a contact alias from the contacts table of the main database in the "
                 "same app data directory. The Draft Text column was an empty string, not null, on "
                 "every row of every tested extraction: the app keeps a draft row per conversation "
                 "and clears the text when the message is sent, so a row records that a draft existed "
                 "for that conversation and the tested devices held no recoverable draft text. The "
                 "same database carries a messages_buffer table, which held no rows in any tested "
                 "extraction and is not reported.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_temp.db*',
                  '*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*'),
        "output_types": "standard",
        "artifact_icon": "pencil",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_media_downloads": {
        "name": "Teleguard - Media Downloads",
        "description": "Teleguard media download tasks",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "The app fetches message media through the flutter_downloader plugin, which records "
                 "each attempt in databases/download_tasks.db. A row records that the app requested "
                 "one media object and what became of that request; the status and progress values "
                 "are the plugin's own and are reported as stored. The file name is the server file "
                 "identifier, which is the key used in a message's metadata files object, so rows are "
                 "joined back to the message that carried the media by that identifier. One media "
                 "object can own more than one row, because a retry is recorded as its own task. The "
                 "task's headers column holds a bearer token; the token is not written to the report "
                 "and only the account identifier from its subject claim is reported. MIME Type, "
                 "Saved Directory and Requesting Account each held one value across the tested "
                 "extraction, which reflects one account fetching every item into one cache "
                 "directory with the server declaring a generic type, not columns that cannot vary.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/databases/download_tasks.db*',
                  '*/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_saved_images": {
        "name": "Teleguard - Saved Images",
        "description": "Teleguard images written outside the message media cache",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Two locations, distinguished by the Location column. Files named avatar<epoch>.jpg "
                 "in the app's app_flutter directory carry a Unix millisecond epoch in the file name, "
                 "reported in the File Name Timestamp column; in the tested extraction that image was "
                 "not byte identical to any avatar blob stored in the contacts table, and what the "
                 "app writes it for is not established here. Files under the device's shared "
                 "Pictures/TeleGuard directory are images present in shared storage rather than in "
                 "the app's private data. Their names are RFC 4122 version 1 UUIDs, whose embedded "
                 "timestamp is reported in the UUID Timestamp column; that timestamp is a property of "
                 "the identifier, not a recorded file time. Message media held in the app's cache "
                 "directory is reported by Teleguard - Messages, not here.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/app_flutter/avatar*.jpg',
                  '*/data/media/*/Pictures/TeleGuard/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    },
    "get_teleguard_app_settings": {
        "name": "Teleguard - App Settings",
        "description": "Teleguard app configuration values",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "Last Cache Clearing is the flutter.lastCacheClearing value from the app's "
                 "FlutterSharedPreferences file, stored as a Unix millisecond epoch. Database Version "
                 "is the contents of the app_flutter/db.version file. The same preferences file also "
                 "holds a bundled emoji catalogue that accounts for most of its size and is not user "
                 "data; it is not reported.",
        "paths": ('*/ch.swisscows.messenger.teleguardapp/shared_prefs/FlutterSharedPreferences.xml',
                  '*/ch.swisscows.messenger.teleguardapp/app_flutter/db.version'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | ch.swisscows.messenger.teleguardapp vc 176 | 1 row; same install as hc_pixel8pro_a16, whose app files, code path and update time are identical, so this is the same TeleGuard dataset rather than a second one",
        },
    }
}

import base64
import datetime
import hashlib
import json
import os
import sqlite3
import uuid
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media, check_in_embedded_media
from scripts.artifacts.storagePathViews import unique_files

PACKAGE = 'ch.swisscows.messenger.teleguardapp'

# RFC 4122 version 1 timestamps count 100 ns intervals from the Gregorian reform.
_GREGORIAN_EPOCH = datetime.datetime(1582, 10, 15, tzinfo=datetime.timezone.utc)


def _container_root(path):
    """The app data directory a file sits in, or '' when it is not under one.

    Matched on a whole path segment equal to the package name so a directory merely
    containing the name never resolves, and so the two Android users of one package
    stay separate directories rather than collapsing onto each other.
    """
    parts = str(path).replace('\\', '/').split('/')
    for index, segment in enumerate(parts):
        if segment == PACKAGE:
            return '/'.join(parts[:index + 1])
    return ''


def _containers(context):
    """Files grouped by the app data directory they belong to.

    unique_files() first collapses the duplicate storage spellings of one file, and the
    grouping then keeps a second Android user's directory as its own container so its
    rows are reported rather than shadowed by user 0's.
    """
    grouped = {}
    for file_found in unique_files(context):
        root = _container_root(file_found)
        if root:
            grouped.setdefault(root, []).append(str(file_found))
    return grouped


def _pick(paths, filename):
    for path in paths:
        if os.path.basename(path) == filename:
            return path
    return ''


def _owner_id(db_path):
    """The local account's serverId, used to derive message and call direction."""
    for (data,) in _run(db_path, "SELECT data FROM service WHERE id = 'user'"):
        try:
            return (json.loads(data) or {}).get('serverId', '') or ''
        except (ValueError, TypeError):
            return ''
    return ''


def _uuid1_utc(value):
    """The timestamp embedded in an RFC 4122 version 1 UUID, or '' for anything else."""
    try:
        parsed = uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return ''
    if parsed.version != 1:
        return ''
    return _GREGORIAN_EPOCH + datetime.timedelta(microseconds=parsed.time // 10)


def _ms_to_utc(value):
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, TypeError, OSError, OverflowError):
        return ''


def _pem_fingerprint(pem):
    """SHA-256 of a PEM body's DER bytes, so a key can be correlated without copying it."""
    if not pem:
        return ''
    body = ''.join(line for line in str(pem).splitlines() if 'BEGIN' not in line and 'END' not in line)
    try:
        der = base64.b64decode(body, validate=False)
    except (ValueError, TypeError):
        return ''
    return hashlib.sha256(der).hexdigest() if der else ''


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _run(source_path, sql):
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


def _collect_messages(rows, files_found, owner_id, data_list):
    """Append one output row per message row, resolving media within this container."""
    for row in rows:
        media_refs = []
        if row[2] == 'MEDIA' and row[6]:
            try:
                files = json.loads(row[6]).get('files', {})
            except (ValueError, TypeError):
                files = {}
            for key in files:
                # The metadata key is a path fragment: TeleGuard stores each item
                # under cache/<key>/<file>, so match by substring. Require an actual
                # file so the cache/<key> directory itself is never matched -- a
                # directory makes check_in_media return None, and a None -> null in
                # the serialized media list makes the LAVA viewer show a broken-media
                # marker and crash on hover (the HTML report silently skips it).
                match = next((str(f) for f in files_found
                              if os.path.isfile(str(f)) and key in str(f)), None)
                if match:
                    ref = check_in_media(match, os.path.basename(match))
                    if ref:
                        media_refs.append(ref)
        if len(media_refs) == 1:
            media_cell = media_refs[0]
        elif media_refs:
            media_cell = media_refs
        else:
            media_cell = ''
        if owner_id and row[3]:
            direction = 'Outgoing' if row[3] == owner_id else 'Incoming'
        else:
            direction = ''
        data_list.append((
            _str_to_utc(row[0]),
            _str_to_utc(row[1]),
            direction,
            row[3],
            row[5],
            media_cell,
            row[2],
            row[4],
            row[6],
            row[7],
            row[8],
            row[9],
        ))


@artifact_processor
def get_teleguard(context):
    data_list = []
    sources = []
    for paths in _containers(context).values():
        source_path = _pick(paths, 'teleguard_database.db')
        if not source_path:
            continue
        rows = _run(source_path, '''
            SELECT datetime(createDate/1000,'unixepoch'), datetime(userTime/1000,'unixepoch'),
            type, sender, receiver, content, metadata, status, isEdited, chatId
            FROM messages
        ''')
        if not rows:
            continue
        sources.append(source_path)
        # local account id lives in the service table ('user' row) of the same db
        # and media is resolved from this container's files only, never across containers
        _collect_messages(rows, paths, _owner_id(source_path), data_list)

    data_headers = (
        ('Timestamp', 'datetime'),
        ('User Time', 'datetime'),
        'Direction',
        'Sender',
        'Content',
        ('Media', 'media'),
        'Type',
        'Receiver',
        'Metadata',
        'Status',
        'Is Edited?',
        'Chat ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_posts(context):
    data_list = []
    sources = []
    for paths in _containers(context).values():
        source_path = _pick(paths, 'teleguard_database.db')
        if not source_path:
            continue
        rows = _run(source_path, '''
            SELECT datetime(createDate/1000,'unixepoch'), channelId, header, content, type, localStatus,
            viewsCount, likesCount, dislikesCount, metadata, media
            FROM posts
        ''')
        if not rows:
            continue
        sources.append(source_path)
        data_list.extend((_str_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10])
                         for r in rows)
    data_headers = (('Timestamp', 'datetime'), 'Channel ID', 'Header', 'Content', 'Type', 'Local Status',
                    'Views Count', 'Likes Count', 'Dislikes Count', 'Metadata', 'Media')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_contacts(context):
    data_list = []
    sources = []
    for paths in _containers(context).values():
        source_path = _pick(paths, 'teleguard_database.db')
        if not source_path:
            continue
        rows = _run(source_path, '''
            SELECT datetime(lastActivityTime/1000,'unixepoch'), serverId, alias, type, color, avatar,
            options, info, datetime(lastVisitTime/1000,'unixepoch'), personalId
            FROM contacts
        ''')
        if not rows:
            continue
        sources.append(source_path)
        for r in rows:
            avatar = ''
            if r[5] is not None:
                avatar = check_in_embedded_media(source_path, r[5], f'{r[1]}_avatar.jpg',
                                                 force_type='image/jpeg', force_extension='jpg')
            data_list.append((_str_to_utc(r[0]), r[1], r[2], r[3], r[4], avatar, r[6], r[7],
                              _str_to_utc(r[8]), r[9]))

    data_headers = (('Last Activity Timestamp', 'datetime'), 'Server ID', 'Alias', 'Type', 'Color',
                    ('Avatar', 'media'), 'Options', 'Info', ('Last Visit Time', 'datetime'), 'Personal ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_channels(context):
    data_list = []
    sources = []
    for paths in _containers(context).values():
        source_path = _pick(paths, 'teleguard_database.db')
        if not source_path:
            continue
        rows = _run(source_path, 'SELECT * FROM channels')
        if not rows:
            continue
        sources.append(source_path)
        data_list.extend(tuple(r)[:12] for r in rows)
    data_headers = ('ID', 'Alias', 'Description', 'Category', 'Color', 'Avatar ID', 'Subscribers Count',
                    'Admin', 'Posts Count', 'Is Deleted', 'Language', 'Type')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_calls(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Call Type',
        'Connected',
        'Duration or Result (as stored)',
        'Members (as stored)',
        'Event Label (as stored)',
        'Sender',
        'Chat ID',
        'Message ID',
    )
    data_list = []
    sources = []
    for paths in _containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if not db_path:
            continue
        rows = _run(db_path, '''
            SELECT datetime(createDate/1000,'unixepoch'), sender, chatId, content, metadata, id
            FROM messages WHERE type = 'CALL'
        ''')
        if not rows:
            continue
        sources.append(db_path)
        owner_id = _owner_id(db_path)
        for row in rows:
            try:
                meta = json.loads(row[4]) or {}
            except (ValueError, TypeError):
                meta = {}
            if owner_id and row[1]:
                direction = 'Outgoing' if row[1] == owner_id else 'Incoming'
            else:
                direction = ''
            connected = meta.get('isSuccessfull')
            data_list.append((
                _str_to_utc(row[0]),
                direction,
                meta.get('callType', ''),
                '' if connected is None else ('Yes' if connected else 'No'),
                meta.get('subtext', ''),
                meta.get('membersText') or '',
                row[3],
                row[1],
                row[2],
                row[5],
            ))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_chat_events(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Event (as stored)',
        'Sender',
        'Chat ID',
        'Message ID',
    )
    data_list = []
    sources = []
    for paths in _containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if not db_path:
            continue
        rows = _run(db_path, '''
            SELECT datetime(createDate/1000,'unixepoch'), content, sender, chatId, id
            FROM messages WHERE type = 'SERVICE'
        ''')
        if not rows:
            continue
        sources.append(db_path)
        for row in rows:
            data_list.append((_str_to_utc(row[0]), row[1], row[2] or '', row[3], row[4]))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_account(context):
    data_headers = (
        'Server ID',
        'Alias',
        'User ID',
        'Personal ID',
        'Avatar Ref ID',
        'Current Phone',
        'Public Key Present',
        'Public Key SHA-256',
        'Private Key Present',
        'Private Key SHA-256',
    )
    data_list = []
    sources = []
    for paths in _containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if not db_path:
            continue
        user = {}
        for (data,) in _run(db_path, "SELECT data FROM service WHERE id = 'user'"):
            try:
                user = json.loads(data) or {}
            except (ValueError, TypeError):
                user = {}
        if not user:
            continue
        settings = {}
        for (data,) in _run(db_path, "SELECT data FROM service WHERE id = 'settings'"):
            try:
                settings = json.loads(data) or {}
            except (ValueError, TypeError):
                settings = {}
        # the key was spelled '_currentPhone' on Android and 'currentPhone' on iOS in the
        # tested extractions, so both spellings are resolved rather than one replaced
        phone = settings.get('currentPhone', settings.get('_currentPhone', ''))
        public_key = user.get('publicKey') or ''
        private_key = user.get('privateKey') or ''
        sources.append(db_path)
        data_list.append((
            user.get('serverId', '') or '',
            user.get('alias', '') or '',
            user.get('userId', '') or '',
            user.get('personalId', '') or '',
            user.get('avatarRefId', '') or '',
            phone or '',
            'Yes' if public_key else 'No',
            _pem_fingerprint(public_key),
            'Yes' if private_key else 'No',
            _pem_fingerprint(private_key),
        ))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_drafts(context):
    data_headers = (
        'Recipient Server ID',
        'Recipient Alias',
        'Draft Text',
    )
    data_list = []
    sources = []
    for paths in _containers(context).values():
        temp_path = _pick(paths, 'teleguard_temp.db')
        if not temp_path:
            continue
        rows = _run(temp_path, 'SELECT serverId, text FROM draft')
        if not rows:
            continue
        sources.append(temp_path)
        aliases = {}
        db_path = _pick(paths, 'teleguard_database.db')
        if db_path:
            for server_id, alias in _run(db_path, 'SELECT serverId, alias FROM contacts'):
                aliases[server_id] = alias
            if db_path not in sources:
                sources.append(db_path)
        for server_id, text in rows:
            data_list.append((server_id, aliases.get(server_id, ''), text or ''))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_media_downloads(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        ('Linked Message Timestamp', 'datetime'),
        'Status (as stored)',
        'Progress',
        'Server File ID',
        'File Name',
        'MIME Type (as stored)',
        'Saved Directory',
        'Requesting Account',
        'Linked Message ID',
        'Linked Chat ID',
        'URL',
    )
    data_list = []
    sources = []
    for paths in _containers(context).values():
        tasks_path = _pick(paths, 'download_tasks.db')
        if not tasks_path:
            continue
        rows = _run(tasks_path, '''
            SELECT time_created, status, progress, file_name, url, saved_dir, mime_type, headers
            FROM task
        ''')
        if not rows:
            continue
        sources.append(tasks_path)

        # a message's metadata files object is keyed on the server file id, which is the
        # stem of the task's file name, so the join is on a value both stores record
        by_file_id = {}
        db_path = _pick(paths, 'teleguard_database.db')
        if db_path:
            for message_id, chat_id, created, metadata in _run(db_path, '''
                    SELECT id, chatId, datetime(createDate/1000,'unixepoch'), metadata
                    FROM messages WHERE metadata IS NOT NULL AND metadata != '' '''):
                try:
                    files = (json.loads(metadata) or {}).get('files') or {}
                except (ValueError, TypeError):
                    files = {}
                for file_id in files:
                    by_file_id.setdefault(file_id, (message_id, chat_id, created))
            if db_path not in sources:
                sources.append(db_path)

        for created, status, progress, file_name, url, saved_dir, mime_type, headers in rows:
            file_id = os.path.splitext(file_name or '')[0]
            message_id, chat_id, message_time = by_file_id.get(file_id, ('', '', ''))
            data_list.append((
                _ms_to_utc(created),
                _str_to_utc(message_time),
                status,
                progress,
                file_id,
                file_name,
                mime_type,
                saved_dir,
                _account_from_bearer(headers),
                message_id,
                chat_id,
                url,
            ))
    return data_headers, data_list, '\n'.join(sources)


def _account_from_bearer(headers):
    """The account identifier from a task's bearer token, never the token itself."""
    try:
        token = (json.loads(headers) or {}).get('authorization') or ''
    except (ValueError, TypeError):
        return ''
    token = token.replace('Bearer', '', 1).strip()
    parts = token.split('.')
    if len(parts) != 3:
        return ''
    payload = parts[1]
    try:
        decoded = base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4))
        subject = (json.loads(decoded) or {}).get('sub') or ''
    except (ValueError, TypeError):
        return ''
    return str(subject).split(':', maxsplit=1)[0]


@artifact_processor
def get_teleguard_saved_images(context):
    data_headers = (
        ('File Name Timestamp', 'datetime'),
        ('UUID Timestamp', 'datetime'),
        'Location',
        'File Name',
        ('Image', 'media'),
        'Size (bytes)',
    )
    data_list = []
    sources = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        name = os.path.basename(file_found)
        stem = os.path.splitext(name)[0]
        if _container_root(file_found):
            location = 'App private storage'
            filename_time = _ms_to_utc(stem[len('avatar'):]) if stem.startswith('avatar') else ''
        else:
            location = 'Shared storage'
            filename_time = ''
        media_ref = check_in_media(file_found, name)
        sources.append(file_found)
        data_list.append((
            filename_time,
            _uuid1_utc(stem),
            location,
            name,
            media_ref or '',
            os.path.getsize(file_found),
        ))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_teleguard_app_settings(context):
    data_headers = (
        ('Last Cache Clearing', 'datetime'),
        'Database Version',
    )
    data_list = []
    sources = []
    for paths in _containers(context).values():
        prefs_path = _pick(paths, 'FlutterSharedPreferences.xml')
        version_path = _pick(paths, 'db.version')
        last_clearing = ''
        if prefs_path:
            try:
                for element in ET.parse(prefs_path).getroot():
                    if element.get('name') == 'flutter.lastCacheClearing':
                        value = element.get('value')
                        last_clearing = _ms_to_utc(value if value is not None else element.text)
            except (ET.ParseError, OSError):
                last_clearing = ''
            sources.append(prefs_path)
        db_version = ''
        if version_path:
            try:
                with open(version_path, 'r', encoding='utf-8', errors='replace') as handle:
                    db_version = handle.read().strip()
            except OSError:
                db_version = ''
            sources.append(version_path)
        if last_clearing or db_version:
            data_list.append((last_clearing, db_version))
    return data_headers, data_list, '\n'.join(sources)
