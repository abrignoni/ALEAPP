# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_snapchat_feeds": {
        "name": "Snapchat - Feeds",
        "description": "Snapchat feed (last interaction per conversation)",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "rss",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 0 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
        },
    },
    "get_snapchat_friends": {
        "name": "Snapchat - Friends",
        "description": "Snapchat friends / contacts",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 4 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 6 rows",
        },
    },
    "get_snapchat_messages": {
        "name": "Snapchat - Messages",
        "description": "Snapchat chat messages",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 0 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
        },
    },
    "get_snapchat_memories": {
        "name": "Snapchat - Memories",
        "description": "Snapchat memories entries",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "standard", "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 3 rows",
        },
    },
    "get_snapchat_meo": {
        "name": "Snapchat - MEO My Eyes Only",
        "description": "Snapchat My Eyes Only confidential data; recovers the 4-digit passcode via bcrypt",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat",
        "notes": "Passcode recovery brute-forces the 4-digit MEO code (bcrypt); can be slow.",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "standard", "artifact_icon": "eye-off",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 1 row",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
        },
    },
    "get_snapchat_snap_media": {
        "name": "Snapchat - Snap Media",
        "description": "Snapchat memories snap media (incl. geolocation)",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "all", "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 5 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 3 rows",
        },
    },
    "get_snapchat_identity": {
        "name": "Snapchat - Identity Persistent Store",
        "description": "Snapchat identity_persistent_store.xml",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/shared_prefs/identity_persistent_store.xml',),
        "output_types": "standard", "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 12 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 10 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 12 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 13 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 12 rows",
        },
    },
    "get_snapchat_login_signup": {
        "name": "Snapchat - Login Signup Store",
        "description": "Snapchat LoginSignupStore.xml",
        "author": "", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/shared_prefs/LoginSignupStore.xml',),
        "output_types": "standard", "artifact_icon": "login-2",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 2 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 3 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 2 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 1 row",
        },
    }
}

import datetime
import sqlite3
import xml.etree.ElementTree as ET

import bcrypt

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_MEO_CODES = {}
_XML_UNIX_KEYS = {'INSTALL_ON_DEVICE_TIMESTAMP', 'LONG_CLIENT_ID_DEVICE_TIMESTAMP',
                  'FIRST_LOGGED_IN_ON_DEVICE_TIMESTAMP'}


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(files_found, *suffixes):
    for f in files_found:
        f = str(f)
        if f.endswith(suffixes):
            return f
    return ''


def _rows(source_path, sql):
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


def _text_from_blob(blob, start_byte, len_byte, type_=None):
    if type_ is not None and type_ != 'text':
        return ''
    try:
        length = blob[len_byte]
        return blob[start_byte:start_byte + length].decode('utf-8', 'replace')
    except (TypeError, IndexError, AttributeError):
        return ''


def _decrypt_meo_code(hashed):
    if hashed in _MEO_CODES:
        return _MEO_CODES[hashed]
    try:
        hash_bytes = hashed.encode()
    except (AttributeError, UnicodeEncodeError):
        return ''
    for code in range(10000):  # 4-digit numeric passcode, O(10^4)
        psw = f'{code:04d}'
        try:
            if bcrypt.checkpw(psw.encode(), hash_bytes):
                _MEO_CODES[hashed] = psw
                return psw
        except (ValueError, TypeError):
            return ''
    return 'Could not find any passcode'


@artifact_processor
def get_snapchat_feeds(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT lastInteractionTimestamp, key, displayInteractionType, lastReadTimestamp, lastReader,
               lastWriteTimestamp, lastWriter, lastWriteType FROM Feed
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], _ms_to_utc(r[3]), r[4], _ms_to_utc(r[5]), r[6], r[7])
                 for r in rows]
    data_headers = (('Last Interaction Timestamp', 'datetime'), 'Key', 'Display Interaction Type',
                    ('Last Read Timestamp', 'datetime'), 'Last Reader',
                    ('Last Write Timestamp', 'datetime'), 'Last Writer', 'Last Write Type')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_friends(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT addedTimestamp, username, userId, displayName, phone, birthday
        FROM Friend WHERE addedTimestamp IS NOT NULL
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Added Timestamp', 'datetime'), 'Username', 'User ID', 'Display Name',
                    'Phone Nr', 'Birthday')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_messages(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT timestamp, seenTimestamp, senderId, username, displayName, type, content
        FROM Message JOIN Friend on senderId = Friend._id
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5],
                  _text_from_blob(r[6], 0x2c, 0x28, r[5])) for r in rows]
    data_headers = (('Creation Timestamp', 'datetime'), ('Seen Timestamp', 'datetime'), 'Sender ID',
                    'Sender Username', 'Sender Display Name', 'Message Type', 'Text')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_memories(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path, '''
        SELECT create_time, _id, snap_ids, CASE is_private WHEN 1 THEN 'YES' ELSE 'NO' END,
               cached_servlet_media_formats FROM memories_entry
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], _text_from_blob(r[2], 0x20, 0x1c), r[3],
                  _text_from_blob(r[4], 0x20, 0x1c)) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Memory ID', 'Snap ID', 'Is Private', 'Media Format')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_meo(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path,
                 'SELECT user_id, hashed_passcode, master_key, master_key_iv FROM memories_meo_confidential')
    data_list = [(r[0], r[1], _decrypt_meo_code(r[1]), r[2], r[3]) for r in rows]
    data_headers = ('User ID', 'Hashed Passcode', 'Passcode', 'Master Key', 'Master Key IV')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_snap_media(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path, '''
        SELECT create_time, memories_snap._id, media_id, memories_entry_id, time_zone_id, format,
               width, height, duration,
               CASE has_overlay_image WHEN 1 THEN 'YES' ELSE 'NO' END,
               overlay_size, overlay_redirect_info,
               CASE front_facing WHEN 1 THEN 'YES' ELSE 'NO' END, size,
               CASE has_location WHEN 1 THEN 'YES' ELSE 'NO' END, latitude, longitude,
               snap_create_user_agent, thumbnail_size, thumbnail_redirect_info
        FROM memories_snap JOIN memories_media ON memories_media._id = media_id
    ''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Create Time', 'datetime'), 'ID', 'Media ID', 'Memories Entry ID', 'Time Zone ID',
                    'Format', 'Width', 'Height', 'Duration', 'Has Overlay', 'Overlay Size',
                    'Overlay Info', 'Front Facing', 'Size', 'Has Location Info', 'Latitude',
                    'Longitude', 'Snap User Agent', 'Thumbnail Size', 'Thumbnail Info')
    return data_headers, data_list, source_path


def _parse_xml_rows(xml_file):
    data_list = []
    if not xml_file:
        return data_list
    try:
        root = ET.parse(xml_file).getroot()
    except (ET.ParseError, OSError, ValueError):
        return data_list
    for node in root:
        name = node.attrib.get('name', '')
        value = node.attrib.get('value', node.text)
        if name in _XML_UNIX_KEYS and value:
            try:
                value = datetime.datetime.fromtimestamp(
                    int(value) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            except (ValueError, TypeError, OverflowError, OSError):
                pass
        data_list.append((name, value))
    return data_list


@artifact_processor
def get_snapchat_identity(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'identity_persistent_store.xml')
    return ('Key', 'Value'), _parse_xml_rows(source_path), source_path


@artifact_processor
def get_snapchat_login_signup(files_found, report_folder, seeker, wrap_text):
    source_path = _find(files_found, 'LoginSignupStore.xml')
    return ('Key', 'Value'), _parse_xml_rows(source_path), source_path
