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
                 "with no reader implemented is reported by name alone. When the client "
                 "stored the message's media at a known location it appends that path to the "
                 "record as a trailing string, which is reported as the recorded media path; "
                 "it is the path the app wrote, and the file is linked only when it is still "
                 "present in the extraction, since Telegram evicts cached media. Reference: "
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
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',
                  '*/org.telegram.messenger*/cache/**',
                  '*/org.telegram.messenger*/files/Telegram/**'),
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
    "get_telegramPeerDetails": {
        "name": "Telegram - Peer Details",
        "description": (
            "Parses the cached profile detail Telegram stores for users in the user_settings "
            "table of cache4.db, reporting the profile bio and whether the user is blocked. "
            "Telegram caches this record when a profile is opened, so it can exist for a user "
            "with no exchanged messages."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The info column holds a TL user full record. Across the record versions "
                 "this parser covers, the about field follows the id and precedes the nested "
                 "objects, so it is read directly; blocked is flag bit 1 and needs no field "
                 "read. Fields that sit after the nested settings and notification objects, "
                 "such as the common chat count, are not read because those objects are not "
                 "implemented. Names are resolved from the users table. Reference: "
                 "Telegram-Android, 'generated TlGen_UserFull.kt (record layout and flag "
                 "bits)', https://github.com/DrKLO/Telegram/tree/master/TMessagesProj_AppTests"
                 "/src/androidTest/kotlin/org/telegram/tgnet/model/generated",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "address-book",
    },
    "get_telegramChatDetails": {
        "name": "Telegram - Chat Details",
        "description": (
            "Parses the cached group and channel detail Telegram stores in the "
            "chat_settings_v2 table of cache4.db, reporting the description and, where the "
            "record carries them, the participant, administrator, removed, banned and online "
            "member counts."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The info column holds a TL chat full or channel full record. The "
                 "description is written unconditionally after the id, and the member counts "
                 "follow it behind flags, so both are read directly; fields that sit after "
                 "the record's nested photo and notification objects are not read because "
                 "those objects are not implemented. Basic group records carry a description "
                 "but no counts. Names are resolved from the chats table. Reference: "
                 "Telegram-Android, 'generated TlGen_ChatFull.kt (record layouts and flag "
                 "bits)', https://github.com/DrKLO/Telegram/tree/master/TMessagesProj_AppTests"
                 "/src/androidTest/kotlin/org/telegram/tgnet/model/generated",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "users-group",
    },
    "get_telegramSaveToGallery": {
        "name": "Telegram - Save to Gallery Settings",
        "description": (
            "Parses the Telegram save-to-gallery configuration from the mainconfig.xml shared "
            "preferences file, reporting for each category of chat whether incoming photos "
            "and videos are saved to the device gallery and the video size limit. Telegram "
            "writes these keys only after the setting is changed, so a category reported as "
            "not set was still at the app default of off."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Keys are <prefix>_save_gallery_photo, <prefix>_save_gallery_video and "
                 "<prefix>_save_gallery_limitVideo, where the prefix is user, groups or "
                 "channels. The client reads each with a default of false, so an absent key "
                 "means the category was left at the app default. The older single "
                 "save_gallery key is reported when present. Reference: Telegram-Android, "
                 "'SaveToGallerySettingsHelper.java (preference key names and defaults)', "
                 "https://github.com/DrKLO/Telegram/blob/master/TMessagesProj/src/main/java/"
                 "org/telegram/messenger/SaveToGallerySettingsHelper.java",
        "paths": ('*/org.telegram.messenger*/shared_prefs/mainconfig.xml',),
        "output_types": "standard",
        "artifact_icon": "photo",
    },
    "get_telegramChannelMembers": {
        "name": "Telegram - Channel & Group Members",
        "description": (
            "Parses the channel and group membership Telegram cached, from the "
            "channel_users_v2 table of cache4.db, reporting the chat, the member and the "
            "date recorded against that membership, with names resolved from the users and "
            "chats tables."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The dialog id, user id and date columns are stored as plain integers and "
                 "are reported as such. The data column holds a TL channel participant "
                 "record; the creator constructor is named where it appears and any other "
                 "constructor is reported by its id rather than guessed at. The membership "
                 "cached here is what the client had retrieved, which is not necessarily "
                 "the full member list of the chat.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "users-group",
    },
    "get_telegramChatHints": {
        "name": "Telegram - Frequent Chats",
        "description": (
            "Parses the chat_hints table of cache4.db, which Telegram maintains to rank the "
            "chats it suggests first. Each row carries a chat and a rating value, so the "
            "table reflects which chats the client scored as most used."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The did, rating and date columns are stored as plain values. The type "
                 "column is reported as stored because its values are not documented in the "
                 "client source that was checked. The rating is the client's own ranking "
                 "figure; the scale and how it decays over time were not established, so it "
                 "is reported as stored and is useful for ordering rather than as a count.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "star",
    },
    "get_telegramVoipLogs": {
        "name": "Telegram - VoIP Call Logs",
        "description": (
            "Parses the per-call WebRTC logs Telegram writes under cache/voip_logs. Each log "
            "is named for the call it belongs to, so the file itself records that a call took "
            "place and how long the call stack was running, independently of the message "
            "history."
        ),
        "author": "Alexis Brignoni",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The log file name is the call id, which is the same id the phone call "
                 "service message in the chat carries, so the two can be tied together. The "
                 "timestamps inside the log are local-time strings with no timezone, so they "
                 "are reported as recorded and only their difference is used for the logged "
                 "span; the file modification time is used as the UTC reference point. A log "
                 "spans the call stack running, which starts before and ends after the "
                 "connected call, so the logged span is not the billed call duration. "
                 "Approach adapted from a Telegram parser contributed by WriteBlocked in "
                 "ALEAPP pull request 716.",
        "paths": ('*/org.telegram.messenger*/cache/voip_logs/*',),
        "output_types": "standard",
        "artifact_icon": "phone",
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
import datetime
import io
import os
import re
import struct
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, convert_unix_ts_to_utc, \
    get_sqlite_db_records, get_file_path, check_in_media


# --- TL deserialisation ------------------------------------------------------
# Telegram stores message objects in the data column using the TL wire format:
# a 4-byte little-endian constructor id followed by the object's fields.

_PEER_USER = 0x59511722
_PEER_CHAT = 0x36C6019A
_PEER_CHANNEL = 0xA2A5371E
# Layer 132 and older wrote the peer id as an Int32 under its own constructor.
# A device on an older Telegram build stores messages with these, and reading
# them as the 64-bit form misaligns every field that follows.
_PEER_USER_LEGACY = 0x9DB1BC6D
_PEER_CHAT_LEGACY = 0xBAD0E5BB
_PEER_CHANNEL_LEGACY = 0xBDDDE532

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
        if constructor in (_PEER_USER_LEGACY, _PEER_CHAT_LEGACY,
                           _PEER_CHANNEL_LEGACY):
            return self.read_int32()
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


def _attach_path(blob):
    """The local media path the client appends when it stores a message.

    Telegram writes the message record and then the attachment path as a
    trailing TL string, so the path is read from the end of the blob. Walking
    forward to it would require decoding the media objects, which this parser
    does not implement. A candidate is accepted only when its length byte, its
    contents and the TL padding account for the blob exactly to its final byte,
    which is what distinguishes the real trailing field from a coincidental
    run of bytes.
    """
    if not isinstance(blob, bytes) or len(blob) < 6:
        return ''
    end = len(blob)
    while end > 0 and blob[end - 1] == 0:        # TL pads to a 4-byte boundary
        end -= 1
    for length in range(1, 255):
        start = end - length
        marker = start - 1
        if marker < 0:
            break
        if blob[marker] != length:
            continue
        consumed = length + 1
        if marker + consumed + ((4 - consumed % 4) % 4) != len(blob):
            continue
        try:
            text = blob[start:end].decode('utf-8')
        except UnicodeDecodeError:
            continue
        if text.startswith('/'):
            return text
    return ''


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
        'Recorded Media Path',
        ('Media File', 'media'),
        'Read State',
        'Message ID',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)

    # Basename index of whatever media directories the extraction carried.
    media_index = {}
    for found in context.get_files_found():
        path = str(found)
        normalized = path.replace('\\', '/')
        if '/org.telegram.messenger' not in normalized:
            continue
        if '/cache/' not in normalized and '/files/Telegram/' not in normalized:
            continue
        if os.path.isfile(path):
            media_index.setdefault(normalized.rsplit('/', 1)[-1], path)

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
        attach = _attach_path(blob)
        media_ref = ''
        if attach:
            local = media_index.get(attach.replace('\\', '/').rsplit('/', 1)[-1])
            if local:
                media_ref = check_in_media(file_path=local)

        data_list.append((
            convert_unix_ts_to_utc(date),
            uid,
            names.get(uid, ''),
            'Outgoing' if out else 'Incoming',
            sender_id if sender_id is not None else '',
            names.get(sender_id, '') if sender_id is not None else '',
            text,
            attach,
            media_ref,
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


# TL user full records whose prefix is flags, then optionally flags2, then the
# id and the about string. Layouts from the generated TlGen_UserFull.kt.
_USER_FULL_FLAGS2 = {
    0x06CBE645, 0x22FF3E85, 0xCC997720, 0x1F58E369, 0x979D2376, 0x4D975BBC,
    0xD2234EA0, 0x99E78045, 0x29DE80BE, 0x7E63CE1F, 0x3FD81E28, 0xC577B5AD,
    0xA02BC13E,
}
_USER_FULL_NO_FLAGS2 = {
    0xCF366521, 0x8C72EA81, 0xC4B1FC3F, 0xF8D32AED, 0x93EADB53, 0x4FE1CC86,
    0xB9B12C6C,
}
_USER_FULL = _USER_FULL_FLAGS2 | _USER_FULL_NO_FLAGS2


def _decode_user_full(blob):
    """Read the about text and blocked flag from a TL user full record."""
    if not isinstance(blob, bytes) or len(blob) < 12:
        return {}
    reader = _TLReader(blob)
    constructor = reader.read_uint32()
    if constructor not in _USER_FULL:
        return {'unknown': constructor}
    try:
        flags = reader.read_uint32()
        if constructor in _USER_FULL_FLAGS2:
            reader.read_uint32()
        reader.read_int64()                              # id
        about = reader.read_string() if flags & 2 else ''
        return {'about': about, 'blocked': bool(flags & 1)}
    except (struct.error, IndexError, UnicodeDecodeError):
        return {}


@artifact_processor
def get_telegramPeerDetails(context):
    data_headers = (
        'User ID',
        'Name',
        'Username',
        'Bio',
        'Blocked',
        'Pinned',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = {}
    for uid, name in get_sqlite_db_records(db_file, 'SELECT uid, name FROM users') or []:
        names[uid] = _split_user_name(name)

    query = 'SELECT uid, info, pinned FROM user_settings'
    for uid, blob, pinned in get_sqlite_db_records(db_file, query) or []:
        decoded = _decode_user_full(blob)
        if decoded.get('unknown') is not None:
            bio = f"[Unrecognised record {decoded['unknown']:#010x}]"
            blocked = ''
        else:
            bio = decoded.get('about', '')
            blocked = 'Yes' if decoded.get('blocked') else 'No' if decoded else ''
        display, username = names.get(uid, ('', ''))
        data_list.append((uid, display, username, bio, blocked, 'Yes' if pinned else ''))
    return data_headers, data_list, db_file


# TL chat/channel full records, grouped by the shape of the readable prefix.
# A: flags, flags2, id, about, then the counts.
# B: flags, id, about, then the counts.
# C: flags, id, about only, which is the basic group record.
_CHAT_FULL_A = {
    0x0F2BCB6F,
    0x44C054A7,
    0x52D6806B,
    0x723027BD,
    0x9FF3B858,
    0xA04E8D3A,
    0xBBAB348D,
    0xE07429DE,
    0xE4E0B29D,
    0xEA68A619,
    0xF2355507,
}
_CHAT_FULL_B = {
    0x03648977,
    0x10916653,
    0x17F45FCF,
    0x1C87A71A,
    0x2548C037,
    0x2D895C74,
    0x2F532F3C,
    0x548C3F93,
    0x56662E2E,
    0x59CFF963,
    0x76AF5481,
    0x7A7DE4F7,
    0x95CB5F57,
    0x97BEE562,
    0x9882E516,
    0x9E341DDF,
    0xC3D5512F,
    0xE13C3D20,
    0xE9B27A17,
    0xEF3A6ACD,
    0xF0E6672A,
    0xFAB31AA3,
}
_CHAT_FULL_C = {
    0x0DC8C181,
    0x1B7C9DB3,
    0x22A235DA,
    0x2633421B,
    0x46A6FFB4,
    0x49A0A5D9,
    0x4DBDC099,
    0x8A1E2983,
    0xC9D31138,
    0xCBB7A507,
    0xD18EE226,
    0xF06C4018,
    0xF3474AF6,
}
_CHAT_FULL = _CHAT_FULL_A | _CHAT_FULL_B | _CHAT_FULL_C


def _decode_chat_full(blob):
    """Read the description and member counts from a chat or channel record."""
    if not isinstance(blob, bytes) or len(blob) < 12:
        return {}
    reader = _TLReader(blob)
    constructor = reader.read_uint32()
    if constructor not in _CHAT_FULL:
        return {'unknown': constructor}
    try:
        flags = reader.read_uint32()
        if constructor in _CHAT_FULL_A:
            reader.read_uint32()                         # flags2
        reader.read_int64()                              # id
        record = {'about': reader.read_string()}
        if constructor in _CHAT_FULL_C:
            return record                                # basic group: no counts
        if flags & 1:
            record['participants'] = reader.read_int32()
        if flags & 2:
            record['admins'] = reader.read_int32()
        if flags & 4:
            record['kicked'] = reader.read_int32()
            record['banned'] = reader.read_int32()
        if flags & 8192:
            record['online'] = reader.read_int32()
        return record
    except (struct.error, IndexError, UnicodeDecodeError):
        return {}


@artifact_processor
def get_telegramChatDetails(context):
    data_headers = (
        'Chat ID',
        'Chat',
        'Description',
        'Participants',
        'Administrators',
        'Removed',
        'Banned',
        'Online',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = {}
    try:
        for uid, name in get_sqlite_db_records(
                db_file, 'SELECT uid, name FROM chats') or []:
            names[uid] = name or ''
    except Exception:      # pylint: disable=broad-except
        pass

    query = 'SELECT uid, info FROM chat_settings_v2'
    for uid, blob in get_sqlite_db_records(db_file, query) or []:
        record = _decode_chat_full(blob)
        if record.get('unknown') is not None:
            description = f"[Unrecognised record {record['unknown']:#010x}]"
        else:
            description = record.get('about', '')
        data_list.append((
            uid,
            names.get(uid, ''),
            description,
            record.get('participants', ''),
            record.get('admins', ''),
            record.get('kicked', ''),
            record.get('banned', ''),
            record.get('online', ''),
        ))
    return data_headers, data_list, db_file


# SaveToGallerySettingsHelper.java: one settings group per category of chat.
_GALLERY_PREFIXES = (('user', 'Private chats'), ('groups', 'Groups'),
                     ('channels', 'Channels'))
_GALLERY_DEFAULT = 'Not set (app default, off)'


@artifact_processor
def get_telegramSaveToGallery(context):
    data_headers = (
        'Chat Category',
        'Save Photos',
        'Save Videos',
        'Video Size Limit',
    )
    data_list = []
    xml_file = get_file_path(context.get_files_found(), 'mainconfig.xml')
    if not xml_file:
        return data_headers, data_list, ''
    try:
        root = ET.parse(xml_file).getroot()
    except ET.ParseError as err:
        logfunc(f'Telegram save to gallery: could not parse {xml_file}: {err}')
        return data_headers, data_list, xml_file
    values = {element.get('name'): (element.get('value') or element.text or '')
              for element in root}

    def flag(key):
        if key not in values:
            return _GALLERY_DEFAULT
        return 'Yes' if values[key] == 'true' else 'No'

    for prefix, label in _GALLERY_PREFIXES:
        limit_key = f'{prefix}_save_gallery_limitVideo'
        limit = values.get(limit_key, '')
        data_list.append((
            label,
            flag(f'{prefix}_save_gallery_photo'),
            flag(f'{prefix}_save_gallery_video'),
            limit if limit else _GALLERY_DEFAULT,
        ))
    if 'save_gallery' in values:
        data_list.append((
            'All chats (legacy setting)',
            'Yes' if values['save_gallery'] == 'true' else 'No', '', '',
        ))
    return data_headers, data_list, xml_file


# Channel participant constructors seen in the corpus. Only the creator form is
# present in the client's generated model; anything else is reported by id.
_CHANNEL_PARTICIPANTS = {0x2FE601D3: 'Creator'}


@artifact_processor
def get_telegramChannelMembers(context):
    data_headers = (
        ('Date', 'datetime'),
        'Chat ID',
        'Chat',
        'User ID',
        'User',
        'Role',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    query = 'SELECT did, uid, date, data FROM channel_users_v2 ORDER BY did, date'
    for did, uid, date, blob in get_sqlite_db_records(db_file, query) or []:
        role = ''
        if isinstance(blob, bytes) and len(blob) >= 4:
            constructor = struct.unpack('<I', blob[:4])[0]
            role = _CHANNEL_PARTICIPANTS.get(constructor, f'{constructor:#010x}')
        data_list.append((
            convert_unix_ts_to_utc(date) if date else '',
            did,
            names.get(did, '') or names.get(abs(did), ''),
            uid,
            names.get(uid, ''),
            role,
        ))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramChatHints(context):
    data_headers = (
        ('Date', 'datetime'),
        'Chat ID',
        'Chat',
        'Rating (as stored)',
        'Type (as stored)',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    query = 'SELECT did, type, rating, date FROM chat_hints ORDER BY rating DESC'
    for did, kind, rating, date in get_sqlite_db_records(db_file, query) or []:
        data_list.append((
            convert_unix_ts_to_utc(date) if date else '',
            did,
            names.get(did, '') or names.get(abs(did), ''),
            rating,
            kind,
        ))
    return data_headers, data_list, db_file


# Telegram writes one WebRTC log per call under cache/voip_logs, named for the
# call id. Entries look like: 2024-1-31 12:36:34:849 <file>: (line N): <text>
_VOIP_ENTRY = re.compile(r'^(\d{4})-(\d+)-(\d+) (\d+):(\d+):(\d+):(\d+)')


def _voip_log_span(path):
    """First and last entry times in a voip log, as recorded (device local)."""
    first = last = None
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as handle:
            for line in handle:
                match = _VOIP_ENTRY.match(line)
                if not match:
                    continue
                stamp = datetime.datetime(*[int(match.group(i)) for i in range(1, 7)])
                if first is None:
                    first = stamp
                last = stamp
    except OSError:
        return None, None
    return first, last


@artifact_processor
def get_telegramVoipLogs(context):
    data_headers = (
        ('Log Last Modified (UTC)', 'datetime'),
        'Call ID',
        'Logged Span (seconds)',
        'First Entry (device local time)',
        'Last Entry (device local time)',
        'Log Size (bytes)',
        'Stats Log Present',
        'Log File',
    )
    data_list = []
    sources = []

    logs, stats = {}, set()
    for found in context.get_files_found():
        path = str(found)
        name = os.path.basename(path.replace('\\', '/'))
        if '/voip_logs/' not in path.replace('\\', '/') or not os.path.isfile(path):
            continue
        if name.endswith('_stats.log'):
            stats.add(name[:-len('_stats.log')])
        elif name.endswith('.log'):
            logs[name[:-len('.log')]] = path

    for call_id, path in sorted(logs.items()):
        first, last = _voip_log_span(path)
        span = int((last - first).total_seconds()) if first and last else ''
        try:
            modified = convert_unix_ts_to_utc(int(os.path.getmtime(path)))
            size = os.path.getsize(path)
        except OSError:
            modified, size = '', ''
        data_list.append((
            modified,
            call_id,
            span,
            first.strftime('%Y-%m-%d %H:%M:%S') if first else '',
            last.strftime('%Y-%m-%d %H:%M:%S') if last else '',
            size,
            'Yes' if call_id in stats else '',
            path,
        ))
        sources.append(path)

    return data_headers, data_list, '\n'.join(sources) if sources else ''


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
