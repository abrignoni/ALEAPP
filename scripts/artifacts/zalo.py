__artifacts_v2__ = {
    "zalo_messages": {
        "name": "Zalo - Messages",
        "description": "Messages from the ChatContent table of each Zalo conversation database, one "
                       "database per one to one or group conversation under each account folder, "
                       "with the media file the row's LocalPath names.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            (
            'Class and line references are to the Zalo 26.11.01 APK (base.apk SHA-256 '
            '16c7b2fc6ea88505f2cecea6dc6feb59af929fbd5d686b72e1221625697d3a43) decompiled with jadx 1.5.6'
            ' (--no-res); the classes are obfuscated, in defpackage unless named in full. Reads the '
            'ChatContent table of each conversation database under databases/<account id>/ of '
            'com.zing.zalo: <peer id>.db for a one to one conversation and group_<group id>.db for a '
            'group. A write-ahead log beside a database is applied; a database with no log beside it is '
            'read alone. Every storage spelling of one app data folder (data/data and data/user/0) is '
            "read as one folder. When one database is present under more than one of those spellings, "
            "a copy is also read when its database file, or the content of its -wal or -journal, "
            "matches no copy already read. A row equal in every reported column other than "
            "Conversation Database is reported once; a message that differs in any other reported "
            "column is reported once per version, and Conversation Database names the copy. Values "
            "are compared as read, after the conversions described here: in Message, a stored NULL "
            "and an empty string count as different, and so do a number and the same digits stored "
            "as text, though each pair looks the same in the report. When a copy cannot be read as a "
            "SQLite database, the failed read is logged, it gives no rows, and the other copies are "
            "still reported. A zero-byte copy gives no rows: for a conversation or _ext database the "
            "run log gets a no such table error, and for the zalo database nothing is logged. "
            "Where copies of the zalo database hold different "
            "names for Sender Name and Conversation, the name from the data/data copy is used, then "
            "data/user/<n>, then data_mirror. A rollback snapshot that is not byte identical to the "
            "live database is read as its own copy: its rows are reported in addition to the live "
            "rows, under the same Conversation Key. The Android user is read from the path, "
            "including a rollback snapshot under data/misc_ce/<n>/rollback or "
            "data/misc_de/<n>/rollback; a path that names no user is read as user 0. This copy "
            "handling is shown with synthetic stores only; no real image in the corpus has a second "
            "copy of a Zalo database. Account ID is "
            "the account folder's name, the same id Zalo stores as "
            'currentUserUid in its zalo database. Conversation Key is the Android user, the account and '
            'the conversation (group_<id> for a group) joined by slashes; it is what the conversation '
            'view groups by, so two accounts that talk to the same person keep separate conversations. '
            'Direction is derived, not stored: Outgoing when SenderId equals Account ID, otherwise '
            'Incoming. Timestamp is TimeStamp read as Unix milliseconds; a value too large for a date is '
            'left blank. In the decompiled Zalo code a message the app builds without a time takes it '
            'from vtg.c() (sv3.java:68-71, vv3.java:13077), which starts from z5q.a(), '
            'SystemClock.elapsedRealtime() less one stored value plus another (z5q.java:40), and when '
            'that is not above the highest time already held uses that time plus one (vtg.java:40-48). It'
            " is not a direct reading of the device clock. How a received message's time is set was not "
            "traced. Message Type is MsgType as stored and Type Name is the raw type name the app's "
            'MessageTypeMapper gives it (r9g.java:9): 0 and 20 are both webchat, 20 being a webchat '
            'message whose layoutType is 1 (q9g.java:19-20), and a type the mapper does not list has no '
            'Type Name. Status, TTL and Reply To Client ID (RefCliMsgId) are as stored; what each Status '
            "value means is not established. Media is the file the row's LocalPath names. An absolute "
            '/storage/emulated/<n>/Android/data/com.zing.zalo/ path is looked up below that folder for '
            'Android user <n>. A relative path starting zalo/picture/, zalo/voice/, zalo/paint, zalo/bg, '
            'zalo/data/, zalo/download, zalo/zinstant/chat or zalo/semicache, which the app resolves '
            'against one storage root (v9g.java:302, with zalo/semicache from ji7.java:22), is looked up '
            "below Android/data/com.zing.zalo/files/ for the database's Android user. The app falls back "
            'to another folder when its external files folder is not writable; that case is not looked '
            'up. Other relative prefixes and absolute paths outside that folder are not looked up, and '
            'those rows have a blank Media and a blank Media Format. A path that is looked up and matches'
            " no file shows File not in extraction in Media Format. Media Format is read from the file's "
            'first bytes, not its name; a JPEG XL file is checked in as media but shows in the report '
            'only where the browser supports JPEG XL. Zalo - Media Files lists the files of the media '
            'folders, including those no message names. Sender Name and Conversation come from the zalo '
            'database: the alias stored for the user under the account (alias_friend), else the display '
            "name in the account's contact_profile_friend_<account id> table, else contact_profile_5; a "
            "group's name is from group_info_v6. Hidden Chat is Yes when uid_hidden_chat_table holds the "
            "conversation's id, or group_<id> for a group, for the account; the group case was not "
            'exercised, and a blank does not show that a chat is not hidden. Message is MsgContent as '
            'stored. The BinNet blob and the E2EE, SeqId and FLStatus columns are not read, so a row with'
            ' no MsgContent and no LocalPath has no Message and no Media. Not reported: zalo_search.db (a'
            ' search index that repeats message text), zalo_x_1.db (message id and seen-status '
            'bookkeeping), call_data (call background image addresses, not call records), '
            'table_pin_board, poll_info, conversation_common_info2, phone_contacts_v2 (a copy of the '
            "device's contacts) and the app's settings and analytics stores.")),
        "paths": ('*/com.zing.zalo/databases/[0-9]*',
                  '*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*',
                  '*/Android/data/com.zing.zalo/files/zalo/picture/*',
                  '*/Android/data/com.zing.zalo/files/zalo/file_resource/*',
                  '*/Android/data/com.zing.zalo/files/zalo/voice/*',
                  '*/Android/data/com.zing.zalo/files/zalo/video/*',
                  '*/Android/data/com.zing.zalo/files/zalo/paint/*',
                  '*/Android/data/com.zing.zalo/files/zalo/recommend_link/*'),
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
                "senderColumn": "Sender Name",
                "mediaColumn": "Media",
            }
        },
    },
    "zalo_reactions": {
        "name": "Zalo - Reactions",
        "description": "Reactions from the Reaction table of each Zalo conversation's _ext database, "
                       "with the message each reaction is attached to.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Reads the Reaction table of each <conversation>_ext.db beside a conversation database. "
            "A write-ahead log beside a database is applied; a database with no log beside it is "
            "read alone. A reaction is matched to its message by client_id equal to the CliMsgId of "
            "a message in the conversation database of the same name, account and app data folder. "
            "Message Found says whether that message was found; Message and Message Timestamp are "
            "blank when it was not. Reactor ID is sender_id, Reaction is icon and Count is count, all "
            "as stored and not decoded; the table's writer was not traced. Timestamp is timestamp "
            "read as Unix milliseconds, which the stored 13-digit values fit; the app code that sets "
            "it was not traced. The fuid column is not reported because its meaning is not "
            "established. Account ID, Conversation, Conversation Key and Reactor Name are resolved as "
            "in Zalo - Messages. Copies of one database under more than one storage path are read as "
            "in Zalo - Messages; a reaction that differs in any reported column other than Database "
            "is listed once "
            "per version, and Database names the copy. With several copies of a conversation "
            "database, Message and Message Timestamp come from the first copy that holds the "
            "message."),
        "paths": ('*/com.zing.zalo/databases/[0-9]*',
                  '*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*'),
        "output_types": "standard",
        "artifact_icon": "smile",
    },
    "zalo_contacts": {
        "name": "Zalo - Contacts",
        "description": "Contact profiles Zalo stored in its zalo database, with the alias stored "
                       "for each under an account.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            (
            'Class and line references are to the Zalo 26.11.01 APK (base.apk SHA-256 '
            '16c7b2fc6ea88505f2cecea6dc6feb59af929fbd5d686b72e1221625697d3a43) decompiled with jadx 1.5.6'
            ' (--no-res); the classes are obfuscated, in defpackage unless named in full. Rows of each '
            'contact_profile_friend_<account id> table, one per account, and of contact_profile_5, which '
            "carries no account and has a blank Account ID. Stored Time is the row's timestamp. For a "
            'contact_profile_friend table the app sets it to System.currentTimeMillis() once per batch of'
            ' rows written (lw6.java:139 and 158), so every row of a batch shares it. For '
            'contact_profile_5 it is the time held by the profile object when the row is written '
            '(pw6.java:1926), which the app sets when it builds the profile from JSON '
            '(com/zing/zalo/control/ContactProfile.java:303). Neither is an action of the person. Display'
            ' Name is dpn, which ContactProfile reads from the JSON key dpn (ContactProfile.java:280). '
            'Alias is aliasName from alias_friend for that account and user; it is blank for '
            'contact_profile_5 rows, which carry no account. usr, Phone, Zalo Friend, ged and Date of '
            'Birth are usr, phone, isZaloFriend, ged and dob as stored; what usr and ged hold is not '
            'established, and dob holds the value of the JSON key sdob (ContactProfile.java:285, '
            'lw6.java:166). The stt, avt, cover, username and other profile columns are not reported. '
            'Copies of the zalo database under more than one storage path are read as in Zalo - '
            'Messages; a contact that differs in any reported column, alias included, is listed once '
            'per version, with no column naming the copy. Alias is taken from the same copy as the '
            'row.')),
        "paths": ('*/com.zing.zalo/databases/[0-9]*',
                  '*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "zalo_groups": {
        "name": "Zalo - Groups",
        "description": "Group conversations Zalo stored in group_info_v6, per account.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Rows of group_info_v6, one per account (currentUserUid) and group. Group ID is the id "
            "column; Zalo - Messages names a group conversation by the number in its group_<id>.db "
            "file name. Creator Name is resolved as Sender Name is in Zalo - Messages. Member Count "
            "is totalMem and Member IDs is member_uids, as stored. ts is the stored value, not "
            "converted, because what it records was not traced in the app code. The admin_uids, "
            "settingJson, avatar_new and other columns are not reported. Copies of the zalo database "
            "under more than one storage path are read as in Zalo - Messages; a group that differs in "
            "any reported column is listed once per version, with no column naming the "
            "copy."),
        "paths": ('*/com.zing.zalo/databases/[0-9]*',
                  '*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "zalo_media": {
        "name": "Zalo - Media Files",
        "description": "Files in the Zalo media folders that message LocalPath values point into, "
                       "with the conversations whose messages name each file, including files no "
                       "message names.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "One row per file below Android/data/com.zing.zalo/files/zalo/ in the folders picture, "
            "file_resource, voice, video, paint and recommend_link, per Android user. Those are the "
            "folders message LocalPath values pointed into; the app's caches beside them (semicache, "
            "sticker, zinstant, call_asr) are not listed. Named by a Message is Yes when a message's "
            "LocalPath resolves to the file as in Zalo - Messages, and Conversation Keys lists those "
            "conversations; No marks a file no message in the extraction names. Copies of one file "
            "under more than one storage path are each listed when their bytes differ. Their rows "
            "differ only in Media and, where the sizes differ, Size (bytes); the storage path of "
            "each copy is not shown. The message row in Zalo - Messages shows one of them, the first "
            "the file search returned; which storage path that is was not established. Media Format is read from the file's first "
            "bytes. File times are not reported."),
        "paths": ('*/com.zing.zalo/databases/[0-9]*',
                  '*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*',
                  '*/Android/data/com.zing.zalo/files/zalo/picture/*',
                  '*/Android/data/com.zing.zalo/files/zalo/file_resource/*',
                  '*/Android/data/com.zing.zalo/files/zalo/voice/*',
                  '*/Android/data/com.zing.zalo/files/zalo/video/*',
                  '*/Android/data/com.zing.zalo/files/zalo/paint/*',
                  '*/Android/data/com.zing.zalo/files/zalo/recommend_link/*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
}

import hashlib
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
from scripts.ilapfuncs import (artifact_processor, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, is_sqlite_sidecar, logfunc)

PACKAGE = 'com.zing.zalo'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Stored message type to Zalo's raw type name: MessageTypeMapper (r9g.b and q9g.c in the
# decompiled Zalo 26.11.01 code). Type 0 and 20 are both 'webchat'; 20 is a webchat message
# whose layoutType is 1. A type the mapper does not list is left without a name.
TYPE_NAMES = {
    0: 'webchat', 20: 'webchat (layoutType 1)',
    2: 'chat.doodle', 3: 'chat.photo', 4: 'chat.photo', 31: 'chat.photo', 6: 'chat.voice',
    10: 'chat.sticker', 12: 'chat.recommended', 15: 'chat.list.action', 18: 'chat.location.new',
    19: 'chat.video.msg', 21: 'chat.ecard', 22: 'share.file', 23: 'chat.gif',
    24: 'chat.webcontent', 25: 'chat.video.live.msg', 26: 'group.poll', 28: 'chat.video.memo',
    29: 'chat.sync.theme', 32: 'chat.livelocation', 44: 'chat.msg.update',
    53: 'chat.webcontent.v2',
}

# The folders below Android/data/com.zing.zalo/files/zalo that message LocalPath values point
# into; Zalo - Media Files lists every file in them.
MEDIA_FOLDERS = ('picture', 'file_resource', 'voice', 'video', 'paint', 'recommend_link')

# Relative LocalPath prefixes Zalo resolves against one app storage root (v9g.D in the same
# code; zalo/semicache is ji7.d). The root is the app's external files folder,
# Android/data/com.zing.zalo/files.
RELATIVE_PREFIXES = ('zalo/voice/', 'zalo/bg', 'zalo/paint', 'zalo/picture/', 'zalo/data/',
                     'zalo/download', 'zalo/zinstant/chat', 'zalo/semicache')


def _ms_to_utc(value):
    """Unix milliseconds to a UTC datetime, or '' for an empty, zero or out of range value."""
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


def _parts(path):
    return os.path.normpath(str(path)).replace('\\', '/').split('/')


def _container(path):
    """The app data folder a staged path belongs to: the path up to its com.zing.zalo segment."""
    parts = _parts(path)
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == PACKAGE:
            return '/'.join(parts[:index + 1])
    return None


_ROOT_STOP = ('data', 'data_mirror', 'media', 'mnt', 'storage', 'sdcard', 'userdata', 'user',
              'user_de')
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')


def _evidence_root(relative_path):
    """The folders above the device's storage in a relative path ('' for a plain /data dump).

    Two devices in one input sit under different roots, so their files are never joined."""
    parts = str(relative_path).replace('\\', '/').strip('/').split('/')
    for index, part in enumerate(parts):
        if part in _ROOT_STOP:
            return '/'.join(parts[:index])
    return '/'.join(parts[:-1])


def _android_user(context, path):
    """The Android user whose storage holds a path, read from a rollback snapshot path too.

    A path under no app data folder and no rollback snapshot is read as user 0."""
    relative = context.get_relative_path(path)
    user = android_user(relative)
    if user:
        return user
    match = _ROLLBACK.search(str(relative).replace('\\', '/'))
    return match.group(2) if match else '0'


def _stores(context):
    """Per app data folder: the zalo database and the conversation databases per account.

    Every spelling of one app data folder is grouped under one key. A copy of a database under
    another storage spelling (data/data and data/user/0) is kept when it is not byte identical,
    so 'mains' and 'conversations' can hold several copies of one file; the four database
    artifacts join the rows read from them with union_view_rows."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.isdir(path) or is_sqlite_sidecar(path):
            continue
        container = _container(path)
        if not container:
            continue
        rel = path[len(container):].replace('\\', '/').strip('/').split('/')
        if len(rel) < 2 or rel[0] != 'databases':
            continue
        key = canonical_path(context.get_relative_path(container))[0]
        entry = stores.setdefault(key, {'mains': [], 'conversations': [],
                                        'user': _android_user(context, path),
                                        'root': _evidence_root(context.get_relative_path(path))})
        if len(rel) == 2 and rel[1] == 'zalo':
            entry['mains'].append(path)
        elif len(rel) == 3 and rel[1].isdigit() and rel[2].endswith('.db'):
            name = rel[2][:-3]
            is_ext = name.endswith('_ext')
            base = name[:-4] if is_ext else name
            is_group = base.startswith('group_')
            conversation = base[len('group_'):] if is_group else base
            if conversation.isdigit():
                entry['conversations'].append({
                    'path': path, 'account': rel[1], 'conversation': conversation,
                    'group': is_group, 'ext': is_ext, 'base': base,
                    'thread': ('group_' if is_group else '') + conversation})
    for entry in stores.values():
        entry['conversations'].sort(key=lambda item: (item['account'], item['base'], item['ext']))
    return dict(sorted(stores.items()))


def _conversation_key(entry, item):
    """Android user, account and thread: one key per conversation, never shared by accounts."""
    key = f"{entry['user']}/{item['account']}/{item['thread']}"
    return f"{entry['root']}/{key}" if entry['root'] else key


def _rows(path, query):
    """The rows of a query, or [] with a log line when the database cannot be read.

    A damaged copy of a store is then skipped and the readable copies are still reported."""
    try:
        return list(get_sqlite_db_records(path, query))
    except sqlite3.DatabaseError as error:
        logfunc(f'Zalo: could not read {path}: {error}')
        return []


def _names(mains):
    """Lookups from the zalo database copies: aliases, profile names, group names, hidden chats.

    Where copies hold different non-empty names, the first copy's name is used (the order
    unique_files ranks them: data/data, then data/user/<n>, then data_mirror)."""
    names = {'alias': {}, 'profile': {}, 'shared_profile': {}, 'group': {}, 'hidden': set()}
    for main in reversed(mains):
        _add_names(names, main)
    return names


def _add_names(names, main):
    if does_table_exist_in_db(main, 'alias_friend'):
        for account, uid, alias in _rows(main, 'SELECT currentUserUid, uIdTo, aliasName FROM alias_friend'):
            if alias:
                names['alias'][(str(account), str(uid))] = alias
    tables = [row[0] for row in _rows(
        main, "SELECT name FROM sqlite_master WHERE type = 'table' "
              "AND name LIKE 'contact_profile_friend_%'")]
    for table in tables:
        account = table[len('contact_profile_friend_'):]
        for uid, display in _rows(main, f'SELECT uid, dpn FROM "{table}"'):
            if display:
                names['profile'][(account, str(uid))] = display
    if does_table_exist_in_db(main, 'contact_profile_5'):
        for uid, display in _rows(main, 'SELECT uid, dpn FROM contact_profile_5'):
            if display:
                names['shared_profile'][str(uid)] = display
    if does_table_exist_in_db(main, 'group_info_v6'):
        for account, group_id, name in _rows(main, 'SELECT currentUserUid, id, name FROM group_info_v6'):
            if name:
                names['group'][(str(account), str(group_id))] = name
    if does_table_exist_in_db(main, 'uid_hidden_chat_table'):
        for account, uid in _rows(main, 'SELECT currentUserUid, uid FROM uid_hidden_chat_table'):
            names['hidden'].add((str(account), str(uid)))


def _person(names, account, uid):
    uid = str(uid)
    return (names['alias'].get((account, uid)) or names['profile'].get((account, uid))
            or names['shared_profile'].get(uid) or '')


def _conversation_label(names, item):
    if item['group']:
        return names['group'].get((item['account'], item['conversation']), '') or ''
    return _person(names, item['account'], item['conversation'])


def _sniff(path):
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return 'Not readable'
    if head[:2] == b'\xff\x0a' or head[:12] == b'\x00\x00\x00\x0cJXL \r\n\x87\n':
        return 'JPEG XL'
    if head[:3] == b'\xff\xd8\xff':
        return 'JPEG'
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'PNG'
    if head[:6] in (b'GIF87a', b'GIF89a'):
        return 'GIF'
    if head[4:8] == b'ftyp':
        return 'ISO base media (MP4 family)'
    if head[:4] == b'\x1a\x45\xdf\xa3':
        return 'Matroska/WebM'
    if head[:4] == b'%PDF':
        return 'PDF'
    if head[:3] == b'ID3' or head[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'):
        return 'MP3'
    if head[:2] in (b'\xff\xf1', b'\xff\xf9'):
        return 'AAC (ADTS)'
    if head[:4] == b'OggS':
        return 'Ogg'
    if head[:4] == b'RIFF':
        return 'RIFF'
    return 'Unknown'


def _escape(text):
    return re.sub(r'([\[\]*?])', r'[\1]', text)


def _media_user_and_tail(relative_path):
    """(Android user, path below Android/data/com.zing.zalo) for a staged media file."""
    path = '/' + str(relative_path).replace('\\', '/').lstrip('/')
    marker = f'/Android/data/{PACKAGE}/'
    if marker not in path:
        return None, None
    head, tail = path.split(marker, 1)
    user = head.rstrip('/').split('/')[-1]
    return (user if user.isdigit() else '0'), tail


def _digest(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            sha.update(block)
    return sha.hexdigest()


def _distinct(paths):
    """The paths with byte-identical copies dropped, first copy kept, order kept."""
    if len(paths) < 2:
        return list(paths)
    kept = {}
    for path in paths:
        try:
            kept.setdefault((os.path.getsize(path), _digest(path)), path)
        except OSError:
            kept.setdefault(('unreadable', path), path)
    return list(kept.values())


def _media_index(context):
    """{(evidence root, Android user, tail): [staged paths]} for the media folder files.

    Copies of one file under several storage spellings are kept when their bytes differ."""
    index = {}
    for file_found in unique_files(context):
        path = str(file_found)
        if not os.path.isfile(path):
            continue
        relative = context.get_relative_path(path)
        user, tail = _media_user_and_tail(relative)
        parts = tail.split('/') if tail else []
        if len(parts) >= 4 and parts[0] == 'files' and parts[1] == 'zalo' and parts[2] in MEDIA_FOLDERS:
            index.setdefault((_evidence_root(relative), user, tail), []).append(path)
    return {key: _distinct(paths) for key, paths in index.items()}


def _media_tail(local_path):
    """The part of a LocalPath below Android/data/com.zing.zalo, with the Android user it names."""
    if not local_path:
        return None, None
    match = re.match(r'^/storage/emulated/(\d+)/Android/data/com\.zing\.zalo/(.+)$', local_path)
    if match:
        return match.group(1), match.group(2)
    if local_path.startswith(RELATIVE_PREFIXES):
        return None, 'files/' + local_path
    return None, None


def _media_key(entry, local_path):
    user, tail = _media_tail(local_path)
    if not tail:
        return None
    return (entry['root'], user or entry['user'], tail)


def _in_media_folder(tail):
    parts = tail.split('/')
    return len(parts) >= 3 and parts[0] == 'files' and parts[1] == 'zalo' and parts[2] in MEDIA_FOLDERS


def _media(context, seeker, index, cache, key):
    """(media reference, format) for a resolved LocalPath key."""
    if key is None:
        return '', ''
    if key not in cache:
        copies = index.get(key)
        path = copies[0] if copies else None
        root, user, tail = key
        if path is None and not _in_media_folder(tail):
            # A resolvable path outside the indexed folders is looked up on its own, in the
            # same evidence root and for the same Android user.
            pattern = f'*/{user}/Android/data/{PACKAGE}/' + _escape(tail)
            found = [str(p) for p in seeker.search(pattern) if os.path.isfile(str(p))
                     and _evidence_root(context.get_relative_path(str(p))) == root]
            path = found[0] if found else None
        if path:
            cache[key] = (check_in_media(path, os.path.basename(path)) or '', _sniff(path))
        else:
            cache[key] = ('', 'File not in extraction')
    return cache[key]


@artifact_processor
def zalo_messages(context):
    seeker = context.get_seeker()
    index = _media_index(context)
    media_cache = {}
    data_list = []
    sources = []
    for _container_key, entry in _stores(context).items():
        names = _names(entry['mains'])
        sources.extend(entry['mains'])
        file_rows = []
        for item in entry['conversations']:
            if item['ext']:
                continue
            item_rows = []
            file_rows.append((item['path'], item_rows))
            rows = _rows(item['path'], '''
                SELECT TimeStamp, SenderId, MsgContent, LocalPath, MsgType, MsgStatus,
                       RefCliMsgId, CliMsgId, GlbMsgId, TTL
                FROM ChatContent ORDER BY TimeStamp''')
            sources.append(item['path'])
            account = item['account']
            label = _conversation_label(names, item)
            hidden = 'Yes' if (account, item['thread']) in names['hidden'] else ''
            conversation_key = _conversation_key(entry, item)
            for stamp, sender, content, local_path, msg_type, status, ref, cli, glb, ttl in rows:
                outgoing = str(sender) == account
                media, media_format = _media(context, seeker, index, media_cache,
                                             _media_key(entry, local_path))
                item_rows.append((
                    _ms_to_utc(stamp), 'Outgoing' if outgoing else 'Incoming',
                    _person(names, account, sender), label, content, media, account,
                    item['conversation'], conversation_key, 'Yes' if item['group'] else 'No',
                    hidden, sender, media_format, msg_type, TYPE_NAMES.get(msg_type, ''), status,
                    ref if ref is not None else '', cli, glb, ttl if ttl is not None else '',
                    local_path or '', context.get_relative_path(item['path'])))
        # The last column, the database's path, differs between copies of one database.
        data_list.extend(union_view_rows(context, file_rows, ignore=(21,)))
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Sender Name', 'Conversation', 'Message',
        ('Media', 'media'), 'Account ID', 'Conversation ID', 'Conversation Key', 'Group Chat',
        'Hidden Chat', 'Sender ID', 'Media Format', 'Message Type', 'Type Name',
        'Status (as stored)', 'Reply To Client ID', 'Client Message ID', 'Global Message ID',
        'TTL (as stored)', 'Local Path (as stored)', 'Conversation Database')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zalo_reactions(context):
    data_list = []
    sources = []
    for _container_key, entry in _stores(context).items():
        names = _names(entry['mains'])
        messages = {}
        for item in entry['conversations']:
            if not item['ext']:
                messages.setdefault((item['account'], item['base']), []).append(item)
        file_rows = []
        for item in entry['conversations']:
            if not item['ext']:
                continue
            item_rows = []
            file_rows.append((item['path'], item_rows))
            rows = _rows(item['path'], '''
                SELECT timestamp, sender_id, icon, count, client_id, global_id FROM Reaction
                ORDER BY timestamp''')
            sources.append(item['path'])
            targets = {}
            for message_db in messages.get((item['account'], item['base']), []):
                for cli, stamp, content in _rows(message_db['path'],
                                                 'SELECT CliMsgId, TimeStamp, MsgContent FROM ChatContent'):
                    targets.setdefault(cli, (stamp, content))
            account = item['account']
            label = _conversation_label(names, item)
            conversation_key = _conversation_key(entry, item)
            for stamp, sender, icon, count, cli, glb in rows:
                target_stamp, target_text = targets.get(cli, ('', ''))
                item_rows.append((
                    _ms_to_utc(stamp), _ms_to_utc(target_stamp), account, label,
                    item['conversation'], conversation_key, sender, _person(names, account, sender),
                    icon, count, target_text, 'Yes' if cli in targets else 'No', cli, glb,
                    context.get_relative_path(item['path'])))
        data_list.extend(union_view_rows(context, file_rows, ignore=(14,)))
    data_headers = (
        ('Timestamp', 'datetime'), ('Message Timestamp', 'datetime'), 'Account ID', 'Conversation',
        'Conversation ID', 'Conversation Key', 'Reactor ID', 'Reactor Name', 'Reaction (as stored)',
        'Count', 'Message', 'Message Found', 'Client Message ID', 'Global Message ID', 'Database')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zalo_contacts(context):
    data_list = []
    sources = []
    for _container_key, entry in _stores(context).items():
        file_rows = []
        for main in entry['mains']:
            sources.append(main)
            main_rows = []
            file_rows.append((main, main_rows))
            # Each copy's own aliases, so an alias that differs between copies is kept.
            _contact_rows(main, _names([main]), main_rows)
        data_list.extend(union_view_rows(context, file_rows))
    data_headers = (
        ('Stored Time', 'datetime'), 'Account ID', 'User ID', 'Display Name', 'Alias',
        'usr (as stored)', 'Phone (as stored)', 'Zalo Friend (as stored)',
        'ged (as stored)', 'Date of Birth (as stored)', 'Table')
    return data_headers, data_list, '\n'.join(sources)


def _contact_rows(main, names, data_list):
    """Append the contact rows of one zalo database copy to data_list."""
    tables = [row[0] for row in _rows(
        main, "SELECT name FROM sqlite_master WHERE type = 'table' "
              "AND name LIKE 'contact_profile_friend_%' ORDER BY name")]
    if does_table_exist_in_db(main, 'contact_profile_5'):
        tables.append('contact_profile_5')
    for table in tables:
        account = table[len('contact_profile_friend_'):] if table != 'contact_profile_5' else ''
        for stamp, uid, display, user, phone, friend, gender, dob in _rows(
                main, f'SELECT timestamp, uid, dpn, usr, phone, isZaloFriend, ged, dob '
                      f'FROM "{table}" ORDER BY uid'):
            alias = names['alias'].get((account, str(uid)), '') if account else ''
            data_list.append((
                _ms_to_utc(stamp), account, uid, display or '', alias, user or '', phone or '',
                friend if friend is not None else '', gender if gender is not None else '',
                dob or '', table))


@artifact_processor
def zalo_groups(context):
    data_list = []
    sources = []
    for _container_key, entry in _stores(context).items():
        names = _names(entry['mains'])
        file_rows = []
        for main in entry['mains']:
            if not does_table_exist_in_db(main, 'group_info_v6'):
                continue
            sources.append(main)
            main_rows = []
            file_rows.append((main, main_rows))
            for account, group_id, name, creator, total, members, stamp in _rows(
                    main, 'SELECT currentUserUid, id, name, creatorId, totalMem, member_uids, ts '
                          'FROM group_info_v6 ORDER BY currentUserUid, id'):
                account = str(account)
                main_rows.append((
                    account, group_id, name or '', creator, _person(names, account, creator),
                    total if total is not None else '', members or '',
                    stamp if stamp is not None else ''))
        data_list.extend(union_view_rows(context, file_rows))
    if not data_list and sources:
        logfunc('Zalo - Groups: group_info_v6 holds no rows')
    data_headers = (
        'Account ID', 'Group ID', 'Group Name', 'Creator ID', 'Creator Name', 'Member Count',
        'Member IDs (as stored)', 'ts (as stored)')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zalo_media(context):
    index = _media_index(context)
    references = {}
    for _container_key, entry in _stores(context).items():
        for item in entry['conversations']:
            if item['ext']:
                continue
            for (local_path,) in _rows(item['path'],
                                       "SELECT LocalPath FROM ChatContent WHERE LocalPath <> ''"):
                key = _media_key(entry, local_path)
                if key in index:
                    references.setdefault(key, set()).add(_conversation_key(entry, item))
    data_list = []
    sources = []
    for (root, user, tail), copies in sorted(index.items()):
        keys = sorted(references.get((root, user, tail), ()))
        for path in copies:
            sources.append(path)
            data_list.append((
                check_in_media(path, os.path.basename(path)) or '', _sniff(path),
                os.path.getsize(path), os.path.basename(path), tail.split('/')[2], user,
                'Yes' if keys else 'No', '\n'.join(keys)))
    data_headers = (
        ('Media', 'media'), 'Media Format', 'Size (bytes)', 'File Name', 'Folder', 'Android User',
        'Named by a Message', 'Conversation Keys')
    return data_headers, data_list, '\n'.join(sources)
