import bcrypt
import xml.etree.ElementTree as ET
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.artifacts.mewe import APP_NAME
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

APP_NAME = 'Snapchat'

# Last actions taken in the application and who did them
FEED_QUERY = '''
    SELECT
        DATETIME(lastInteractionTimestamp/1000, 'unixepoch', 'localtime'),
        key,
        displayInteractionType,
        DATETIME(lastReadTimestamp/1000, 'unixepoch', 'localtime'),
        lastReader,
        DATETIME(lastWriteTimestamp/1000, 'unixepoch', 'localtime'),
        lastWriter,
        lastWriteType
    FROM Feed
'''

# Contacts and friends
#
# NOTE(s) FOR EXAMINERS:
#   1. it is possible to remove the WHERE clause to see a more extensive
#      list, but there could be old data not related to the current
#      accounts'
#   2. since everyone is linked to "teamsnapchat" user, the addedTimestamp
#      field indicates when the user was created
FRIEND_QUERY = '''
    SELECT 
        case addedTimestamp
			when 0 then ''
			else datetime(addedTimestamp/1000, 'unixepoch', 'localtime')
		end,
        username,
        userId,
        displayName,
        phone,
        birthday
    FROM Friend
    WHERE addedTimestamp IS NOT NULL;
'''

# Chat messages
CHAT_MESSAGE_QUERY = '''
    SELECT
        DATETIME(timestamp/1000, 'unixepoch', 'localtime') as timestamp,
        CASE
            WHEN seenTimestamp IS NULL THEN "UNREAD"
            ELSE DATETIME(seenTimestamp/1000, 'unixepoch', 'localtime')
        END seenTimestamp,
        senderId,
        username as senderName,
        displayName as senderDisplayName,
        type,
        content
    FROM Message
    JOIN Friend on senderId = Friend._id;
'''

MEMORIES_ENTRY_QUERY = '''
    SELECT
        DATETIME(create_time/1000, 'unixepoch', 'localtime'),
        _id,
        snap_ids,
        CASE is_private
            WHEN 1 THEN "YES"
            ELSE "NO"
        END is_private,
        cached_servlet_media_formats
    FROM memories_entry
'''

MEO_QUERY = '''
    SELECT
        user_id,
        hashed_passcode,
        master_key,
        master_key_iv
    FROM memories_meo_confidential
'''

SNAP_MEDIA_QUERY = '''
    SELECT
        DATETIME(create_time/1000, 'unixepoch', 'localtime'),
        memories_snap._id,
        media_id,
        memories_entry_id,
        time_zone_id,
        format,
        width,
        height,
        duration,
        CASE has_overlay_image
            WHEN 1 THEN "YES"
            ELSE "NO"
        END has_overlay_image,
        overlay_size,
        overlay_redirect_info,
        CASE front_facing
            WHEN 1 THEN "YES"
            ELSE "NO"
        END front_facing,
        size,
        CASE has_location
            WHEN 1 THEN "YES"
            ELSE "NO"
        END has_location,
        latitude,
        longitude,
        snap_create_user_agent,
        thumbnail_size,
        thumbnail_redirect_info
    FROM memories_snap
    JOIN memories_media ON memories_media._id = media_id;
'''

# ATTENTION: this function can slow down the processing
meo_codes = {} # to optimize the search in case of multiple meo with same hash
def _decrypt_meo_code(hash):
    try:
        return meo_codes[hash]
    except KeyError:
        # the passcode is 4-digit and numeric, O(10^4)
        for p1 in range(10):
            for p2 in range(10):
                for p3 in range(10):
                    for p4 in range(10):
                        psw = f'{p1}{p2}{p3}{p4}'
                        if bcrypt.checkpw(psw.encode(), hash.encode()):
                            meo_codes[hash] = psw
                            return psw
        return 'Could not find any passcode'


def _get_text_from_blob(blob, start_byte, len_byte, type=None):
    if type != None and type != 'text':
        return ''

    length = blob[len_byte]
    msg = blob[start_byte:start_byte+length].decode()
    return msg


def _perform_query(cursor, query):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return len(rows), rows
    except Exception as e:
        return 0, None


def _make_reports(title, data_headers, data_list, report_folder, db_file_name, tl_bool):
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, db_file_name)
    report.end_artifact_report()

    tsv(report_folder, data_headers, data_list, title, db_file_name)
    if tl_bool == True:
        timeline(report_folder, title, data_list, data_headers)

def _parse_feeds(feeds_count, rows, report_folder, db_file_name):
    logfunc(f'{feeds_count} feeds found')

    data_headers = (
        'Last Interaction Timestamp','Key', 'Display Interaction Type',
        'Last Read Timestamp', 'Last Reader', 'Last Write Timestamp',
        'Last Writer', 'Last Write Type'
    )
    data_list = [(
        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
    ) for row in rows]
    
    tl_bool = True

    _make_reports(f'{APP_NAME} - Feeds', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_friends(friends_count, rows, report_folder, db_file_name):
    logfunc(f'{friends_count} friends found')

    data_headers = (
        'Added Timestamp', 'Username', 'User ID', 'Display Name', 'Phone Nr',
        'Birthday'
    )
    data_list = [(
        row[0], row[1], row[2], row[3], row[4], row[5]
    ) for row in rows]
    
    tl_bool = True

    _make_reports(f'{APP_NAME} - Friends', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_messages(messages_count, rows, report_folder, db_file_name):
    logfunc(f'{messages_count} messages found')

    data_headers = (
        'Creation Timestamp', 'Seen Timestamp', 'Sender ID', 'Sender Username',
        'Sender Display Name', 'Message Type', 'Text',
    )
    data_list = [(
        row[0], row[1], row[2], row[3], row[4], row[5],
        _get_text_from_blob(row[6], 0x2c, 0x28, row[5])
    ) for row in rows]

    tl_bool = True

    _make_reports(f'{APP_NAME} - Messages', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_memories_entry(memories_count, rows, report_folder, db_file_name):
    logfunc(f'{memories_count} memories found')

    data_headers = (
        'Timestamp', 'Memory ID', 'Snap ID', 'Is Private', 'Media Format',
    )
    data_list = [(
        row[0], row[1], _get_text_from_blob(row[2], 0x20, 0x1c),
        row[3], _get_text_from_blob(row[4], 0x20, 0x1c)
    ) for row in rows]

    tl_bool = True

    _make_reports(f'{APP_NAME} - Memories', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_meo(meo_count, rows, report_folder, db_file_name):
    logfunc(f'{meo_count} MEO (My Eyes Only) found')

    # NOTE(s) FOR EXAMINERS:
    #   if the processing gets to slow, remove the 'Passcode' column and
    #   also the _decrypt_meo_code() function invocation
    data_headers = (
        'User ID', 'Hashed Passcode', 'Passcode', 'Master Key', 'Master Key IV'
    )
    data_list = [(
        row[0], row[1], _decrypt_meo_code(row[1]), row[2], row[3]
    ) for row in rows]
    
    tl_bool = False

    _make_reports(f'{APP_NAME} - MEO (My Eyes Only)', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_snap_media(snap_media_count, rows, report_folder, db_file_name):
    logfunc(f'{snap_media_count} Snap Media found')

    data_headers = (
        'Create Time', 'ID', 'Media ID', 'Memories Entry ID', 'Time Zone ID', 'Format',
        'Width', 'Heigth', 'Duration', 'Has Overlay', 'Overlay Size', 'Overlay Info',
        'Front Facing', 'Size', 'Has Location Info', 'Latitude', 'Longitude',
        'Snap User Agent', 'Thumbnail Size', 'Thumbnail Info'
    )
    data_list = [(
        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
        row[8], row[9], row[10], row[11], row[12], row[13], row[14],
        row[15], row[16], row[17], row[18], row[19]
    ) for row in rows]
    
    tl_bool = True

    _make_reports(f'{APP_NAME} - Snap Media', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_main_db(db_file, db_file_name, report_folder):
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()

    feeds_count, rows = _perform_query(cursor, FEED_QUERY)
    if feeds_count > 0 and rows:
        _parse_feeds(feeds_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} feeds data found')

    friends_count, rows = _perform_query(cursor, FRIEND_QUERY)
    if friends_count > 0 and rows:
        _parse_friends(friends_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} friends data found')

    messages_count, rows = _perform_query(cursor, CHAT_MESSAGE_QUERY)
    if messages_count > 0 and rows:
        _parse_messages(messages_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} messages data found')

    cursor.close()
    db.close()


def _parse_memories_db(db_file, db_file_name, report_folder):
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()

    memories_count, rows = _perform_query(cursor, MEMORIES_ENTRY_QUERY)
    if memories_count > 0 and rows:
        _parse_memories_entry(memories_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} memories data found')

    meo_count, rows = _perform_query(cursor, MEO_QUERY)
    if meo_count > 0 and rows:
        _parse_meo(meo_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} MEO (My Eyes Only) data found')

    snap_media_count, rows = _perform_query(cursor, SNAP_MEDIA_QUERY)
    if snap_media_count > 0 and rows:
        _parse_snap_media(snap_media_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} snap media memories data found')

    cursor.close()
    db.close()


def _parse_xml(xml_file, xml_file_name, report_folder, title, report_name):
    logfunc(f'{title} found')

    tree = ET.parse(xml_file)
    data_headers = ('Key', 'Value')
    data_list = []
    unix_stamps = ['INSTALL_ON_DEVICE_TIMESTAMP','LONG_CLIENT_ID_DEVICE_TIMESTAMP','FIRST_LOGGED_IN_ON_DEVICE_TIMESTAMP']

    root = tree.getroot()
    for node in root:
        value = None
        try:
            value = node.attrib['value']
        except:
            value = node.text
            
        if node.attrib['name'] in unix_stamps:
            value = datetime.datetime.utcfromtimestamp(int(value)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        else:
            pass
        
        data_list.append((node.attrib['name'], value))

    tl_bool = False
    
    _make_reports(f'{APP_NAME} - {report_name}', data_headers, data_list, report_folder, xml_file_name, tl_bool)


def get_snapchat(files_found, report_folder, seeker, wrap_text):
    db_file = None
    db_file_name = None
    xml_file = None
    xml_file_name = None

    main_processed = False
    memories_processed = False
    identity_persistent_processed = False
    login_signup_store_processed = False
    user_session_processed = False

    for ff in files_found:
        ###
        # Note:
        # the rest of the functions ware tested against a "main.db" instance.
        # Snapchat decided to change name of their DBs in latest versions of
        # the app. The queries can fail on "tcspahn" but the interesting
        # tables have a very similar schema, so I hope they won't :)
        ###
        if (ff.endswith('main.db') or ff.endswith('tcspahn.db')) and not main_processed:
            db_file = ff
            db_file_name = ff.replace(seeker.data_folder, '')
            _parse_main_db(db_file, db_file_name, report_folder)
            main_processed = True
        elif ff.endswith('memories.db') and not memories_processed:
            db_file = ff
            db_file_name = ff.replace(seeker.data_folder, '')
            _parse_memories_db(db_file, db_file_name, report_folder)
            memories_processed = True
        elif ff.endswith('identity_persistent_store.xml') and not identity_persistent_processed:
            xml_file = ff
            xml_file_name = ff.replace(seeker.data_folder, '')
            _parse_xml(xml_file, xml_file_name, report_folder, 'identity_persistent_store.xml', 'Identity Persistent')
            identity_persistent_processed = True
        elif ff.endswith('LoginSignupStore.xml') and not login_signup_store_processed:
            xml_file = ff
            xml_file_name = ff.replace(seeker.data_folder, '')
            _parse_xml(xml_file, xml_file_name, report_folder, 'LoginSignupStore.xml', 'Login Signup')
            login_signup_store_processed = True
        elif ff.endswith('user_session_shared_pref.xml') and not user_session_processed:
            xml_file = ff
            xml_file_name = ff.replace(seeker.data_folder, '')
            _parse_xml(xml_file, xml_file_name, report_folder, 'user_session_shared_pref.xml', 'User Session Shared')
            user_session_processed = True

    artifacts = [
        main_processed, memories_processed, identity_persistent_processed,
        login_signup_store_processed, user_session_processed
    ]
    if not (True in artifacts):
        logfunc(f'{APP_NAME} data not found')

__artifacts__ = {
        "snapchat": (
                "Snapchat",
                ('*/com.snapchat.android/databases/*.db', '*/com.snapchat.android/shared_prefs/*.xml'),
                get_snapchat)
}