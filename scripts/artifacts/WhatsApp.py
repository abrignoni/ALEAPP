__artifacts_v2__ = {
    "get_whatsapp_contacts": {
        "name": "WhatsApp - Contacts",
        "description": "WhatsApp contacts (wa.db)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/wa.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 268 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 14 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 295 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 92 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 28 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 638 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 2 rows",
        },
    },
    "get_whatsapp_call_logs": {
        "name": "WhatsApp - Call Logs",
        "description": "WhatsApp call logs (msgstore.db)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 4 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
        },
    },
    "get_whatsapp_messages": {
        "name": "WhatsApp - Messages",
        "description": "WhatsApp messages (legacy msgstore.db schema with messages.data)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Legacy schema only; modern databases are covered by the One To One / Group Messages artifacts.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
        },
    },
    "get_whatsapp_one_to_one_messages": {
        "name": "WhatsApp - One To One Messages",
        "description": "WhatsApp 1:1 messages (modern msgstore.db schema)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 29 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 7 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 3877 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 73 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 195 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 781 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 71 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Other Participant WA User Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Other Participant WA User Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_group_messages": {
        "name": "WhatsApp - Group Messages",
        "description": "WhatsApp group messages (modern msgstore.db schema)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 39 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 156 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 4730 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sending Party",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_group_details": {
        "name": "WhatsApp - Group Details",
        "description": "WhatsApp chats with a subject in msgstore.db (groups, and newsletter chats where stored), with the group creator where wa.db records one",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": (
            "Reads msgstore.db's chat table joined to jid, one row per chat that carries a subject "
            "and whose jid_row_id names a jid row; all 27 chats with a subject on the tested images "
            "had one. The chat table is read directly rather than through chat_view, because "
            "chat_view has no jid_row_id column on 7 of the 12 tested images (pixel3_a11, "
            "pixel3_a12, pixel7a_a14, russell_a14, russell_pixel6a_a13, sharon_a13, sharon_a14); on "
            "the other 5, reading chat gives the same rows as reading chat_view. Chats keyed by a "
            "newsletter jid (...@newsletter) also carry a subject and are reported here: of the 27 "
            "rows on the tested images, 18 are newsletter chats (10 on kevin_pocox7_a15, 5 on "
            "russell_a14, 3 on samsungs20_a13) and 9 are groups (...@g.us). Group Creation "
            "Timestamp is chat.created_timestamp. Creator JID is wa.db's "
            "wa_group_admin_settings.creator_jid for the chat's jid. It held a value on 4 of the 9 "
            "group rows and on none of the 18 newsletter rows, and it was blank for all 5 groups on "
            "pixel7a_a14, russell_a14 and sharon_a14. It is also blank when wa.db lacks the "
            "creator_jid column, as on pixel3_a11, or when no wa.db is found (exercised on a "
            "constructed database only). Creator WA User Name and Creator WA Number come from the "
            "wa.db wa_contacts row whose jid equals Creator JID, and held no value on any tested "
            "image: on anne_a15, hc_pixel8pro_a16 and hc_pixel8pro_a17 the creator is recorded by a "
            "LID jid (@lid) that matches no wa_contacts row, and on sharon_a13 the matching "
            "wa_contacts row stores no name or number. Creator WA Profile Picture looks for a file "
            "named after Creator WA Number and held no value on any tested image. The files in "
            "com.whatsapp/files/Avatars are named by jid with a .j extension on the four tested "
            "images whose folder was listed (anne_a15, pixel7a_a14, russell_a14, sharon_a14), and "
            "none of the four images with a Creator JID (anne_a15, hc_pixel8pro_a16, "
            "hc_pixel8pro_a17, sharon_a13) holds a file named after it. Only the first msgstore.db "
            "matched is read, as in the module's other artifacts."
        ),
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*',
                  '*/com.whatsapp/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 10 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 3 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 6 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 3 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 1 row",
        },
    },
    "get_whatsapp_user_profile": {
        "name": "WhatsApp - User Profile",
        "description": "WhatsApp local user profile (shared_prefs xml)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml',
                  '*/com.whatsapp/shared_prefs/startup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 1 row",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 1 row",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 1 row",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
        },
    }
}

import datetime
import os
import sqlite3

import xmltodict

from scripts.ilapfuncs import artifact_processor, attach_sqlite_db_readonly, open_sqlite_db_readonly, check_in_media, \
    logfunc

# Re-used location columns shared by the one-to-one and group message queries.
_LOCATION_HEADERS = ('Shared Latitude/Starting Latitude (Live Location)',
                     'Shared Longitude/Starting Longitude (Live Location)',
                     'Duration Live Location Shared (Seconds)', 'Final Live Latitude',
                     'Final Live Longitude')

_MESSAGE_TYPE_CASE = '''CASE
        WHEN message.message_type=0 THEN "Text"
        WHEN message.message_type=1 THEN "Picture"
        WHEN message.message_type=2 THEN "Audio"
        WHEN message.message_type=3 THEN "Video"
        WHEN message.message_type=5 THEN "Static Location"
        WHEN message.message_type=7 THEN "System Message"
        WHEN message.message_type=9 THEN "Document"
        WHEN message.message_type=16 THEN "Live Location"
        ELSE message.message_type
        END'''


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _find(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if file_found.endswith(suffix):
            return file_found
    return ''


def _media(file_path):
    if not file_path:
        return ''
    ref = check_in_media(str(file_path), name=os.path.basename(str(file_path)))
    return ref or ''


def _open_msgstore(files_found):
    """Open msgstore.db with wa.db attached as wadb (when present)."""
    msg = _find(files_found, 'msgstore.db')
    wa = _find(files_found, 'wa.db')
    if not msg:
        return None, None, '', ''
    db = open_sqlite_db_readonly(msg)
    cursor = db.cursor()
    if wa:
        try:
            cursor.execute(attach_sqlite_db_readonly(wa, 'wadb'))
        except sqlite3.Error:
            pass
    return db, cursor, msg, wa


def _run(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as exc:
        logfunc(f'WhatsApp: query not run against this database schema, no rows read: {exc}')
        return []


def _has_column(cursor, schema, table, column):
    try:
        return column in [row[1] for row in cursor.execute(f'PRAGMA {schema}.table_info({table})')]
    except sqlite3.Error:
        return False


@artifact_processor
def get_whatsapp_contacts(context):
    files_found = context.get_files_found()
    source = _find(files_found, 'wa.db')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _run(cursor, '''
        SELECT
            CASE
                WHEN WC.given_name IS NULL AND WC.family_name IS NULL AND WC.display_name IS NULL THEN WC.jid
                WHEN WC.given_name IS NULL AND WC.family_name IS NULL THEN WC.display_name
                WHEN WC.given_name IS NULL THEN WC.family_name
                WHEN WC.family_name IS NULL THEN WC.given_name
                ELSE WC.given_name || " " || WC.family_name
            END,
            jid,
            CASE WHEN WC.number IS NULL THEN WC.jid WHEN WC.number == "" THEN WC.jid ELSE WC.number END
        FROM wa_contacts AS WC
        ''')
        for row in rows:
            data_list.append((row[0], row[1], row[2]))
        db.close()

    data_headers = ('Name', 'JID', 'Number')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_call_logs(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        rows = _run(cursor, '''
        SELECT
            datetime(call_log.timestamp/1000,'unixepoch'),
            datetime((call_log.timestamp/1000 + call_log.duration),'unixepoch'),
            strftime('%H:%M:%S', call_log.duration ,'unixepoch'),
            chat.subject,
            CASE WHEN call_log.from_me=0 THEN "Incoming" WHEN call_log.from_me=1 THEN "Outgoing" END,
            CASE WHEN call_log.from_me=1 THEN "Self" ELSE wa_contacts.wa_name END,
            CASE WHEN call_log.from_me=1 THEN "" ELSE wa_contacts.jid END,
            CASE WHEN call_log.video_call=0 THEN "Audio" WHEN call_log.video_call=1 THEN "Video" END
        FROM call_log
        LEFT JOIN jid ON jid._id=call_log.jid_row_id
        JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
        LEFT JOIN chat ON chat.jid_row_id=call_log.group_jid_row_id
        ORDER BY call_log.timestamp ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              row[5], row[6], row[7]))
        db.close()

    data_headers = (('Call Start Timestamp', 'datetime'), ('Call End Timestamp', 'datetime'),
                    'Call Duration', 'Group Name', 'Call Direction', 'Caller', 'Caller JID',
                    'Call Type')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        rows = _run(cursor, '''
        SELECT
            datetime(messages.timestamp/1000,'unixepoch'),
            CASE messages.received_timestamp WHEN 0 THEN ''
                ELSE datetime(messages.received_timestamp/1000,'unixepoch') END,
            messages.key_remote_jid,
            CASE WHEN contact_book_w_groups.recipients IS NULL THEN messages.key_remote_jid
                ELSE contact_book_w_groups.recipients END,
            CASE key_from_me WHEN 0 THEN "Incoming" WHEN 1 THEN "Outgoing" END,
            messages.data,
            CASE WHEN messages.remote_resource IS NULL THEN messages.key_remote_jid
                ELSE messages.remote_resource END,
            messages.media_url
        FROM (SELECT jid, recipients FROM wadb.wa_contacts AS contacts
            LEFT JOIN (SELECT gjid, group_concat(CASE WHEN jid == "" THEN NULL ELSE jid END) AS recipients
                FROM group_participants GROUP BY gjid) AS groups ON contacts.jid = groups.gjid
            GROUP BY jid) AS contact_book_w_groups
        JOIN messages ON messages.key_remote_jid = contact_book_w_groups.jid
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              row[5], row[6], row[7]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    'Message ID', 'Recipients', 'Direction', 'Message', 'Group Sender', 'Attachment')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_one_to_one_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        rows = _run(cursor, '''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            wa_contacts.wa_name,
            CASE WHEN message.from_me=0 THEN wa_contacts.jid ELSE "" END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            ''' + _MESSAGE_TYPE_CASE + ''',
            message.text_data,
            message_media.file_path,
            message_media.file_size,
            message_location.latitude,
            message_location.longitude,
            message_location.live_location_share_duration,
            message_location.live_location_final_latitude,
            message_location.live_location_final_longitude,
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch')
        FROM message
        JOIN chat ON chat._id=message.chat_row_id
        JOIN jid ON jid._id=chat.jid_row_id
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        LEFT JOIN message_location ON message_location.message_row_id=message._id
        JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
        WHERE message.recipient_count=0
        ORDER BY message.timestamp ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), _str_to_utc(row[14]),
                              row[4], row[2], row[6], _media(row[7]), row[3],
                              row[5], row[7], row[8], row[9], row[10], row[11],
                              row[12], row[13]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    ('Final Location Timestamp', 'datetime'), 'Message Direction',
                    'Other Participant WA User Name', 'Message', ('Media', 'media'),
                    'Sending Party JID', 'Message Type', 'Local Path To Media',
                    'Media File Size') + _LOCATION_HEADERS
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_group_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        rows = _run(cursor, '''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            chat.subject,
            CASE WHEN message.from_me=1 THEN "Self" ELSE wa_contacts.wa_name END,
            CASE WHEN message.from_me=0 THEN wa_contacts.jid ELSE "" END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            ''' + _MESSAGE_TYPE_CASE + ''',
            message.text_data,
            message_media.file_path,
            message_media.file_size,
            message_location.latitude,
            message_location.longitude,
            message_location.live_location_share_duration,
            message_location.live_location_final_latitude,
            message_location.live_location_final_longitude,
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch')
        FROM message
        JOIN chat ON chat._id=message.chat_row_id
        LEFT JOIN jid ON jid._id=message.sender_jid_row_id
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        LEFT JOIN message_location ON message_location.message_row_id=message._id
        LEFT JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
        WHERE message.recipient_count>=1
        ORDER BY message.timestamp ASC, message.rowid, chat.rowid, jid.rowid, message_media.rowid,
            message_location.rowid, wa_contacts.rowid
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), _str_to_utc(row[15]),
                              row[5], row[3], row[7], _media(row[8]), row[2], row[4],
                              row[6], row[8], row[9], row[10], row[11],
                              row[12], row[13], row[14]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    ('Final Location Timestamp', 'datetime'), 'Message Direction',
                    'Sending Party', 'Message', ('Media', 'media'), 'Conversation Name',
                    'Sending Party JID', 'Message Type', 'Local Path To Media',
                    'Media File Size') + _LOCATION_HEADERS
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_group_details(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        # The chat table, not chat_view: the view has no jid_row_id column on older schemas.
        # The creator columns come from wa.db and are NULL when it lacks creator_jid or is absent.
        creator = name = number = 'NULL'
        if _has_column(cursor, 'wadb', 'wa_group_admin_settings', 'creator_jid'):
            creator = ('''(SELECT creator_jid FROM wadb.wa_group_admin_settings
                WHERE wadb.wa_group_admin_settings.jid = jid.raw_string)''')
            name = f'(SELECT wa_name FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid = {creator})'
            number = f'(SELECT number FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid = {creator})'
        rows = _run(cursor, f'''
        SELECT
            datetime(chat.created_timestamp/1000,'unixepoch'),
            chat.subject,
            {creator},
            {name},
            {number}
        FROM chat
        JOIN jid ON jid._id = chat.jid_row_id
        WHERE chat.subject NOT NULL
        ORDER BY chat.created_timestamp ASC, chat._id
        ''')
        for row in rows:
            media = ''
            number = row[4]
            if number:
                avatar = number[1:] if number.startswith('+') else number
                media = _media(avatar + '.jpg')
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], media))
        db.close()

    data_headers = (('Group Creation Timestamp', 'datetime'), 'Group Name', 'Creator JID',
                    'Creator WA User Name', 'Creator WA Number',
                    ('Creator WA Profile Picture', 'media'))
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_user_profile(context):
    files_found = context.get_files_found()
    keys = ('push_name', 'my_current_status', 'version', 'ph', 'cc')
    data = {k: '' for k in keys}
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'com.whatsapp_preferences_light.xml' not in file_found and 'startup_prefs.xml' not in file_found:
            continue
        source = source or file_found
        try:
            with open(file_found, encoding='utf-8') as fd:
                xml_dict = xmltodict.parse(fd.read())
        except (OSError, ValueError):
            continue
        strings = (xml_dict.get('map') or {}).get('string') or []
        if isinstance(strings, dict):
            strings = [strings]
        for entry in strings:
            if not isinstance(entry, dict):
                continue
            name = entry.get('@name')
            if name in data and not data[name]:
                data[name] = entry.get('#text', '')

    data_list = []
    if any(data.values()):
        data_list.append((data['version'], data['push_name'], data['my_current_status'], data['cc'],
                          data['ph']))

    data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number')
    return data_headers, data_list, source
