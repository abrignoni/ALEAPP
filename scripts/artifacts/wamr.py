__artifacts_v2__ = {
    "wamr_notifications": {
        "name": "WAMR - Captured Notifications",
        "description": "Copies of other apps' notifications that the WAMR app (com.drilens.wamr) "
                       "saved in its notifs.db, one table per app.",
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
            "app_<package> table of notifs.db (l91.java:41 and 45). A write-ahead log beside the "
            "database is applied; a database with no log beside it is read alone. The test data had "
            "no write-ahead log. When one database is present under more than one storage path "
            "(data/data and data/user/0) and the copies read differently, the rows of every copy "
            "are reported, a row the copies share once. Android User is read from the path, "
            "including a rollback snapshot under misc_ce/<n>/rollback, and a path that "
            "names no user is read as user 0. Captured is the time column, which WAMR sets to the device clock "
            "when it handles the notification, not a time the notification carries "
            "(com/drilens/wamr/NotificationListener.java:155 and 200), written as "
            "yyyy-MM-dd HH:mm:ss_SSS in UTC (l91.java:27-29); a value that does not parse is left "
            "blank. App is the app column, the posting app's package name "
            "(NotificationListener.java:154 and 190). Title is built from the notification's title "
            "and big title fields; when the big title starts with the title, WAMR stores the big "
            "text as the title (NotificationListener.java:124-130). Content is built from its text, "
            "big text and text lines (NotificationListener.java:97-150). Subtext is its sub text. "
            "When a notification has no title or no content WAMR stores the word null "
            "(NotificationListener.java:191-198); that stored word is shown here as a blank, so a "
            "notification whose text was the word null is also blank. WAMR skips a notification "
            "whose title and content match its newest row for that app within 2 seconds "
            "(NotificationListener.java:187), and the WAMR user can delete rows from the app "
            "(hg1.java:174), so not every notification has a row. WhatsApp and GBWhatsApp "
            "notifications are not stored here; they go to WAMR - WhatsApp Chats "
            "(NotificationListener.java:93). Only apps in WAMR's monitored list are captured "
            "(NotificationListener.java:89-92); WAMR - Monitored Apps lists them."),
        "paths": ('*/com.drilens.wamr/databases/notifs.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
    },
    "wamr_whatsapp_chats": {
        "name": "WAMR - WhatsApp Chats",
        "description": "WhatsApp messages the WAMR app (com.drilens.wamr) rebuilt from WhatsApp "
                       "notifications and saved in its textmess.db, one table per chat.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "Rows are WAMR's copies of what WhatsApp or GBWhatsApp notifications showed, not "
            "WhatsApp's own records. Class and line references are as in WAMR - Captured "
            "Notifications. Reads every chat_ table of textmess.db. Chat is the author column. WAMR "
            "fills it from the notification's title after removing direction marks and zero-width "
            "spaces. When the title holds ' @ ' it keeps the part after it, and when the title "
            "holds a colon and a space it keeps the part before the last one "
            "(NotificationListener.java:210-335, 631 and 644), so in those cases it is not the "
            "sender's name. When the title carries a sender, WAMR writes Content as the sender, a "
            "colon and the text (NotificationListener.java:300-302 and 310-325); otherwise Content "
            "is the notification's line or text as received. WAMR drops a line whose chat name is "
            "empty or contains backup (NotificationListener.java:342) and stores only lines that "
            "differ from the rows it already holds (NotificationListener.java:623-650), so not every "
            "WhatsApp notification line has a row. WAMR names a chat's table chat_ followed by the "
            "chat name, with every character other than an ASCII letter or digit written as four "
            "hex digits (i31.java:49-58). That encoding cannot be reversed, since digits are kept as "
            "they are, so Chat Table is shown as stored and is not decoded. Captured is "
            "received_at, which WAMR sets to the device clock when it handles the notification "
            "(fz1.java:13-16, NotificationListener.java:254, 289 and 333), written as "
            "yyyy-MM-dd HH:mm:ss_SSS in UTC (NotificationListener.java:546, 585-586 and 633); "
            "several lines from one notification can share one time, and a value that does not "
            "parse is left blank. Marked Deleted is the deleted column. WAMR sets it to 1 on the "
            "newest row of a chat when a later notification for that chat matches the "
            "deleted-message text WAMR lists for the device locale, and that row is not already "
            "marked (NotificationListener.java:362-538). It does not record which message WhatsApp "
            "deleted. The WAMR user can also set or clear it, delete a row, or delete a chat's "
            "table from the app (jz1.java:113 and 135-160, hg1.java:154). The Marked Deleted "
            "behaviour was read in the code; no row in the test data had it set. Row ID is _id."),
        "paths": ('*/com.drilens.wamr/databases/textmess.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "wamr_media": {
        "name": "WAMR - Media Copies",
        "description": "Copies of WhatsApp media files that the WAMR app (com.drilens.wamr) made in "
                       "its external files folder, with the media.db row for each where there is one.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "Class and line references are as in WAMR - Captured Notifications. WAMR copies WhatsApp "
            "media files to Android/data/com.drilens.wamr/files/WAMR/<folder>/ and records the copy "
            "in the MediaMessages table of media.db unless a row with that file name already exists "
            "(y21.java:195-209, c82.java:140-155, i31.java:211-229). One row per MediaMessages row, "
            "then one row per file in those folders that no MediaMessages row names (In media.db "
            "No); no such file was in the test data. Copied is download_at, set to the device clock "
            "when WAMR makes the copy (y21.java:205, c82.java:150), written as yyyy-MM-dd HH:mm:ss "
            "in UTC (i31.java:212-217). Original Deleted is the deleted column. WAMR sets it to 1 "
            "when it sees a delete event for a file of that name in WhatsApp's media folder within "
            "24 hours of copying it (c82.java:78-99, g72.java:73-82, y21.java:285-288, "
            "i31.java:232-252); after 24 hours the same event removes WAMR's copy and its row "
            "(i31.java:273-291 and 328-337). So Yes means WAMR saw that delete event and kept its "
            "copy. The deleted_at column is not reported: the step that sets deleted does not write "
            "it (i31.java:80-84), and it was empty on every row of the test data. A day after a copy "
            "WAMR runs a cleanup that removes rows still at 0 that were copied before that copy, "
            "with their files (f72.java:55-58 and 66-69, i31.java:61-77 and 273-291), so a No row "
            "may not last. Media Type is media_type with the folder name WAMR gives it "
            "(jy0.java:16-39, x00.java:20 and 314-337, yh2.java:20-25): 1 Voice Notes, 2 Images, "
            "3 Video, 4 Audio, 5 Documents, 6 Animated Gifs, 7 Stickers, 8 Video Notes. Only 1 and 2 "
            "were seen in the test data. The file is looked up in that folder for the database's "
            "Android user. Copies "
            "of one file under more than one storage path are each listed when their bytes differ. "
            "Media Format is read from the file's first bytes, and File not in "
            "extraction means no file was found. When it marks a voice note deleted, WAMR renames "
            "its .opus file to .mp3 without converting it (c82.java:88-99; ik0.java:69-75 does the "
            "same rename). The 4 voice note files in the test data are named .mp3 and read as Ogg. "
            "The author column is not reported because WAMR does not write it (i31.java:211-223). "
            "WAMR's chat and media records carry no link to each other, so the media is not shown on "
            "the WAMR - WhatsApp Chats rows."),
        "paths": ('*/com.drilens.wamr/databases/media.db*',
                  '*/Android/data/com.drilens.wamr/files/WAMR/*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "wamr_monitored_apps": {
        "name": "WAMR - Monitored Apps",
        "description": "Apps the WAMR app (com.drilens.wamr) is set to watch, and the apps that "
                       "have a notification table in its notifs.db.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Notifications",
        "notes": (
            "Class and line references are as in WAMR - Captured Notifications. In Monitored List is "
            "Yes when the package is in the monitored_apps value of the Settings table of settings.db, "
            "a list separated by semicolons (cp1.java:19 and 34-41, l91.java:47-50); a value of NULL "
            "is read as no list, as WAMR reads it (cp1.java:24). WAMR captures a notification only "
            "from an app in that list (NotificationListener.java:89-92), so an app missing from it, "
            "or listed with no rows, was not necessarily silent. Notification Table is Yes when "
            "notifs.db has an app_<package> table for it. WAMR creates the table when it adds the "
            "app to the list (l91.java:44-53), and no code removes a table, so an app with a table "
            "and No was in the list earlier. When settings.db holds no monitored_apps value, every "
            "app reads No, and WAMR itself then rebuilds the list from the tables of installed apps "
            "(l91.java:103-139). Captured Notifications is that table's row count. WhatsApp's chats "
            "are counted in WAMR - WhatsApp Chats, not here."),
        "paths": ('*/com.drilens.wamr/databases/settings.db*',
                  '*/com.drilens.wamr/databases/notifs.db*'),
        "output_types": "standard",
        "artifact_icon": "list",
    },
}

import hashlib
import os
import re
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
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

_ROOT_STOP = ('data', 'data_mirror', 'media', 'mnt', 'storage', 'sdcard', 'userdata', 'user',
              'user_de')
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_EARLIEST = datetime.min.replace(tzinfo=timezone.utc)


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


def _by_time(row):
    return (row[0] == '', row[0] or _EARLIEST)


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


def _user(relative_path):
    """The Android user of an app data path, read from a rollback snapshot path too.

    A path that names no user (data/data, or an extraction rooted at /data/data) is user 0's."""
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK.search(str(relative_path).replace('\\', '/'))
    return match.group(2) if match else '0'


def _stores(context):
    """Per app data folder: every copy of each WAMR database, the Android user and the root.

    A copy under another storage spelling (data/data and data/user/0) is kept when it reads
    differently, so the rows read from the copies are joined with union_view_rows."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
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
        entry = stores.setdefault(key, {'user': _user(relative), 'root': _evidence_root(relative)})
        entry.setdefault(rel[1], []).append(path)
    return dict(sorted(stores.items()))


def _tables(path, prefix):
    rows = get_sqlite_db_records(
        path, "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
    return [row[0] for row in rows if row[0].startswith(prefix) and row[0] != prefix]


def _quote(name):
    return '"' + name.replace('"', '""') + '"'


def _notification_rows(context, entry):
    """(rows joined across copies, tables seen in any copy) of one notifs.db.

    Each row ends with the package its table is named for, which the report leaves out."""
    file_rows = []
    tables = set()
    for path in entry.get('notifs.db', []):
        rows = []
        for table in _tables(path, 'app_'):
            tables.add(table[len('app_'):])
            for row_id, app, title, subtext, content, stamp in get_sqlite_db_records(
                    path, f'SELECT _id, app, title, subtext, content, time FROM {_quote(table)}'):
                rows.append((
                    _parse_utc(stamp), app or table[len('app_'):], _not_null_word(title),
                    subtext or '', _not_null_word(content), entry['user'], row_id,
                    table[len('app_'):]))
        file_rows.append((path, rows))
    return union_view_rows(context, file_rows), tables


@artifact_processor
def wamr_notifications(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry.get('notifs.db', []))
        data_list.extend(row[:-1] for row in _notification_rows(context, entry)[0])
    data_list.sort(key=_by_time)
    data_headers = (('Captured', 'datetime'), 'App', 'Title', 'Subtext', 'Content',
                    'Android User', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def wamr_whatsapp_chats(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        file_rows = []
        for path in entry.get('textmess.db', []):
            sources.append(path)
            rows = []
            for table in _tables(path, 'chat_'):
                for row_id, author, content, stamp, deleted in get_sqlite_db_records(
                        path, f'SELECT _id, author, content, received_at, deleted FROM {_quote(table)}'):
                    rows.append((
                        _parse_utc(stamp), author or '', content or '',
                        'Yes' if deleted == 1 else 'No' if deleted == 0 else str(deleted),
                        entry['user'], table, row_id))
            file_rows.append((path, rows))
        data_list.extend(union_view_rows(context, file_rows))
    data_list.sort(key=_by_time)
    data_headers = (('Captured', 'datetime'), 'Chat', 'Content', 'Marked Deleted',
                    'Android User', 'Chat Table', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


def _digest(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            sha.update(block)
    return sha.hexdigest()


def _media_files(context):
    """{(evidence root, Android user, folder, file name): [staged paths]} for WAMR's copies.

    Copies of one file under several storage spellings are kept when their bytes differ."""
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
                          parts[0], parts[1]), []).append(path)
    for key, paths in index.items():
        distinct = {}
        for path in paths:
            try:
                distinct.setdefault((os.path.getsize(path), _digest(path)), path)
            except OSError:
                distinct.setdefault(('unreadable', path), path)
        index[key] = list(distinct.values())
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


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return ''


@artifact_processor
def wamr_media(context):
    files = _media_files(context)
    named = set()
    data_list = []
    sources = []
    for entry in _stores(context).values():
        file_rows = []
        for path in entry.get('media.db', []):
            sources.append(path)
            file_rows.append((path, list(get_sqlite_db_records(
                path, 'SELECT _id, file_name, media_type, download_at, deleted '
                      'FROM MediaMessages'))))
        for row_id, name, media_type, stamp, deleted in union_view_rows(context, file_rows):
            folder = MEDIA_TYPES.get(media_type, '')
            key = (entry['root'], entry['user'], folder, name)
            found = files.get(key, []) if folder else []
            if found:
                named.add(key)
            base = (_parse_utc(stamp), name or '',
                    f'{media_type} ({folder})' if folder else str(media_type),
                    'Yes' if deleted == 1 else 'No' if deleted == 0 else str(deleted))
            for copy in found or [None]:
                if copy:
                    sources.append(copy)
                    media, media_format, size = (check_in_media(copy, name) or '', _sniff(copy),
                                                 _size(copy))
                else:
                    media, media_format, size = '', 'File not in extraction', ''
                data_list.append((base[0], media, media_format, base[1], base[2], base[3], size,
                                  'Yes', entry['user'], row_id))
    for key, copies in sorted(files.items()):
        if key in named:
            continue
        for copy in copies:
            sources.append(copy)
            data_list.append((
                '', check_in_media(copy, key[3]) or '', _sniff(copy), key[3], key[2], '',
                _size(copy), 'No', key[1], ''))
    data_headers = (('Copied', 'datetime'), ('Media', 'media'), 'Media Format', 'File Name',
                    'Media Type', 'Original Deleted', 'Size (bytes)',
                    'In media.db', 'Android User', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def wamr_monitored_apps(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        listed = set()
        for settings in entry.get('settings.db', []):
            sources.append(settings)
            for (value,) in get_sqlite_db_records(
                    settings, "SELECT value FROM Settings WHERE key_name = 'monitored_apps'"):
                if value and value != 'NULL':
                    listed.update(item for item in value.split(';') if item)
        sources.extend(entry.get('notifs.db', []))
        rows, tables = _notification_rows(context, entry)
        counts = dict.fromkeys(tables, 0)
        for row in rows:
            counts[row[-1]] = counts.get(row[-1], 0) + 1
        for package in sorted(listed | set(counts)):
            data_list.append((
                package, 'Yes' if package in listed else 'No',
                'Yes' if package in tables else 'No',
                counts.get(package, ''), entry['user']))
    data_headers = ('App', 'In Monitored List', 'Notification Table', 'Captured Notifications',
                    'Android User')
    return data_headers, data_list, '\n'.join(sources)
