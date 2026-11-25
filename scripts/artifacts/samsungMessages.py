__artifacts_v2__ = {
    "get_samsung_messages": {
        "name": "Samsung Messages",
        "description": "Messages from the Samsung Messages app database (message_content.db): SMS, MMS "
                       "and any other stored message type, with MMS attachments shown on the message row",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per message in the messages table of com.samsung.android.messaging/databases/"
                 "message_content.db, or one row per attachment part for a message with more than one; no "
                 "message with more than one attachment part was present on the images checked, so that "
                 "path is code-present but unexercised. Body is the text of the message's text/ parts in "
                 "part order (only text/plain was present on the images checked); it was blank on MMS rows "
                 "that carried an image and no text part. Created Time and Sent Time are "
                 "messages.created_timestamp and sent_timestamp read as Unix milliseconds; Sent Time is "
                 "blank when the stored value is 0 or not a positive integer. On the six images with SMS or "
                 "MMS rows (100 of the sharon_a13 rows are also in sharon_a14, with the same message id, "
                 "created time and provider URI, and are counted once here) created_timestamp equalled "
                 "sms.date on 561 of 561 SMS rows and pdu.date times 1000 on 29 of 29 MMS rows, and "
                 "sent_timestamp equalled sms.date_sent on 561 of 561 SMS rows; sent_timestamp was 0 on "
                 "every Sent and Failed SMS and MMS row (180), so Sent Time is blank there, and set on "
                 "every Received one (410). "
                 "Box maps message_box_type 100, 101 and 102 to Received, Failed and Sent, Direction maps "
                 "100 to Incoming and 101 and 102 to Outgoing, and Message Type maps message_type 10 and 12 "
                 "to SMS and MMS; any other value is shown as stored. No Samsung source for these values is "
                 "cited. They are data-proven by a recorded join: remote_message_uri names the telephony "
                 "provider row (content://sms/<id> or content://mms/<id>), and on the six images with SMS or "
                 "MMS rows (galaxys10_a10, samsungs20_a13, sharon_a13, sharon_a14, falken_a326u_a13, "
                 "samsung_a166u_a16_known_20261116; 590 distinct rows of type 10 or 12) every row joined to "
                 "a mmssms.db row, every 100 row (410) to sms.type or pdu.msg_box 1, every 102 row (178) to "
                 "2, "
                 "and the 2 rows holding 101 (one each on sharon_a14 and falken_a326u_a13) to sms.type 5. "
                 "AOSP defines those values as inbox (1), sent (2) and failed outgoing message (5) for SMS, "
                 "and inbox, sent and failed message boxes for MMS (https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/Telephony.java#L139-L157, https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/Telephony.java#L1477-L1487). The "
                 "same Box and Direction labels are applied to rows of other message types (24 on "
                 "falken_a326u_a13, 2 of them 101), where no provider join supports them. On "
                 "falken_a326u_a13, 22 of the 23 message_type 13 rows named content://im/chat/ (21) or "
                 "content://bin_im/ (1) and one had no URI, and the message_type 14 row named "
                 "content://im/ft/: URIs outside the sms and mms authorities. What message_type 13 and 14 "
                 "denote is not established; the URI names suggest RCS chat and file transfer. Those 24 "
                 "rows are shown with their stored type, and 23 of them carried text that mmssms.db did not "
                 "hold (0 of 23 matched an sms body), so artifacts that read only mmssms.db do not show it. "
                 "Address is messages.recipients, or the addresses of the conversation's recipients when "
                 "that column is empty (8 rows: 7 sent MMS rows and one message_type 13 row holding 101); no conversation with more than one "
                 "recipient was present on the images checked. Contact Name is the recipients.cache_name "
                 "the app cached for the conversation (the column is absent on the Android 10 image). "
                 "Creator (as stored) is messages.creator. On the known-data image it held tpsync on the "
                 "165 rows that were already in the telephony provider when Samsung Messages was installed "
                 "and made the default SMS app, and was empty on the 3 messages sent from Samsung Messages "
                 "itself; what tpsync stands for is not established, and a row here does not by itself show "
                 "that the message was sent or read in Samsung Messages. Creator (as stored) had no value "
                 "on any row of falken_a326u_a13, sharon_a13 and sharon_a14, and held tpsync on 13 of 32 "
                 "rows of galaxys10_a10 and 32 of 41 of samsungs20_a13. Read is messages.is_read as stored. "
                 "Read held 1 on all 40 rows of falken_a326u_a13. Message Type held SMS on all 32 rows of "
                 "galaxys10_a10. "
                 "Media renders the attachment file the part's _data column records, matched on that "
                 "recorded path (storage class, Android user, package and file name) to "
                 "com.android.providers.telephony/app_parts, never on the file name alone. Every MMS "
                 "attachment part with a _data path resolved: 6 on samsung_a166u_a16_known_20261116, 1 on "
                 "sharon_a13 and 17 on sharon_a14 (24 of 24; the sharon_a13 part is also one of the 17). The "
                 "one message_type 14 part "
                 "(falken_a326u_a13) recorded a content://im/ft_original/ URI and no _data path; its row "
                 "has an Attachment Name and a blank Media. "
                 "Flags lists the messages columns is_spam, is_bin, is_locked, is_favorite, is_hidden and "
                 "is_secret that are not 0, with bin_timestamp and scheduled_timestamp when set, read as "
                 "Unix milliseconds (one bin_timestamp value seen; the unit is not sourced). Flags had no "
                 "value on any of the 168 rows of the known-data image or the 325 of sharon_a14. On the "
                 "eleven images checked Flags held a value on 2 rows, both message_type 13 rows on "
                 "falken_a326u_a13: one with is_bin and its bin_timestamp, and one with is_hidden. What "
                 "Samsung Messages does when is_hidden is set is not established. The spam, locked, "
                 "favorite, secret and scheduled paths are code-present but unexercised. "
                 "Not reported: messages.subject (empty on the known-data image), message_status (no "
                 "source), delivered_timestamp and sim_slot (0 on every row of the known-data image), the "
                 "conversations table beyond its recipients (name and from_address were empty on all 10 "
                 "rows of the known-data image), the sessions and bot tables (sessions, bots, bot_menus, "
                 "bot_related_bots, bot_service_id_sms_number; sessions held 2 rows on falken_a326u_a13), "
                 "cmas, block_filter and mcs_block_sync (0 rows on the known-data image), suggestions, "
                 "suggest_conversation_categories (rows on falken_a326u_a13 and samsungs20_a13), "
                 "categories, conversation_categories, cmc_commands, mms_addr, my_channels, plugin (18 "
                 "rows on the known-data image) and sim_imsi, with_app.db (tables quick_responses, "
                 "user_setting_by_sim, recent_search and recent_search_bot; recent_search held 0 rows on "
                 "every image checked), messageservice.db (one table, request_details, holding a "
                 "transaction id and a package name), useful_cards.db (0 rows in every table but "
                 "android_metadata on the four images that have it) and scpm.db under user_de on "
                 "galaxys10_a10 (tables cmas_channel and scpm_version). The DE-storage copy under user_de held the schema and no messages "
                 "on each of the eleven images; on the known-data image none of the 7 committed states of "
                 "its write-ahead log held a message (3 of them predate the messages table). The image and "
                 "avatar caches under cache/ are keyed by hex digests; no message id or URI was readable in "
                 "their journals on the known-data image, and they are not reported.",
        "paths": (
            '*/com.samsung.android.messaging/databases/message_content.db*',
            '*/com.android.providers.telephony/app_parts/*',
        ),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.messaging vc 1579500101 | 168 rows",
            "adams_ss135dl_a13": "Android 13 | com.samsung.android.messaging | 0 rows",
            "anne_a15": "Android 15 | com.samsung.android.messaging | 0 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.messaging (DE copy only) | 0 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.messaging | 40 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.messaging | 32 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.messaging | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.messaging | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.messaging | 41 rows",
            "sharon_a13": "Android 13 | com.samsung.android.messaging | 108 rows",
            "sharon_a14": "Android 14 | com.samsung.android.messaging | 325 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Body",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Created Time",
                "senderColumn": "Address",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_BOX = {100: 'Received', 101: 'Failed', 102: 'Sent'}
_DIRECTION = {100: 'Incoming', 101: 'Outgoing', 102: 'Outgoing'}
_TYPE = {10: 'SMS', 12: 'MMS'}
_FLAG_COLUMNS = ('is_spam', 'is_bin', 'is_locked', 'is_favorite', 'is_hidden', 'is_secret')

_MESSAGE_COLUMNS = ('_id', 'conversation_id', 'message_type', 'message_box_type', 'recipients',
                    'created_timestamp', 'sent_timestamp', 'is_read', 'creator', 'remote_message_uri',
                    'bin_timestamp', 'scheduled_timestamp') + _FLAG_COLUMNS
_PART_COLUMNS = ('_id', 'message_id', 'text', 'content_type', 'file_name', '_data')


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _storage_key(relative_path):
    """Storage class, Android user and in-package path of a file, or None."""
    key, _rank = canonical_path(relative_path)
    if '\x00' not in key:
        return None
    return key.split('\x00', 1)[1]


def _part_files(context, files_found):
    """Map the storage key of each telephony app_parts file to its staged path."""
    by_key = {}
    for file_found in files_found:
        file_found = str(file_found)
        parent = file_found.replace('\\', '/').rsplit('/', 2)
        if len(parent) < 3 or parent[-2] != 'app_parts' or os.path.isdir(file_found):
            continue
        key = _storage_key(context.get_relative_path(file_found))
        if key is not None:
            by_key.setdefault(key, file_found)
    return by_key


def _select(db, table, wanted, order_by):
    """Rows of table with every wanted column, NULL where this schema version lacks one."""
    present = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    columns = ', '.join(f'"{name}"' if name in present else f'NULL AS "{name}"' for name in wanted)
    order = ', '.join(name for name in order_by if name in present) or 'rowid'
    return db.execute(f'SELECT {columns} FROM "{table}" ORDER BY {order}').fetchall()


def _aux(db_path, label, read):
    """Run one auxiliary read; a failure costs that field, not the messages."""
    try:
        return read()
    except sqlite3.Error as ex:
        logfunc(f'Samsung Messages: {label} not read from {db_path}: {ex}')
        return None


def _flags(row):
    flags = [name for name in _FLAG_COLUMNS if row[name] not in (None, 0)]
    for name in ('bin_timestamp', 'scheduled_timestamp'):
        when = _ms_to_utc(row[name])
        if when:
            flags.append(f'{name}={when.isoformat()}')
    return '; '.join(flags)


def _read_db(db_path, part_files):
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return []
    db.row_factory = sqlite3.Row
    rows = []
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'messages' not in tables:
            return []
        messages = _select(db, 'messages', _MESSAGE_COLUMNS, ('created_timestamp', '_id'))
    except sqlite3.Error as ex:
        logfunc(f'Samsung Messages: could not read {db_path}: {ex}')
        db.close()
        return []

    parts = {}
    if 'parts' in tables:
        for part in _aux(db_path, 'parts', lambda: _select(db, 'parts', _PART_COLUMNS, ('message_id', '_id'))) or []:
            parts.setdefault(part['message_id'], []).append(part)

    addresses, names = {}, {}
    if 'conversation_recipients' in tables and 'recipients' in tables:
        links = _aux(db_path, 'conversation_recipients', lambda: _select(
            db, 'conversation_recipients', ('conversation_id', 'recipient_id'), ('conversation_id', '_id'))) or []
        recipients = {r['_id']: r for r in _aux(db_path, 'recipients', lambda: _select(
            db, 'recipients', ('_id', 'address', 'cache_name'), ('_id',))) or []}
        for link in links:
            rec = recipients.get(link['recipient_id'])
            if rec is None:
                continue
            if rec['address']:
                addresses.setdefault(link['conversation_id'], []).append(rec['address'])
            if rec['cache_name']:
                names.setdefault(link['conversation_id'], []).append(rec['cache_name'])
    db.close()

    for msg in messages:
        msg_parts = parts.get(msg['_id'], [])
        body = '\n'.join(p['text'] for p in msg_parts
                         if (p['content_type'] or '').startswith('text/') and p['text'])
        attachments = [p for p in msg_parts if not (p['content_type'] or '').startswith('text/')]
        conv = msg['conversation_id']
        common = (
            _ms_to_utc(msg['created_timestamp']),
            _ms_to_utc(msg['sent_timestamp']),
            _DIRECTION.get(msg['message_box_type'], msg['message_box_type']),
            msg['recipients'] or ', '.join(addresses.get(conv, [])),
            body,
        )
        contact = ', '.join(names.get(conv, []))
        tail = (
            _BOX.get(msg['message_box_type'], msg['message_box_type']),
            _TYPE.get(msg['message_type'], msg['message_type']),
            msg['is_read'],
            msg['creator'] or '',
            _flags(msg),
            conv,
            msg['_id'],
            msg['remote_message_uri'] or '',
        )
        if not attachments:
            rows.append(common + ('', contact, '') + tail)
            continue
        for part in attachments:
            media_ref = ''
            data_path = part['_data']
            if data_path:
                key = _storage_key(str(data_path).replace('\\', '/').lstrip('/'))
                match = part_files.get(key) if key is not None else None
                if match:
                    media_ref = check_in_media(match, part['file_name'] or os.path.basename(str(data_path))) or ''
            rows.append(common + (media_ref, contact, part['file_name'] or '') + tail)
    return rows


@artifact_processor
def get_samsung_messages(context):
    files_found = unique_files(context)
    part_files = _part_files(context, files_found)
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('message_content.db') or os.path.isdir(file_found):
            continue
        source_paths.append(file_found)
        data_list.extend(_read_db(file_found, part_files))

    data_headers = (
        ('Created Time', 'datetime'), ('Sent Time', 'datetime'), 'Direction', 'Address', 'Body',
        ('Media', 'media'), 'Contact Name', 'Attachment Name', 'Box', 'Message Type', 'Read', 'Creator (as stored)',
        'Flags', 'Conversation ID', 'Message ID', 'Provider URI',
    )
    return data_headers, data_list, '\n'.join(source_paths)
