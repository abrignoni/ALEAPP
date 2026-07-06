# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_googleChat": {
        "name": "Google Chat - Messages",
        "description": "Google Chat messages (dynamite.db)",
        "author": "Josh Hickman & Alexis Brignoni",
        "creation_date": "2021-02-05",
        "last_update_date": "2026-07-03",
        "requirements": "blackboxprotobuf",
        "category": "Google Chat",
        "notes": "",
        "paths": ('*/com.google.android.gm/databases/user_accounts/*/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/user_accounts/*/dynamite.db*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Group ID",
                "conversationLabelColumn": "Group Name",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sender"
            }
        },
    },
    "get_googleChat_groups": {
        "name": "Google Chat - Groups",
        "description": "Google Chat group information (dynamite.db)",
        "author": "Josh Hickman & Alexis Brignoni",
        "creation_date": "2021-02-05",
        "last_update_date": "2021-02-05",
        "requirements": "none",
        "category": "Google Chat",
        "notes": "",
        "paths": ('*/com.google.android.gm/databases/user_accounts/*/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/user_accounts/*/dynamite.db*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_googleChat_drafts": {
        "name": "Google Chat - Drafts",
        "description": "Google Chat draft messages (dynamite.db)",
        "author": "Josh Hickman & Alexis Brignoni",
        "creation_date": "2021-02-05",
        "last_update_date": "2021-02-05",
        "requirements": "none",
        "category": "Google Chat",
        "notes": "",
        "paths": ('*/com.google.android.gm/databases/user_accounts/*/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/user_accounts/*/dynamite.db*'),
        "output_types": "standard",
        "artifact_icon": "edit",
    },
    "get_googleChat_users": {
        "name": "Google Chat - Users",
        "description": "Google Chat users (dynamite.db)",
        "author": "Josh Hickman & Alexis Brignoni",
        "creation_date": "2021-02-05",
        "last_update_date": "2021-02-05",
        "requirements": "none",
        "category": "Google Chat",
        "notes": "",
        "paths": ('*/com.google.android.gm/databases/user_accounts/*/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/user_accounts/*/dynamite.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
    }
}

import datetime
import os
import re
import sqlite3

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _us_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _d(value):
    return value.decode('utf-8', 'replace') if isinstance(value, bytes) else value


def _dbs(files_found):
    return [str(f) for f in files_found if os.path.basename(str(f)) == 'dynamite.db']


def _run(source_path, sql):
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _parse_annotation(blob):
    '''Returns (meeting_code, meeting_url, meeting_sender, meeting_pic, filename, filetype, width, height).'''
    blank = ('',) * 8
    if not blob:
        return blank
    try:
        values = blackboxprotobuf.decode_message(blob)
    except Exception:
        return blank
    try:  # image attachment
        v = values[0]['1']['10']
        return ('', '', '', '', _d(v.get('3')), _d(v.get('4')), v['5']['1'], v['5']['2'])
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    try:  # meeting (plain)
        v = values[0]['1']['12']['1']
        return (_d(v['3']), _d(v['2']), '', '', '', '', '', '')
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    try:  # meeting with sender name
        v = values[0]['1'][0]['12']['1']
        return (_d(v['3']), _d(v['6']['16']['1']), _d(v['6']['16']['2']), '', '', '', '', '')
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    try:  # meeting (sender variant)
        v = values[0]['1'][0]['12']['1']
        return (_d(v['3']), _d(v['2']), '', '', '', '', '', '')
    except (KeyError, TypeError, AttributeError, IndexError):
        pass
    return blank


@artifact_processor
def get_googleChat(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        rows = _run(source_path, '''
            SELECT topic_messages.create_time, Groups.name, users.name, topic_messages.text_body,
                   topic_messages.annotation, topic_messages.group_id, topic_messages.creator_id
            FROM topic_messages
            JOIN Groups on Groups.group_id=topic_messages.group_id
            JOIN users ON users.user_id=topic_messages.creator_id
            ORDER BY topic_messages.create_time ASC
        ''')
        # the account email is in the db path (user_accounts/<email>/dynamite.db);
        # resolve it to the gaia id via the users table of the same db
        owner_id = ''
        email_match = re.search(r'user_accounts/([^/]+)/dynamite\.db', source_path.replace('\\', '/'))
        if email_match:
            email_sql = email_match.group(1).replace("'", "''")
            owner_rows = _run(source_path, f"SELECT user_id FROM users WHERE email = '{email_sql}'")
            if owner_rows:
                owner_id = str(owner_rows[0][0])
        for r in rows:
            ann = _parse_annotation(r[4])
            if owner_id and r[6] is not None:
                direction = 'Outgoing' if str(r[6]) == owner_id else 'Incoming'
            else:
                direction = ''
            data_list.append((_us_to_utc(r[0]), r[1], r[2], r[3]) + ann + (source_path, r[5], direction))

    data_headers = (('Message Timestamp', 'datetime'), 'Group Name', 'Sender', 'Message',
                    'Meeting Code', 'Meeting URL', 'Meeting Sender', 'Meeting Sender Profile Pic URL',
                    'Filename', 'File Type', 'Width', 'Height', 'Source File', 'Group ID', 'Direction')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleChat_groups(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        rows = _run(source_path, '''
            SELECT Groups.create_time, Groups.name, users.name, Groups.last_view_time
            FROM Groups
            JOIN users ON users.user_id=Groups.creator_id
            ORDER BY Groups.create_time ASC
        ''')
        for r in rows:
            data_list.append((_us_to_utc(r[0]), r[1], r[2], _us_to_utc(r[3]), source_path))

    data_headers = (('Group Created Time', 'datetime'), 'Group Name', 'Group Creator',
                    ('Group Last Viewed', 'datetime'), 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleChat_drafts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        rows = _run(source_path, '''
            SELECT drafts.group_id, drafts.topic_id, drafts.text, Groups.name, drafts.group_type
            FROM drafts
            LEFT JOIN Groups on drafts.group_id = Groups.group_id
        ''')
        for r in rows:
            data_list.append((r[0], r[1], r[2], r[3], r[4], source_path))

    data_headers = ('Group ID', 'Topic ID', 'Message', 'Group Name', 'Group Type', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleChat_users(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        rows = _run(source_path, '''
            SELECT last_updated_time_micros, user_id, name, email, avatar_url, dasher_customer_id
            FROM users
        ''')
        for r in rows:
            data_list.append((_us_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], source_path))

    data_headers = (('Last Updated Time', 'datetime'), 'User ID', 'Name', 'Email', 'Avatar URL',
                    'Dasher Customer ID', 'Source File')
    return data_headers, data_list, source_path
