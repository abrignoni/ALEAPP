__artifacts_v2__ = {
    "get_telegramMessages": {
        "name": "Telegram - Messages",
        "description": (
            "Parses Telegram messages from the cache4.db messages_v2 table. Message text is "
            "decoded from the TL-serialised message blob stored in the data column; the "
            "timestamp, direction and read state are read from the table's own columns. "
            "System events such as calls, screenshot notifications and auto-delete timer "
            "changes are named, with the detail they carry. Messages whose blob uses a "
            "constructor this parser does not cover are still reported, with that "
            "constructor named in the message column."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The data column holds a TL-serialised TLRPC message object. The message "
                 "constructors and their field order are taken from the open-source Telegram "
                 "Android client; constructors from layer 179 onward read a second flags "
                 "integer before the message id, which this parser accounts for. Forward and "
                 "reply headers are stepped over field by field using the same source, so "
                 "forwarded messages and replies are decoded structurally. A reply that "
                 "carries inline reply media, quoted entities or a poll option holds a "
                 "further object tree this parser does not implement; for those, and for any "
                 "header constructor not covered, the text is instead located by searching "
                 "the blob for the row's own date value, which sits immediately before the "
                 "text, and is accepted only when it is a well-formed TL string that decodes "
                 "as strict UTF-8. The same fallback is used when a structural walk ends on a "
                 "date that disagrees with the date column. Text that neither route recovers "
                 "is reported as not recovered rather than guessed at. All eight "
                 "TL_messageService constructors are recognised; their header is walked the "
                 "same way and the action that follows is named from the client's own action "
                 "constructors, so system events such as a phone call, a screenshot "
                 "notification, a cleared history or an auto-delete timer change are "
                 "identified rather than reported as an unlabelled service message. Detail "
                 "fields are read for the actions that carry them, including the outcome and "
                 "duration of a call and the new value of an auto-delete timer; an action "
                 "with no reader implemented is reported by name alone. Reference: "
                 "Telegram-Android, "
                 "'TL_legacy_message.java (TL_message layer constructors)', "
                 "https://github.com/DrKLO/Telegram/blob/master/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java. Reference: "
                 "Telegram-Android, 'generated TlGen_MessageReplyHeader.kt, "
                 "TlGen_MessageFwdHeader.kt, TlGen_Message.kt and TlGen_MessageAction.kt "
                 "(header field order, flag bits, service constructors and action "
                 "constructors)', https://github.com/DrKLO/Telegram/tree/"
                 "master/TMessagesProj_AppTests/src/androidTest/kotlin/org/telegram/tgnet/"
                 "model/generated",
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
    "get_telegramAccounts": {
        "name": "Telegram - Accounts",
        "description": (
            "Parses the Telegram account slots from the userconfing.xml and userconfig1-3.xml "
            "shared preferences files. Reports the signed-in user of each slot, decoded from "
            "the stored user record, together with the app passcode configuration, the "
            "auto-lock delay, the last contacts synchronisation time and the last dialled "
            "number the app recorded."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Telegram supports several accounts on one device; slot 0 is stored in "
                 "userconfing.xml, spelled that way by the client, and slots 1 to 3 in "
                 "userconfig1.xml through userconfig3.xml. The user key holds a "
                 "base64-encoded TL user record, decoded here for the account id, names, "
                 "username and phone number. A passcode is in use when passcodeHash1 holds a "
                 "value; passcodeType 0 is a PIN and 1 is a password. The stored hash and "
                 "salt are not reported, only whether they are present. Reference: "
                 "Telegram-Android, 'SharedConfig.java (passcodeHash1, passcodeType, "
                 "autoLockIn)', https://github.com/DrKLO/Telegram/blob/master/TMessagesProj/"
                 "src/main/java/org/telegram/messenger/SharedConfig.java",
        "paths": ('*/org.telegram.messenger*/shared_prefs/userconf*.xml',),
        "output_types": "standard",
        "artifact_icon": "user-circle",
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

import base64
import io
import os
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

# Every TL_messageService constructor defined by the client. Their action
# payload is not decoded, so they are reported without an action label.
_MSG_SERVICE = {
    0x7A800E0A,   # TL_messageService
    0xD3D28540,   # TL_messageService_layer204
    0x2B085862,   # TL_messageService_layer195
    0x286FA604,   # TL_messageService_layer123
    0x9E19A1F6,   # TL_messageService_layer118
    0xC06B9607,   # TL_messageService_layer48
    0x1D86F70E,   # TL_messageService_layer37
    0x9F8D60BB,   # TL_messageService_layer16
}

# Forward headers, as (constructor: (flag, kind) steps). A flag of 0 marks an
# unconditional field. Every field is a scalar, string or peer, so a forward
# header can always be stepped over.
_FWD_HEADERS = {
    0x4E4DF4BB: (   # TL_messageFwdHeader
        (1, 'peer'), (32, 'string'), (0, 'int32'), (4, 'int32'), (8, 'string'),
        (16, 'peer'), (16, 'int32'), (256, 'peer'), (512, 'string'),
        (1024, 'int32'), (64, 'string'),
    ),
    0x5F777DCE: (   # TL_messageFwdHeader_layer169
        (1, 'peer'), (32, 'string'), (0, 'int32'), (4, 'int32'), (8, 'string'),
        (16, 'peer'), (16, 'int32'), (64, 'string'),
    ),
}

# Reply headers. 'media', 'entities' and 'bytes' mark fields whose payload is a
# further object tree this parser does not implement; hitting one stops the
# structural walk and the text is recovered by anchoring on the date instead.
_REPLY_HEADERS = {
    0x1B97DD66: (   # TL_messageReplyHeader
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'), (1024, 'int32'), (2048, 'int32'),
        (4096, 'bytes'),
    ),
    0x6917560B: (   # TL_messageReplyHeader_layer223
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'), (1024, 'int32'), (2048, 'int32'),
    ),
    0xAFBC09DB: (   # TL_messageReplyHeader_layer207
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'), (1024, 'int32'),
    ),
    0x6EEBCABD: (   # TL_messageReplyHeader_layer166
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'),
    ),
    0xA6D57763: (   # TL_messageReplyHeader_layer165; the id is unconditional
        (0, 'int32'), (1, 'peer'), (2, 'int32'),
    ),
}

# Story reply headers carry no flags field.
_REPLY_STORY_HEADERS = {
    0x0E5AF939: (('peer',), ('int32',)),    # TL_messageReplyStoryHeader
    0x9C98BFC1: (('int64',), ('int32',)),   # TL_messageReplyStoryHeader_layer173
}


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


# Service message headers, as (reads_flags, steps) up to but excluding the
# action. Layouts from the client's generated TL model.
_SERVICE_HEADERS = {
    0x7A800E0A: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (268435456, 'peer'), (8, 'reply'), (0, 'int32'))),
    0xD3D28540: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (8, 'reply'), (0, 'int32'))),
    0x2B085862: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (8, 'reply'), (0, 'int32'))),
    0x286FA604: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (8, 'reply'), (0, 'int32'))),
    0x9E19A1F6: (True, ((0, 'int32'), (256, 'int32'), (0, 'peer'),
                        (8, 'int32'), (0, 'int32'))),
    0xC06B9607: (True, ((0, 'int32'), (256, 'int32'), (0, 'peer'), (0, 'int32'))),
    0x1D86F70E: (True, ((0, 'int32'), (0, 'int32'), (0, 'peer'), (0, 'int32'))),
    0x9F8D60BB: (False, ((0, 'int32'), (0, 'int32'), (0, 'peer'), (0, 'int32'),
                         (0, 'int32'), (0, 'int32'))),
}

# Human labels for every TL_messageAction constructor the client defines.
_ACTION_NAMES = {
    0x031224c3: 'Joined chat by invite link',
    0x08557637: 'Star gift',
    0x0d999256: 'Topic created',
    0x15cefd00: 'User added to chat',
    0x16605e3e: 'Managed bot created',
    0x26077b99: 'Star gift unique',
    0x2a9fadc5: 'Giveaway results',
    0x2c8f2a25: 'Suggest birthday',
    0x2e3ae60e: 'Star gift unique',
    0x2ffe2f7a: 'Conference call',
    0x31518e9b: 'Requested peer',
    0x31c48347: 'Gift code',
    0x332ba9ed: 'Giveaway launch',
    0x34f762f3: 'Star gift unique',
    0x399674dc: 'Poll delete answer',
    0x3c134d7b: 'Auto-delete timer changed',
    0x3e2793ba: 'No forwards request',
    0x40699cd0: 'Payment sent',
    0x41b3e202: 'Payment refunded',
    0x45d5b021: 'Gift stars',
    0x4717e8a5: 'Star gift',
    0x4792929b: 'Screenshot taken',
    0x47dd8079: 'Web view data sent me',
    0x488a7337: 'User added to chat',
    0x48e91302: 'Gift premium',
    0x502f92f7: 'Invited to group call',
    0x5060a3f4: 'Chat wallpaper changed',
    0x51bdb021: 'Group upgraded to supergroup',
    0x56d03994: 'Gift code',
    0x57de635e: 'Profile photo suggested',
    0x5d20bae8: 'Change community',
    0x5e3cfc4b: 'User added to chat',
    0x678c2e09: 'Gift code',
    0x69f916f8: 'Suggested post refund',
    0x6c6274fa: 'Gift premium',
    0x70ef8294: 'Contact joined Telegram',
    0x73ada76b: 'Star gift purchase offer declined',
    0x76b9f11a: 'Invited to group call',
    0x774278d4: 'Star gift purchase offer',
    0x7a0d7f42: 'Group call',
    0x7fcb13a8: 'Chat photo changed',
    0x80e11a7f: 'Phone call',
    0x84b88578: 'Paid messages price',
    0x87e2f155: 'Giveaway results',
    0x8f31b327: 'Payment sent me',
    0x92a72876: 'Game score',
    0x94bd38ed: 'Message pinned',
    0x95728543: 'Star gift unique',
    0x95d2ac92: 'Channel created',
    0x95ddcf69: 'Suggested post success',
    0x95e3f807: 'Chat photo removed',
    0x95e3fbef: 'Chat photo removed',
    0x96163f56: 'Payment sent',
    0x98e0d697: 'Proximity alert triggered',
    0x9bb3ef44: 'Star gift',
    0x9da1cd6c: 'Poll append answer',
    0x9fbab604: 'History cleared',
    0xa43f30cc: 'User removed from chat',
    0xa6638b9a: 'Group created',
    0xa80f51e4: 'Giveaway launch',
    0xa8a3c699: 'Gift ton',
    0xaa1afbfd: 'Auto-delete timer changed',
    0xaa786345: 'Chat theme changed',
    0xaba0f5c6: 'Gift premium',
    0xabe9affe: 'Bot allowed',
    0xac1f1fcd: 'Paid messages refunded',
    0xacdfcb81: 'Star gift unique',
    0xb00c47a2: 'Prize stars',
    0xb055eaee: 'Migrated from group',
    0xb07ed085: 'New creator pending',
    0xb18a431c: 'Topic edited',
    0xb2ae9b0c: 'User removed from chat',
    0xb3a07661: 'Group call scheduled',
    0xb4c38cb5: 'Web view data sent',
    0xb5a1ce5a: 'Chat title changed',
    0xb6aef7b0: 'Empty action',
    0xb91bbd3a: 'Chat theme changed',
    0xbc44a927: 'Chat wallpaper changed',
    0xbcd71419: 'Paid messages price',
    0xbd47cbad: 'Group created',
    0xbf7d6572: 'Content protection toggled',
    0xc0787d6d: 'Set same chat wall paper',
    0xc0944820: 'Topic edited',
    0xc516d679: 'Bot allowed',
    0xc624b16e: 'Payment sent',
    0xc7edbc83: 'Todo append tasks',
    0xc83d6aec: 'Gift premium',
    0xcc02aa6d: 'Boost apply',
    0xcc7c5c89: 'Todo completions',
    0xd2cfdb0e: 'Gift code',
    0xd8f4f0a7: 'Star gift',
    0xd95c6154: 'Telegram Passport data sent',
    0xdb596550: 'Star gift',
    0xe1037f92: 'Group upgraded to supergroup',
    0xe188503b: 'Chat owner changed',
    0xe6c31522: 'Star gift unique',
    0xe7e75f97: 'Attach menu bot allowed',
    0xea2c31d3: 'Star gift',
    0xea3948e9: 'Migrated from group',
    0xebbca3cb: 'Joined chat by request',
    0xee7a1596: 'Suggested post approval',
    0xf24de7fa: 'Star gift',
    0xf3f25f76: 'Contact joined Telegram',
    0xf89cf5e8: 'Joined chat by invite link',
    0xfae69f56: 'Custom action',
    0xfe77345d: 'Requested peer',
    0xffa00ccc: 'Payment sent me',
}

# TlGen_Vector writes this constructor, then a count, then the elements.
_VECTOR = 0x1CB5C415

# InputGroupCall variants carried by TL_messageActionInviteToGroupCall.
_INPUT_GROUP_CALLS = {
    0xD8AA840F: ('int64', 'int64'),   # TL_inputGroupCall: id, access_hash
    0xFE06823F: ('string',),          # TL_inputGroupCallSlug: slug
    0x8C10603F: ('int32',),           # TL_inputGroupCallInviteMessage: msg_id
}

# Bare constructors carried by TL_messageActionPhoneCall.
_DISCARD_REASONS = {
    0x85E42301: 'missed',
    0xE095C1A0: 'disconnected',
    0x57ADC690: 'hung up',
    0xFAF7E8C9: 'busy',
}

# Payload readers for the actions that carry detail worth reporting. Each entry
# is (flags?, steps); a step of (flag, kind, label) with flag 0 is unconditional.
_ACTION_PAYLOADS = {
    0xB5A1CE5A: (False, ((0, 'string', 'title'),)),                  # ChatEditTitle
    0xBD47CBAD: (False, ((0, 'string', 'title'),
                         (0, 'vector-int64', 'members'))),           # ChatCreate
    0xA6638B9A: (False, ((0, 'string', 'title'),
                         (0, 'vector-int32', 'members'))),           # ChatCreate_layer132
    0x15CEFD00: (False, ((0, 'vector-int64', 'users'),)),            # ChatAddUser
    0x488A7337: (False, ((0, 'vector-int32', 'users'),)),            # ChatAddUser_layer132
    0x502F92F7: (False, ((0, 'groupcall', 'call'),
                         (0, 'vector-int64', 'users'))),             # InviteToGroupCall
    0x76B9F11A: (False, ((0, 'groupcall', 'call'),
                         (0, 'vector-int32', 'users'))),             # InviteToGroupCall_layer132
    0xA43F30CC: (False, ((0, 'int64', 'user'),)),                    # ChatDeleteUser
    0x031224C3: (False, ((0, 'int64', 'inviter'),)),                 # ChatJoinedByLink
    0xFAE69F56: (False, ((0, 'string', 'message'),)),                # CustomAction
    0x92A72876: (False, ((0, 'int64', 'game'), (0, 'int32', 'score'))),  # GameScore
    0x3C134D7B: (True, ((0, 'int32', 'timer seconds'),)),                  # SetMessagesTTL
    0x80E11A7F: (True, ((0, 'int64', 'call id'), (1, 'reason', 'outcome'),
                        (2, 'int32', 'duration seconds'))),          # PhoneCall
    0x98E0D697: (False, ((0, 'peer', 'from'), (0, 'peer', 'to'),
                         (0, 'int32', 'metres'))),                   # GeoProximityReached
    0xC624B16E: (True, ((0, 'string', 'currency'), (0, 'int64', 'amount'))),  # PaymentSent
}


def _read_action_payload(reader, constructor):
    """Read the detail fields of an action, when one is implemented for it."""
    entry = _ACTION_PAYLOADS.get(constructor)
    if entry is None:
        return ''
    reads_flags, steps = entry
    flags = reader.read_uint32() if reads_flags else 0
    parts = []
    for flag, kind, label in steps:
        if flag and not flags & flag:
            continue
        if kind == 'int32':
            value = reader.read_int32()
        elif kind == 'int64':
            value = reader.read_int64()
        elif kind == 'string':
            value = reader.read_string()
        elif kind == 'peer':
            value = reader.read_peer()
        elif kind == 'reason':
            value = _DISCARD_REASONS.get(reader.read_uint32(), 'unknown')
        elif kind in ('vector-int64', 'vector-int32'):
            if reader.read_uint32() != _VECTOR:
                return ', '.join(parts)
            count = reader.read_int32()
            if count < 0 or count > 10000:
                return ', '.join(parts)
            read = reader.read_int64 if kind == 'vector-int64' else reader.read_int32
            members = [str(read()) for _ in range(count)]
            if not members:
                continue
            value = ', '.join(members)
        elif kind == 'groupcall':
            fields = _INPUT_GROUP_CALLS.get(reader.read_uint32())
            if fields is None:
                return ', '.join(parts)
            values = []
            for field in fields:
                if field == 'int64':
                    values.append(str(reader.read_int64()))
                elif field == 'int32':
                    values.append(str(reader.read_int32()))
                else:
                    values.append(reader.read_string())
            value = values[0] if values else ''
        else:
            return ''
        if kind == 'string' and not value:
            continue
        parts.append(f'{label} {value}')
    return ', '.join(parts)


def _decode_service(reader, constructor):
    """Walk a service message header and name its action."""
    entry = _SERVICE_HEADERS.get(constructor)
    if entry is None:
        return None
    reads_flags, steps = entry
    flags = reader.read_uint32() if reads_flags else 0
    for flag, kind in steps:
        if flag and not flags & flag:
            continue
        if kind == 'int32':
            reader.read_int32()
        elif kind == 'peer':
            reader.read_peer()
        elif kind == 'reply':
            if not _skip_reply_header(reader):
                return None
    action = reader.read_uint32()
    name = _ACTION_NAMES.get(action)
    if name is None:
        return f'Unrecognised action {action:#010x}'
    try:
        detail = _read_action_payload(reader, action)
    except (struct.error, IndexError, UnicodeDecodeError, ValueError):
        detail = ''
    return f'{name} ({detail})' if detail else name


def _skip_fields(reader, flags, steps):
    """Step over a flag-driven field list. False when a field is not implemented."""
    for flag, kind in steps:
        if flag and not flags & flag:
            continue
        if kind == 'int32':
            reader.read_int32()
        elif kind == 'int64':
            reader.read_int64()
        elif kind == 'string':
            reader.read_string()
        elif kind == 'peer':
            reader.read_peer()
        elif kind == 'fwd':
            if not _skip_fwd_header(reader):
                return False
        else:                       # media, entities, bytes
            return False
    return True


def _skip_fwd_header(reader):
    """Step over a MessageFwdHeader. False when the constructor is unknown."""
    constructor = reader.read_uint32()
    steps = _FWD_HEADERS.get(constructor)
    if steps is None:
        return False
    return _skip_fields(reader, reader.read_uint32(), steps)


def _skip_reply_header(reader):
    """Step over a MessageReplyHeader. False when it cannot be fully stepped."""
    constructor = reader.read_uint32()
    story = _REPLY_STORY_HEADERS.get(constructor)
    if story is not None:
        for (kind,) in story:
            if kind == 'peer':
                reader.read_peer()
            elif kind == 'int64':
                reader.read_int64()
            else:
                reader.read_int32()
        return True
    steps = _REPLY_HEADERS.get(constructor)
    if steps is None:
        return False
    return _skip_fields(reader, reader.read_uint32(), steps)


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
        try:
            return {'service': True, 'action': _decode_service(reader, constructor)}
        except (struct.error, IndexError, UnicodeDecodeError, ValueError):
            return {'service': True}
    if constructor not in _MSG_ALL:
        return {'unknown': constructor}

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
    forwarded = bool(flags & (1 << 2))
    if forwarded:
        position = reader.stream.tell()
        if not _skip_fwd_header(reader):
            return {'sender': sender, 'forwarded': True,
                    'text': _text_after_date(blob, position, date)}
    if flags & (1 << 11):
        reader.read_int64()                              # via_bot_id
    if constructor in _MSG_WITH_FLAGS2 and flags2 & 1:
        reader.read_int64()                              # via_business_bot_id
    reply = bool(flags & (1 << 3))
    if reply:
        position = reader.stream.tell()
        if not _skip_reply_header(reader):
            return {'sender': sender, 'reply': True,
                    'text': _text_after_date(blob, position, date)}
    stored_date = reader.read_int32()
    if date and stored_date != date:
        # The walk drifted; the date column is authoritative, so fall back.
        return {'sender': sender, 'forwarded': forwarded, 'reply': reply,
                'text': _text_after_date(blob, 0, date)}
    return {'sender': sender, 'date': stored_date, 'text': reader.read_string(),
            'forwarded': forwarded, 'reply': reply, 'structural': True}


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
            action = decoded.get('action')
            text = f'[{action}]' if action else '[Service message]'
        elif decoded.get('unknown') is not None:
            text = f"[Unrecognised message constructor {decoded['unknown']:#010x}]"
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


# TL_user constructors whose prefix is flags, flags2, id, then the optional
# access hash, names, username and phone. TL_user_layer184 and _layer227.
_USER_RECORDS = {0x215C4438, 0x31774388}

_PASSCODE_TYPES = {0: 'PIN', 1: 'Password'}


def _decode_account_user(raw):
    """Decode the base64 TL user record stored under the 'user' key."""
    try:
        blob = base64.b64decode(raw)
    except (ValueError, TypeError):
        return {}
    if len(blob) < 16:
        return {}
    reader = _TLReader(blob)
    if reader.read_uint32() not in _USER_RECORDS:
        return {}
    try:
        flags = reader.read_uint32()
        reader.read_uint32()                       # flags2
        user = {'id': reader.read_int64()}
        if flags & 1:
            reader.read_int64()                    # access_hash
        for bit, name in ((2, 'first_name'), (4, 'last_name'),
                          (8, 'username'), (16, 'phone')):
            if flags & bit:
                user[name] = reader.read_string()
        return user
    except (struct.error, IndexError, UnicodeDecodeError):
        return {}


@artifact_processor
def get_telegramAccounts(context):
    data_headers = (
        ('Last Contacts Sync', 'datetime'),
        'Account Slot',
        'User ID',
        'First Name',
        'Last Name',
        'Username',
        'Phone',
        'Passcode',
        'Auto-Lock',
        'Unlock With Fingerprint',
        'Last Dialled Number',
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        path = str(file_found)
        name = os.path.basename(path.replace('\\', '/'))
        if not name.startswith('userconf') or not name.endswith('.xml'):
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as err:
            logfunc(f'Telegram accounts: could not parse {path}: {err}')
            continue
        values = {element.get('name'): (element.get('value') or element.text or '')
                  for element in root}
        user = _decode_account_user(values.get('user', ''))
        digits = ''.join(ch for ch in name if ch.isdigit())
        slot = digits if digits else '0'

        if not user and not values.get('passcodeHash1') \
                and not values.get('last_call_phone_number'):
            continue                                # an unused account slot

        passcode_hash = values.get('passcodeHash1', '')
        if passcode_hash:
            kind = _PASSCODE_TYPES.get(_as_int(values.get('passcodeType')), 'Unknown')
            passcode = f'Set ({kind})'
        else:
            passcode = 'Not set'
        auto_lock = _as_int(values.get('autoLockIn'))
        sync = _as_int(values.get('lastContactsSyncTime'))

        data_list.append((
            convert_unix_ts_to_utc(sync) if sync else '',
            slot,
            user.get('id', ''),
            user.get('first_name', ''),
            user.get('last_name', ''),
            user.get('username', ''),
            user.get('phone', ''),
            passcode,
            f'{auto_lock} seconds' if auto_lock else '',
            'Yes' if values.get('useFingerprint') == 'true' else '',
            values.get('last_call_phone_number', ''),
        ))
        sources.append(path)

    return data_headers, data_list, '\n'.join(sources) if sources else ''


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


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
