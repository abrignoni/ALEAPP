__artifacts_v2__ = {
    "get_samsung_messages": {
        "name": "Samsung Messages",
        "description": "SMS and MMS messages from the Samsung Messages app database (message_content.db), "
                       "with MMS attachments shown on the message row",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "One row per message in the messages table of com.samsung.android.messaging/databases/"
                 "message_content.db, or one row per attachment part for a message with more than one. "
                 "Body is the text of the message's text/plain parts in part order; it was blank on MMS rows "
                 "that carried an image and no text part. Created Time and Sent Time are "
                 "messages.created_timestamp and sent_timestamp read as Unix milliseconds; Sent Time is "
                 "blank when the stored value is 0. On samsung_a166u_a16_known_20261116 created_timestamp "
                 "equalled sms.date of the joined provider row on 162 of 162 SMS rows. "
                 "Direction maps message_box_type 100, 101 and 102 to Received, Failed and Sent, and "
                 "Message Type maps message_type 10 and 12 to SMS and MMS. No Samsung source for these "
                 "values is cited. They are data-proven by a recorded join: remote_message_uri names the "
                 "telephony provider row (content://sms/<id> or content://mms/<id>), and on the six images "
                 "with SMS or MMS rows (galaxys10_a10, samsungs20_a13, sharon_a13, sharon_a14, "
                 "falken_a326u_a13, samsung_a166u_a16_known_20261116; 690 rows of type 10 or 12) every row "
                 "joined to a mmssms.db row, every 100 row to an inbox row (sms.type or pdu.msg_box 1), "
                 "every 102 row to a sent row (2), and the 2 rows holding 101 (one each on sharon_a14 and "
                 "falken_a326u_a13) to sms.type 5 (failed). Any other value is shown as stored. On "
                 "falken_a326u_a13, message_type 13 rows named content://im/chat/ or content://bin_im/ and "
                 "the message_type 14 row content://im/ft/, URIs of the RCS provider rather than mmssms.db; "
                 "those 24 rows are shown with their stored type, and 23 of them carried text that the SMS "
                 "and MMS artifacts do not report. "
                 "Address is messages.recipients, or the addresses of the conversation's recipients when "
                 "that column is empty; Contact Name is the recipients.cache_name the app cached for the "
                 "conversation (the column is absent on the Android 10 image). Creator (as stored) is "
                 "messages.creator. On the known-data image it held tpsync on the 165 rows that were "
                 "already in the telephony provider when Samsung Messages was installed and made the "
                 "default SMS app, and was empty on the 3 messages sent from Samsung Messages itself; what "
                 "tpsync stands for is not established, and a row here does not by itself show that the "
                 "message was sent or read in Samsung Messages. Creator (as stored) had no value on any row of "
                 "falken_a326u_a13, sharon_a13 and sharon_a14, and held tpsync on 13 of 32 rows of "
                 "galaxys10_a10 and 32 of 41 of samsungs20_a13. Read is messages.is_read as stored. Read held "
                 "1 on all 40 rows of falken_a326u_a13. "
                 "Media renders the attachment file the part's _data column records, matched on that "
                 "recorded path (storage class, Android user, package and file name) to "
                 "com.android.providers.telephony/app_parts, never on the file name alone; every MMS "
                 "attachment part with a _data path resolved on the images listed (24 of 24). An RCS file "
                 "part records a content://im/ft_original/ URI and no _data path, so it keeps Attachment "
                 "Name and a blank Media. "
                 "Flags lists the messages columns is_spam, is_bin, is_locked, is_favorite, is_hidden and "
                 "is_secret that are not 0, with bin_timestamp and scheduled_timestamp when set. Flags had no "
                 "value on any of the 168 rows of the known-data image or the 325 of sharon_a14. On the "
                 "eleven images checked Flags held a value on 2 rows, both on falken_a326u_a13: one RCS "
                 "row with is_bin and its bin_timestamp, and one with is_hidden. What Samsung Messages does "
                 "when is_hidden is set is not established. The spam, locked, favorite, secret and scheduled "
                 "paths are code-present but unexercised. "
                 "Not reported: message_status (no source), delivered_timestamp and sim_slot (0 on every "
                 "row of the known-data image), the conversations table beyond its recipients (name and "
                 "from_address were empty on all 10 rows of the known-data image), the RCS sessions and bot "
                 "tables (sessions, bots, bot_menus, bot_related_bots, bot_service_id_sms_number), cmas "
                 "(emergency alerts; 0 rows on the known-data image), block_filter and mcs_block_sync "
                 "(block rules; 0 rows on the known-data image), suggestions and "
                 "suggest_conversation_categories, plugin and sim_imsi (app configuration), with_app.db "
                 "(quick reply templates and per-SIM settings) and messageservice.db (service requests). "
                 "The DE-storage copy under user_de held the schema and no messages on every image, and on "
                 "the known-data image in all 7 states of its write-ahead log. The image, thumbnail and "
                 "avatar caches under cache/ record no link to a message and are not reported.",
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
                "directionSentValue": "Sent",
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
            _BOX.get(msg['message_box_type'], msg['message_box_type']),
            msg['recipients'] or ', '.join(addresses.get(conv, [])),
            body,
        )
        contact = ', '.join(names.get(conv, []))
        tail = (
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
        ('Media', 'media'), 'Contact Name', 'Attachment Name', 'Message Type', 'Read', 'Creator (as stored)',
        'Flags', 'Conversation ID', 'Message ID', 'Provider URI',
    )
    return data_headers, data_list, '\n'.join(source_paths)
