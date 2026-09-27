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
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "A chat keyed by a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. Messages whose chat matches no contact are still reported. When no contact matches, or the contact has no WhatsApp name, the participant is shown by jid. Messages in channel (newsletter) chats are not reported here; WhatsApp - Channel Messages reports them.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 31 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 29 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 29 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 154 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 73 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 491 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 71 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 14 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 435 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 788 rows",
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
        "last_update_date": "2026-09-26",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "A sender keyed by a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. A sender that matches no contact, or has no WhatsApp name, is shown by jid.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 39 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 39 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 156 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 76 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 2383 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 4730 rows",
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
        "description": "WhatsApp group details (modern msgstore.db schema)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Channel (newsletter) chats also carry a subject in msgstore.db and are not reported here; WhatsApp - Channels reports them.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*',
                  '*/com.whatsapp/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
        },
    },
    "get_whatsapp_channels": {
        "name": "WhatsApp - Channels",
        "description": "WhatsApp channels with a row in msgstore.db's newsletter table",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-27",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Reads msgstore.db's newsletter table, one row per channel, joined to the channel's chat. Local Chat Created Timestamp is chat.created_timestamp. On the three tested images holding channels (kevin_pocox7_a15, russell_a14, samsungs20_a13; 18 channels), each channel's earliest stored message was one of two system messages with from_me=1 (message_system action_type 132 and 134) carrying that same millisecond value, and no message in the channel was older. What those two system messages record, and whether the timestamp marks when the channel was followed, was not established. Verified (as stored), Membership (as stored) and Muted (as stored) are the newsletter table's integers, reported without an interpretation. Membership (as stored) and Muted (as stored) each held the same value, 1, on all 18 channels. Verified (as stored) held 1 on 15 channels and 0 on 3, and held the same value, 1, on all 3 channels of samsungs20_a13. Subscriber Count is newsletter.subscribers_count as stored. Messages Stored counts the chat's rows in the message table. Newsletter chats with no newsletter row are not reported: pixel7a_a14 and sharon_a14 each hold 20, with no name, no timestamps and no messages. wa.db lists newsletter jids for channels absent from this table (275 newsletter jids on kevin_pocox7_a15 against its 10 channels), so a newsletter jid in wa.db does not show that the channel was followed. wa.db's wa_newsletter_props, whose property names are keyed by a numeric id or a two-letter code, is not reported. Only the first msgstore.db matched is read, as in the module's other artifacts.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*',),
        "output_types": "standard",
        "artifact_icon": "broadcast",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 10 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 5 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 3 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
        },
    },
    "get_whatsapp_channel_messages": {
        "name": "WhatsApp - Channel Messages",
        "description": "Messages stored in WhatsApp channel (newsletter) chats",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-27",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Every message in a channel (newsletter) chat in msgstore.db. Channel Name comes from the newsletter table, falling back to the chat subject and then the jid. On the three tested images holding channel messages (kevin_pocox7_a15, russell_a14, samsungs20_a13; 5,217 rows), sender_jid_row_id was 0 on every message, so msgstore.db records no author and the channel is shown as the sender. Message Direction is from_me as stored: the 36 Outgoing rows on those images were all system messages (message_type 7, message_system action_type 132 or 134), two per channel, carrying the channel chat's created timestamp; what they record was not established. Message Type values the module does not name are reported as stored. Server Message ID is newsletter_message.server_message_id and is blank on the 106 rows with no newsletter_message row; newsletter_message rows with no message row (one on each of the three images) are not reported. Reaction From Me is newsletter_message.reaction_from_me and held no value on any tested image. Of the 2,276 channel messages with a message_media row, 29 recorded a local file path, all on kevin_pocox7_a15, and all 29 render in Media; the others record no local file. Media and Local Path To Media held no value on any row of russell_a14 or samsungs20_a13. Reaction totals from other followers (newsletter_message_reaction) and the channel message search index (the message_newsletter_fts tables) are not reported. Only the first msgstore.db matched is read, as in the module's other artifacts.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 3731 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 1291 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 195 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Channel Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
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

from scripts.ilapfuncs import artifact_processor, attach_sqlite_db_readonly, open_sqlite_db_readonly, check_in_media

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
    except sqlite3.Error:
        return []


def _has_table(cursor, name):
    try:
        cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False


def _contact_jid(cursor, jid_alias):
    """Return (joins, expression) giving the jid to match wa_contacts.jid against.

    Newer msgstore.db files can key a 1:1 chat or a group sender by a LID jid
    (``...@lid``), while wa_contacts.jid holds the ``...@s.whatsapp.net`` form.
    msgstore.db's jid_map table links the two jid rows (lid_row_id -> jid_row_id).
    When jid_map is absent (older databases) the jid's own raw_string is used.
    """
    if not _has_table(cursor, 'jid_map'):
        return '', f'{jid_alias}.raw_string'
    joins = f'''LEFT JOIN jid_map ON jid_map.lid_row_id={jid_alias}._id
        LEFT JOIN jid AS mapped_jid ON mapped_jid._id=jid_map.jid_row_id'''
    return joins, f'COALESCE(mapped_jid.raw_string, {jid_alias}.raw_string)'


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
        lid_joins, contact_jid = _contact_jid(cursor, 'jid')
        rows = _run(cursor, f'''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            COALESCE(NULLIF(wa_contacts.wa_name, ''), {contact_jid}),
            CASE WHEN message.from_me=0 THEN COALESCE(wa_contacts.jid, {contact_jid}) ELSE "" END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            ''' + _MESSAGE_TYPE_CASE + f''',
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
        {lid_joins}
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        LEFT JOIN message_location ON message_location.message_row_id=message._id
        LEFT JOIN wa_contacts ON wa_contacts.jid={contact_jid}
        WHERE message.recipient_count=0
            AND COALESCE(jid.raw_string, '') NOT LIKE '%@newsletter'
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
        lid_joins, contact_jid = _contact_jid(cursor, 'jid')
        rows = _run(cursor, f'''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            chat.subject,
            CASE WHEN message.from_me=1 THEN "Self" ELSE COALESCE(NULLIF(wa_contacts.wa_name, ''), {contact_jid}) END,
            CASE WHEN message.from_me=0 THEN COALESCE(wa_contacts.jid, {contact_jid}) ELSE "" END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            ''' + _MESSAGE_TYPE_CASE + f''',
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
        {lid_joins}
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        LEFT JOIN message_location ON message_location.message_row_id=message._id
        LEFT JOIN wa_contacts ON wa_contacts.jid={contact_jid}
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
            AND COALESCE(jid.raw_string, '') NOT LIKE '%@newsletter'
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


def _newsletter_joins(cursor):
    """Return (joins, channel name expression), tolerating an absent newsletter table."""
    if not _has_table(cursor, 'newsletter'):
        return '', 'NULL'
    return ('\n        LEFT JOIN newsletter ON newsletter.chat_row_id=chat._id',
            "NULLIF(newsletter.name, '')")


@artifact_processor
def get_whatsapp_channels(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        if _has_table(cursor, 'newsletter'):
            rows = _run(cursor, '''
            SELECT
                CASE WHEN COALESCE(chat.created_timestamp, 0) = 0 THEN ''
                    ELSE datetime(chat.created_timestamp/1000,'unixepoch') END,
                COALESCE(NULLIF(newsletter.name, ''), NULLIF(chat.subject, ''), jid.raw_string),
                jid.raw_string,
                newsletter.description,
                newsletter.invite_code,
                newsletter.verified,
                newsletter.membership,
                newsletter.muted,
                newsletter.subscribers_count,
                (SELECT COUNT(*) FROM message WHERE message.chat_row_id=chat._id)
            FROM newsletter
            JOIN chat ON chat._id=newsletter.chat_row_id
            JOIN jid ON jid._id=chat.jid_row_id
            ORDER BY chat.created_timestamp ASC
            ''')
            for row in rows:
                data_list.append((_str_to_utc(row[0]),) + tuple(row[1:]))
        db.close()

    data_headers = (('Local Chat Created Timestamp', 'datetime'), 'Channel Name', 'Channel JID',
                    'Description', 'Invite Code', 'Verified (as stored)', 'Membership (as stored)',
                    'Muted (as stored)', 'Subscriber Count', 'Messages Stored')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_channel_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        joins, name = _newsletter_joins(cursor)
        server_id, reaction = "''", "''"
        if _has_table(cursor, 'newsletter_message'):
            joins += '\n        LEFT JOIN newsletter_message ON newsletter_message.message_row_id=message._id'
            server_id = 'newsletter_message.server_message_id'
            reaction = 'newsletter_message.reaction_from_me'
        rows = _run(cursor, f'''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            COALESCE({name}, NULLIF(chat.subject, ''), jid.raw_string),
            message.text_data,
            message_media.file_path,
            ''' + _MESSAGE_TYPE_CASE + f''',
            jid.raw_string,
            {server_id},
            {reaction},
            message_media.file_size
        FROM message
        JOIN chat ON chat._id=message.chat_row_id
        JOIN jid ON jid._id=chat.jid_row_id{joins}
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        WHERE jid.raw_string LIKE '%@newsletter'
        ORDER BY message.timestamp ASC, message._id ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              _media(row[5]), row[6], row[7], row[8], row[9], row[5], row[10]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    'Message Direction', 'Channel Name', 'Message', ('Media', 'media'),
                    'Message Type', 'Channel JID', 'Server Message ID', 'Reaction From Me',
                    'Local Path To Media', 'Media File Size')
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
