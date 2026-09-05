__artifacts_v2__ = {
    "get_discordChats": {
        "name": "discordChats",
        "description": "Parses Discord chat messages from the kv-storage key-value store",
        "author": "@abrignoni",
        "creation_date": "2023-09-18",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Discord Chats",
        "notes": "Reference: Discord Developer Documentation, 'Message Types (DEFAULT=0, CALL=3, USER_JOIN=7, REPLY=19)', "
                 "https://discord.com/developers/docs/resources/message. Each account's kv-storage/@account.<id>/a "
                 "database is read separately; Direction is Outgoing when the sender id equals the account id in that "
                 "folder name. Attachment renders the first attachment whose URL path (scheme, host and path, ignoring "
                 "the size parameters) equals the URL of an image entry in the same container's OkHttp response cache "
                 "(cache/http-cache, <hash>.0 metadata beside the <hash>.1 body), taking the largest cached copy; "
                 "Attachment Filename, Attachment URL and Attachment Proxy URL list every attachment as stored, joined "
                 "with semicolons. The cache is the same store the Discord Cached Messages artifact reads.",
        "paths": ('*/com.discord/files/kv-storage/*/a*',
                  '*/com.discord/cache/http-cache/[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f].[01]'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.discord vc 333012 | 7 rows",
            "pixel7a_a14": "Android 14 | com.discord vc 239015 | 47 rows",
            "samsungs20_a13": "Android 13 | com.discord vc 310011 | 1 row",
            "userb2_a13": "Android 13 | com.discord vc 255014 | 25 rows",
        },
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
    }
}

import json
import os
import re
import sqlite3
import sys

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_PACKAGE = 'com.discord'
_ENTRY = re.compile(r'^([0-9a-f]{32})\.([01])$')
_ACCOUNT = re.compile(r'@account\.(\d+)')
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png', 'png'),
    (b'GIF87a', 'image/gif', 'gif'),
    (b'GIF89a', 'image/gif', 'gif'),
)
# table mapping all non-printable characters to None; the stored JSON carries a leading length byte
_NOPRINT = {i: None for i in range(sys.maxunicode + 1) if not chr(i).isprintable()}


def _container_key(context, file_found):
    """A key shared by every file of one app container, across its storage-view spellings."""
    parts = context.get_relative_path(file_found).replace('\\', '/').split('/')
    if _PACKAGE in parts:
        parts = parts[:parts.index(_PACKAGE) + 1]
    return canonical_path('/'.join(parts))[0]


def _image_type(head):
    for magic, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return mime, extension
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'image/webp', 'webp'
    return '', ''


def _url_path(url):
    return str(url or '').split('?', 1)[0].split('#', 1)[0]


def _cached_images(context, container, files):
    """{URL path: (size, body path, mime, extension)} of the largest cached image per URL in one container."""
    images = {}
    for file_found in files:
        file_found = str(file_found)
        base = os.path.basename(file_found)
        match = _ENTRY.match(base)
        if not match or match.group(2) != '0' or _container_key(context, file_found) != container:
            continue
        body_path = file_found[:-1] + '1'
        try:
            with open(file_found, 'rb') as handle:
                lines = handle.read().decode('utf-8', 'replace').split('\n')
            size = os.path.getsize(body_path)
            with open(body_path, 'rb') as handle:
                head = handle.read(16)
        except OSError:
            continue
        if not lines or not lines[0].startswith(('http://', 'https://')):
            continue
        # skip gzip-encoded bodies: the header block follows the vary block, so search the lines
        if any(line.lower().startswith('content-encoding:') and 'gzip' in line.lower() for line in lines[3:60]):
            continue
        mime, extension = _image_type(head)
        if not mime:
            continue
        path = _url_path(lines[0])
        if path not in images or size > images[path][0]:
            images[path] = (size, body_path, mime, extension)
    return images


def _media(images, url, name):
    hit = images.get(_url_path(url))
    if not hit:
        return ''
    _size, body_path, mime, extension = hit
    return check_in_media(body_path, name, force_type=mime, force_extension=extension) or ''


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def get_discordChats(context):
    files = unique_files(context)
    databases = [str(f) for f in files if os.path.basename(str(f)) == 'a' and '/kv-storage/' in str(f).replace('\\', '/')
                 and not os.path.isdir(f)]
    data_list = []
    sources = []
    for source_path in databases:
        account_match = _ACCOUNT.search(source_path)
        account_id = account_match.group(1) if account_match else ''
        images = _cached_images(context, _container_key(context, source_path), files)
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            continue
        try:
            rows = db.execute('SELECT data FROM messages0').fetchall()
        except sqlite3.Error as error:
            logfunc(f'Discord kv-storage {context.get_relative_path(source_path)}: {error}')
            rows = []
        sources.append(source_path)
        for (blob,) in rows:
            try:
                data = json.loads(bytes(blob).decode('utf-8', 'replace').translate(_NOPRINT))
            except (ValueError, TypeError):
                continue
            message = data.get('message') if isinstance(data, dict) else None
            if not isinstance(message, dict):
                continue
            author = message.get('author') or {}
            sender_id = _text(author.get('id'))
            attachments = [a for a in message.get('attachments') or [] if isinstance(a, dict)]
            media = ''
            for attachment in attachments:
                for url in (attachment.get('proxy_url'), attachment.get('url')):
                    media = _media(images, url, f"{_text(data.get('id'))}_{_text(attachment.get('filename'))}")
                    if media:
                        break
                if media:
                    break
            if account_id and sender_id:
                direction = 'Outgoing' if sender_id == account_id else 'Incoming'
            else:
                direction = ''
            data_list.append((
                _text(message.get('timestamp')),
                _text(message.get('edited_timestamp')),
                direction,
                _text(author.get('username')),
                _text(message.get('content')),
                media,
                _text(data.get('channelId')),
                _text(data.get('id')),
                '; '.join(_text(a.get('filename')) for a in attachments),
                '; '.join(_text(a.get('url')) for a in attachments),
                '; '.join(_text(a.get('proxy_url')) for a in attachments),
                _text(message.get('mentions')),
                _text(message.get('mention_roles')),
                _text(message.get('pinned')),
                _text(author.get('avatar')),
                sender_id,
                account_id,
            ))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Edited Timestamp', 'datetime'),
        'Direction',
        'Username',
        'Content',
        ('Attachment', 'media'),
        'Channel ID',
        'ID',
        'Attachment Filename',
        'Attachment URL',
        'Attachment Proxy URL',
        'Mentions',
        'Mention Roles',
        'Pinned',
        'Avatar',
        'Sender ID',
        'Account ID',
    )
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
