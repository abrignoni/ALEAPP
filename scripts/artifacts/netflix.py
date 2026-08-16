__artifacts_v2__ = {
    "netflix_playback": {
        "name": "Netflix Playback Events",
        "description": "Rows of the playEvent table in the Netflix appHistory database, with the "
                       "event time, the playable identifier and the playback session identifier",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "eventType, network and offline are stored as integers. The enum constant names "
                 "are stripped by R8 in the app binary checked, so the integers are reported as "
                 "stored and are not mapped to labels. Only one value of eventType was present in "
                 "the data tested, so the column is unexercised beyond that value. The duration "
                 "value was identical across every repeat in the data tested (9 playable ids with "
                 "more than one event, none with a differing duration), so it appears to describe "
                 "the playable rather than the individual event. Titles are filled in from the "
                 "offlineFalkorPlayable table and the Apollo cache when the same video id appears "
                 "there, and are left blank otherwise; those two stores hold whatever the app had "
                 "cached, so most rows have no title available. Artwork is shown when a file named "
                 "after the playable id exists under files/img/of/videos. The database uses WAL, "
                 "so the -wal and -shm sidecars are matched with it."
                 " In the corpora listed below the app was installed and the "
                 "database was present with this table empty, checked directly "
                 "against the store; the row producing path was exercised against "
                 "a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/databases/appHistory*',
                  '*/com.netflix.mediaclient/databases/OfflineDb*',
                  '*/com.netflix.mediaclient/databases/apollo_cache_v1_*',
                  '*/com.netflix.mediaclient/files/img/of/*'),
        "output_types": "standard",
        "artifact_icon": "player-play",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_streaming_sessions": {
        "name": "Netflix Streaming Sessions",
        "description": "Rows of the sessionNetworkStatistics table in the Netflix appHistory "
                       "database, with the timestamp, byte count, server address and network type "
                       "recorded for each stream",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "streamId values overlap the playableId values in the playEvent table, so the "
                 "same title lookup is applied here. The overlap is not total: in the data tested "
                 "37 of 43 stream ids also appeared as a playable id, 6 appeared only here, and 3 "
                 "playable ids had no row in this table. The ip and locationID values are reported "
                 "as stored; the schema does not document whether the address belongs to the "
                 "device or to the serving node, so no reading is asserted here. The database uses "
                 "WAL and the sidecars are matched with it."
                 " In the corpora listed below the app was installed and the "
                 "database was present with this table empty, checked directly "
                 "against the store; the row producing path was exercised against "
                 "a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/databases/appHistory*',
                  '*/com.netflix.mediaclient/databases/OfflineDb*',
                  '*/com.netflix.mediaclient/databases/apollo_cache_v1_*'),
        "output_types": "standard",
        "artifact_icon": "network",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_bookmarks": {
        "name": "Netflix Playback Bookmarks",
        "description": "Rows of the bookmarkStore table in the Netflix OfflineDb database, holding "
                       "a stored playback position per playable per profile with the time the "
                       "position was last updated",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "bookmarkInMs is reported as stored and also formatted as hours, minutes and "
                 "seconds. Titles are filled in from the offlineFalkorPlayable table and the "
                 "Apollo cache where the same video id appears there. Artwork is shown when a file "
                 "named after the playable id exists under files/img/of/videos. The database uses "
                 "WAL and the sidecars are matched with it."
                 " In the corpora listed below the app was installed and the "
                 "database was present with this table empty, checked directly "
                 "against the store; the row producing path was exercised against "
                 "a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/databases/OfflineDb*',
                  '*/com.netflix.mediaclient/databases/apollo_cache_v1_*',
                  '*/com.netflix.mediaclient/files/img/of/*'),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_offline_titles": {
        "name": "Netflix Offline Title Metadata",
        "description": "Rows of the offlineFalkorPlayable table in the Netflix OfflineDb database, "
                       "carrying the title, season and episode numbering, runtime and artwork URLs "
                       "the app stored for a playable",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "The table carries many columns; the ones reported here are the descriptive "
                 "fields. videoType, maturityLevel and the boolean-looking integers are reported "
                 "as stored because the app's constant names are stripped by R8 in the app binary "
                 "checked. Artwork is shown when a file named after the video id exists under "
                 "files/img/of/videos. The table holds the playables the app had prepared for "
                 "offline use, which is a smaller set than the titles played. The database uses "
                 "WAL and the sidecars are matched with it."
                 " In the corpora listed below the app was installed and the "
                 "database was present with this table empty, checked directly "
                 "against the store; the row producing path was exercised against "
                 "a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/databases/OfflineDb*',
                  '*/com.netflix.mediaclient/files/img/of/*'),
        "output_types": "standard",
        "artifact_icon": "movie",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_profiles": {
        "name": "Netflix Profiles",
        "description": "Rows of the offlineFalkorProfile table in the Netflix OfflineDb database, "
                       "with the profile identifier, the profile name and the avatar URL, plus the "
                       "cached avatar image where one is on disk",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Profile identifiers also appear as the file name of the Apollo cache database "
                 "and of the cached avatar under files/img/of/profiles, and those are used to add "
                 "rows for profiles the table itself does not list. isKids is reported as stored. "
                 "The database uses WAL and the sidecars are matched with it."
                 " In the corpora listed below the app was installed and the "
                 "database was present with this table empty, checked directly "
                 "against the store; the row producing path was exercised against "
                 "a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/databases/OfflineDb*',
                  '*/com.netflix.mediaclient/databases/apollo_cache_v1_*',
                  '*/com.netflix.mediaclient/files/img/of/*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_browse_cache": {
        "name": "Netflix Browse Cache",
        "description": "Video entries held in the Netflix Apollo GraphQL cache, listing the title, "
                       "the entry kind and the runtime and category tags stored alongside it",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "The cache file name carries the profile identifier, which is reported per row. "
                 "The records table holds normalised GraphQL objects keyed as Video.<video id>; "
                 "this artifact reads those keys and the tag and artwork records that reference "
                 "them. The cache holds entries the app had fetched, which is not the same set as "
                 "the titles played on the device, and the two did not overlap in the data "
                 "tested (0 of 40 playable ids and 0 of 15 bookmarked ids resolved here)."
                 " This store was not present in any of the corpora listed below, so "
                 "those entries record a checked absence; the row producing path was "
                 "exercised against a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/databases/apollo_cache_v1_*',),
        "output_types": "standard",
        "artifact_icon": "device-tv",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_artwork": {
        "name": "Netflix Cached Artwork",
        "description": "Images cached by Netflix under files/img/of, with the video or profile "
                       "identifier taken from the file name and the title resolved where the "
                       "databases carry it",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "The files carry an .img extension whatever the format; content is identified by "
                 "signature, and WebP and PNG were both observed. The file name is the video id "
                 "for images under videos and the profile id for images under profiles, sometimes "
                 "with a suffix naming the artwork field. Every image on disk gets a row, "
                 "including ones no database record points at."
                 " This store was not present in any of the corpora listed below, so "
                 "those entries record a checked absence; the row producing path was "
                 "exercised against a separate populated extraction.",
        "paths": ('*/com.netflix.mediaclient/files/img/of/*',
                  '*/com.netflix.mediaclient/databases/OfflineDb*',
                  '*/com.netflix.mediaclient/databases/apollo_cache_v1_*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
    "netflix_account": {
        "name": "Netflix Account and Device",
        "description": "Device and account values read from the Netflix nfxpref preferences file "
                       "and the CurrentCountryCode file, including the ESN, the Widevine "
                       "identifiers, the stored country and language and the app install time",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "One row per preferences file that carries at least one of the reported values. "
                 "Older releases write none of them, and such a file produces no row here; its "
                 "contents still appear in the Netflix Preferences artifact. "
                 "The ESN and the Widevine device id are identifiers "
                 "the app stores for itself; they are reported as stored. Credential bearing keys "
                 "are deliberately not reported: the Netflix ID and Secure Netflix ID cookies, the "
                 "MSL and secure stores, the NGP device id store, the Widevine key request sample "
                 "and the push tokens. The country and language values are the ones the app had "
                 "stored, which is not by itself a statement about where the device was. Which "
                 "keys are present varies by app version, and absent keys are left blank.",
        "paths": ('*/com.netflix.mediaclient/shared_prefs/nfxpref.xml',
                  '*/com.netflix.mediaclient/shared_prefs/CurrentCountryCode.xml'),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 1 row",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 1 row",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 1 row",
        },
    },
    "netflix_preferences": {
        "name": "Netflix Preferences",
        "description": "Key and value pairs from the Netflix nfxpref preferences file, excluding "
                       "the numbered feature flag entries and the credential bearing keys",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "The file also holds several hundred persistent_<number> entries which are not "
                 "reported here. The same credential bearing keys excluded from the account "
                 "artifact are excluded here. Values are reported as stored, including the JSON "
                 "ones, which are left unparsed.",
        "paths": ('*/com.netflix.mediaclient/shared_prefs/nfxpref.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 31 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 2 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 4 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 37 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 38 rows",
        },
    },
    "netflix_logblobs": {
        "name": "Netflix Log Blobs",
        "description": "Entries from the JSON log blobs Netflix queues under files/logblobs, with "
                       "the client timestamp and the device and session values carried in each "
                       "entry",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Each file holds a JSON array of entries that were queued for delivery. Entries "
                 "carry differing fields depending on the blob type, so the columns here are the "
                 "ones observed across the files tested and are left blank when an entry does not "
                 "carry them. The rooted value is the app's own recorded value and is reported as "
                 "stored rather than treated as a finding about the device.",
        "paths": ('*/com.netflix.mediaclient/files/logblobs/*',),
        "output_types": "standard",
        "artifact_icon": "file-analytics",
        "sample_data": {
            "anne_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.netflix.mediaclient | 0 rows",
            "s20fe_a13": "Android 13 | com.netflix.mediaclient | 0 rows",
            "sharon_a13": "Android 13 | com.netflix.mediaclient | 3 rows",
            "sharon_a14": "Android 14 | com.netflix.mediaclient | 0 rows",
        },
    },
}

import json
import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)

# Preference keys that carry an authentication token, a key store or a push token. They are
# read from the same file as everything else and are deliberately not reported.
_CREDENTIAL_KEYS = frozenset((
    'shadowCookieNetflixId',
    'shadowCookieSecureNetflixId',
    'pref_secure_store',
    'nf_msl_store_json',
    'nf_msl_rsa_store_json',
    'pref_ngp_device_id_store',
    'wv_keyrequest_sample_data',
    'last_push_message_token',
    'old_push_message_token',
    'signInConfigData',
))

_MEDIA_SIGNATURES = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF87a', 'GIF', 'image/gif', 'gif'),
    (b'GIF89a', 'GIF', 'image/gif', 'gif'),
)


def _sniff(data):
    """Identify image bytes by signature. The cached files are named .img whatever they hold."""
    for signature, label, mime, extension in _MEDIA_SIGNATURES:
        if data.startswith(signature):
            return label, mime, extension
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'WebP', 'image/webp', 'webp'
    return '', None, None


def _paths_matching(files_found, *fragments):
    """Return the found files whose path contains every fragment, as forward slashed text."""
    matches = []
    for file_found in files_found:
        candidate = str(file_found).replace('\\', '/')
        if not os.path.isfile(candidate):
            continue
        if all(fragment in candidate for fragment in fragments):
            matches.append(candidate)
    return matches


def _databases(files_found, name):
    """Return the database files of the given name, skipping the WAL and SHM sidecars.

    The sidecars are matched by the artifact paths so SQLite can apply them, but they are
    not databases to open in their own right.
    """
    return [path for path in _paths_matching(files_found, f'/databases/{name}')
            if not path.endswith(('-wal', '-shm', '-journal'))]


def _apollo_databases(files_found):
    return [path for path in _paths_matching(files_found, '/databases/apollo_cache_v1_')
            if not path.endswith(('-wal', '-shm', '-journal'))]


def _apollo_profile_id(path):
    """The Apollo cache file is named apollo_cache_v1_<profile id>.db."""
    match = re.search(r'apollo_cache_v1_(.+?)(?:\.db)?$', os.path.basename(path))
    return match.group(1) if match else ''


def _title_lookup(files_found):
    """Build a video id to title map from the offline metadata table and the Apollo cache.

    Neither source is a catalogue of what was played; each holds whatever the app had stored,
    so a playable id often has no entry and the caller leaves the title blank.
    """
    titles = {}
    for path in _databases(files_found, 'OfflineDb'):
        for video_id, title in get_sqlite_db_records(
                path, 'SELECT videoId, title FROM offlineFalkorPlayable'):
            if video_id and title:
                titles.setdefault(str(video_id), title)
    for path in _apollo_databases(files_found):
        for key, record in get_sqlite_db_records(path, 'SELECT key, record FROM records'):
            match = re.fullmatch(r'Video\.(\d+)', key or '')
            if not match:
                continue
            try:
                parsed = json.loads(record)
            except (TypeError, ValueError):
                continue
            title = parsed.get('title')
            if title:
                titles.setdefault(match.group(1), title)
    return titles


def _artwork_index(files_found):
    """Map an identifier to the cached image files named after it.

    Images live at files/img/of/videos/<video id>[_<field>].img and
    files/img/of/profiles/<profile id>.img, so the identity is recorded in the name rather
    than inferred.
    """
    index = {}
    for path in _paths_matching(files_found, '/files/img/of/'):
        stem = os.path.splitext(os.path.basename(path))[0]
        identifier = stem.split('_')[0]
        index.setdefault(identifier, []).append(path)
    return index


def _artwork_media(index, identifier, title=''):
    """Check in the first cached image for an identifier and return its media reference."""
    for path in index.get(str(identifier), []):
        try:
            with open(path, 'rb') as handle:
                head = handle.read(16)
        except OSError:
            continue
        _, mime, extension = _sniff(head)
        if not mime:
            continue
        name = f'{title} ({identifier})' if title else str(identifier)
        media = check_in_media(path, name, force_type=mime, force_extension=extension)
        if media:
            return media
    return ''


def _ms_to_hms(value):
    """Format a millisecond offset as hours, minutes and seconds."""
    try:
        total = int(value) // 1000
    except (TypeError, ValueError):
        return ''
    return f'{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}'


def _timestamp_value(raw):
    """Convert a millisecond epoch preference value, tolerating a missing or non numeric one."""
    if raw is None or not str(raw).strip().lstrip('-').isdigit():
        return ''
    value = int(raw)
    return convert_unix_ts_to_utc(value) if value > 0 else ''


def _widevine_device_id(raw):
    """Pull the deviceId out of the colon separated nf_drm_migration_identity value."""
    for part in str(raw).split(':'):
        name, _, value = part.partition('=')
        if name.strip() == 'deviceId':
            return value.strip()
    return ''


def _read_prefs(path):
    """Read an Android shared preferences XML into a name to text map."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        logfunc(f'Error with {path}:')
        logfunc(f' - {str(error)}')
        return {}
    values = {}
    for element in root:
        name = element.get('name')
        if not name:
            continue
        if element.tag in ('string', 'set'):
            values[name] = element.text or ''
        else:
            values[name] = element.get('value') or ''
    return values


def _json_field(raw, *keys):
    """Return a nested value from a JSON preference, or an empty string."""
    try:
        current = json.loads(raw)
    except (TypeError, ValueError):
        return ''
    for key in keys:
        if not isinstance(current, dict):
            return ''
        current = current.get(key)
        if current is None:
            return ''
    if isinstance(current, (dict, list)):
        return json.dumps(current, separators=(',', ':'))
    return current


def _json_timestamp(raw, *keys):
    return _timestamp_value(_json_field(raw, *keys))


@artifact_processor
def netflix_playback(context):
    files_found = context.get_files_found()
    titles = _title_lookup(files_found)
    artwork = _artwork_index(files_found)
    data_list = []
    source_path = ''

    for path in _databases(files_found, 'appHistory'):
        source_path = path
        for row in get_sqlite_db_records(path, '''
                SELECT eventTime, playableId, xid, eventType, network, duration, offline, id
                FROM playEvent ORDER BY eventTime'''):
            event_time, playable_id, xid, event_type, network, duration, offline, row_id = row
            playable_id = str(playable_id) if playable_id is not None else ''
            title = titles.get(playable_id, '')
            data_list.append((
                convert_unix_ts_to_utc(event_time),
                title,
                playable_id,
                _artwork_media(artwork, playable_id, title),
                str(xid) if xid is not None else '',
                event_type,
                network,
                offline,
                duration,
                _ms_to_hms(duration),
                row_id,
            ))

    data_headers = (
        ('Event Time', 'datetime'),
        'Title',
        'Playable ID',
        ('Artwork', 'media'),
        'Playback Session ID (xid)',
        'Event Type (as stored)',
        'Network (as stored)',
        'Offline (as stored)',
        'Duration (ms)',
        'Duration (hh:mm:ss)',
        'Row ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_streaming_sessions(context):
    files_found = context.get_files_found()
    titles = _title_lookup(files_found)
    data_list = []
    source_path = ''

    for path in _databases(files_found, 'appHistory'):
        source_path = path
        for row in get_sqlite_db_records(path, '''
                SELECT timestamp, streamId, bytes, interval, locationID, ip, networkType,
                       totalBufferingTime
                FROM sessionNetworkStatistics ORDER BY timestamp'''):
            (timestamp, stream_id, num_bytes, interval, location_id, ip, network_type,
             buffering) = row
            stream_id = str(stream_id) if stream_id is not None else ''
            data_list.append((
                convert_unix_ts_to_utc(timestamp),
                titles.get(stream_id, ''),
                stream_id,
                ip,
                location_id,
                network_type,
                num_bytes,
                interval,
                buffering,
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Title',
        'Stream ID',
        'IP Address (as stored)',
        'Location ID (as stored)',
        'Network Type',
        'Bytes',
        'Interval (ms)',
        'Total Buffering Time (ms)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_bookmarks(context):
    files_found = context.get_files_found()
    titles = _title_lookup(files_found)
    artwork = _artwork_index(files_found)
    data_list = []
    source_path = ''

    for path in _databases(files_found, 'OfflineDb'):
        source_path = path
        for row in get_sqlite_db_records(path, '''
                SELECT bookmarkUpdateTimeInUTCMs, playableId, profileId, bookmarkInMs
                FROM bookmarkStore ORDER BY bookmarkUpdateTimeInUTCMs'''):
            updated, playable_id, profile_id, position = row
            playable_id = str(playable_id) if playable_id is not None else ''
            title = titles.get(playable_id, '')
            data_list.append((
                convert_unix_ts_to_utc(updated),
                title,
                playable_id,
                _artwork_media(artwork, playable_id, title),
                position,
                _ms_to_hms(position),
                profile_id,
            ))

    data_headers = (
        ('Bookmark Update Time', 'datetime'),
        'Title',
        'Playable ID',
        ('Artwork', 'media'),
        'Position (ms)',
        'Position (hh:mm:ss)',
        'Profile ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_offline_titles(context):
    files_found = context.get_files_found()
    artwork = _artwork_index(files_found)
    data_list = []
    source_path = ''

    for path in _databases(files_found, 'OfflineDb'):
        source_path = path
        for row in get_sqlite_db_records(path, '''
                SELECT videoId, title, parentId, videoType, isEpisode, seasonNumber,
                       episodeNumber, seasonLabel, duration, year, maturityLevel, cert,
                       synopsis, actors, genres, quality, boxshotUrl, horzDispUrl,
                       profileId, expTime
                FROM offlineFalkorPlayable'''):
            (video_id, title, parent_id, video_type, is_episode, season_number, episode_number,
             season_label, duration, year, maturity, cert, synopsis, actors, genres, quality,
             boxshot_url, horizontal_url, profile_id, expiry) = row
            video_id = str(video_id) if video_id is not None else ''
            data_list.append((
                title,
                video_id,
                _artwork_media(artwork, video_id, title),
                parent_id,
                video_type,
                is_episode,
                season_label,
                season_number,
                episode_number,
                duration,
                year,
                maturity,
                cert,
                quality,
                genres,
                actors,
                synopsis,
                convert_unix_ts_to_utc(expiry) if expiry else '',
                profile_id,
                boxshot_url,
                horizontal_url,
            ))

    data_headers = (
        'Title',
        'Video ID',
        ('Artwork', 'media'),
        'Parent ID',
        'Video Type (as stored)',
        'Is Episode (as stored)',
        'Season Label',
        'Season Number',
        'Episode Number',
        'Duration (seconds)',
        'Year',
        'Maturity Level (as stored)',
        'Certification',
        'Quality',
        'Genres',
        'Actors',
        'Synopsis',
        ('Expiry Time', 'datetime'),
        'Profile ID',
        'Boxshot URL',
        'Horizontal Artwork URL',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_profiles(context):
    files_found = context.get_files_found()
    artwork = _artwork_index(files_found)
    data_list = []
    source_path = ''
    seen = set()

    for path in _databases(files_found, 'OfflineDb'):
        source_path = path
        for profile_id, name, is_kids, avatar_url in get_sqlite_db_records(
                path, 'SELECT profileId, name, isKids, avatarUrl FROM offlineFalkorProfile'):
            profile_id = str(profile_id) if profile_id is not None else ''
            seen.add(profile_id)
            data_list.append((
                profile_id,
                name,
                _artwork_media(artwork, profile_id, name or ''),
                is_kids,
                'offlineFalkorProfile',
                avatar_url,
            ))

    # Profile identifiers also name the Apollo cache file and the cached avatar, so a profile
    # with no row in the table is still reported rather than dropped.
    for path in _apollo_databases(files_found):
        profile_id = _apollo_profile_id(path)
        if not profile_id or profile_id in seen:
            continue
        seen.add(profile_id)
        source_path = source_path or path
        data_list.append((
            profile_id, '', _artwork_media(artwork, profile_id), '', 'Apollo cache file name', '',
        ))

    for path in _paths_matching(files_found, '/files/img/of/profiles/'):
        profile_id = os.path.splitext(os.path.basename(path))[0].split('_')[0]
        if not profile_id or profile_id in seen:
            continue
        seen.add(profile_id)
        source_path = source_path or path
        data_list.append((
            profile_id, '', _artwork_media(artwork, profile_id), '', 'Cached avatar file name', '',
        ))

    data_headers = (
        'Profile ID',
        'Profile Name',
        ('Avatar', 'media'),
        'Is Kids (as stored)',
        'Recovered From',
        'Avatar URL',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_browse_cache(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for path in _apollo_databases(files_found):
        source_path = path
        profile_id = _apollo_profile_id(path)
        records = {}
        for key, record in get_sqlite_db_records(path, 'SELECT key, record FROM records'):
            if key:
                records[key] = record

        tags = {}
        for key, record in records.items():
            match = re.fullmatch(r'Video\.(\d+)\.tags\.\d+', key)
            if not match:
                continue
            try:
                parsed = json.loads(record)
            except (TypeError, ValueError):
                continue
            name = parsed.get('displayName')
            if name:
                tags.setdefault(match.group(1), []).append(name)

        for key, record in records.items():
            match = re.fullmatch(r'Video\.(\d+)', key)
            if not match:
                continue
            try:
                parsed = json.loads(record)
            except (TypeError, ValueError):
                continue
            video_id = match.group(1)
            parent = parsed.get('parentShow') or ''
            parent_match = re.search(r'Video\.(\d+)', str(parent))
            data_list.append((
                parsed.get('title', ''),
                video_id,
                parsed.get('__typename', ''),
                parsed.get('number', ''),
                parsed.get('runtimeSec', ''),
                ', '.join(tags.get(video_id, [])),
                parent_match.group(1) if parent_match else '',
                parsed.get('isAvailable', ''),
                parsed.get('isAvailableForDownload', ''),
                profile_id,
            ))

    data_headers = (
        'Title',
        'Video ID',
        'Kind',
        'Number',
        'Runtime (seconds)',
        'Tags',
        'Parent Show ID',
        'Is Available (as stored)',
        'Is Available For Download (as stored)',
        'Profile ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_artwork(context):
    files_found = context.get_files_found()
    titles = _title_lookup(files_found)
    data_list = []
    source_path = ''

    for path in sorted(_paths_matching(files_found, '/files/img/of/')):
        try:
            with open(path, 'rb') as handle:
                head = handle.read(16)
        except OSError:
            continue
        label, mime, extension = _sniff(head)
        if not mime:
            continue
        source_path = os.path.dirname(path)
        stem = os.path.splitext(os.path.basename(path))[0]
        identifier, _, field = stem.partition('_')
        kind = 'Profile' if '/img/of/profiles/' in path else 'Video'
        title = titles.get(identifier, '') if kind == 'Video' else ''
        media = check_in_media(path, f'{title} ({identifier})' if title else identifier,
                               force_type=mime, force_extension=extension) or ''
        data_list.append((
            media,
            identifier,
            kind,
            title,
            field,
            label,
            os.path.getsize(path),
            context.get_relative_path(path),
        ))

    data_headers = (
        ('Artwork', 'media'),
        'Identifier',
        'Kind',
        'Title',
        'Artwork Field',
        'Format',
        'Size (bytes)',
        'Local Path',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_account(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    country_files = _paths_matching(files_found, '/shared_prefs/CurrentCountryCode.xml')
    country_code = ''
    for path in country_files:
        country_code = _read_prefs(path).get('code', '') or country_code

    for path in _paths_matching(files_found, '/shared_prefs/nfxpref.xml'):
        source_path = path
        prefs = _read_prefs(path)
        row = (
            _timestamp_value(prefs.get('playAppInstallTime')),
            _json_timestamp(prefs.get('device_history'), 'osInfo', 'firstSeenTime'),
            _timestamp_value(prefs.get('last_contact_netflix_ms')),
            _timestamp_value(prefs.get('netflix_server_time_ms')),
            _timestamp_value(prefs.get('netflix_device_time_ms')),
            prefs.get('nf_drm_esn', ''),
            _json_field(prefs.get('nf_drm_proxy_esn'), 'esn'),
            _widevine_device_id(prefs.get('nf_drm_migration_identity', '')),
            prefs.get('nf_drm_crypto_provider', ''),
            prefs.get('nf_drm_system_id', ''),
            prefs.get('pref_offline_profile_guid', ''),
            country_code,
            _json_field(prefs.get('deviceConfig'), 'geoCountryCode'),
            _json_field(prefs.get('nrmLanguages'), 'default'),
            prefs.get('nf_device_category_at_start', ''),
            prefs.get('manifestVersionCode', ''),
            prefs.get('nf_user_status_loggedin', ''),
            prefs.get('nf_user_is_former_or_never_member', ''),
            prefs.get('offline_ever_worked', ''),
            prefs.get('playReferrer', ''),
            prefs.get('channelIdValue', ''),
        )
        # Older releases of the app write none of these keys. Reporting a row of empty
        # columns says nothing the preferences artifact does not already show.
        if any(value not in (None, '') for value in row):
            data_list.append(row + (context.get_relative_path(path),))

    data_headers = (
        ('App Install Time', 'datetime'),
        ('OS First Seen Time', 'datetime'),
        ('Last Contact With Netflix', 'datetime'),
        ('Netflix Server Time', 'datetime'),
        ('Netflix Device Time', 'datetime'),
        'ESN',
        'DRM Proxy ESN',
        'Widevine Device ID',
        'Widevine Crypto Provider',
        'Widevine System ID',
        'Offline Profile GUID',
        'Current Country Code',
        'Device Config Country Code',
        'Default Language',
        'Device Category',
        'Manifest Version Code',
        'User Logged In (as stored)',
        'Former Or Never Member (as stored)',
        'Offline Ever Worked (as stored)',
        'Play Referrer',
        'Channel ID',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def netflix_preferences(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for path in _paths_matching(files_found, '/shared_prefs/nfxpref.xml'):
        source_path = path
        relative = context.get_relative_path(path)
        for name, value in sorted(_read_prefs(path).items()):
            if name.startswith('persistent_') or name in _CREDENTIAL_KEYS:
                continue
            data_list.append((name, value, relative))

    data_headers = ('Preference Key', 'Value', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def netflix_logblobs(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for path in sorted(_paths_matching(files_found, '/files/logblobs/')):
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as handle:
                parsed = json.load(handle)
        except (OSError, ValueError):
            continue
        if isinstance(parsed, dict):
            parsed = [parsed]
        if not isinstance(parsed, list):
            continue
        source_path = os.path.dirname(path)
        for entry in parsed:
            if not isinstance(entry, dict):
                continue
            client = entry.get('clientJson')
            client = client if isinstance(client, dict) else {}
            data_list.append((
                _timestamp_value(entry.get('clientEpoch')),
                client.get('type', ''),
                client.get('sev', ''),
                client.get('errormsg', ''),
                client.get('AndroidDeviceID', ''),
                client.get('android_version', ''),
                client.get('rooted', ''),
                client.get('fingerprint', ''),
                client.get('clver', ''),
                client.get('playerver', ''),
                client.get('installerName', ''),
                client.get('installationsource', ''),
                client.get('devicecategory', ''),
                client.get('system_id', ''),
                client.get('appid', ''),
                client.get('sessionid', ''),
                client.get('uniqueLogId', ''),
                context.get_relative_path(path),
            ))

    data_headers = (
        ('Client Timestamp', 'datetime'),
        'Type',
        'Severity',
        'Message',
        'Android Device ID',
        'Android Version',
        'Rooted (as stored)',
        'Build Fingerprint',
        'Client Version',
        'Player Version',
        'Installer Name',
        'Installation Source',
        'Device Category',
        'Widevine System ID',
        'App ID',
        'Session ID',
        'Unique Log ID',
        'Source File',
    )
    return data_headers, data_list, source_path
