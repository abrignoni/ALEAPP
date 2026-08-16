__artifacts_v2__ = {
    "get_tikTok": {
        "name": "TikTok - Messages",
        "description": "Parses TikTok direct messages (timestamp, user, nickname, message, "
                       "links, read state and conversation) from the TikTok IM databases, "
                       "covering the per-account _im.db files found.",
        "author": "@abrignoni",
        "creation_date": "2021-03-02",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "TikTok",
        "notes": "One _im.db exists per logged-in account, named <account uid>_im.db, and "
                 "all of them are parsed; the Account ID column carries each file's uid and "
                 "messages whose sender equals it are marked Outgoing.\n"
                 "Every msg row is reported. The Message, link and sticker columns are "
                 "filled only when the row's content field holds JSON; rows whose content "
                 "is not JSON report the SQL columns alone, with Message Type and Deleted "
                 "as stored since no source for those integers was verified.\n"
                 "Sender names are resolved against SIMPLE_USER in db_im_xx and "
                 "IM_USER_BASE_INFO in the db_im_contact databases, where present. A sender "
                 "in neither store shows a bare UID.",
        "paths": ('*_im.db*', '*db_im_xx*', '*db_im_contact*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 31 rows",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 88 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 11 rows",
            "russell_a14": "Android 14 | 20 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 6 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 4 rows",
            "pixel3_a12": "Android 12 | 36 rows",
            "pixel3_a11": "Android 11 | 28 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 0 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 0 rows",
            "samsunga53_a14": "Android 14 | com.bd.nproject vc 100203 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Nickname"
            }
        },
    },
    "get_tikTok_contacts": {
        "name": "TikTok - Contacts",
        "description": "Parses TikTok contacts (UID, nickname, unique ID, avatar and follow "
                       "status) from the TikTok IM databases.",
        "author": "@abrignoni",
        "creation_date": "2021-03-02",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Contacts come from IM_USER_BASE_INFO in the db_im_contact databases and "
                 "from SIMPLE_USER in db_im_xx. A UID present in more than one store is "
                 "reported once, from the first store that carries it, with "
                 "IM_USER_BASE_INFO preferred since it also records an update timestamp. "
                 "Update Time, Blocked and Deleted are only available from "
                 "IM_USER_BASE_INFO; Blocked and Deleted are reported as stored since no "
                 "source for those integers was verified.",
        "paths": ('*db_im_xx*', '*db_im_contact*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 48 rows",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 188 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 2 rows",
            "russell_a14": "Android 14 | 13 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 8 rows",
            "sharon_a13": "Android 13 | 5 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 4 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 5 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 2 rows",
            "pixel3_a12": "Android 12 | 4 rows",
            "pixel3_a11": "Android 11 | 4 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 1 row",
            "samsunga53_a14": "Android 14 | com.bd.nproject vc 100203 | 0 rows",
        },
    }
}

import datetime
import json
import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_ACCOUNT_DB_RE = re.compile(r'(\d+)_im\.db$')


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _rows(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _account_dbs(files_found):
    '''Every per-account <uid>_im.db, as [(account uid, path)].'''
    account_dbs = []
    for file_found in files_found:
        file_found = str(file_found)
        match = _ACCOUNT_DB_RE.search(os.path.basename(file_found))
        if match and file_found.endswith('_im.db'):
            account_dbs.append((match.group(1), file_found))
    return sorted(account_dbs, key=lambda item: item[1])


def _contact_sources(files_found):
    '''Contact stores as [(table, path)], IM_USER_BASE_INFO stores first.'''
    contact_dbs = []
    simple_dbs = []
    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name == 'db_im_xx':
            simple_dbs.append(('SIMPLE_USER', file_found))
        elif name == 'db_im_contact' or (name.startswith('db_im_contact-')
                                         and not name.endswith(('-wal', '-shm', '-journal'))):
            contact_dbs.append(('IM_USER_BASE_INFO', file_found))
    return sorted(contact_dbs, key=lambda item: item[1]) + sorted(
        simple_dbs, key=lambda item: item[1])


def _json_field(content, *path):
    try:
        node = json.loads(content)
    except (ValueError, TypeError):
        return None
    for key in path:
        if isinstance(key, int):
            node = node[key] if isinstance(node, list) and len(node) > key else None
        else:
            node = node.get(key) if isinstance(node, dict) else None
    return node if isinstance(node, (str, int, float)) else None


def _name_map(files_found):
    '''UID to (unique id, nickname) from every contact store found.'''
    names = {}
    for table, path in _contact_sources(files_found):
        for uid, unique_id, nickname in _rows(
                path, f'SELECT UID, UNIQUE_ID, NICK_NAME FROM {table}'):
            if uid is not None and uid not in names:
                names[uid] = (unique_id or '', nickname or '')
    return names


@artifact_processor
def get_tikTok(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    names = _name_map(files_found)

    for account_uid, maindb in _account_dbs(files_found):
        source_path = source_path or maindb
        source_file = context.get_relative_path(maindb)
        for (created, sender, content, message_type, deleted, read_status,
             conversation_id) in _rows(maindb, '''
                SELECT created_time, sender, content, type, deleted, read_status,
                       conversation_id
                FROM msg ORDER BY created_time'''):
            unique_id, nickname = names.get(sender, ('', ''))
            if read_status == 0:
                local_info = 'Not read'
            elif read_status == 1:
                local_info = 'Read'
            else:
                local_info = read_status
            if sender is not None and account_uid:
                direction = 'Outgoing' if str(sender) == account_uid else 'Incoming'
            else:
                direction = ''
            data_list.append((
                _ms_to_utc(created), sender, unique_id, nickname,
                _json_field(content, 'text'),
                _json_field(content, 'display_name'),
                _json_field(content, 'url', 'url_list', 0),
                message_type, deleted, read_status, local_info,
                conversation_id, account_uid, direction, source_file))

    data_headers = (('Timestamp', 'datetime'), 'UID', 'Unique ID', 'Nickname', 'Message',
                    'Link GIF Name', 'Link GIF URL', 'Message Type (as stored)',
                    'Deleted (as stored)', 'Read?', 'Local Info', 'Conversation ID',
                    'Account ID', 'Direction', 'Source File')
    return data_headers, data_list, source_path or 'see Source File column'


@artifact_processor
def get_tikTok_contacts(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    seen = set()

    for table, path in _contact_sources(files_found):
        source_path = source_path or path
        source_file = context.get_relative_path(path)
        if table == 'IM_USER_BASE_INFO':
            sql = '''SELECT UID, NICK_NAME, UNIQUE_ID, INITIAL_LETTER, AVATAR_THUMB,
                            FOLLOW_STATUS, UPDATE_TIME, BLOCK, DELETED
                     FROM IM_USER_BASE_INFO'''
        else:
            sql = '''SELECT UID, NICK_NAME, UNIQUE_ID, INITIAL_LETTER, AVATAR_THUMB,
                            FOLLOW_STATUS, NULL, NULL, NULL
                     FROM SIMPLE_USER'''
        for (uid, nickname, unique_id, initial_letter, avatar, follow_status,
             update_time, blocked, deleted) in _rows(path, sql):
            if uid in seen:
                continue
            seen.add(uid)
            data_list.append((
                _ms_to_utc(update_time), uid, nickname, unique_id, initial_letter,
                _json_field(avatar, 'url_list', 0),
                follow_status, blocked, deleted, source_file))

    data_headers = (('Update Time', 'datetime'), 'UID', 'Nickname', 'Unique ID',
                    'Initial Letter', 'Avatar URL', 'Follow Status', 'Blocked (as stored)',
                    'Deleted (as stored)', 'Source File')
    return data_headers, data_list, source_path or 'see Source File column'
