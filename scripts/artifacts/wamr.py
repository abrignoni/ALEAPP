__artifacts_v2__ = {
    "wamr_notifications": {
        "name": "WAMR - Captured Notifications",
        "description": "Copies of other apps' notifications that the WAMR notification recovery app "
                       "saved in its notifs.db, one table per app it watched.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "WAMR (com.drilens.wamr) is a third-party app that keeps what other apps' notifications "
            "showed. These rows are WAMR's copies, not the other app's own records. Class and line "
            "references are to the WAMR 2.4.1 APK (version code 74, base.apk SHA-256 "
            "05a714a7beae3ebf33fe5d512a29b8c352d2bd277ae3baf6e1bddd854c65fe43) decompiled with jadx "
            "1.5.6; the classes are obfuscated, in defpackage unless named in full. Reads every "
            "app_<package> table of notifs.db (l91.java:41 and 44). A write-ahead log beside the "
            "database is applied; a database with no log beside it is read alone. Captured is the "
            "time column, which WAMR sets to the device clock when it handles the notification, not a "
            "time the notification carries (com/drilens/wamr/NotificationListener.java:155 and 200), "
            "written as yyyy-MM-dd HH:mm:ss_SSS in UTC (l91.java:27-29); a value that does not parse "
            "is left blank. App is the app column, the posting app's package name "
            "(NotificationListener.java:154 and 190). Title is built from the notification's title and big "
            "title fields, and Content from its text, big text and text lines "
            "(NotificationListener.java:97-150). Subtext is its sub text. When a notification has no "
            "title or no content WAMR stores the word null (NotificationListener.java:191-198); that "
            "stored word is shown here as a blank, so a notification whose text was the word null is "
            "also blank. WAMR skips a notification whose title and content match its newest row for "
            "that app within 2 seconds (NotificationListener.java:187), so not every notification has "
            "a row. WhatsApp and GBWhatsApp notifications are not stored here; they go to "
            "WAMR - WhatsApp Chats (NotificationListener.java:93). Only apps in WAMR's monitored list "
            "are captured (NotificationListener.java:89-92); WAMR - Monitored Apps lists them."),
        "paths": ('*/com.drilens.wamr/databases/notifs.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
    },
    "wamr_whatsapp_chats": {
        "name": "WAMR - WhatsApp Chats",
        "description": "WhatsApp messages the WAMR notification recovery app rebuilt from WhatsApp "
                       "notifications and saved in its textmess.db, one table per chat.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "Rows are WAMR's copies of what WhatsApp or GBWhatsApp notifications showed, not "
            "WhatsApp's own records. Class and line references are as in WAMR - Captured "
            "Notifications. Reads every chat_ table of textmess.db. Chat is the author column: WAMR "
            "fills it with the notification's title after removing direction marks, and for a group "
            "the part naming the group (NotificationListener.java:210-335, 631 and 644), so it names "
            "the chat, not the sender. In a group the sender is part of Content, written as the "
            "sender, a colon and the text (NotificationListener.java:322-325). WAMR names a chat's "
            "table chat_ followed by the chat name, with every character other than an ASCII letter "
            "or digit written as four hex digits (i31.java:49-58). That encoding cannot be reversed, "
            "since digits are kept as they are, so Chat Table is shown as stored and is not decoded. "
            "Captured is received_at, which WAMR sets to the device clock when it handles the "
            "notification (fz1.java:13-16, NotificationListener.java:254, 289 and 333), written as "
            "yyyy-MM-dd HH:mm:ss_SSS in UTC (NotificationListener.java:546, 585-586 and 633); several lines from one "
            "notification can share one time, and a value that does not parse is left blank. Marked "
            "Deleted is the deleted column. WAMR sets it to 1 on the newest row of a chat when a "
            "later notification for that chat reads as WhatsApp's This message was deleted text in "
            "the device language (NotificationListener.java:497-538). It does not record which "
            "message WhatsApp deleted. The WAMR user can also set or clear it, delete a row, or delete "
            "a chat's table from the app (jz1.java:113 and 135-160). This was read in the code; no row in the "
            "test data had it set. Row ID is _id."),
        "paths": ('*/com.drilens.wamr/databases/textmess.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "wamr_media": {
        "name": "WAMR - Recovered Media",
        "description": "Copies of WhatsApp media files that the WAMR notification recovery app made "
                       "in its external files folder, with the media.db row for each.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "Class and line references are as in WAMR - Captured Notifications. WAMR copies WhatsApp "
            "media files to Android/data/com.drilens.wamr/files/WAMR/<folder>/ and records each copy "
            "in the MediaMessages table of media.db (y21.java:195-209, c82.java:140-155, "
            "i31.java:211-229). One row per MediaMessages row, then one row per file in those folders "
            "that no MediaMessages row names (In media.db No). Copied is download_at, set to the "
            "device clock when WAMR makes the copy (y21.java:205, c82.java:150), written as "
            "yyyy-MM-dd HH:mm:ss in UTC (i31.java:212-217). Original Deleted is the deleted column: "
            "WAMR sets it to 1 when it sees WhatsApp's own copy of the file deleted (c82.java:78-99, "
            "g72.java:73-82, y21.java:285-288), so Yes means the original was deleted and WAMR's copy "
            "is kept. Deleted At is deleted_at, which that step does not write (i31.java:80-84). WAMR "
            "schedules a cleanup a day after a copy that removes rows still at 0 copied before then, "
            "with their files (f72.java:57, i31.java:61-77 and 273-291), so a No row may not last. "
            "Media Type is media_type with the folder name WAMR gives it (jy0.java:16-39, "
            "x00.java:20, yh2.java:20-25): 1 Voice Notes, 2 Images, 3 Video, 4 Audio, 5 Documents, "
            "6 Animated Gifs, 7 Stickers, 8 Video Notes. Only 1 and 2 were seen in the test data. The "
            "file is looked up in that folder for the database's Android user; Media Format is read "
            "from the file's first bytes, and File not in extraction means no file was found. WAMR "
            "renames a voice note's .opus file to .mp3 without converting it (c82.java:88-99), so "
            "those files are Ogg. The author column is not reported because WAMR does not write it "
            "(i31.java:211-223). WAMR's chat and media records carry no link to each other, so the "
            "media is not shown on the WAMR - WhatsApp Chats rows."),
        "paths": ('*/com.drilens.wamr/databases/media.db*',
                  '*/Android/data/com.drilens.wamr/files/WAMR/*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "wamr_monitored_apps": {
        "name": "WAMR - Monitored Apps",
        "description": "Apps the WAMR notification recovery app is set to watch, and the apps that "
                       "have a notification table in its notifs.db.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "Class and line references are as in WAMR - Captured Notifications. In Monitored List is "
            "Yes when the package is in the monitored_apps value of the Settings table of settings.db, "
            "a list separated by semicolons (cp1.java:19 and 34-41, l91.java:47-50). WAMR captures a "
            "notification only from an app in that list (NotificationListener.java:89-92), so an app "
            "missing from it, or listed with no rows, was not necessarily silent. Notification Table "
            "is Yes when notifs.db has an app_<package> table for it; WAMR creates the table when it "
            "adds the app (l91.java:44-45), so an app with a table and No in the list was watched "
            "earlier. Captured Notifications is that table's row count. WhatsApp's chats are counted "
            "in WAMR - WhatsApp Chats, not here."),
        "paths": ('*/com.drilens.wamr/databases/settings.db*',
                  '*/com.drilens.wamr/databases/notifs.db*'),
        "output_types": "standard",
        "artifact_icon": "list",
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, canonical_path, unique_files
from scripts.ilapfuncs import (artifact_processor, check_in_media, get_sqlite_db_records,
                               is_sqlite_sidecar)

PACKAGE = 'com.drilens.wamr'
DATABASES = ('notifs.db', 'textmess.db', 'media.db', 'settings.db')

# media_type as stored -> the WAMR folder for it: jy0.a() maps the type enum (1..9) to the stored
# value, x00.e names the folders by enum position (yh2.B() is the enum value less one).
MEDIA_TYPES = {
    1: 'Voice Notes', 2: 'Images', 3: 'Video', 4: 'Audio', 5: 'Documents', 6: 'Animated Gifs',
    7: 'Stickers', 8: 'Video Notes',
}

_ROOT_STOP = ('data', 'data_mirror', 'media', 'storage', 'sdcard', 'userdata', 'user', 'user_de')


def _parse_utc(value):
    """A WAMR time text (yyyy-MM-dd HH:mm:ss, with _SSS on some tables) as UTC, else ''."""
    if not isinstance(value, str):
        return ''
    for pattern in ('%Y-%m-%d %H:%M:%S_%f', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(value, pattern).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return ''


def _not_null_word(value):
    """WAMR writes the word null for a missing title or content."""
    return '' if value is None or value == 'null' else value


def _parts(path):
    return os.path.normpath(str(path)).replace('\\', '/').split('/')


def _container(path):
    """The app data folder a staged path belongs to: the path up to its com.drilens.wamr segment."""
    parts = _parts(path)
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == PACKAGE:
            return '/'.join(parts[:index + 1])
    return None


def _evidence_root(relative_path):
    """The folders above the device's storage in a relative path ('' for a plain /data dump)."""
    parts = str(relative_path).replace('\\', '/').strip('/').split('/')
    for index, part in enumerate(parts):
        if part in _ROOT_STOP:
            return '/'.join(parts[:index])
    return '/'.join(parts[:-1])


def _stores(context):
    """Per app data folder: its four WAMR databases, the Android user and the evidence root.

    Duplicate storage views of one file (data/data and data/user/0) are read once, and every
    spelling of one app data folder is grouped under one key."""
    stores = {}
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.isdir(path) or is_sqlite_sidecar(path):
            continue
        container = _container(path)
        if not container:
            continue
        rel = path[len(container):].replace('\\', '/').strip('/').split('/')
        if len(rel) != 2 or rel[0] != 'databases' or rel[1] not in DATABASES:
            continue
        relative = context.get_relative_path(path)
        key = canonical_path(context.get_relative_path(container))[0]
        entry = stores.setdefault(key, {'user': android_user(relative) or '0',
                                        'root': _evidence_root(relative)})
        entry.setdefault(rel[1], path)
    return dict(sorted(stores.items()))


def _tables(path, prefix):
    rows = get_sqlite_db_records(
        path, "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
    return [row[0] for row in rows if row[0].startswith(prefix) and row[0] != prefix]


def _quote(name):
    return '"' + name.replace('"', '""') + '"'


@artifact_processor
def wamr_notifications(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        path = entry.get('notifs.db')
        if not path:
            continue
        sources.append(path)
        for table in _tables(path, 'app_'):
            for row_id, app, title, subtext, content, stamp in get_sqlite_db_records(
                    path, f'SELECT _id, app, title, subtext, content, time FROM {_quote(table)}'):
                data_list.append((
                    _parse_utc(stamp), app or table[len('app_'):], _not_null_word(title),
                    subtext or '', _not_null_word(content), entry['user'], row_id))
    data_list.sort(key=lambda row: (row[0] == '', row[0] or datetime.min.replace(tzinfo=timezone.utc)))
    data_headers = (('Captured', 'datetime'), 'App', 'Title', 'Subtext', 'Content',
                    'Android User', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def wamr_whatsapp_chats(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        path = entry.get('textmess.db')
        if not path:
            continue
        sources.append(path)
        for table in _tables(path, 'chat_'):
            for row_id, author, content, stamp, deleted in get_sqlite_db_records(
                    path, f'SELECT _id, author, content, received_at, deleted FROM {_quote(table)}'):
                data_list.append((
                    _parse_utc(stamp), author or '', content or '',
                    'Yes' if deleted == 1 else 'No' if deleted == 0 else str(deleted),
                    entry['user'], table, row_id))
    data_list.sort(key=lambda row: (row[0] == '', row[0] or datetime.min.replace(tzinfo=timezone.utc)))
    data_headers = (('Captured', 'datetime'), 'Chat', 'Content', 'Marked Deleted',
                    'Android User', 'Chat Table', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


def _media_files(context):
    """{(evidence root, Android user, folder, file name): staged path} for WAMR's copies."""
    marker = f'/Android/data/{PACKAGE}/files/WAMR/'
    index = {}
    for file_found in unique_files(context):
        path = str(file_found)
        if not os.path.isfile(path):
            continue
        relative = '/' + str(context.get_relative_path(path)).replace('\\', '/').lstrip('/')
        if marker not in relative:
            continue
        head, tail = relative.split(marker, 1)
        parts = tail.split('/')
        if len(parts) != 2:
            continue
        user = head.rstrip('/').split('/')[-1]
        index.setdefault((_evidence_root(relative.lstrip('/')), user if user.isdigit() else '0',
                          parts[0], parts[1]), path)
    return index


def _sniff(path):
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return 'Not readable'
    if head[:3] == b'\xff\xd8\xff':
        return 'JPEG'
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'PNG'
    if head[:6] in (b'GIF87a', b'GIF89a'):
        return 'GIF'
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'WebP'
    if head[4:8] == b'ftyp':
        return 'ISO base media (MP4 family)'
    if head[:4] == b'OggS':
        return 'Ogg'
    if head[:4] == b'%PDF':
        return 'PDF'
    if head[:3] == b'ID3' or head[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'):
        return 'MP3'
    return 'Unknown'


@artifact_processor
def wamr_media(context):
    files = _media_files(context)
    named = set()
    data_list = []
    sources = []
    for entry in _stores(context).values():
        path = entry.get('media.db')
        if not path:
            continue
        sources.append(path)
        for row_id, name, media_type, stamp, deleted_at, deleted in get_sqlite_db_records(
                path, 'SELECT _id, file_name, media_type, download_at, deleted_at, deleted '
                      'FROM MediaMessages'):
            folder = MEDIA_TYPES.get(media_type, '')
            key = (entry['root'], entry['user'], folder, name)
            found = files.get(key) if folder else None
            if found:
                named.add(key)
                sources.append(found)
                media, media_format = check_in_media(found, name) or '', _sniff(found)
                size = os.path.getsize(found)
            else:
                media, media_format, size = '', 'File not in extraction', ''
            data_list.append((
                _parse_utc(stamp), media, media_format, name or '',
                f'{media_type} ({folder})' if folder else str(media_type),
                'Yes' if deleted == 1 else 'No' if deleted == 0 else str(deleted),
                _parse_utc(deleted_at), size, 'Yes', entry['user'], row_id))
    for key, found in sorted(files.items()):
        if key in named:
            continue
        sources.append(found)
        data_list.append((
            '', check_in_media(found, key[3]) or '', _sniff(found), key[3], key[2], '', '',
            os.path.getsize(found), 'No', key[1], ''))
    data_headers = (('Copied', 'datetime'), ('Media', 'media'), 'Media Format', 'File Name',
                    'Media Type', 'Original Deleted', ('Deleted At', 'datetime'), 'Size (bytes)',
                    'In media.db', 'Android User', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def wamr_monitored_apps(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        listed = []
        settings = entry.get('settings.db')
        if settings:
            sources.append(settings)
            for (value,) in get_sqlite_db_records(
                    settings, "SELECT value FROM Settings WHERE key_name = 'monitored_apps'"):
                listed.extend(item for item in (value or '').split(';') if item)
        counts = {}
        notifs = entry.get('notifs.db')
        if notifs:
            sources.append(notifs)
            for table in _tables(notifs, 'app_'):
                rows = list(get_sqlite_db_records(notifs, f'SELECT COUNT(*) FROM {_quote(table)}'))
                counts[table[len('app_'):]] = rows[0][0] if rows else 0
        for package in sorted(set(listed) | set(counts)):
            data_list.append((
                package, 'Yes' if package in listed else 'No',
                'Yes' if package in counts else 'No',
                counts.get(package, ''), entry['user']))
    data_headers = ('App', 'In Monitored List', 'Notification Table', 'Captured Notifications',
                    'Android User')
    return data_headers, data_list, '\n'.join(sources)
