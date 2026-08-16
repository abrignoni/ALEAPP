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
            "russell_a14": "Android 14 | 20 rows",
            "pixel3_a11": "Android 11 | 14 rows",
            "pixel3_a12": "Android 12 | 12 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 11 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 6 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 4 rows",
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
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 188 rows",
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 48 rows",
            "russell_a14": "Android 14 | 13 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 8 rows",
            "sharon_a13": "Android 13 | 5 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 5 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 4 rows",
            "pixel3_a12": "Android 12 | 4 rows",
            "pixel3_a11": "Android 11 | 4 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 2 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 2 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 1 row",
            "samsunga53_a14": "Android 14 | com.bd.nproject vc 100203 | 0 rows",
        },
    },
    "get_tikTok_app_open": {
        "name": "TikTok - App Open Records",
        "description": "Rows from the app_open table in TIKTOK.db, one timestamp per row, "
                       "reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Hu and Karabiyik describe TIKTOK.db as keeping track of the timestamps "
                 "for each instance the app is opened. On the tested image every open_time "
                 "value fell exactly on a local midnight, so that build appears to record "
                 "at day rather than moment granularity; the value is reported as stored. "
                 "Reference: Xiao Hu and Umit Karabiyik, 'Shopping while Watching: An "
                 "Updated Forensic Analysis of TikTok on Android and iOS', ISNCC 2024, "
                 "https://doi.org/10.1109/ISNCC62547.2024.10759027",
        "paths": ('*/com.zhiliaoapp.musically/databases/TIKTOK.db*',),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 145 rows",
            "russell_a14": "Android 14 | 68 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 24 rows",
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 14 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 5 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 4 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 3 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 3 rows",
            "pixel3_a12": "Android 12 | 3 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 1 row",
        },
    },
    "get_tikTok_downloads": {
        "name": "TikTok - Downloads",
        "description": "Rows from the downloader table in downloader.db: URL, save path, "
                       "name, sizes, status and timestamps as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "TikTok",
        "notes": "On the tested image the rows were the app's own resource downloads "
                 "(models, assets, images), not user-saved videos; what a given row "
                 "represents is read from its URL and save path, not asserted here. "
                 "Status and the md5 column are reported as stored. Older builds lack the "
                 "download timestamp columns (observed on an Android 11 era image); absent "
                 "columns report as blank rather than dropping the rows. "
                 "Reference: Xiao Hu and Umit Karabiyik, 'Shopping while Watching: An "
                 "Updated Forensic Analysis of TikTok on Android and iOS', ISNCC 2024, "
                 "https://doi.org/10.1109/ISNCC62547.2024.10759027",
        "paths": ('*/com.zhiliaoapp.musically/databases/downloader.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 518 rows",
            "russell_a14": "Android 14 | 411 rows",
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 187 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 102 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 94 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 78 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 77 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 75 rows",
            "sharon_a13": "Android 13 | 60 rows",
            "pixel3_a12": "Android 12 | 49 rows",
            "pixel3_a11": "Android 11 | 48 rows (schema lacks the timestamp columns)",
            "samsunga53_a14": "Android 14 | com.bd.nproject vc 100203 | 12 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 5 rows",
        },
    },
    "get_tikTok_app_log_events": {
        "name": "TikTok - App Log Events",
        "description": "Rows from the event and session tables in ss_app_log.db: event "
                       "tag, JSON payload, session and user ids with millisecond "
                       "timestamps, reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Event rows carry the app's own tag strings and an ext_json payload "
                 "reported as stored; what an individual event means is not established "
                 "here. Session rows carry a session UUID, app version and duration. The "
                 "user_id column joins events to the logged-in account uid. "
                 "Reference: Xiao Hu and Umit Karabiyik, 'Shopping while Watching: An "
                 "Updated Forensic Analysis of TikTok on Android and iOS', ISNCC 2024, "
                 "https://doi.org/10.1109/ISNCC62547.2024.10759027",
        "paths": ('*/com.zhiliaoapp.musically/databases/ss_app_log.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 107 rows",
            "pixel3_a11": "Android 11 | 24 rows",
            "russell_a14": "Android 14 | 15 rows",
            "sharon_a13": "Android 13 | 7 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 6 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 2 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 1 row",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 1 row",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 0 rows",
        },
    },
    "get_tikTok_account": {
        "name": "TikTok - Account",
        "description": "Account values from the aweme_user.xml preference file, reported "
                       "as stored under the app's own key names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "TikTok",
        "notes": "aweme_user.xml keeps one entry per key; several entries hold JSON "
                 "documents whose names carry the account uid as a prefix "
                 "(<uid>_account_user_info, <uid>_aweme_user_info, "
                 "<uid>_significant_user_info) alongside user_info_raw. String, number "
                 "and boolean fields of those documents are reported one per row, empty "
                 "values skipped, nested objects not descended beyond the top level and "
                 "the data sub-document. Plain entries (current_foreground_uid, "
                 "logged_in_uid_list, mandatory_2sv) are reported as rows too. On the "
                 "tested image the documents carried the account uid, sec_uid, name, "
                 "avatar URLs, country code and registration values.",
        "paths": ('*/com.zhiliaoapp.musically/shared_prefs/aweme_user.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 225 rows",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 224 rows",
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 223 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 214 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 209 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 209 rows",
            "russell_a14": "Android 14 | 208 rows",
            "sharon_a13": "Android 13 | 195 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 191 rows",
            "pixel3_a12": "Android 12 | 167 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 157 rows",
            "pixel3_a11": "Android 11 | 148 rows",
        },
    }
}

import datetime
import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET

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


def _unique_files(context, suffix=None):
    '''The context's files matching suffix, without the duplicate paths extractions carry
    for the same file (data_mirror, and /data/data next to /data/user/0), preserving order.

    The dedupe key is the evidence-relative path, not the extracted path: the report's own
    data folder ends in /data, so a raw-path regex can rewrite the harness boundary instead
    of the evidence path on archives whose members start with data/.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if suffix is not None and not file_found.endswith(suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


def _account_dbs(context):
    '''Every per-account <uid>_im.db, as [(account uid, path)].'''
    account_dbs = []
    for file_found in _unique_files(context, suffix='_im.db'):
        match = _ACCOUNT_DB_RE.search(os.path.basename(file_found))
        if match:
            account_dbs.append((match.group(1), file_found))
    return sorted(account_dbs, key=lambda item: item[1])


def _contact_sources(context):
    '''Contact stores as [(table, path)], IM_USER_BASE_INFO stores first.'''
    contact_dbs = []
    simple_dbs = []
    for file_found in _unique_files(context):
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


def _name_map(context):
    '''UID to (unique id, nickname) from every contact store found.'''
    names = {}
    for table, path in _contact_sources(context):
        for uid, unique_id, nickname in _rows(
                path, f'SELECT UID, UNIQUE_ID, NICK_NAME FROM {table}'):
            if uid is not None and uid not in names:
                names[uid] = (unique_id or '', nickname or '')
    return names


@artifact_processor
def get_tikTok(context):
    data_list = []
    source_path = ''
    names = _name_map(context)

    for account_uid, maindb in _account_dbs(context):
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
    data_list = []
    source_path = ''
    seen = set()

    for table, path in _contact_sources(context):
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


def _account_json_rows(entry_name, text, source_file):
    try:
        document = json.loads(text)
    except (ValueError, TypeError):
        return [(entry_name, '', text, source_file)]
    if not isinstance(document, dict):
        return [(entry_name, '', text, source_file)]
    if isinstance(document.get('data'), dict):
        document = document['data']
    rows = []
    for key in sorted(document):
        value = document[key]
        if isinstance(value, (str, int, float, bool)) and value != '':
            rows.append((entry_name, key, str(value), source_file))
    return rows


@artifact_processor
def get_tikTok_account(context):
    data_list = []
    source_path = ''

    for file_found in _unique_files(context, suffix='aweme_user.xml'):
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        try:
            root = ET.parse(file_found).getroot()
        except (ET.ParseError, OSError, ValueError):
            continue
        for node in root:
            name = node.attrib.get('name', '')
            value = node.attrib.get('value', node.text)
            if value is None or value == '':
                continue
            value = str(value)
            if value.lstrip().startswith('{'):
                data_list.extend(_account_json_rows(name, value, source_file))
            else:
                data_list.append((name, '', value, source_file))

    data_headers = ('Entry', 'Key', 'Value', 'Source File')
    return data_headers, data_list, source_path


def _tolerant_select(source_path, table, columns, tail=''):
    """A SELECT naming every requested column, substituting NULL AS <name> for columns the
    file's schema generation does not have, so one absent column does not silently drop
    every row. Older TikTok builds carry strict subsets; nothing observed was renamed."""
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return ''
    try:
        present = {row[1] for row in db.execute(f'PRAGMA table_info({table})')}
    except sqlite3.Error:
        present = set()
    db.close()
    if not present:
        return ''
    select_list = ', '.join(
        column if column in present else f'NULL AS {column}' for column in columns)
    return f'SELECT {select_list} FROM {table} {tail}'


@artifact_processor
def get_tikTok_app_open(context):
    data_list = []
    source_path = ''
    for file_found in _unique_files(context, suffix='TIKTOK.db'):
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        for (open_time,) in _rows(file_found,
                                  'SELECT open_time FROM app_open ORDER BY open_time'):
            data_list.append((_ms_to_utc(open_time), open_time, source_file))
    data_headers = (('Open Time', 'datetime'), 'open_time (as stored)', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_tikTok_downloads(context):
    data_list = []
    source_path = ''
    for file_found in _unique_files(context, suffix='downloader.db'):
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        sql = _tolerant_select(
            file_found, 'downloader',
            ('downloadStartTimeStamp', 'downloadFinishTimeStamp', 'url', 'savePath',
             'name', 'mimeType', 'status', 'curBytes', 'totalBytes', 'md5'),
            'ORDER BY downloadStartTimeStamp')
        for (start, finish, url, save_path, name, mime, status, cur_bytes,
             total_bytes, md5) in (_rows(file_found, sql) if sql else []):
            data_list.append((
                _ms_to_utc(start), _ms_to_utc(finish), url, save_path, name, mime,
                status, cur_bytes, total_bytes, md5, source_file))
    data_headers = (('Download Start', 'datetime'), ('Download Finish', 'datetime'),
                    'URL', 'Save Path', 'Name', 'MIME Type', 'Status (as stored)',
                    'Current Bytes', 'Total Bytes', 'MD5 (as stored)', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_tikTok_app_log_events(context):
    data_list = []
    source_path = ''
    for file_found in _unique_files(context, suffix='ss_app_log.db'):
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        for (timestamp, category, tag, label, ext_json, session_id,
             user_id) in _rows(file_found, """
                SELECT timestamp, category, tag, label, ext_json, session_id, user_id
                FROM event ORDER BY timestamp"""):
            data_list.append((
                _ms_to_utc(timestamp), 'event', category, tag, label, ext_json,
                session_id, user_id, '', '', source_file))
        for (timestamp, value, duration, app_version, session_row_id) in _rows(
                file_found, """
                SELECT timestamp, value, duration, app_version, _id
                FROM session ORDER BY timestamp"""):
            data_list.append((
                _ms_to_utc(timestamp), 'session', '', '', '', '', session_row_id, '',
                value, f'{app_version} (duration {duration})', source_file))
    data_headers = (('Timestamp', 'datetime'), 'Row Type', 'Category', 'Tag', 'Label',
                    'Payload (as stored)', 'Session ID', 'User ID', 'Session UUID',
                    'Session Info', 'Source File')
    return data_headers, data_list, source_path
