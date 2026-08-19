__artifacts_v2__ = {
    "shazam_recognitions": {
        "name": "Shazam Recognitions",
        "description": "Rows of the tag table in the Shazam library database, each holding the "
                       "time of a music recognition with the track it resolved to, the stored "
                       "coordinates and place names, and the recognition request identifier",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Shazam",
        "notes": "timestamp is Unix milliseconds. Read as seconds every value in the one device "
                 "tested falls outside the range a date can represent, and read as milliseconds "
                 "every value falls inside the period the rest of the device supports, so the "
                 "unit is taken from the data rather than from the column name. No value fell on "
                 "midnight in UTC, so the column carries an instant and not a calendar date. The "
                 "conversion is done in this module rather than by the shared helper so the "
                 "millisecond part is kept. status and unread are reported as stored. The device "
                 "tested carried no copy of the app binary, so no code mapping any stored value "
                 "to a label could be read from the extraction and none is asserted here. "
                 "Latitude and Longitude are reported as stored and no reading of them is "
                 "asserted. On the one device tested they were populated on 3 of 111 rows and "
                 "each of those three stored 0.0 in both columns, every place name column was "
                 "empty on every row, and the app's own preferences carry a key recording that "
                 "the coarse location permission had been permanently denied. Those columns are "
                 "carried despite being uniformly empty here because they are the only record of "
                 "where a recognition happened. The KML export skips a row whose coordinates are "
                 "zero, so it produced no points here and that path is code present and "
                 "unexercised. status was SUCCESSFUL on every row tested, so no failed or "
                 "pending recognition was seen and the column is unexercised beyond that value. "
                 "The table's retry count, audio offset and locale columns are not reported: "
                 "they were constant or empty across the device tested and carry no fact an "
                 "examiner can act on. The release date sits in Shazam Tracks rather than being "
                 "repeated per recognition. Cover art is shown when the artwork URL the track "
                 "row stores hashes to a file present in the app's image cache; on the device "
                 "tested that resolved 102 of the 109 rows carrying a URL, and a row whose "
                 "artwork is no longer cached is still reported with the cell left empty. "
                 "Artwork is only taken from the image cache inside the same app data directory "
                 "as the database the row came from, so a second Android user's cached file is "
                 "never shown against another user's row. The database uses WAL and the sidecars "
                 "are matched with it: the tested device held 2 recognitions that are only "
                 "present once the WAL is applied. The one device tested carried a single copy "
                 "of the app data directory, so the storage view handling and that scoping were "
                 "exercised against a constructed tree holding the directory at data/data, at "
                 "data/user/0 and at data/user/10 rather than against a real extraction: the two "
                 "user 0 spellings were read once and the second user was reported separately.",
        "paths": ('*/com.shazam.android/databases/library.db*',
                  '*/com.shazam.android/cache/image_cache/*'),
        "output_types": ['html', 'tsv', 'timeline', 'lava', 'kml'],
        "artifact_icon": "music",
    },
    "shazam_tracks": {
        "name": "Shazam Tracks",
        "description": "Rows of the track table in the Shazam library database, with the artists, "
                       "genres and moods the app stored against each track, how many times it "
                       "was recognised and when it was last recognised",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Shazam",
        "notes": "A track row is created for a recognition result, so this table holds the "
                 "distinct tracks behind the rows in Shazam Recognitions rather than a separate "
                 "activity. Artists are joined through the apple_artist_track table on the "
                 "artist_adam_id and artist_id columns, which agreed on 109 of the 110 join rows "
                 "on the device tested; the one row without a match is reported with the artist "
                 "left empty. The artist table is reported through this join rather than as its "
                 "own artifact: it carries no time of its own and nothing beyond the names and "
                 "identifiers shown here. genre_type is reported as stored. release_date is "
                 "stored as text and is passed through as stored rather than parsed, because the "
                 "values seen were years rather than full dates. last_attempt_timestamp comes "
                 "from the metadata_update_status table and is Unix milliseconds on the same "
                 "basis as the recognition timestamp; that table's status column read success on "
                 "every row tested and is not reported. Cover art is shown when the stored "
                 "artwork URL hashes to a file present in the app's image cache in the same app "
                 "data directory, which resolved 91 of the 98 stored URLs on the device tested.",
        "paths": ('*/com.shazam.android/databases/library.db*',
                  '*/com.shazam.android/cache/image_cache/*'),
        "output_types": "standard",
        "artifact_icon": "disc",
    },
    "shazam_http_cache": {
        "name": "Shazam HTTP Cache",
        "description": "Entries of the app's HTTP response cache, each holding the URL the app "
                       "requested, the times the request was sent and the response received, and "
                       "the track the URL refers to where the library database records it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Shazam",
        "notes": "Each entry dates a fetch the app made, which is why the entries are reported "
                 "individually rather than summarised. The cache is a DiskLruCache holding a "
                 "metadata file and a body file per entry. The metadata file records the URL on "
                 "its first line, and the entry file name is the MD5 of that URL, which held for "
                 "all 417 entries on the device tested, so the URL to file link is read from the "
                 "cache rather than inferred. Where a URL contains a track key or an artist "
                 "identifier the library database also holds, the track title is filled in from "
                 "that database so the row names what was fetched; on the device tested 196 of "
                 "417 URLs carried a known track key and 153 carried a known artist identifier, "
                 "and a URL matching neither is reported with those columns empty. The two times "
                 "are read from response headers the cache itself writes and which name their "
                 "own units in milliseconds; they describe the app's own fetch and not anything "
                 "a server recorded. Every entry on the device tested was a GET that returned "
                 "200, so the method and status columns were dropped as uniformly constant. The "
                 "response body is reported by size only and is not decoded here.",
        "paths": ('*/com.shazam.android/cache/OK_HTTP_CACHE/*',
                  '*/com.shazam.android/databases/library.db*'),
        "output_types": "standard",
        "artifact_icon": "api",
    },
    "shazam_offline_request_queue": {
        "name": "Shazam Offline Request Queue",
        "description": "Rows of the guaranteed_requests table in the Shazam guaranteed requests "
                       "database, holding HTTP requests the app queued for later delivery",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Shazam",
        "notes": "The stored request is JSON carrying an HTTP method and a URL, and the URL "
                 "carries app and device identifying values, which is why the row is reported "
                 "rather than summarised. The table has no timestamp column, so when a request "
                 "was queued cannot be read from it. The database carries a trigger that deletes "
                 "a row once its retry count reaches ten, so a queue that failed repeatedly "
                 "leaves nothing behind. On the device tested the table held one row.",
        "paths": ('*/com.shazam.android/databases/guaranteed_requests.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "shazam_app_state": {
        "name": "Shazam App State",
        "description": "Entries of the Shazam application preferences file, holding the install "
                       "identifier, the times the app recorded for its last recognition and last "
                       "foreground, and the flags it kept about its own state",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Shazam",
        "notes": "Every entry in the file is reported with its stored type and value. The file is "
                 "small and holds the install identifier, the last recognition and last "
                 "foreground times and the app's record of which permissions were refused, so it "
                 "is reported whole rather than filtered: dropping keys would misstate what the "
                 "file contains, and the counters it also holds are few. A UTC reading is filled "
                 "in only where the value is a thirteen digit integer, which is the width every "
                 "value that behaved as a time had on the device tested; the one shorter integer "
                 "in the file is left unconverted rather than read as a time it is not. The key "
                 "names are the app's own and several are abbreviated; no meaning is assigned to "
                 "a key beyond what its name states. A value longer than 512 characters is "
                 "reported by length instead of content, because the long values on the device "
                 "tested were a configuration blob and a category mapping table the app fetches "
                 "from its own endpoint rather than anything the user entered. The app also keeps "
                 "a com.shazam.ams.xml preferences file whose keys and values are encrypted: it "
                 "carries the two androidx security keyset entries that name the scheme, and the "
                 "master key for it lives in the device keystore rather than in app storage, so "
                 "it is not recoverable from an extraction of this directory and is not reported "
                 "here.",
        "paths": ('*/com.shazam.android/shared_prefs/com.shazam.android_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
    "shazam_cached_content": {
        "name": "Shazam Cached Content",
        "description": "One row per store of content the app downloaded and held, giving what "
                       "each store contains, how much of it is on disk and the period the store "
                       "itself records",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Shazam",
        "notes": "These stores hold content the app fetched, not anything the user produced, and "
                 "their individual items are not enumerated here because a single cached image, "
                 "video fragment or announcement carries no fact an examiner can act on. The "
                 "artwork that is tied to a recognition is rendered on the Shazam Recognitions "
                 "and Shazam Tracks rows instead, which is where it answers a question. The "
                 "underlying files remain in the extraction at the paths this artifact names, so "
                 "the detail is still reachable. Image cache: a DiskLruCache whose entry name is "
                 "a hash of the key the image was stored under; the entry does not record that "
                 "key, so an item is counted as linked only where a track artwork URL in the "
                 "library database has a SHA-256 equal to the entry name. The two times come "
                 "from the first and second lines of an entry's metadata file, read as Unix "
                 "milliseconds; the first was never later than the second across all 463 "
                 "metadata files on the device tested, and the file format does not name either "
                 "of them, so no role is assigned to them. Video cache: the index is read with "
                 "every declared length checked against the bytes actually remaining, so a "
                 "truncated index stops rather than reporting a structure that is not there; on "
                 "the device tested it declared 50 entries and all 50 parsed, leaving four "
                 "trailing bytes unread. Its URLs pointed at Apple video preview hosts and none "
                 "of the 50 carried a track key or artist identifier the library database also "
                 "held, so no entry could be tied to a recognition. The times come from the "
                 "third field of the fragment file names, read as Unix milliseconds. No entry "
                 "held its full declared length, so the fragments are partial and are not "
                 "checked in as media. Home screen announcements: rows the app stored for "
                 "display, whose payload field names are single letters, and whose count is "
                 "reported without the payloads because nothing in them names a user action. "
                 "Stores are counted per app data directory, so a second Android user's caches "
                 "are reported as their own rows.",
        "paths": ('*/com.shazam.android/cache/image_cache/*',
                  '*/com.shazam.android/cache/video_cache/*',
                  '*/com.shazam.android/databases/library.db*'),
        "output_types": "standard",
        "artifact_icon": "cloud-download",
    },
}

import hashlib
import json
import os
import re
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_sqlite_db_records,
    logfunc,
)
from scripts.artifacts.storagePathViews import unique_files

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Every value this module converts is known to be milliseconds from the data it was read
# against, so the conversion is done here rather than through the shared helper, which
# sizes the unit from the value's magnitude and returns whole seconds.
def _ms_to_utc(value):
    """A UTC datetime from a Unix millisecond value, keeping the sub-second part."""
    if value is None or value == '':
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value == 0:
        return ''
    return _UNIX_EPOCH_UTC + timedelta(milliseconds=value)


def _relative(context, path):
    return context.get_relative_path(path).replace('\\', '/')


def _matching(context, files_found, pattern):
    """The files whose evidence relative path matches a compiled pattern."""
    return [path for path in files_found if pattern.search(_relative(context, path))]


def _container(relative):
    """The app data directory a relative path sits under, matched on a path segment.

    A cache entry is only joined to a database inside the same directory. An extraction
    can carry a second Android user's copy of this app, and that user's cache holds that
    user's images, so keying a cache index on the entry name alone would let one user's
    file be reported against another user's row.
    """
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == 'com.shazam.android':
            return '/'.join(parts[:position + 1])
    return relative


_LIBRARY_DB = re.compile(r'/databases/library\.db$')
_GUARANTEED_DB = re.compile(r'/databases/guaranteed_requests\.db$')
_IMAGE_CACHE = re.compile(r'/cache/image_cache/([0-9a-f]{64})\.([01])$')
_OKHTTP_CACHE = re.compile(r'/cache/OK_HTTP_CACHE/([0-9a-f]{32})\.0$')
_VIDEO_INDEX = re.compile(r'/cache/video_cache/cached_content_index\.exi$')
_VIDEO_FRAGMENT = re.compile(r'/cache/video_cache/.*/(\d+)\.(\d+)\.(\d+)\.v\d+\.exo$')
_APP_PREFS = re.compile(r'/shared_prefs/com\.shazam\.android_preferences\.xml$')
_DIGIT_RUN = re.compile(r'\d+')


def _artwork_index(context, files_found):
    """{(container, entry name): payload path} for the image cache bodies present."""
    index = {}
    for path in files_found:
        relative = _relative(context, path)
        match = _IMAGE_CACHE.search(relative)
        if match and match.group(2) == '1':
            index[(_container(relative), match.group(1))] = path
    return index


def _artwork_media(index, container, url, name):
    """The checked in cached image for a stored artwork URL, or an empty cell.

    The cache entry is named for the hash of the key the image was stored under. Where
    that key is the URL the database recorded, the URL resolves the file; where the app
    stored the image under some other key it does not, and the cell is left empty rather
    than filled from a file matched some other way.
    """
    if not url:
        return ''
    path = index.get((container, hashlib.sha256(str(url).encode()).hexdigest()))
    if not path:
        return ''
    return check_in_media(path, name) or ''


def _image_cache_metadata(path):
    """(first value, second value, headers) from an image cache metadata file.

    The file holds two integers, a third field, a header count and that many header
    lines. Anything that does not hold to that shape is reported as unparsed rather than
    guessed at.
    """
    try:
        with open(path, 'rb') as handle:
            lines = handle.read().split(b'\n')
    except OSError as error:
        logfunc(f'Could not read Shazam image cache metadata {path}: {error}')
        return None, None, {}
    if len(lines) < 4:
        return None, None, {}
    try:
        first = int(lines[0])
        second = int(lines[1])
        count = int(lines[3])
    except ValueError:
        return None, None, {}
    headers = {}
    for line in lines[4:4 + count]:
        text = line.decode('utf-8', 'replace')
        if ':' in text:
            key, value = text.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    return first, second, headers


@artifact_processor
def shazam_recognitions(context):
    files_found = unique_files(context)
    artwork = _artwork_index(context, files_found)
    data_list = []
    source_path = ''

    for path in _matching(context, files_found, _LIBRARY_DB):
        source_path = path
        container = _container(_relative(context, path))
        for row in get_sqlite_db_records(path, '''
                SELECT tag.timestamp,
                       track.track_title,
                       (SELECT group_concat(artist.artist_name, ', ')
                          FROM apple_artist_track
                          JOIN artist ON artist.artist_id = apple_artist_track.artist_adam_id
                         WHERE apple_artist_track.track_key = tag.track_key),
                       tag.status,
                       tag.lat,
                       tag.lon,
                       tag.location_name,
                       tag.location_city,
                       tag.location_country,
                       tag.unread,
                       tag.track_key,
                       tag.request_id,
                       track.cover_art
                  FROM tag
                  LEFT JOIN track ON track.track_key = tag.track_key
                 ORDER BY tag.timestamp'''):
            (timestamp, title, artists, status, lat, lon, location_name, location_city,
             location_country, unread, track_key, request_id, cover_art) = row
            data_list.append((
                _ms_to_utc(timestamp),
                title or '',
                artists or '',
                _artwork_media(artwork, container, cover_art, title or track_key or ''),
                status,
                lat,
                lon,
                location_name or '',
                location_city or '',
                location_country or '',
                unread,
                track_key or '',
                request_id,
                cover_art or '',
                _relative(context, path),
            ))

    data_headers = (
        ('Recognition Time', 'datetime'),
        'Track Title',
        'Artist',
        ('Cover Art', 'media'),
        'Status (as stored)',
        'Latitude',
        'Longitude',
        'Location Name',
        'Location City',
        'Location Country',
        'Unread (as stored)',
        'Track Key',
        'Request ID',
        'Cover Art URL',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def shazam_tracks(context):
    files_found = unique_files(context)
    artwork = _artwork_index(context, files_found)
    data_list = []
    source_path = ''

    for path in _matching(context, files_found, _LIBRARY_DB):
        source_path = path
        container = _container(_relative(context, path))
        for row in get_sqlite_db_records(path, '''
                SELECT track.track_key,
                       track.track_title,
                       (SELECT group_concat(artist.artist_name, ', ')
                          FROM apple_artist_track
                          JOIN artist ON artist.artist_id = apple_artist_track.artist_adam_id
                         WHERE apple_artist_track.track_key = track.track_key),
                       track.release_date,
                       (SELECT group_concat(genre_id || ' (' || genre_type || ')', ', ')
                          FROM track_genre WHERE track_genre.track_key = track.track_key),
                       (SELECT group_concat(mood_id, ', ')
                          FROM track_mood WHERE track_mood.track_key = track.track_key),
                       (SELECT count(*) FROM tag WHERE tag.track_key = track.track_key),
                       (SELECT max(timestamp) FROM tag WHERE tag.track_key = track.track_key),
                       (SELECT last_attempt_timestamp FROM metadata_update_status
                         WHERE metadata_update_status.track_key = track.track_key),
                       track.cover_art
                  FROM track
                 ORDER BY track.track_title'''):
            (track_key, title, artists, release_date, genres, moods, tag_count, last_tag,
             last_attempt, cover_art) = row
            data_list.append((
                _ms_to_utc(last_tag),
                _ms_to_utc(last_attempt),
                title or '',
                artists or '',
                _artwork_media(artwork, container, cover_art, title or track_key or ''),
                release_date or '',
                genres or '',
                moods or '',
                tag_count,
                track_key,
                cover_art or '',
                _relative(context, path),
            ))

    data_headers = (
        ('Most Recent Recognition', 'datetime'),
        ('Metadata Update Attempt', 'datetime'),
        'Track Title',
        'Artist',
        ('Cover Art', 'media'),
        'Release Date (as stored)',
        'Genres (as stored)',
        'Moods (as stored)',
        'Recognition Count',
        'Track Key',
        'Cover Art URL',
        'Source File',
    )
    return data_headers, data_list, source_path


def _preference_entries(path):
    """(key, stored type, value) for each entry of an Android preferences file."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'Could not read Shazam preferences {path}: {error}')
        return
    for element in root:
        key = element.get('name')
        if key is None:
            continue
        if element.tag == 'string':
            yield key, 'string', element.text or ''
        elif element.tag == 'set':
            yield key, 'set', ', '.join(child.text or '' for child in element)
        else:
            yield key, element.tag, element.get('value', '')


@artifact_processor
def shazam_offline_request_queue(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for path in _matching(context, files_found, _GUARANTEED_DB):
        source_path = path
        for row in get_sqlite_db_records(path, '''
                SELECT _id, retries, request FROM guaranteed_requests ORDER BY _id'''):
            row_id, retries, request = row
            method = ''
            url = ''
            try:
                parsed = json.loads(request)
                http = parsed.get('httpRequest', {}) if isinstance(parsed, dict) else {}
                method = http.get('httpmethod', '') or ''
                url = http.get('url', '') or ''
            except (TypeError, ValueError):
                pass
            data_list.append((
                method,
                url,
                retries,
                row_id,
                _relative(context, path),
            ))

    data_headers = (
        'Method',
        'URL',
        'Retries',
        'Row ID',
        'Source File',
    )
    return data_headers, data_list, source_path


def _track_lookup(context, files_found):
    """{container: {identifier: label}} for the track and artist ids the library records.

    A cached URL carries these ids in its path, so the identifier is what names the row.
    Keys are matched as whole runs of digits rather than as substrings, so a short id
    cannot match part of a longer number that happens to contain it.
    """
    lookup = {}
    for path in _matching(context, files_found, _LIBRARY_DB):
        container = _container(_relative(context, path))
        names = lookup.setdefault(container, {})
        for row in get_sqlite_db_records(path, 'SELECT track_key, track_title FROM track'):
            if row[0]:
                names[str(row[0])] = (str(row[0]), row[1] or '')
        for row in get_sqlite_db_records(path, 'SELECT artist_id, artist_name FROM artist'):
            if row[0] and str(row[0]) not in names:
                names[str(row[0])] = ('', row[1] or '')
    return lookup


@artifact_processor
def shazam_http_cache(context):
    files_found = unique_files(context)
    lookup = _track_lookup(context, files_found)
    bodies = {}
    for path in files_found:
        relative = _relative(context, path)
        if relative.endswith('.1') and '/cache/OK_HTTP_CACHE/' in relative:
            bodies[(_container(relative), os.path.basename(relative)[:-2])] = path

    data_list = []
    source_path = ''
    for path in files_found:
        relative = _relative(context, path)
        match = _OKHTTP_CACHE.search(relative)
        if not match:
            continue
        source_path = path
        entry = _okhttp_entry(path)
        if entry is None:
            continue
        url, _method, _status, headers = entry
        container = _container(relative)
        body = bodies.get((container, match.group(1)))
        track_key, title = '', ''
        names = lookup.get(container, {})
        for token in _DIGIT_RUN.findall(url):
            if token in names:
                track_key, title = names[token]
                break
        data_list.append((
            _ms_to_utc(headers.get('okhttp-sent-millis')),
            _ms_to_utc(headers.get('okhttp-received-millis')),
            title,
            url,
            track_key,
            headers.get('content-type', ''),
            os.path.getsize(body) if body and os.path.exists(body) else '',
            match.group(1),
            _relative(context, path),
        ))

    data_list.sort(key=lambda row: (row[0] == '', row[0]))
    data_headers = (
        ('Request Sent', 'datetime'),
        ('Response Received', 'datetime'),
        'Track or Artist Named In URL',
        'URL',
        'Track Key',
        'Content Type',
        'Body Size (bytes)',
        'Cache Entry Name',
        'Source File',
    )
    return data_headers, data_list, source_path


def _okhttp_entry(path):
    """(url, method, status line, headers) from an HTTP cache metadata file.

    The file records the URL, the method, a request header count, the status line and a
    response header count, each on its own line, followed by that many header lines. A
    file that does not hold to that shape is skipped rather than read past.
    """
    try:
        with open(path, 'rb') as handle:
            lines = handle.read().decode('utf-8', 'replace').split('\n')
    except OSError as error:
        logfunc(f'Could not read Shazam HTTP cache entry {path}: {error}')
        return None
    if len(lines) < 5:
        return None
    url, method = lines[0], lines[1]
    try:
        request_headers = int(lines[2])
    except ValueError:
        return None
    offset = 3 + request_headers
    if offset + 1 >= len(lines):
        return None
    status = lines[offset]
    try:
        count = int(lines[offset + 1])
    except ValueError:
        return None
    headers = {}
    for line in lines[offset + 2:offset + 2 + count]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    return url, method, status, headers


def _artwork_url_index(context, files_found):
    """{(container, cache entry name): URL} for artwork URLs the library database records.

    A URL is only offered for an entry in the same app data directory as the database it
    came from, so a second Android user's cached file is not labelled with a URL taken
    from another user's database.
    """
    index = {}
    for path in _matching(context, files_found, _LIBRARY_DB):
        container = _container(_relative(context, path))
        for query in ('SELECT cover_art FROM track WHERE cover_art IS NOT NULL',
                      'SELECT artist_img FROM artist WHERE artist_img IS NOT NULL'):
            for (url,) in get_sqlite_db_records(path, query):
                index[(container, hashlib.sha256(str(url).encode()).hexdigest())] = url
    return index


def _video_index_entries(path):
    """(content id, key, declared length) for each entry of the video cache index.

    Every declared length is checked against the bytes remaining before it is read, so a
    truncated or unexpected index stops at the point it stops making sense rather than
    reporting entries that are not there.
    """
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        logfunc(f'Could not read Shazam video cache index {path}: {error}')
        return
    end = len(raw)
    if end < 12:
        return
    offset = 8
    count = struct.unpack_from('>i', raw, offset)[0]
    offset += 4
    if count < 0:
        return

    def read_string(position):
        if position + 2 > end:
            return None, position
        length = struct.unpack_from('>H', raw, position)[0]
        position += 2
        if position + length > end:
            return None, position
        return raw[position:position + length].decode('utf-8', 'replace'), position + length

    for index in range(count):
        if offset + 4 > end:
            logfunc(f'Shazam video cache index ended after {index} of {count} entries: {path}')
            return
        content_id = struct.unpack_from('>i', raw, offset)[0]
        offset += 4
        key, offset = read_string(offset)
        if key is None or offset + 4 > end:
            logfunc(f'Shazam video cache index ended inside entry {index}: {path}')
            return
        metadata_count = struct.unpack_from('>i', raw, offset)[0]
        offset += 4
        declared = None
        for _ in range(max(metadata_count, 0)):
            name, offset = read_string(offset)
            if name is None or offset + 4 > end:
                logfunc(f'Shazam video cache index ended inside entry {index}: {path}')
                return
            length = struct.unpack_from('>i', raw, offset)[0]
            offset += 4
            if length < 0 or offset + length > end:
                logfunc(f'Shazam video cache index ended inside entry {index}: {path}')
                return
            value = raw[offset:offset + length]
            offset += length
            if name == 'exo_len' and length == 8:
                declared = struct.unpack('>q', value)[0]
        yield content_id, key, declared


@artifact_processor
def shazam_cached_content(context):
    """One row per store of downloaded content, counted rather than enumerated."""
    files_found = unique_files(context)
    urls = _artwork_url_index(context, files_found)
    stores = {}

    def store(container, name):
        return stores.setdefault((container, name), {
            'items': 0, 'linked': 0, 'bytes': 0, 'times': [], 'path': '', 'source': ''})

    for path in files_found:
        relative = _relative(context, path)
        container = _container(relative)
        match = _IMAGE_CACHE.search(relative)
        if match:
            entry = store(container, 'Image cache')
            entry['path'] = f'{container}/cache/image_cache'
            entry['source'] = entry['source'] or relative
            if match.group(2) == '1':
                entry['items'] += 1
                entry['bytes'] += os.path.getsize(path) if os.path.exists(path) else 0
                if (container, match.group(1)) in urls:
                    entry['linked'] += 1
            else:
                first, second, _headers = _image_cache_metadata(path)
                entry['times'] += [value for value in (first, second) if value]
            continue
        match = _VIDEO_FRAGMENT.search(relative)
        if match:
            entry = store(container, 'Video cache')
            entry['path'] = f'{container}/cache/video_cache'
            entry['bytes'] += os.path.getsize(path) if os.path.exists(path) else 0
            entry['times'].append(int(match.group(3)))
            continue
        if _VIDEO_INDEX.search(relative):
            entry = store(container, 'Video cache')
            entry['path'] = f'{container}/cache/video_cache'
            entry['source'] = relative
            entry['items'] += sum(1 for _ in _video_index_entries(path))

    for path in _matching(context, files_found, _LIBRARY_DB):
        relative = _relative(context, path)
        entry = store(_container(relative), 'Home screen announcements')
        entry['path'] = relative
        entry['source'] = relative
        for row in get_sqlite_db_records(
                path, 'SELECT count(*) FROM home_screen_announcement'):
            entry['items'] += row[0]

    data_list = []
    source_path = ''
    for (_container_key, name), entry in sorted(stores.items(), key=lambda item: item[0][1]):
        source_path = source_path or entry['source']
        data_list.append((
            _ms_to_utc(min(entry['times'])) if entry['times'] else '',
            _ms_to_utc(max(entry['times'])) if entry['times'] else '',
            name,
            entry['items'],
            entry['linked'] if name == 'Image cache' else '',
            entry['bytes'] or '',
            entry['path'],
            entry['source'],
        ))

    data_headers = (
        ('Earliest Time Recorded In Store', 'datetime'),
        ('Latest Time Recorded In Store', 'datetime'),
        'Store',
        'Items',
        'Items Linked To A Library Record',
        'Bytes On Disk',
        'Store Path',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def shazam_app_state(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for path in _matching(context, files_found, _APP_PREFS):
        source_path = path
        relative = _relative(context, path)
        for key, stored_type, value in _preference_entries(path):
            text = str(value)
            reported = text if len(text) <= 512 else f'<{len(text)} characters, not reported>'
            converted = ''
            if stored_type == 'long' and re.fullmatch(r'-?\d{13}', text):
                converted = _ms_to_utc(text)
            data_list.append((
                converted,
                key,
                stored_type,
                reported,
                relative,
            ))

    data_list.sort(key=lambda row: row[1])
    data_headers = (
        ('Value as UTC where the value is Unix milliseconds', 'datetime'),
        'Preference Key',
        'Stored Type',
        'Value',
        'Source File',
    )
    return data_headers, data_list, source_path
