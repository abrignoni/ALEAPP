__artifacts_v2__ = {
    "justalk_messages": {
        "name": "JusTalk - Messages",
        "description": "Chat messages from the JusTalk Realm store, with the message body, the "
                       "direction, the sender, the media type and the cached media file where it "
                       "is present in the extraction",
        "author": "@AlexisBrignoni, @Antho4n6, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Messages are read from the class_CallLog table of the per-account Realm store "
                 "(files/<account uid>.realm), not from class_MessageChat, which was present in "
                 "the schema but empty in the sample this artifact was built from. class_CallLog "
                 "holds chat messages and call records in the same table; rows whose type is "
                 "AudioCall or VideoCall are reported by the JusTalk - Call Logs artifact instead.\n"
                 "Direction is taken from the boolean 'incoming' column. The separate 'state' "
                 "column is reported as stored: nothing in the extraction documents its values.\n"
                 "Media is linked without guessing. The message's 'fileUrl' column is a row index "
                 "into the class_ROFileUrl table, and that row's 'md5' column is base64 of the MD5 "
                 "of the media file's contents. Every file in the paths above is hashed and matched "
                 "against it, so a message is tied to a file by content rather than by name, size "
                 "or timestamp proximity. A message with no matching file means no copy of that "
                 "media was found in the extraction; it does not establish that the media never "
                 "existed on the device.\n"
                 "Duration is stored in seconds on voice and video message rows. That was derived "
                 "by dividing the stored byte length by the stored duration across the sampled "
                 "rows, which gave consistent audio and video bitrates; it is an inference from "
                 "the data, not a documented unit.\n"
                 "Validation boundary. This was built from a single private sample holding one "
                 "one-to-one conversation, so the fields are mapped from that sample and the "
                 "counts here are not from a public corpus. The class_ServerGroup, "
                 "class_ServerMember, class_Moment and class_ROKids* tables were all empty in it, "
                 "so group chats, Moments posts and JusTalk Kids parental controls are not "
                 "covered. The reply, reaction, sticker, poll and link columns of class_CallLog "
                 "were unpopulated and are not reported. A sample exercising any of those would "
                 "be welcome.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',
                  '*/com.juphoon.justalk/files/imfilecache/*',
                  '*/com.juphoon.justalk/files/image_manager_disk_cache/*',
                  '*/com.juphoon.justalk/files/http410cache/*',
                  '*/com.juphoon.justalk/files/JusTalk/profiles/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {},
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat Partner",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Media",
            }
        },
    },
    "justalk_calls": {
        "name": "JusTalk - Call Logs",
        "description": "Audio and video calls from the JusTalk Realm store, with the direction, "
                       "the duration and the server call identifier",
        "author": "@AlexisBrignoni, @Antho4n6, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from the rows of class_CallLog whose type is AudioCall or VideoCall. "
                 "Direction is taken from the boolean 'incoming' column.\n"
                 "Duration on these rows is reported both as stored and converted from "
                 "milliseconds. Milliseconds is an inference: in the sample, three calls were "
                 "followed by a further message 15.4, 31.6 and 24.0 seconds after the call record, "
                 "each slightly longer than the duration read as milliseconds and not reconcilable "
                 "with the same value read as seconds. Note that this differs from the duration on "
                 "voice and video message rows, which is in seconds. The stored value is kept in "
                 "its own column so the conversion can be checked.\n"
                 "The 'state' and 'reason' columns are reported as stored; nothing in the "
                 "extraction documents their values. A duration of zero is not by itself evidence "
                 "that a call was not answered.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {},
    },
    "justalk_media": {
        "name": "JusTalk - Media",
        "description": "File records from the JusTalk Realm store with the cached copies found in "
                       "the extraction, plus any cached files the store does not account for",
        "author": "@AlexisBrignoni, @Antho4n6, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Each row is one class_ROFileUrl record. The record's 'md5' column is base64 of "
                 "the MD5 of the file's contents, so cached copies are located by hashing every "
                 "file in the paths above and matching, rather than by file name. The same content "
                 "is often cached in more than one place: files/imfilecache holds the app's own "
                 "copy, files/image_manager_disk_cache and files/http410cache held further copies "
                 "of some items in the sample. All matches are reported.\n"
                 "Cached files that no class_ROFileUrl record accounts for are listed as their own "
                 "rows with an empty File Key so they are not dropped. Thumbnails, avatars and "
                 "sticker assets are expected to appear there. Files in these caches are often "
                 "stored with no extension or a '.0' extension; in the sample they were still "
                 "images, so the extension is reported as found and the content is checked in on "
                 "its own sniffed type.\n"
                 "The class_ROFileUrl table also carries sticker pack assets, which have a "
                 "filePath but no encryptedUrl and are not messages. 'localPath' and "
                 "'thumbnailLocalPath' are the paths the app recorded; in the sample they pointed "
                 "into the app's own cache, not to a user-initiated export to shared storage. They "
                 "are reported as stored and are not resolved against the extraction.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',
                  '*/com.juphoon.justalk/files/imfilecache/*',
                  '*/com.juphoon.justalk/files/image_manager_disk_cache/*',
                  '*/com.juphoon.justalk/files/http410cache/*',
                  '*/com.juphoon.justalk/files/JusTalk/profiles/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {},
    },
    "justalk_contacts": {
        "name": "JusTalk - Contacts",
        "description": "Contacts from the JusTalk Realm store, with the JusTalk ID, the display "
                       "and nickname, the client version reported for that account and the last "
                       "online time",
        "author": "@AlexisBrignoni, @Antho4n6, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from the class_ServerFriend table. The class_Contact table, which holds "
                 "device address book matches, was empty in the sample this artifact was built "
                 "from and is not covered here.\n"
                 "The 'version' column carries a platform-prefixed client version string for the "
                 "other party's account, for example a value beginning 'ios.'. 'loginCountry' is "
                 "reported as stored; in the sample it held a value matching a telephone country "
                 "calling code, but nothing in the extraction documents the format.\n"
                 "relationType and serverRelationType are reported as stored.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "justalk_account": {
        "name": "JusTalk - Account",
        "description": "The local JusTalk account identifiers taken from the Realm store file "
                       "name, the app's provisioning file and the Realm schema version",
        "author": "@AlexisBrignoni, @Antho4n6, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "The per-account Realm store is named after the local account's own user id, so "
                 "the file name is reported as the account UID. The profile user name comes from "
                 "the cur_prof_user attribute of files/JusTalk/profiles/provisions.xml, which the "
                 "app also uses as the name of the per-profile directory beside it.\n"
                 "The Realm header reports two top references, which is the store's normal "
                 "committed and uncommitted pair. Both are read and their row counts compared; "
                 "where they differ, content is present in one view and not the other. In the "
                 "sample they matched exactly.\n"
                 "shared_prefs/com.juphoon.justalk_preferences.xml was checked and carries only "
                 "advertising consent framework keys, no account identity, so it is not parsed.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',
                  '*/com.juphoon.justalk/files/JusTalk/profiles/provisions.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {},
    },
}

import base64
import hashlib
import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc
from scripts.realm_parser import parse_realm_file, realm_rows

# Rows of class_CallLog carrying these type values are call records rather than chat
# messages, and are reported by justalk_calls instead of justalk_messages.
CALL_TYPES = ('AudioCall', 'VideoCall')

# Files under the paths above that are the store itself or app configuration rather than
# cached media, so they are not hashed and do not appear as unaccounted media.
SKIP_SUFFIXES = ('.realm', '.lock', '.crc', '.log', '.backup-log', '.xml', '.ini')


def _is_justalk_realm(path):
    """The realm glob picks up default.realm and the versioned backup copy as well as the
    account store, so confirm the file carries JusTalk classes before reading it."""
    try:
        tables = parse_realm_file(path).get('active', {})
    except Exception:  # pylint: disable=broad-exception-caught
        return False
    return 'class_CallLog' in tables and 'class_ROFileUrl' in tables


def _account_realm(files_found):
    """Return the per-account Realm store. The account store is named after the local
    account uid; default.realm is a separate empty store and the .v23.backup.realm copy is
    a pre-upgrade snapshot, so both are passed over when a live account store is present."""
    candidates = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.realm'):
            continue
        name = os.path.basename(file_found)
        if name == 'default.realm':
            continue
        candidates.append(file_found)
    live = [path for path in candidates if '.backup.' not in os.path.basename(path)]
    for path in live + candidates:
        if _is_justalk_realm(path):
            return path
    return ''


def _rows(realm_path, class_name):
    if not realm_path:
        return []
    try:
        return list(realm_rows(realm_path, class_name))
    except Exception:  # pylint: disable=broad-exception-caught
        return []


def _md5_hex(stored):
    """class_ROFileUrl.md5 holds base64 of the raw MD5 digest, so decode it to hex before
    comparing against a hash computed over a file in the extraction."""
    if not stored:
        return ''
    try:
        raw = base64.b64decode(stored, validate=True)
    except Exception:  # pylint: disable=broad-exception-caught
        return ''
    if len(raw) != 16:
        return ''
    return raw.hex()


def _hash_index(files_found):
    """Map the MD5 of each candidate media file's contents to the paths holding it. The
    same content is cached in more than one directory, so a digest maps to a list."""
    index = {}
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(SKIP_SUFFIXES) or os.path.isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as handle:
                digest = hashlib.md5(handle.read()).hexdigest()
        except OSError:
            continue
        index.setdefault(digest, []).append(file_found)
    return index


def _check_in(paths):
    references = [check_in_media(path, os.path.basename(path)) for path in paths]
    references = [reference for reference in references if reference]
    if len(references) == 1:
        return references[0]
    return references if references else ''


def _file_record(file_records, link):
    """class_CallLog.fileUrl is a row index into class_ROFileUrl, not a URL."""
    if link is None:
        return {}
    try:
        return file_records[int(link)]
    except (TypeError, ValueError, IndexError):
        return {}


def _int_or_blank(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return ''


def _seconds_from_ms(value):
    value = _int_or_blank(value)
    if value == '' or value == 0:
        return ''
    return round(value / 1000, 3)


@artifact_processor
def justalk_messages(context):
    files_found = context.get_files_found()
    source_path = _account_realm(files_found)
    data_list = []

    file_records = _rows(source_path, 'class_ROFileUrl')
    hash_index = _hash_index(files_found)

    for row in sorted(_rows(source_path, 'class_CallLog'), key=lambda r: r.get('timestamp') or 0):
        if row.get('type') in CALL_TYPES:
            continue
        outgoing = not row.get('incoming')
        media = _file_record(file_records, row.get('fileUrl'))
        matches = hash_index.get(_md5_hex(media.get('md5')), []) if media else []
        data_list.append((
            convert_unix_ts_to_utc(row.get('timestamp')),
            'Outgoing' if outgoing else 'Incoming',
            row.get('senderName'),
            row.get('name'),
            row.get('type'),
            row.get('content'),
            _check_in(matches),
            '' if not media else ('Recovered' if matches else 'Not in extraction'),
            media.get('encryptedUrl', ''),
            _int_or_blank(media.get('length')) if media else '',
            media.get('suffix', ''),
            _int_or_blank(media.get('duration')) if media else '',
            media.get('localPath', ''),
            media.get('thumbnailLocalPath', ''),
            row.get('senderUid'),
            row.get('uid'),
            row.get('imdnId'),
            row.get('logId'),
            row.get('state'),
            row.get('readState'),
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender Name',
        'Chat Partner',
        'Message Type',
        'Message',
        ('Media', 'media'),
        'Media Recovery',
        'Encrypted URL',
        'Media Size (bytes)',
        'Media Suffix',
        'Media Duration (seconds)',
        'Recorded Local Path',
        'Recorded Thumbnail Path',
        'Sender UID',
        'Partner UID',
        'IMDN ID',
        'Log ID',
        'State (as stored)',
        'Read State (as stored)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def justalk_calls(context):
    source_path = _account_realm(context.get_files_found())
    data_list = []

    for row in sorted(_rows(source_path, 'class_CallLog'), key=lambda r: r.get('timestamp') or 0):
        if row.get('type') not in CALL_TYPES:
            continue
        data_list.append((
            convert_unix_ts_to_utc(row.get('timestamp')),
            'Outgoing' if not row.get('incoming') else 'Incoming',
            row.get('type'),
            row.get('name'),
            _seconds_from_ms(row.get('duration')),
            _int_or_blank(row.get('duration')),
            row.get('uid'),
            row.get('serverCallId'),
            row.get('logId'),
            row.get('state'),
            row.get('reason'),
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Call Type',
        'Partner Name',
        'Duration (seconds)',
        'Duration (as stored)',
        'Partner UID',
        'Server Call ID',
        'Log ID',
        'State (as stored)',
        'Reason (as stored)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def justalk_media(context):
    files_found = context.get_files_found()
    source_path = _account_realm(files_found)
    data_list = []

    hash_index = _hash_index(files_found)
    accounted = set()

    file_records = _rows(source_path, 'class_ROFileUrl')
    # A message row points at its file record by index, so build the reverse map to report
    # which message each file belongs to.
    message_by_index = {}
    for row in _rows(source_path, 'class_CallLog'):
        link = row.get('fileUrl')
        if link is not None:
            message_by_index.setdefault(int(link), row)

    for index, media in enumerate(file_records):
        digest = _md5_hex(media.get('md5'))
        matches = hash_index.get(digest, [])
        accounted.update(matches)
        message = message_by_index.get(index, {})
        data_list.append((
            convert_unix_ts_to_utc(message.get('timestamp')) if message else '',
            _check_in(matches),
            media.get('suffix'),
            _int_or_blank(media.get('length')),
            _int_or_blank(media.get('duration')),
            digest,
            media.get('encryptedUrl'),
            media.get('fileKey'),
            media.get('fileName'),
            media.get('fileUrl'),
            media.get('filePath'),
            media.get('localPath'),
            media.get('thumbnailLocalPath'),
            _int_or_blank(media.get('width')),
            _int_or_blank(media.get('height')),
            message.get('type', ''),
            message.get('logId', ''),
            '; '.join(os.path.basename(path) for path in matches),
        ))

    for digest, paths in sorted(hash_index.items()):
        for path in paths:
            if path in accounted:
                continue
            data_list.append((
                '', _check_in([path]), os.path.splitext(path)[1].lstrip('.'),
                os.path.getsize(path) if os.path.exists(path) else '', '',
                digest, '', '', '', '', '', '', '', '', '', '', '',
                os.path.basename(path),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Media', 'media'),
        'Suffix',
        'Size (bytes)',
        'Duration (seconds)',
        'Content MD5',
        'Encrypted URL',
        'File Key',
        'File Name',
        ('Remote URL', 'url'),
        'Server File Path',
        'Recorded Local Path',
        'Recorded Thumbnail Path',
        'Width',
        'Height',
        'Message Type',
        'Message Log ID',
        'Cached File Names',
    )
    return data_headers, data_list, source_path


@artifact_processor
def justalk_contacts(context):
    source_path = _account_realm(context.get_files_found())
    data_list = []

    for row in _rows(source_path, 'class_ServerFriend'):
        data_list.append((
            convert_unix_ts_to_utc(row.get('timestamp')),
            convert_unix_ts_to_utc(row.get('lastOnlineTime')),
            convert_unix_ts_to_utc(row.get('birthday')),
            row.get('justalkId'),
            row.get('name'),
            row.get('nickName'),
            row.get('uid'),
            row.get('phone'),
            row.get('gender'),
            row.get('loginCountry'),
            row.get('version'),
            row.get('packageName'),
            row.get('avatarUrl'),
            row.get('relationType'),
            row.get('serverRelationType'),
            row.get('onlineState'),
            'Yes' if row.get('mute') else 'No',
            'Yes' if row.get('sticky') else 'No',
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Last Online Time', 'datetime'),
        ('Birthday', 'datetime'),
        'JusTalk ID',
        'Name',
        'Nickname',
        'UID',
        'Phone',
        'Gender',
        'Login Country (as stored)',
        'Client Version',
        'Package Name',
        ('Avatar URL', 'url'),
        'Relation Type (as stored)',
        'Server Relation Type (as stored)',
        'Online State (as stored)',
        'Muted',
        'Pinned',
    )
    return data_headers, data_list, source_path


def _profile_user(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('provisions.xml'):
            continue
        try:
            general = ET.parse(file_found).getroot().find('GENERAL')
        except (ET.ParseError, OSError):
            continue
        if general is not None:
            return general.get('cur_prof_user', ''), file_found
    return '', ''


@artifact_processor
def justalk_account(context):
    files_found = context.get_files_found()
    source_path = _account_realm(files_found)
    data_list = []

    profile_user, profile_path = _profile_user(files_found)
    if not source_path and not profile_user:
        return _account_headers(), data_list, ''

    counts = {}
    if source_path:
        for section in ('active', 'inactive'):
            total = 0
            for class_name in ('class_CallLog', 'class_ROFileUrl', 'class_ServerFriend',
                               'class_Conversation'):
                try:
                    total += len(list(realm_rows(source_path, class_name, section=section)))
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            counts[section] = total

    metadata = _rows(source_path, 'metadata')
    account_uid = os.path.basename(source_path)[:-len('.realm')] if source_path else ''

    data_list.append((
        account_uid,
        profile_user,
        metadata[0].get('version') if metadata else '',
        counts.get('active', ''),
        counts.get('inactive', ''),
        'Yes' if counts and counts.get('active') != counts.get('inactive') else 'No',
        source_path,
        profile_path,
    ))

    return _account_headers(), data_list, source_path or profile_path


def _account_headers():
    return (
        'Account UID',
        'Profile User Name',
        'Realm Schema Version',
        'Rows in Committed View',
        'Rows in Uncommitted View',
        'Views Differ',
        'Realm Store Path',
        'Provisioning File Path',
    )
