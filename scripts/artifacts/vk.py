__artifacts_v2__ = {
    "vk_messages": {
        "name": "VK - Messages",
        "description": "Messages of the VK app (com.vkontakte.android) from the messages table of its "
                       "vkim-<number>.sqlite database, with the conversation and sender names.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            (
            (
            "Class and line references are to the VK 8.183 APK (version code 54465) decompiled with jadx "
            "1.5.6, in com/vk/im/engine/internal/storage/delegates unless named in full; the obfuscated "
            "helper classes are in xsna. Reads the messages table of each databases/vkim-<number>.sqlite; "
            "Account Number is that number as it appears in the file name, and what it identifies was not "
            "traced. A write-ahead log beside a database is applied; a database with no log beside it is "
            "read alone. When one database is present under more than one storage path (data/data and "
            "data/user/0), a copy is also read when its database file, or the content of its -wal or "
            "-journal, matches no copy already read. Rows are compared on the columns read from their own "
            "table: a row equal in all of them is reported once, and a row that differs in any is "
            "reported once per version. Names, attachment types and message counts are looked up across "
            "the copies and are not versioned. A query that fails on a copy is logged and gives no rows "
            "from that copy; the other copies are still reported. Android User is read from the path, "
            "including a rollback snapshot under data/misc_ce/<n>/rollback; a path that names no user is "
            "shown as 0, which is an assumption. Timestamp is time, which the app reads into the message "
            "(messages/a.java:410), read here as Unix milliseconds, which the stored 13-digit values fit. "
            "Direction is Incoming when is_incoming is 1 and Outgoing when it is 0, the field the app "
            "reads into the message (messages/a.java:416); any other value is shown as stored. Message "
            "Type is type with the name the app's MsgDbType gives it (messages/MsgDbType.java, the value "
            "list; read at messages/a.java:205-207); a value it does not list is shown as stored. Message "
            "is body; when body is empty and the type is not FROM_USER, Message shows the type name in "
            "brackets, and no such row was in the test data. Sender ID and Sender Type are from_member_id "
            "and from_member_type, with the type named as the app's Peer.Type names it "
            "(com/vk/dto/common/Peer.java:80-109: 0 UNKNOWN, 1 USER, 2 EMAIL, 3 GROUP, 4 CHAT, 5 CONTACT, "
            "6 CHANNEL; read at messages/a.java:413-415). Sender is the first and last name of that id in "
            "the users table for a USER, and the title in the groups table for a GROUP. Dialog ID is "
            "dialog_id, and Dialog Kind is derived from it by the ranges of the app's classifier "
            "(Peer.java:261-281): above 2147483647 a user, above 2000000000 a chat, above 1900000000 a "
            "contact, above 0 a user, below -2147483648 a group, below -2000000000 an email, below 0 a "
            "group (its id negated), 0 unknown. Conversation is the chat title stored in dialogs, the "
            "user's name or the group's title, and blank when the id is in none of them or is a contact "
            "or email. Conversation Key joins the folders above the device storage (when the input holds "
            "more than one device), the Android User, the Account Number and the Dialog ID, which is what "
            "the conversation view groups by. Database names the database copy each row was read from, "
            "and it is left out when copies are compared. Attachments lists the content type of each "
            "message_attaches row of the message, named from the app's map of attachment classes to "
            "numbers (xsna/s34.java:48, written at messages/b.java:506). The attachment objects "
            "themselves (the attach column, written with the app's own Serializer) are not decoded and no "
            "attachment file is linked; the app has an image cache folder (cache/fresco_cache), and how "
            "its file names relate to an attachment was not traced. Edited and Hidden are is_edited and "
            "is_hidden shown as Yes or No; Expire TTL and Delete TTL are expire_ttl and delete_ttl as "
            "stored (messages/a.java:418-425), and the TTL columns were empty in the test data. Local ID "
            "and Conversation Message ID are local_id and cnv_msg_id. Not reported: the channel tables "
            "(channels, channel_messages, channels_recommendations), and what fills them was not traced; "
            "the full-text search tables, which repeat message and name text (messages/b.java:256); the "
            "dialog appearance, theme and background tables; and the app's other databases, which were "
            "not examined for message content."))),
        "paths": ('*/com.vkontakte.android/databases/vkim-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation Key",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
            }
        },
    },
    "vk_dialogs": {
        "name": "VK - Dialogs",
        "description": "Conversations the VK app listed in the dialogs table of its vkim-<number>.sqlite database.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            (
            (
            "Class and line references, Account Number and the reading of database copies are as in VK - "
            "Messages. One row per dialogs row. Dialog ID, Dialog Kind and Conversation are derived as in "
            "VK - Messages. Unread Count is count_unread, Last Conversation Message ID is last_msg_cnv_id "
            "and Members Count is chat_settings_members_count, all as stored; Members Count was empty in "
            "the test data. Messages in Database counts the rows of the messages table for that dialog, "
            "which need not be every message the conversation had. Database names the database copy each "
            "row was read from."))),
        "paths": ('*/com.vkontakte.android/databases/vkim-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "vk_users": {
        "name": "VK - Users",
        "description": "User profiles the VK app stored in the users table of its vkim-<number>.sqlite database.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            (
            (
            "Account Number and the reading of database copies are as in VK - Messages. One row per users "
            "row. First Name and Last Name are first_name_nom and last_name_nom (the app also stores "
            "other grammatical cases of the name, not reported). Domain, Mobile Phone and Friend Status "
            "are as stored, and the meaning of each Friend Status value was not traced. Blocked and "
            "Blocked by Me are shown as Yes or No. Deactivated is as stored, and the meaning of each "
            "value was not traced. Last Seen is online_last_seen, read as Unix milliseconds where the "
            "stored value has 13 digits; otherwise it is shown in Last Seen (as stored), which is blank "
            "when the value was converted. What sets it was not traced. Birthday joins birthday_year, "
            "birthday_month and birthday_day with hyphens; empty or zero parts are left out. The contacts "
            "table, which has local_phone, local_name and device_local_id columns, is not reported. "
            "Database names the database copy each row was read from."))),
        "paths": ('*/com.vkontakte.android/databases/vkim-*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import android_user, canonical_path, union_view_rows, \
    unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, is_sqlite_sidecar, logfunc

PACKAGE = 'com.vkontakte.android'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_DB_NAME = re.compile(r'vkim-(\d+)\.sqlite')
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_CHAT_BASE = 2000000000

# MsgDbType (messages/MsgDbType.java): the stored type value and the app's name for it.
MSG_TYPES = dict(enumerate((
    'UNSUPPORTED', 'FROM_USER', 'CHAT_CREATE', 'CHAT_TITLE_UPDATE', 'CHAT_AVATAR_UPDATE',
    'CHAT_AVATAR_REMOVE', 'CHAT_MEMBER_INVITE', 'CHAT_MEMBER_KICK', 'CHAT_JOIN_BY_LINK', 'PIN',
    'UNPIN', 'CHAT_MEMBER_INVITE_BY_MR', 'SCREENSHOT', 'GROUP_CALL_STARTED', 'MR_ACCEPTED',
    'CHAT_MEMBER_INVITE_BY_CALL', 'CHAT_MEMBER_INVITE_BY_CALL_LINK', 'CUSTOM',
    'CHAT_MEMBER_KICK_CALL_BLOCK', 'CHAT_DON_KICK', 'CHAT_UPDATE_STYLE', 'FROM_CHANNEL',
    'CALL_ASR_FAILED', 'CHAT_REQUEST_SENT', 'CHAT_REQUEST_REJECT', 'CHAT_OWNER_UDPATE',
    'CANNOT_CALL_PRIVACY_SETTINGS')))
# Peer.Type (com/vk/dto/common/Peer.java:80-107).
PEER_TYPES = {0: 'UNKNOWN', 1: 'USER', 2: 'EMAIL', 3: 'GROUP', 4: 'CHAT', 5: 'CONTACT', 6: 'CHANNEL'}
# The attachment class each content_type number stands for (xsna/s34.java:48).
ATTACH_TYPES = {
    1: 'Article', 2: 'Audio', 3: 'AudioMsg', 4: 'Call', 5: 'Doc', 8: 'Graffiti', 9: 'Image',
    10: 'Link', 11: 'Map', 12: 'Market', 15: 'Playlist', 16: 'Poll', 17: 'Sticker', 18: 'Story',
    19: 'Unsupported', 20: 'Video', 21: 'Wall', 22: 'WallReply', 23: 'PodcastEpisode', 24: 'Artist',
    26: 'Deleted', 27: 'Event', 28: 'MiniApp', 29: 'GroupCallInProgress', 30: 'GroupCallFinished',
    31: 'Curator', 32: 'DonutLink', 33: 'Widget', 34: 'Highlight', 35: 'VideoMsg',
    36: 'MiniAppSnippetData', 38: 'UgcSticker', 39: 'Question', 40: 'Room', 41: 'ChannelStub',
    42: 'ChannelMessage', 43: 'Gift'}


def _ms_to_utc(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        return ''


def _rows(path, query):
    """The rows of a query, or [] with a log line when the database cannot be read."""
    try:
        return list(get_sqlite_db_records(path, query))
    except sqlite3.DatabaseError as error:
        logfunc(f'VK: could not read {path}: {error}')
        return []


def _user(relative):
    user = android_user(relative)
    if user:
        return user
    match = _ROLLBACK.search(str(relative).replace('\\', '/'))
    return match.group(2) if match else '0'


def _stores(context):
    """{(app folder key, account number): {'paths': [copies], 'user': ..., 'account': ...}}."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.isdir(path) or is_sqlite_sidecar(path):
            continue
        match = _DB_NAME.fullmatch(os.path.basename(path))
        parts = os.path.normpath(path).replace('\\', '/').split('/')
        if not match or len(parts) < 3 or parts[-2] != 'databases' or parts[-3] != PACKAGE:
            continue
        relative = context.get_relative_path(path)
        container = canonical_path(context.get_relative_path(os.path.dirname(os.path.dirname(path))))[0]
        entry = stores.setdefault((container, match.group(1)), {
            'paths': [], 'user': _user(relative), 'account': match.group(1),
            'root': _evidence_root(relative)})
        entry['paths'].append(path)
    return dict(sorted(stores.items()))


def _union(context, entry, query):
    return union_view_rows(context, [(path, _rows(path, query)) for path in entry['paths']])


def _union_with_source(context, entry, query):
    """Rows joined across copies, each ending with the database it was read from.

    The database path differs between copies of one database, so it is left out when the
    copies' rows are compared."""
    file_rows = []
    for path in entry['paths']:
        relative = context.get_relative_path(path)
        file_rows.append((path, [tuple(row) + (relative,) for row in _rows(path, query)]))
    if not file_rows:
        return []
    width = max((len(rows[0]) for _, rows in file_rows if rows), default=0)
    return union_view_rows(context, file_rows, ignore=(width - 1,) if width else ())


_ROOT_STOP = ('data', 'data_mirror', 'userdata', 'user', 'user_de')


def _evidence_root(relative_path):
    """The folders above the device's storage in a relative path ('' for a plain /data dump)."""
    parts = str(relative_path).replace('\\', '/').strip('/').split('/')
    for index, part in enumerate(parts):
        if part in _ROOT_STOP or part == PACKAGE:
            return '/'.join(parts[:index])
    return '/'.join(parts[:-1])


def _dialog_kind(dialog_id):
    """The peer kind of a dialog id, by the ranges of the app's own classifier (Peer.java:261-281)."""
    try:
        dialog_id = int(dialog_id)
    except (TypeError, ValueError):
        return ''
    if dialog_id > 2147483647:
        return 'User'
    if dialog_id > _CHAT_BASE:
        return 'Chat'
    if dialog_id > 1900000000:
        return 'Contact'
    if dialog_id > 0:
        return 'User'
    if dialog_id < -2147483648:
        return 'Group'
    if dialog_id < -_CHAT_BASE:
        return 'Email'
    return 'Group' if dialog_id < 0 else 'Unknown'


def _names(context, entry):
    """(user names by id, group titles by id, chat titles by dialog id) from the first copy."""
    users, groups, chats = {}, {}, {}
    for uid, first, last in _union(context, entry,
                                   'SELECT id, first_name_nom, last_name_nom FROM users'):
        users.setdefault(uid, ' '.join(part for part in (first, last) if part))
    for gid, title in _union(context, entry, 'SELECT id, title FROM groups'):
        groups.setdefault(gid, title or '')
    for did, title in _union(context, entry, 'SELECT id, chat_settings_title FROM dialogs'):
        if title:
            chats.setdefault(did, title)
    return users, groups, chats


def _conversation(names, dialog_id):
    users, groups, chats = names
    kind = _dialog_kind(dialog_id)
    if kind == 'Chat':
        return chats.get(dialog_id, '')
    if kind == 'Group':
        return groups.get(-dialog_id, '')
    if kind == 'User':
        return users.get(dialog_id, '')
    return ''


@artifact_processor
def vk_messages(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry['paths'])
        names = _names(context, entry)
        attaches = {}
        for msg_id, content_type in _union(context, entry,
                                           'SELECT msg_local_id, content_type FROM message_attaches '
                                           'ORDER BY msg_local_id, position'):
            attaches.setdefault(msg_id, []).append(
                ATTACH_TYPES.get(content_type, str(content_type)))
        for (local_id, dialog_id, cnv_id, stamp, member_type, member_id, incoming, msg_type, body,
             edited, hidden, expire_ttl, delete_ttl, database) in _union_with_source(context, entry, '''
                SELECT local_id, dialog_id, cnv_msg_id, time, from_member_type, from_member_id,
                       is_incoming, type, body, is_edited, is_hidden, expire_ttl, delete_ttl
                FROM messages ORDER BY time'''):
            type_name = MSG_TYPES.get(msg_type, '' if msg_type is None else str(msg_type))
            sender_type = PEER_TYPES.get(member_type, '' if member_type is None else str(member_type))
            if sender_type == 'USER':
                sender = names[0].get(member_id, '')
            elif sender_type == 'GROUP':
                sender = names[1].get(member_id, '')
            else:
                sender = ''
            direction = 'Incoming' if incoming == 1 else 'Outgoing' if incoming == 0 else str(incoming)
            message = body or ''
            if not message and type_name and type_name != 'FROM_USER':
                message = f'[{type_name}]'
            data_list.append((
                _ms_to_utc(stamp), direction, sender, _conversation(names, dialog_id), message,
                ', '.join(attaches.get(local_id, [])), type_name, sender_id_or_blank(member_id),
                sender_type, dialog_id, _dialog_kind(dialog_id),
                _conversation_key(entry, dialog_id), _yes_no(edited), _yes_no(hidden),
                '' if expire_ttl is None else expire_ttl, '' if delete_ttl is None else delete_ttl,
                entry['account'], entry['user'], local_id, cnv_id, database))
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Sender', 'Conversation', 'Message', 'Attachments',
        'Message Type', 'Sender ID', 'Sender Type', 'Dialog ID', 'Dialog Kind', 'Conversation Key',
        'Edited', 'Hidden', 'Expire TTL (as stored)', 'Delete TTL (as stored)', 'Account Number',
        'Android User', 'Local ID', 'Conversation Message ID', 'Database')
    return data_headers, data_list, '\n'.join(sources)


def _conversation_key(entry, dialog_id):
    """Evidence root, Android user, account number and dialog: one key per conversation."""
    key = f"{entry['user']}/{entry['account']}/{dialog_id}"
    return f"{entry['root']}/{key}" if entry['root'] else key


def sender_id_or_blank(value):
    return '' if value is None else value


def _yes_no(value):
    return '' if value is None else 'Yes' if value else 'No'


@artifact_processor
def vk_dialogs(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry['paths'])
        names = _names(context, entry)
        counts = dict(_union(context, entry,
                             'SELECT dialog_id, COUNT(*) FROM messages GROUP BY dialog_id'))
        for dialog_id, unread, last_msg, members, database in _union_with_source(context, entry, '''
                SELECT id, count_unread, last_msg_cnv_id, chat_settings_members_count FROM dialogs
                ORDER BY id'''):
            data_list.append((
                _conversation(names, dialog_id), dialog_id, _dialog_kind(dialog_id),
                counts.get(dialog_id, 0), '' if unread is None else unread,
                '' if last_msg is None else last_msg, '' if members is None else members,
                entry['account'], entry['user'], database))
    data_headers = ('Conversation', 'Dialog ID', 'Dialog Kind', 'Messages in Database',
                    'Unread Count', 'Last Conversation Message ID', 'Members Count', 'Account Number',
                    'Android User', 'Database')
    return data_headers, data_list, '\n'.join(sources)


def _last_seen(value):
    if value is not None and len(str(value)) == 13:
        return _ms_to_utc(value)
    return ''


@artifact_processor
def vk_users(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry['paths'])
        for (uid, first, last, domain, phone, friend, blocked, blocked_by_me, deactivated, seen,
             day, month, year, database) in _union_with_source(context, entry, '''
                SELECT id, first_name_nom, last_name_nom, domain, mobile_phone, friend_status,
                       blocked, blocked_by_me, deactivated, online_last_seen, birthday_day,
                       birthday_month, birthday_year
                FROM users ORDER BY id'''):
            birthday = '-'.join(str(part) for part in (year, month, day) if part)
            data_list.append((
                _last_seen(seen), '' if seen is None or len(str(seen)) == 13 else seen, uid,
                first or '', last or '', domain or '', phone or '',
                '' if friend is None else friend, _yes_no(blocked), _yes_no(blocked_by_me),
                '' if deactivated is None else deactivated, birthday, entry['account'],
                entry['user'], database))
    data_headers = (('Last Seen', 'datetime'), 'Last Seen (as stored)', 'User ID', 'First Name',
                    'Last Name', 'Domain', 'Mobile Phone', 'Friend Status (as stored)', 'Blocked',
                    'Blocked by Me', 'Deactivated (as stored)', 'Birthday',
                    'Account Number', 'Android User', 'Database')
    return data_headers, data_list, '\n'.join(sources)
