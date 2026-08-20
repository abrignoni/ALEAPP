__artifacts_v2__ = {
    "threads_accounts": {
        "name": "Threads - Accounts",
        "description": "Parses the Threads accounts the Android app recorded on the device, "
                       "with the account it was last using.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Threads",
        "notes": "One row per account the app recorded. Account identifiers are read from "
                 "the app's own preference files, and the user name and profile picture "
                 "address from the backup preference file, which is the only store in the "
                 "tested extraction that carried them; an account present in one and not the "
                 "other is still reported, with the missing fields empty. Current and Last "
                 "Seen mark which account the app recorded as selected and which it recorded "
                 "as previously selected. Field mapping was done against a private sample "
                 "provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.instagram.barcelona/shared_prefs/com.instagram.barcelona_preferences.xml',
            '*/com.instagram.barcelona/shared_prefs/autobackupprefs.xml',
            '*/com.instagram.barcelona/shared_prefs/*_USER_PREFERENCES.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "threads_app_usage": {
        "name": "Threads - App Usage",
        "description": "Parses the foreground intervals the Threads Android app recorded "
                       "for each account, with the time each began and ended.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Threads",
        "notes": "One row per recorded interval. The app keeps one of these stores per "
                 "account and names the file after the account identifier, which is where "
                 "the Account column comes from. Start and End are Unix seconds. Duration is "
                 "the difference between them and is given in seconds. Start Event and End "
                 "Event are integer codes and are reported as stored, because the extraction "
                 "carries no app binary and nothing in it maps them to a meaning. The store "
                 "records its own last eviction time, so the earliest interval present is "
                 "bounded by that rather than by when the app was installed; that time is "
                 "reported on every row of the store it came from. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded "
                 "for it.",
        "paths": (
            '*/com.instagram.barcelona/databases/time_in_app_*.db*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "clock"
    },
    "threads_feed_items": {
        "name": "Threads - Cached Feed Items",
        "description": "Parses the Threads posts the Android app held in its per account "
                       "feed store, including the author, the text and the time each post "
                       "was made.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Threads",
        "notes": "One row per post inside a stored feed item. These are posts by other "
                 "people that the app held for the account named in the store's file name, "
                 "not posts made by the account holder. Source is the value the row carries "
                 "for how the item arrived and read background_prefetch on the tested "
                 "device, so a row records that the app fetched the item rather than that "
                 "the account holder saw it. Posted is the post's own Unix second timestamp "
                 "and Stored is the Unix millisecond time the app wrote the row. Liked By "
                 "Viewer is the flag the post carries for the account whose store it is. "
                 "Like Count and the account badges are the values the post carries, as "
                 "stored. The images the posts reference were not linked to the app's image "
                 "cache: that cache names its files with a signed integer and neither the "
                 "Java string hash of a stored image address nor of its path alone matched "
                 "any of them, so no reproducible link was found and no media column is "
                 "offered. Field mapping was done against a private sample provided by "
                 "Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.instagram.barcelona/databases/barcelona_feed_items_room_db_*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "message-circle"
    },
}

import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.instagram.barcelona'
_USAGE_NAME = re.compile(r'^time_in_app_(\d+)\.db$')
_FEED_NAME = re.compile(r'^barcelona_feed_items_room_db_(\d+)$')


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate. Every
    index this module builds is keyed on it together with the account, because this app
    keeps one store per account and two app data directories can hold the same account.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context):
    '''{container key: [path]} for the files this artifact matched.'''
    grouped = {}
    for file_found in unique_files(context):
        grouped.setdefault(_container(context, file_found), []).append(str(file_found))
    return grouped


def _seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _prefs(source_path):
    '''{name: text} for an Android shared preferences file.'''
    values = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Threads: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _open(path):
    '''One database opened read only, or None.'''
    try:
        return open_sqlite_db_readonly(get_sqlite_db_path(path))
    except sqlite3.Error as ex:
        logfunc(f'Threads: could not open {os.path.basename(path)}: {ex}')
        return None


def _rows(database, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    if database is None:
        return []
    try:
        cursor = database.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Threads: could not read from the database: {ex}')
        return []


def _document(blob):
    '''The JSON document held in a stored blob, or None when it does not parse.'''
    if isinstance(blob, (bytes, bytearray)):
        blob = bytes(blob).decode('utf-8', 'replace')
    try:
        return json.loads(blob)
    except (TypeError, ValueError):
        return None


@artifact_processor
def threads_accounts(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        general = {}
        backup = {}
        per_account = set()
        relative_paths = []
        for path in paths:
            name = os.path.basename(path)
            if name == 'com.instagram.barcelona_preferences.xml':
                general = _prefs(path)
                relative_paths.append(context.get_relative_path(path))
            elif name == 'autobackupprefs.xml':
                backup = _prefs(path)
                relative_paths.append(context.get_relative_path(path))
            elif name.endswith('_USER_PREFERENCES.xml'):
                per_account.add(name.split('_USER_PREFERENCES.xml')[0])

        listed = {}
        stored = _document(backup.get('cloud_account_user_map', '')) or {}
        for entry in stored.get('cloud_accounts_list') or []:
            if isinstance(entry, dict) and entry.get('user_id'):
                listed[str(entry['user_id'])] = entry

        current = str(general.get('current_user_id', '') or '')
        last_seen = str(general.get('last_seen_user_id', '') or '')
        known = set(listed) | per_account | {a for a in (current, last_seen) if a}
        if not known:
            continue

        for account in sorted(known):
            entry = listed.get(account, {})
            source_files.extend(relative_paths)
            data_list.append((
                account,
                str(entry.get('username', '')),
                str(entry.get('profile_pic_url', '')),
                'Yes' if account == current else '',
                'Yes' if account == last_seen else '',
                'Yes' if account in per_account else '',
                '; '.join(relative_paths),
            ))

    data_headers = (
        'Account ID',
        'User Name',
        'Profile Picture Address',
        'Current Account',
        'Last Seen Account',
        'Has Preference File',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def threads_app_usage(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for path in paths:
            match = _USAGE_NAME.match(os.path.basename(path))
            if not match:
                continue
            account = match.group(1)
            database = _open(path)
            if database is None:
                continue
            relative = context.get_relative_path(path)
            evicted = ''
            for key, value in _rows(database, 'SELECT key, value FROM metadata'):
                if key == 'last_eviction_timestamp':
                    evicted = value

            for row in _rows(database, '''SELECT start_walltime, end_walltime, start_event,
                                                 end_event, start_uptime, end_uptime, seq_num
                                          FROM intervals'''):
                start, end, start_event, end_event, start_uptime, end_uptime, sequence = row
                duration = ''
                if start is not None and end is not None:
                    duration = int(end) - int(start)
                source_files.append(relative)
                data_list.append((
                    _seconds(start),
                    _seconds(end),
                    duration,
                    account,
                    str(start_event if start_event is not None else ''),
                    str(end_event if end_event is not None else ''),
                    str(start_uptime if start_uptime is not None else ''),
                    str(end_uptime if end_uptime is not None else ''),
                    str(sequence if sequence is not None else ''),
                    _seconds(evicted),
                    relative,
                ))
            database.close()

    data_list.sort(key=lambda row: (str(row[0]), str(row[8])), reverse=True)

    data_headers = (
        ('Start', 'datetime'),
        ('End', 'datetime'),
        'Duration (seconds)',
        'Account',
        'Start Event (as stored)',
        'End Event (as stored)',
        'Start Uptime (as stored)',
        'End Uptime (as stored)',
        'Sequence',
        ('Store Last Eviction', 'datetime'),
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def threads_feed_items(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for path in paths:
            match = _FEED_NAME.match(os.path.basename(path))
            if not match:
                continue
            account = match.group(1)
            database = _open(path)
            if database is None:
                continue
            relative = context.get_relative_path(path)

            columns = {row[1] for row in _rows(database, 'PRAGMA table_info(barcelona_user_feed_items)')}
            selected = ['id', 'data', 'media_age', 'stored_age', 'item_type']
            # The column naming how an item arrived was added in a later release, so it is
            # selected only where the store declares it rather than failing the whole read.
            if 'source' in columns:
                selected.append('source')
            statement = f'SELECT {", ".join(selected)} FROM barcelona_user_feed_items'

            for row in _rows(database, statement):
                values = dict(zip(selected, row))
                document = _document(values.get('data'))
                thread_id = str(values.get('id') or '')
                items = (document or {}).get('thread_items')
                if not isinstance(items, list) or not items:
                    items = [{}]
                for item in items:
                    post = item.get('post') if isinstance(item, dict) else {}
                    post = post if isinstance(post, dict) else {}
                    user = post.get('user') if isinstance(post.get('user'), dict) else {}
                    caption = post.get('caption') if isinstance(post.get('caption'), dict) else {}
                    source_files.append(relative)
                    data_list.append((
                        _seconds(post.get('taken_at')),
                        _ms(values.get('stored_age')),
                        account,
                        str(user.get('username', '')),
                        str(user.get('full_name', '')),
                        str(caption.get('text', '')),
                        str(post.get('like_count', '')),
                        str(post.get('has_liked', '')),
                        str(post.get('code', '')),
                        str(post.get('media_type', '')),
                        str(user.get('is_verified', '')),
                        str(user.get('is_private', '')),
                        str(user.get('friendship_status', '')),
                        str(user.get('id', '')),
                        str(values.get('item_type') or ''),
                        str(values.get('source') or ''),
                        thread_id,
                        relative,
                    ))
            database.close()

    data_list.sort(key=lambda row: (str(row[0]), str(row[16])), reverse=True)

    data_headers = (
        ('Posted', 'datetime'),
        ('Stored', 'datetime'),
        'Account',
        'Author User Name',
        'Author Full Name',
        'Post Text',
        'Like Count (as stored)',
        'Liked By Viewer (as stored)',
        'Post Code',
        'Media Type (as stored)',
        'Author Verified (as stored)',
        'Author Private (as stored)',
        'Friendship Status (as stored)',
        'Author ID',
        'Item Type (as stored)',
        'Source (as stored)',
        'Thread ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
