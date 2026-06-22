# pylint: disable=W0613
__artifacts_v2__ = {
    "get_whatsapp_contacts": {
        "name": "WhatsApp - Contacts",
        "description": "WhatsApp contacts (wa.db)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/wa.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_whatsapp_call_logs": {
        "name": "WhatsApp - Call Logs",
        "description": "WhatsApp call logs (msgstore.db)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
    },
    "get_whatsapp_messages": {
        "name": "WhatsApp - Messages",
        "description": "WhatsApp messages (legacy msgstore.db schema with messages.data)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Legacy schema only; modern databases are covered by the One To One / Group Messages artifacts.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_whatsapp_one_to_one_messages": {
        "name": "WhatsApp - One To One Messages",
        "description": "WhatsApp 1:1 messages (modern msgstore.db schema)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*',
                  '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*',
                  '*/Android/media/com.whatsapp/WhatsApp/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_whatsapp_group_messages": {
        "name": "WhatsApp - Group Messages",
        "description": "WhatsApp group messages (modern msgstore.db schema)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*',
                  '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*',
                  '*/Android/media/com.whatsapp/WhatsApp/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_whatsapp_group_details": {
        "name": "WhatsApp - Group Details",
        "description": "WhatsApp group details (modern msgstore.db schema)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*',
                  '*/com.whatsapp/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_whatsapp_user_profile": {
        "name": "WhatsApp - User Profile",
        "description": "WhatsApp local user profile (shared_prefs xml)",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml',
                  '*/com.whatsapp/shared_prefs/startup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
    }
}

import datetime
import os
import sqlite3

import xmltodict

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media

# Re-used location columns shared by the one-to-one and group message queries.
_LOCATION_HEADERS = ('Shared Latitude/Starting Latitude (Live Location)',
                     'Shared Longitude/Starting Longitude (Live Location)',
                     'Duration Live Location Shared (Seconds)', 'Final Live Latitude',
                     'Final Live Longitude', ('Final Location Timestamp', 'datetime'))

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
            cursor.execute('attach database "%s" as wadb' % wa)
        except sqlite3.Error:
            pass
    return db, cursor, msg, wa


def _run(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


@artifact_processor
def get_whatsapp_contacts(files_found, report_folder, seeker, wrap_text):
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
def get_whatsapp_call_logs(files_found, report_folder, seeker, wrap_text):
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
def get_whatsapp_messages(files_found, report_folder, seeker, wrap_text):
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
def get_whatsapp_one_to_one_messages(files_found, report_folder, seeker, wrap_text):
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
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              row[5], row[6], _media(row[7]), row[7], row[8], row[9], row[10], row[11],
                              row[12], row[13], _str_to_utc(row[14])))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    'Other Participant WA User Name', 'Sending Party JID', 'Message Direction',
                    'Message Type', 'Message', ('Media', 'media'), 'Local Path To Media',
                    'Media File Size') + _LOCATION_HEADERS
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_group_messages(files_found, report_folder, seeker, wrap_text):
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
        ORDER BY message.timestamp ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              row[5], row[6], row[7], _media(row[8]), row[8], row[9], row[10], row[11],
                              row[12], row[13], row[14], _str_to_utc(row[15])))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    'Conversation Name', 'Sending Party', 'Sending Party JID', 'Message Direction',
                    'Message Type', 'Message', ('Media', 'media'), 'Local Path To Media',
                    'Media File Size') + _LOCATION_HEADERS
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_group_details(files_found, report_folder, seeker, wrap_text):
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        rows = _run(cursor, '''
        SELECT
            datetime(chat_view.created_timestamp/1000,'unixepoch'),
            chat_view.subject,
            (SELECT creator_jid FROM wadb.wa_group_admin_settings
                WHERE wadb.wa_group_admin_settings.jid = jid.raw_string),
            (SELECT wa_name FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid =
                (SELECT creator_jid FROM wadb.wa_group_admin_settings
                    WHERE wadb.wa_group_admin_settings.jid = jid.raw_string)),
            (SELECT number FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid =
                (SELECT creator_jid FROM wadb.wa_group_admin_settings
                    WHERE wadb.wa_group_admin_settings.jid = jid.raw_string))
        FROM chat_view
        JOIN jid ON jid._id = chat_view.jid_row_id
        LEFT JOIN wa_group_admin_settings ON wa_group_admin_settings.jid=chat_view.jid_row_id
        LEFT JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
        WHERE chat_view.subject NOT NULL
        ORDER BY chat_view.created_timestamp ASC
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
def get_whatsapp_user_profile(files_found, report_folder, seeker, wrap_text):
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
