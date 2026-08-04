__artifacts_v2__ = {
    "get_telegramMessages": {
        "name": "Telegram - Messages",
        "description": (
            "Parses Telegram messages from the cache4.db messages_v2 table. Message text is "
            "decoded from the TL-serialised message blob stored in the data column; the "
            "timestamp, direction and read state are read from the table's own columns. "
            "Messages whose blob uses a message constructor this parser does not cover are "
            "still reported, with the text column left empty."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The data column holds a TL-serialised TLRPC message object. The message "
                 "constructors and their field order are taken from the open-source Telegram "
                 "Android client; constructors from layer 179 onward read a second flags "
                 "integer before the message id, which this parser accounts for. Messages "
                 "carrying a forward or reply header nest further optional objects that this "
                 "parser does not implement, so for those the text is located by searching "
                 "the blob for the row's own date value, which sits immediately before the "
                 "text, and reading the string that follows it; the candidate is accepted "
                 "only when it is a well-formed TL string that decodes as strict UTF-8, and "
                 "is otherwise reported as not recovered rather than guessed at. Service "
                 "(system event) messages use a different constructor and are reported as "
                 "'[Service message]' without an action label, because the action "
                 "constructors were not verified against the client source. Reference: "
                 "Telegram-Android, 'TL_legacy_message.java (TL_message layer constructors)', "
                 "https://github.com/DrKLO/Telegram/blob/master/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
    "get_telegramContacts": {
        "name": "Telegram - Contacts",
        "description": (
            "Parses the device contacts Telegram imported, from the user_contacts_v7 and "
            "user_phones_v7 tables of cache4.db, including the first and last name as stored "
            "on the device and the phone numbers recorded for that contact key."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Both tables store their values as plain text. They are joined on the key "
                 "column, which is the device address-book identifier Telegram used for the "
                 "import, so one contact can carry several phone numbers. The uid column "
                 "links the imported contact to a Telegram user in the users table.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "address-book",
    },
    "get_telegramUsers": {
        "name": "Telegram - Users",
        "description": (
            "Parses the Telegram users cached in the users table of cache4.db, including the "
            "display name, username and last-seen status. Telegram caches a user record when "
            "it encounters the account, so a user can appear here without any exchanged "
            "messages."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The name column stores the display name and username separated by ';;;'. "
                 "The status column holds the last-seen time as a Unix timestamp when it is "
                 "positive; the client also stores small negative values that encode a "
                 "hidden or bucketed last-seen state rather than a time, so only positive "
                 "values are reported as a timestamp and the raw value is kept alongside.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_telegramChats": {
        "name": "Telegram - Chats",
        "description": (
            "Parses the Telegram chat list from the dialogs table of cache4.db, including the "
            "resolved chat name, the time of the last activity, unread counts and whether the "
            "chat is pinned or filed in the archive folder."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The did column is the dialog peer id, resolved against the users and chats "
                 "tables for a name. A folder_id of 1 is the Archived chat list. The message "
                 "count is taken from the messages_v2 rows carrying the same dialog id.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "messages",
    },
    "get_telegramAutoDownload": {
        "name": "Telegram - Auto-Download Settings",
        "description": (
            "Parses the Telegram media auto-download configuration from the mainconfig.xml "
            "shared preferences file. Reports, for each network type, whether auto-download "
            "is enabled, which media types are downloaded automatically for each category of "
            "chat, and the per-media size limits."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Each preset is an underscore-separated string. The first four values are "
                 "auto-download masks for contacts, other private chats, groups and channels "
                 "in that order, and each mask is a bit field of photo 1, audio 2, video 4 "
                 "and document 8. The next four values are the photo, video, document and "
                 "audio size limits in bytes, followed by preload video, preload music and "
                 "the enabled flag. Reference: Telegram-Android, 'DownloadController.java "
                 "(Preset string layout and AUTODOWNLOAD_TYPE masks)', "
                 "https://github.com/DrKLO/Telegram/blob/master/TMessagesProj/src/main/java/"
                 "org/telegram/messenger/DownloadController.java",
        "paths": ('*/org.telegram.messenger*/shared_prefs/mainconfig.xml',),
        "output_types": "standard",
        "artifact_icon": "download",
    },
}

import io
import struct
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, convert_unix_ts_to_utc, \
    get_sqlite_db_records, get_file_path


# --- TL deserialisation ------------------------------------------------------
# Telegram stores message objects in the data column using the TL wire format:
# a 4-byte little-endian constructor id followed by the object's fields.

_PEER_USER = 0x59511722
_PEER_CHAT = 0x36C6019A
_PEER_CHANNEL = 0xA2A5371E

# TL_message constructors that read a second flags integer before the id.
# TL_legacy_message.java, classes TL_message_layer179 and newer.
_MSG_WITH_FLAGS2 = {
    0x95EF6F2B, 0x3AE56482, 0x9CB490E9, 0xB92F76CF, 0x9815CEC8,
    0xEABCDD4D, 0x96FDBBE9, 0x94345242, 0xBDE09C2E, 0x2357BF25,
}
# TL_message constructors without the second flags integer.
_MSG_NO_FLAGS2 = {
    0xA66C7EFC, 0x1E4C8A69, 0x76BEC211, 0x38116EE0, 0x85D6CBE2,
    0xBCE383D2, 0x58AE39C9, 0xF52E6B7F,
}
_MSG_ALL = _MSG_WITH_FLAGS2 | _MSG_NO_FLAGS2

# Service (system event) message constructors seen in the wild. Their action
# payload is not decoded, so they are reported without an action label.
_MSG_SERVICE = {0x2B085862, 0x7A800E0A, 0x286FA604}


class _TLReader:
    """Minimal reader for the TL wire format."""

    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def read_int32(self):
        return struct.unpack('<i', self.stream.read(4))[0]

    def read_uint32(self):
        return struct.unpack('<I', self.stream.read(4))[0]

    def read_int64(self):
        return struct.unpack('<q', self.stream.read(8))[0]

    def read_string(self):
        length = self.stream.read(1)[0]
        if length < 254:
            data = self.stream.read(length)
            consumed = length + 1
        else:
            length = int.from_bytes(self.stream.read(3), 'little')
            data = self.stream.read(length)
            consumed = length + 4
        self.stream.read((4 - consumed % 4) % 4)   # TL pads to a 4-byte boundary
        return data.decode('utf-8', 'replace')

    def read_peer(self):
        constructor = self.read_uint32()
        if constructor in (_PEER_USER, _PEER_CHAT, _PEER_CHANNEL):
            return self.read_int64()
        raise ValueError(f'unexpected peer constructor {constructor:#x}')


def _text_after_date(blob, start, date):
    """Recover the message text of a blob whose header could not be walked.

    A forward or reply header nests further optional objects, so the offset of
    the text cannot be reached by walking the structure without implementing
    those objects as well. The date field sits immediately before the text and
    its value is known independently, from the row's own date column, so the
    text is located by finding that value and reading the string that follows.
    The candidate is accepted only when it is a well-formed TL string that
    decodes as strict UTF-8, and the first match is used; when nothing
    validates the text is reported as unavailable rather than guessed at.
    """
    if not date:
        return None
    needle = struct.pack('<i', date)
    position = blob.find(needle, start)
    while position != -1:
        try:
            reader = _TLReader(blob[position + 4:])
            length = blob[position + 4]
            if length < 254 and position + 5 + length <= len(blob):
                candidate = blob[position + 5:position + 5 + length]
                candidate.decode('utf-8')          # strict: rejects a bad offset
                return reader.read_string()
        except (UnicodeDecodeError, IndexError, struct.error):
            pass
        position = blob.find(needle, position + 1)
    return None


def _decode_message_blob(blob, date=None):
    """Decode a messages_v2 data blob.

    Returns a dict with the sender id and message text when the constructor is
    known. Messages carrying a forward or reply header fall back to
    _text_after_date, because those headers nest further optional objects.
    """
    if not isinstance(blob, bytes) or len(blob) < 8:
        return {}
    reader = _TLReader(blob)
    constructor = reader.read_uint32()
    if constructor in _MSG_SERVICE:
        return {'service': True}
    if constructor not in _MSG_ALL:
        return {}

    flags = reader.read_uint32()
    flags2 = reader.read_uint32() if constructor in _MSG_WITH_FLAGS2 else 0
    reader.read_int32()                                  # message id
    sender = None
    if flags & (1 << 8):
        sender = reader.read_peer()
    if constructor in _MSG_WITH_FLAGS2 and flags & (1 << 29):
        reader.read_int32()                              # from_boosts_applied
    reader.read_peer()                                   # peer_id
    if flags & (1 << 28):
        reader.read_peer()                               # saved_peer_id
    if flags & (1 << 2):                                 # forward header
        return {'sender': sender, 'forwarded': True,
                'text': _text_after_date(blob, reader.stream.tell(), date)}
    if flags & (1 << 11):
        reader.read_int64()                              # via_bot_id
    if constructor in _MSG_WITH_FLAGS2 and flags2 & 1:
        reader.read_int64()                              # via_business_bot_id
    if flags & (1 << 3):                                 # reply header
        return {'sender': sender, 'reply': True,
                'text': _text_after_date(blob, reader.stream.tell(), date)}
    date = reader.read_int32()
    return {'sender': sender, 'date': date, 'text': reader.read_string()}


# --- shared helpers ----------------------------------------------------------

def _split_user_name(name):
    """users.name stores 'display name;;;username'."""
    if not name:
        return '', ''
    parts = name.split(';;;')
    display = parts[0].strip() if parts else ''
    username = parts[-1].strip() if len(parts) > 1 else ''
    return display, username


def _name_lookup(db_file):
    """Map peer id to a display name using the users and chats tables."""
    names = {}
    for uid, name in get_sqlite_db_records(db_file, 'SELECT uid, name FROM users') or []:
        display, username = _split_user_name(name)
        names[uid] = f'{display} (@{username})' if username else display
    try:
        for uid, name in get_sqlite_db_records(db_file, 'SELECT uid, name FROM chats') or []:
            if name:
                names[uid] = name
    except Exception:      # pylint: disable=broad-except
        pass               # older databases may not carry a chats table
    return names


# --- artifacts ---------------------------------------------------------------

@artifact_processor
def get_telegramMessages(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Dialog ID',
        'Chat',
        'Direction',
        'Sender ID',
        'Sender',
        'Message',
        'Read State',
        'Message ID',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    query = '''SELECT mid, uid, date, out, read_state, data
               FROM messages_v2 ORDER BY date'''
    for mid, uid, date, out, read_state, blob in get_sqlite_db_records(db_file, query) or []:
        decoded = _decode_message_blob(blob, date)
        text = decoded.get('text') or ''
        if decoded.get('service'):
            text = '[Service message]'
        elif decoded.get('forwarded') and not text:
            text = '[Forwarded message, text not recovered]'
        elif decoded.get('reply') and not text:
            text = '[Reply, text not recovered]'
        sender_id = decoded.get('sender')
        if sender_id is None and not out:
            sender_id = uid            # in a one-to-one chat the peer is the sender
        data_list.append((
            convert_unix_ts_to_utc(date),
            uid,
            names.get(uid, ''),
            'Outgoing' if out else 'Incoming',
            sender_id if sender_id is not None else '',
            names.get(sender_id, '') if sender_id is not None else '',
            text,
            read_state,
            mid,
        ))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramContacts(context):
    data_headers = (
        'User ID',
        'First Name',
        'Last Name',
        'Phone Numbers',
        'Imported',
        'Device Contact Key',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    phones = {}
    for key, phone, deleted in get_sqlite_db_records(
            db_file, 'SELECT key, phone, deleted FROM user_phones_v7') or []:
        if deleted:
            continue
        phones.setdefault(key, []).append(phone)

    query = 'SELECT key, uid, fname, sname, imported FROM user_contacts_v7 ORDER BY fname'
    for key, uid, fname, sname, imported in get_sqlite_db_records(db_file, query) or []:
        data_list.append((
            uid,
            fname or '',
            sname or '',
            ', '.join(phones.get(key, [])),
            imported,
            key,
        ))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramUsers(context):
    data_headers = (
        ('Last Seen', 'datetime'),
        'User ID',
        'Display Name',
        'Username',
        'Status Value',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    for uid, name, status in get_sqlite_db_records(
            db_file, 'SELECT uid, name, status FROM users') or []:
        display, username = _split_user_name(name)
        last_seen = convert_unix_ts_to_utc(status) if status and status > 0 else ''
        data_list.append((last_seen, uid, display, username, status))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramChats(context):
    data_headers = (
        ('Last Activity', 'datetime'),
        'Dialog ID',
        'Chat',
        'Messages Stored',
        'Unread Count',
        'Pinned',
        'Folder',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    counts = {}
    for uid, total in get_sqlite_db_records(
            db_file, 'SELECT uid, count(*) FROM messages_v2 GROUP BY uid') or []:
        counts[uid] = total

    query = '''SELECT did, date, unread_count, pinned, folder_id
               FROM dialogs ORDER BY date DESC'''
    for did, date, unread, pinned, folder_id in get_sqlite_db_records(db_file, query) or []:
        data_list.append((
            convert_unix_ts_to_utc(date),
            did,
            names.get(did, ''),
            counts.get(did, 0),
            unread,
            'Yes' if pinned else '',
            'Archived' if folder_id == 1 else 'Main',
        ))
    return data_headers, data_list, db_file


# DownloadController.java: mask index is the chat category, mask bits the media type.
_MASK_CATEGORIES = ('Contacts', 'Other private chats', 'Groups', 'Channels')
_MASK_TYPES = ((1, 'Photos'), (2, 'Audio'), (4, 'Videos'), (8, 'Documents'))
_PRESET_KEYS = (
    ('mobilePreset', 'Mobile data'),
    ('wifiPreset', 'Wi-Fi'),
    ('roamingPreset', 'Roaming'),
)


def _describe_mask(mask):
    enabled = [label for bit, label in _MASK_TYPES if mask & bit]
    return ', '.join(enabled) if enabled else 'None'


@artifact_processor
def get_telegramAutoDownload(context):
    data_headers = (
        'Network',
        'Auto-Download Enabled',
        'Chat Category',
        'Media Auto-Downloaded',
        'Photo Size Limit',
        'Video Size Limit',
        'Document Size Limit',
    )
    data_list = []
    xml_file = get_file_path(context.get_files_found(), 'mainconfig.xml')
    if not xml_file:
        return data_headers, data_list, ''

    try:
        root = ET.parse(xml_file).getroot()
    except ET.ParseError as err:
        logfunc(f'Telegram auto-download: could not parse {xml_file}: {err}')
        return data_headers, data_list, xml_file

    values = {element.get('name'): (element.get('value') or element.text or '')
              for element in root}

    for key, network in _PRESET_KEYS:
        raw = values.get(key, '')
        parts = raw.split('_')
        if len(parts) < 11:
            continue
        try:
            masks = [int(parts[index]) for index in range(4)]
            sizes = [int(parts[index]) for index in range(4, 8)]
            enabled = int(parts[10]) == 1
        except ValueError:
            continue
        for index, category in enumerate(_MASK_CATEGORIES):
            data_list.append((
                network,
                'Yes' if enabled else 'No',
                category,
                _describe_mask(masks[index]),
                sizes[0],
                sizes[1],
                sizes[2],
            ))
    return data_headers, data_list, xml_file
