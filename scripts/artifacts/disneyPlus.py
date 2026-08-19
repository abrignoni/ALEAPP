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
                 "content id, and is left empty otherwise; on the one tested sample that "
                 "resolved one row of fifteen, so an empty title means the cache did not "
                 "carry that content id rather than that the title is unknown to the service. "
                 "The database carries no write-ahead log and its rollback journal is zero "
                 "length, so the committed state is the only state. Field mapping was done "
                 "against one private sample from a single device; no sample data is recorded "
                 "for it.",
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
                 "than a correlation, and the two keys held identical values because the last "
                 "item played overall was the one from that series. contentIdentifierType is "
                 "reported as stored. Field mapping was done against one private sample from "
                 "a single device; no sample data is recorded for it.",
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
                 "here, so only their form is reported. The app's own preference files were "
                 "searched for key material that would open them and none was found. The "
                 "offline fallback value names a profile id, which on the one tested sample "
                 "was the same profile id the resume points table and the recent search store "
                 "carry. The device grant records only its grant type. Field mapping was done "
                 "against one private sample from a single device; no sample data is recorded "
                 "for it.",
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
                 "default file, BAMPLAYER, AnalyticsSharedPrefs and Conviva. These carry the "
                 "playback preferences, the install referrer, the first run flag and the time "
                 "the app was last backgrounded. Values are reported as stored. A value is "
                 "additionally rendered as a UTC timestamp only where the key names a time "
                 "and the value is a thirteen digit integer; on the one tested sample the app "
                 "backgrounded key resolved to within a second of the most recent resume "
                 "point write, which is what supports reading it as milliseconds. The "
                 "bookmarksHandshake keys of the same file are reported by the Last Played "
                 "Item artifact instead of here. Third party software development kit "
                 "preference files that sit in the same directory are not read by this "
                 "artifact. Field mapping was done against one private sample from a single "
                 "device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/shared_prefs/default.xml',
                  '*/com.disney.disneyplus/shared_prefs/BAMPLAYER.xml',
                  '*/com.disney.disneyplus/shared_prefs/AnalyticsSharedPrefs.xml',
                  '*/com.disney.disneyplus/shared_prefs/Conviva.xml'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "disneyplus_playback_requests": {
        "name": "Disney+ - Playback Requests",
        "description": "Summarises the cached streaming requests of the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "One row per media identifier, summarising the request URLs recorded in the "
                 "app's sdk-cache entries for the media delivery hosts. The individual "
                 "manifest fetches are counted rather than listed, because they repeat for a "
                 "single playback and an examiner cannot act on each one; the URL path of "
                 "every one of them carries the same media, device and account identifiers, "
                 "which are reported here, and the cache directory still holds each entry. "
                 "The expiry values are Unix seconds naming when a delivery token ceases to "
                 "be valid, so the earliest and latest are reported as a bound on when the "
                 "requests were made rather than as event times. A cached request records "
                 "that the app asked for the manifest, not how much of the media was played. "
                 "Field mapping was done against one private sample from a single device; no "
                 "sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/cache/sdk-cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud-download"
    },
    "disneyplus_trickplay": {
        "name": "Disney+ - Trickplay Preview",
        "description": "Checks in a preview frame from each trickplay index cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "One row per cached trickplay index, which is the only stored content that "
                 "shows what a cached title looks like. The sdk-cache entries whose content "
                 "type is application/bif hold a Base Index Frames file: an eight byte "
                 "signature, a declared image count, a declared timestamp multiplier and an "
                 "index of frame number and byte offset pairs, each pointing at a JPEG, "
                 "closed by a terminator entry giving the end of the last one. Every declared "
                 "offset is checked against the bytes actually present and a frame is counted "
                 "only where those bytes start with a start of image marker and end with an "
                 "end of image marker, so a truncated entry yields the frames it really holds "
                 "rather than the count its header declares. On the one tested sample both "
                 "files declared 185 images and the terminator declared an end one byte past "
                 "the cached body; the last frame was complete within the bytes present, so "
                 "it is counted and the disagreement is reported in its own column rather "
                 "than the frame being dropped. A single frame from about a quarter of the "
                 "way through each index is checked in and rendered, because the opening "
                 "frames of a title are commonly blank; every frame remains in the cached "
                 "file for an examiner who needs them. The app fetches the whole index for a "
                 "title, so the presence of a frame does not establish that the offset it "
                 "sits at was played. Field mapping was done against one private sample from "
                 "a single device; no sample data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/cache/sdk-cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo-video"
    },
    "disneyplus_cached_content": {
        "name": "Disney+ - Cached Content Responses",
        "description": "Summarises the content service responses cached by the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "One row per cached content service response, giving the endpoint, the "
                 "availability region the response was served for and the number of titles it "
                 "carries. The titles themselves are deliberately not enumerated: these "
                 "responses are the catalogue the service composed for the profile, covering "
                 "curated, trending, recommendation, because you watched and up next sets, so "
                 "listing them beside an account reads as things the user chose when the "
                 "container does not establish that. The title text is still used internally "
                 "to name a content id in the Playback Resume Points artifact, which does "
                 "record user activity. The response bodies remain in the sdk-cache directory "
                 "named in the Source File column and carry the full title list for an "
                 "examiner who needs it. Bodies are gzip encoded and are decompressed before "
                 "reading. Two further stores in the same container are server supplied and "
                 "are summarised here rather than given artifacts of their own: "
                 "contentSetAvailability records the home page rails and their availability "
                 "with no time and no user action attached, and the AvatarImpl table of the "
                 "profiles database is a catalogue of selectable avatars that holds no "
                 "profile record and does not record which avatar a profile chose. Field "
                 "mapping was done against one private sample from a single device; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.disney.disneyplus/cache/sdk-cache/*',
                  '*/com.disney.disneyplus/shared_prefs/contentSetAvailability.xml',
                  '*/com.disney.disneyplus/databases/profiles*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "movie"
    },
    "disneyplus_cached_images": {
        "name": "Disney+ - Cached Image Stores",
        "description": "Summarises the image caches of the Disney+ Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Disney+",
        "notes": "One row per image store rather than one per file. The images are service "
                 "supplied artwork for catalogue titles and avatars; the app stores no user "
                 "created images, so enumerating each file would fill the report with rows an "
                 "examiner cannot act on. Each row gives the file count, how many are "
                 "distinct by content hash, how many can be tied to a source URL and on what "
                 "basis, and the directory holding them. An http-cache entry records its own "
                 "request URL. A file under files/offline_images is named with a numeric "
                 "identifier that appears nowhere else in the container, and a glide-cache-v2 "
                 "file name is not derived from the URL either: both were tested against the "
                 "MD5, SHA-1 and SHA-256 of the URLs of images holding identical bytes and "
                 "matched none, so a URL is attributed to those stores only where the bytes "
                 "are identical to a cached response body, which is a content hash match. A "
                 "cached body may be stored gzip encoded, so images are counted from the "
                 "decoded bytes; reading the files as they sit on disk misses every "
                 "compressed one. File type comes from the leading bytes rather than the file "
                 "name. Field mapping was done against one private sample from a single "
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
                 "carrying their own offset and are reported with that offset preserved, so "
                 "the queue places the app in time. The event records the service operation "
                 "invoked, the host, path and method requested, the response status where one "
                 "was received, the serving region and the session id the event was raised "
                 "under. Transport detail that identifies nothing, such as the edge node and "
                 "request identifiers, is not reported. Error codes are reported as stored; "
                 "the values observed on the tested sample were network-error and "
                 "authenticationExpired, read from the files rather than from any external "
                 "list. These events record calls the app's SDK made, so they evidence the "
                 "app running rather than anything the user chose. Field mapping was done "
                 "against one private sample from a single device; no sample data is recorded "
                 "for it.",
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

# The delivery URL carries the media identifier in two places that agree: the scope of the
# signed token (~url=/ps01/disney[/thumbnails]/<id>/) and the asset path that follows it.
# An unsigned request carries no token and names the media directly under /int/ps01/disney/.
# Matched by position rather than by taking the first identifier in the string, because the
# same URL also carries per rendition asset identifiers that are not the media.
_MEDIA_ID_RES = (
    re.compile(r'~url=/ps01/disney/(?:thumbnails/)?([0-9a-fA-F-]{36})/'),
    re.compile(r'/int/ps01/disney/([0-9a-fA-F-]{36})/'),
    re.compile(r'/ps01/disney/(?:thumbnails/)?([0-9a-fA-F-]{36})/'),
)


def _media_id(decoded_path):
    '''The media identifier a delivery URL names, or '' when none of the forms match.'''
    for pattern in _MEDIA_ID_RES:
        found = pattern.search(decoded_path)
        if found:
            return found.group(1)
    return ''

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
def disneyplus_playback_requests(context):
    data_list = []
    source_path = ''
    per_media = {}
    for url, headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        parsed = urlparse(url)
        if not _MEDIA_HOST_RE.search(parsed.netloc):
            continue
        source_path = source_path or body
        decoded = unquote(parsed.path)
        media_id = _media_id(decoded)
        record = per_media.setdefault(media_id, {
            'expiries': [], 'manifests': 0, 'indexes': 0, 'other': 0, 'hosts': set(),
            'device': '', 'account': '', 'key': '', 'forms': set(),
            'source': _relative(context, body)})
        record['forms'].add('Signed delivery token' if '~url=' in decoded
                            else 'Unsigned path')
        expiry = re.search(r'exp=(\d+)', decoded)
        if expiry:
            record['expiries'].append(int(expiry.group(1)))
        for field, group in (('device', 'did'), ('account', 'aid'), ('key', 'kid')):
            found = re.search(rf'~{group}=([^~/]+)', decoded)
            if found and not record[field]:
                record[field] = found.group(1)
        record['hosts'].add(parsed.netloc)
        name = os.path.basename(parsed.path).lower()
        content_type = headers.get('content-type', '').lower()
        if name.endswith('.m3u8') or 'mpegurl' in content_type:
            record['manifests'] += 1
        elif name.endswith('.bif') or 'bif' in content_type:
            record['indexes'] += 1
        else:
            record['other'] += 1

    for media_id, record in per_media.items():
        expiries = sorted(record['expiries'])
        data_list.append((
            _seconds(expiries[0]) if expiries else '',
            _seconds(expiries[-1]) if expiries else '',
            media_id, record['manifests'], record['indexes'], record['other'],
            record['device'], record['account'], record['key'],
            ', '.join(sorted(record['forms'])), ', '.join(sorted(record['hosts'])),
            record['source']))

    data_headers = (
        ('Earliest Token Expiry', 'datetime'), ('Latest Token Expiry', 'datetime'),
        'Media ID', 'Manifest Requests', 'Trickplay Index Requests', 'Other Requests',
        'Device ID', 'Account ID', 'Key ID', 'Request Form', 'Delivery Hosts',
        'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_trickplay(context):
    data_list = []
    source_path = ''
    for url, _headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        raw = _body_bytes(body)
        if not raw.startswith(_BIF_MAGIC):
            continue
        source_path = source_path or body
        decoded = unquote(urlparse(url).path)
        media_id = _media_id(decoded)
        frames, declared, multiplier = _bif_frames(raw)
        if not frames:
            continue
        overran = sum(1 for _frame, _chunk, flag in frames if flag)
        # The opening frames of a title are commonly blank, so the frame rendered is taken
        # from about a quarter of the way in rather than from the start.
        pick = frames[len(frames) // 4]
        media_ref = check_in_embedded_media(
            body, pick[1], name=f'{media_id or "trickplay"}_{pick[0]}.jpg',
            force_type='image/jpeg', force_extension='jpg')
        spacing = frames[1][0] - frames[0][0] if len(frames) > 1 else ''
        data_list.append((
            media_ref, media_id, declared, len(frames), pick[0], spacing,
            frames[-1][0], multiplier, 'Yes' if overran else 'No',
            os.path.basename(decoded), _relative(context, body)))

    data_headers = (
        ('Preview Frame', 'media'), 'Media ID', 'Declared Frame Count', 'Frames Recovered',
        'Rendered Frame Index', 'Frame Index Spacing', 'Last Frame Index',
        'Declared Multiplier', 'Declared End Overran Cached Bytes', 'Index File',
        'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_cached_content(context):
    data_list = []
    source_path = ''
    for url, headers, body in _cache_entries(_matching(context, '/cache/sdk-cache/')):
        if 'json' not in headers.get('content-type', ''):
            continue
        parsed = _json_or_none(_body_bytes(body))
        if parsed is None:
            continue
        source_path = source_path or body
        segments = urlparse(url).path.strip('/').split('/')
        titles = set()
        regions = set()
        for item in _walk_titles(parsed):
            if _title_text(item.get('text')):
                titles.add(item.get('contentId'))
            availability = item.get('currentAvailability') or {}
            if availability.get('region'):
                regions.add(availability['region'])
        if not titles:
            continue
        data_list.append((
            '/'.join(segments[:3]), segments[2] if len(segments) > 2 else '',
            len(titles), ', '.join(sorted(regions)), urlparse(url).netloc,
            os.path.getsize(body), _relative(context, body)))

    # Two further server supplied stores are summarised rather than enumerated. Neither
    # records a time or a user action, so a row each stating what they hold is enough.
    for file_found in _named(context, 'contentSetAvailability.xml'):
        prefs = _prefs(file_found)
        if not prefs:
            continue
        source_path = source_path or file_found
        data_list.append((
            'contentSetAvailability', 'home page sets', len(prefs), '', '',
            os.path.getsize(file_found), _relative(context, file_found)))

    for file_found in _named(context, 'profiles'):
        rows = _rows(file_found, 'SELECT count(*) FROM `AvatarImpl`')
        if not rows:
            continue
        source_path = source_path or file_found
        data_list.append((
            'profiles/AvatarImpl', 'avatar catalogue', rows[0][0], '', '',
            os.path.getsize(file_found), _relative(context, file_found)))

    data_headers = (
        'Store Or Endpoint', 'Kind', 'Items Held', 'Availability Regions', 'Host',
        'Stored Size', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def disneyplus_cached_images(context):
    data_list = []
    source_path = ''

    # Index the decoded cache bodies by content hash so an image held in another store can
    # be given that URL. That is a content hash match and is reported as such, never as a
    # link the container itself records.
    by_hash = {}
    stores = {}

    def record(store, path, data, url, basis):
        entry = stores.setdefault(store, {
            'files': 0, 'hashes': set(), 'linked': 0, 'basis': set(), 'bytes': 0,
            'kinds': set(), 'gzip': 0, 'dir': ''})
        entry['files'] += 1
        entry['hashes'].add(hashlib.sha256(data).hexdigest())
        entry['bytes'] += len(data)
        if url:
            entry['linked'] += 1
            entry['basis'].add(basis)
        if not entry['dir']:
            entry['dir'] = os.path.dirname(_relative(context, path))

    for url, _headers, body in _cache_entries(_matching(context, '/cache/http-cache/')):
        data, encoding = _image_payload(body)
        label, _extension, _mime = _image_kind(data)
        if not label:
            continue
        source_path = source_path or body
        by_hash.setdefault(hashlib.sha256(data).hexdigest(), url)
        record('http-cache', body, data, url, 'URL recorded in cache entry')
        stores['http-cache']['kinds'].add(label)
        if encoding:
            stores['http-cache']['gzip'] += 1

    for store, fragment in (('offline_images', '/files/offline_images/'),
                            ('glide-cache-v2', '/cache/glide-cache-v2/')):
        for file_found in _matching(context, fragment):
            if os.path.isdir(str(file_found)):
                continue
            data, encoding = _image_payload(file_found)
            label, _extension, _mime = _image_kind(data)
            if not label:
                continue
            source_path = source_path or file_found
            url = by_hash.get(hashlib.sha256(data).hexdigest(), '')
            record(store, file_found, data, url,
                   'Content hash match to a cached response')
            stores[store]['kinds'].add(label)
            if encoding:
                stores[store]['gzip'] += 1

    for store, entry in stores.items():
        data_list.append((
            store, entry['files'], len(entry['hashes']), entry['linked'],
            ', '.join(sorted(entry['basis'])) or 'No link established',
            ', '.join(sorted(entry['kinds'])), entry['gzip'], entry['bytes'],
            entry['dir']))

    data_headers = (
        'Store', 'Image Files', 'Distinct By Content Hash', 'With A Source URL',
        'Link Basis', 'Types', 'Stored Gzip Encoded', 'Decoded Bytes', 'Directory')
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
