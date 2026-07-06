# pylint: disable=W0613
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
    },
    "get_fb_msys_chats": {
        "name": "Facebook Messenger - Chats (msys_database)",
        "description": "Facebook/Messenger chat messages (msys_database)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/msys_database*',),
        "output_types": "standard",
        "artifact_icon": "message",
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
        "notes": "",
        "paths": ('*/msys_database*',),
        "output_types": "standard",
        "artifact_icon": "phone",
    },
    "get_fb_msys_contacts": {
        "name": "Facebook Messenger - Contacts (msys_database)",
        "description": "Facebook/Messenger contacts (msys_database)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/msys_database*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_fb_threads_chats": {
        "name": "Facebook Messenger - Chats (threads_db2)",
        "description": "Facebook/Messenger chat messages (threads_db2)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/*threads_db2',),
        "output_types": "standard",
        "artifact_icon": "message",
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
    },
    "get_fb_threads_contacts": {
        "name": "Facebook Messenger - Contacts (threads_db2)",
        "description": "Facebook/Messenger contacts (threads_db2)",
        "author": "Kevin Pagano",
        "creation_date": "2021-03-03",
        "last_update_date": "2021-03-03",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ('*/*threads_db2',),
        "output_types": "standard",
        "artifact_icon": "users",
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


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


@artifact_processor
def get_fb_user_id(files_found, report_folder, seeker, wrap_text):
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
def get_fb_msys_chats(files_found, report_folder, seeker, wrap_text):
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
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              row[7], row[8], row[9], row[10], row[11], _str_to_utc(row[12]), row[13],
                              row[14], rel, direction))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), 'Sender', 'Sender ID', 'Thread Key', 'Message',
                    'Snippet', 'Call/Location Information', 'Attachment Name', 'Attachment Type',
                    'Attachment URL', 'Location Lat/Long', 'Reaction',
                    ('Reaction Timestamp', 'datetime'), 'Is Admin Message', 'Message ID',
                    'Source File', 'Direction')
    return data_headers, data_list, source


@artifact_processor
def get_fb_msys_calls(files_found, report_folder, seeker, wrap_text):
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
    return data_headers, data_list, source


@artifact_processor
def get_fb_msys_contacts(files_found, report_folder, seeker, wrap_text):
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
    return data_headers, data_list, source


@artifact_processor
def get_fb_threads_chats(files_found, report_folder, seeker, wrap_text):
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
            datetime(message_reactions.reaction_timestamp/1000,'unixepoch'),
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
            datetime(message_reactions.reaction_timestamp/1000,'unixepoch'),
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
        try:
            cursor.execute(primary)
            rows, has_snippet = cursor.fetchall(), True
        except sqlite3.Error:
            rows, has_snippet = _q(cursor, fallback), False
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
def get_fb_threads_calls(files_found, report_folder, seeker, wrap_text):
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
def get_fb_threads_contacts(files_found, report_folder, seeker, wrap_text):
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
            substr(user_key,10), first_name, last_name, username,
            json_extract(profile_pic_square, '$[0].url'),
            CASE is_messenger_user WHEN 0 THEN '' ELSE 'Yes' END,
            CASE is_friend WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
            friendship_status, contact_relationship_status
        FROM thread_users
        ''')
        for row in rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                              rel))
        db.close()

    data_headers = ('User ID', 'First Name', 'Last Name', 'Username', 'Profile Pic URL',
                    'Is Messenger User', 'Is Friend', 'Friendship Status',
                    'Contact Relationship Status', 'Source File')
    return data_headers, data_list, source
