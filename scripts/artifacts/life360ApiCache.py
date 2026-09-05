__artifacts_v2__ = {
    "life360CacheMemberHistory": {
        "name": "Life360 - Member Location History (API cache)",
        "description": "Location history records of circle members, read from the JSON responses to the "
                       "app's members/<member id>/history API calls that its OkHttp response cache holds. "
                       "One row per distinct record; a record returned by several cached responses is "
                       "reported once with the number of copies.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the app's OkHttp response caches under cache/ (http_cache holds these "
                 "responses on the tested images). Each cache entry is a pair of files named by the MD5 "
                 "of the URL: <hash>.0 holds the URL, the status line and the response headers, <hash>.1 "
                 "the body, gzip-compressed when the Content-Encoding header says so (OkHttp Cache.kt "
                 "Entry.writeTo at release parent-5.5.0, the same layout since 2.x). The URL names the "
                 "circle and the member; the body is a locations list whose timestamp, startTimestamp, "
                 "endTimestamp and since values are Unix seconds and are rendered in UTC. Latitude, "
                 "longitude, accuracy, speed, battery, and the charge, inTransit, isDriving, wifiState, "
                 "userActivity, driveSDKStatus and algorithm values are reported as stored; Life360 is "
                 "closed source and their meanings are not documented. Member Name is resolved from the "
                 "circles/<id>/members and users/me responses in the same cache and is blank when no cached "
                 "response names the member. The same record is returned by many cached history responses "
                 "(the app fetches the history repeatedly with a moving time parameter), so rows are "
                 "de-duplicated on member, timestamp, coordinates and the start and end timestamps; "
                 "Cached Copies counts the responses holding the record and First Cached is the earliest "
                 "OkHttp-Received-Millis among them. The device's own location events are reported by "
                 "the Life360 Locations artifacts from L360EventStore.db; this artifact adds the history "
                 "the app fetched for circle members.",
        "paths": ('*/com.life360.android.safetymapd/cache/*/journal',
                  '*/com.life360.android.safetymapd/cache/*/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]'),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "life360CacheEmergencyContacts": {
        "name": "Life360 - Emergency Contacts (API cache)",
        "description": "Emergency contacts of a circle, read from the JSON responses to the app's "
                       "circles/<circle id>/emergencyContacts API calls held in its OkHttp response cache.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the same OkHttp response caches as the Member Location History artifact. One "
                 "row per distinct contact id per circle; the Cached time is the OkHttp-Received-Millis "
                 "header of the response that held it. Phone Numbers joins each phone with its type in "
                 "parentheses where the type is stored. Accepted is reported as stored. No database the "
                 "other Life360 artifacts read holds these contacts.",
        "paths": ('*/com.life360.android.safetymapd/cache/*/journal',
                  '*/com.life360.android.safetymapd/cache/*/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]'),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    },
    "life360CacheEntries": {
        "name": "Life360 - API Cache Entries",
        "description": "Index of the exchanges held in the Life360 app's OkHttp response caches: the URL "
                       "requested, when it was sent and received, the status, the content type and size, "
                       "and the cached image where the body is one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "One row per <hash>.0 metadata file in each DiskLruCache directory under the app's cache/ "
                 "folder whose entries start with a URL (http_cache, l360_http_cache, core_http_cache, "
                 "picasso-cache, the LaunchDarkly and Statsig SDK caches on the tested images). Sent and "
                 "Received are the OkHttp-Sent-Millis and OkHttp-Received-Millis headers OkHttp writes into "
                 "the entry (Unix milliseconds; written since OkHttp 3.4.0, absent from entries of older "
                 "releases). OkHttp caches GET responses only (Cache.kt put, release parent-5.5.0), so no "
                 "method column is reported. The URLs themselves carry request parameters the app sent, "
                 "such as a phone number passed to users/lookup, an invite code passed to code/<code>, and "
                 "the coordinates passed to nearbyplaces/<lat>/<lon>. Journal State is the last CLEAN, "
                 "DIRTY or REMOVE line for the entry's key in the directory's journal, blank when the key "
                 "is not in the journal. Media renders the body when its bytes are a JPEG, PNG, GIF or WebP "
                 "image and the response is not compressed; other bodies are not decoded here.",
        "paths": ('*/com.life360.android.safetymapd/cache/*/journal',
                  '*/com.life360.android.safetymapd/cache/*/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]'),
        "output_types": "standard",
        "artifact_icon": "list",
    },
}

import gzip
import json
import os
import re
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_PACKAGE = 'com.life360.android.safetymapd'
_ENTRY = re.compile(r'^([0-9a-f]{32})\.([01])$')
_HISTORY = re.compile(r'/v3/circles/([0-9a-f-]{36})/members/([0-9a-f-]{36})/history(?:\?|$)')
_MEMBERS = re.compile(r'/v4/circles/([0-9a-f-]{36})/members$')
_CONTACTS = re.compile(r'/v3/circles/([0-9a-f-]{36})/emergencyContacts$')
_ME = re.compile(r'/v3/users/me$')
# OkHttp writes its two timing pseudo-headers with the platform prefix: "OkHttp" for the
# library an app bundles (Platform.kt), "X-Android" for the copy inside the Android framework
# (external/okhttp android/src/main/java/com/squareup/okhttp/internal/Platform.java).
_SENT = ('okhttp-sent-millis', 'x-android-sent-millis')
_RECEIVED = ('okhttp-received-millis', 'x-android-received-millis')
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png', 'png'),
    (b'GIF87a', 'image/gif', 'gif'),
    (b'GIF89a', 'image/gif', 'gif'),
)


def _utc_seconds(value):
    """UTC datetime from a Unix-seconds value stored as int, float or digit string."""
    try:
        return datetime.fromtimestamp(float(value), timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _utc_millis(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _first_header(headers, names):
    for name in names:
        if name in headers:
            return headers[name]
    return ''


def _read_entry(path):
    """(url, status line, headers) from an OkHttp cache <hash>.0 file, or None.

    Layout (Cache.kt Entry.writeTo, parent-5.5.0): URL, request method, vary header count and
    lines, status line, response header count and lines, then the TLS block for https URLs.
    """
    try:
        with open(path, 'rb') as handle:
            lines = handle.read().decode('utf-8', 'replace').split('\n')
    except OSError:
        return None
    if len(lines) < 5 or not lines[0].startswith(('http://', 'https://')):
        return None
    try:
        index = 3 + int(lines[2])
        status = lines[index]
        count = int(lines[index + 1])
        header_lines = lines[index + 2:index + 2 + count]
    except (ValueError, IndexError):
        return None
    headers = {}
    for line in header_lines:
        name, sep, value = line.partition(':')
        if sep:
            headers.setdefault(name.strip().lower(), value.strip())
    return lines[0], status, headers


def _read_journal(path):
    """{entry key: last CLEAN/DIRTY/REMOVE state} from a libcore DiskLruCache journal, or None."""
    try:
        with open(path, 'rb') as handle:
            lines = handle.read().decode('utf-8', 'replace').split('\n')
    except OSError:
        return None
    if lines[:2] != ['libcore.io.DiskLruCache', '1']:
        return None
    states = {}
    for line in lines[5:]:
        parts = line.split(' ')
        if len(parts) >= 2 and parts[0] in ('CLEAN', 'DIRTY', 'REMOVE'):
            states[parts[1]] = parts[0]
    return states


def _cache_label(context, folder):
    """The cache folder relative to the package directory, e.g. cache/http_cache."""
    parts = context.get_relative_path(folder).replace('\\', '/').split('/')
    if _PACKAGE in parts:
        return '/'.join(parts[parts.index(_PACKAGE) + 1:])
    return parts[-1]


def _caches(context):
    """{cache folder: {'journal': path or None, 'entries': {key: {'0': path, '1': path}}}}.

    Folders are keyed by their storage-view canonical path, so a journal and its entries staged
    from two spellings of one folder (data/data, data/user/0, data_mirror) pair up.
    """
    caches = {}
    by_key = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        folder = os.path.dirname(file_found)
        match = _ENTRY.match(base)
        if base != 'journal' and not match:
            continue
        key = canonical_path(context.get_relative_path(folder))[0]
        folder = by_key.setdefault(key, folder)
        cache = caches.setdefault(folder, {'journal': None, 'entries': {}})
        if base == 'journal':
            cache['journal'] = file_found
        else:
            cache['entries'].setdefault(match.group(1), {})[match.group(2)] = file_found
    return caches


def _exchanges(context):
    """Every parsed cache entry as a dict, plus the number of <hash>.0 files that did not parse."""
    exchanges = []
    skipped = 0
    for folder, cache in sorted(_caches(context).items()):
        states = _read_journal(cache['journal']) if cache['journal'] else None
        label = _cache_label(context, folder)
        for key, files in sorted(cache['entries'].items()):
            if '0' not in files:
                continue
            parsed = _read_entry(files['0'])
            if parsed is None:
                skipped += 1
                continue
            url, status, headers = parsed
            exchanges.append({
                'cache': label, 'key': key, 'url': url, 'status': status, 'headers': headers,
                'sent': _utc_millis(_first_header(headers, _SENT)),
                'received': _utc_millis(_first_header(headers, _RECEIVED)),
                'received_raw': _first_header(headers, _RECEIVED),
                'files': files,
                'state': states.get(key, '') if states is not None else '',
            })
    if skipped:
        logfunc(f'Life360 API cache: {skipped} .0 files did not start with a URL and were skipped')
    return exchanges


def _body(exchange):
    """The response body bytes, gunzipped when the response says gzip, or None."""
    path = exchange['files'].get('1')
    if not path:
        return None
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError:
        return None
    if exchange['headers'].get('content-encoding', '').lower() == 'gzip':
        try:
            data = gzip.decompress(data)
        except (OSError, EOFError, ValueError):
            return None
    return data


def _json_body(exchange):
    data = _body(exchange)
    if data is None:
        return None
    try:
        return json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return None


def _member_names(exchanges):
    """{member id: 'First Last'} from the circle members and users/me responses."""
    names = {}
    for exchange in exchanges:
        url = exchange['url'].split('?')[0]
        if _MEMBERS.search(url):
            payload = _json_body(exchange)
            members = payload.get('members', []) if isinstance(payload, dict) else []
        elif _ME.search(url):
            payload = _json_body(exchange)
            members = [payload] if isinstance(payload, dict) else []
        else:
            continue
        for member in members:
            if isinstance(member, dict) and member.get('id'):
                name = ' '.join(str(member.get(k) or '') for k in ('firstName', 'lastName')).strip()
                if name:
                    names.setdefault(member['id'], name)
    return names


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def life360CacheMemberHistory(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        ('Start Timestamp', 'datetime'),
        ('End Timestamp', 'datetime'),
        ('Since', 'datetime'),
        'Member Name',
        'Member ID',
        'Circle ID',
        'Latitude',
        'Longitude',
        'Accuracy (as stored)',
        'Address 1',
        'Address 2',
        'Short Address',
        'Place Name',
        'Speed (as stored)',
        'User Activity (as stored)',
        'In Transit (as stored)',
        'Is Driving (as stored)',
        'Battery',
        'Charge (as stored)',
        'Wi-Fi State (as stored)',
        'Drive SDK Status (as stored)',
        'Algorithm (as stored)',
        'Trip ID',
        ('First Cached', 'datetime'),
        'Cached Copies',
        'Source File',
    )
    exchanges = _exchanges(context)
    names = _member_names(exchanges)
    records = {}
    sources = []
    responses = 0
    for exchange in exchanges:
        match = _HISTORY.search(exchange['url'])
        if not match:
            continue
        payload = _json_body(exchange)
        if not isinstance(payload, dict):
            continue
        responses += 1
        sources.append(exchange['files']['0'])
        circle_id, member_id = match.group(1), match.group(2)
        for loc in payload.get('locations', []):
            if not isinstance(loc, dict):
                continue
            key = (member_id, _text(loc.get('timestamp')), _text(loc.get('latitude')),
                   _text(loc.get('longitude')), _text(loc.get('startTimestamp')),
                   _text(loc.get('endTimestamp')))
            record = records.get(key)
            received = exchange['received_raw']
            if record is None:
                records[key] = {
                    'loc': loc, 'circle': circle_id, 'member': member_id, 'copies': 1,
                    'received': received, 'source': exchange['files']['0'],
                }
            else:
                record['copies'] += 1
                if received and (not record['received'] or int(received) < int(record['received'])):
                    record['received'] = received
                    record['source'] = exchange['files']['0']
    data_list = []
    for key in sorted(records, key=lambda k: (k[0], k[1])):
        record = records[key]
        loc = record['loc']
        data_list.append((
            _utc_seconds(loc.get('timestamp')),
            _utc_seconds(loc.get('startTimestamp')),
            _utc_seconds(loc.get('endTimestamp')),
            _utc_seconds(loc.get('since')),
            names.get(record['member'], ''),
            record['member'],
            record['circle'],
            _text(loc.get('latitude')),
            _text(loc.get('longitude')),
            _text(loc.get('accuracy')),
            _text(loc.get('address1')),
            _text(loc.get('address2')),
            _text(loc.get('shortAddress')),
            _text(loc.get('name')),
            _text(loc.get('speed')),
            _text(loc.get('userActivity')),
            _text(loc.get('inTransit')),
            _text(loc.get('isDriving')),
            _text(loc.get('battery')),
            _text(loc.get('charge')),
            _text(loc.get('wifiState')),
            _text(loc.get('driveSDKStatus')),
            _text(loc.get('algorithm')),
            _text(loc.get('tripId')),
            _utc_millis(record['received']),
            record['copies'],
            context.get_relative_path(record['source']),
        ))
    if responses:
        logfunc(f'Life360 API cache: {len(data_list)} distinct location records from {responses} history responses')
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def life360CacheEmergencyContacts(context):
    data_headers = (
        ('Cached', 'datetime'),
        'First Name',
        'Last Name',
        'Phone Numbers',
        'Emails',
        'Accepted (as stored)',
        'Contact ID',
        'Owner ID',
        'Circle ID',
        'Avatar URL',
        'URL (as stored)',
        'Source File',
    )
    data_list = []
    sources = []
    seen = set()
    for exchange in _exchanges(context):
        match = _CONTACTS.search(exchange['url'].split('?')[0])
        if not match:
            continue
        payload = _json_body(exchange)
        if not isinstance(payload, dict):
            continue
        sources.append(exchange['files']['0'])
        for contact in payload.get('emergencyContacts', []):
            if not isinstance(contact, dict):
                continue
            ident = (match.group(1), _text(contact.get('id')))
            if ident in seen:
                continue
            seen.add(ident)
            phones = []
            for phone in contact.get('phoneNumbers') or []:
                if isinstance(phone, dict):
                    number = _text(phone.get('phone'))
                    kind = _text(phone.get('type'))
                    phones.append(f'{number} ({kind})' if kind else number)
                else:
                    phones.append(_text(phone))
            emails = []
            for email in contact.get('emails') or []:
                if isinstance(email, dict):
                    emails.append(_text(email.get('email') or json.dumps(email)))
                else:
                    emails.append(_text(email))
            data_list.append((
                exchange['received'],
                _text(contact.get('firstName')),
                _text(contact.get('lastName')),
                '; '.join(p for p in phones if p),
                '; '.join(e for e in emails if e),
                _text(contact.get('accepted')),
                _text(contact.get('id')),
                _text(contact.get('ownerId')),
                match.group(1),
                _text(contact.get('avatar')),
                _text(contact.get('url')),
                context.get_relative_path(exchange['files']['0']),
            ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


def _image_type(head):
    """(mime, extension) for image bytes, or ('', '')."""
    for magic, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return mime, extension
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'image/webp', 'webp'
    return '', ''


@artifact_processor
def life360CacheEntries(context):
    data_headers = (
        ('Sent', 'datetime'),
        ('Received', 'datetime'),
        'Cache',
        'URL',
        'Status Line (as stored)',
        'Content Type',
        'Content Encoding',
        'Body Bytes',
        'Date (as stored)',
        ('Media', 'media'),
        'Journal State (as stored)',
        'Entry Key',
        'Source File',
    )
    data_list = []
    sources = []
    for exchange in _exchanges(context):
        headers = exchange['headers']
        body_path = exchange['files'].get('1')
        size = ''
        media = ''
        if body_path:
            try:
                size = os.path.getsize(body_path)
            except OSError:
                size = ''
            if size and headers.get('content-encoding', '').lower() != 'gzip':
                try:
                    with open(body_path, 'rb') as handle:
                        head = handle.read(16)
                except OSError:
                    head = b''
                mime, extension = _image_type(head)
                if mime:
                    media = check_in_media(body_path, f"{exchange['key']}.1",
                                           force_type=mime, force_extension=extension) or ''
        sources.append(exchange['files']['0'])
        data_list.append((
            exchange['sent'],
            exchange['received'],
            exchange['cache'],
            exchange['url'],
            exchange['status'],
            headers.get('content-type', ''),
            headers.get('content-encoding', ''),
            size,
            headers.get('date', ''),
            media,
            exchange['state'],
            exchange['key'],
            context.get_relative_path(exchange['files']['0']),
        ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
