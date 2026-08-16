__artifacts_v2__ = {
    "instagramDirectMessages": {
        "name": "Instagram - Direct Messages",
        "description": "Direct messages from the messages table of the Instagram database "
                       "direct.db, with the direction, the sender's username and the media URL "
                       "for media messages",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Instagram",
        "notes": "Each messages row holds a JSON copy of the message; the text, sender, item "
                 "type and media fields are read from it. Its thread_key and timestamp fields "
                 "agreed with the table's own thread_id and timestamp columns on every tested "
                 "row. Timestamps are stored as epoch microseconds.\n"
                 "Direction is derived: the session table of the same database holds the "
                 "signed-in account's user id, and a message whose JSON user_id equals it is "
                 "reported as Outgoing, otherwise Incoming. Sender Username resolves the JSON "
                 "user_id against the participant list in the thread's thread_info JSON, and "
                 "for the signed-in account against the preferences file named in the paths; "
                 "it is blank when neither source carries the id.\n"
                 "Item Type is reported as stored. Rows typed video_call_event are reported by "
                 "the Instagram - Direct Call Events artifact, not here. Rows typed media carry "
                 "no text; their Media URL column holds the first image or video candidate URL "
                 "from the JSON, with the media's stored taken_at time and owner where present. "
                 "The URLs are reported as text and are not fetched. No cached copy of any "
                 "direct-message media was locatable in the tested images by media id or URL "
                 "file name, so no media is rendered; absence of a cached copy is a property "
                 "of these extractions, not proof the media never existed on the device.\n"
                 "In newer images the app stores direct messages elsewhere and this database "
                 "holds none; a zero-row result is not evidence no messages existed.",
        "paths": ('*/com.instagram.android/databases/direct.db*',
                  '*/com.instagram.android/shared_prefs/com.instagram.android_preferences.xml'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "pixel3_a11": "Android 11 | 20 rows",
            "pixel3_a12": "Android 12 | 22 rows",
            "samsungs20_a13": "Android 13 | 11 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 2 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 1 row",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Username",
            }
        },
    },
    "instagramDirectCalls": {
        "name": "Instagram - Direct Call Events",
        "description": "Video call events from the messages table of the Instagram database "
                       "direct.db, with the stored action, description and joined flag",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Instagram",
        "notes": "Rows of the messages table whose type is video_call_event. Action, "
                 "Description and Did Join are the stored values of the event JSON; the "
                 "description is the app's own wording (for example 'You started a video "
                 "chat'). Timestamps are epoch microseconds. Direction follows the same "
                 "session-table derivation as the Instagram - Direct Messages artifact. An "
                 "event row is not a call log; start and end appear as separate rows where "
                 "the app recorded both.",
        "paths": ('*/com.instagram.android/databases/direct.db*',
                  '*/com.instagram.android/shared_prefs/com.instagram.android_preferences.xml'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "pixel3_a11": "Android 11 | 8 rows",
            "pixel3_a12": "Android 12 | 6 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
        },
    },
    "instagramDirectThreads": {
        "name": "Instagram - Direct Threads",
        "description": "Conversation threads from the threads table of the Instagram database "
                       "direct.db, with the participants, the inviter and the last activity "
                       "time",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Instagram",
        "notes": "One row per threads table entry. Participants and the inviter are read from "
                 "the thread_info JSON as username (full name) pairs; the signed-in account is "
                 "not listed among the participants by the app. Last Activity Time is the "
                 "table's own column, stored as epoch microseconds. Thread Title is the stored "
                 "title, which the app may derive from the participant names.",
        "paths": ('*/com.instagram.android/databases/direct.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 3 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 1 row",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
        },
    },
    "instagramAccounts": {
        "name": "Instagram - Accounts",
        "description": "Signed-in account profiles from the Instagram shared preferences file "
                       "com.instagram.android_preferences.xml, with the username, user id and "
                       "profile fields",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Instagram",
        "notes": "Parses the account JSON the app keeps in the 'current' and 'user_access_map' "
                 "preference keys; entries from both are reported and the Source Key column "
                 "says which one a row came from, so the same account can appear twice with "
                 "different levels of detail. The user id is the JSON id, instagram_pk or pk "
                 "field, whichever is present. Follower Count, Following Count, Biography and "
                 "External URL are only stored in the user_access_map entries of some app "
                 "versions and are blank elsewhere; a blank is absence from the file, not a "
                 "zero. Account Type is reported as stored; nothing in the extraction maps "
                 "its values.",
        "paths": ('*/com.instagram.android/shared_prefs/com.instagram.android_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 2 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "samsungs20_a13": "Android 13 | 4 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "pixel7a_a14": "Android 14 | 2 rows",
            "samsunga53_a14": "Android 14 | 2 rows",
            "sharon_a14": "Android 14 | 2 rows",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
        },
    },
    "instagramContacts": {
        "name": "Instagram - Contacts",
        "description": "Contacts from the contacts table of the Instagram database "
                       "ig_msys_database, with names, usernames, phone numbers, email "
                       "addresses and block state as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Instagram",
        "notes": "The per-account ig_msys_database_<number> is plain SQLite in the tested "
                 "images and its contacts table carries named columns, which are reported "
                 "under their own names. The integer columns contact_type, "
                 "blocked_by_viewer_status and gender are reported as stored; nothing in the "
                 "extraction maps their values. Blocked Since converts "
                 "blocked_since_timestamp_ms where present. The WAL sidecar is load-bearing "
                 "for this database: in one tested image five contacts existed only in the "
                 "WAL, so the sidecars must travel with the database.\n"
                 "A contact row is an entry in the app's local contact store. Its presence "
                 "does not establish that the account holder communicated with, followed or "
                 "knew the listed account.",
        "paths": ('*/com.instagram.android/databases/ig_msys_database_*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 4 rows",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 58 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
        },
    },
    "instagramTimeInApp": {
        "name": "Instagram - Time In App",
        "description": "App usage intervals from the intervals table of the Instagram database "
                       "time_in_app_<user id>.db, with the start and end times and the stored "
                       "event codes",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Instagram",
        "notes": "One row per intervals table entry. start_walltime and end_walltime are "
                 "stored as epoch seconds. The start_event and end_event integers are "
                 "reported as stored; nothing in the extraction maps them. The user id in "
                 "the User ID column is taken from the database file name. An interval is a "
                 "record the app wrote about its own foreground time; this artifact does not "
                 "interpret what activity occurred within it.",
        "paths": ('*/com.instagram.android/databases/time_in_app_*.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 40 rows",
            "pixel3_a11": "Android 11 | 211 rows",
            "pixel3_a12": "Android 12 | 452 rows",
            "samsungs20_a13": "Android 13 | 38 rows",
            "sharon_a13": "Android 13 | 104 rows",
            "pixel7a_a14": "Android 14 | 25 rows",
            "samsunga53_a14": "Android 14 | 55 rows",
            "sharon_a14": "Android 14 | 92 rows",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 70 rows",
            "hc_pixel8pro_a16": "Android 16 | 113 rows",
            "hc_pixel8pro_a17": "Android 17 | 142 rows",
        },
    },
}

import datetime
import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def _epoch_to_utc(value, unit_divisor):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number == 0:
        return ''
    try:
        return _EPOCH + datetime.timedelta(seconds=number / unit_divisor)
    except OverflowError:
        return ''


def _us_to_utc(value):
    return _epoch_to_utc(value, 1_000_000)


def _ms_to_utc(value):
    return _epoch_to_utc(value, 1_000)


def _s_to_utc(value):
    return _epoch_to_utc(value, 1)


def _rows(source_path, sql, params=()):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    try:
        return db.execute(sql, params).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Instagram: query failed on {source_path}: {ex}')
        return []
    finally:
        db.close()


def _loads(raw):
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


# /data/user/<n>/ and /data_mirror/data_ce/null/<n>/ are bind mounts of /data/data;
# extractions that keep more than one view carry the same app directory two or
# three times.
_MIRROR_PREFIXES = re.compile(r'/data/user/\d+/|/data_mirror/data_[a-z]+/null/\d+/')


def _dedupe_mirrored(paths):
    '''Report each app file once when an extraction holds several mirror views of
    it, preferring the /data/data/ copy.'''
    normalized_seen = {}
    for path in sorted(paths):
        forward = path.replace('\\', '/')
        normalized = _MIRROR_PREFIXES.sub('/data/data/', forward)
        preferred = normalized_seen.get(normalized)
        if preferred is None or _MIRROR_PREFIXES.search(preferred.replace('\\', '/')):
            normalized_seen[normalized] = path
    return sorted(normalized_seen.values())


def _files_ending(files_found, *suffixes):
    return _dedupe_mirrored(str(f) for f in files_found
                            if str(f).replace('\\', '/').endswith(suffixes))


def _direct_dbs(files_found):
    return _files_ending(files_found, '/direct.db')


def _account_entries(file_found):
    '''(source key, account dict) pairs from a com.instagram.android_preferences.xml.'''
    try:
        root = ET.parse(file_found).getroot()
    except ET.ParseError as ex:
        logfunc(f'Instagram: unparseable preferences XML {file_found}: {ex}')
        return []
    entries = []
    for item in root:
        key = item.attrib.get('name')
        if key not in ('current', 'user_access_map'):
            continue
        try:
            parsed = json.loads(item.text or '')
        except (ValueError, TypeError):
            continue
        if isinstance(parsed, dict):
            entries.append((key, parsed))
        elif isinstance(parsed, list):
            for element in parsed:
                if isinstance(element, dict):
                    entries.append((key, element.get('user_info', element)))
    return [(key, user) for key, user in entries if isinstance(user, dict)]


def _account_username_map(files_found):
    '''user id -> username for every signed-in account found in the preferences.'''
    usernames = {}
    for file_found in _files_ending(files_found,
                                    'com.instagram.android_preferences.xml'):
        for _key, user in _account_entries(file_found):
            user_id = str(user.get('id') or user.get('instagram_pk')
                          or user.get('pk') or '')
            if user_id and user.get('username'):
                usernames.setdefault(user_id, user['username'])
    return usernames


def _session_user_id(source_path):
    rows = _rows(source_path, 'SELECT user_id FROM session')
    return str(rows[0][0]) if rows else ''


def _participants(info):
    '''The participant dicts of a thread_info JSON, inviter included. The list key
    is recipients in the tested generations; users is accepted as well.'''
    participants = []
    for key in ('recipients', 'users'):
        value = info.get(key)
        if isinstance(value, list):
            participants.extend(value)
    inviter = info.get('inviter')
    if isinstance(inviter, dict):
        participants.append(inviter)
    return [user for user in participants if isinstance(user, dict)]


def _participant_id(user):
    return str(user.get('pk') or user.get('pk_id') or user.get('id') or '')


def _thread_maps(source_path):
    '''Per thread_id: a display title, and user_id -> username from thread_info.'''
    titles = {}
    users = {}
    for thread_id, info_raw in _rows(
            source_path, 'SELECT thread_id, thread_info FROM threads'):
        info = _loads(info_raw)
        members = {}
        names = []
        for user in _participants(info):
            pk = _participant_id(user)
            username = user.get('username') or ''
            if pk and pk not in members:
                members[pk] = username
                if username:
                    names.append(username)
        title = info.get('thread_title') or ', '.join(sorted(set(names)))
        titles[str(thread_id)] = title
        users[str(thread_id)] = members
    return titles, users


def _media_fields(message):
    '''(media url, taken_at datetime, owner username) for a media message.'''
    media = message.get('media')
    if not isinstance(media, dict):
        return '', '', ''
    url = ''
    for key in ('image_versions2', 'video_versions'):
        value = media.get(key)
        candidates = value.get('candidates') if isinstance(value, dict) else value
        if isinstance(candidates, list) and candidates:
            first = candidates[0]
            if isinstance(first, dict) and first.get('url'):
                url = first['url']
                break
    owner = media.get('user')
    owner_name = owner.get('username', '') if isinstance(owner, dict) else ''
    return url, _s_to_utc(media.get('taken_at')), owner_name


@artifact_processor
def instagramDirectMessages(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    account_usernames = _account_username_map(files_found)
    for source_path in _direct_dbs(files_found):
        own_id = _session_user_id(source_path)
        titles, users = _thread_maps(source_path)
        rows = _rows(source_path, '''
            SELECT timestamp, thread_id, message_type, text, message
            FROM messages WHERE message_type != 'video_call_event'
            ORDER BY timestamp
        ''')
        if rows:
            sources.append(source_path)
        for timestamp, thread_id, message_type, text, message_raw in rows:
            message = _loads(message_raw)
            sender_id = str(message.get('user_id') or '')
            direction = ''
            if own_id and sender_id:
                direction = 'Outgoing' if sender_id == own_id else 'Incoming'
            thread_id = str(thread_id)
            media_url, media_taken_at, media_owner = _media_fields(message)
            data_list.append((
                _us_to_utc(timestamp),
                direction,
                titles.get(thread_id, ''),
                users.get(thread_id, {}).get(sender_id)
                or account_usernames.get(sender_id, ''),
                text or '',
                message_type,
                message.get('content_type', ''),
                media_url,
                media_taken_at,
                media_owner,
                sender_id,
                thread_id,
                str(message.get('item_id') or ''),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Thread',
        'Sender Username',
        'Message',
        'Item Type (as stored)',
        'Content Type (as stored)',
        'Media URL',
        ('Media Taken At', 'datetime'),
        'Media Owner Username',
        'Sender ID',
        'Thread ID',
        'Item ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def instagramDirectCalls(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    account_usernames = _account_username_map(files_found)
    for source_path in _direct_dbs(files_found):
        own_id = _session_user_id(source_path)
        titles, users = _thread_maps(source_path)
        rows = _rows(source_path, '''
            SELECT timestamp, thread_id, message
            FROM messages WHERE message_type = 'video_call_event'
            ORDER BY timestamp
        ''')
        if rows:
            sources.append(source_path)
        for timestamp, thread_id, message_raw in rows:
            message = _loads(message_raw)
            event = message.get('video_call_event')
            event = event if isinstance(event, dict) else {}
            sender_id = str(message.get('user_id') or '')
            direction = ''
            if own_id and sender_id:
                direction = 'Outgoing' if sender_id == own_id else 'Incoming'
            thread_id = str(thread_id)
            data_list.append((
                _us_to_utc(timestamp),
                direction,
                titles.get(thread_id, ''),
                users.get(thread_id, {}).get(sender_id)
                or account_usernames.get(sender_id, ''),
                event.get('action', ''),
                event.get('description', ''),
                event.get('did_join', ''),
                event.get('vc_id', ''),
                sender_id,
                thread_id,
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Thread',
        'Sender Username',
        'Action (as stored)',
        'Description (as stored)',
        'Did Join (as stored)',
        'Call ID',
        'Sender ID',
        'Thread ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def instagramDirectThreads(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for source_path in _direct_dbs(files_found):
        rows = _rows(source_path, '''
            SELECT last_activity_time, thread_id, thread_info FROM threads
            ORDER BY last_activity_time
        ''')
        if rows:
            sources.append(source_path)
        for last_activity, thread_id, info_raw in rows:
            info = _loads(info_raw)
            participants = []
            inviter = info.get('inviter')
            inviter = inviter if isinstance(inviter, dict) else {}
            inviter_id = _participant_id(inviter)
            seen = set()
            for user in _participants(info):
                pk = _participant_id(user)
                if pk and (pk in seen or pk == inviter_id):
                    continue
                seen.add(pk)
                username = user.get('username', '')
                full_name = user.get('full_name', '')
                participants.append(f'{username} ({full_name})' if full_name
                                    else username)
            data_list.append((
                _us_to_utc(last_activity),
                info.get('thread_title', ''),
                '; '.join(participants),
                inviter.get('username', ''),
                str(thread_id),
                str(info.get('thread_v2_id') or ''),
            ))

    data_headers = (
        ('Last Activity Time', 'datetime'),
        'Thread Title',
        'Participants',
        'Inviter Username',
        'Thread ID',
        'Thread V2 ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def instagramAccounts(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for file_found in _files_ending(files_found,
                                    'com.instagram.android_preferences.xml'):
        entries = _account_entries(file_found)
        if entries:
            sources.append(file_found)
        for key, user in entries:
            data_list.append((
                user.get('username', ''),
                user.get('full_name', ''),
                str(user.get('id') or user.get('instagram_pk') or user.get('pk') or ''),
                str(user.get('account_type', '')),
                user.get('is_business', ''),
                user.get('is_verified', ''),
                user.get('follower_count', ''),
                user.get('following_count', ''),
                user.get('biography', ''),
                user.get('external_url', ''),
                user.get('profile_pic_url', ''),
                key,
            ))

    data_headers = (
        'Username',
        'Full Name',
        'User ID',
        'Account Type (as stored)',
        'Is Business (as stored)',
        'Is Verified (as stored)',
        'Follower Count',
        'Following Count',
        'Biography',
        'External URL',
        'Profile Pic URL',
        'Source Key',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def instagramContacts(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for source_path in _dedupe_mirrored(
            str(f) for f in files_found
            if not str(f).endswith(('-wal', '-shm', '-journal'))):
        rows = _rows(source_path, '''
            SELECT id, name, first_name, last_name, username, phone_number,
                   email_address, is_messenger_user, contact_type,
                   blocked_by_viewer_status, blocked_since_timestamp_ms,
                   work_company_name, work_job_title, profile_picture_url
            FROM contacts ORDER BY name
        ''')
        if rows:
            sources.append(source_path)
        for (contact_id, name, first_name, last_name, username, phone, email,
             is_messenger_user, contact_type, blocked_status, blocked_since,
             company, job_title, picture_url) in rows:
            data_list.append((
                name or '',
                username or '',
                str(contact_id),
                first_name or '',
                last_name or '',
                phone or '',
                email or '',
                is_messenger_user,
                contact_type,
                blocked_status,
                _ms_to_utc(blocked_since),
                company or '',
                job_title or '',
                picture_url or '',
            ))

    data_headers = (
        'Name',
        'Username',
        'Contact ID',
        'First Name',
        'Last Name',
        'Phone Number',
        'Email Address',
        'Is Messenger User (as stored)',
        'Contact Type (as stored)',
        'Blocked By Viewer Status (as stored)',
        ('Blocked Since', 'datetime'),
        'Work Company Name',
        'Work Job Title',
        'Profile Picture URL',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def instagramTimeInApp(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for source_path in _dedupe_mirrored(str(f) for f in files_found):
        base = os.path.basename(source_path)
        match = re.fullmatch(r'time_in_app_(\d+)\.db', base)
        if not match:
            continue
        user_id = match.group(1)
        rows = _rows(source_path, '''
            SELECT start_walltime, end_walltime, start_event, end_event, seq_num
            FROM intervals ORDER BY start_walltime
        ''')
        if rows:
            sources.append(source_path)
        for start_walltime, end_walltime, start_event, end_event, seq_num in rows:
            data_list.append((
                _s_to_utc(start_walltime),
                _s_to_utc(end_walltime),
                start_event,
                end_event,
                user_id,
                seq_num,
            ))

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        'Start Event (as stored)',
        'End Event (as stored)',
        'User ID',
        'Sequence Number',
    )
    return data_headers, data_list, '\n'.join(sources)
