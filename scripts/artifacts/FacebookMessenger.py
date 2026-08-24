__artifacts_v2__ = {
    "get_fb_user_id": {
        "name": "Facebook Messenger - User ID",
        "description": "Facebook/Messenger logged-in user id (threads_db2-uid)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/*threads_db2-uid',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.orca vc 335215725 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.orca vc 343213368 | 1 row",
            "pixel7a_a14": "Android 14 | com.facebook.orca vc 323609457 | 1 row",
            "sharon_a14": "Android 14 | com.facebook.orca vc 324209509 | 1 row",
        },
    },
    "get_fb_msys_chats": {
        "name": "Facebook Messenger - Chats (msys_database)",
        "description": "Facebook/Messenger chat messages (msys_database)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Rows that are the same record found in more than one place are merged, and the Source File column lists every location a row was found in. The Facebook app and Messenger keep the same MSYS mailbox, so an extraction holding both carries a copy in each sandbox; the join in this query can also emit the same row more than once from a single copy. Merging is keyed on row content, not on package name, so a record present in only one sandbox is kept: on one tested image the two copies held 11 and 13 contacts and the merged result is 13. Signed CDN links are excluded from the key because each app fetches its own for the same item, which means two genuinely different items would merge if they matched on every other reported column.",
        "paths": ('*/msys_database*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.katana vc 465218038, com.facebook.orca vc 335215725 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.katana vc 472143277, com.facebook.orca vc 343213368 | 0 rows",
            "pixel7a_a14": "Android 14 | com.facebook.orca vc 323609457 | 26 rows",
            "samsungs20_a13": "Android 13 | com.facebook.katana vc 467618094, com.facebook.orca vc 337415659 | 0 rows",
            "sharon_a14": "Android 14 | com.facebook.katana vc 454415791, com.facebook.orca vc 324209509 | 14 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread Key",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sender"
            }
        },
    },
    "get_fb_msys_calls": {
        "name": "Facebook Messenger - Calls (msys_database)",
        "description": "Facebook/Messenger call log (msys_database)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Rows that are the same record found in more than one place are merged, and the Source File column lists every location a row was found in. The Facebook app and Messenger keep the same MSYS mailbox, so an extraction holding both carries a copy in each sandbox; the join in this query can also emit the same row more than once from a single copy. Merging is keyed on row content, not on package name, so a record present in only one sandbox is kept: on one tested image the two copies held 11 and 13 contacts and the merged result is 13. Signed CDN links are excluded from the key because each app fetches its own for the same item, which means two genuinely different items would merge if they matched on every other reported column.",
        "paths": ('*/msys_database*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.katana vc 465218038, com.facebook.orca vc 335215725 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.katana vc 472143277, com.facebook.orca vc 343213368 | 2 rows",
            "pixel7a_a14": "Android 14 | com.facebook.orca vc 323609457 | 8 rows",
            "samsungs20_a13": "Android 13 | com.facebook.katana vc 467618094, com.facebook.orca vc 337415659 | 0 rows",
            "sharon_a14": "Android 14 | com.facebook.katana vc 454415791, com.facebook.orca vc 324209509 | 0 rows",
        },
    },
    "get_fb_msys_contacts": {
        "name": "Facebook Messenger - Contacts (msys_database)",
        "description": "Facebook/Messenger contacts (msys_database)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "Rows that are the same record found in more than one place are merged, and the Source File column lists every location a row was found in. The Facebook app and Messenger keep the same MSYS mailbox, so an extraction holding both carries a copy in each sandbox; the join in this query can also emit the same row more than once from a single copy. Merging is keyed on row content, not on package name, so a record present in only one sandbox is kept: on one tested image the two copies held 11 and 13 contacts and the merged result is 13. Signed CDN links are excluded from the key because each app fetches its own for the same item, which means two genuinely different items would merge if they matched on every other reported column.",
        "paths": ('*/msys_database*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.katana vc 465218038, com.facebook.orca vc 335215725 | 22 rows",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.katana vc 472143277, com.facebook.orca vc 343213368 | 3 rows",
            "pixel7a_a14": "Android 14 | com.facebook.orca vc 323609457 | 2 rows",
            "samsungs20_a13": "Android 13 | com.facebook.katana vc 467618094, com.facebook.orca vc 337415659 | 1 row",
            "sharon_a14": "Android 14 | com.facebook.katana vc 454415791, com.facebook.orca vc 324209509 | 35 rows",
        },
    },
    "get_fb_threads_chats": {
        "name": "Facebook Messenger - Chats (threads_db2)",
        "description": "Facebook/Messenger chat messages (threads_db2)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/*threads_db2',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.katana vc 465218038 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.katana vc 472143277 | 0 rows",
            "samsungs20_a13": "Android 13 | com.facebook.katana vc 467618094 | 0 rows",
            "sharon_a14": "Android 14 | com.facebook.katana vc 454415791 | 0 rows",
        },
    },
    "get_fb_threads_calls": {
        "name": "Facebook Messenger - Calls (threads_db2)",
        "description": "Facebook/Messenger call log (threads_db2)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/*threads_db2',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.katana vc 465218038 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.katana vc 472143277 | 0 rows",
            "samsungs20_a13": "Android 13 | com.facebook.katana vc 467618094 | 0 rows",
            "sharon_a14": "Android 14 | com.facebook.katana vc 454415791 | 0 rows",
        },
    },
    "get_fb_threads_contacts": {
        "name": "Facebook Messenger - Contacts (threads_db2)",
        "description": "Facebook/Messenger contacts (threads_db2)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/*threads_db2',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.facebook.katana vc 465218038 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.facebook.katana vc 472143277 | 0 rows",
            "samsungs20_a13": "Android 13 | com.facebook.katana vc 467618094 | 0 rows",
            "sharon_a14": "Android 14 | com.facebook.katana vc 454415791 | 0 rows",
        },
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, null_absent_columns, open_sqlite_db_readonly


def _str_to_utc(value):
    """Parse a 'YYYY-MM-DD HH:MM:SS' UTC string (from SQL datetime()) into an aware datetime."""
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _candidate(file_found):
    # Skip mirror copies and the /user/0/ duplicate of /data/data/com.facebook.orca.
    return 'mirror' not in file_found and '/user/0/' not in file_found


def _src(file_found, seeker):
    try:
        return file_found.replace(seeker.data_folder, '')
    except AttributeError:
        return file_found


def _q(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


def _merge_by_source(data_list, volatile=()):
    '''Collapse rows that are the same record found in more than one app sandbox.

    The Facebook app and Messenger keep the same MSYS mailbox, and an extraction holding
    both carries a copy in each app's own sandbox
    (com.facebook.katana/app_mib_msys/v2/<uid>/ and com.facebook.orca/databases/). Without
    this the same message is reported once per copy.

    Rows are keyed on their content rather than filtered by package name, so a record
    present in only one of the sandboxes is kept. The Source File column, which is last,
    is excluded from the key and the paths of every copy are joined, so the row still
    records each location the record was found in.

    volatile holds the indexes of columns that legitimately differ between copies of the
    same record and so must not take part in the key. Each app requests its own signed
    CDN link for the same attachment or profile picture, and on the tested images those
    links were the only difference: across the two copies of an eleven contact store the
    profile picture URL differed on nine and every other column matched, and across eight
    shared messages the attachment URL differed on one. The first copy's value is kept.
    '''
    skip = set(volatile)
    merged = {}
    order = []
    for row in data_list:
        key = tuple(value for index, value in enumerate(row[:-1]) if index not in skip)
        if key not in merged:
            merged[key] = list(row)
            order.append(key)
            continue
        existing = str(merged[key][-1] or '')
        addition = str(row[-1] or '')
        if addition and addition not in existing.split('; '):
            merged[key][-1] = f'{existing}; {addition}' if existing else addition
    return [tuple(merged[key]) for key in order]


@artifact_processor
def get_fb_user_id(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or not file_found.endswith('threads_db2-uid'):
            continue
        source = source or file_found
        rel = _src(file_found, seeker)
        try:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as dat:
                for line in dat:
                    uid = line.strip()
                    if uid:
                        data_list.append((uid, rel))
        except OSError:
            continue

    data_headers = ('User ID', 'Source File')
    return data_headers, data_list, source


@artifact_processor
def get_fb_msys_chats(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or file_found.endswith(('-shm', '-wal')):
            continue
        if 'msys_database_' not in file_found:
            continue
        source = source or file_found
        # local account uid from the threads_db2-uid file (fetched via paths)
        fb_uid = ''
        for uid_file in files_found:
            if str(uid_file).endswith('threads_db2-uid'):
                try:
                    with open(str(uid_file), 'r', encoding='utf-8', errors='replace') as dat:
                        fb_uid = next((line.strip() for line in dat if line.strip()), '')
                except OSError:
                    fb_uid = ''
                break
        rel = _src(file_found, seeker)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            datetime(messages.timestamp_ms/1000,'unixepoch'),
            contacts.name,
            messages.sender_id,
            messages.thread_key,
            messages.text,
            attachments.title_text,
            attachments.subtitle_text,
            attachments.filename,
            attachments.playable_url_mime_type,
            attachments.playable_url,
            attachment_ctas.native_url,
            reactions.reaction,
            datetime(reactions.reaction_creation_timestamp_ms/1000,'unixepoch'),
            CASE
                WHEN messages.is_admin_message = 1 THEN "Yes"
                WHEN messages.is_admin_message = 0 THEN "No"
                ELSE messages.is_admin_message
            END,
            messages.message_id
        FROM messages
        JOIN contacts ON contacts.id = messages.sender_id
        LEFT JOIN attachments ON attachments.message_id = messages.message_id
        LEFT JOIN attachment_ctas ON messages.message_id = attachment_ctas.message_id
        LEFT JOIN reactions ON reactions.message_id = messages.message_id
        ORDER BY messages.timestamp_ms ASC
        ''')
        for row in rows:
            if fb_uid and row[2] is not None:
                direction = 'Outgoing' if str(row[2]) == fb_uid else 'Incoming'
            else:
                direction = ''
            data_list.append((
                _str_to_utc(row[0]),
                _str_to_utc(row[12]),
                direction,
                row[1],
                row[4],
                row[2],
                row[3],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                row[13],
                row[14],
                rel,
            ))
        db.close()

    data_headers = (
        ('Message Timestamp', 'datetime'),
        ('Reaction Timestamp', 'datetime'),
        'Direction',
        'Sender',
        'Message',
        'Sender ID',
        'Thread Key',
        'Snippet',
        'Call/Location Information',
        'Attachment Name',
        'Attachment Type',
        'Attachment URL',
        'Location Lat/Long',
        'Reaction',
        'Is Admin Message',
        'Message ID',
        'Source File',
    )
    # index 11 is Attachment URL, a per-app signed CDN link
    return data_headers, _merge_by_source(data_list, volatile=(11,)), source


@artifact_processor
def get_fb_msys_calls(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or file_found.endswith(('-shm', '-wal')):
            continue
        if 'msys_database_' not in file_found:
            continue
        source = source or file_found
        rel = _src(file_found, seeker)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            datetime(call_log.call_timestamp_ms/1000,'unixepoch'),
            strftime('%H:%M:%S',call_log.call_duration, 'unixepoch'),
            contacts.name,
            CASE call_log.call_direction WHEN 1 THEN "Outgoing" WHEN 2 THEN "Incoming" END,
            CASE call_log.call_media_type WHEN 2 THEN "Yes" ELSE "" END,
            CASE has_been_seen WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
            call_log.thread_key
        FROM call_log
        LEFT JOIN contacts ON contacts.id = call_log.thread_key
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              rel))
        db.close()

    data_headers = (('Call Timestamp', 'datetime'), 'Call Duration', 'Party Name', 'Call Direction',
                    'Video Call', 'Call Answered', 'Thread Key', 'Source File')
    return data_headers, _merge_by_source(data_list), source


@artifact_processor
def get_fb_msys_contacts(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or file_found.endswith(('-shm', '-wal')):
            continue
        if 'msys_database_' not in file_found:
            continue
        source = source or file_found
        rel = _src(file_found, seeker)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            id, name, normalized_name_for_search, username, profile_picture_large_url,
            email_address, phone_number,
            CASE is_messenger_user WHEN 0 THEN "" WHEN 1 THEN "Yes" END,
            CASE friendship_status
                WHEN 0 THEN "N/A (Self)" WHEN 1 THEN "Friends"
                WHEN 2 THEN "Friend Request Received" WHEN 3 THEN "Friend Request Sent"
                WHEN 4 THEN "Not Friends"
            END,
            substr(datetime(birthday_timestamp,'unixepoch'),6,5)
        FROM contacts
        ''')
        for row in rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                              row[9], rel))
        db.close()

    data_headers = ('Facebook ID', 'Name', 'Normalized Name', 'User Name', 'Profile Pic URL',
                    'Email Address', 'Phone Number', 'Is Messenger User', 'Friendship Status',
                    'Birthdate (MM-DD)', 'Source File')
    # index 4 is Profile Pic URL, a per-app signed CDN link
    return data_headers, _merge_by_source(data_list, volatile=(4,)), source


_REACTION_TS_COLUMNS = ('reaction_timestamp', 'reaction_timestamp_ms',
                        'reaction_creation_timestamp_ms', 'reaction_creation_time_ms')


def _reaction_ts_expr(cursor):
    """Pick the reaction-timestamp spelling this database carries.

    Four spellings have been reported across threads_db2 generations
    (community report, PR #638). Only reaction_timestamp is corpus-verified
    here; a database with none of the four reports the reaction with no time.
    """
    try:
        cols = {row[1] for row in cursor.execute('PRAGMA table_info(message_reactions)')}
    except sqlite3.Error:
        cols = set()
    for name in _REACTION_TS_COLUMNS:
        if name in cols:
            return f"datetime(message_reactions.{name}/1000,'unixepoch')"
    return 'NULL'


@artifact_processor
def get_fb_threads_chats(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    primary = '''
        SELECT
            CASE messages.timestamp_ms WHEN 0 THEN ''
                ELSE datetime(messages.timestamp_ms/1000,'unixepoch') END,
            json_extract(messages.sender, '$.name'),
            substr(json_extract(messages.sender, '$.user_key'),10),
            messages.thread_key,
            messages.text,
            messages.snippet,
            json_extract(messages.attachments, '$[0].filename'),
            json_extract(messages.shares, '$[0].name'),
            json_extract(messages.shares, '$[0].description'),
            json_extract(messages.shares, '$[0].href'),
            message_reactions.reaction,
            {reaction_ts},
            messages.msg_id
        FROM messages, threads
        LEFT JOIN message_reactions ON message_reactions.msg_id = messages.msg_id
        WHERE messages.thread_key=threads.thread_key
            AND generic_admin_message_extensible_data IS NULL AND msg_type != -1
        ORDER BY messages.thread_key, messages.timestamp_ms
        '''
    fallback = '''
        SELECT
            CASE messages.timestamp_ms WHEN 0 THEN ''
                ELSE datetime(messages.timestamp_ms/1000,'unixepoch') END,
            json_extract(messages.sender, '$.name'),
            substr(json_extract(messages.sender, '$.user_key'),10),
            messages.thread_key,
            messages.text,
            json_extract(messages.attachments, '$[0].filename'),
            json_extract(messages.shares, '$[0].name'),
            json_extract(messages.shares, '$[0].description'),
            json_extract(messages.shares, '$[0].href'),
            message_reactions.reaction,
            {reaction_ts},
            messages.msg_id
        FROM messages, threads
        LEFT JOIN message_reactions ON message_reactions.msg_id = messages.msg_id
        WHERE messages.thread_key=threads.thread_key
            AND generic_admin_message_extensible_data IS NULL AND msg_type != -1
        ORDER BY messages.thread_key, messages.timestamp_ms
        '''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or not file_found.endswith('threads_db2'):
            continue
        source = source or file_found
        rel = _src(file_found, seeker)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        reaction_ts = _reaction_ts_expr(cursor)
        try:
            cursor.execute(primary.format(reaction_ts=reaction_ts))
            rows, has_snippet = cursor.fetchall(), True
        except sqlite3.Error:
            rows, has_snippet = _q(cursor, fallback.format(reaction_ts=reaction_ts)), False
        for row in rows:
            if has_snippet:
                data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                                  row[7], row[8], row[9], row[10], _str_to_utc(row[11]), row[12], rel))
            else:
                data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], '', row[5],
                                  row[6], row[7], row[8], row[9], _str_to_utc(row[10]), row[11], rel))
        db.close()

    data_headers = (('Timestamp', 'datetime'), 'Sender Name', 'Sender ID', 'Thread Key', 'Message',
                    'Snippet', 'Attachment Name', 'Share Name', 'Share Description', 'Share Link',
                    'Message Reaction', ('Message Reaction Timestamp', 'datetime'), 'Message ID',
                    'Source File')
    return data_headers, data_list, source


@artifact_processor
def get_fb_threads_calls(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or not file_found.endswith('threads_db2'):
            continue
        source = source or file_found
        rel = _src(file_found, seeker)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            datetime((messages.timestamp_ms/1000)-(json_extract(messages.generic_admin_message_extensible_data, '$.call_duration')),'unixepoch'),
            strftime('%H:%M:%S',json_extract(messages.generic_admin_message_extensible_data, '$.call_duration'), 'unixepoch'),
            json_extract(messages.generic_admin_message_extensible_data, '$.caller_id'),
            json_extract(messages.sender, '$.name'),
            substr(json_extract(messages.sender, '$.user_key'),10),
            CASE json_extract(messages.generic_admin_message_extensible_data, '$.video')
                WHEN false THEN '' ELSE 'Yes' END,
            messages.thread_key
        FROM messages, threads
        WHERE messages.thread_key=threads.thread_key AND generic_admin_message_extensible_data NOT NULL
        ORDER BY messages.thread_key
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              rel))
        db.close()

    data_headers = (('Timestamp', 'datetime'), 'Call Duration', 'Caller ID', 'Receiver Name',
                    'Receiver ID', 'Video Call', 'Thread Key', 'Source File')
    return data_headers, data_list, source


@artifact_processor
def get_fb_threads_contacts(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _candidate(file_found) or not file_found.endswith('threads_db2'):
            continue
        source = source or file_found
        rel = _src(file_found, seeker)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        rows = _q(cursor, null_absent_columns(file_found, '''
        SELECT
            substr(user_key,10), first_name, last_name, username,
            json_extract(profile_pic_square, '$[0].url'),
            CASE is_messenger_user WHEN 0 THEN '' ELSE 'Yes' END,
            CASE is_friend WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
            friendship_status, contact_relationship_status
        FROM thread_users
        '''))
        for row in rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                              rel))
        db.close()

    data_headers = ('User ID', 'First Name', 'Last Name', 'Username', 'Profile Pic URL',
                    'Is Messenger User', 'Is Friend', 'Friendship Status',
                    'Contact Relationship Status', 'Source File')
    return data_headers, data_list, source
