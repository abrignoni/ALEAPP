__artifacts_v2__ = {
    "ebay_watch_list": {
        "name": "eBay - Watch List",
        "description": "Parses the watched listings stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the watch_list table of nautilus_db. Listing End Date is a Unix "
                 "millisecond value. The table's primary key is a separate entry key that is not "
                 "the listing id on any tested row, so both are reported. Aspects is the record's "
                 "own JSON and is reported as stored. Where the app's image cache is present in "
                 "the extraction the cached picture is rendered on the row: the cache file name is "
                 "the base64url encoded SHA-256 of the image URL the app requested, and the app "
                 "requests a rewritten size and extension rather than the URL stored here, so the "
                 "stored URL is matched against the rendition variants observed in the cache. A "
                 "match is a SHA-256 equality on the full URL, not a size or time correlation. "
                 "On one tested sample 5 of its 10 watched listings resolved to a cached picture, "
                 "together accounting for 9 cache files because the app had cached several sizes of "
                 "the same picture; the largest rendition found is the one rendered here, and every "
                 "rendition is listed by eBay - Cached Images. Another sample held 370 watched "
                 "listings and no cache directory at all, so none of its rows carry a picture. "
                 "Field mapping was done against private samples; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/com.ebay.mobile/databases/nautilus_db*',
            '*/com.ebay.mobile/cache/cacheManager/image_cache.disk/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "eye"
    },
    "ebay_recent_searches": {
        "name": "eBay - Recent Searches",
        "description": "Parses the recent search history stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the RecentSearchEntity table of nautilus_db, which the app keys by its "
                 "own user id, so rows for more than one account can be present in one table and "
                 "the user id is reported on every row. Timestamp is a Unix millisecond value. "
                 "Search Result Count is the count the app recorded for that search, not a count "
                 "of anything in this extraction. The table carries a thumbnail column; it was "
                 "null on every row of every tested sample, so no picture is rendered from it. "
                 "Its productPrefix and isSpelledCorrectly columns are not reported because they "
                 "were empty and zero respectively on every row of every tested sample; sellerPrefix "
                 "is reported because one sample populated it. The same terms also appear in the "
                 "separate suggestions.db store reported by eBay - Search Suggestions, which "
                 "retains a different set; on one tested sample 43 of that store's 44 terms were "
                 "also here, so neither store is a superset of the other. Field mapping was done "
                 "against private samples; no sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "ebay_search_suggestions": {
        "name": "eBay - Search Suggestions",
        "description": "Parses the saved search queries stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the suggestions table of suggestions.db, whose schema is the one the "
                 "Android platform's SearchRecentSuggestionsProvider creates. This store holds "
                 "terms entered on the device rather than suggestions downloaded from a server. "
                 "On the tested samples the row ids were gapped rather than a contiguous run, "
                 "every stored date was distinct and they spanned 122, 205 and 183 days, no two "
                 "consecutive rows were written within a second of each other, the schema carries "
                 "no relevance or score column, and no preference naming a fetch, cache version or "
                 "partition for this store was found in the app's shared_prefs. The terms also "
                 "cross-check against the app's own separate recent search table. Distinctness of "
                 "the values is not evidence either way here, because the display column is "
                 "declared UNIQUE ON CONFLICT REPLACE and so cannot repeat. Date is a Unix "
                 "millisecond value. The display column equalled the query column on every row of "
                 "every tested sample, so only the query is reported. Field mapping was done "
                 "against private samples; no sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/suggestions.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "ebay_followed_searches": {
        "name": "eBay - Followed Searches",
        "description": "Parses the followed searches and interests cached by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the app's own cacheManager store, whose entries begin with a four byte "
                 "big endian length, a JSON header carrying an item count and an expiration time, "
                 "and then the cached JSON. Two caches are read: the followed searches cache, "
                 "which carries a follow date, and the interests cache, which carries the same "
                 "interest records without one. Follow Date is stored as an ISO 8601 string ending "
                 "in Z. Since Time and View Time are Unix millisecond values, and on the tested "
                 "sample all three agreed on the same instant. Type and Visibility are reported as "
                 "stored. An interest present only in the interests cache is reported with no "
                 "follow date rather than dropped. Cache Expires is the expiration the app "
                 "recorded for the cache entry, not a property of the followed search. Field "
                 "mapping was done against private samples; no sample data is recorded for them.",
        "paths": (
            '*/com.ebay.mobile/cache/cacheManager/FollowingDataManager_FollowedSearches.disk/*',
            '*/com.ebay.mobile/cache/cacheManager/FollowingDataManager_Interests.disk/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bell"
    },
    "ebay_followed_sellers": {
        "name": "eBay - Followed Sellers",
        "description": "Parses the followed seller records stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the followed_seller_entity table of nautilus_db. The table carries no "
                 "timestamp, so when the seller was followed cannot be established from it. "
                 "Following is the flag as stored; a row whose value is zero records a seller the "
                 "app tracked as not currently followed, so presence of a row is not by itself "
                 "evidence the account follows that seller. The hashed user id is the same 64 "
                 "character form the recent search table uses, which is what ties these rows to an "
                 "account. Field mapping was done against private samples; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user-check"
    },
    "ebay_app_sessions": {
        "name": "eBay - App Sessions",
        "description": "Parses the app session records stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the apls_session table of nautilus_db, with the screen names joined "
                 "from apls_beacon and a count of the network calls the session recorded. Session "
                 "Start is startTimeWallClock, a Unix millisecond value, and is the only column in "
                 "these tables that is an epoch. startTimeElapsedRealtime is milliseconds since "
                 "boot and is reported as stored. The endTimeElapsedRealtime column is not reported "
                 "because it was zero on every row of every tested sample, so no session end or "
                 "duration can be derived. "
                 "apls_call table records the app's own network timing and its start column is an "
                 "offset within the session rather than an epoch; its rows were dominated by "
                 "telemetry uploads and its listing and product identifier columns were empty on "
                 "every row of every tested sample, so those calls are counted here rather than "
                 "enumerated. Screens is the activity names the session recorded, which is what "
                 "shows which parts of the app were opened. Field mapping was done against private "
                 "samples; no sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock"
    },
    "ebay_cached_images": {
        "name": "eBay - Cached Images",
        "description": "Parses the cached listing images stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the app's own image cache under cache/cacheManager/image_cache.disk. "
                 "Each file begins with a four byte big endian length, a JSON header carrying the "
                 "item size and an expiration time, then a count and length prefixed metadata "
                 "block, then the image bytes. The image is rendered from the bytes that follow "
                 "that framing rather than from the file, because the file is not itself an image. "
                 "The format is taken from those bytes; every image on the tested sample was WEBP. "
                 "The file name is the base64url encoded SHA-256 of the URL the app requested, so "
                 "the URL cannot be recovered from the name, but a listing whose image URL is held "
                 "elsewhere in the extraction can be matched to its file by hashing; where that "
                 "resolves the listing is named on the row. A row with no listing named is an "
                 "image the app cached that no watched listing in this extraction points at. Cache "
                 "A listing whose picture was cached at more than one size owns one row per size, so "
                 "the listing columns can repeat. Cache Expires is the expiration the app recorded, "
                 "not a time the image was viewed. On the tested sample every image was WEBP and "
                 "every metadata block read is_ai_generated false; both are reported rather than "
                 "dropped because a different value is what would matter. "
                 "Field mapping was done against private samples; no sample data is recorded for "
                 "them.",
        "paths": (
            '*/com.ebay.mobile/cache/cacheManager/image_cache.disk/*',
            '*/com.ebay.mobile/databases/nautilus_db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image"
    },
    "ebay_accounts": {
        "name": "eBay - Accounts",
        "description": "Parses the user identifiers the eBay Android app stored across its own tables.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "One row per distinct user identifier found in nautilus_db, naming the table and "
                 "column it came from. The app stores several different identifier forms for the "
                 "same person and does not key every table the same way, so the forms are reported "
                 "separately rather than merged: a short public user id, a 64 character hashed "
                 "user id, and a longer hashed form used by the push token table. On the tested "
                 "samples the share table's user id equalled the identifier the network log "
                 "recorded, and the followed seller table's hashed user id equalled the one the "
                 "recent search table recorded, which is what allows rows in those tables to be "
                 "attributed. More than one identifier of the same form in one extraction means "
                 "more than one account was used on the device; two tested samples held two and "
                 "three distinct recent search user ids. No account name, email address or display "
                 "name is stored in these tables. Field mapping was done against private samples; "
                 "no sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "ebay_app_configuration": {
        "name": "eBay - App Configuration",
        "description": "Parses the app and marketplace configuration record of the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the FtsMetadataEntity table of nautilus_db, which is the record the app "
                 "wrote when it last fetched its feature configuration. It states the app version, "
                 "the eBay marketplace site and country, the language, the Android SDK level and "
                 "the environment the app was running against, and the fetch time as a Unix "
                 "millisecond value. Site Code and Country Code are separate values that agree on a "
                 "marketplace whose site and country codes are the same letters. The companion "
                 "FtsDataEntity table "
                 "values themselves, which are settings the server sent to the device rather than "
                 "anything the user did, so its rows are counted here and not listed. Field "
                 "mapping was done against private samples; no sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "ebay_app_state": {
        "name": "eBay - App State",
        "description": "Parses the timestamped application state entries of the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the key_value table of nautilus_db, one row per entry, with the value "
                 "taken from whichever of the table's typed columns the entry populated and the "
                 "column named on the row. Timestamp is a Unix millisecond value and is when the "
                 "app last wrote that entry. Entries are keyed by the app's own user id as well as "
                 "by name, so the same key can appear more than once for different accounts and "
                 "the user id is reported. What the app does with each entry is not established "
                 "here, so no meaning is asserted beyond the key name the app itself uses. Two "
                 "entries hold an encrypted device registration blob; their length is reported and "
                 "the bytes are not decoded. Field mapping was done against private samples; no "
                 "sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "sliders"
    },
    "ebay_share_channels": {
        "name": "eBay - Share Channels",
        "description": "Parses the share channel records stored by the eBay Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "eBay",
        "notes": "Read from the share_channels table of nautilus_db, which records a named sharing "
                 "destination against the app's user id. The schema names the numeric column "
                 "value; it held a Unix millisecond value on every row of the tested samples and "
                 "is reported both as a date and as stored, because the schema does not state that "
                 "it is a time. What the channel name records is the destination the app offered "
                 "or used, and the table does not record what was shared, so a row is not by "
                 "itself evidence that a particular listing was sent. Field mapping was done "
                 "against private samples; no sample data is recorded for them.",
        "paths": ('*/com.ebay.mobile/databases/nautilus_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "share-2"
    },
}

import base64
import hashlib
import json
import os
import re
import struct
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    get_sqlite_db_records,
    logfunc,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Leading bytes to (label, mime, extension). The cached images carry no extension and the
# type is taken from the bytes rather than from the file name.
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF87a', 'GIF', 'image/gif', 'gif'),
    (b'GIF89a', 'GIF', 'image/gif', 'gif'),
)

# Rendition sizes the app is observed to request. The listing record stores one URL and the
# app fetches a rewritten size and extension, so the stored URL alone does not hash to the
# cache file name. Each candidate is confirmed by SHA-256 equality with a file name, so a
# wrong candidate cannot match: a hit names the exact URL whose response that file holds.
# Largest first, so a listing cached at several sizes renders its best available picture.
_RENDITIONS = ('s-l1600', 's-l1200', 's-l960', 's-l640', 's-l500', 's-l400',
               's-l300', 's-l225', 's-l140', 's-l96', 's-l64')
_RENDITION_EXTENSIONS = ('.webp', '.jpg', '.png')
_RENDITION_PATTERN = re.compile(r's-l\d+\.(?:jpg|jpeg|webp|png)$', re.I)

# The value columns of key_value, in the order they are tried.
_VALUE_COLUMNS = ('booleanValue', 'intValue', 'longValue', 'floatValue', 'value', 'stringSet')


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.

    Converted here rather than through the shared helper, which infers the unit from the
    value's magnitude and so cannot separate milliseconds from seconds near the epoch.
    These columns are always milliseconds. Adding a timedelta to the epoch also avoids
    datetime.fromtimestamp, which raises on Windows for any value before 1970.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    return _EPOCH + timedelta(milliseconds=value) if value else ''


def _iso(value):
    '''An ISO 8601 string as a UTC datetime, or '' when it cannot be read as one.

    The fractional part is padded to six digits because datetime.fromisoformat rejects any
    other length before Python 3.11, and a trailing Z is replaced because it is not
    accepted before 3.11 either.
    '''
    if not value:
        return ''
    text = str(value).strip()
    if text.endswith(('Z', 'z')):
        text = text[:-1] + '+00:00'
    match = re.search(r'\.(\d{1,6})', text)
    if match:
        text = text.replace(f'.{match.group(1)}', '.' + match.group(1).ljust(6, '0'), 1)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return ''
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _text(value):
    '''A cell value as text, with None rendered as an empty cell.'''
    if value is None:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return str(value)


def _databases(context, name):
    '''The deduplicated paths of one database, ignoring its journal and WAL sidecars.'''
    return [path for path in unique_files(context)
            if os.path.basename(path) == name]


def _table_exists(file_found, table):
    '''Whether a table is present, so a release that predates it is skipped, not failed.

    The name is a literal from this module rather than anything read out of the evidence,
    and it is quoted here so a table name is never concatenated raw into a statement.
    '''
    quoted = table.replace("'", "''")
    for row in get_sqlite_db_records(
            file_found,
            f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{quoted}'"):
        return bool(row[0])
    return False


def _cache_entry(file_found):
    '''The header, metadata blocks and payload of one cacheManager entry.

    The entry is a four byte big endian length, a JSON header, and then the cached value.
    An image entry additionally carries a count and a length prefixed metadata block ahead
    of its bytes; a JSON entry does not, so the metadata block is read only when what
    follows the header is not itself the start of the cached JSON. Every length is checked
    against the bytes that remain, so a truncated file yields nothing rather than a
    fabricated payload.
    '''
    with open(file_found, 'rb') as handle:
        raw = handle.read()
    if len(raw) < 4:
        return None, [], b''
    offset = 0
    (length,) = struct.unpack('>I', raw[offset:offset + 4])
    offset += 4
    if length <= 0 or offset + length > len(raw):
        return None, [], b''
    try:
        header = json.loads(raw[offset:offset + length])
    except ValueError:
        return None, [], b''
    offset += length
    if offset < len(raw) and raw[offset:offset + 1] in (b'{', b'['):
        return header, [], raw[offset:]
    metadata = []
    if offset + 4 <= len(raw):
        (count,) = struct.unpack('>I', raw[offset:offset + 4])
        if 0 < count <= 16:
            probe = offset + 4
            blocks = []
            for _ in range(count):
                if probe + 4 > len(raw):
                    blocks = []
                    break
                (size,) = struct.unpack('>I', raw[probe:probe + 4])
                probe += 4
                if size < 0 or probe + size > len(raw):
                    blocks = []
                    break
                blocks.append(raw[probe:probe + size])
                probe += size
            if blocks:
                metadata = blocks
                offset = probe
    return header, metadata, raw[offset:]


def _image_kind(payload):
    '''(label, mime, extension) for the image bytes, or None when they are not an image.'''
    for magic, label, mime, extension in _IMAGE_MAGIC:
        if payload.startswith(magic):
            return label, mime, extension
    if payload[:4] == b'RIFF' and payload[8:12] == b'WEBP':
        return 'WEBP', 'image/webp', 'webp'
    return None


def _cache_key(url):
    '''The cache file name the app uses for a URL: base64url of its SHA-256.'''
    return base64.urlsafe_b64encode(hashlib.sha256(url.encode()).digest()).decode()


def _url_candidates(url):
    '''The stored URL and the rendition variants the app is observed to request.'''
    yield url
    base = _RENDITION_PATTERN.sub('', url)
    if base == url:
        return
    for size in _RENDITIONS:
        for extension in _RENDITION_EXTENSIONS:
            yield base + size + extension


_PACKAGE = 'com.ebay.mobile'


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The cache
    and listing indexes below are keyed on it together with their own key, because a cache
    entry name repeats across app data directories: keying on the name alone dropped a
    second Android user's cache entries and could hand one directory's image to another
    directory's listing.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _image_cache_files(context):
    '''(container, cache file name) to path for every entry of the app's image cache.'''
    files = {}
    for path in unique_files(context):
        parts = path.replace('\\', '/').split('/')
        if 'image_cache.disk' not in parts:
            continue
        name = os.path.basename(path)
        if not name.endswith('.dat'):
            continue
        files.setdefault((_container(context, path), name[:-4]), path)
    return files


def _watch_rows(file_found):
    '''The watch_list rows of one database, or an empty list when the table is absent.'''
    if not _table_exists(file_found, 'watch_list'):
        return []
    return list(get_sqlite_db_records(file_found, '''
        SELECT listingEndDate, title, listingId, variationId, aspects, listingImageUrl,
               isPartial, key
        FROM watch_list'''))


def _listing_by_cache_key(context):
    '''(container, cache file name) to (listing id, title) for each resolving listing.

    The listing's stored image URL and each rendition variant of it are hashed and looked
    up among the cache file names. Equality of a SHA-256 over the whole URL is what makes
    the match, so this identifies the file rather than ranking candidates.
    '''
    resolved = {}
    for file_found in _databases(context, 'nautilus_db'):
        owner = _container(context, file_found)
        for row in _watch_rows(file_found):
            url = _text(row[5])
            if not url:
                continue
            for candidate in _url_candidates(url):
                key = (owner, _cache_key(candidate))
                if key not in resolved:
                    resolved[key] = (_text(row[2]), _text(row[1]))
    return resolved


@artifact_processor
def ebay_watch_list(context):
    data_list = []
    source_path = ''
    cache_files = _image_cache_files(context)

    for file_found in _databases(context, 'nautilus_db'):
        rows = _watch_rows(file_found)
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        owner = _container(context, file_found)
        for row in rows:
            url = _text(row[5])
            media = ''
            if url and cache_files:
                for candidate in _url_candidates(url):
                    cache_path = cache_files.get((owner, _cache_key(candidate)))
                    if not cache_path:
                        continue
                    _, _, payload = _cache_entry(cache_path)
                    kind = _image_kind(payload)
                    if kind:
                        media = check_in_embedded_media(
                            cache_path, payload, f'{_text(row[2])}.{kind[2]}',
                            force_type=kind[1], force_extension=kind[2])
                    break
            data_list.append((
                _ms(row[0]),
                _text(row[1]),
                _text(row[2]),
                _text(row[3]),
                media,
                url,
                _text(row[4]),
                _text(row[6]),
                _text(row[7]),
                relative,
            ))

    data_headers = (
        ('Listing End Date', 'datetime'),
        'Title',
        'Listing ID',
        'Variation ID',
        ('Cached Image', 'media'),
        'Listing Image URL',
        'Aspects',
        'Partial Record (as stored)',
        'Entry Key',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_recent_searches(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        if not _table_exists(file_found, 'RecentSearchEntity'):
            continue
        rows = list(get_sqlite_db_records(file_found, '''
            SELECT timestamp, keyword, categoryId, searchResultCount, isSpelledCorrectly,
                   sellerPrefix, productPrefix, userId, uid
            FROM RecentSearchEntity'''))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for row in rows:
            data_list.append((
                _ms(row[0]),
                _text(row[1]),
                _text(row[2]),
                _text(row[3]),
                _text(row[5]),
                _text(row[7]),
                _text(row[8]),
                relative,
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Search Keyword',
        'Category ID',
        'Search Result Count (as recorded)',
        'Seller Prefix',
        'User ID',
        'Row ID',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_search_suggestions(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'suggestions.db'):
        if not _table_exists(file_found, 'suggestions'):
            continue
        rows = list(get_sqlite_db_records(
            file_found, 'SELECT date, query, _id FROM suggestions'))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for row in rows:
            data_list.append((_ms(row[0]), _text(row[1]), _text(row[2]), relative))

    data_headers = (
        ('Date', 'datetime'),
        'Search Query',
        'Row ID',
        'Source File',
    )
    return data_headers, data_list, source_path


def _interest_columns(interest):
    '''The reported fields of one interest record.'''
    request = interest.get('searchRequest') or {}
    return (
        _text(interest.get('searchName')),
        _text(request.get('keyword')),
        _text(request.get('categoryId')),
        _text(request.get('sortOrder')),
        _text(request.get('shipToLocation')),
        _text(interest.get('searchFilters')),
        _text(interest.get('marketplaceId')),
        _text(interest.get('title')),
        _text(interest.get('searchUrl')),
    )


@artifact_processor
def ebay_followed_searches(context):
    data_list = []
    source_path = ''
    seen = set()

    followed = [path for path in unique_files(context)
                if 'FollowingDataManager_FollowedSearches.disk' in path.replace('\\', '/')
                and path.endswith('.dat')]
    interests = [path for path in unique_files(context)
                 if 'FollowingDataManager_Interests.disk' in path.replace('\\', '/')
                 and path.endswith('.dat')]

    for file_found in followed:
        header, _, payload = _cache_entry(file_found)
        if header is None:
            logfunc(f'eBay followed searches: could not read cache framing of {file_found}')
            continue
        try:
            document = json.loads(payload.decode('utf-8', 'replace'))
        except ValueError:
            logfunc(f'eBay followed searches: cached value is not JSON in {file_found}')
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for entry in document.get('followedSearches') or []:
            interest = entry.get('interest') or {}
            identifier = _text(entry.get('interestId') or interest.get('interestId'))
            seen.add(identifier)
            data_list.append((
                _iso(entry.get('followDate')),
                _ms(entry.get('sinceTime')),
                _ms(entry.get('viewTime')),
                *_interest_columns(interest),
                _text(entry.get('customTitle')),
                identifier,
                _text(entry.get('type')),
                _text(entry.get('visibility')),
                _text(entry.get('newItems')),
                _ms(header.get('expirationTime')),
                relative,
            ))

    for file_found in interests:
        header, _, payload = _cache_entry(file_found)
        if header is None:
            continue
        try:
            document = json.loads(payload.decode('utf-8', 'replace'))
        except ValueError:
            continue
        if not source_path:
            source_path = file_found
        relative = context.get_relative_path(file_found)
        for interest in document.get('interests') or []:
            identifier = _text(interest.get('interestId'))
            if identifier in seen:
                continue
            seen.add(identifier)
            data_list.append((
                '', '', '',
                *_interest_columns(interest),
                '', identifier, '', '', '',
                _ms(header.get('expirationTime')),
                relative,
            ))

    data_headers = (
        ('Follow Date', 'datetime'),
        ('Since Time', 'datetime'),
        ('View Time', 'datetime'),
        'Search Name',
        'Keyword',
        'Category ID',
        'Sort Order',
        'Ship To Location',
        'Search Filters',
        'Marketplace',
        'Title',
        'Search URL',
        'Custom Title',
        'Interest ID',
        'Type (as stored)',
        'Visibility (as stored)',
        'New Items (as stored)',
        ('Cache Expires', 'datetime'),
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_followed_sellers(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        if not _table_exists(file_found, 'followed_seller_entity'):
            continue
        rows = list(get_sqlite_db_records(
            file_found, 'SELECT sellerId, following, hashedUserId FROM followed_seller_entity'))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for row in rows:
            data_list.append((_text(row[0]), _text(row[1]), _text(row[2]), relative))

    data_headers = (
        'Seller ID',
        'Following (as stored)',
        'Hashed User ID',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_app_sessions(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        if not _table_exists(file_found, 'apls_session'):
            continue
        rows = list(get_sqlite_db_records(file_found, '''
            SELECT s.startTimeWallClock, s.guid, s.startTimeElapsedRealtime,
                   s.endTimeElapsedRealtime,
                   (SELECT group_concat(DISTINCT b.activity) FROM apls_beacon b
                     WHERE b.sessionId = s.guid),
                   (SELECT count(*) FROM apls_call c WHERE c.sessionId = s.guid)
            FROM apls_session s
            ORDER BY s.startTimeWallClock'''))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for row in rows:
            data_list.append((
                _ms(row[0]),
                _text(row[4]),
                _text(row[5]),
                _text(row[1]),
                _text(row[2]),
                relative,
            ))

    data_headers = (
        ('Session Start', 'datetime'),
        'Screens',
        'Network Call Count',
        'Session GUID',
        'Start Elapsed Realtime (as stored)',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_cached_images(context):
    data_list = []
    source_path = ''
    listings = _listing_by_cache_key(context)

    for (owner, name), file_found in sorted(_image_cache_files(context).items()):
        header, metadata, payload = _cache_entry(file_found)
        if header is None:
            logfunc(f'eBay cached images: could not read cache framing of {file_found}')
            continue
        kind = _image_kind(payload)
        if not kind:
            logfunc(f'eBay cached images: cached value is not an image in {file_found}')
            continue
        source_path = file_found
        listing_id, title = listings.get((owner, name), ('', ''))
        media = check_in_embedded_media(
            file_found, payload, f'{name}.{kind[2]}',
            force_type=kind[1], force_extension=kind[2])
        notes = ''
        for block in metadata:
            try:
                notes = json.dumps(json.loads(block.decode('utf-8', 'replace')))
            except ValueError:
                notes = ''
        data_list.append((
            _ms(header.get('expirationTime')),
            media,
            listing_id,
            title,
            kind[0],
            _text(len(payload)),
            notes,
            name,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Cache Expires', 'datetime'),
        ('Cached Image', 'media'),
        'Linked Listing ID',
        'Linked Listing Title',
        'Format',
        'Image Bytes',
        'Cache Metadata (as stored)',
        'Cache Key',
        'Source File',
    )
    return data_headers, data_list, source_path


# (table, column, the form the identifier takes) for every place a user id is stored.
_IDENTIFIER_SOURCES = (
    ('key_value', 'publicUserId', 'Public user id'),
    ('RecentSearchEntity', 'userId', 'Recent search user id'),
    ('followed_seller_entity', 'hashedUserId', 'Hashed user id'),
    ('share_entity', 'userId', 'Share user id'),
    ('fcm_token', 'hashedUserId', 'Push token user id'),
    ('opt_in_encode_entity', 'userId', 'Opt in user id'),
)


@artifact_processor
def ebay_accounts(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        relative = context.get_relative_path(file_found)
        found = False
        for table, column, form in _IDENTIFIER_SOURCES:
            if not _table_exists(file_found, table):
                continue
            for row in get_sqlite_db_records(
                    file_found,
                    f'SELECT DISTINCT {column} FROM {table} '
                    f'WHERE {column} IS NOT NULL AND {column} <> ""'):
                value = _text(row[0])
                if not value or value == 'global':
                    continue
                found = True
                data_list.append((value, form, table, column, _text(len(value)), relative))
        if found:
            source_path = file_found

    data_headers = (
        'User Identifier',
        'Identifier Form',
        'Source Table',
        'Source Column',
        'Identifier Length',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_app_configuration(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        if not _table_exists(file_found, 'FtsMetadataEntity'):
            continue
        rows = list(get_sqlite_db_records(file_found, '''
            SELECT timestamp, appVersion, siteCode, countryCode, languageCode, androidSdk,
                   environment, isGbh, responseLevel, rolloutThreshold, eTag
            FROM FtsMetadataEntity'''))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        values = 0
        for row in get_sqlite_db_records(file_found, 'SELECT count(*) FROM FtsDataEntity'):
            values = row[0]
        for row in rows:
            data_list.append((
                _ms(row[0]),
                _text(row[1]),
                _text(row[2]),
                _text(row[3]),
                _text(row[4]),
                _text(row[5]),
                _text(row[6]),
                _text(row[7]),
                _text(row[8]),
                _text(row[9]),
                _text(row[10]),
                _text(values),
                relative,
            ))

    data_headers = (
        ('Configuration Fetched', 'datetime'),
        'App Version',
        'Site Code',
        'Country Code',
        'Language Code',
        'Android SDK',
        'Environment',
        'Global Buyer Hub (as stored)',
        'Response Level (as stored)',
        'Rollout Threshold (as stored)',
        'ETag',
        'Configuration Value Count',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_app_state(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        if not _table_exists(file_found, 'key_value'):
            continue
        rows = list(get_sqlite_db_records(file_found, f'''
            SELECT timestamp, key, publicUserId, {", ".join(_VALUE_COLUMNS)},
                   length(encryptedData)
            FROM key_value'''))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for row in rows:
            value = ''
            column = ''
            for index, name in enumerate(_VALUE_COLUMNS, start=3):
                if row[index] is not None:
                    value = _text(row[index])
                    column = name
                    break
            encrypted = row[3 + len(_VALUE_COLUMNS)]
            if not column and encrypted:
                column = 'encryptedData'
                value = f'{encrypted} encrypted bytes, not decoded'
            data_list.append((
                _ms(row[0]),
                _text(row[1]),
                value,
                column,
                _text(row[2]),
                relative,
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Key',
        'Value',
        'Stored In Column',
        'User ID',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def ebay_share_channels(context):
    data_list = []
    source_path = ''

    for file_found in _databases(context, 'nautilus_db'):
        if not _table_exists(file_found, 'share_channels'):
            continue
        rows = list(get_sqlite_db_records(
            file_found, 'SELECT value, channelName, id FROM share_channels'))
        if not rows:
            continue
        source_path = file_found
        relative = context.get_relative_path(file_found)
        for row in rows:
            data_list.append((_ms(row[0]), _text(row[1]), _text(row[0]), _text(row[2]), relative))

    data_headers = (
        ('Value As Date', 'datetime'),
        'Channel Name',
        'Value (as stored)',
        'User ID',
        'Source File',
    )
    return data_headers, data_list, source_path
