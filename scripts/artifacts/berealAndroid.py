__artifacts_v2__ = {
    "bereal_cached_media": {
        "name": "BeReal Cached Media",
        "description": "Photos and videos recovered from the BeReal caches on disk, with the "
                       "source URL and cache date read from the OkHttp cache metadata where present",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "BeReal",
        "notes": "BeReal keeps its Room databases (bereal.core.database.db and the others) as "
                 "SQLCipher encrypted files whose passphrase is wrapped by an Android Keystore "
                 "backed key, so those databases cannot be read from a file system extraction. "
                 "The media itself survives in the app caches. The OkHttp network cache stores a "
                 "'.0' metadata file next to each '.1' body; the source URL is the first line and "
                 "the response date is a header, and both are reported here. The Coil image caches "
                 "(memories, friend timeline, profile pictures) keep only response headers, so "
                 "those rows carry the cache date but no URL. Files are matched to their metadata "
                 "by name, and content is checked in by signature rather than by any extension.",
        "paths": ('*/com.bereal.ft/cache/network/*',
                  '*/com.bereal.ft/cache/memories_cache/*',
                  '*/com.bereal.ft/cache/friend_timeline_cache/*',
                  '*/com.bereal.ft/cache/profile_picture_friends_cache/*',
                  '*/com.bereal.ft/cache/bereal_user_video_cache/*',
                  '*/com.bereal.ft/cache/bereal_mypost_user_video_cache/*',
                  '*/com.bereal.ft/files/bereal_my_user_temp_video/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.bereal.ft | media recovered from caches",
            "hc_pixel8pro_a17": "Android 17 | com.bereal.ft | media recovered from caches",
        },
    },
    "bereal_friends": {
        "name": "BeReal Friends",
        "description": "Friends recovered from cached responses of the relationships and friend "
                       "recommendation endpoints, with the user name, full name and status BeReal "
                       "returned",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "BeReal",
        "notes": "Read from the JSON bodies in the OkHttp network cache, not from the encrypted "
                 "databases, so the list reflects what had been fetched and cached rather than the "
                 "full friend list. The hashed phone number is reported as BeReal stored it.",
        "paths": ('*/com.bereal.ft/cache/network/*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.bereal.ft | cached relationships responses",
            "hc_pixel8pro_a17": "Android 17 | com.bereal.ft | 1 friend cached",
        },
    },
    "bereal_cached_api": {
        "name": "BeReal Cached API Responses",
        "description": "Index of the BeReal API responses held in the OkHttp network cache, with "
                       "the endpoint URL, the cached response date and a short summary of the body",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "BeReal",
        "notes": "Lists every cached response so an examiner can see which endpoints were called "
                 "and open the JSON bodies that this artifact does not expand, for example the "
                 "moment of the day, block lists and friend requests.",
        "paths": ('*/com.bereal.ft/cache/network/*',),
        "output_types": "standard",
        "artifact_icon": "server",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.bereal.ft | cached API responses",
            "hc_pixel8pro_a17": "Android 17 | com.bereal.ft | cached API responses",
        },
    },
}

import json
import os

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_human_ts_to_utc,
)

# Media file signatures. BeReal serves WebP from its CDN and keeps MP4 for videos.
_SIGNATURES = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF87a', 'GIF', 'image/gif', 'gif'),
    (b'GIF89a', 'GIF', 'image/gif', 'gif'),
)


def _sniff(data):
    for signature, label, mime, extension in _SIGNATURES:
        if data.startswith(signature):
            return label, mime, extension
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'WebP', 'image/webp', 'webp'
    if data[4:8] == b'ftyp':
        return 'MP4', 'video/mp4', 'mp4'
    return '', None, None


def _http_date(value):
    """Convert an HTTP date header (RFC 1123) to the UTC form the report expects."""
    if not value:
        return ''
    try:
        from email.utils import parsedate_to_datetime
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return ''
    if parsed is None:
        return ''
    return convert_human_ts_to_utc(parsed.strftime('%Y-%m-%d %H:%M:%S'))


def _parse_okhttp_metadata(path):
    """Parse an OkHttp DiskLruCache '.0' sidecar into url and response headers.

    The network cache writes the request URL on the first line, the method next, then the
    request headers, the status line and the response headers. The Coil image caches reuse
    the same file name pattern but start with two timestamps and carry no URL, so those are
    reported with an empty URL.
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            lines = handle.read().split('\n')
    except OSError:
        return {'url': '', 'headers': {}}

    url = ''
    if lines and lines[0].startswith('http'):
        url = lines[0].strip()

    headers = {}
    for line in lines:
        if ': ' in line and not line.startswith('http'):
            name, _, value = line.partition(': ')
            headers.setdefault(name.strip().lower(), value.strip())
    return {'url': url, 'headers': headers}


def _cache_pairs(files_found):
    """Yield (body_path, metadata) for each cached object.

    OkHttp/Coil store a '.0' metadata file and a '.1' body. Files without that suffix (the
    user's own video copies) are yielded with empty metadata so they are still recovered.
    """
    by_stem = {}
    singles = []
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        if file_found.endswith('.0'):
            by_stem.setdefault(file_found[:-2], {})['meta'] = file_found
        elif file_found.endswith('.1'):
            by_stem.setdefault(file_found[:-2], {})['body'] = file_found
        else:
            singles.append(file_found)

    for parts in by_stem.values():
        body = parts.get('body')
        if not body:
            continue
        metadata = _parse_okhttp_metadata(parts['meta']) if parts.get('meta') else {'url': '', 'headers': {}}
        yield body, metadata
    for path in singles:
        yield path, {'url': '', 'headers': {}}


def _iter_cached_json(files_found):
    """Yield (url, headers, parsed_json, body_path) for cached JSON responses."""
    for body, metadata in _cache_pairs(files_found):
        if not metadata['url']:
            continue
        try:
            with open(body, 'rb') as handle:
                raw = handle.read()
        except OSError:
            continue
        if raw[:1] not in (b'{', b'['):
            continue
        try:
            parsed = json.loads(raw)
        except ValueError:
            continue
        yield metadata['url'], metadata['headers'], parsed, body


@artifact_processor
def bereal_cached_media(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for body, metadata in _cache_pairs(files_found):
        try:
            with open(body, 'rb') as handle:
                head = handle.read(16)
        except OSError:
            continue
        label, mime, extension = _sniff(head)
        if not mime:
            continue  # JSON and other non-media cache bodies are handled elsewhere
        source_path = os.path.dirname(body)
        url = metadata['url']
        name = os.path.basename(url.split('?')[0]) if url else os.path.basename(body)
        if not os.path.splitext(name)[1] and extension:
            name = f'{name}.{extension}'
        media = check_in_media(body, name, force_type=mime, force_extension=extension) or ''
        cache_dir = os.path.basename(os.path.dirname(body))
        data_list.append((
            _http_date(metadata['headers'].get('date')),
            media,
            label,
            os.path.getsize(body),
            cache_dir,
            url,
            context.get_relative_path(body),
        ))

    data_headers = (
        ('Cached Response Date', 'datetime'),
        ('Media', 'media'),
        'Format',
        'Size (bytes)',
        'Cache',
        ('Source URL', 'url'),
        'Local Path',
    )
    return data_headers, data_list, source_path


@artifact_processor
def bereal_friends(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    seen = set()

    for url, headers, parsed, body in _iter_cached_json(files_found):
        if not isinstance(parsed, dict):
            continue
        entries = parsed.get('data')
        if not isinstance(entries, list):
            continue
        if 'relationships' not in url and 'recommendations' not in url and 'friend' not in url.lower():
            continue
        cached = _http_date(headers.get('date'))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            user_id = entry.get('id') or entry.get('userId') or ''
            username = entry.get('username', '')
            key = (user_id, username, url)
            if key in seen:
                continue
            seen.add(key)
            source_path = body
            data_list.append((
                cached,
                username,
                entry.get('fullname', ''),
                entry.get('status', ''),
                user_id,
                entry.get('hashedPhoneNumber', ''),
                url,
            ))

    data_headers = (
        ('Cached Response Date', 'datetime'),
        'User Name',
        'Full Name',
        'Status',
        'User ID',
        'Hashed Phone Number',
        ('Source Endpoint', 'url'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def bereal_cached_api(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for url, headers, parsed, body in _iter_cached_json(files_found):
        source_path = os.path.dirname(body)
        if isinstance(parsed, dict):
            shape = ', '.join(list(parsed)[:8])
            if isinstance(parsed.get('data'), list):
                shape = f'data[{len(parsed["data"])}]; ' + shape
        elif isinstance(parsed, list):
            shape = f'list[{len(parsed)}]'
        else:
            shape = type(parsed).__name__
        data_list.append((
            _http_date(headers.get('date')),
            url.split('?')[0],
            os.path.getsize(body),
            shape,
            url,
            context.get_relative_path(body),
        ))

    data_headers = (
        ('Cached Response Date', 'datetime'),
        'Endpoint',
        'Body Size (bytes)',
        'Body Summary',
        ('Full URL', 'url'),
        'Local Path',
    )
    return data_headers, data_list, source_path
