# pylint: disable=W0613
__artifacts_v2__ = {
    "get_gboardCache": {
        "name": "Gboard - Clipboard",
        "description": "Gboard keyboard clipboard entries (gboard_clipboard.db)",
        "author": "@KevinPagano3 (https://startme.stark4n6.com)",
        "creation_date": "2021-01-09",
        "last_update_date": "2023-05-01",
        "requirements": "none",
        "category": "Gboard Keyboard",
        "notes": "",
        "paths": ('*/com.google.android.inputmethod.latin/databases/gboard_clipboard.db*',
                  '*/com.google.android.inputmethod.latin/files/clipboard_image/*'),
        "output_types": "standard",
        "artifact_icon": "clipboard",
    },
    "get_gboardCache_keystrokes": {
        "name": "Gboard - Keystroke Cache",
        "description": "Keystrokes typed by the user in app input fields, temporarily cached by Gboard",
        "author": "",
        "creation_date": "2021-01-09",
        "last_update_date": "2023-05-01",
        "requirements": "none",
        "category": "Gboard Keyboard",
        "notes": "",
        "paths": ('*/com.google.android.inputmethod.latin/databases/trainingcache*.db',),
        "output_types": "standard",
        "artifact_icon": "chrome",
    },
    "get_gboardCache_sessions": {
        "name": "Gboard - Sessions",
        "description": "Gboard keyboard input sessions (trainingcachev3.db)",
        "author": "",
        "creation_date": "2021-01-09",
        "last_update_date": "2023-05-01",
        "requirements": "none",
        "category": "Gboard Keyboard",
        "notes": "",
        "paths": ('*/com.google.android.inputmethod.latin/databases/trainingcachev3.db',),
        "output_types": "standard",
        "artifact_icon": "chrome",
    }
}

import datetime
import os
import sqlite3

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, \
    does_table_exist_in_db, check_in_media


class keyboard_event:
    def __init__(self, event_id, app, text, textbox_name, textbox_id, event_date, start_date='', end_date=''):
        self.id = event_id
        self.app = app
        self.text = text
        self.textbox_name = textbox_name
        self.textbox_id = textbox_id
        self.event_date = event_date
        self.start_date = start_date
        self.end_date = end_date


def _str_to_utc(value):
    '''Parse a SQLite datetime(...,'unixepoch') 'YYYY-MM-DD HH:MM:SS' UTC string to an aware datetime.'''
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _events_trainingcache2(file_found):
    events = []
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    if does_table_exist_in_db(file_found, 'training_input_events_table'):
        try:
            cursor.execute('''
                SELECT _id, _payload, f2 as app, f4 as textbox_name, f5 as textbox_id,
                datetime(f9/1000, "unixepoch") as ts
                FROM training_input_events_table
            ''')
            pb_types = {'7': {'type': 'message', 'message_typedef':
                              {'2': {'type': 'message', 'message_typedef':
                                     {'1': {'name': '', 'type': 'bytes'}}}}}}
            for row in cursor.fetchall():
                data, _ = blackboxprotobuf.decode_message(row['_payload'], pb_types)
                texts = data.get('7', {}).get('2', [])
                text_typed = ''
                if texts:
                    if isinstance(texts, list):
                        for t in texts:
                            text_typed += t.get('1', b'').decode('utf8', 'ignore')
                    else:
                        text_typed = texts.get('1', b'').decode('utf8', 'ignore')
                events.append(keyboard_event(row['_id'], row['app'], text_typed,
                                             row['textbox_name'], row['textbox_id'], row['ts']))
        except (sqlite3.Error, TypeError, ValueError) as ex:
            logfunc(f'gboard trainingcache2 error reading {file_found}: {ex}')
    elif does_table_exist_in_db(file_found, 'tf_table'):
        try:
            cursor.execute('''
                SELECT s._id, ts, f3_concat as text_entered, s.f7 as textbox_name, s.f8 as app, s.f9,
                datetime(s.f10/1000, 'unixepoch') as start_ts, datetime(s.f11/1000, 'unixepoch') as end_ts
                FROM
                (SELECT datetime(_timestamp/1000, 'unixepoch') as ts, f1,
                group_concat(f3, '') as f3_concat FROM tf_table GROUP BY f1) x
                LEFT JOIN s_table s on s.f1=x.f1
            ''')
            for row in cursor.fetchall():
                events.append(keyboard_event(row['_id'], row['app'], row['text_entered'],
                                             row['textbox_name'], '', row['ts'], row['start_ts'], row['end_ts']))
        except (sqlite3.Error, TypeError, ValueError) as ex:
            logfunc(f'gboard trainingcache2 error reading {file_found}: {ex}')
    db.close()
    return events


def _events_trainingcachev2(file_found):
    events = []
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    try:
        cursor.execute('''
            SELECT i._payload as data_proto, s._payload as desc_proto,
            datetime(i._timestamp/1000, 'unixepoch') as ts1, datetime(s._timestamp/1000, 'unixepoch') as ts2,
            s._id as session, i._id as id
            FROM input_action_table i LEFT JOIN session_table s ON s._session_id=i._session_id
        ''')
        last_session = None
        ke = None
        for row in cursor.fetchall():
            session = row['session']
            if last_session != session:
                if ke and ke.text:
                    events.append(ke)
                last_session = session
                ke = keyboard_event(row['id'], '', '', '', '', row['ts2'], row['ts1'], row['ts1'])
                desc_proto = row['desc_proto']
                if desc_proto:
                    desc, _ = blackboxprotobuf.decode_message(desc_proto, None)
                    try:
                        ke.textbox_name = desc.get('6', b'').decode('utf8', 'ignore')
                    except AttributeError:
                        pass
                    try:
                        ke.app = desc.get('7', b'').decode('utf8', 'ignore')
                    except AttributeError:
                        pass
            ke.end_date = row['ts1']
            data_proto = row['data_proto']
            if data_proto:
                data, _ = blackboxprotobuf.decode_message(data_proto, None)
                input_dict = data.get('6', None)
                if input_dict:
                    chars_items = input_dict.get('4', {})
                    chars = ''
                    if isinstance(chars_items, list):
                        for item in chars_items:
                            try:
                                chars += item.get('1', b'').decode('utf8', 'ignore')
                            except AttributeError:
                                pass
                    else:
                        try:
                            chars = chars_items.get('1', b'').decode('utf8', 'ignore')
                        except AttributeError:
                            pass
                    ke.text += chars
        if ke and ke.text:
            events.append(ke)
    except (sqlite3.Error, TypeError, ValueError) as ex:
        logfunc(f'gboard trainingcachev2 error reading {file_found}: {ex}')
    db.close()
    return events


@artifact_processor
def get_gboardCache(files_found, report_folder, seeker, wrap_text):
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('gboard_clipboard.db'):
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT datetime(timestamp/1000,'unixepoch'), text, html_text, uri,
            CASE item_type WHEN 0 THEN '' WHEN 1 THEN 'Pinned' ELSE item_type END,
            CASE entity_type WHEN 0 THEN '' WHEN 1 THEN 'Link' ELSE entity_type END,
            _id,
            replace(uri, rtrim(uri, replace(uri, '/', '')), '')
            FROM clips
        ''')
        rows = cursor.fetchall()
        db.close()
        for row in rows:
            image = ''
            file_key = str(row[7])
            if file_key:
                for match in files_found:
                    match = str(match)
                    if file_key in match:
                        image = check_in_media(match, os.path.basename(match))
                        break
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], image, row[4], row[5], row[6]))

    data_headers = (('Timestamp', 'datetime'), 'Text', 'HTML Text', 'URI', ('Image', 'media'),
                    'Item Type', 'Entity Type', 'ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_gboardCache_keystrokes(files_found, report_folder, seeker, wrap_text):
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if '/mirror/' in file_found or '\\mirror\\' in file_found:
            continue
        if file_found.endswith(('trainingcache2.db', 'trainingcache3.db')):
            events = _events_trainingcache2(file_found)
        elif file_found.endswith('trainingcachev2.db'):
            events = _events_trainingcachev2(file_found)
        else:
            continue
        source_path = file_found
        name = os.path.basename(file_found)
        for ke in events:
            data_list.append((name, _str_to_utc(ke.event_date), ke.id, ke.text, ke.app,
                              ke.textbox_name, ke.textbox_id))

    data_headers = ('Source', ('Event Timestamp', 'datetime'), 'ID', 'Text', 'App', 'Input Name', 'Input ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_gboardCache_sessions(files_found, report_folder, seeker, wrap_text):
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('trainingcachev3.db'):
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT datetime(session._session_id / 1000, 'unixepoch'),
                datetime(session._timestamp_ / 1000, 'unixepoch'),
                session._session_id, session.package_name
                FROM session
            ''')
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
        db.close()
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3]))

    data_headers = (('Start', 'datetime'), ('Finish', 'datetime'), 'Session ID', 'Application')
    return data_headers, data_list, source_path
