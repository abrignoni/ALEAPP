__artifacts_v2__ = {
    "ok_tamtam_messages": {
        "name": "OK - Messages (tamtam_messages)",
        "description": "Messages the OK (Odnoklassniki) app holds in its tamtam_messages database, with "
                       "their chat and sender.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Class and line references are to the OK APK held in the extraction (package ru.ok.android, "
            "version code 26061802 as the device's packages.xml records it), decompiled with jadx; the "
            "cited ru/ok/tamtam classes are not obfuscated. The app opens tamtam_messages "
            "(MessagingSdkModule.java:1092). Chat and contact rows hold protobuf messages whose field "
            "numbers and types are read from the generated classes in ru/ok/tamtam/nano/Protos.java; "
            "the module reads the wire format by those numbers, with no type guessing, and a blob that "
            "does not decode is logged and read as empty. One row per row of the messages table "
            "(MessageManager.java:1133-1135; columns at :55). Time and Update Time are msg_time and "
            "msg_update_time. The app writes them from the message's time and update time "
            "(MessageManager.java:318-319 and 444-445; outgoing messages at :191-194 and :238), and "
            "compares msg_time with its clock in milliseconds (MessageOptionsLogic.java:127, "
            "BaseClientPrefs.java:263-264), so both are read as Unix milliseconds; the unit of "
            "msg_update_time is not cited from the app. A 0 is blank. msg_time_local is not read. Chat "
            "Title and Chat Type come from the chats row whose _id is msg_chat_id: Protos.Chat field 7 "
            "(title) and field 2 (type), mapped to DIALOG, CHAT, CHANNEL, GROUP_CHAT, CONSTRUCTOR or "
            "SELF_DIALOG as ProtoUtils.chatFrom does, with 0 or absent as DIALOG "
            "(ProtoUtils.java:300-317); another value is shown as stored, where the app reads DIALOG. "
            "The DIALOG chat in the test data had no title; a chat's participants are in OK - Chats "
            "(tamtam_messages). Sender ID is msg_sender (MessageManager.java:320), and Sender the names "
            "of the contacts row whose ctt_server_id is that id, as in OK - Contacts (tamtam_messages). "
            "Text is msg_text. Attachments lists the entries of the Protos.Attaches message in "
            "msg_attaches (field 1), each as its type (Attach field 1, mapped as the switch at "
            "ProtoUtils.java:1053-1103 does, except that 13 and any other unlisted value are shown as "
            "stored where the app reads UNKNOWN) and, when set, its localPath (field 14); the module "
            "does not link media to the row, and in the test data none of the 4 local paths named a "
            "file the extraction holds. Delivery Status, Status and Message Type are "
            "msg_delivered_status, msg_status and msg_type with the names of the app's "
            "MessageDeliveryStatus, MessageStatus and MessageType values "
            "(ru/ok/tamtam/messages/MessageDeliveryStatus.java:18-22, "
            "ru/ok/tamtam/models/message/MessageStatus.java:15-18, "
            "ru/ok/tamtam/messages/MessageType.java:5-9); a value outside them is shown as stored. A "
            "DELETED status was not present in the test data. Server ID is msg_server_id. Not read: the "
            "phones, tasks, events and upload_files tables (no rows in the test data) and the stickers "
            "table (4,248 rows in the test data). Each database copy is read on its own, with its own "
            "chat and contact rows, and the copies are then joined: a copy under another storage "
            "spelling is read when it differs, and a row both hold appears once; a rollback snapshot "
            "that differs is read separately, so a row both hold appears twice. The test data held one "
            "copy. Android User is read from the database's path; a path that names no user shows 0."),
        "paths": ('*/ru.ok.android/databases/tamtam_messages*',),
        "output_types": "standard",
        "multiline_columns": ["Sender", "Text", "Attachments"],
        "artifact_icon": "message-square",
    },
    "ok_tamtam_chats": {
        "name": "OK - Chats (tamtam_messages)",
        "description": "Chats the OK (Odnoklassniki) app holds in its tamtam_messages database, with "
                       "their type, title and participants.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Class and line references are to the OK APK held in the extraction (package ru.ok.android, "
            "version code 26061802 as the device's packages.xml records it), decompiled with jadx; the "
            "cited ru/ok/tamtam classes are not obfuscated. The app opens tamtam_messages "
            "(MessagingSdkModule.java:1092). Chat and contact rows hold protobuf messages whose field "
            "numbers and types are read from the generated classes in ru/ok/tamtam/nano/Protos.java; "
            "the module reads the wire format by those numbers, with no type guessing, and a blob that "
            "does not decode is logged and read as empty. One row per row of the chats table, whose "
            "cht_data the app writes with ProtoUtils.toBytes (ChatManager.java:72 and 94) and reads "
            "with ProtoUtils.chatFrom (ChatManager.java:148). Fields read from Protos.Chat "
            "(Protos.java:2338-2741): 1 serverId (Server ID), 2 type, 3 status, 4 owner (Owner ID), 5 "
            "participants, 7 title, 11 lastEventTime (Last Event Time, which ChatController.java:2318 "
            "sets from a message time, read as Unix milliseconds), 25 link, 29 participantsCount and 30 "
            "description. Type and Status are mapped as ProtoUtils.chatFrom does "
            "(ProtoUtils.java:300-344), absent as 0 (DIALOG, ACTIVE); another value is shown as stored. "
            "Participants lists the ids of the participants map (each entry's key, field 1), with the "
            "first entry of that contact's Names where the contacts table holds that id. Field 6 "
            "(created) held a one-digit value in the test data, so it is not reported. Each database "
            "copy is read on its own, with its own chat and contact rows, and the copies are then "
            "joined: a copy under another storage spelling is read when it differs, and a row both hold "
            "appears once; a rollback snapshot that differs is read separately, so a row both hold "
            "appears twice. The test data held one copy. Android User is read from the database's path; "
            "a path that names no user shows 0."),
        "paths": ('*/ru.ok.android/databases/tamtam_messages*',),
        "output_types": "standard",
        "multiline_columns": ["Participants"],
        "artifact_icon": "users",
    },
    "ok_tamtam_contacts": {
        "name": "OK - Contacts (tamtam_messages)",
        "description": "Contacts the OK (Odnoklassniki) app holds in its tamtam_messages database.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Class and line references are to the OK APK held in the extraction (package ru.ok.android, "
            "version code 26061802 as the device's packages.xml records it), decompiled with jadx; the "
            "cited ru/ok/tamtam classes are not obfuscated. The app opens tamtam_messages "
            "(MessagingSdkModule.java:1092). Chat and contact rows hold protobuf messages whose field "
            "numbers and types are read from the generated classes in ru/ok/tamtam/nano/Protos.java; "
            "the module reads the wire format by those numbers, with no type guessing, and a blob that "
            "does not decode is logged and read as empty. One row per row of the contacts table, whose "
            "ctt_data is a Protos.Contact (ContactManager.java:19 and 31, ContactData.java:197-198, "
            "ProtoUtils.java:172-176; Protos.java:4139-4245). Where several rows share a ctt_server_id, "
            "the messages and chats artifacts name the sender from the last of them. Names lists the "
            "entries of field 14 (names), each a name (field 1) with its type (field 2) mapped to OK, "
            "TT, CUSTOM, DEVICE or CONSTRUCTOR as ProtoUtils.java:79-92 does, other values as UNKNOWN; "
            "an entry with no name is left out, and field 5 (name) is used when there is none. Last "
            "Update Time is field 8 (lastUpdateTime), read as Unix milliseconds; the unit is not cited "
            "from the app, and both values in the test data are 13 digits. Phone (serverPhone), "
            "Birthday, Description, OK Profile URL and Link are fields 9, 18, 16, 7 and 17 as stored. "
            "Field 6 (deviceName) is not reported: no writer of it was found in this app version's "
            "ru/ok/tamtam classes. Server ID is ctt_server_id. The presence columns are not reported. "
            "Each database copy is read on its own, with its own chat and contact rows, and the copies "
            "are then joined: a copy under another storage spelling is read when it differs, and a row "
            "both hold appears once; a rollback snapshot that differs is read separately, so a row both "
            "hold appears twice. The test data held one copy. Android User is read from the database's "
            "path; a path that names no user shows 0."),
        "paths": ('*/ru.ok.android/databases/tamtam_messages*',),
        "output_types": "standard",
        "multiline_columns": ["Names"],
        "artifact_icon": "user",
    },
}

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, is_sqlite_sidecar, logfunc

DATABASE = 'tamtam_messages'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')

# ProtoUtils.chatFrom: Protos.Chat.type and .status to ChatData.Type and .Status.
CHAT_TYPES = {0: 'DIALOG', 1: 'CHAT', 2: 'CHANNEL', 3: 'GROUP_CHAT', 4: 'CONSTRUCTOR', 5: 'SELF_DIALOG'}
CHAT_STATUSES = {0: 'ACTIVE', 1: 'LEFT', 2: 'LEAVING', 3: 'REMOVED', 4: 'REMOVING', 5: 'CLOSED',
                 6: 'HIDDEN'}
# MessageDeliveryStatus, MessageStatus and MessageType values.
DELIVERY = {0: 'UNKNOWN', 10: 'SENDING', 20: 'SENT', 30: 'READ', 40: 'ERROR'}
STATUS = {0: 'ACTIVE', 10: 'DELETED', 20: 'EDITED', 30: 'DELAYED_FIRE_ERROR'}
MESSAGE_TYPES = {0: 'UNKNOWN', 10: 'USER', 20: 'GROUP', 30: 'CHANNEL', 40: 'CHANNEL_ADMIN'}
# ProtoUtils: Protos.Attaches.Attach.type to AttachesData.Attach.Type.
ATTACH_TYPES = {0: 'UNKNOWN', 1: 'CONTROL', 2: 'PHOTO', 3: 'VIDEO', 4: 'AUDIO', 5: 'STICKER',
                6: 'SHARE', 7: 'APP', 8: 'CALL', 9: 'MUSIC', 10: 'FILE', 11: 'CONTACT', 12: 'PRESENT',
                14: 'LOCATION', 15: 'DAILY_MEDIA'}
# ProtoUtils: Protos.Contact.ContactName.type to ContactData.ContactName.Type.
NAME_TYPES = {1: 'OK', 2: 'TT', 3: 'CUSTOM', 4: 'DEVICE', 5: 'CONSTRUCTOR'}


class _ProtoError(ValueError):
    pass


def _varint(data, index):
    shift = value = 0
    while True:
        if index >= len(data):
            raise _ProtoError('truncated varint')
        byte = data[index]
        index += 1
        value |= (byte & 0x7f) << shift
        if not byte & 0x80:
            return value, index
        shift += 7
        if shift > 70:
            raise _ProtoError('varint too long')


def _fields(data):
    """{field number: [values]} of a protobuf message: integers for varints, bytes otherwise.

    Field numbers and types are taken from the app's generated classes (Protos.java), so the
    wire format is read as written, with no type guessing."""
    out = {}
    index = 0
    data = bytes(data or b'')
    while index < len(data):
        key, index = _varint(data, index)
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, index = _varint(data, index)
        elif wire == 1:
            value, index = data[index:index + 8], index + 8
        elif wire == 2:
            length, index = _varint(data, index)
            value, index = data[index:index + length], index + length
        elif wire == 5:
            value, index = data[index:index + 4], index + 4
        else:
            raise _ProtoError(f'wire type {wire}')
        if index > len(data):
            raise _ProtoError('truncated field')
        out.setdefault(number, []).append(value)
    return out


def _decode(blob, label, path):
    """The fields of a nested message, or {} when the value is not a length-delimited field."""
    if blob is not None and not isinstance(blob, (bytes, bytearray, memoryview)):
        logfunc(f'OK tamtam_messages: a {label} in {path} is not a message field')
        return {}
    try:
        return _fields(blob)
    except _ProtoError as error:
        logfunc(f'OK tamtam_messages: could not decode a {label} in {path}: {error}')
        return {}


def _first(fields, number, default=None):
    """The first value of a varint field, or default when absent or of another wire type."""
    for value in fields.get(number, []):
        if isinstance(value, int):
            return value
    return default


def _text(fields, number):
    """The first value of a length-delimited field as UTF-8 text, or ''."""
    for value in fields.get(number, []):
        if isinstance(value, bytes):
            return value.decode('utf-8', 'replace')
    return ''


def _signed(value):
    """An int64 varint read as signed, as the generated classes write it."""
    if value is None:
        return None
    return value - (1 << 64) if value >= 1 << 63 else value


def _ms_to_utc(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        return ''


def _named(table, value):
    if value is None:
        return ''
    return table.get(value, value)


def _blank(value):
    return '' if value is None else value


def _rows(path, query):
    try:
        return list(get_sqlite_db_records(path, query))
    except sqlite3.DatabaseError as error:
        logfunc(f'OK tamtam_messages: could not read {path}: {error}')
        return []


def _user(relative_path):
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK.search(str(relative_path).replace('\\', '/'))
    return match.group(2) if match else '0'


def _databases(context):
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.basename(path) != DATABASE or is_sqlite_sidecar(path):
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        stores.setdefault((canonical_path(os.path.dirname(relative))[0], _user(relative)), []).append(path)
    return dict(sorted(stores.items()))


def _contact_rows(path):
    """[(row id, server id, names text, fields)] of one database copy, one per contacts row."""
    out = []
    for row_id, blob, server_id in _rows(path, 'SELECT _id, ctt_data, ctt_server_id FROM contacts ORDER BY _id'):
        fields = _decode(blob, 'contact', path)
        names = []
        for entry in fields.get(14, []):
            name_fields = _decode(entry, 'contact name', path)
            name = _text(name_fields, 1)
            kind = NAME_TYPES.get(_first(name_fields, 2, 0), 'UNKNOWN')
            if name:
                names.append(f'{name} ({kind})')
        name = _text(fields, 5)
        if name and not names:
            names.append(name)
        out.append((row_id, server_id, '\n'.join(names), fields))
    return out


def _contacts(path):
    """{contact server id: (names text,)} of one database copy; the last row of an id wins."""
    return {server_id: (names,) for _row_id, server_id, names, _fields in _contact_rows(path)}


def _chats(path, contacts):
    """{chat row id: (title, type, participants text, fields)} of one database copy."""
    chats = {}
    for row_id, blob in _rows(path, 'SELECT _id, cht_data FROM chats'):
        fields = _decode(blob, 'chat', path)
        participants = []
        for entry in fields.get(5, []):
            member = _signed(_first(_decode(entry, 'participant', path), 1))
            name = contacts.get(member, ('',))[0].split('\n')[0]
            participants.append(f'{name} [{member}]' if name else str(member))
        chats[row_id] = (_text(fields, 7), CHAT_TYPES.get(_first(fields, 2, 0), _first(fields, 2, 0)),
                         '\n'.join(participants), fields)
    return chats


def _attachments(blob, path):
    out = []
    for entry in _decode(blob, 'attaches', path).get(1, []):
        fields = _decode(entry, 'attach', path)
        kind = _first(fields, 1, 0)
        local = _text(fields, 14)
        out.append(f'{ATTACH_TYPES.get(kind, kind)}' + (f' {local}' if local else ''))
    return out


@artifact_processor
def ok_tamtam_messages(context):
    data_list = []
    sources = []
    for (_key, user), paths in _databases(context).items():
        sources.extend(paths)
        per_copy = []
        for path in paths:
            contacts = _contacts(path)
            chats = _chats(path, contacts)
            rows = []
            for row in _rows(path, '''
                    SELECT msg_time, msg_update_time, msg_chat_id, msg_sender, msg_text, msg_attaches,
                           msg_delivered_status, msg_status, msg_type, msg_server_id, _id
                    FROM messages ORDER BY msg_time, _id'''):
                (time, updated, chat_id, sender, text, attaches, delivered, status, mtype, server_id,
                 row_id) = row
                title, chat_type, _participants, _fields_unused = chats.get(chat_id, ('', '', '', {}))
                sender_name = contacts.get(sender, ('',))[0]
                listed = _attachments(attaches, path) if attaches else []
                rows.append((
                    _ms_to_utc(time), _ms_to_utc(updated), title, chat_type, sender_name, _blank(sender),
                    _blank(text), '\n'.join(listed), _named(DELIVERY, delivered), _named(STATUS, status),
                    _named(MESSAGE_TYPES, mtype), user, _blank(chat_id), _blank(server_id), _blank(row_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Time', 'datetime'), ('Update Time', 'datetime'), 'Chat Title', 'Chat Type', 'Sender',
        'Sender ID', 'Text', 'Attachments', 'Delivery Status', 'Status', 'Message Type', 'Android User',
        'Chat Row ID', 'Server ID', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ok_tamtam_chats(context):
    data_list = []
    sources = []
    for (_key, user), paths in _databases(context).items():
        sources.extend(paths)
        per_copy = []
        for path in paths:
            chats = _chats(path, _contacts(path))
            rows = []
            for row_id, (title, chat_type, participants, fields) in sorted(chats.items()):
                rows.append((
                    _ms_to_utc(_first(fields, 11)), title, chat_type,
                    _named(CHAT_STATUSES, _first(fields, 3, 0)), participants,
                    _blank(_first(fields, 29)), _blank(_signed(_first(fields, 4))), _text(fields, 30),
                    _text(fields, 25), user, _blank(_signed(_first(fields, 1))), row_id))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Last Event Time', 'datetime'), 'Title', 'Type', 'Status',
        'Participants', 'Participants Count', 'Owner ID', 'Description', 'Link', 'Android User',
        'Server ID', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ok_tamtam_contacts(context):
    data_list = []
    sources = []
    for (_key, user), paths in _databases(context).items():
        sources.extend(paths)
        per_copy = []
        for path in paths:
            rows = []
            for row_id, server_id, names, fields in _contact_rows(path):
                rows.append((
                    _ms_to_utc(_first(fields, 8)), names, _blank(_signed(_first(fields, 9))),
                    _text(fields, 18), _text(fields, 16), _text(fields, 7), _text(fields, 17), user,
                    _blank(server_id), row_id))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Last Update Time', 'datetime'), 'Names', 'Phone (serverPhone)', 'Birthday',
        'Description', 'OK Profile URL', 'Link', 'Android User', 'Server ID', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)
