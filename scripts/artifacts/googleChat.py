# pylint: disable=W0718
__artifacts_v2__ = {
    "get_googleChat": {
        "name": "Google Chat - Messages",
        "description": "Rows of topic_messages in dynamite.db joined to Groups and users; a message whose group or creator is not in those tables is not reported. Messages and earlier message text another state in the write-ahead log holds and the current state does not are reported too. Direction is derived, not stored: Outgoing when the creator id equals the user id of the account e-mail named in the database path, Incoming otherwise, and blank when that account cannot be resolved.",
        "author": "Josh Hickman & Alexis Brignoni",
        "creation_date": "2021-02-05",
        "last_update_date": "2026-10-26",
        "requirements": "blackboxprotobuf",
        "category": "Google Chat",
        "notes": "Record Origin. Live rows come from a normal read of the query. A message is the unique index of topic_messages on (group_id, topic_id, id), not row_id: on hickman_a13 12 of 39 messages held a different row_id in different states. A Recovered row is a message another state in the database's write-ahead log holds and the current topic_messages table does not. An Earlier version row is a non-empty text_body another state held for a message whose current text_body differs, one row per distinct text. A row whose message and text the current state still holds is not reported again. The whole query is run in each state, so a Recovered or Earlier version row's sender and conversation come from the same state as its text. Recovery Method and Recovery Location are filled in only on those rows. Why a message is absent or its text changed is not established here. States are read by scripts/sqlite_wal.py: each readable earlier committed state of the log's current generation (state n is the database after the first n committed transactions, and state 0 the database file without its log; states the reader cannot rebuild exactly are skipped and counted in the run log), the previous generation's left-over frames where its checks pass, and frames after the last commit where SQLite's quick_check passes. Each row is reported as the newest committed state holding it stored it, else the previous generation's newest left-over commit, else the frames after the last commit. Recovery Location names the committed states the row was read in, with their first and last numbers, and the previous log generation with the first and last numbers of its left-over commits; for a row read only after the last commit it names the log's frames after the last commit. Recovery Method is WAL committed states, or WAL uncommitted frames for a row read only after the last commit. On pixel7a_a14 the reader read 4 of the previous generation's 17 left-over commits and no row came from them. No row on the tested images or in the unit test went through the previous-generation or uncommitted-frame wording of Recovery Method and Recovery Location. "
                 "On the tested images no Recovered or Earlier version row was returned, so Record "
                 "Origin held Live on every row and Recovery Method and Recovery Location were empty "
                 "on every row. The Recovered and Earlier version paths are exercised by a unit test "
                 "and by the same code in iLEAPP's Google Chat artifact, not by these images.",
        "paths": ('*/com.google.android.gm/databases/user_accounts/*/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/dynamite.db*',
                  '*/com.google.android.apps.dynamite/databases/user_accounts/*/dynamite.db*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.dynamite vc 5349480, com.google.android.gm vc 64361093 | 37 rows",
            "hickman_a13": "Android 13 | 39 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.dynamite vc 6281014, com.google.android.gm vc 65429598 | 18 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 0 rows",
        },
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
        "description": "Rows of the Groups table in dynamite.db with the creator's name from the users table. A group whose creator is not in users is not reported.",
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
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.dynamite vc 5349480, com.google.android.gm vc 64361093 | 2 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.dynamite vc 6281014, com.google.android.gm vc 65429598 | 1 row",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 0 rows",
        },
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
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.dynamite vc 5349480, com.google.android.gm vc 64361093 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.dynamite vc 6281014, com.google.android.gm vc 65429598 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 0 rows",
        },
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
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.dynamite vc 5349480, com.google.android.gm vc 64361093 | 12 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.dynamite vc 6281014, com.google.android.gm vc 65429598 | 2 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 0 rows",
        },
    }
}

import datetime
import os
import re
import sqlite3

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.context import Context
from scripts.artifacts.storagePathViews import unique_files
from scripts.sqlite_wal import (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED,
                                rows_not_in_current)


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
        values = decode_protobuf(blob)
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



# topic_messages is unique on (group_id, topic_id, id) (its IDXU_ index); row_id is not the
# message, because a rewritten row takes a new row_id. The message query ends with those three.
_KEY = slice(-3, None)
_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_ORIGIN_EARLIER = 'Earlier version'
_METHOD_WAL_STATES = 'WAL committed states'
_METHOD_WAL_UNCOMMITTED = 'WAL uncommitted frames'


def _recovery_location(name, spans):
    """(method, location) for a row read in the states spans names."""
    parts = []
    committed, earlier = spans['committed'], spans['earlier']
    if committed:
        first, last = committed
        if last == 0:
            parts.append(f'{name} without its log, state 0')
        elif first == 0:
            parts.append(f'{name} and {name}-wal, committed states 0 to {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if earlier:
        first, last = earlier
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    if not parts:
        return _METHOD_WAL_UNCOMMITTED, f'{name}-wal, frames after the last commit'
    return _METHOD_WAL_STATES, '; '.join(parts)


def _current_texts(db_file):
    """{(group_id, topic_id, id): text_body} for every row topic_messages holds now."""
    db = open_sqlite_db_readonly(db_file)
    try:
        return {tuple(row[:3]): row[3] for row in db.execute(
            'SELECT group_id, topic_id, id, text_body FROM topic_messages')}
    except sqlite3.Error:
        return {}
    finally:
        db.close()


def _rows_in_log(db_file, query, text_index, live_texts):
    """Rows of query that another state in the write-ahead log holds, read through
    scripts/sqlite_wal.py with each state's own joins: a message whose key the current state
    does not hold (Recovered), and a non-empty text of a message whose current text differs
    (Earlier version).

    live_texts maps each key topic_messages holds now to its current text, read from the table
    itself rather than the joined query, whose joins can drop a current row. Returns
    [(row, origin, method, location)], one per Recovered key and one per distinct earlier text,
    each as the newest state holding it stored it (a committed state before the previous log
    generation before the frames after the last commit).
    """
    try:
        _columns, found, wal = rows_not_in_current(str(db_file), query, include=_WAL_KINDS)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'Google Chat: write-ahead log not read: {ex}')
        return []
    if wal.log:
        logfunc(f'Google Chat: {wal.summary()}')
    entries = {}
    for item in found:
        key = tuple(item.values[_KEY])
        text = item.values[text_index]
        if key in live_texts:
            if not text or text == live_texts[key]:
                continue
            slot, origin = (key, text), _ORIGIN_EARLIER
        else:
            slot, origin = (key,), _ORIGIN_RECOVERED
        rank = ((2, item.last_state) if item.first_state is not None else
                (1, item.earlier_generation[1]) if item.earlier_generation else (0, 0))
        entry = entries.setdefault(slot, {'row': item.values, 'origin': origin, 'rank': rank,
                                          'committed': None, 'earlier': None})
        if rank > entry['rank']:
            entry['row'], entry['rank'] = item.values, rank
        for part, span in (('committed', (item.first_state, item.last_state)
                            if item.first_state is not None else None),
                           ('earlier', item.earlier_generation)):
            if span:
                old = entry[part]
                entry[part] = span if old is None else (min(old[0], span[0]), max(old[1], span[1]))
    name = os.path.basename(str(db_file))
    return [(entry['row'], entry['origin'], *_recovery_location(name, entry))
            for entry in entries.values()]


@artifact_processor
def get_googleChat(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        query = '''
            SELECT topic_messages.create_time, Groups.name, users.name, topic_messages.text_body,
                   topic_messages.annotation, topic_messages.group_id, topic_messages.creator_id,
                   topic_messages.group_id, topic_messages.topic_id, topic_messages.id
            FROM topic_messages
            JOIN Groups on Groups.group_id=topic_messages.group_id
            JOIN users ON users.user_id=topic_messages.creator_id
            ORDER BY topic_messages.create_time ASC
        '''
        live = _run(source_path, query)
        rows = [(row, _ORIGIN_LIVE, '', '') for row in live]
        rows.extend(_rows_in_log(source_path, query, 3, _current_texts(source_path)))
        # the account email is in the db path (user_accounts/<email>/dynamite.db);
        # resolve it to the gaia id via the users table of the same db
        owner_id = ''
        email_match = re.search(r'user_accounts/([^/]+)/dynamite\.db', source_path.replace('\\', '/'))
        if email_match:
            email_sql = email_match.group(1).replace("'", "''")
            owner_rows = _run(source_path, f"SELECT user_id FROM users WHERE email = '{email_sql}'")
            if owner_rows:
                owner_id = str(owner_rows[0][0])
        for r, origin, method, location in rows:
            ann = _parse_annotation(r[4])
            if owner_id and r[6] is not None:
                direction = 'Outgoing' if str(r[6]) == owner_id else 'Incoming'
            else:
                direction = ''
            data_list.append((_us_to_utc(r[0]), direction, r[2], r[1], r[3], origin) + ann
                             + (Context.get_relative_path(source_path), r[5], method, location))

    data_headers = (('Message Timestamp', 'datetime'), 'Direction', 'Sender', 'Group Name', 'Message',
                    'Record Origin', 'Meeting Code', 'Meeting URL', 'Meeting Sender',
                    'Meeting Sender Profile Pic URL', 'Filename', 'File Type', 'Width', 'Height',
                    'Source File', 'Group ID', 'Recovery Method', 'Recovery Location')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleChat_groups(context):
    files_found = unique_files(context)
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
            data_list.append((_us_to_utc(r[0]), r[1], r[2], _us_to_utc(r[3]), Context.get_relative_path(source_path)))

    data_headers = (('Group Created Time', 'datetime'), 'Group Name', 'Group Creator',
                    ('Group Last Viewed', 'datetime'), 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleChat_drafts(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        rows = _run(source_path, '''
            SELECT drafts.group_id, drafts.topic_id, drafts.text, Groups.name, drafts.group_type
            FROM drafts
            LEFT JOIN Groups on drafts.group_id = Groups.group_id
        ''')
        for r in rows:
            data_list.append((r[0], r[1], r[2], r[3], r[4], Context.get_relative_path(source_path)))

    data_headers = ('Group ID', 'Topic ID', 'Message', 'Group Name', 'Group Type', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleChat_users(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for source_path in _dbs(files_found):
        rows = _run(source_path, '''
            SELECT last_updated_time_micros, user_id, name, email, avatar_url, dasher_customer_id
            FROM users
        ''')
        for r in rows:
            data_list.append((_us_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], Context.get_relative_path(source_path)))

    data_headers = (('Last Updated Time', 'datetime'), 'User ID', 'Name', 'Email', 'Avatar URL',
                    'Dasher Customer ID', 'Source File')
    return data_headers, data_list, source_path
