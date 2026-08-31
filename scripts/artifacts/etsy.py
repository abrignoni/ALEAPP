__artifacts_v2__ = {
    "etsy_account": {
        "name": "Etsy - Account and Device",
        "description": "Parses the signed in account and the app and device identifiers "
                       "stored by the Etsy Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "One row per app data directory. The account fields come from the app's "
                 "own EtsyUserPrefs preferences file. The install identifier is written by three "
                 "different code paths, the app's EtsyInstallPrefs file, the crash "
                 "reporter's cached user record and the device_id field of the app's own "
                 "log envelope, and the account id by two, the app's preferences file and "
                 "the same crash reporter record. Each is read from the app's own store "
                 "and falls back to the others only when that store is absent, so the "
                 "column names one value rather than comparing them; on the tested device "
                 "all three copies of the install identifier and both copies of the "
                 "account id held the same value. First and last app start are Unix "
                 "milliseconds. SecureEtsyUserPrefs holds "
                 "further preferences under AndroidX EncryptedSharedPreferences; the "
                 "count of entries is reported but their names and values are not "
                 "recoverable from a file system extraction, because both Tink keysets in "
                 "that file are EncryptedKeyset structures whose key material is wrapped "
                 "by an Android Keystore key that the extraction does not contain. Only "
                 "the algorithm names are readable, AES-SIV for the entry names and "
                 "AES-GCM for the values. Field mapping was done against a private sample "
                 "provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.etsy.android/shared_prefs/EtsyUserPrefs.xml',
            '*/com.etsy.android/shared_prefs/EtsyInstallPrefs.xml',
            '*/com.etsy.android/shared_prefs/SecureEtsyUserPrefs.xml',
            '*/com.etsy.android/shared_prefs/com.etsy.android_preferences.xml',
            '*/com.etsy.android/shared_prefs/server_config.xml',
            '*/com.etsy.android/files/INSTALLATION',
            '*/com.etsy.android/files/device-id',
            '*/com.etsy.android/files/internal-device-id',
            '*/com.etsy.android/cache/sentry/*/.scope-cache/user.json',
            '*/com.etsy.android/cache/sentry/*/.scope-cache/extras.json',
            '*/com.etsy.android/cache/sentry/*/.options-cache/release.json',
            '*/com.etsy.android/databases/etsy-logs*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "etsy_recently_viewed": {
        "name": "Etsy - Recently Viewed Listings",
        "description": "Parses listings the Etsy Android app recorded as recently viewed, "
                       "including views recovered from the write-ahead log.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "One row per recorded view. The table keeps one row per listing, so a "
                 "listing viewed more than once owns one row per view time recovered. "
                 "timestamp is Unix milliseconds. The store is read three ways and each "
                 "row carries the view it came from. Live is the committed state with the "
                 "write-ahead log applied, Pre-checkpoint is the main file read with "
                 "immutable=1 so the log is ignored, and Recovered is a row read out of an "
                 "individual write-ahead log frame that neither of the other two returns. "
                 "Every declared length is checked against the bytes present and a "
                 "candidate is kept only when it carries nine values, an image URL on the "
                 "app's own image host and a timestamp inside the range the column uses, "
                 "so a page image belonging to another table is rejected rather than "
                 "reported. Why a row is not in the committed state is not established "
                 "here: app eviction, a re-sync and a user action all produce the same "
                 "result. Cached images are matched by hashing the stored image URL and a "
                 "list of Etsy size variants with SHA-256 and looking the digest up as a "
                 "cache entry name, which is how the app's image cache names its entries. "
                 "Matching is done inside one app data directory so a second directory "
                 "cannot supply another's image. On the tested device the variants that "
                 "matched were il_794xN, il_680x540, il_570xN and il_fullxfull. The "
                 "largest matched file is the one rendered. The visible column was 1 on "
                 "every row on the tested device and is reported as stored rather than "
                 "dropped, because a differing value would be a property of the row worth "
                 "seeing. Field mapping was done against a private sample provided by "
                 "Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.etsy.android/databases/recentlyViewedListings*',
            '*/com.etsy.android/cache/image_manager_disk_cache/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "eye"
    },
    "etsy_listing_interactions": {
        "name": "Etsy - Listing Interactions",
        "description": "Parses listing impressions and taps recorded by the Etsy Android "
                       "app, including rows recovered from the write-ahead log.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "timestamp is Unix milliseconds. Interaction type, listing source and "
                 "display location are reported as stored; the extraction carries no app "
                 "binary, so no mapping for them was available to source. The store is "
                 "read three ways and each row carries the view it came from, as described "
                 "on Etsy - Recently Viewed Listings. The encoded_data column, where "
                 "populated, begins with a number and a ten digit value before a base64 "
                 "section; both are reported as stored. On the tested device that leading "
                 "number matched a listing id in the recently viewed store on 4 of the 22 "
                 "rows that carry it, and in each of those four the interaction preceded "
                 "the recorded view by between 6 and 89 seconds. That is an observation "
                 "about one device, not a definition of the field. The ten digit value ran "
                 "between 97 and 129 seconds earlier than the row's own timestamp on every "
                 "row that carried it. The base64 section is not reproduced; it is in the "
                 "encoded_data column of the source table. Field mapping was done against "
                 "a private sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/com.etsy.android/databases/ListingInteractions*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shopping-bag"
    },
    "etsy_ad_impressions": {
        "name": "Etsy - Ad Impressions and Clicks",
        "description": "Parses advertising impressions and clicks recorded by the Etsy "
                       "Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "These rows record advertising the app displayed to the user and, for a "
                 "click row, that the advertisement was tapped. An impression records "
                 "delivery by the app rather than an action by the user. timestamp is Unix "
                 "milliseconds. Impression and click rows share a column count, so they "
                 "are told apart by the shape their schemas require: the click table's "
                 "first column is its integer primary key and is therefore absent from the "
                 "stored record, while the impression table's first column is its text "
                 "display location. On the tested device both tables were empty in the "
                 "committed state, in the pre-checkpoint read and in every write-ahead log "
                 "frame, and the main file held no schema at all, so this reader is "
                 "code-present and was not exercised against any row. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.etsy.android/databases/AdImpressions*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag"
    },
    "etsy_app_logs": {
        "name": "Etsy - Application Logs",
        "description": "Parses the app's own queued log records, including records "
                       "recovered from the write-ahead log.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "Each row holds one JSON record the app queued for upload. "
                 "log_created_time is Unix seconds with a fractional part. The app version "
                 "is carried on every record, so the rows place a sequence of app versions "
                 "on the device over the period they span. The store is read three ways "
                 "and each row carries the view it came from, as described on Etsy - "
                 "Recently Viewed Listings. A candidate read from a log frame is kept only "
                 "when its second value parses as JSON and carries the envelope keys the "
                 "app writes, which is what separates it from the other two tables in the "
                 "same file that also hold two columns. Log namespace and data type are "
                 "reported as stored. The separate analytics_logs.db in the same directory "
                 "held no rows, no write-ahead log and no recoverable record text on the "
                 "tested device, while its sequence counter recorded 1971 rows written "
                 "over the life of the store, so that content is gone rather than missed. "
                 "Field mapping was done against a private sample provided by Mattia; no "
                 "sample data is recorded for it.",
        "paths": ('*/com.etsy.android/databases/etsy-logs*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file-text"
    },
    "etsy_network_breadcrumbs": {
        "name": "Etsy - Network Breadcrumbs",
        "description": "Parses the cached request breadcrumbs the Etsy Android app's crash "
                       "reporter kept for its most recent session.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "The breadcrumb cache is written by the Sentry SDK the app embeds and is "
                 "scoped here to the app's own data directory. It holds the requests of "
                 "the session in progress when the file was last written, so it is a short "
                 "record of the most recent session rather than a history. The file is a "
                 "fixed size buffer, so JSON objects are located within it rather than the "
                 "file being parsed as a whole document. Start and end times are Unix "
                 "milliseconds and the duration is their difference. Each breadcrumb also "
                 "carries the full URL and, on some rows, the request's query string; "
                 "neither is reproduced here because the host and path columns already "
                 "carry the request and the query string held feature flags rather than "
                 "anything the user supplied. Both remain in the source file. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.etsy.android/cache/sentry/*/.scope-cache/breadcrumbs.json',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    "etsy_image_caches": {
        "name": "Etsy - Image Cache Summary",
        "description": "Summarises the image caches the Etsy Android app keeps on disk.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Etsy",
        "notes": "One row per cache directory per app data directory. The caches are "
                 "summarised rather than listed: an entry name is a digest, so an entry "
                 "that cannot be matched back to a URL carries nothing an examiner can act "
                 "on by itself. The entries that do match a recently viewed listing are "
                 "reported and rendered on Etsy - Recently Viewed Listings instead. Type "
                 "counts are taken from each file's leading bytes after any transfer "
                 "encoding is decoded; on the tested device no entry was stored compressed. "
                 "The image_manager_disk_cache directory is written by the Glide image "
                 "library and the appboy directory by the Braze SDK, both embedded in the "
                 "app, and both are scoped here to the app's own data directory. The files "
                 "themselves remain in the extraction at the reported path. Field mapping "
                 "was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/com.etsy.android/cache/image_manager_disk_cache/*',
            '*/com.etsy.android/cache/appboy.imageloader.lru.cache/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image"
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

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.etsy.android'

# Leading bytes to (label, mime, extension). Cache entries carry no extension, so the
# type comes from the bytes rather than from the name.
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF87a', 'GIF', 'image/gif', 'gif'),
    (b'GIF89a', 'GIF', 'image/gif', 'gif'),
)
_RENDERABLE = {'JPEG', 'PNG', 'GIF'}

# Size variants of one Etsy image URL. The app requests a rendition rather than the URL
# the listing row stores, so the stored URL alone finds a cache entry only when those
# happen to agree. A variant that the app never requested simply does not match.
_RENDITIONS = (
    'fullxfull', '1588xN', '1140xN', '1080xN', '794xN', '794x1044', '680x540', '680xN',
    '640xN', '570xN', '500xN', '340x270', '340xN', '300x300', '300xN', '224xN',
    '180x135', '170x135', '150x150', '100x100', '75x75', '75xN',
)
_RENDITION_RE = re.compile(r'(.*/il_)([^./]+)(\..*)$')


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate. Any
    index this module builds is keyed on it, because an index keyed on a bare entry name
    or file name would merge two app data directories into one.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context, predicate):
    '''{container key: [path]} for the matched files predicate accepts.

    Every caller iterates the list rather than taking the first entry that parses, so a
    second app data directory contributes its own rows instead of being dropped.
    '''
    grouped = {}
    for file_found in unique_files(context):
        if predicate(file_found):
            grouped.setdefault(_container(context, file_found), []).append(file_found)
    return grouped


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _seconds(value):
    '''A Unix second value, fractional part included, as a UTC datetime, or ''.'''
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


# --------------------------------------------------------------------------------------
# Reading a store three ways
#
# The app's Room stores keep a write-ahead log that is large relative to the main file. A
# normal read applies it and returns the committed state, which on the tested device was
# empty for three of the four stores. Two further reads recover content the committed
# state no longer holds: the main file on its own, and the individual page images the log
# still carries. Nothing below reports why a row is absent from the committed state.
# --------------------------------------------------------------------------------------

def _rows(source_path, sql):
    '''Rows for sql with the write-ahead log applied. Empty on any SQLite error.'''
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        rows = []
    db.close()
    return rows


def _rows_pre_wal(source_path, sql):
    '''Rows for sql as of the file's last checkpoint, ignoring the write-ahead log.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    db.text_factory = lambda raw: raw.decode('utf-8', 'replace')
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _varint(buf, offset, end):
    '''A SQLite variable length integer, or (None, offset) if it runs past end.'''
    value = 0
    for index in range(9):
        if offset + index >= end:
            return None, offset
        byte = buf[offset + index]
        if index == 8:
            return (value << 8) | byte, offset + 9
        value = (value << 7) | (byte & 0x7f)
        if not byte & 0x80:
            return value, offset + index + 1
    return None, offset


def _serial_size(code):
    '''The byte length a serial type code occupies, or None if the code is undefined.'''
    if code == 0 or code == 8 or code == 9:
        return 0
    if code <= 4:
        return code
    if code == 5:
        return 6
    if code == 6 or code == 7:
        return 8
    if code >= 12:
        return (code - 12) // 2 if code % 2 == 0 else (code - 13) // 2
    return None


def _record(payload):
    '''The values of one record body, or None if it does not fit its own header.

    Every declared length is checked against the bytes actually present. A record whose
    header claims more than the payload holds is rejected rather than clamped, so a page
    image that is not a record of this shape cannot be reported as one.
    '''
    end = len(payload)
    header_size, offset = _varint(payload, 0, end)
    if header_size is None or header_size < 1 or header_size > end:
        return None
    codes = []
    position = offset
    while position < header_size:
        code, position = _varint(payload, position, header_size)
        if code is None:
            return None
        codes.append(code)
    if position != header_size:
        return None
    values = []
    position = header_size
    for code in codes:
        size = _serial_size(code)
        if size is None or position + size > end:
            return None
        raw = payload[position:position + size]
        position += size
        if code == 0:
            values.append(None)
        elif code <= 6:
            values.append(int.from_bytes(raw, 'big', signed=True))
        elif code == 7:
            values.append(struct.unpack('>d', raw)[0])
        elif code == 8:
            values.append(0)
        elif code == 9:
            values.append(1)
        elif code % 2 == 0:
            values.append(raw)
        else:
            values.append(raw.decode('utf-8', 'replace'))
    return values


def _leaf_cells(page, usable):
    '''(rowid, payload) for each cell of a table b-tree leaf page, bounded by the page.

    A cell whose payload spills onto overflow pages is skipped rather than reported from
    its local part alone, because the tail is not reachable from a single page image.
    '''
    if not page or page[0] != 0x0d:
        return
    length = len(page)
    cell_count = int.from_bytes(page[3:5], 'big')
    if 8 + 2 * cell_count > length:
        return
    max_local = usable - 35
    for index in range(cell_count):
        pointer = 8 + 2 * index
        offset = int.from_bytes(page[pointer:pointer + 2], 'big')
        if offset < 8 or offset >= length:
            continue
        payload_size, position = _varint(page, offset, length)
        if payload_size is None or payload_size < 1 or payload_size > max_local:
            continue
        rowid, position = _varint(page, position, length)
        if rowid is None or position + payload_size > length:
            continue
        yield rowid, page[position:position + payload_size]


def _page_images(source_path):
    '''Every page image the file and its write-ahead log hold, newest frame last.

    The main file's pages come first, then one entry per log frame. A frame is a full page
    image, and a page rewritten many times leaves one frame per version, so the log holds
    states the committed database no longer has.
    '''
    try:
        with open(source_path, 'rb') as handle:
            main = handle.read()
    except OSError as ex:
        logfunc(f'Could not read {os.path.basename(source_path)}: {ex}')
        return
    if len(main) < 100 or main[:15] != b'SQLite format 3':
        return
    page_size = int.from_bytes(main[16:18], 'big')
    page_size = 65536 if page_size == 1 else page_size
    if page_size < 512 or page_size & (page_size - 1):
        return
    usable = page_size - main[20]
    for index in range(len(main) // page_size):
        yield main[index * page_size:(index + 1) * page_size], usable

    log_path = f'{source_path}-wal'
    try:
        with open(log_path, 'rb') as handle:
            log = handle.read()
    except OSError:
        return
    if len(log) < 32 or log[:4] not in (b'\x37\x7f\x06\x82', b'\x37\x7f\x06\x83'):
        return
    log_page_size = int.from_bytes(log[8:12], 'big')
    if log_page_size < 512 or log_page_size & (log_page_size - 1):
        return
    offset = 32
    while offset + 24 + log_page_size <= len(log):
        yield log[offset + 24:offset + 24 + log_page_size], log_page_size - main[20]
        offset += 24 + log_page_size


def _recovered(source_path, accept):
    '''{key: values} for the records accept() recognises across every page image.

    accept(rowid, values) returns a key for a record it recognises and None for anything
    else. It is what keeps a page belonging to another table in the same file, or a page
    holding bytes that merely parse, out of the result.
    '''
    found = {}
    for page, usable in _page_images(source_path):
        for rowid, payload in _leaf_cells(page, usable):
            values = _record(payload)
            if values is None:
                continue
            key = accept(rowid, values)
            if key is not None and key not in found:
                found[key] = values
    return found


def _merge(live, pre_checkpoint, recovered):
    '''(key, values, source view) for the union of the three reads, live winning.'''
    merged = []
    for key, values in live.items():
        merged.append((key, values, 'Live'))
    for key, values in pre_checkpoint.items():
        if key not in live:
            merged.append((key, values, 'Pre-checkpoint'))
    for key, values in recovered.items():
        if key not in live and key not in pre_checkpoint:
            merged.append((key, values, 'Recovered'))
    return merged


# --------------------------------------------------------------------------------------
# Preferences and small JSON stores
# --------------------------------------------------------------------------------------

def _prefs(source_path):
    '''{name: text} for an Android shared preferences file.'''
    values = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _json_file(source_path):
    '''A JSON document, or None when it will not parse.'''
    try:
        with open(source_path, 'r', encoding='utf-8', errors='replace') as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _named(paths, name):
    '''The matched paths whose base name is name.'''
    return [path for path in paths if os.path.basename(path) == name]


def _first(paths, name):
    '''The first matched path called name, or ''. Used only for files an app data
    directory holds exactly one of.'''
    matches = _named(paths, name)
    return matches[0] if matches else ''


# --------------------------------------------------------------------------------------
# Image cache
# --------------------------------------------------------------------------------------

def _sniff_image(head):
    '''(label, mime, extension) from a file's leading bytes.'''
    for magic, label, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return label, mime, extension
    return 'Unrecognised', '', ''


def _read_head(source_path, count=16):
    '''The leading bytes of a file, decompressed first when it is stored gzipped.

    A cache body can be stored under a transfer encoding, in which case the bytes on disk
    are not the bytes of the image and a magic byte test applied to them reports the wrong
    type or none at all. Nothing in the tested device's caches was stored compressed, so
    this path was exercised on a constructed copy rather than on a sample.
    '''
    try:
        with open(source_path, 'rb') as handle:
            head = handle.read(count)
            if head[:2] != b'\x1f\x8b':
                return head
            handle.seek(0)
            with gzip.GzipFile(fileobj=handle) as decoded:
                return decoded.read(count)
    except (OSError, EOFError, ValueError):
        return b''


def _cache_index(context, directory):
    '''{(container, entry name): path} for one cache directory.

    Keyed on the container as well as the entry name. An index keyed on the entry name
    alone would let two app data directories holding an entry of the same name overwrite
    each other, dropping one and joining rows to the other's bytes.
    '''
    index = {}
    marker = f'/{directory}/'
    for file_found in unique_files(context):
        normalised = str(file_found).replace('\\', '/')
        if marker not in normalised:
            continue
        name = os.path.basename(normalised)
        if name == 'journal':
            continue
        index[(_container(context, file_found), name)] = file_found
    return index


def _cached_renditions(index, container, image_url):
    '''The cache entries holding any size variant of image_url, largest file first.

    The cache names an entry with the SHA-256 of the URL that was requested. The listing
    row stores one rendition of the image and the app may have requested others, so each
    variant is hashed and looked up. A variant that was never requested does not match.
    '''
    if not image_url or not isinstance(image_url, str):
        return []
    candidates = [image_url]
    match = _RENDITION_RE.match(image_url)
    if match:
        candidates += [f'{match.group(1)}{token}{match.group(3)}' for token in _RENDITIONS]
    found = []
    for candidate in dict.fromkeys(candidates):
        digest = hashlib.sha256(candidate.encode('utf-8')).hexdigest()
        path = index.get((container, f'{digest}.0'))
        if path and path not in found:
            found.append(path)
    try:
        found.sort(key=os.path.getsize, reverse=True)
    except OSError:
        pass
    return found


# --------------------------------------------------------------------------------------
# Artifacts
# --------------------------------------------------------------------------------------

@artifact_processor
def etsy_account(context):
    data_list = []
    source_files = []
    grouped = _by_container(
        context,
        lambda path: os.path.basename(path) in {
            'EtsyUserPrefs.xml', 'EtsyInstallPrefs.xml', 'SecureEtsyUserPrefs.xml',
            'com.etsy.android_preferences.xml', 'server_config.xml', 'INSTALLATION',
            'device-id', 'internal-device-id', 'user.json', 'extras.json', 'release.json',
            'etsy-logs'})

    for paths in grouped.values():
        user = _prefs(_first(paths, 'EtsyUserPrefs.xml'))
        install = _prefs(_first(paths, 'EtsyInstallPrefs.xml'))
        general = _prefs(_first(paths, 'com.etsy.android_preferences.xml'))
        config = _prefs(_first(paths, 'server_config.xml'))

        secure_path = _first(paths, 'SecureEtsyUserPrefs.xml')
        secure = _prefs(secure_path) if secure_path else {}
        encrypted_entries = len([name for name in secure
                                 if not name.startswith('__androidx_security_crypto')])

        sentry_user = _json_file(_first(paths, 'user.json')) or {}
        sentry_extras = _json_file(_first(paths, 'extras.json')) or {}
        release = _json_file(_first(paths, 'release.json'))
        installation = ''
        installation_path = _first(paths, 'INSTALLATION')
        if installation_path:
            try:
                with open(installation_path, 'r', encoding='utf-8', errors='replace') as handle:
                    installation = handle.read().strip()
            except OSError:
                installation = ''
        device_id = (_json_file(_first(paths, 'device-id')) or {}).get('id', '')
        internal_id = (_json_file(_first(paths, 'internal-device-id')) or {}).get('id', '')

        # The log envelope repeats the install id, app version, device model and OS
        # version. Read the most recent record rather than trusting one arbitrary row.
        envelope = {}
        for log_path in _named(paths, 'etsy-logs'):
            for record in _recovered(log_path, _accept_log).values():
                document = _log_document(record)
                if not document:
                    continue
                try:
                    stamp = float(document.get('log_created_time'))
                except (TypeError, ValueError):
                    continue
                if stamp >= envelope.get('_stamp', 0):
                    envelope = dict(document, _stamp=stamp)

        browser_id = (install.get('EtsyUUID')
                      or (sentry_user.get('data') or {}).get('Browser ID')
                      or envelope.get('device_id', ''))

        row_paths = [context.get_relative_path(path) for path in paths]
        source_files.extend(row_paths)
        data_list.append((
            _ms(general.get('app_start_time')),
            _ms(general.get('app_inital_start_time')),
            _ms(config.get('last_updated')),
            user.get('etsyUserId', '') or sentry_user.get('id', ''),
            user.get('etsyUserLogin', ''),
            user.get('user_display_name', ''),
            user.get('user_primary_email', ''),
            browser_id,
            installation,
            device_id,
            internal_id,
            (sentry_user.get('data') or {}).get('Is Logged-in', ''),
            sentry_extras.get('AppLocale', ''),
            user.get('shippingCountryName', ''),
            user.get('shippingAddressCountryIso', ''),
            envelope.get('app_version', '') or (release if isinstance(release, str) else ''),
            envelope.get('hardware_platform_string', ''),
            envelope.get('device_system_version', ''),
            user.get('user_profile_image_url', ''),
            encrypted_entries,
            '; '.join(sorted({os.path.dirname(path) for path in row_paths})),
        ))

    data_headers = (
        ('Last App Start', 'datetime'),
        ('First App Start', 'datetime'),
        ('Server Config Last Updated', 'datetime'),
        'User ID',
        'Login Name',
        'Display Name',
        'Primary Email',
        'Browser ID',
        'Installation ID',
        'Device ID',
        'Internal Device ID',
        'Logged In (as stored)',
        'App Locale',
        'Shipping Country',
        'Shipping Country ISO',
        'App Version',
        'Device Model',
        'OS Version',
        'Profile Image URL',
        'Encrypted Preference Entries',
        'Source Directories',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


def _accept_viewed(rowid, values):
    '''(listing id, view time) for a recently viewed record, else None.

    The store holds three tables and only this one declares nine columns, so the count
    narrows the candidates. The image host and the timestamp range settle it: a page image
    that merely parses into nine values will not also carry the app's own image host in
    the third value and a timestamp in the range the column uses in the ninth.
    '''
    if len(values) != 9:
        return None
    image_url, timestamp = values[2], values[8]
    if not isinstance(image_url, str) or not image_url.startswith('https://i.etsystatic.com/'):
        return None
    if not isinstance(timestamp, int) or not 1_000_000_000_000 < timestamp < 2_000_000_000_000:
        return None
    if not isinstance(rowid, int) or rowid <= 0:
        return None
    return rowid, timestamp


@artifact_processor
def etsy_recently_viewed(context):
    data_list = []
    source_files = []
    index = _cache_index(context, 'image_manager_disk_cache')
    grouped = _by_container(context,
                            lambda path: os.path.basename(path) == 'recentlyViewedListings')

    statement = ('SELECT listingId, title, imageUrl, formattedOriginalPrice, '
                 'formattedDiscountedPrice, visible, rating, ratingCount, timestamp '
                 'FROM recentlyViewedListings')
    for container, paths in grouped.items():
        for source_path in paths:
            live = {(row[0], row[8]): list(row) for row in _rows(source_path, statement)}
            pre = {(row[0], row[8]): list(row) for row in _rows_pre_wal(source_path, statement)}
            recovered = {key: [key[0]] + list(values[1:])
                         for key, values in _recovered(source_path, _accept_viewed).items()}

            relative = context.get_relative_path(source_path)
            source_files.append(relative)
            for key, values, view in _merge(live, pre, recovered):
                cached = _cached_renditions(index, container, values[2])
                media = ''
                if cached:
                    label, mime, extension = _sniff_image(_read_head(cached[0]))
                    if label in _RENDERABLE:
                        media = check_in_media(cached[0], os.path.basename(cached[0]),
                                               force_type=mime, force_extension=extension)
                data_list.append((
                    _ms(values[8]),
                    values[0],
                    values[1] or '',
                    values[3] or '',
                    values[4] or '',
                    values[6] if values[6] is not None else '',
                    values[7] if values[7] is not None else '',
                    values[5] if values[5] is not None else '',
                    media or '',
                    len(cached),
                    values[2] or '',
                    view,
                    relative,
                ))

    data_headers = (
        ('View Time', 'datetime'),
        'Listing ID',
        'Title',
        'Original Price',
        'Discounted Price',
        'Rating',
        'Rating Count',
        'Visible (as stored)',
        ('Cached Image', 'media'),
        'Cached Renditions',
        'Image URL',
        'Source View',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


def _accept_interaction(rowid, values):
    '''The row id of a listing interaction record, else None.

    Only this table declares eight columns in its file. The logging key and interaction
    type must be text and the timestamp must fall in the range the column uses, so a page
    image holding eight values of another shape is rejected.
    '''
    if len(values) != 8:
        return None
    if not isinstance(values[1], str) or not isinstance(values[5], str):
        return None
    if not isinstance(values[7], int) or not 1_000_000_000_000 < values[7] < 2_000_000_000_000:
        return None
    return rowid


_ENCODED_RE = re.compile(r'^(\d+)-(\d{10})-')


@artifact_processor
def etsy_listing_interactions(context):
    data_list = []
    source_files = []
    statement = ('SELECT id, logging_key, display_loc, position, listing_source, '
                 'interaction_type, encoded_data, timestamp FROM listingInteractions')
    grouped = _by_container(context,
                            lambda path: os.path.basename(path) == 'ListingInteractions')

    for paths in grouped.values():
        for source_path in paths:
            live = {row[0]: list(row) for row in _rows(source_path, statement)}
            pre = {row[0]: list(row) for row in _rows_pre_wal(source_path, statement)}
            recovered = {key: [key] + list(values[1:])
                         for key, values in _recovered(source_path, _accept_interaction).items()}

            relative = context.get_relative_path(source_path)
            source_files.append(relative)
            for key, values, view in _merge(live, pre, recovered):
                encoded = values[6] if isinstance(values[6], str) else ''
                match = _ENCODED_RE.match(encoded)
                data_list.append((
                    _ms(values[7]),
                    values[5] or '',
                    values[4] or '',
                    values[2] or '',
                    values[3] if values[3] is not None else '',
                    match.group(1) if match else '',
                    _seconds(match.group(2)) if match else '',
                    values[1] or '',
                    view,
                    relative,
                ))

    data_headers = (
        ('Interaction Time', 'datetime'),
        'Interaction Type (as stored)',
        'Listing Source (as stored)',
        'Display Location (as stored)',
        'Position (as stored)',
        'Encoded Data Leading Value (as stored)',
        ('Encoded Data Time (as stored)', 'datetime'),
        'Logging Key',
        'Source View',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


def _accept_impression(_rowid, values):
    '''The (display location, logging key) of an ad impression record, else None.

    The impression and click tables both declare three columns. The impression table's
    primary key is its display location and logging key, so its first value is stored text.
    The click table's first column is its integer primary key, which SQLite stores as the
    row id and leaves out of the record, so its first value is always absent. That is what
    separates the two.
    '''
    if len(values) != 3:
        return None
    if not isinstance(values[0], str) or not isinstance(values[1], str):
        return None
    if not isinstance(values[2], int) or not 1_000_000_000_000 < values[2] < 2_000_000_000_000:
        return None
    return values[0], values[1]


def _accept_click(rowid, values):
    '''The row id of an ad click record, else None. See _accept_impression.'''
    if len(values) != 3 or values[0] is not None:
        return None
    if not isinstance(values[1], str):
        return None
    if not isinstance(values[2], int) or not 1_000_000_000_000 < values[2] < 2_000_000_000_000:
        return None
    return rowid


@artifact_processor
def etsy_ad_impressions(context):
    data_list = []
    source_files = []
    grouped = _by_container(context, lambda path: os.path.basename(path) == 'AdImpressions')

    for paths in grouped.values():
        for source_path in paths:
            relative = context.get_relative_path(source_path)
            source_files.append(relative)

            impressions = 'SELECT displayLocation, loggingKey, timestamp FROM adImpressions'
            live = {(row[0], row[1]): list(row) for row in _rows(source_path, impressions)}
            pre = {(row[0], row[1]): list(row) for row in _rows_pre_wal(source_path, impressions)}
            recovered = _recovered(source_path, _accept_impression)
            for key, values, view in _merge(live, pre, recovered):
                data_list.append((_ms(values[2]), 'Impression', values[0] or '',
                                  values[1] or '', view, relative))

            clicks = 'SELECT id, loggingKey, timestamp FROM adClicks'
            live = {row[0]: list(row) for row in _rows(source_path, clicks)}
            pre = {row[0]: list(row) for row in _rows_pre_wal(source_path, clicks)}
            recovered = {key: [key] + list(values[1:])
                         for key, values in _recovered(source_path, _accept_click).items()}
            for key, values, view in _merge(live, pre, recovered):
                data_list.append((_ms(values[2]), 'Click', '', values[1] or '', view, relative))

    data_headers = (
        ('Event Time', 'datetime'),
        'Event',
        'Display Location (as stored)',
        'Logging Key',
        'Source View',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


_LOG_ENVELOPE = {'log_created_time', 'app_version', 'device_id', 'data_type',
                 'app_name', 'data'}


def _log_document(values):
    '''The JSON document of a log record, or None when it is not one.'''
    if len(values) != 2 or not isinstance(values[1], str):
        return None
    try:
        document = json.loads(values[1])
    except ValueError:
        return None
    if not isinstance(document, dict) or not _LOG_ENVELOPE.issubset(document.keys()):
        return None
    return document


def _accept_log(rowid, values):
    '''The row id of a queued log record, else None.

    Three tables in this file hold two columns, so the column count decides nothing here.
    A candidate is kept only when its second value parses as JSON carrying the envelope
    keys the app writes, which no other table in the file produces.
    '''
    return rowid if _log_document(values) else None


@artifact_processor
def etsy_app_logs(context):
    data_list = []
    source_files = []
    grouped = _by_container(context, lambda path: os.path.basename(path) == 'etsy-logs')

    for paths in grouped.values():
        for source_path in paths:
            statement = 'SELECT id, logAsJson FROM logs'
            live = {row[0]: list(row) for row in _rows(source_path, statement)}
            pre = {row[0]: list(row) for row in _rows_pre_wal(source_path, statement)}
            recovered = {key: [key, values[1]]
                         for key, values in _recovered(source_path, _accept_log).items()}

            relative = context.get_relative_path(source_path)
            source_files.append(relative)
            for key, values, view in _merge(live, pre, recovered):
                document = _log_document(values)
                if not document:
                    continue
                payload = document.get('data')
                payload = payload if isinstance(payload, dict) else {}
                data_list.append((
                    _seconds(document.get('log_created_time')),
                    document.get('data_type', ''),
                    payload.get('log_namespace', ''),
                    payload.get('log_message', ''),
                    document.get('app_version', ''),
                    view,
                    relative,
                ))

    data_headers = (
        ('Log Time', 'datetime'),
        'Data Type (as stored)',
        'Log Namespace (as stored)',
        'Log Message',
        'App Version',
        'Source View',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


def _json_objects(text):
    '''Every balanced top level JSON object in text.

    The breadcrumb cache is a fixed size buffer rather than a document, so it holds a
    length prefix and whatever the previous write left behind. Objects are located inside
    it instead of the file being parsed as a whole.
    '''
    depth = 0
    start = None
    in_string = False
    escaped = False
    for position, character in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif character == '\\':
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == '{':
            if depth == 0:
                start = position
            depth += 1
        elif character == '}':
            if depth:
                depth -= 1
                if depth == 0 and start is not None:
                    try:
                        yield json.loads(text[start:position + 1])
                    except ValueError:
                        pass
                    start = None


@artifact_processor
def etsy_network_breadcrumbs(context):
    data_list = []
    source_files = []
    grouped = _by_container(context,
                            lambda path: os.path.basename(path) == 'breadcrumbs.json')

    for paths in grouped.values():
        for source_path in paths:
            try:
                with open(source_path, 'rb') as handle:
                    text = handle.read().decode('utf-8', 'replace')
            except OSError as ex:
                logfunc(f'Could not read {os.path.basename(source_path)}: {ex}')
                continue
            relative = context.get_relative_path(source_path)
            source_files.append(relative)
            for document in _json_objects(text):
                payload = document.get('data')
                if not isinstance(payload, dict):
                    continue
                start = payload.get('http.start_timestamp')
                end = payload.get('http.end_timestamp')
                duration = ''
                if isinstance(start, int) and isinstance(end, int):
                    duration = end - start
                data_list.append((
                    _ms(start) or document.get('timestamp', ''),
                    payload.get('method', ''),
                    payload.get('host', ''),
                    payload.get('path', ''),
                    payload.get('error_message', ''),
                    duration,
                    document.get('type', ''),
                    relative,
                ))

    data_headers = (
        ('Request Time', 'datetime'),
        'Method',
        'Host',
        'Path',
        'Error Message',
        'Duration (ms)',
        'Breadcrumb Type (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def etsy_image_caches(context):
    data_list = []
    source_files = []
    summary = {}

    for file_found in unique_files(context):
        normalised = str(file_found).replace('\\', '/')
        parts = normalised.split('/')
        if len(parts) < 2:
            continue
        directory = parts[-2]
        if directory not in ('image_manager_disk_cache', 'appboy.imageloader.lru.cache'):
            continue
        key = (_container(context, file_found), directory)
        entry = summary.setdefault(key, {'entries': 0, 'bytes': 0, 'types': {},
                                         'earliest': None, 'latest': None, 'path': ''})
        entry['path'] = context.get_relative_path(os.path.dirname(normalised))
        if os.path.basename(normalised) == 'journal':
            continue
        entry['entries'] += 1
        try:
            entry['bytes'] += os.path.getsize(file_found)
            modified = os.path.getmtime(file_found)
        except OSError:
            continue
        label = _sniff_image(_read_head(file_found))[0]
        entry['types'][label] = entry['types'].get(label, 0) + 1
        if entry['earliest'] is None or modified < entry['earliest']:
            entry['earliest'] = modified
        if entry['latest'] is None or modified > entry['latest']:
            entry['latest'] = modified

    for (_key, directory), entry in sorted(summary.items()):
        if not entry['entries']:
            continue
        source_files.append(entry['path'])
        data_list.append((
            _EPOCH + timedelta(seconds=entry['latest']) if entry['latest'] else '',
            _EPOCH + timedelta(seconds=entry['earliest']) if entry['earliest'] else '',
            directory,
            entry['entries'],
            entry['bytes'],
            ', '.join(f'{label} {count}'
                      for label, count in sorted(entry['types'].items())),
            entry['path'],
        ))

    data_headers = (
        ('Latest Entry Modified', 'datetime'),
        ('Earliest Entry Modified', 'datetime'),
        'Cache Directory',
        'Entries',
        'Bytes On Disk',
        'Entry Types',
        'Source Path',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
