__artifacts_v2__ = {
    "tinderMessages": {
        "name": "Tinder - Messages",
        "description": "Chat messages from the message table of the Tinder database tinder-3.db, "
                       "with the direction, the matched person's name and the delivery fields",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "Direction is derived, not stored. The match_person table holds the profiles of "
                 "matched accounts and the match table links each match to one of them through "
                 "person_id. A message whose from_id equals that person_id is reported as Incoming; "
                 "a message whose to_id equals it is reported as Outgoing. In the tested images "
                 "every message row satisfied exactly one of the two comparisons, and on Outgoing "
                 "rows from_id equalled the account identifier held in files/datastore/id. A row "
                 "matching neither comparison is reported with a blank Direction.\n"
                 "Sender Name is the matched person's stored name on Incoming rows and the profile "
                 "name from files/datastore/user on Outgoing rows; it is blank when those sources "
                 "are absent. Timestamps are stored as epoch milliseconds. The type and "
                 "delivery_status columns are reported as stored; in the tested images type was "
                 "'UNKNOWN' and delivery_status was 'SUCCESS' on every row, and nothing in the "
                 "extraction documents their other values. A match whose messages were "
                 "removed reports no rows here; an empty result is not evidence no messages were "
                 "ever exchanged.",
        "paths": ('*/com.tinder/databases/tinder-3.db*',
                  '*/com.tinder/files/datastore/id',
                  '*/com.tinder/files/datastore/user'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "cookbook_a11": "Android 11 | 15 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Matched Person",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Sent Timestamp",
                "senderColumn": "Sender Name",
            }
        },
    },
    "tinderMatches": {
        "name": "Tinder - Matches",
        "description": "Matches from the match and match_person tables of the Tinder database "
                       "tinder-3.db, with the matched person's profile fields and photo URLs",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "One row per match table entry, joined to the matched person's match_person row. "
                 "creation_date and last_activity_date are stored as epoch milliseconds and are "
                 "reported under those names; this artifact does not interpret what activity "
                 "updates the latter. Birth Date converts the stored birth_date value read as "
                 "epoch milliseconds; values before 1970 are stored as negative numbers and "
                 "convert accordingly.\n"
                 "Gender is a small protobuf whose single varint field is reported as stored; "
                 "nothing in the extraction maps those integers to labels, so none are applied. "
                 "The is_blocked, is_muted, type and attribution columns are also reported as "
                 "stored. Photo URLs are the full-size image URLs from the photos protobuf of the "
                 "match_person row; the URLs are reported as text and are not fetched.\n"
                 "The jobs, schools and city columns of match_person were empty in every tested "
                 "image and are not reported. A sample with them populated would be welcome.",
        "paths": ('*/com.tinder/databases/tinder-3.db*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "cookbook_a11": "Android 11 | 23 rows",
        },
    },
    "tinderAccount": {
        "name": "Tinder - Account",
        "description": "Account identity from the Tinder datastore files account, accountinfo, id "
                       "and user, with the profile fields the app stores for its own user",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "One row per com.tinder data directory. The files/datastore files are Jetpack "
                 "DataStore protobufs with no published schema, so fields are reported by "
                 "position: the email and phone number come from files/datastore/account, the "
                 "account identifier from files/datastore/id, and the name, birth date, bio, "
                 "gender, sexual orientation, job, school, city and photo URLs from "
                 "files/datastore/user. Where the store pairs a code with a display string (for "
                 "example gen_1 with a gender label) both are reported as stored.\n"
                 "Accountinfo Timestamp 1-1 and 1-2-1 name the protobuf field paths they are read "
                 "from; their meaning is not documented in the extraction. In the three tested "
                 "images the 1-1 value equalled, to the second, the timestamp embedded in the "
                 "first four bytes of the account identifier, and the 1-2-1 value fell within "
                 "hours of the newest activity elsewhere in the extraction. Both observations are "
                 "reported here so the reader can weigh them; neither is a documented meaning.\n"
                 "Last Activity Date is the single value of the last_activity_date table in "
                 "tinder-3.db, reported under the table's own name. All timestamps are epoch "
                 "milliseconds.",
        "paths": ('*/com.tinder/files/datastore/account',
                  '*/com.tinder/files/datastore/accountinfo',
                  '*/com.tinder/files/datastore/id',
                  '*/com.tinder/files/datastore/user',
                  '*/com.tinder/databases/tinder-3.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "cookbook_a11": "Android 11 | 1 row",
        },
    },
    "tinderInboxMessages": {
        "name": "Tinder - Inbox Messages",
        "description": "Rows from the inbox_message table of the Tinder database tinder-3.db, "
                       "with the message body, sent time, seen flag and campaign fields",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "These are not user-to-user chat messages; those are in the Tinder - Messages "
                 "artifact. In the tested public image the inbox_message bodies were notices "
                 "from Tinder itself, carrying campaign and experiment identifiers. sent_date is "
                 "epoch milliseconds; type and seen are reported as stored.",
        "paths": ('*/com.tinder/databases/tinder-3.db*',),
        "output_types": "standard",
        "artifact_icon": "inbox",
        "sample_data": {
            "cookbook_a11": "Android 11 | 3 rows",
        },
    },
    "tinderProfilePhotos": {
        "name": "Tinder - Profile Photos",
        "description": "Image files from the Tinder files/ProfilePhotos directory, checked in as "
                       "media with their file names and sizes",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Tinder",
        "notes": "A listing of the files present in files/ProfilePhotos, with the content shown. "
                 "File names are UUIDs with no extension; the content is sniffed from the file "
                 "header, and every tested file was a JPEG. In the tested images these file "
                 "names did not match the photo identifiers of the published profile photos in "
                 "files/datastore/user, so no link between the two is asserted. No timestamp is "
                 "reported: the on-disk times available here depend on the extraction. An empty "
                 "result means the directory held no files in the image, not that the account "
                 "had no photos.",
        "paths": ('*/com.tinder/files/ProfilePhotos/*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "cookbook_a11": "Android 11 | 2 rows",
        },
    },
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, check_in_media, decode_protobuf, logfunc, \
    open_sqlite_db_readonly

# blackboxprotobuf raises these when a blob does not decode as protobuf.
_PB_ERRORS = (ValueError, TypeError, IndexError, KeyError, AttributeError)

_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def _ms_to_utc(value):
    '''Epoch milliseconds to a UTC datetime. Handles the negative values Tinder stores for
    pre-1970 birth dates, which fromtimestamp() rejects on some platforms.'''
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return ''
    if ms == 0:
        return ''
    try:
        return _EPOCH + datetime.timedelta(milliseconds=ms)
    except OverflowError:
        return ''


def _tinder_root(file_found):
    '''The path of the com.tinder directory a found file belongs to, or '' if the
    path does not contain one.'''
    path = str(file_found).replace('\\', '/')
    marker = '/com.tinder/'
    index = path.rfind(marker)
    if index == -1:
        return ''
    return path[:index + len(marker) - 1]


def _group_by_root(files_found):
    groups = {}
    for file_found in files_found:
        root = _tinder_root(file_found)
        if root:
            groups.setdefault(root, []).append(str(file_found))
    return groups


def _find(files, *suffixes):
    for f in files:
        if f.replace('\\', '/').endswith(suffixes):
            return f
    return ''


def _rows(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Tinder: query failed on {source_path}: {ex}')
        return []
    finally:
        db.close()


def _decode(data):
    if not data:
        return {}
    try:
        message, _ = decode_protobuf(data)
    except _PB_ERRORS:
        return {}
    return message if isinstance(message, dict) else {}


def _decode_file(path):
    if not path or not os.path.isfile(path):
        return {}
    try:
        with open(path, 'rb') as f:
            return _decode(f.read())
    except OSError:
        return {}


def _pb_get(node, key):
    '''Read one field out of a blackboxprotobuf dict.

    blackboxprotobuf splits a field whose repeats decode to different typedefs into
    'N-1', 'N-2' keys, so fall back to the first such variant when the plain key is absent.
    '''
    if not isinstance(node, dict):
        return None
    if key in node:
        return node[key]
    for name in sorted(node):
        if name.startswith(f'{key}-'):
            return node[name]
    return None


def _pb_list(node, key):
    value = _pb_get(node, key)
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _pb_walk(node, *path):
    current = node
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        current = _pb_get(current, key)
    if isinstance(current, list):
        current = current[0] if current else None
    return current


def _pb_text(node, *path):
    value = _pb_walk(node, *path)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    return ''


def _photo_urls(photos_node):
    '''Full-size URLs from a repeated photo message (field 1 of each entry).'''
    urls = []
    for photo in photos_node if isinstance(photos_node, list) else [photos_node]:
        url = _pb_text(photo, '1')
        if url:
            urls.append(url)
    return urls


def _code_and_label(node):
    '''A 'code (label)' string from a message holding a code in field 1 and a display
    string in field 2, reporting whichever halves decode as text.'''
    parts = []
    for entry in node if isinstance(node, list) else [node]:
        code = _pb_text(entry, '1')
        label = _pb_text(entry, '2')
        if code and label:
            parts.append(f'{code} ({label})')
        elif code or label:
            parts.append(code or label)
    return '; '.join(parts)


def _sniffed_extension(path):
    try:
        with open(path, 'rb') as f:
            magic = f.read(16)
    except OSError:
        return None
    if magic.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if magic.startswith(b'\x89PNG'):
        return '.png'
    if magic.startswith(b'RIFF') and b'WEBP' in magic:
        return '.webp'
    if magic.startswith(b'GIF8'):
        return '.gif'
    if b'ftyp' in magic:
        return '.mp4'
    return None


@artifact_processor
def tinderMessages(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for _root, files in sorted(_group_by_root(files_found).items()):
        source_path = _find(files, 'tinder-3.db')
        if not source_path:
            continue
        own_name = _pb_text(_decode_file(_find(files, 'datastore/user')), '1', '6')
        rows = _rows(source_path, '''
            SELECT message.sent_date, match.person_id, match_person.name,
                   message.from_id, message.to_id, message.text, message.type,
                   message.delivery_status, message.is_liked, message.is_seen,
                   message.id, message.match_id
            FROM message
            LEFT JOIN `match` ON message.match_id = `match`.id
            LEFT JOIN match_person ON `match`.person_id = match_person.id
            ORDER BY message.sent_date
        ''')
        if rows:
            sources.append(source_path)
        for (sent_date, person_id, person_name, from_id, to_id, text, msg_type,
             delivery_status, is_liked, is_seen, message_id, match_id) in rows:
            if person_id and from_id == person_id:
                direction = 'Incoming'
                sender_name = person_name or ''
            elif person_id and to_id == person_id:
                direction = 'Outgoing'
                sender_name = own_name
            else:
                direction = ''
                sender_name = ''
            data_list.append((
                _ms_to_utc(sent_date),
                direction,
                person_name or '',
                sender_name,
                text,
                msg_type,
                delivery_status,
                is_liked,
                is_seen,
                from_id,
                to_id,
                person_id or '',
                message_id,
                match_id,
            ))

    data_headers = (
        ('Sent Timestamp', 'datetime'),
        'Direction',
        'Matched Person',
        'Sender Name',
        'Message',
        'Type (as stored)',
        'Delivery Status (as stored)',
        'Is Liked (as stored)',
        'Is Seen (as stored)',
        'Sender ID',
        'Recipient ID',
        'Matched Person ID',
        'Message ID',
        'Match ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tinderMatches(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for _root, files in sorted(_group_by_root(files_found).items()):
        source_path = _find(files, 'tinder-3.db')
        if not source_path:
            continue
        rows = _rows(source_path, '''
            SELECT `match`.creation_date, `match`.last_activity_date, match_person.name,
                   match_person.bio, match_person.birth_date, match_person.gender,
                   match_person.membership_status, `match`.is_blocked, `match`.is_muted,
                   `match`.type, `match`.attribution, match_person.photos,
                   `match`.person_id, `match`.id
            FROM `match`
            LEFT JOIN match_person ON `match`.person_id = match_person.id
            ORDER BY `match`.creation_date
        ''')
        if rows:
            sources.append(source_path)
        for (creation_date, last_activity, name, bio, birth_date, gender_blob,
             membership_status, is_blocked, is_muted, match_type, attribution,
             photos_blob, person_id, match_id) in rows:
            gender = _pb_get(_decode(gender_blob), '1')
            urls = _photo_urls(_pb_list(_decode(photos_blob), '1'))
            data_list.append((
                _ms_to_utc(creation_date),
                _ms_to_utc(last_activity),
                name or '',
                _ms_to_utc(birth_date),
                bio or '',
                gender if gender is not None else '',
                membership_status or '',
                is_blocked,
                is_muted,
                match_type,
                attribution,
                len(urls),
                '; '.join(urls),
                person_id or '',
                match_id,
            ))

    data_headers = (
        ('Match Creation Date', 'datetime'),
        ('Last Activity Date', 'datetime'),
        'Matched Person',
        ('Birth Date', 'datetime'),
        'Bio',
        'Gender (as stored)',
        'Membership Status (as stored)',
        'Is Blocked (as stored)',
        'Is Muted (as stored)',
        'Match Type (as stored)',
        'Attribution (as stored)',
        'Photo Count',
        'Photo URLs',
        'Matched Person ID',
        'Match ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tinderAccount(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for _root, files in sorted(_group_by_root(files_found).items()):
        account = _decode_file(_find(files, 'datastore/account'))
        accountinfo = _decode_file(_find(files, 'datastore/accountinfo'))
        account_id = _decode_file(_find(files, 'datastore/id'))
        user = _pb_get(_decode_file(_find(files, 'datastore/user')), '1')
        db_path = _find(files, 'tinder-3.db')
        last_activity_rows = _rows(db_path, 'SELECT last_activity_date FROM last_activity_date')

        user_id = _pb_text(account_id, '1', '1') or _pb_text(user, '1')
        email = _pb_text(account, '1', '1', '1')
        phone = _pb_text(account, '1', '4', '1') or _pb_text(accountinfo, '1', '3', '1')
        if not (user_id or email or phone or user):
            continue
        for f in ('datastore/account', 'datastore/accountinfo', 'datastore/id',
                  'datastore/user'):
            found = _find(files, f)
            if found:
                sources.append(found)

        data_list.append((
            _ms_to_utc(_pb_walk(accountinfo, '1', '1')),
            _ms_to_utc(_pb_walk(accountinfo, '1', '2', '1')),
            _ms_to_utc(last_activity_rows[0][0]) if last_activity_rows else '',
            user_id,
            _pb_text(user, '6'),
            _ms_to_utc(_pb_walk(user, '4', '1')),
            email,
            phone,
            _code_and_label(_pb_list(user, '12')) or _pb_text(user, '5', '2', '1'),
            _code_and_label(_pb_list(user, '11')),
            _pb_text(user, '3', '1'),
            ' '.join(part for part in (_pb_text(user, '8', '5', '1'),
                                       _pb_text(user, '8', '2', '1')) if part),
            _pb_text(user, '9', '1'),
            ', '.join(part for part in (_pb_text(user, '10', '1'),
                                        _pb_text(user, '10', '2', '1')) if part),
            '; '.join(_photo_urls(_pb_list(user, '7'))),
        ))

    data_headers = (
        ('Accountinfo Timestamp 1-1 (as stored)', 'datetime'),
        ('Accountinfo Timestamp 1-2-1 (as stored)', 'datetime'),
        ('Last Activity Date', 'datetime'),
        'User ID',
        'Name',
        ('Birth Date', 'datetime'),
        'Email',
        'Phone Number',
        'Gender (as stored)',
        'Sexual Orientation (as stored)',
        'Bio',
        'Job (as stored)',
        'School',
        'City (as stored)',
        'Profile Photo URLs',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tinderInboxMessages(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for _root, files in sorted(_group_by_root(files_found).items()):
        source_path = _find(files, 'tinder-3.db')
        if not source_path:
            continue
        rows = _rows(source_path, '''
            SELECT sent_date, body, type, seen, campaign_id, experiment_name, variant_name,
                   message_id, segment_id
            FROM inbox_message
            ORDER BY sent_date
        ''')
        if rows:
            sources.append(source_path)
        for (sent_date, body, msg_type, seen, campaign_id, experiment_name,
             variant_name, message_id, segment_id) in rows:
            data_list.append((
                _ms_to_utc(sent_date),
                body or '',
                msg_type,
                seen,
                campaign_id or '',
                experiment_name or '',
                variant_name or '',
                message_id,
                segment_id,
            ))

    data_headers = (
        ('Sent Timestamp', 'datetime'),
        'Body',
        'Type (as stored)',
        'Seen (as stored)',
        'Campaign ID',
        'Experiment Name',
        'Variant Name',
        'Message ID',
        'Segment ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tinderProfilePhotos(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in sorted(str(f) for f in files_found):
        if not os.path.isfile(file_found):
            continue
        source_path = os.path.dirname(file_found)
        media_ref = check_in_media(file_found, os.path.basename(file_found),
                                   force_extension=_sniffed_extension(file_found))
        data_list.append((
            media_ref or '',
            os.path.basename(file_found),
            os.path.getsize(file_found),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Photo', 'media'),
        'File Name',
        'File Size (bytes)',
        'Path',
    )
    return data_headers, data_list, source_path
