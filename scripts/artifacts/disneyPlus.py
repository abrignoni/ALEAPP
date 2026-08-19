__artifacts_v2__ = {
    "disneyplus_resume_points": {
        "name": "Disney+ - Playback Resume Points",
        "description": "Parses the playback resume positions stored by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from the bookmarks table of the app's db_offline_bookmarks database. "
                 "occurredOn is Unix milliseconds. playhead and runtime are media offsets "
                 "rather than timestamps and are reported both as stored and formatted; the "
                 "unit is seconds, established from the data because every populated runtime "
                 "falls in the range of a feature or episode length when read as seconds and "
                 "under ten seconds when read as milliseconds, and because playhead is at or "
                 "below runtime on every row where runtime is populated. The app binary is "
                 "not present in a data-only container, so the unit is not sourced from the "
                 "producing call site. ccDefault and ccMedia are undocumented and are "
                 "reported as stored; nothing in the container defines them. A row's title is "
                 "filled in only where the app's own cached content responses name the same "
                 "content id, and is left empty otherwise. The database carries no "
                 "write-ahead log and its rollback journal is zero length, so the committed "
                 "state is the only state. Field mapping was done against one private sample "
                 "from a single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/databases/db_offline_bookmarks*',
                  '*/com.disney.disneyplus/cache/sdk-cache/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "player-play"
    },
    "disneyplus_last_played": {
        "name": "Disney+ - Last Played Item",
        "description": "Parses the last played item recorded by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from the bookmarksHandshake keys of the app's default shared "
                 "preferences file. Each value is a JSON object naming a media id, a content "
                 "id, a series id, a content identifier type and a timestamp in Unix "
                 "milliseconds. One key records the last item played overall and a further "
                 "key is written per series, with the series identifier carried in the key "
                 "name itself. On the one tested sample the content id of the overall key was "
                 "also present in the resume points table, which is a recorded link rather "
                 "than a correlation. contentIdentifierType is reported as stored. Field "
                 "mapping was done against one private sample from a single device; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/shared_prefs/default.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "player-track-next"
    },
    "disneyplus_recent_searches": {
        "name": "Disney+ - Recent Searches",
        "description": "Parses the recent search terms stored by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from the recentSearches key of RecentSearchSharedPref. The value is a "
                 "JSON object keyed by profile id, so a term is attributable to the profile "
                 "that holds it. Each entry carries the search term together with a content "
                 "id. The store records no time for a search, so no date is reported and the "
                 "order is the order the file holds. The searchTerm value is text the store "
                 "holds against that profile; the store does not itself distinguish a term "
                 "the user typed from one the app placed there. Field mapping was done "
                 "against one private sample from a single device; no sample data is recorded "
                 "for it.",
        "paths": ('*/com.disney.disneyplus/shared_prefs/RecentSearchSharedPref.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "disneyplus_session": {
        "name": "Disney+ - Session State",
        "description": "Parses the streaming SDK session state of the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from the BAM_SDK_STORAGE shared preferences file. The session state "
                 "value records when the access context was generated, when it expires, the "
                 "service region, the token type, a refresh attempt count and the time of the "
                 "last refresh failure, all as ISO 8601 strings carrying their own offset. "
                 "The access and refresh tokens in the same object are five part JWE, so "
                 "their claims are encrypted and are not recoverable from the container; the "
                 "tokens themselves are present in the source file and are not reproduced "
                 "here. The offline fallback value names a profile id, which on the one "
                 "tested sample was the same profile id the resume points table and the "
                 "recent search store carry. The device grant records only its grant type and "
                 "an assertion. Field mapping was done against one private sample from a "
                 "single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/shared_prefs/BAM_SDK_STORAGE.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "key"
    },
    "disneyplus_app_settings": {
        "name": "Disney+ - App Settings and State",
        "description": "Parses the app state and playback preferences of the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Key and value pairs from the app's own shared preferences files: the "
                 "default file, BAMPLAYER, AnalyticsSharedPrefs and Conviva. Values are "
                 "reported as stored. A value is additionally rendered as a UTC timestamp "
                 "only where the key names a time and the value is a thirteen digit integer; "
                 "on the one tested sample the app backgrounded key resolved to within a "
                 "second of the most recent resume point write, which is what supports "
                 "reading it as milliseconds. The bookmarksHandshake keys of the same file "
                 "are reported by the Last Played Item artifact instead of here. Third party "
                 "software development kit preference files that sit in the same directory "
                 "are not read by this artifact. Field mapping was done against one private "
                 "sample from a single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/shared_prefs/default.xml',
                  '*/com.disney.disneyplus/shared_prefs/BAMPLAYER.xml',
                  '*/com.disney.disneyplus/shared_prefs/AnalyticsSharedPrefs.xml',
                  '*/com.disney.disneyplus/shared_prefs/Conviva.xml'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "disneyplus_home_sets": {
        "name": "Disney+ - Home Page Sets",
        "description": "Parses the home page set availability cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from contentSetAvailability, whose keys carry a set type and a set id "
                 "and whose values record availability. The observed values are HAS_CONTENT "
                 "and UNKNOWN, taken from the file rather than from any external list. These "
                 "rows record the rails the service composed for the profile, including "
                 "recommendation, trending, because you watched and continue watching sets. "
                 "They are a property of the page the service returned and do not establish "
                 "that the user opened or interacted with any of them. The store records no "
                 "time. Field mapping was done against one private sample from a single "
                 "device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/shared_prefs/contentSetAvailability.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "layout-grid"
    },
    "disneyplus_avatars": {
        "name": "Disney+ - Avatars",
        "description": "Parses the profile avatars cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from the AvatarImpl table of the app's profiles database. That "
                 "database holds this table only and carries no profile record, so it names "
                 "avatars rather than the profiles on the account. Each row carries an avatar "
                 "id, a title, a master id and an image URL; on the one tested sample the "
                 "master id appeared inside the image URL on every row, which is a recorded "
                 "link between the two. The table does not record which avatar a profile "
                 "selected. The database carries no write-ahead log and its rollback journal "
                 "is zero length. Field mapping was done against one private sample from a "
                 "single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/databases/profiles*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user-circle"
    },
    "disneyplus_cached_titles": {
        "name": "Disney+ - Cached Titles",
        "description": "Parses the title metadata cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Titles read from the content service responses held in the app's sdk-cache, "
                 "which is a DiskLruCache whose entry records the request URL alongside the "
                 "response body. Bodies are gzip encoded and are decompressed before reading. "
                 "Each title carries the content id, content type, program type, encoded "
                 "series id, family id and the availability region the response was served "
                 "for. These rows are the catalogue the service returned for the profile, "
                 "covering curated, trending, recommendation, because you watched and up next "
                 "sets. A row records what the response contained and does not establish that "
                 "the user viewed, selected or watched that title. The endpoint each title "
                 "came from is reported so the two can be told apart. Field mapping was done "
                 "against one private sample from a single device; no sample data is recorded "
                 "for it.",
        "paths": ('*/com.disney.disneyplus/cache/sdk-cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "movie"
    },
    "disneyplus_playback_requests": {
        "name": "Disney+ - Playback Requests",
        "description": "Parses the cached streaming requests of the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Read from the request URLs recorded in the app's sdk-cache entries for the "
                 "media delivery hosts. The URL path carries a media identifier, a device "
                 "identifier, an account identifier, a key id and an expiry, each reported as "
                 "the URL stores it. The expiry is a Unix second value naming when the "
                 "delivery token ceases to be valid; it is not the time the request was made "
                 "and is reported as an expiry rather than as an event time. The cached "
                 "bodies are HLS playlists and a trickplay index, which is what the entry's "
                 "content type declares. A cached request records that the app asked for the "
                 "manifest, not how much of the media was played. Field mapping was done "
                 "against one private sample from a single device; no sample data is recorded "
                 "for it.",
        "paths": ('*/com.disney.disneyplus/cache/sdk-cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud-download"
    },
    "disneyplus_trickplay": {
        "name": "Disney+ - Trickplay Frames",
        "description": "Checks in the trickplay preview frames cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "The sdk-cache entries whose content type is application/bif hold a Base "
                 "Index Frames file: an eight byte signature, a declared image count, a "
                 "declared timestamp multiplier and an index of frame number and byte offset "
                 "pairs, each pointing at a JPEG, closed by a terminator entry giving the end "
                 "of the last one. Every declared offset is checked against the bytes "
                 "actually present. A frame is reported only where the bytes present start "
                 "with a start of image marker and end with an end of image marker, and the "
                 "walk stops at the first entry that does not, so a truncated entry yields "
                 "the frames it really holds rather than a count taken from the header. On "
                 "the one tested sample both files declared 185 images and the terminator "
                 "declared an end one byte past the cached body; the last frame was complete "
                 "within the bytes present, so it is reported and flagged in the Declared End "
                 "Overran Cached Bytes column rather than dropped. The frames are checked in "
                 "as embedded media and rendered. The media identifier "
                 "is taken from the request URL the cache entry records. The app fetches the "
                 "whole index for a title, so the presence of a frame does not establish that "
                 "the offset it sits at was played. Frame numbers are reported as the index "
                 "stores them. Field mapping was done against one private sample from a "
                 "single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/cache/sdk-cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo-video"
    },
    "disneyplus_cached_images": {
        "name": "Disney+ - Cached Images",
        "description": "Checks in the images cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Images from three stores are checked in and rendered. An http-cache entry "
                 "records its own request URL, so those rows carry the URL the image came "
                 "from. The files under files/offline_images are named with a numeric "
                 "identifier that does not appear anywhere else in the container; a URL is "
                 "reported for one of them only where its bytes are identical to a cached "
                 "response body, which is a content hash match and is stated as such in the "
                 "Link Basis column. A glide-cache-v2 file name is not derived from the URL: it "
                 "was tested against the MD5, SHA-1 and SHA-256 of the URLs of images holding "
                 "identical bytes and matched none of them, so no link is asserted from the name; "
                 "those entries carry a URL only where the same content hash match applies. A "
                 "cached body may be stored gzip encoded, so images are read from the decoded "
                 "bytes and the encoding is reported. File type comes from the leading bytes "
                 "rather than the file name. "
                 "The same image may appear in more than one store and is reported once per "
                 "store. Field mapping was done against one private sample from a single "
                 "device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/cache/http-cache/*',
                  '*/com.disney.disneyplus/cache/glide-cache-v2/*',
                  '*/com.disney.disneyplus/files/offline_images/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo"
    },
    "disneyplus_sdk_events": {
        "name": "Disney+ - SDK Events",
        "description": "Parses the streaming SDK telemetry events of the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "Each file under files/dustv2 is one queued telemetry event in CloudEvents "
                 "form. The event time and the invocation start time are ISO 8601 strings "
                 "carrying their own offset and are reported with that offset preserved. The "
                 "event records the service operation invoked, the host, path and method "
                 "requested, the response status where one was received, the round trip time, "
                 "the serving region and the session id the event was raised under. Error "
                 "codes are reported as stored; the values observed on the tested sample were "
                 "network-error and authenticationExpired, read from the files rather than "
                 "from any external list. These events record calls the app's SDK made and "
                 "the file name carries the queue time, so they evidence the app running "
                 "rather than anything the user chose. Field mapping was done against one "
                 "private sample from a single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/files/dustv2/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "activity"
    },
}

import gzip
import hashlib
import json
import os
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlparse

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    check_in_media,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.disney.disneyplus'

# Media delivery hosts seen in the app's own cached request URLs.
_MEDIA_HOST_RE = re.compile(r'\.media\.dssott\.com$')

# A preference key is rendered as a time only when it names one. Value must still be a
# 13 digit integer, so a key that names a duration rather than an instant is not converted.
_TIME_KEY_RE = re.compile(r'(backgrounded|_at|_time|timestamp|lastseen)$', re.IGNORECASE)

_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'jpg', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'png', 'image/png'),
    (b'GIF8', 'GIF', 'gif', 'image/gif'),
    (b'RIFF', 'WEBP', 'webp', 'image/webp'),
)

_BIF_MAGIC = b'\x89BIF\r\n\x1a\n'


def _relative(context, path):
    return context.get_relative_path(path)


def _matching(context, *fragments):
    '''Matched files whose relative path contains any fragment, one per storage view.'''
    out = []
    for file_found in unique_files(context):
        norm = str(file_found).replace('\\', '/')
        if any(frag in norm for frag in fragments):
            out.append(file_found)
    return out


def _named(context, *basenames):
    '''Matched files with these basenames, one per storage view.'''
    wanted = set(basenames)
    return [path for path in unique_files(context)
            if os.path.basename(str(path).replace('\\', '/')) in wanted]


def _rows(source_path, sql):
    '''Rows for sql. Empty on any SQLite error, which is logged.'''
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return []
    try:
        rows = db.cursor().execute(sql).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        rows = []
    db.close()
    return rows


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.

    Converted here rather than through the shared helper because every column routed
    through this is known to be milliseconds; the shared helper infers the unit from the
    value's magnitude, which cannot decide it.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


def _iso(value):
    '''An ISO 8601 string as a datetime keeping the offset the string carries.

    The string names its own offset, so it is not routed through a timezone database.
    The fractional part is padded because fromisoformat rejected counts other than three
    or six digits before Python 3.11 and the repo supports older runtimes.
    '''
    if not isinstance(value, str) or not value:
        return ''
    text = value.strip().replace('Z', '+00:00')
    match = re.match(r'^(.*\.)(\d{1,6})(.*)$', text)
    if match:
        text = f'{match.group(1)}{match.group(2).ljust(6, "0")}{match.group(3)}'
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return ''


def _clock(value):
    '''A media offset in seconds rendered as H:MM:SS, or '' when absent.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return f'{value // 3600}:{value // 60 % 60:02d}:{value % 60:02d}'


def _prefs(source_path):
    '''Key to value for an Android shared preferences file. Values are kept as text.'''
    out = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
        return out
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        value = element.get('value')
        if value is None:
            value = element.text or ''
        out[name] = (element.tag, value)
    return out


def _json_or_none(text):
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return None


def _cache_entries(paths):
    '''(url, headers, body_path) for each DiskLruCache entry whose body is present.

    The .0 member of an OkHttp entry begins with the request URL on its own line and the
    response headers follow. The body is the .1 member beside it.
    '''
    entries = []
    for path in paths:
        norm = str(path).replace('\\', '/')
        if not norm.endswith('.0'):
            continue
        body = str(path)[:-2] + '.1'
        if not os.path.exists(body):
            continue
        try:
            with open(path, 'rb') as handle:
                head = handle.read(65536).decode('utf-8', 'replace')
        except OSError:
            continue
        lines = head.split('\n')
        url = lines[0].strip()
        if not url.lower().startswith('http'):
            continue
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, _, val = line.partition(':')
                headers.setdefault(key.strip().lower(), val.strip())
        entries.append((url, headers, body))
    return entries


def _body_bytes(path):
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError:
        return b''
    if raw[:2] == b'\x1f\x8b':
        try:
            return gzip.decompress(raw)
        except (OSError, EOFError, gzip.BadGzipFile):
            return raw
    return raw


def _image_kind(data):
    for magic, label, extension, mime in _IMAGE_MAGIC:
        if data.startswith(magic):
            return label, extension, mime
    return '', '', ''


def _title_index(context):
    '''content id to (title, content type, program type) from the app's cached responses.

    A recorded lookup rather than a correlation: the title is read from the same response
    object that carries the content id.
    '''
    index = {}
    for _url, headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        if 'json' not in headers.get('content-type', ''):
            continue
        parsed = _json_or_none(_body_bytes(body))
        if parsed is None:
            continue
        for item in _walk_titles(parsed):
            content_id = item.get('contentId')
            text = item.get('text')
            if not isinstance(content_id, str) or not isinstance(text, dict):
                continue
            title = _title_text(text)
            if title and content_id not in index:
                index[content_id] = (title, item.get('contentType') or '',
                                     item.get('programType') or '')
    return index


def _walk_titles(node):
    '''Every dict in the tree that carries a contentId.'''
    if isinstance(node, dict):
        if isinstance(node.get('contentId'), str):
            yield node
        for value in node.values():
            yield from _walk_titles(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_titles(value)


def _title_text(text):
    """The display title from a cached title object.

    The object nests as text.title.<form>.<entity>.default.content, where form is full or
    slug and entity is program or series. The full form is the display title and the slug
    form is the URL fragment, so the form is selected by name rather than by taking the
    first string found.
    """
    if not isinstance(text, dict):
        return ''
    title = text.get('title')
    if not isinstance(title, dict):
        return ''
    for form in ('full', 'slug'):
        entities = title.get(form)
        if not isinstance(entities, dict):
            continue
        for entity in entities.values():
            if not isinstance(entity, dict):
                continue
            default = entity.get('default')
            if isinstance(default, dict) and isinstance(default.get('content'), str):
                return default['content']
    return ''


_BOOKMARK_SQL = ('SELECT `occurredOn`, `playhead`, `runtime`, `contentId`, `profileId`, '
                 '`ccDefault`, `ccMedia` FROM `bookmarks` ORDER BY `occurredOn` DESC')


@artifact_processor
def disneyplus_resume_points(context):
    data_list = []
    source_path = ''
    titles = _title_index(context)
    for file_found in _named(context, 'db_offline_bookmarks'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for row in _rows(file_found, _BOOKMARK_SQL):
            occurred, playhead, runtime, content_id, profile_id, cc_default, cc_media = row
            title = titles.get(content_id, ('', '', ''))
            data_list.append((
                _ms(occurred), title[0], _clock(playhead), _clock(runtime), playhead,
                runtime, content_id, profile_id,
                '' if cc_default is None else cc_default,
                '' if cc_media is None else cc_media,
                source_file))

    data_headers = (
        ('Occurred On', 'datetime'), 'Title', 'Playhead', 'Runtime', 'Playhead (seconds)',
        'Runtime (seconds)', 'Content ID', 'Profile ID', 'ccDefault (as stored)',
        'ccMedia (as stored)', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_last_played(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'default.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for key, (_tag, value) in _prefs(file_found).items():
            if not key.startswith('bookmarksHandshake'):
                continue
            parsed = _json_or_none(value)
            if not isinstance(parsed, dict):
                logfunc(f'Disney+: {key} in {os.path.basename(file_found)} is not JSON')
                continue
            data_list.append((
                _ms(parsed.get('timestamp')), key, parsed.get('contentId', ''),
                parsed.get('mediaId', ''), parsed.get('seriesId', ''),
                parsed.get('contentIdentifierType', ''), source_file))

    data_headers = (
        ('Timestamp', 'datetime'), 'Preference Key', 'Content ID', 'Media ID', 'Series ID',
        'Content Identifier Type (as stored)', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_recent_searches(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'RecentSearchSharedPref.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        entry = _prefs(file_found).get('recentSearches')
        parsed = _json_or_none(entry[1]) if entry else None
        if not isinstance(parsed, dict):
            continue
        for profile_id, payload in parsed.items():
            searches = (payload or {}).get('recentSearches') or []
            for position, item in enumerate(searches, 1):
                if not isinstance(item, dict):
                    continue
                data_list.append((
                    item.get('searchTerm', ''), item.get('contentId', ''), profile_id,
                    position, source_file))

    data_headers = ('Search Term', 'Content ID', 'Profile ID', 'Position In File',
                    'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_session(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'BAM_SDK_STORAGE.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        prefs = _prefs(file_found)
        values = {key: value for key, (_tag, value) in prefs.items()}
        session = {}
        grant = {}
        fallback = {}
        state_type = ''
        config_version = ''
        for key, value in values.items():
            if key.endswith('_SESSION_STATE'):
                session = _json_or_none(value) or {}
            elif key.endswith('_SESSION_STATE_TYPE'):
                state_type = value
            elif key.endswith('_DEVICE_GRANT'):
                grant = _json_or_none(value) or {}
            elif key.endswith('_OFFLINE_FALLBACK_DATA'):
                fallback = _json_or_none(value) or {}
            elif key.endswith('_CONFIGURATION_VERSION'):
                config_version = value
        if not (session or grant or fallback):
            continue
        access = session.get('accessContext') or {}
        token = access.get('accessToken') or ''
        refresh = access.get('refreshToken') or ''
        data_list.append((
            _iso(access.get('generatedOn')), _iso(access.get('expiration')),
            _iso(session.get('lastFailure')), session.get('attempts', ''),
            access.get('tokenType', ''), access.get('region', ''), state_type,
            fallback.get('profileId', ''), grant.get('grantType', ''), config_version,
            _token_form(token), _token_form(refresh), source_file))

    data_headers = (
        ('Generated On', 'datetime'), ('Expiration', 'datetime'),
        ('Last Refresh Failure', 'datetime'), 'Refresh Attempts', 'Token Type', 'Region',
        'Session State Type', 'Offline Fallback Profile ID', 'Device Grant Type',
        'Configuration Version', 'Access Token Form', 'Refresh Token Form', 'Source File')
    return data_headers, data_list, source_path


def _token_form(token):
    '''How a token is encoded, without reproducing it.

    A five part compact serialisation is JWE, whose claims are encrypted; a three part one
    is JWS, whose claims are readable. Reported so a reader knows which without the token
    being copied into the report.
    '''
    if not token:
        return ''
    parts = token.count('.') + 1
    if parts == 5:
        return 'JWE, 5 part, claims encrypted'
    if parts == 3:
        return 'JWS, 3 part'
    return f'{parts} part'


@artifact_processor
def disneyplus_app_settings(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'default.xml', 'BAMPLAYER.xml',
                             'AnalyticsSharedPrefs.xml', 'Conviva.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        name = os.path.basename(str(file_found).replace('\\', '/'))
        for key, (tag, value) in _prefs(file_found).items():
            if key.startswith('bookmarksHandshake'):
                continue
            resolved = ''
            if _TIME_KEY_RE.search(key) and re.fullmatch(r'\d{13}', str(value).strip()):
                resolved = _ms(value)
            data_list.append((resolved, name, key, tag, value, source_file))

    data_headers = (
        ('Value As Timestamp', 'datetime'), 'Preference File', 'Key', 'Type', 'Value',
        'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_home_sets(context):
    data_list = []
    source_path = ''
    pattern = re.compile(r'^type_(?P<type>.+?)_id_(?P<id>.+)$')
    for file_found in _named(context, 'contentSetAvailability.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for key, (_tag, value) in _prefs(file_found).items():
            match = pattern.match(key)
            set_type = match.group('type') if match else ''
            set_id = match.group('id') if match else key
            data_list.append((set_type, set_id, value, source_file))

    data_headers = ('Set Type', 'Set ID', 'Availability (as stored)', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_avatars(context):
    data_list = []
    source_path = ''
    sql = ('SELECT `avatarId`, `avatarTitle`, `masterId`, `masterWidth`, `imageUrl` '
           'FROM `AvatarImpl` ORDER BY `avatarTitle`')
    for file_found in _named(context, 'profiles'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for row in _rows(file_found, sql):
            avatar_id, title, master_id, master_width, image_url = row
            in_url = 'Yes' if master_id and master_id in (image_url or '') else 'No'
            data_list.append((
                title, avatar_id, master_id or '',
                '' if master_width is None else master_width, image_url or '', in_url,
                source_file))

    data_headers = ('Avatar Title', 'Avatar ID', 'Master ID', 'Master Width', 'Image URL',
                    'Master ID In Image URL', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_cached_titles(context):
    data_list = []
    source_path = ''
    for url, headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        if 'json' not in headers.get('content-type', ''):
            continue
        parsed = _json_or_none(_body_bytes(body))
        if parsed is None:
            continue
        source_path = source_path or body
        source_file = _relative(context, body)
        endpoint = '/'.join(urlparse(url).path.strip('/').split('/')[:3])
        seen = set()
        for item in _walk_titles(parsed):
            content_id = item.get('contentId')
            title = _title_text(item.get('text'))
            if not title or content_id in seen:
                continue
            seen.add(content_id)
            family = item.get('family') or {}
            availability = item.get('currentAvailability') or {}
            data_list.append((
                title, content_id, item.get('contentType') or '',
                item.get('programType') or '', item.get('encodedSeriesId') or '',
                family.get('familyId') or '',
                '' if item.get('episodeSequenceNumber') is None
                else item.get('episodeSequenceNumber'),
                availability.get('region') or '',
                '' if availability.get('kidsMode') is None
                else ('Yes' if availability.get('kidsMode') else 'No'),
                item.get('badging') or '', endpoint, source_file))

    data_headers = (
        'Title', 'Content ID', 'Content Type (as stored)', 'Program Type (as stored)',
        'Encoded Series ID', 'Family ID', 'Episode Sequence Number',
        'Availability Region', 'Kids Mode', 'Badging (as stored)', 'Endpoint',
        'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_playback_requests(context):
    data_list = []
    source_path = ''
    for url, headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        parsed = urlparse(url)
        if not _MEDIA_HOST_RE.search(parsed.netloc):
            continue
        source_path = source_path or body
        source_file = _relative(context, body)
        decoded = unquote(parsed.path)
        media = re.search(r'url=/[^/]+/[^/]+/([0-9a-fA-F-]{36})', decoded)
        if not media:
            media = re.search(r'/([0-9a-fA-F-]{36})/', decoded)
        device = re.search(r'~did=([^~/]+)', decoded)
        account = re.search(r'~aid=([^~/]+)', decoded)
        key_id = re.search(r'~kid=([^~/]+)', decoded)
        expiry = re.search(r'exp=(\d+)', decoded)
        data_list.append((
            _seconds(expiry.group(1)) if expiry else '',
            media.group(1) if media else '',
            os.path.basename(parsed.path),
            headers.get('content-type', ''),
            device.group(1) if device else '',
            account.group(1) if account else '',
            key_id.group(1) if key_id else '',
            parsed.netloc, os.path.getsize(body), source_file))

    data_headers = (
        ('Delivery Token Expiry', 'datetime'), 'Media ID', 'Requested File',
        'Content Type', 'Device ID', 'Account ID', 'Key ID', 'Host', 'Cached Body Size',
        'Source File')
    return data_headers, data_list, source_path


def _image_payload(path):
    """(bytes, stored_encoding) for a possibly gzip encoded image body.

    A cache body may be stored gzip encoded. Reading the file as it sits on disk would
    fail the magic test for every compressed entry and drop it with no error, leaving a
    short table, so the bytes are decoded first and the encoding is carried to the report.
    """
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError:
        return b'', ''
    if raw[:2] == b'\x1f\x8b':
        try:
            return gzip.decompress(raw), 'gzip'
        except (OSError, EOFError):
            return raw, ''
    return raw, ''


def _check_in_image(path, data, encoding, name, mime, extension):
    """Check in the file itself, or the decoded bytes where the file is encoded."""
    if encoding:
        return check_in_embedded_media(path, data, name=name, force_type=mime,
                                       force_extension=extension)
    return check_in_media(path, name=name, force_type=mime, force_extension=extension)


def _bif_frames(data):
    """(frame_number, jpeg_bytes, declared_end_overran) for a Base Index Frames file.

    Every declared offset is checked against the bytes actually present. Where the index
    declares an end beyond the file the frame is not discarded silently and the overrun is
    not clamped away silently either: the available bytes are taken, kept only if they
    still form a complete JPEG, and the row is flagged so the reader sees that the index
    and the cached bytes disagree. Anything that does not resolve to a complete JPEG stops
    the walk and is logged.
    """
    if not data.startswith(_BIF_MAGIC) or len(data) < 64:
        return [], 0, 0
    _version, declared, multiplier = struct.unpack_from('<III', data, 8)
    index = []
    for position in range(declared + 1):
        start = 64 + 8 * position
        if start + 8 > len(data):
            break
        index.append(struct.unpack_from('<II', data, start))
    frames = []
    for position in range(len(index) - 1):
        frame, offset = index[position]
        end = index[position + 1][1]
        if offset >= len(data) or end <= offset:
            logfunc('Disney+: trickplay index entry falls outside the cached bytes, '
                    'stopping the walk')
            break
        overran = end > len(data)
        chunk = data[offset:min(end, len(data))]
        if not (chunk.startswith(b'\xff\xd8') and chunk.endswith(b'\xff\xd9')):
            logfunc('Disney+: trickplay frame is not a complete JPEG in the cached bytes, '
                    'stopping the walk')
            break
        if overran:
            logfunc('Disney+: trickplay index declares an end past the cached bytes; '
                    'the frame is reported from the bytes present and flagged')
        frames.append((frame, chunk, overran))
    return frames, declared, multiplier


@artifact_processor
def disneyplus_trickplay(context):
    data_list = []
    source_path = ''
    for url, _headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        raw = _body_bytes(body)
        if not raw.startswith(_BIF_MAGIC):
            continue
        source_path = source_path or body
        source_file = _relative(context, body)
        decoded = unquote(urlparse(url).path)
        media = re.search(r'/([0-9a-fA-F-]{36})/', decoded)
        media_id = media.group(1) if media else ''
        frames, declared, multiplier = _bif_frames(raw)
        for frame, chunk, overran in frames:
            media_ref = check_in_embedded_media(
                body, chunk, name=f'{media_id or "trickplay"}_{frame}.jpg',
                force_type='image/jpeg', force_extension='jpg')
            data_list.append((
                media_ref, media_id, frame, multiplier, declared, len(frames),
                'Yes' if overran else 'No', len(chunk), os.path.basename(decoded),
                source_file))

    data_headers = (
        ('Frame', 'media'), 'Media ID', 'Frame Index Value', 'Declared Multiplier',
        'Declared Frame Count', 'Frames Recovered', 'Declared End Overran Cached Bytes',
        'Frame Size', 'Index File', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_cached_images(context):
    data_list = []
    source_path = ''

    # Index the decoded cache bodies by content hash so an image held in another store can
    # be given that URL. That is a content hash match and is reported as such, never as a
    # link the container itself records.
    by_hash = {}
    cached = []
    for url, _headers, body in _cache_entries(_matching(context, '/cache/http-cache/')):
        data, encoding = _image_payload(body)
        label, extension, mime = _image_kind(data)
        if not label:
            continue
        by_hash.setdefault(hashlib.sha256(data).hexdigest(), url)
        cached.append((body, url, data, encoding, label, extension, mime))

    for body, url, data, encoding, label, extension, mime in cached:
        source_path = source_path or body
        media_ref = _check_in_image(body, data, encoding,
                                    os.path.basename(urlparse(url).path) or 'image',
                                    mime, extension)
        data_list.append((
            media_ref, 'http-cache', os.path.basename(str(body).replace('\\', '/')), url,
            'URL recorded in cache entry', label, encoding or 'identity', len(data),
            _relative(context, body)))

    for store, fragment in (('offline_images', '/files/offline_images/'),
                            ('glide-cache-v2', '/cache/glide-cache-v2/')):
        for file_found in _matching(context, fragment):
            if os.path.isdir(str(file_found)):
                continue
            data, encoding = _image_payload(file_found)
            label, extension, mime = _image_kind(data)
            if not label:
                continue
            source_path = source_path or file_found
            name = os.path.basename(str(file_found).replace('\\', '/'))
            url = by_hash.get(hashlib.sha256(data).hexdigest(), '')
            basis = 'Content hash match to a cached response' if url else ''
            media_ref = _check_in_image(file_found, data, encoding, name, mime, extension)
            data_list.append((
                media_ref, store, name, url, basis, label, encoding or 'identity',
                len(data), _relative(context, file_found)))

    data_headers = (
        ('Image', 'media'), 'Store', 'File Name', 'Source URL', 'Link Basis', 'Type',
        'Stored Encoding', 'Decoded Size', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_sdk_events(context):
    data_list = []
    source_path = ''
    for file_found in _matching(context, '/files/dustv2/'):
        if os.path.isdir(str(file_found)):
            continue
        try:
            with open(file_found, 'rb') as handle:
                parsed = json.loads(handle.read())
        except (OSError, ValueError):
            logfunc(f'Disney+: could not read telemetry file '
                    f'{os.path.basename(str(file_found))}')
            continue
        if not isinstance(parsed, dict):
            continue
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        payload = parsed.get('data') or {}
        invocation = payload.get('invocation') or {}
        error = payload.get('error') or {}
        services = payload.get('services') or []
        service = services[0] if services and isinstance(services[0], dict) else {}
        request = service.get('request') or {}
        response = service.get('response') or {}
        device = payload.get('deviceInfo') or {}
        data_list.append((
            _iso(parsed.get('time')), _iso(payload.get('startTime')),
            invocation.get('urn') or '', request.get('method') or '',
            request.get('host') or '', request.get('path') or '',
            '' if response.get('statusCode') is None else response.get('statusCode'),
            error.get('code') or error.get('errorCode') or '',
            '' if payload.get('totalDuration') is None else payload.get('totalDuration'),
            '' if response.get('roundTripTime') is None
            else response.get('roundTripTime'),
            response.get('region') or '', parsed.get('subject') or '',
            device.get('platformId') or '', payload.get('sdkInstanceId') or '',
            os.path.basename(str(file_found).replace('\\', '/')), source_file))

    data_headers = (
        ('Event Time', 'datetime'), ('Invocation Start', 'datetime'),
        'Operation (as stored)', 'Method', 'Host', 'Path', 'Response Status',
        'Error Code (as stored)', 'Total Duration', 'Round Trip Time', 'Response Region',
        'Subject', 'Platform ID (as stored)', 'SDK Instance ID', 'File Name',
        'Source File')
    return data_headers, data_list, source_path
