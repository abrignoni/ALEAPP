# pylint: disable=W0613
__artifacts_v2__ = {
    "get_wire_profile": {
        "name": "Wire User Profile",
        "description": "Parses details about the user profile for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2024-04-24",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35",
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows",
        },
    },
    "get_wire_contacts": {
        "name": "Wire Contacts",
        "description": "Parses user contacts for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2024-04-24",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35",
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows",
        },
    },
    "get_wire_messages": {
        "name": "Wire Messages",
        "description": "Parses messages and call history for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2024-04-24",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35",
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows",
        },
    }
}

import datetime
import re
import sqlite3
import xml.etree.ElementTree as ET
from os.path import basename, isdir

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media

UUID_RE = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')

MESSAGES_SQL = '''
    SELECT datetime(Messages.time/1000,'unixepoch'), Messages._id, Users.name, Messages.msg_type,
    json_extract(Messages.content, '$[0].content'),
    CASE Likings."action" WHEN 1 THEN 'Liked' END,
    datetime(Likings."timestamp"/1000,'unixepoch'), Users1.name,
    time(Messages.duration/1000,'unixepoch'), Assets2.name
    FROM Messages
    LEFT JOIN Users ON Users._id = Messages.user_id
    LEFT JOIN Likings ON Messages._id = Likings.message_id
    LEFT JOIN Users Users1 ON Likings.user_id = Users1._id
    LEFT JOIN Assets2 ON Messages.asset_id = Assets2._id
    ORDER BY Messages.time
'''


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _user_id(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.wire.preferences.xml'):
            try:
                root = ET.parse(file_found).getroot()
            except (ET.ParseError, OSError):
                continue
            for elem in root:
                if 'active_account' in str(elem.attrib):
                    return elem.text
    return None


def _user_db(files_found):
    user_id = _user_id(files_found)
    if not user_id or not UUID_RE.match(user_id):
        return ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(user_id) or isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as fh:
                if fh.read(16) == b'SQLite format 3\x00':
                    return file_found
        except OSError:
            continue
    return ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_wire_profile(files_found, report_folder, seeker, wrap_text):
    source_path = _user_db(files_found)
    rows = _run(source_path, '''
        SELECT Users._id, Users.name, Users.email, Users.phone,
        json_extract(data, '$.clients[0].verification'),
        json_extract(data, '$.clients[0].label'),
        json_extract(data, '$.clients[0].model'),
        datetime(json_extract(data, '$.clients[0].regTime') / 1000, 'unixepoch'),
        Users.picture
        FROM Users LEFT JOIN Clients ON Users._id = Clients._id
        WHERE Users."connection" = "self"
    ''')
    data_list = []
    for row in rows:
        picture_id = str(row[8]) if row[8] is not None else ''
        thumb = ''
        if picture_id:
            match = next((str(f) for f in files_found if picture_id in str(f) and not isdir(str(f))), None)
            if match:
                thumb = check_in_media(match, basename(match))
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], _str_to_utc(row[7]),
                          row[8], thumb))

    data_headers = ('User ID', 'Display Name', 'Email Address', 'Phone Number', 'Verification Status',
                    'Verification Device', 'Device Model', ('Date Registered', 'datetime'),
                    'Profile Picture Name', ('Profile Picture', 'media'))
    return data_headers, data_list, source_path


@artifact_processor
def get_wire_contacts(files_found, report_folder, seeker, wrap_text):
    source_path = _user_db(files_found)
    rows = _run(source_path, '''
        SELECT Users._id, Users.name, Users.handle, Users.connection,
        datetime(Users.conn_timestamp/1000,'unixepoch'), Users.picture
        FROM Users WHERE Users.connection != 'self'
    ''')
    data_list = [(r[0], r[1], r[2], r[3], _str_to_utc(r[4]), r[5]) for r in rows]
    data_headers = ('User ID', 'Display Name', 'Handle ID', 'Connection Status',
                    ('Connection Time', 'datetime'), 'Profile Picture ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_wire_messages(files_found, report_folder, seeker, wrap_text):
    source_path = _user_db(files_found)
    data_list = []
    for r in _run(source_path, MESSAGES_SQL):
        data_list.append((_str_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], _str_to_utc(r[6]), r[7], r[8], r[9]))

    # Surface deleted messages from MsgDeletion read-only (the original modified the source DB to do this)
    for d in _run(source_path, 'SELECT message_id, timestamp FROM MsgDeletion'):
        data_list.append((_ms_to_utc(d[1]), d[0], '', 'Deleted', '', '', '', '', '', ''))

    data_headers = (('Date / Time Sent', 'datetime'), 'Message ID', 'User Name', 'Message Type',
                    'Message Content', 'Reaction', ('Date / Time Reacted', 'datetime'), 'Reacted By',
                    'Call Duration', 'Asset ID')
    return data_headers, data_list, source_path
