__artifacts_v2__ = {
    "gettr_messages": {
        "name": "GETTR - Messages",
        "description": "Direct messages from the app's per-account chat database, with the "
                       "sender, the conversation, the message text and the stored attachment "
                       "descriptors",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "GETTR",
        "notes": "The chat database is app_flutter/db_u<user id>.sqlite, one per signed-in "
                 "account, and its schema is the Stream Chat Flutter client's, not GETTR's own. "
                 "Message Direction is derived by comparing each message's user id against the "
                 "account id the same database records in connection_events.own_user, so it "
                 "comes from a value the app stored rather than from the file name; it is left "
                 "blank when that row is absent. Sender is the username the users table carries "
                 "for that id, and falls back to the raw user id when the users row is missing. "
                 "created_at, updated_at and deleted_at are Unix seconds. A message deleted in "
                 "the app keeps its row with Message Type 'deleted' and its stored text replaced "
                 "by the app's own tombstone wording, so the row still shows when it was sent and "
                 "by whom but no longer holds what it said; 2 of 17 messages were in that state "
                 "on the corpus below. Attachments holds the descriptor JSON as stored, which "
                 "carries remote URLs rather than local files, and no attachment referenced a "
                 "file present in the extraction, so no media is checked in. Reaction Counts is "
                 "as stored; the one reaction present used a numeric type code that was not "
                 "resolved to an emoji. Message text can be empty on a row whose content is an "
                 "attachment, which is why Message is blank on 2 rows. Conversation holds the "
                 "channel identifier and carries one value on every row of the corpus below "
                 "because that extraction held a single conversation; it is kept because it is "
                 "what separates conversations on a device that has more than one. Reply Count "
                 "was 0 on every row there, meaning no message carried a threaded reply.",
        "paths": ('*/com.gettr.gettr/app_flutter/db_u*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sender",
                "sentMessageStaticLabel": "Local User",
            }
        },
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.gettr.gettr | 17 rows",
            "pixel3_a12": "Android 12 | com.gettr.gettr | 0 rows",
        },
    },
    "gettr_channel_members": {
        "name": "GETTR - Conversation Members",
        "description": "One row per account in each conversation the chat database holds, with "
                       "that account's role, ban state, last read position and unread count",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "GETTR",
        "notes": "Joins the members, users and reads tables of the per-account chat database on "
                 "the user id and the channel identifier. Last Read Timestamp and Unread "
                 "Messages come from the reads table and are blank when that table has no row "
                 "for the pair, which is not evidence the conversation was unread. Member Role "
                 "and Channel Role are the two separate role columns the schema carries and are "
                 "reported as stored. Invited, Banned and Shadow Banned are the schema's own "
                 "0 or 1 columns. The times are Unix seconds. On the corpus below both members "
                 "of the one conversation were present in the users table, so no row fell back "
                 "to a bare user id.",
        "paths": ('*/com.gettr.gettr/app_flutter/db_u*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.gettr.gettr | 2 rows",
            "pixel3_a12": "Android 12 | com.gettr.gettr | 0 rows",
        },
    },
    "gettr_notifications": {
        "name": "GETTR - Notifications",
        "description": "Rows from the notification table of the app's per-account database, "
                       "each carrying an action code, a related account and the notification "
                       "payload as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "GETTR",
        "notes": "The store is databases/private_<username>.db, one per signed-in account, and "
                 "the account name is taken from that file name. msg_date is Unix milliseconds "
                 "here, unlike the Unix seconds the chat database uses, so the two are converted "
                 "differently. msg_action holds a short code; the code seen on the corpus below "
                 "was 'f' on both rows and it is reported as stored rather than expanded, "
                 "because no source for the code list was located. The payload's ruid field "
                 "held the account's own name on both rows below, so it is not repeated as a "
                 "column. Other Account Identifiers and Other Account Display Names come from "
                 "the i and n fields of the payload's othr list; one of the two identifiers "
                 "seen also appears as a user in the chat database of the same extraction, "
                 "which is why i is read as an account identifier, and the list's remaining "
                 "field is an image path. Payload holds the whole msg_data JSON as stored, so "
                 "fields this artifact does not break out are still readable. Notification "
                 "User ID (as stored) is the msg_user_id column, which was null on both rows "
                 "below, so it is blank there.",
        "paths": ('*/com.gettr.gettr/databases/private_*.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.gettr.gettr | 2 rows",
            "pixel3_a12": "Android 12 | com.gettr.gettr | 0 rows",
        },
    },
    "gettr_app_state": {
        "name": "GETTR - App State",
        "description": "Key and value rows from the app's kv stores, which hold the signed-in "
                       "account record, the device identifier the app generated, and the app's "
                       "own settings",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "GETTR",
        "notes": "Every row of the kv table in databases/g.db and in each "
                 "databases/private_<username>.db is reported, so keys written by later versions "
                 "still appear and nothing is filtered on a guess at which keys matter. The "
                 "values are as stored. Some carry account identity and session material, "
                 "including a key holding the account record with a refresh token and a key "
                 "holding an app-generated device identifier. Others are timeline and feed "
                 "caches whose contents are posts the app fetched from the server, which record "
                 "that the app retrieved them and not that anyone read them; those values are "
                 "reported as stored and are not broken out into rows of their own for that "
                 "reason. Store names the file the row came from and Account is taken from the "
                 "private_<username>.db file name, and is blank for g.db, which is not per "
                 "account.",
        "paths": ('*/com.gettr.gettr/databases/g.db*',
                  '*/com.gettr.gettr/databases/private_*.db*'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.gettr.gettr | 47 rows",
            "pixel3_a12": "Android 12 | com.gettr.gettr | 5 rows",
        },
    },
    "gettr_cached_images": {
        "name": "GETTR - Cached Images",
        "description": "Rows from the cacheObject table, each pairing the remote URL the app "
                       "requested with the file it wrote for it, and the image itself where that "
                       "file is present",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "GETTR",
        "notes": "files/libCachedImageData.db records the URL, the stored file name and the "
                 "length for each image this cache holds, so the link between a cached file and "
                 "the address it came from is one the app recorded rather than one derived by "
                 "matching sizes or times. The file is looked up under the same package "
                 "container as the database and the image is checked in when it is present; "
                 "Media is blank when it is not. validTill and touched are Unix milliseconds. "
                 "This cache is not the app's only image store: the package also holds a Glide "
                 "cache under cache/image_manager_disk_cache, 43 files on one corpus below and "
                 "33 on the other, whose file names are hashes carrying no recorded URL, so "
                 "those files are not reported here and no attempt is made to attribute them.",
        "paths": ('*/com.gettr.gettr/files/libCachedImageData.db*',
                  '*/com.gettr.gettr/cache/libCachedImageData/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.gettr.gettr | 1 row",
            "pixel3_a12": "Android 12 | com.gettr.gettr | 0 rows",
        },
    },
}

import json
import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)

PACKAGE = 'com.gettr.gettr'

SIDECARS = ('-wal', '-shm', '-journal')


def _container(path):
    """The path up to and including the package directory, or '' if not under one.

    Matched on a whole path segment so a directory merely containing the package
    name cannot be mistaken for the container, and so two app data directories are
    never merged under one key.
    """
    parts = str(path).replace('\\', '/').split('/')
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == PACKAGE:
            return '/'.join(parts[:index + 1])
    return ''


def _stores(context, suffix_test):
    """Candidate store paths, storage views collapsed and sidecars dropped."""
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if suffix_test(os.path.basename(file_found)):
            found.append(file_found)
    return found


def _account_from_private(path):
    """The account name carried by a private_<username>.db file name."""
    name = os.path.basename(path)
    if name.startswith('private_') and name.endswith('.db'):
        return name[len('private_'):-len('.db')]
    return ''


def _own_user(db_path):
    """(account id, account name) the chat database records for the device account."""
    rows = get_sqlite_db_records(db_path, 'SELECT own_user FROM connection_events')
    for row in rows or []:
        if not row[0]:
            continue
        try:
            own = json.loads(row[0])
        except (TypeError, ValueError) as error:
            logfunc(f'GETTR: connection_events.own_user did not parse as JSON: {error}')
            continue
        return own.get('id', ''), (own.get('username') or own.get('name') or '')
    return '', ''


def _usernames(db_path):
    """Map of user id to the username the users table carries."""
    names = {}
    rows = get_sqlite_db_records(db_path, 'SELECT id, extra_data FROM users')
    for user_id, extra in rows or []:
        label = ''
        if extra:
            try:
                data = json.loads(extra)
                label = data.get('username') or data.get('name') or data.get('nickname') or ''
            except (TypeError, ValueError) as error:
                logfunc(f'GETTR: users.extra_data did not parse as JSON for {user_id}: {error}')
        names[user_id] = label
    return names


@artifact_processor
def gettr_messages(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context, lambda n: n.startswith('db_u') and n.endswith('.sqlite')):
        own_id, _ = _own_user(db_path)
        names = _usernames(db_path)
        rows = get_sqlite_db_records(db_path, '''
            SELECT created_at, updated_at, deleted_at, user_id, channel_cid, message_text,
                   type, attachments, quoted_message_id, reply_count, reaction_counts, id
            FROM messages ORDER BY created_at
        ''')
        rows = list(rows)
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (created, updated, deleted, user_id, channel, text,
             kind, attachments, quoted, replies, reactions, message_id) = row
            if not own_id:
                direction = ''
            elif user_id == own_id:
                direction = 'Outgoing'
            else:
                direction = 'Incoming'
            data_list.append((
                convert_unix_ts_to_utc(created),
                convert_unix_ts_to_utc(updated),
                convert_unix_ts_to_utc(deleted),
                direction,
                names.get(user_id) or user_id or '',
                text or '',
                channel or '',
                kind or '',
                attachments if attachments not in ('[]', None) else '',
                quoted or '',
                replies if replies is not None else '',
                reactions or '',
                message_id or '',
                user_id or '',
            ))

    data_headers = (
        ('Message Timestamp', 'datetime'),
        ('Updated Timestamp', 'datetime'),
        ('Deleted Timestamp', 'datetime'),
        'Message Direction',
        'Sender',
        'Message',
        'Conversation',
        'Message Type',
        'Attachments',
        'Quoted Message ID',
        'Reply Count',
        'Reaction Counts',
        'Message ID',
        'Sender User ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_channel_members(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context, lambda n: n.startswith('db_u') and n.endswith('.sqlite')):
        names = _usernames(db_path)
        rows = get_sqlite_db_records(db_path, '''
            SELECT r.last_read, u.created_at, u.last_active, m.user_id, m.channel_cid,
                   m.channel_role, m.role, m.invited, m.banned, m.shadow_banned,
                   r.unread_messages, u.online, u.banned
            FROM members m
            LEFT JOIN users u ON u.id = m.user_id
            LEFT JOIN reads r ON r.user_id = m.user_id AND r.channel_cid = m.channel_cid
        ''')
        rows = list(rows)
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (last_read, created, last_active, user_id, channel, channel_role, member_role,
             invited, banned, shadow_banned, unread, online, user_banned) = row
            data_list.append((
                convert_unix_ts_to_utc(last_read) if last_read else '',
                convert_unix_ts_to_utc(created) if created else '',
                convert_unix_ts_to_utc(last_active) if last_active else '',
                names.get(user_id) or user_id or '',
                channel or '',
                channel_role or '',
                member_role or '',
                invited if invited is not None else '',
                banned if banned is not None else '',
                shadow_banned if shadow_banned is not None else '',
                unread if unread is not None else '',
                online if online is not None else '',
                user_banned if user_banned is not None else '',
                user_id or '',
            ))

    data_headers = (
        ('Last Read Timestamp', 'datetime'),
        ('Account Created', 'datetime'),
        ('Last Active', 'datetime'),
        'Username',
        'Conversation',
        'Channel Role',
        'Member Role',
        'Invited',
        'Banned In Conversation',
        'Shadow Banned',
        'Unread Messages',
        'Online',
        'Account Banned',
        'User ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_notifications(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context, lambda n: n.startswith('private_') and n.endswith('.db')):
        rows = get_sqlite_db_records(db_path, '''
            SELECT msg_date, msg_action, msg_user_id, msg_tag, msg_is_read, msg_data, msg_id
            FROM notification ORDER BY msg_date
        ''')
        rows = list(rows)
        source_paths.append(context.get_relative_path(db_path))
        account = _account_from_private(db_path)
        for msg_date, action, user_id, tag, is_read, payload, msg_id in rows:
            others, other_names = [], []
            if payload:
                try:
                    for entry in json.loads(payload).get('othr') or []:
                        if entry.get('i'):
                            others.append(entry['i'])
                        if entry.get('n'):
                            other_names.append(entry['n'])
                except (TypeError, ValueError, AttributeError) as error:
                    logfunc(f'GETTR: notification msg_data did not parse as JSON: {error}')
            data_list.append((
                convert_unix_ts_to_utc(msg_date / 1000) if msg_date else '',
                account,
                action or '',
                ', '.join(others),
                ', '.join(other_names),
                is_read if is_read is not None else '',
                tag if tag is not None else '',
                user_id or '',
                msg_id or '',
                payload or '',
            ))

    data_headers = (
        ('Notification Timestamp', 'datetime'),
        'Account',
        'Action (as stored)',
        'Other Account Identifiers',
        'Other Account Display Names',
        'Read',
        'Tag',
        'Notification User ID (as stored)',
        'Notification ID',
        'Payload (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_app_state(context):
    data_list = []
    source_paths = []

    def wanted(name):
        return name == 'g.db' or (name.startswith('private_') and name.endswith('.db'))

    for db_path in _stores(context, wanted):
        rows = list(get_sqlite_db_records(db_path, 'SELECT key, value FROM kv ORDER BY key'))
        source_paths.append(context.get_relative_path(db_path))
        name = os.path.basename(db_path)
        account = _account_from_private(db_path)
        for key, value in rows:
            data_list.append((key or '', value or '', name, account))

    data_headers = ('Key', 'Value (as stored)', 'Store', 'Account')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_cached_images(context):
    data_list = []
    source_paths = []

    # Files the seeker returned, indexed by (container, base name), so a cached file
    # is only ever paired with the database from its own app data directory.
    files_by_key = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        files_by_key.setdefault((_container(file_found), os.path.basename(file_found)),
                                file_found)

    for db_path in _stores(context, lambda n: n == 'libCachedImageData.db'):
        rows = get_sqlite_db_records(db_path, '''
            SELECT touched, validTill, url, relativePath, length, eTag, key
            FROM cacheObject ORDER BY touched
        ''')
        rows = list(rows)
        source_paths.append(context.get_relative_path(db_path))
        container = _container(db_path)
        for touched, valid_till, url, relative, length, etag, key in rows:
            media = ''
            cached = files_by_key.get((container, relative)) if relative else None
            if cached:
                media = check_in_media(cached, relative)
            data_list.append((
                convert_unix_ts_to_utc(touched / 1000) if touched else '',
                convert_unix_ts_to_utc(valid_till / 1000) if valid_till else '',
                media,
                url or '',
                relative or '',
                length if length is not None else '',
                etag or '',
                key or '',
            ))

    data_headers = (
        ('Touched Timestamp', 'datetime'),
        ('Valid Until', 'datetime'),
        ('Media', 'media'),
        'URL',
        'Cached File',
        'Length',
        'ETag',
        'Cache Key',
    )
    return data_headers, data_list, '\n'.join(source_paths)
