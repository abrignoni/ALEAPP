__artifacts_v2__ = {
    "xiaohongshu_play_history": {
        "name": "Xiaohongshu (RED) - Play History",
        "description": "Entries in the Xiaohongshu play history store, with the note identifier, "
                       "the note title and description as stored, the note author's display name "
                       "and the recorded timestamp",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Xiaohongshu",
        "notes": "Read from the historyRecord table of the PlayHistoryRecordDB Room store in "
                 "com.xingin.xhs (Xiaohongshu, also published as RED and as Little Red Book).\n"
                 "Column meanings are taken from the column names the app declares. user_id is "
                 "the local account the row is filed under and is reported as Account User ID; "
                 "user_name is the note author's display name, which is a different party, so the "
                 "two are reported under distinct headers to keep them from being read as the "
                 "same person. author_id is populated on some rows and an empty string on others: "
                 "19 of the 45 rows in the tested corpus held an empty string. It is reported as "
                 "stored, so an empty cell there means the app recorded no author id for that "
                 "row rather than that the parser dropped it.\n"
                 "The timestamp is Unix epoch milliseconds. What the app records in this table is "
                 "an entry per note; the table is named a play history by the app, and this "
                 "artifact reports its rows without asserting how much of a note was played or "
                 "that the account holder saw any particular part of it.\n"
                 "Note Title and Note Description are stored by the app as the note's own text "
                 "and are reported as stored, in their original language, hashtags included. The "
                 "title was empty on some rows in the tested corpus while the description was "
                 "populated.\n"
                 "Scope: this is the readable SQLite store. The account profile, recent chats and "
                 "app launch times are read from the app's MMKV stores by the other artifacts in "
                 "this module. The message bodies are in the encrypted stores; see the module "
                 "notes.",
        "paths": ('*/com.xingin.xhs/databases/PlayHistoryRecordDB*',),
        "output_types": "standard",
        "artifact_icon": "play-circle",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Xiaohongshu | 45 rows",
            "sharon_a14": "Android 14 | Xiaohongshu | 0 rows (store not present)",
        },
    },
    "xiaohongshu_account": {
        "name": "Xiaohongshu (RED) - Account",
        "description": "The Xiaohongshu account signed in on the device, with the user id, RED "
                       "id, display name, registration time and the profile fields the app "
                       "cached, including follower and following counts",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Xiaohongshu",
        "notes": "Read from the app's own MMKV stores with the vendored mmkv_parser: the profile "
                 "JSON in the com.xingin.xhs store (key_desc_userinfo) and the login record in "
                 "login_user_info_kv (login_account_info_key). One row. Both globs are scoped to "
                 "the package. Register Time is the register_time field, a Unix seconds value. "
                 "Gender and Account Role are reported as stored. The count and location fields "
                 "are what the app cached and are blank where the app stored nothing. The "
                 "account's session id and token are in the same stores and are not reported. Birthday, "
                 "IP Location and Last Login Type are profile fields the app leaves empty until the "
                 "user sets them and were blank on the tested account.",
        "paths": ('*/com.xingin.xhs/files/mmkv/com.xingin.xhs',
                  '*/com.xingin.xhs/files/mmkv/login_user_info_kv'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Xiaohongshu | 1 row",
        },
    },
    "xiaohongshu_recent_chats": {
        "name": "Xiaohongshu (RED) - Recent Chats",
        "description": "The users the account recently had a direct chat with, as the app cached "
                       "them for its recent-shares list",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Xiaohongshu",
        "notes": "Read from the IMRecentChatsManager MMKV store. One row per recent chat entry. "
                 "Peer User ID and Nickname identify the other party as the app cached them; "
                 "Group Chat is true for a group. Source and Type are reported as stored. This "
                 "is a cached recent-shares list, not the message history, which is in the "
                 "encrypted msgDB and is not decoded here.",
        "paths": ('*/com.xingin.xhs/files/mmkv/IMRecentChatsManager*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Xiaohongshu | 2 rows",
        },
    },
    "xiaohongshu_app_launches": {
        "name": "Xiaohongshu (RED) - App Launches",
        "description": "Times the Xiaohongshu app recorded a successful launch",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Xiaohongshu",
        "notes": "Read from every write of the last_launch_success_time key in the "
                 "app_cold_start_record MMKV store. The store is append-only, so each launch is "
                 "a separate entry; one row per entry, in Unix milliseconds. The store holds a "
                 "recent window of launches rather than the full history.",
        "paths": ('*/com.xingin.xhs/files/mmkv/app_cold_start_record',),
        "output_types": "standard",
        "artifact_icon": "rotate-clock",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Xiaohongshu | 21 rows",
        },
    },
}

# What this module does not cover, and why.
#
# The account profile, recent chats and app launch times are read from the app's MMKV
# stores under files/mmkv. The message bodies and contact relations are not:
#
# Xiaohongshu keeps its messages in databases/msgDB and its contact relations in
# databases/localRelationDB. In both tested corpora those files carry no SQLite
# header and measure Shannon entropy of 8.00 (msgDB) and 7.95 (localRelationDB)
# over the sampled bytes, while their -wal sidecars carry the standard SQLite WAL
# magic. That combination is consistent with page-level encryption of the main
# database, such as SQLCipher. The app links Tencent WCDB, whose dex strings name
# SQLiteCipherSpec and setCipherSpec, so the cipher is WCDB rather than plain
# SQLCipher. A search of the app's shared_prefs found no key. They are therefore
# not parsed here, and no claim is made about their contents.
#
# The same applies to xhs_common_demotion_cache.db, which is the largest store in
# the package at about 11 MB.
#
# databases/cg.db and databases/dim.db are readable SQLite but hold base64 blobs
# under single-letter column names, which in the tested corpus decoded to SDK
# configuration rather than user data, so they are not reported.

import json
import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, does_table_exist_in_db,
                               get_file_path, get_sqlite_db_records, logfunc)
from scripts.mmkv_parser import MMKVError, decode_value, read_dict, read_entries


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _store_dict(path):
    try:
        return read_dict(path)
    except (MMKVError, OSError) as error:
        logfunc(f'Xiaohongshu: could not read {os.path.basename(path)}: {error}')
        return {}


def _json(value):
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode('utf-8')
        except UnicodeDecodeError:
            return None
    if not isinstance(value, str) or value[:1] not in '{[':
        return None
    try:
        return json.loads(value)
    except ValueError:
        return None


@artifact_processor
def xiaohongshu_play_history(context):
    source_path = get_file_path(context.get_files_found(), 'PlayHistoryRecordDB')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'historyRecord'):
        query = '''
        SELECT timestamp, note_title, note_desc, user_name, note_id, author_id, user_id
        FROM historyRecord
        ORDER BY timestamp
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                convert_unix_ts_to_utc(record[0]) if record[0] else '',
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Note Title',
        'Note Description',
        'Note Author Name',
        'Note ID',
        'Note Author ID (as stored)',
        'Account User ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def xiaohongshu_account(context):
    data_headers = (
        ('Register Time', 'datetime'),
        'User ID',
        'RED ID',
        'Nickname',
        'Gender (as stored)',
        'Birthday',
        'IP Location',
        'Location',
        'Bind Phone',
        'Geographic Zone',
        'Holder Country',
        'Account Role (as stored)',
        'Last Login Type',
        'Fans',
        'Follows',
        'Liked',
        'Collected',
        'Real Login',
        'Source File',
    )
    data_list = []
    source = ''
    profile = {}
    login = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        if base == 'com.xingin.xhs':
            profile = _json(_store_dict(file_found).get('key_desc_userinfo')) or {}
            source = source or file_found
        elif base == 'login_user_info_kv':
            login = _json(_store_dict(file_found).get('login_account_info_key')) or {}
            source = source or file_found
    if profile or login:
        register = profile.get('register_time')
        data_list.append((
            convert_unix_ts_to_utc(int(register)) if str(register).isdigit() else '',
            _text(profile.get('userid') or login.get('userId')),
            _text(profile.get('red_id')),
            _text(profile.get('nickname')),
            _text(profile.get('gender')),
            _text(profile.get('birthday')),
            _text(profile.get('ip_location')),
            _text(profile.get('location')),
            _text(profile.get('bind_phone')),
            _text(profile.get('account_geographic_zone') or login.get('geographicZone')),
            _text(profile.get('account_holder_country') or login.get('holderCountry')),
            _text(login.get('accountRole')),
            _text(profile.get('last_login_type')),
            _text(profile.get('fans')),
            _text(profile.get('follows')),
            _text(profile.get('liked')),
            _text(profile.get('collected')),
            _text(login.get('isRealLogin')),
            source,
        ))
    return data_headers, data_list, source


@artifact_processor
def xiaohongshu_recent_chats(context):
    data_headers = (
        'Peer User ID',
        'Nickname',
        'Group Chat',
        'Source (as stored)',
        'Type (as stored)',
        'Source File',
    )
    data_list = []
    source = ''
    for file_found in unique_files(context):
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if os.path.isdir(file_found) or file_found.endswith('.crc') or not base.startswith('IMRecentChatsManager'):
            continue
        rows = 0
        for key, value in _store_dict(file_found).items():
            if not key.startswith('IMRecentChatsManager_Default_Share_User_'):
                continue
            for entry in _json(value) or []:
                if not isinstance(entry, dict):
                    continue
                data_list.append((
                    _text(entry.get('user_id')),
                    _text(entry.get('nickname')),
                    _text(entry.get('is_group_chat')),
                    _text(entry.get('source')),
                    _text(entry.get('type')),
                    file_found,
                ))
                rows += 1
        if rows:
            source = file_found
    return data_headers, data_list, source


@artifact_processor
def xiaohongshu_app_launches(context):
    data_headers = (
        ('Launched At', 'datetime'),
        'Write Index',
        'Source File',
    )
    data_list = []
    source = ''
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or os.path.basename(file_found) != 'app_cold_start_record':
            continue
        try:
            entries = read_entries(file_found)
        except (MMKVError, OSError) as error:
            logfunc(f'Xiaohongshu: could not read {os.path.basename(file_found)}: {error}')
            continue
        rows = 0
        for index, (key, raw) in enumerate(entries):
            if key != 'last_launch_success_time':
                continue
            value = decode_value(raw)
            if isinstance(value, int):
                data_list.append((convert_unix_ts_to_utc(value), index, file_found))
                rows += 1
        if rows:
            source = file_found
    return data_headers, data_list, source
