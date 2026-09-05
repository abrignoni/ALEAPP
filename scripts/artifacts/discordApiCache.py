__artifacts_v2__ = {
    "discordCacheMessages": {
        "name": "Discord - Cached Messages (API cache)",
        "description": "Discord messages read from the channel message pages (channels/<channel id>/messages "
                       "responses) held in the app's OkHttp response cache, with the cached attachment image "
                       "where the cache holds one. One row per distinct message id.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Discord Chats",
        "notes": "Read from cache/http-cache, an OkHttp DiskLruCache: <hash>.0 holds the URL, status line and "
                 "response headers, <hash>.1 the body, gzip-compressed when the Content-Encoding header says so "
                 "(OkHttp Cache.kt Entry.writeTo at release parent-5.5.0). Each channels/<id>/messages response is "
                 "a JSON list of message objects in the shape the Discord developer documentation describes "
                 "(https://discord.com/developers/docs/resources/message); the same message id can appear in "
                 "several cached pages and is reported once with the number of pages holding it. Direction is "
                 "Outgoing when the author id equals an account id taken from the kv-storage/@account.<id> folder "
                 "names in the same app container, Incoming for any other author, and blank when no account folder "
                 "was found. Attachment renders the first attachment whose URL path (scheme, host and path, "
                 "ignoring the size parameters) equals the URL of a cached image entry, taking the largest cached "
                 "copy; Attachment Filenames and Attachment URLs list every attachment as stored. Message Type is "
                 "the type value as stored (0 DEFAULT, 3 CALL, 7 USER_JOIN, 19 REPLY per the same documentation). "
                 "Call Ended and Call Participants come from the call object of call messages. Also In kv-storage is "
                 "Yes when the same message id is in the messages0 table of the container's kv-storage database, "
                 "which the Discord Chats artifact reads.",
        "paths": ('*/com.discord/cache/http-cache/journal',
                  '*/com.discord/cache/http-cache/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]',
                  '*/com.discord/files/kv-storage/@account.*/a*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Username",
                "mediaColumn": "Attachment"
            }
        },
    },
    "discordCacheProfiles": {
        "name": "Discord - Cached User Profiles (API cache)",
        "description": "User profiles the app fetched (users/<user id>/profile responses) held in its OkHttp "
                       "response cache: username, display name, bio, connected accounts and mutual servers as "
                       "stored. One row per distinct user id.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Discord Chats",
        "notes": "Read from the same cache as the Cached Messages artifact. The app requests a profile when a user "
                 "is looked at; the cache holds the response, so a row records that the profile was fetched, at "
                 "the Cached time, not who the account holder is. Values are reported as stored; Connected "
                 "Accounts joins each account's type and name. A user fetched more than once is reported once, "
                 "from the earliest cached response, with the number of cached copies.",
        "paths": ('*/com.discord/cache/http-cache/journal',
                  '*/com.discord/cache/http-cache/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "discordCacheEntries": {
        "name": "Discord - API Cache Entries",
        "description": "Index of the exchanges held in the Discord app's OkHttp response cache: the URL requested, "
                       "when it was sent and received, the status, the content type and size, and the cached "
                       "image where the body is one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Discord Chats",
        "notes": "One row per <hash>.0 metadata file in cache/http-cache whose first line is a URL. Sent and "
                 "Received are the OkHttp-Sent-Millis and OkHttp-Received-Millis headers OkHttp writes into the "
                 "entry (Unix milliseconds; written since OkHttp 3.4.0). OkHttp caches GET responses only "
                 "(Cache.kt put, release parent-5.5.0), so no method column is reported. Media renders the body "
                 "when its bytes are a JPEG, PNG, GIF or WebP image and the response is not compressed: the "
                 "attachment images, avatars, server icons and stickers the app displayed. Journal State is the "
                 "last CLEAN, DIRTY or REMOVE line for the entry's key in the cache's journal, blank when the key "
                 "is not in the journal. This is the Android counterpart of the iOS Discord Cache artifact.",
        "paths": ('*/com.discord/cache/http-cache/journal',
                  '*/com.discord/cache/http-cache/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]'),
        "output_types": "standard",
        "artifact_icon": "list",
    },
}

import gzip
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_PACKAGE = 'com.discord'
_ENTRY = re.compile(r'^([0-9a-f]{32})\.([01])$')
_MESSAGES = re.compile(r'/api/v\d+/channels/(\d+)/messages(?:\?|$)')
_PROFILE = re.compile(r'/api/v\d+/users/(\d+)/profile(?:\?|$)')
_ACCOUNT = re.compile(r'@account\.(\d+)')
_SENT = ('okhttp-sent-millis', 'x-android-sent-millis')
_RECEIVED = ('okhttp-received-millis', 'x-android-received-millis')
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png', 'png'),
    (b'GIF87a', 'image/gif', 'gif'),
    (b'GIF89a', 'image/gif', 'gif'),
)
_NOPRINT = {i: None for i in range(sys.maxunicode + 1) if not chr(i).isprintable()}


def _utc_millis(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _iso(value):
    """UTC datetime from Discord's ISO 8601 timestamps ('2024-02-08T16:44:47.780000+00:00'), else ''."""
    if not value:
        return ''
    text = str(value).replace('Z', '+00:00')
    match = re.match(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?([+-]\d\d:\d\d)$', text)
    if not match:
        return ''
    fraction = (match.group(2) or '.0')[1:]
    text = f'{match.group(1)}.{fraction[:6].ljust(6, "0")}{match.group(3)}'
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return ''


def _first_header(headers, names):
    for name in names:
        if name in headers:
            return headers[name]
    return ''


def _read_entry(path):
    """(url, status line, headers) from an OkHttp cache <hash>.0 file, or None."""
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


def _container_key(context, file_found):
    """A key shared by every file of one app container, across its storage-view spellings."""
    parts = context.get_relative_path(file_found).replace('\\', '/').split('/')
    if _PACKAGE in parts:
        parts = parts[:parts.index(_PACKAGE) + 1]
    return canonical_path('/'.join(parts))[0]


def _containers(context):
    """{container key: {'journal': path, 'entries': {key: {'0': path, '1': path}}, 'kv': [a files]}}."""
    containers = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        container = containers.setdefault(_container_key(context, file_found),
                                          {'journal': None, 'entries': {}, 'kv': []})
        match = _ENTRY.match(base)
        if '/kv-storage/' in file_found.replace('\\', '/'):
            if base == 'a':
                container['kv'].append(file_found)
        elif base == 'journal':
            container['journal'] = file_found
        elif match:
            container['entries'].setdefault(match.group(1), {})[match.group(2)] = file_found
    return containers


def _exchanges(container):
    """Every parsed cache entry of one container as a dict, plus the count of .0 files that did not parse."""
    states = _read_journal(container['journal']) if container['journal'] else None
    exchanges = []
    skipped = 0
    for key, files in sorted(container['entries'].items()):
        if '0' not in files:
            continue
        parsed = _read_entry(files['0'])
        if parsed is None:
            skipped += 1
            continue
        url, status, headers = parsed
        received = _first_header(headers, _RECEIVED)
        exchanges.append({
            'key': key, 'url': url, 'status': status, 'headers': headers, 'files': files,
            'sent': _utc_millis(_first_header(headers, _SENT)), 'received': _utc_millis(received),
            'received_raw': received, 'state': states.get(key, '') if states is not None else '',
        })
    return exchanges, skipped


def _body(exchange):
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


def _image_type(head):
    for magic, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return mime, extension
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'image/webp', 'webp'
    return '', ''


def _url_path(url):
    return str(url or '').split('?', 1)[0].split('#', 1)[0]


def _image_bodies(exchanges):
    """{URL path: (size, body path, mime, extension)} of the largest cached image per URL path."""
    images = {}
    for exchange in exchanges:
        body_path = exchange['files'].get('1')
        if not body_path or exchange['headers'].get('content-encoding', '').lower() == 'gzip':
            continue
        try:
            size = os.path.getsize(body_path)
            with open(body_path, 'rb') as handle:
                head = handle.read(16)
        except OSError:
            continue
        mime, extension = _image_type(head)
        if not mime:
            continue
        path = _url_path(exchange['url'])
        if path not in images or size > images[path][0]:
            images[path] = (size, body_path, mime, extension)
    return images


def _media(images, url, name):
    """Media reference for the cached image whose URL path equals that of url, else ''."""
    hit = images.get(_url_path(url))
    if not hit:
        return ''
    _size, body_path, mime, extension = hit
    return check_in_media(body_path, name, force_type=mime, force_extension=extension) or ''


def _kv_message_ids(kv_files):
    """Message ids held in the messages0 table of each kv-storage 'a' database."""
    ids = set()
    for path in kv_files:
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('SELECT data FROM messages0').fetchall()
        except sqlite3.Error:
            rows = []
        for (blob,) in rows:
            try:
                data = json.loads(bytes(blob).decode('utf-8', 'replace').translate(_NOPRINT))
            except (ValueError, TypeError):
                continue
            message = data.get('message', {}) if isinstance(data, dict) else {}
            if isinstance(message, dict) and message.get('id'):
                ids.add(str(message['id']))
        db.close()
    return ids


def _account_ids(kv_files):
    return {m.group(1) for path in kv_files for m in [_ACCOUNT.search(str(path))] if m}


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def discordCacheMessages(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        ('Edited Timestamp', 'datetime'),
        'Direction',
        'Username',
        'Global Name',
        'Content',
        ('Attachment', 'media'),
        'Attachment Filenames',
        'Attachment URLs',
        'Message Type (as stored)',
        'Channel ID',
        'Message ID',
        'Sender ID',
        'Reply To Message ID',
        'Mentions',
        ('Call Ended', 'datetime'),
        'Call Participants',
        'Pinned',
        'Also In kv-storage',
        'Account IDs',
        'Cached Pages',
        'Source File',
    )
    data_list = []
    sources = []
    total_skipped = 0
    for _key, container in sorted(_containers(context).items()):
        exchanges, skipped = _exchanges(container)
        total_skipped += skipped
        images = _image_bodies(exchanges)
        accounts = _account_ids(container['kv'])
        kv_ids = _kv_message_ids(container['kv'])
        messages = {}
        for exchange in exchanges:
            if not _MESSAGES.search(exchange['url']):
                continue
            payload = _json_body(exchange)
            if not isinstance(payload, list):
                continue
            sources.append(exchange['files']['0'])
            for message in payload:
                if not isinstance(message, dict) or not message.get('id'):
                    continue
                record = messages.get(str(message['id']))
                if record is None:
                    messages[str(message['id'])] = {'message': message, 'pages': 1, 'source': exchange['files']['0']}
                else:
                    record['pages'] += 1
        for message_id, record in sorted(messages.items(), key=lambda item: _text(item[1]['message'].get('timestamp'))):
            message = record['message']
            author = message.get('author') or {}
            sender = _text(author.get('id'))
            attachments = [a for a in message.get('attachments') or [] if isinstance(a, dict)]
            media = ''
            for attachment in attachments:
                for url in (attachment.get('proxy_url'), attachment.get('url')):
                    media = _media(images, url, f"{message_id}_{_text(attachment.get('filename'))}")
                    if media:
                        break
                if media:
                    break
            call = message.get('call') or {}
            reference = message.get('message_reference') or {}
            if accounts and sender:
                direction = 'Outgoing' if sender in accounts else 'Incoming'
            else:
                direction = ''
            data_list.append((
                _iso(message.get('timestamp')),
                _iso(message.get('edited_timestamp')),
                direction,
                _text(author.get('username')),
                _text(author.get('global_name')),
                _text(message.get('content')),
                media,
                '; '.join(_text(a.get('filename')) for a in attachments),
                '; '.join(_text(a.get('url')) for a in attachments),
                _text(message.get('type')),
                _text(message.get('channel_id')),
                message_id,
                sender,
                _text(reference.get('message_id')),
                '; '.join(_text(m.get('username')) for m in message.get('mentions') or [] if isinstance(m, dict)),
                _iso(call.get('ended_timestamp')) if isinstance(call, dict) else '',
                '; '.join(_text(p) for p in call.get('participants') or []) if isinstance(call, dict) else '',
                'Yes' if message.get('pinned') else '',
                'Yes' if message_id in kv_ids else '',
                ', '.join(sorted(accounts)),
                record['pages'],
                context.get_relative_path(record['source']),
            ))
    if total_skipped:
        logfunc(f'Discord API cache: {total_skipped} .0 files did not start with a URL and were skipped')
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def discordCacheProfiles(context):
    data_headers = (
        ('Cached', 'datetime'),
        'User ID',
        'Username',
        'Global Name',
        'Legacy Username',
        'Bio',
        'Pronouns',
        'Connected Accounts',
        'Mutual Server IDs',
        ('Premium Since', 'datetime'),
        'Cached Copies',
        'Source File',
    )
    data_list = []
    sources = []
    for _key, container in sorted(_containers(context).items()):
        exchanges, _skipped = _exchanges(container)
        profiles = {}
        for exchange in exchanges:
            match = _PROFILE.search(exchange['url'])
            if not match:
                continue
            payload = _json_body(exchange)
            if not isinstance(payload, dict):
                continue
            sources.append(exchange['files']['0'])
            record = profiles.get(match.group(1))
            received = exchange['received_raw']
            if record is None:
                profiles[match.group(1)] = {'payload': payload, 'copies': 1, 'received': received,
                                            'source': exchange['files']['0']}
            else:
                record['copies'] += 1
                if received and (not record['received'] or int(received) < int(record['received'])):
                    record.update(payload=payload, received=received, source=exchange['files']['0'])
        for user_id, record in sorted(profiles.items()):
            payload = record['payload']
            user = payload.get('user') or {}
            profile = payload.get('user_profile') or {}
            connected = payload.get('connected_accounts') or []
            data_list.append((
                _utc_millis(record['received']),
                user_id,
                _text(user.get('username')),
                _text(user.get('global_name')),
                _text(payload.get('legacy_username')),
                _text(profile.get('bio') or user.get('bio')),
                _text(profile.get('pronouns')),
                '; '.join(f"{_text(c.get('type'))}: {_text(c.get('name'))}" for c in connected if isinstance(c, dict)),
                '; '.join(_text(g.get('id')) for g in payload.get('mutual_guilds') or [] if isinstance(g, dict)),
                _iso(payload.get('premium_since')),
                record['copies'],
                context.get_relative_path(record['source']),
            ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def discordCacheEntries(context):
    data_headers = (
        ('Sent', 'datetime'),
        ('Received', 'datetime'),
        'URL',
        'Status Line (as stored)',
        'Content Type',
        'Content Encoding',
        'Body Bytes',
        ('Media', 'media'),
        'Journal State (as stored)',
        'Entry Key',
        'Source File',
    )
    data_list = []
    sources = []
    for _key, container in sorted(_containers(context).items()):
        exchanges, _skipped = _exchanges(container)
        for exchange in exchanges:
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
                exchange['url'],
                exchange['status'],
                headers.get('content-type', ''),
                headers.get('content-encoding', ''),
                size,
                media,
                exchange['state'],
                exchange['key'],
                context.get_relative_path(exchange['files']['0']),
            ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
