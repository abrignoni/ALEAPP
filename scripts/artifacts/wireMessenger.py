__artifacts_v2__ = {
    "get_wire_profile": {
        "name": "Wire User Profile",
        "description": "Parses details about the user profile for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35. Only the first registered client (clients[0]) "
                 "is reported; any further clients registered to the account are not listed.\n"
                 "Applies to the legacy app generation that keeps a plain-SQLite database named by "
                 "the account id next to com.wire.preferences.xml. Newer app versions store user "
                 "data in databases/user-db-<account id>-wirecom, whose content is not plain SQLite "
                 "(the app's own log records a database keying operation, and the app's published "
                 "core wireapp/kalium carries SqlCipherKey.kt in data/persistence), and their "
                 "shared preferences are encrypted, so nothing is reported for those versions.",
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 1 row",
            "pixel3_a12": "Android 12 | com.wire | 1 row",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, user database not plain SQLite",
        },
    },
    "get_wire_contacts": {
        "name": "Wire Contacts",
        "description": "Parses user contacts for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35.\n"
                 "Applies to the legacy app generation that keeps a plain-SQLite database named by "
                 "the account id next to com.wire.preferences.xml. Newer app versions store user "
                 "data in databases/user-db-<account id>-wirecom, whose content is not plain SQLite "
                 "(the app's own log records a database keying operation, and the app's published "
                 "core wireapp/kalium carries SqlCipherKey.kt in data/persistence), and their "
                 "shared preferences are encrypted, so nothing is reported for those versions.",
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 2 rows",
            "pixel3_a12": "Android 12 | com.wire | 2 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, user database not plain SQLite",
        },
    },
    "get_wire_messages": {
        "name": "Wire Messages",
        "description": "Parses messages and call history for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35. Rows taken from the MsgDeletion table carry "
                 "their timestamp in the Date / Time Deleted column and have no sent time. The call "
                 "duration column is rendered by dividing the stored duration by 1000, which assumes "
                 "the value is milliseconds; that unit has not been independently verified.\n"
                 "Applies to the legacy app generation that keeps a plain-SQLite database named by "
                 "the account id next to com.wire.preferences.xml. Newer app versions store user "
                 "data in databases/user-db-<account id>-wirecom, whose content is not plain SQLite "
                 "(the app's own log records a database keying operation, and the app's published "
                 "core wireapp/kalium carries SqlCipherKey.kt in data/persistence), and their "
                 "shared preferences are encrypted, so nothing is reported for those versions.",
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 15 rows",
            "pixel3_a12": "Android 12 | com.wire | 30 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, user database not plain SQLite",
        },
    },
    "get_wire_cached_files": {
        "name": "Wire Cached Files",
        "description": "Files the Wire app stores on disk per account, shown as media where the "
                       "content is an image",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "One row per file under files/wire.com/<account id>/ and cache/wire.com/"
                 "<account id>/ inside the app sandbox. On tested images these directories hold "
                 "PNG and JPEG content, some of it in files without an extension; the type is "
                 "read from the file content (PNG, JPEG and MP4 observed). These files sit "
                 "outside the databases newer app versions encrypt, so they remain readable "
                 "when the message store is not. What each file was used for by the app is not "
                 "asserted.",
        "paths": ('*/com.wire/files/wire.com/*/*',
                  '*/com.wire/cache/wire.com/*/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 0 rows, no wire.com file directories",
            "pixel3_a12": "Android 12 | com.wire | 0 rows, no wire.com file directories",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 14 rows",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 11 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 20 rows",
        },
    },
    "get_wire_proteus_sessions": {
        "name": "Wire Proteus Sessions",
        "description": "Proteus end-to-end encryption sessions stored by the Wire app, with the "
                       "other party's user id, domain and client id taken from the session file "
                       "name",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "One row per file under app_accounts/<domain>/<account id>/proteus/sessions/ in "
                 "current app versions, or files/otr/<account id>/sessions/ in the legacy "
                 "generation. The file name is the Proteus session id, which the app's published "
                 "core builds as <user id>_<client id> with the user id rendered as "
                 "<value>@<domain> (CryptoSessionId in core/cryptography/src/commonMain/kotlin/"
                 "com/wire/kalium/cryptography/ProteusClient.kt and CryptoQualifiedID in the "
                 "IDs.kt beside it, wireapp/kalium commit e9ac68451ad88f9e67dd41216df926ba47b3a581). "
                 "Legacy session names predate qualified user ids and carry no domain, which is "
                 "reported empty rather than assumed.\n"
                 "These files sit outside the databases current app versions encrypt, so they "
                 "remain readable when the message store is not. A session file records that a "
                 "cryptographic session exists with that client. It does not establish that a "
                 "message was sent, received or read, it carries no message content, and the "
                 "session contents are not decoded here.\n"
                 "An extraction containing both /data/data and /data/user/0 holds the same store "
                 "twice, so each session is listed once per path; the Source Path column "
                 "distinguishes them.",
        "paths": ('*/com.wire/app_accounts/*/*/proteus/sessions/*',
                  '*/com.wire/files/otr/*/sessions/*'),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 14 rows, legacy otr store, 7 distinct "
                          "sessions each listed under /data/data and /data/user/0, no domain "
                          "in the stored names",
            "pixel3_a12": "Android 12 | com.wire | 18 rows, legacy otr store, 9 distinct "
                          "sessions each listed under /data/data and /data/user/0, no domain "
                          "in the stored names",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 5 rows, qualified ids with domain",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, proteus store "
                                "present with no session files",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, proteus store present with no "
                                "session files",
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
    time(Messages.duration/1000,'unixepoch'), {asset_name}
    FROM Messages
    LEFT JOIN Users ON Users._id = Messages.user_id
    LEFT JOIN Likings ON Messages._id = Likings.message_id
    LEFT JOIN Users Users1 ON Likings.user_id = Users1._id
    {asset_join}
    ORDER BY Messages.time
'''


def _asset_source(source_path):
    """Resolve the asset table this Wire release uses.

    Newer databases keep attachments in Assets2, older ones in Assets, and a
    Messages table without asset_id has nothing to join. Returns the SELECT
    expression and JOIN clause for MESSAGES_SQL. Only the Assets2 shape is
    corpus-verified; the Assets fallback comes from a community-reported
    older database (PR #633) and has not been exercised here.
    """
    db = open_sqlite_db_readonly(source_path)
    try:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        cursor.execute('PRAGMA table_info(Messages)')
        has_asset_id = 'asset_id' in {row[1] for row in cursor.fetchall()}
    except sqlite3.Error:
        tables, has_asset_id = set(), False
    finally:
        db.close()
    for table in ('Assets2', 'Assets'):
        if has_asset_id and table in tables:
            db = open_sqlite_db_readonly(source_path)
            try:
                has_name = 'name' in {row[1] for row in db.execute(f'PRAGMA table_info({table})')}
            except sqlite3.Error:
                has_name = False
            finally:
                db.close()
            name_expr = f'{table}.name' if has_name else "''"
            return name_expr, f'LEFT JOIN {table} ON Messages.asset_id = {table}._id'
    return "''", ''


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
def get_wire_profile(context):
    files_found = context.get_files_found()
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
                    'First Client Label', 'Device Model', ('Date Registered', 'datetime'),
                    'Profile Picture ID', ('Profile Picture', 'media'))
    return data_headers, data_list, source_path


@artifact_processor
def get_wire_contacts(context):
    files_found = context.get_files_found()
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
def get_wire_messages(context):
    files_found = context.get_files_found()
    source_path = _user_db(files_found)
    data_list = []
    asset_name, asset_join = _asset_source(source_path) if source_path else ("''", '')
    for r in _run(source_path, MESSAGES_SQL.format(asset_name=asset_name, asset_join=asset_join)):
        data_list.append((_str_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], _str_to_utc(r[6]), r[7], r[8], r[9],
                          ''))

    # Surface deleted messages from MsgDeletion read-only (the original modified the source DB to do this).
    # MsgDeletion.timestamp is a deletion time, not a sent time, so it gets its own column.
    for d in _run(source_path, 'SELECT message_id, timestamp FROM MsgDeletion'):
        data_list.append(('', d[0], '', 'Deleted', '', '', '', '', '', '', _ms_to_utc(d[1])))

    data_headers = (('Date / Time Sent', 'datetime'), 'Message ID', 'User Name', 'Message Type',
                    'Message Content', 'Reaction', ('Date / Time Reacted', 'datetime'), 'Reacted By',
                    'Call Duration (assumes ms)', 'Asset Name', ('Date / Time Deleted', 'datetime'))
    return data_headers, data_list, source_path


_WIRE_ACCOUNT_DIR_RE = re.compile(r'[/\\]wire\.com[/\\]([^/\\]+)[/\\]')


@artifact_processor
def get_wire_cached_files(context):
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        match = _WIRE_ACCOUNT_DIR_RE.search(file_found)
        if not match or isdir(file_found):
            continue
        account_id = match.group(1)

        extension = None
        try:
            with open(file_found, 'rb') as handle:
                magic = handle.read(8)
        except OSError:
            magic = b''
        if magic.startswith(b'\x89PNG'):
            extension = 'png'
        elif magic.startswith(b'\xff\xd8'):
            extension = 'jpg'
        elif magic[4:8] == b'ftyp':
            extension = 'mp4'
        media_ref = ''
        if extension:
            media_ref = check_in_media(file_found, basename(file_found),
                                       force_extension=extension) or ''

        data_list.append((
            basename(file_found),
            media_ref,
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'File Name',
        ('File', 'media'),
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


_PROTEUS_SESSION_RE = re.compile(
    r'[/\\]com\.wire[/\\]app_accounts[/\\][^/\\]+[/\\]([^/\\]+)[/\\]proteus[/\\]sessions[/\\]([^/\\]+)$')
_OTR_SESSION_RE = re.compile(
    r'[/\\]com\.wire[/\\]files[/\\]otr[/\\]([^/\\]+)[/\\]sessions[/\\]([^/\\]+)$')


@artifact_processor
def get_wire_proteus_sessions(context):
    data_list = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if isdir(file_found):
            continue
        match = _PROTEUS_SESSION_RE.search(file_found) or _OTR_SESSION_RE.search(file_found)
        if not match:
            continue
        account_id = match.group(1)
        session_id = match.group(2)

        # The session id is "<user id>_<client id>", and the user id is
        # "<value>@<domain>" once the app started qualifying ids. Legacy names
        # carry no domain, so it stays empty rather than being assumed.
        remote_user, _, remote_client = session_id.rpartition('_')
        if not remote_user:
            remote_user, remote_client = session_id, ''
        user_value, _, domain = remote_user.partition('@')

        data_list.append((
            user_value,
            domain,
            remote_client,
            account_id,
            session_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Other Party User ID',
        'Other Party Domain',
        'Other Party Client ID',
        'Local Account ID',
        'Session ID (as stored)',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'
