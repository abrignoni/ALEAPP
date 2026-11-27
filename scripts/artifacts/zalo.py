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
        "notes": "Reads the ChatContent table of each conversation database under databases/<account id>/ of com.zing.zalo: <peer id>.db for a one to one conversation and group_<group id>.db for a group. A write-ahead log beside a database is applied; a database with no log beside it is read alone. Account ID is the account folder's name, the same id Zalo stores as currentUserUid in its zalo database. Direction is derived, not stored: Outgoing when SenderId equals Account ID, otherwise Incoming. Timestamp is TimeStamp read as Unix milliseconds. In the decompiled Zalo 26.11.01 code a message the app builds without a time takes it from a clock made of SystemClock.elapsedRealtime() and a stored server time (classes sv3, vv3, vtg and z5q); when that value is not above the highest time already held, the app uses that highest time plus one. It is not a direct reading of the device clock. How a received message's time is set was not traced. Message Type is MsgType as stored and Type Name is the raw type name the app's MessageTypeMapper gives it (classes r9g and q9g): 0 and 20 are both webchat, 20 being a webchat message whose layoutType is 1, and a type the mapper does not list has no Type Name. Status, TTL and Reply To Client ID (RefCliMsgId) are as stored; what each Status value means is not established. Media is the file the row's LocalPath names. An absolute /storage/emulated/<n>/Android/data/com.zing.zalo/ path is looked up below that folder for Android user <n>. A relative path starting zalo/picture/, zalo/voice/, zalo/paint, zalo/bg, zalo/data/, zalo/download, zalo/zinstant/chat or zalo/semicache, which the app resolves against its external files folder (v9g.D, ji7), is looked up below Android/data/com.zing.zalo/files/ for the database's Android user. The app falls back to another folder when its external files folder is not writable; that case is not looked up. Other relative prefixes and absolute paths outside that folder are not looked up, and those rows have a blank Media and a blank Media Format. A path that is looked up and matches no file shows File not in extraction in Media Format. Media Format is read from the file's first bytes, not its name; a JPEG XL file is checked in as media but shows in the report only where the browser supports JPEG XL. Sender Name and Conversation come from the zalo database: the alias stored for the user under the account (alias_friend), else the display name in the account's contact_profile_friend_<account id> table, else contact_profile_5; a group's name is from group_info_v6. Hidden Chat is Yes when uid_hidden_chat_table holds the conversation's id, or group_<id> for a group, for the account; the group case was not exercised, and a blank does not show that a chat is not hidden. Message is MsgContent as stored. The BinNet blob and the E2EE, SeqId and FLStatus columns are not read, so a row with no MsgContent and no LocalPath has no Message and no Media.",
        "paths": ('*/com.zing.zalo/databases/[0-9]*',
                  '*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
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
        "notes": "Reads the Reaction table of each <conversation>_ext.db beside a conversation database. A write-ahead log beside a database is applied; a database with no log beside it is read alone. A reaction is matched to its message by client_id equal to the CliMsgId of a message in the conversation database of the same name. Message Found says whether that message was found; Message and Message Timestamp are blank when it was not. Reactor ID is sender_id, Reaction is icon and Count is count, all as stored and not decoded; the table's writer was not traced. Timestamp is timestamp read as Unix milliseconds, which the stored 13-digit values fit; the app code that sets it was not traced. The fuid column is not reported because its meaning is not established. Account ID, Conversation and Reactor Name are resolved as in Zalo - Messages.",
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
        "notes": "Rows of each contact_profile_friend_<account id> table, one per account, and of contact_profile_5, which carries no account and has a blank Account ID. Stored Time is the row's timestamp. For a contact_profile_friend table the decompiled Zalo 26.11.01 code sets it to System.currentTimeMillis() once per batch of rows written (class lw6), so every row of a batch shares it. For contact_profile_5 it is the time held by the profile object when the row is written (class pw6), which the app sets when it builds the profile from JSON. Neither is an action of the person. Display Name is dpn, which the app's ContactProfile class reads from the JSON key dpn. Alias is aliasName from alias_friend for that account and user; it is blank for contact_profile_5 rows, which carry no account. usr, Phone, Zalo Friend, ged and Date of Birth are usr, phone, isZaloFriend, ged and dob as stored; what usr and ged hold is not established, and dob holds the value of the JSON key sdob (ContactProfile, lw6). The stt, avt, cover, username and other profile columns are not reported.",
        "paths": ('*/com.zing.zalo/databases/zalo',
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
        "notes": 'Rows of group_info_v6, one per account (currentUserUid) and group. Group ID is the id column; Zalo - Messages names a group conversation by the number in its group_<id>.db file name. Creator Name is resolved as Sender Name is in Zalo - Messages. Member Count is totalMem and Member IDs is member_uids, as stored. ts is the stored value, not converted, because what it records was not traced in the app code. The admin_uids, settingJson, avatar_new and other columns are not reported.',
        "paths": ('*/com.zing.zalo/databases/zalo',
                  '*/com.zing.zalo/databases/zalo-*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}

import os
import re
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import (artifact_processor, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, is_sqlite_sidecar, logfunc)

PACKAGE = 'com.zing.zalo'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Stored message type to Zalo's own action name: MessageTypeMapper (r9g.b and q9g.c in the
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

# Relative LocalPath prefixes Zalo resolves against one app storage root (v9g.D in the same
# code; zalo/semicache is ji7.d). The root is the app's external files folder, Android/data/com.zing.zalo/files.
RELATIVE_PREFIXES = ('zalo/voice/', 'zalo/bg', 'zalo/paint', 'zalo/picture/', 'zalo/data/',
                     'zalo/download', 'zalo/zinstant/chat', 'zalo/semicache')


def _ms_to_utc(value):
    """Unix milliseconds to a UTC datetime, or '' for an empty or zero value."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _parts(path):
    return os.path.normpath(str(path)).replace('\\', '/').split('/')


def _container(path):
    """The app data folder a staged path belongs to: the path up to its com.zing.zalo segment."""
    parts = _parts(path)
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == PACKAGE:
            return '/'.join(parts[:index + 1])
    return None


def _android_user(context, path):
    """The Android user whose storage holds a path, 0 when the path names none."""
    return android_user(context.get_relative_path(path)) or '0'


def _stores(context):
    """Per app data folder: the zalo database and the conversation databases per account.

    Duplicate storage views of one file (data/data and data/user/0) are read once."""
    stores = {}
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.isdir(path) or is_sqlite_sidecar(path):
            continue
        container = _container(path)
        if not container:
            continue
        rel = path[len(container):].replace('\\', '/').strip('/').split('/')
        if len(rel) < 2 or rel[0] != 'databases':
            continue
        entry = stores.setdefault(container, {'main': None, 'conversations': []})
        if len(rel) == 2 and rel[1] == 'zalo':
            entry['main'] = path
        elif len(rel) == 3 and rel[1].isdigit() and rel[2].endswith('.db'):
            name = rel[2][:-3]
            is_ext = name.endswith('_ext')
            base = name[:-4] if is_ext else name
            is_group = base.startswith('group_')
            conversation = base[len('group_'):] if is_group else base
            if conversation.isdigit():
                entry['conversations'].append({
                    'path': path, 'account': rel[1], 'conversation': conversation,
                    'group': is_group, 'ext': is_ext})
    for entry in stores.values():
        entry['conversations'].sort(key=lambda item: item['path'])
    return dict(sorted(stores.items()))


def _rows(path, query):
    return list(get_sqlite_db_records(path, query))


def _names(main):
    """Lookups from the zalo database: aliases, profile names, group names, hidden chats."""
    names = {'alias': {}, 'profile': {}, 'shared_profile': {}, 'group': {}, 'hidden': set()}
    if not main:
        return names
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
            names['group'][(str(account), str(group_id))] = name
    if does_table_exist_in_db(main, 'uid_hidden_chat_table'):
        for account, uid in _rows(main, 'SELECT currentUserUid, uid FROM uid_hidden_chat_table'):
            names['hidden'].add((str(account), str(uid)))
    return names


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


def _media(context, seeker, cache, database, local_path):
    """(media reference, format) for a LocalPath, looked up under the same Android user."""
    user, tail = _media_tail(local_path)
    if not tail:
        return '', ''
    user = user or _android_user(context, database)
    key = (user, tail)
    if key not in cache:
        pattern = f'*/{user}/Android/data/{PACKAGE}/' + _escape(tail)
        found = [str(p) for p in seeker.search(pattern) if os.path.isfile(str(p))]
        if found:
            cache[key] = (check_in_media(found[0], os.path.basename(found[0])) or '', _sniff(found[0]))
        else:
            cache[key] = ('', 'File not in extraction')
    return cache[key]


@artifact_processor
def zalo_messages(context):
    seeker = context.get_seeker()
    data_list = []
    sources = []
    for _container_path, entry in _stores(context).items():
        names = _names(entry['main'])
        if entry['main']:
            sources.append(entry['main'])
        media_cache = {}
        for item in entry['conversations']:
            if item['ext']:
                continue
            rows = _rows(item['path'], '''
                SELECT TimeStamp, SenderId, MsgContent, LocalPath, MsgType, MsgStatus,
                       RefCliMsgId, CliMsgId, GlbMsgId, TTL
                FROM ChatContent ORDER BY TimeStamp''')
            sources.append(item['path'])
            account = item['account']
            label = _conversation_label(names, item)
            thread = ('group_' if item['group'] else '') + item['conversation']
            hidden = 'Yes' if (account, thread) in names['hidden'] else ''
            for stamp, sender, content, local_path, msg_type, status, ref, cli, glb, ttl in rows:
                outgoing = str(sender) == account
                media, media_format = _media(context, seeker, media_cache, item['path'], local_path)
                data_list.append((
                    _ms_to_utc(stamp), 'Outgoing' if outgoing else 'Incoming',
                    _person(names, account, sender), label, content, media, account,
                    item['conversation'], 'Yes' if item['group'] else 'No', hidden, sender,
                    media_format, msg_type, TYPE_NAMES.get(msg_type, ''), status, ref if ref is not None else '',
                    cli, glb, ttl if ttl is not None else '', local_path or '',
                    context.get_relative_path(item['path'])))
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Sender Name', 'Conversation', 'Message',
        ('Media', 'media'), 'Account ID', 'Conversation ID', 'Group Chat', 'Hidden Chat',
        'Sender ID', 'Media Format', 'Message Type', 'Type Name', 'Status (as stored)', 'Reply To Client ID',
        'Client Message ID', 'Global Message ID', 'TTL (as stored)', 'Local Path (as stored)',
        'Conversation Database')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zalo_reactions(context):
    data_list = []
    sources = []
    for _container_path, entry in _stores(context).items():
        names = _names(entry['main'])
        messages = {item['path'][:-len('.db')]: item for item in entry['conversations'] if not item['ext']}
        for item in entry['conversations']:
            if not item['ext']:
                continue
            rows = _rows(item['path'], '''
                SELECT timestamp, sender_id, icon, count, client_id, global_id FROM Reaction
                ORDER BY timestamp''')
            sources.append(item['path'])
            message_db = messages.get(item['path'][:-len('_ext.db')])
            targets = {}
            if message_db:
                for cli, stamp, content in _rows(message_db['path'],
                                                 'SELECT CliMsgId, TimeStamp, MsgContent FROM ChatContent'):
                    targets[cli] = (stamp, content)
            account = item['account']
            label = _conversation_label(names, item)
            for stamp, sender, icon, count, cli, glb in rows:
                target_stamp, target_text = targets.get(cli, ('', ''))
                data_list.append((
                    _ms_to_utc(stamp), _ms_to_utc(target_stamp), account, label,
                    item['conversation'], sender, _person(names, account, sender), icon, count,
                    target_text, 'Yes' if cli in targets else 'No', cli, glb,
                    context.get_relative_path(item['path'])))
    data_headers = (
        ('Timestamp', 'datetime'), ('Message Timestamp', 'datetime'), 'Account ID', 'Conversation',
        'Conversation ID', 'Reactor ID', 'Reactor Name', 'Reaction (as stored)', 'Count',
        'Message', 'Message Found', 'Client Message ID', 'Global Message ID', 'Database')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zalo_contacts(context):
    data_list = []
    sources = []
    for _container_path, entry in _stores(context).items():
        main = entry['main']
        if not main:
            continue
        sources.append(main)
        names = _names(main)
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
    data_headers = (
        ('Stored Time', 'datetime'), 'Account ID', 'User ID', 'Display Name', 'Alias',
        'usr (as stored)', 'Phone (as stored)', 'Zalo Friend (as stored)',
        'ged (as stored)', 'Date of Birth (as stored)', 'Table')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def zalo_groups(context):
    data_list = []
    sources = []
    for _container_path, entry in _stores(context).items():
        main = entry['main']
        if not main or not does_table_exist_in_db(main, 'group_info_v6'):
            continue
        sources.append(main)
        names = _names(main)
        for account, group_id, name, creator, total, members, stamp in _rows(
                main, 'SELECT currentUserUid, id, name, creatorId, totalMem, member_uids, ts '
                      'FROM group_info_v6 ORDER BY currentUserUid, id'):
            account = str(account)
            data_list.append((
                account, group_id, name or '', creator, _person(names, account, creator),
                total if total is not None else '', members or '',
                stamp if stamp is not None else ''))
    if not data_list and sources:
        logfunc('Zalo - Groups: group_info_v6 holds no rows')
    data_headers = (
        'Account ID', 'Group ID', 'Group Name', 'Creator ID', 'Creator Name', 'Member Count',
        'Member IDs (as stored)', 'ts (as stored)')
    return data_headers, data_list, '\n'.join(sources)
