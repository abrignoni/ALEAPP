__artifacts_v2__ = {
    "pinterest_account": {
        "name": "Pinterest - Account",
        "description": "Parses the signed in account record stored by the Pinterest Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Read from the PREF_MY_USER value of the app's own preferences file, which holds "
                 "the account record as JSON. Account Created and Last Pin Saved are stored as "
                 "formatted text carrying no time zone, so they are reported as stored rather than "
                 "converted. Birthday is a Unix second value; on the tested sample it landed at "
                 "midday UTC, so only its date part is meaningful. A birth date before 1970 is stored "
                 "as a negative value, and this column is seconds rather than milliseconds, so "
                 "it is converted in "
                 "this module rather than inferred from its magnitude. Gender, "
                 "email status and the account type are reported as stored. The counts are the "
                 "values the record carries, not a count of anything parsed from this extraction. "
                 "Field mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.pinterest/shared_prefs/pinterest.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "pinterest_stored_accounts": {
        "name": "Pinterest - Stored Accounts",
        "description": "Parses the accounts held by the Pinterest Android app account switcher.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Each preference entry in the account switcher store is named for an account id "
                 "and holds that account's own record as JSON. The store carries an access token "
                 "and two further tokens per account. These are live account credentials and "
                 "are reported as stored. The tested sample held one "
                 "account, so the multiple account path is code present and unexercised. Field "
                 "mapping was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/com.pinterest/shared_prefs/PREF_MY_USER_USER_ACCOUNTS*',
            '*/com.pinterest/shared_prefs/PREF_ACCUNT_SWITCHER_GROUP_ID.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
    "pinterest_app_state": {
        "name": "Pinterest - App State",
        "description": "Parses selected application state preferences of the Pinterest Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "A selected set of preference keys is reported, one row per key, with the value as "
                 "stored. A key is converted to a timestamp only when its own name states that it "
                 "holds a time and its value is a thirteen digit integer, which is the shape every "
                 "converted value had on the tested sample; every other value is left as text. The "
                 "install referrer and the requested runtime permissions are the values the app "
                 "recorded, not an observation of what was granted. What the app does with each "
                 "preference is not established here, so no meaning is asserted beyond the key name "
                 "the app itself uses. Field mapping was done against a private sample provided by "
                 "Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.pinterest/shared_prefs/pinterest.xml',
            '*/com.pinterest/shared_prefs/pinterest.persist.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "pinterest_search_typeahead_cache": {
        "name": "Pinterest - Search Typeahead Cache",
        "description": "Parses the search typeahead suggestion cache of the Pinterest Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "This store holds suggestions the app downloaded, not terms the user searched for. "
                 "On the tested sample the app's own preferences recorded the partition URL it was "
                 "fetched from on a Pinterest content delivery host, a cache version naming a "
                 "country and gender segment and a dated build, and a single fetch time; the table "
                 "held 25802 rows, all distinct, on a contiguous run of autoincrement ids with no "
                 "gaps, which is one bulk insert. The suggestion text is therefore not reported, "
                 "because a list of server supplied terms presented next to a Pinterest account "
                 "reads as a search history and is not one. The row count and the cache identifiers "
                 "are reported instead, and the suggestions remain in the evidence file, where a "
                 "keyword search of this database will surface them; a hit on one of those strings "
                 "is not evidence that the account holder entered it. Score also decreases "
                 "monotonically with the row id across every row, so the table was written once in "
                 "server rank order, which typed history is not. No store "
                 "holding terms entered by the user was found in the tested sample. The fetch time "
                 "is stored as formatted text carrying its own UTC offset and is reported as "
                 "stored. Field mapping was done against a private sample provided by Mattia; no "
                 "sample data is recorded for it.",
        "paths": (
            '*/com.pinterest/databases/search-typeahead*',
            '*/com.pinterest/shared_prefs/pinterest.persist.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "pinterest_cached_list_pages": {
        "name": "Pinterest - Cached List Pages",
        "description": "Parses cached feed and profile list pages of the Pinterest Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Each file in the app's paged list cache begins with the four bytes 23 06 14 20, "
                 "then a little endian eight byte length and that many bytes of cache key, then a "
                 "second length prefixed string, then eight bytes, then a little endian eight byte "
                 "value, then length prefixed UTF-16 little endian strings. The cache key is ASCII "
                 "and names the list it belongs to; where it carries a nineteen digit run of digits "
                 "that value is reported as the account id, because it matched the signed in "
                 "account id recorded in the app's preferences on the tested sample. The eight byte "
                 "value decoded to a Unix millisecond time in the range of the app's own recorded "
                 "activity on all three tested files, so it is converted, but what event it marks "
                 "is not established and it is labelled only as the timestamp the record carries. "
                 "The trailing strings are reported as stored under Referenced Identifiers; on the "
                 "tested sample they were nineteen digit ids in one file and eight character tokens "
                 "in another, and no source was found that names what either points at. Field "
                 "mapping was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.pinterest/cache/paged_list_cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list"
    },
    "pinterest_cached_images": {
        "name": "Pinterest - Cached Images",
        "description": "Parses and renders the image caches of the Pinterest Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Covers both DiskLruCache stores the app keeps for images, the one under "
                 "image_manager_disk_cache and the one in the cache directory itself. No "
                 "reproducible link from a cached image back to a pin, a board or a URL was found. "
                 "What was checked: the DiskLruCache journal records only the entry key and the "
                 "entry length and carries no URL; the entry key is a SHA-256 over the image "
                 "library's own key object rather than over the URL, and SHA-256, SHA-1, MD5 and "
                 "UTF-16 spellings of the four profile image URLs the account record does hold "
                 "matched none of the 6300 entry names on the tested sample; and the MD5 of every "
                 "cached file matched none of the MD5 values embedded in those URLs, the cached "
                 "bytes being re-encoded variants rather than the original. The entry key is "
                 "reported as stored and the file name is that key followed by .0. Types are taken "
                 "from the leading bytes of each file, not from the name, which carries no "
                 "extension. Raster images are checked in and rendered. A cached SVG is reported "
                 "with its type and not rendered, because an SVG can carry script and these are "
                 "bytes from a remote host. Journal entries whose file is absent are reported with "
                 "an empty media cell, and files present with no journal entry are reported too. "
                 "Field mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/com.pinterest/cache/image_manager_disk_cache/*',
            '*/com.pinterest/cache/*.0',
            '*/com.pinterest/cache/journal',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo"
    },
    "pinterest_cached_videos": {
        "name": "Pinterest - Cached Videos",
        "description": "Parses and renders the video caches of the Pinterest Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Two stores are reported and the Source Store column says which each row came "
                 "from. In the response cache the entry file name is the MD5 of the request URL, "
                 "confirmed by recomputing it for all 13 entries on the tested sample, the first "
                 "line of the .0 file is that URL and the .1 file is the response body, which was a "
                 "complete MP4 in every case, so those are checked in and rendered. Requested and "
                 "Received come from the OkHttp-Sent-Millis and OkHttp-Received-Millis headers the "
                 "cache writes into that entry, in Unix milliseconds on the device clock; the "
                 "server's own date header is reported separately as stored. In the player cache "
                 "the index table maps a cache id to the full media URL and the file metadata table "
                 "names each cached fragment with its length and last touch time in Unix "
                 "milliseconds, and fragment file names begin with that cache id, which resolved "
                 "for all 266 keys and all 1616 fragment rows of the populated index on the tested "
                 "sample. Those fragments are partial CMAF byte ranges rather than playable files, "
                 "so they are reported with their count and cached size and an empty media cell "
                 "rather than rendered. The tested sample also carried a second index whose "
                 "fragment directory was absent, so its rows report a URL with nothing on disk. "
                 "Field mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/com.pinterest/databases/exoplayer_internal.db*',
            '*/com.pinterest/cache/video/response_cache/*',
            '*/com.pinterest/cache/video/media_cache/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "video"
    },
    "pinterest_idea_pin_drafts": {
        "name": "Pinterest - Idea Pin Drafts",
        "description": "Parses unpublished idea pin drafts from the Pinterest Android app database.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Pinterest",
        "notes": "Read from the idea_pin_drafts table of the app's Room database. The file name "
                 "carries a variable suffix, so the path pattern is a prefix match, which also "
                 "picks up the write-ahead log and shared memory sidecars; the tested sample "
                 "carried the unsuffixed spelling. The database is read twice, immutable=1 to "
                 "ignore the write-ahead log and mode=ro to apply it, and the two reads are "
                 "compared on the primary key. Rows returned only by the first read are reported "
                 "with a Source View of Pre-checkpoint. On the tested sample the two reads agreed "
                 "exactly on every table and the table held no rows, so this artifact is code "
                 "present and unexercised against populated data. Columns are selected only where "
                 "the table declares them, so a differing schema version still parses. The "
                 "metadata, page data and extracted image metadata columns hold payloads whose "
                 "structure is not established here, so their presence and length are reported "
                 "rather than a decode. Timestamps are Unix milliseconds. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/com.pinterest/databases/pinterest-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "edit"
    },
}

import json
import os
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_sqlite_db_path,
    get_sqlite_db_records,
    logfunc,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Leading bytes to (label, mime, extension). The cached files carry no extension, so the
# type is taken from the bytes. Only raster images are rendered; see _RENDERABLE below.
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF87a', 'GIF', 'image/gif', 'gif'),
    (b'GIF89a', 'GIF', 'image/gif', 'gif'),
)
_RENDERABLE = {'JPEG', 'PNG', 'GIF', 'WEBP', 'AVIF'}

# Preference keys reported by pinterest_app_state, in the order they are reported.
_STATE_KEYS = (
    'PREF_MY_ID',
    'PREF_INSTALL_ID',
    'PREF_FIRST_LAUNCH',
    'PREF_FIRST_AUTH',
    'PREF_TIME_LAST_NOTIF_PERMISSION_REQUESTED',
    'PREF_APP_PERMISSION_REQUESTS',
    'PREF_GOOGLE_PLAY_INSTALL_REFERRER_DATA',
    'PREF_INSTALL_REFERRER_LATEST',
    'PREF_LAST_TIME_USER_LAND_ON_SEARCH',
    'CLOSEUP_SESSION_KEY',
    'PREF_SHARE_ICON_LAST_ANIMATED_AT',
    'PREF_DOWNLOAD_UPSELL_LAST_SEEN_AT_MS_2022_V1',
    'PREF_DOWNLOAD_UPSELL_SEEN_COUNT_2022_V1',
    'PREF_THIRD_PARTY_AD_CONFIG_EXPIRY_MS',
    'PREF_ACTIVE_NOTIFICATION_TAB',
    'PREF_PROFILE_PIN_VIEW_TYPE',
    'PREF_APP_PREFERENCES',
    'PREF_ACCOUNT_TRANSFER_ATTEMPTED_ONCE',
    'PREF_POWER_SCORE',
    'PREF_MAX_TEXTURE_SIZE',
)

# A key is converted only when its own name states that it holds a time, and only when
# its value is a thirteen digit integer. A key such as PREF_LAST_TIME_USER_LAND_ON_SEARCH
# names a time and stores it as text, so it stays as stored.
_TIME_TOKENS = ('TIME', '_AT', '_MS', 'SESSION_KEY')


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.

    Converted here rather than through convert_unix_ts_to_utc because the shared helper
    infers the unit from the value's magnitude, which cannot separate milliseconds from
    seconds close to the epoch. These columns are always milliseconds, so converting them
    here keeps a value near 1970 correct. Adding a timedelta to the epoch also avoids
    datetime.fromtimestamp, which raises on Windows for any value before 1970.
    '''
    try:
        value = int(float(value))
    except (TypeError, ValueError):
        return ''
    return _EPOCH + timedelta(milliseconds=value) if value else ''


def _seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.

    The account record stores a birth date this way, so any account holder born before
    1970 carries a negative value. This column is always seconds, so it is converted here
    rather than inferred from its magnitude, and adding a timedelta to the epoch avoids
    datetime.fromtimestamp, which raises on Windows for any value before 1970.
    '''
    try:
        value = int(float(value))
    except (TypeError, ValueError):
        return ''
    return _EPOCH + timedelta(seconds=value) if value else ''


def _text(value):
    '''A preference or JSON value as report text, leaving the stored form intact.'''
    if value is None:
        return ''
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ', '.join(_text(item) for item in value)
    return str(value)


def _preference_files(context, names):
    '''The preference files the glob matched whose basename is in names.'''
    return [path for path in unique_files(context)
            if os.path.basename(path) in names]


def _read_preferences(file_found):
    '''Every entry of an Android shared preferences file as {name: value}.

    Values keep the type the file declares. A set becomes a list of its strings.
    '''
    try:
        root = ET.parse(file_found).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {file_found}: {ex}')
        return {}
    entries = {}
    for element in root:
        name = element.get('name')
        if not name:
            continue
        if element.tag == 'set':
            entries[name] = [child.text or '' for child in element]
        elif element.tag == 'string':
            entries[name] = element.text or ''
        else:
            entries[name] = element.get('value', '')
    return entries


def _json_value(entries, key):
    '''A preference value parsed as JSON, or None when it is absent or not JSON.'''
    raw = entries.get(key)
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


@artifact_processor
def pinterest_account(context):
    data_list = []
    source_path = ''

    for file_found in _preference_files(context, {'pinterest.xml'}):
        record = _json_value(_read_preferences(file_found), 'PREF_MY_USER')
        if not isinstance(record, dict) or not record.get('id'):
            continue
        source_path = file_found
        data_list.append((
            _text(record.get('created_at')),
            _text(record.get('last_pin_save_time')),
            _seconds(record.get('birthday')),
            _text(record.get('username')),
            _text(record.get('full_name')),
            _text(record.get('email')),
            _text(record.get('email_status')),
            _text(record.get('has_confirmed_email')),
            _text(record.get('id')),
            _text(record.get('type')),
            _text(record.get('country')),
            _text(record.get('locale')),
            _text(record.get('location')),
            _text(record.get('gender')),
            _text(record.get('age_in_years')),
            _text(record.get('about')),
            _text(record.get('pin_count')),
            _text(record.get('board_count')),
            _text(record.get('secret_board_count')),
            _text(record.get('archived_board_count')),
            _text(record.get('quick_saves_pin_count')),
            _text(record.get('story_pin_count')),
            _text(record.get('video_pin_count')),
            _text(record.get('follower_count')),
            _text(record.get('following_count')),
            _text(record.get('explicit_board_following_count')),
            _text(record.get('explicit_user_following_count')),
            _text(record.get('interest_following_count')),
            _text(record.get('is_private_profile')),
            _text(record.get('exclude_from_search')),
            _text(record.get('search_privacy_enabled')),
            _text(record.get('personalize_from_offsite_browsing')),
            _text(record.get('third_party_marketing_tracking_enabled')),
            _text(record.get('is_under_18')),
            _text(record.get('is_parental_control_passcode_enabled')),
            _text(record.get('connected_to_facebook')),
            _text(record.get('connected_to_instagram')),
            _text(record.get('connected_to_youtube')),
            _text(record.get('connected_to_etsy')),
            _text(record.get('image_xlarge_url')),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Account Created (as stored)',
        'Last Pin Saved (as stored)',
        ('Birthday', 'datetime'),
        'Username',
        'Full Name',
        'Email',
        'Email Status (as stored)',
        'Has Confirmed Email',
        'Account ID',
        'Account Type (as stored)',
        'Country',
        'Locale',
        'Location',
        'Gender (as stored)',
        'Age In Years',
        'About',
        'Pin Count',
        'Board Count',
        'Secret Board Count',
        'Archived Board Count',
        'Quick Saves Pin Count',
        'Story Pin Count',
        'Video Pin Count',
        'Follower Count',
        'Following Count',
        'Explicit Board Following Count',
        'Explicit User Following Count',
        'Interest Following Count',
        'Is Private Profile',
        'Exclude From Search',
        'Search Privacy Enabled',
        'Personalize From Offsite Browsing',
        'Third Party Marketing Tracking Enabled',
        'Is Under 18',
        'Parental Control Passcode Enabled',
        'Connected To Facebook',
        'Connected To Instagram',
        'Connected To YouTube',
        'Connected To Etsy',
        'Profile Image URL',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def pinterest_stored_accounts(context):
    data_list = []
    source_path = ''
    group_ids = {}

    # Read as a fallback: the account record usually carries the group id itself.
    for file_found in _preference_files(context, {'PREF_ACCUNT_SWITCHER_GROUP_ID.xml'}):
        value = _read_preferences(file_found).get('PREF_ACCUNT_SWITCHER_GROUP_ID')
        if value:
            group_ids[context.get_relative_path(file_found)] = _text(value)

    for file_found in unique_files(context):
        if not os.path.basename(file_found).startswith('PREF_MY_USER_USER_ACCOUNTS'):
            continue
        source_path = file_found
        entries = _read_preferences(file_found)
        for account_id in entries:
            record = _json_value(entries, account_id)
            if not isinstance(record, dict):
                continue
            profile = record.get('PREF_MY_USER_OBJECT')
            profile = profile if isinstance(profile, dict) else {}
            data_list.append((
                _text(account_id),
                _text(profile.get('username')),
                _text(profile.get('full_name')),
                _text(profile.get('email')),
                _text(profile.get('is_partner')),
                _text(record.get('PREF_ACCUNT_SWITCHER_GROUP_ID')
                      or next(iter(group_ids.values()), '')),
                _text(record.get('PREF_ACCESSTOKEN')),
                _text(record.get('PREF_V5_ACCESS_TOKEN')),
                _text(record.get('PREF_V5_REFRESH_TOKEN')),
                _text(profile.get('image_xlarge_url')),
                context.get_relative_path(file_found),
            ))

    data_headers = (
        'Account ID',
        'Username',
        'Full Name',
        'Email',
        'Is Partner',
        'Account Switcher Group ID',
        'Access Token (as stored)',
        'V5 Access Token (as stored)',
        'V5 Refresh Token (as stored)',
        'Profile Image URL',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def pinterest_app_state(context):
    data_list = []
    source_path = ''

    files = _preference_files(context, {'pinterest.xml', 'pinterest.persist.xml'})
    for file_found in files:
        source_path = source_path or file_found
        entries = _read_preferences(file_found)
        name = os.path.basename(file_found)
        for key in _STATE_KEYS:
            if key not in entries:
                continue
            value = entries[key]
            timestamp = ''
            if any(token in key for token in _TIME_TOKENS):
                candidates = value if isinstance(value, list) else [value]
                converted = [_ms(item) for item in candidates
                             if isinstance(item, str) and item.isdigit() and len(item) == 13]
                if converted:
                    timestamp = converted[0]
            data_list.append((
                timestamp,
                name,
                key,
                _text(value),
                context.get_relative_path(file_found),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Preference File',
        'Preference Key',
        'Value (as stored)',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def pinterest_search_typeahead_cache(context):
    data_list = []
    source_path = ''
    settings = {}

    for file_found in _preference_files(context, {'pinterest.persist.xml'}):
        entries = _read_preferences(file_found)
        for key in ('PREF_TYPEAHEAD_CACHE_TIME', 'PREF_SEARCH_TYPEAHEAD_CACHE_VERSION',
                    'PREF_TYPEAHEAD_CACHE_PARTITIONS', 'PREF_TYPEAHEAD_CACHE_READY',
                    'PREF_TYPEAHEAD_CACHE_LAST_PARTITION_FETCHED'):
            if key in entries and key not in settings:
                settings[key] = _text(entries[key])

    for file_found in unique_files(context):
        if os.path.basename(file_found) != 'search-typeahead':
            continue
        source_path = file_found
        count = ''
        for row in get_sqlite_db_records(
                file_found, 'SELECT count(*) FROM SearchTypeaheadSuggestionRoom'):
            count = _text(row[0])
        data_list.append((
            settings.get('PREF_TYPEAHEAD_CACHE_TIME', ''),
            settings.get('PREF_SEARCH_TYPEAHEAD_CACHE_VERSION', ''),
            settings.get('PREF_TYPEAHEAD_CACHE_PARTITIONS', ''),
            settings.get('PREF_TYPEAHEAD_CACHE_READY', ''),
            settings.get('PREF_TYPEAHEAD_CACHE_LAST_PARTITION_FETCHED', ''),
            count,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Cache Fetched (as stored)',
        'Cache Version (as stored)',
        'Partition URL',
        'Cache Ready (as stored)',
        'Last Partition Fetched (as stored)',
        'Suggestion Row Count',
        'Source File',
    )
    return data_headers, data_list, source_path


def _parse_list_page(raw):
    '''(cache key, timestamp value, [strings]) from a paged list cache file, or None.

    Layout established from the tested sample and described in this artifact's notes.
    '''
    if len(raw) < 20 or raw[:4] != b'\x23\x06\x14\x20':
        return None
    try:
        key_length = struct.unpack_from('<Q', raw, 4)[0]
        if key_length > len(raw):
            return None
        key = raw[12:12 + key_length].decode('utf-8', 'replace')
        offset = 12 + key_length
        bookmark_length = struct.unpack_from('<Q', raw, offset)[0]
        offset += 8 + bookmark_length
        if offset + 16 > len(raw):
            return None
        timestamp = struct.unpack_from('<Q', raw, offset + 8)[0]
    except (struct.error, IndexError):
        return None

    strings = []
    cursor = offset + 16
    while cursor + 4 <= len(raw):
        try:
            length = struct.unpack_from('>I', raw, cursor)[0]
        except struct.error:
            break
        cursor += 4
        if 0 < length <= 512 and cursor + length * 2 <= len(raw):
            text = raw[cursor:cursor + length * 2].decode('utf-16-le', 'replace')
            if text.isprintable():
                strings.append(text)
                cursor += length * 2
    return key, timestamp, strings


@artifact_processor
def pinterest_cached_list_pages(context):
    data_list = []
    source_path = ''

    for file_found in unique_files(context):
        if os.path.basename(os.path.dirname(file_found)) != 'paged_list_cache':
            continue
        try:
            with open(file_found, 'rb') as handle:
                raw = handle.read()
        except OSError as ex:
            logfunc(f'Could not read {file_found}: {ex}')
            continue
        parsed = _parse_list_page(raw)
        if not parsed:
            logfunc(f'Unrecognised paged list cache layout in {file_found}')
            continue
        key, timestamp, strings = parsed
        source_path = source_path or file_found
        account = re.search(r'\d{16,21}', key)
        data_list.append((
            _ms(timestamp),
            key,
            account.group(0) if account else '',
            len(strings),
            ', '.join(strings),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Record Timestamp', 'datetime'),
        'Cache Key (as stored)',
        'Account ID',
        'Referenced Identifier Count',
        'Referenced Identifiers (as stored)',
        'Source File',
    )
    return data_headers, data_list, source_path


def _sniff_image(head):
    '''(label, mime, extension) for image bytes, or ('', '', '') when unrecognised.'''
    for magic, label, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return label, mime, extension
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'WEBP', 'image/webp', 'webp'
    if head[4:8] == b'ftyp':
        brand = head[8:12].decode('ascii', 'replace')
        if brand.startswith('avi'):
            return 'AVIF', 'image/avif', 'avif'
        return f'ISOBMFF {brand}'.strip(), '', ''
    if head.lstrip()[:4] == b'<svg':
        return 'SVG', 'image/svg+xml', 'svg'
    return '', '', ''


def _read_disk_lru_journal(path):
    '''{entry key: last state} from a DiskLruCache journal, in first appearance order.'''
    states = {}
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            for line in handle:
                parts = line.split()
                if len(parts) >= 2 and parts[0] in ('CLEAN', 'DIRTY', 'READ', 'REMOVE'):
                    states[parts[1]] = parts[0]
    except OSError as ex:
        logfunc(f'Could not read {path}: {ex}')
    return states


@artifact_processor
def pinterest_cached_images(context):
    data_list = []
    source_path = ''
    stores = {}

    for file_found in unique_files(context):
        parent = os.path.dirname(file_found)
        store = os.path.basename(parent)
        if store not in ('image_manager_disk_cache', 'cache'):
            continue
        entry = stores.setdefault(parent, {'store': store, 'files': {}, 'journal': {}})
        name = os.path.basename(file_found)
        if name == 'journal':
            entry['journal'] = _read_disk_lru_journal(file_found)
        elif name.endswith('.0'):
            entry['files'][name[:-2]] = file_found

    for parent in sorted(stores):
        entry = stores[parent]
        source_path = source_path or (next(iter(entry['files'].values()), '') or parent)
        keys = list(entry['journal'])
        keys += [key for key in entry['files'] if key not in entry['journal']]
        for key in keys:
            file_found = entry['files'].get(key, '')
            label = media = ''
            size = ''
            if file_found:
                try:
                    size = os.path.getsize(file_found)
                    with open(file_found, 'rb') as handle:
                        head = handle.read(16)
                except OSError as ex:
                    logfunc(f'Could not read {file_found}: {ex}')
                    head = b''
                label, mime, extension = _sniff_image(head)
                if label in _RENDERABLE:
                    media = check_in_media(file_found, f'{key}.0',
                                           force_type=mime, force_extension=extension)
            data_list.append((
                key,
                entry['journal'].get(key, ''),
                label,
                size,
                media or '',
                entry['store'],
                context.get_relative_path(file_found) if file_found else '',
            ))

    data_headers = (
        'Cache Entry Key',
        'Journal State (as stored)',
        'Detected Type',
        'File Size (Bytes)',
        ('Cached Image', 'media'),
        'Cache Store',
        'Source File',
    )
    return data_headers, data_list, source_path


def _parse_okhttp_entry(path):
    '''(url, status, headers) from an OkHttp cache metadata file, or None.'''
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            lines = handle.read().split('\n')
    except OSError as ex:
        logfunc(f'Could not read {path}: {ex}')
        return None
    if len(lines) < 5 or not lines[0].startswith('http'):
        return None
    try:
        vary_count = int(lines[2])
        status_index = 3 + vary_count
        status = lines[status_index]
        header_count = int(lines[status_index + 1])
    except (ValueError, IndexError):
        return None
    headers = {}
    for line in lines[status_index + 2:status_index + 2 + header_count]:
        name, separator, value = line.partition(':')
        if separator:
            headers[name.strip().lower()] = value.strip()
    return lines[0].strip(), status.strip(), headers


@artifact_processor
def pinterest_cached_videos(context):
    data_list = []
    source_path = ''
    response_entries = {}
    fragment_roots = set()
    databases = []

    for file_found in unique_files(context):
        name = os.path.basename(file_found)
        parent = os.path.dirname(file_found)
        if os.path.basename(parent) == 'response_cache':
            if name.endswith(('.0', '.1')):
                stem, suffix = name[:-2], name[-1]
                response_entries.setdefault(stem, {})[suffix] = file_found
        elif 'media_cache' in parent.replace('\\', '/').split('/'):
            fragment_roots.add(file_found)
        elif name.startswith('exoplayer_internal.db') and not name.endswith(('-wal', '-shm', '-journal')):
            databases.append(file_found)

    for stem in sorted(response_entries):
        entry = response_entries[stem]
        metadata_path, body_path = entry.get('0'), entry.get('1')
        if not metadata_path:
            continue
        source_path = source_path or metadata_path
        parsed = _parse_okhttp_entry(metadata_path)
        if not parsed:
            continue
        url, status, headers = parsed
        media = size = ''
        if body_path:
            try:
                size = os.path.getsize(body_path)
            except OSError:
                size = ''
            media = check_in_media(body_path, f'{stem}.1',
                                   force_type=headers.get('content-type') or None,
                                   force_extension='mp4')
        data_list.append((
            _ms(headers.get('okhttp-sent-millis')),
            _ms(headers.get('okhttp-received-millis')),
            'Response cache',
            url,
            headers.get('content-type', ''),
            status,
            headers.get('etag', ''),
            headers.get('date', ''),
            size,
            '',
            media or '',
            context.get_relative_path(metadata_path),
        ))

    # Fragment file names are the cache id, then the byte offset, then the last touch time.
    fragments = {}
    for path in fragment_roots:
        match = re.match(r'^(\d+)\.\d+\.\d+\.v3\.exo$', os.path.basename(path))
        if match:
            fragments.setdefault(int(match.group(1)), []).append(path)

    for db_path in databases:
        source_path = source_path or db_path
        indexes = [row[0] for row in get_sqlite_db_records(
            db_path,
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name LIKE 'ExoPlayerCacheIndex%'")]
        for table in indexes:
            uid = table.replace('ExoPlayerCacheIndex', '')
            metadata_table = f'ExoPlayerCacheFileMetadata{uid}'
            touched = {}
            for row in get_sqlite_db_records(
                    db_path,
                    f'SELECT name, length, last_touch_timestamp FROM `{metadata_table}`'):
                match = re.match(r'^(\d+)\.', str(row[0]))
                if match:
                    touched.setdefault(int(match.group(1)), []).append((row[1], row[2]))
            for cache_id, url in get_sqlite_db_records(
                    db_path, f'SELECT id, key FROM `{table}`'):
                recorded = touched.get(cache_id, [])
                total = sum(int(length or 0) for length, _ in recorded)
                last_touch = max((stamp for _, stamp in recorded), default=None)
                data_list.append((
                    _ms(last_touch),
                    '',
                    'Player cache',
                    _text(url),
                    '',
                    '',
                    '',
                    '',
                    total if recorded else '',
                    len(fragments.get(cache_id, [])),
                    '',
                    context.get_relative_path(db_path),
                ))

    data_headers = (
        ('Requested', 'datetime'),
        ('Received', 'datetime'),
        'Source Store',
        'Media URL',
        'Content Type (as stored)',
        'HTTP Status (as stored)',
        'ETag (as stored)',
        'Server Date (as stored)',
        'Cached Bytes',
        'Fragment Files On Disk',
        ('Cached Video', 'media'),
        'Source File',
    )
    return data_headers, data_list, source_path


def _select_present(db_path, table, columns):
    '''A SELECT naming only the columns the table declares, or '' when it has none.'''
    present = set()
    for row in get_sqlite_db_records(db_path, f'PRAGMA table_info(`{table}`)'):
        present.add(row[1])
    if not present:
        return ''
    select_list = ', '.join(
        f'`{column}`' if column in present else f'NULL AS `{column}`' for column in columns)
    return f'SELECT {select_list} FROM `{table}`'


def _rows_pre_wal(source_path, sql):
    '''Rows for sql as of the file's last checkpoint, ignoring the write-ahead log.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered. Path handling goes through the same
    get_sqlite_db_path() that open_sqlite_db_readonly() uses, so Windows long paths and
    URI-special characters behave identically.
    '''
    if not source_path or not sql:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


_DRAFT_COLUMNS = (
    'id', 'user_id', 'board_id', 'board_section_id', 'created_at', 'last_updated_at',
    'scheduled_date', 'page_count', 'duration', 'comments_enabled', 'is_broken',
    'is_expiration_supported', 'link', 'tags', 'cover_image_path', 'exported_media',
    'metadata', 'page_data', 'comment_reply_data', 'extracted_image_metadata',
)


@artifact_processor
def pinterest_idea_pin_drafts(context):
    data_list = []
    source_path = ''

    for file_found in unique_files(context):
        name = os.path.basename(file_found)
        if not name.startswith('pinterest-db') or name.endswith(('-wal', '-shm', '-journal')):
            continue
        source_path = file_found
        sql = _select_present(file_found, 'idea_pin_drafts', _DRAFT_COLUMNS)
        if not sql:
            continue
        committed = list(get_sqlite_db_records(file_found, sql))
        seen = {row[0] for row in committed}
        pre_wal = [row for row in _rows_pre_wal(file_found, sql) if row[0] not in seen]
        for view, rows in (('Committed', committed), ('Pre-checkpoint', pre_wal)):
            for row in rows:
                record = dict(zip(_DRAFT_COLUMNS, row))
                data_list.append((
                    _ms(record.get('created_at')),
                    _ms(record.get('last_updated_at')),
                    _ms(record.get('scheduled_date')),
                    view,
                    _text(record.get('id')),
                    _text(record.get('user_id')),
                    _text(record.get('board_id')),
                    _text(record.get('board_section_id')),
                    _text(record.get('page_count')),
                    _text(record.get('duration')),
                    _text(record.get('comments_enabled')),
                    _text(record.get('is_broken')),
                    _text(record.get('is_expiration_supported')),
                    _text(record.get('link')),
                    _text(record.get('tags')),
                    _text(record.get('cover_image_path')),
                    _text(record.get('exported_media')),
                    len(record['metadata']) if record.get('metadata') else 0,
                    len(record['page_data']) if record.get('page_data') else 0,
                    len(record['extracted_image_metadata']) if record.get('extracted_image_metadata') else 0,
                    context.get_relative_path(file_found),
                ))

    data_headers = (
        ('Created', 'datetime'),
        ('Last Updated', 'datetime'),
        ('Scheduled Date', 'datetime'),
        'Source View',
        'Draft ID',
        'User ID',
        'Board ID',
        'Board Section ID',
        'Page Count',
        'Duration (as stored)',
        'Comments Enabled (as stored)',
        'Is Broken (as stored)',
        'Is Expiration Supported (as stored)',
        'Link',
        'Tags (as stored)',
        'Cover Image Path',
        'Exported Media (as stored)',
        'Metadata Length (Bytes)',
        'Page Data Length (Bytes)',
        'Extracted Image Metadata Length (Bytes)',
        'Source File',
    )
    return data_headers, data_list, source_path
