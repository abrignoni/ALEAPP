__artifacts_v2__ = {
    "telekom_mail_messages": {
        "name": "Telekom Mail - Messages",
        "description": (
            "Mails held in telekom-database by the Telekom Mail app, with their folder, account and the "
            "first saved attachment file."),
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the Telekom Mail APK held in the extraction, version code "
            "2613 as the device's packages.xml records it, decompiled with jadx; obfuscated class names "
            "hold for that build only. The app opens telekom-database as its Room database "
            "(r37.java:21). One row per row of the Mail table. Date is dateAndTime, a Date the app "
            "stores as Unix milliseconds (de/telekom/mail/localstorage/room/Converters.java:66-78); "
            "what sets it was not traced. Folder Path is folderPath and Folder Name the name of the "
            "Folder row with the same account and path; Account Email is the email of the Account row "
            "with the mail's accountId. Sender and Reply To are the stored name and address. To, Cc and "
            "Bcc are the entries of the recipients JSON list with that type, one per line; Other "
            "Recipients lists entries of any other type. A recipients value that is not a JSON list is "
            "shown in To as stored. Only type to occurred in the test data. Body Text is the plain "
            "column, or when it is empty the html column with tags removed, script and style content "
            "dropped and character references decoded; nothing is rendered or linked, and the database "
            "copied into the report's data folder holds the HTML as stored. In the test data plain was "
            "empty on every mail, so only the html path ran. The richText column is not read; it was "
            "empty in the test data. Attachments Listed counts the entries of the attachments JSON "
            "list, and Attachment shows the first saved file one of them names, found as described in "
            "Telekom Mail - Attachments. Has Attachments is hasAttachments, 0 and 1 shown as No and "
            "Yes; in the test data two mails list attachments while it is 0. Read is isRead, set to 1 "
            "or 0 by updates that also clear isReadLocally (gb7.java:54309 and 54467). Read Locally is "
            "isReadLocally, set to 1, 0 or null by other updates (gb7.java:54240, 54258, 54324 and "
            "54687); a null is shown blank, and it was null on every mail in the test data. Deleted "
            "Locally is isDeletedLocally, set by two updates (gb7.java:54527 and 54570) and reset to 0 "
            "for a whole account by a third (gb7.java:54324); their callers were not traced. Every "
            "column is also written when the app writes a whole row (gb7.java:35 and 362). Answered and "
            "Forwarded are isAnswered and isForwarded, 0 and 1 shown as No and Yes. Outbox State (as "
            "stored) and Priority (as stored) are outboxState and priority as stored. What sets the "
            "four was not traced. Preview is previewText. Body Format names the column Body Text came "
            "from. Message ID, XGUID and Row ID are messageId, xguid and id as stored; what messageId "
            "and xguid identify was not traced. Not read: the Interaction table (its one row in the "
            "test data has type INSTALLED_NEW_VERSION), AppSetting and StorageInfo (app settings and "
            "mailbox storage figures), and AccountHistory, ManualRecipientSuggestion and Widget, which "
            "were empty in the test data. In the test data Has Attachments, Read, Read Locally, Deleted "
            "Locally, Answered, Forwarded, Outbox State, Priority and Body Format each held one value "
            "across the three mails, so their other outputs did not run. Each database copy is read on "
            "its own, with its folder and account rows, and the copies are then joined: a copy under "
            "another storage spelling is read when it differs, and a row both hold appears once. A "
            "rollback snapshot that differs from the live copy is read separately, so a row both hold "
            "appears twice. Neither case was present in the test data. Android User is read from the "
            "database's path; a path that names no user shows 0."),
        "paths": ('*/de.telekom.mail/databases/telekom-database*',
                  '*/de.telekom.mail/files/attachments/*'),
        "output_types": "standard",
        "multiline_columns": ["To", "Cc", "Bcc", "Other Recipients", "Body Text"],
        "artifact_icon": "mail",
    },
    "telekom_mail_attachments": {
        "name": "Telekom Mail - Attachments",
        "description": "Attachments listed on the Telekom Mail app's mails, and the attachment files "
                       "it saved, including files no mail names.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the Telekom Mail APK held in the extraction, version code "
            "2613 as the device's packages.xml records it, decompiled with jadx; obfuscated class names "
            "hold for that build only. The app opens telekom-database as its Room database "
            "(r37.java:21). One row per entry of a mail's attachments JSON list for each of its full "
            "and preview copies the extraction holds, or one row when it holds neither, and one row per "
            "file under files/attachments that no entry names. The app saves an attachment into the "
            "folder files/attachments/<account>/<folder path>/mail::<key>/fulls/<index> or "
            "previews/<index> (TelekomFileProvider.java:386), and each entry records the content URI of "
            "its copy in its full and preview members; in the test data every full member held a URI "
            "and every preview member was empty. The URI is resolved through the app's file provider "
            "root internal_files, which is the files folder (res/xml/filepaths.xml); a URI under its "
            "cache or external_files root, or any other, is not followed. A file is looked for only "
            "under the app folder that holds the database naming it, so a rollback snapshot is matched "
            "to the files in its own folder; within one folder, byte-identical copies under different "
            "storage spellings are listed once. File not in extraction marks an entry none of whose "
            "copies the extraction holds and whose full URI names a file under that root; a missing "
            "preview beside a held full copy gets no row. No entry was in that state in the test data. "
            "Media Format is read from the file's first bytes. File Name, Media Type, Size (as stored), "
            "Inline and Status (as stored) are the entry's fileName, mediaType and subType, "
            "sizeInBytes, isInline (shown as Yes or No) and the status of its copy. For a file no entry "
            "names, File Name is the file's own name. Status and stored size are not checked against "
            "the file: in the test data all four held copies had status NotAvailable and two had a "
            "stored size different from the file's. For a file no entry names, Mail Folder Path and "
            "Attachment Index are read from its path, and the mail key in the path is not looked up. In "
            "the test data the 8 such files carried 5 keys of 24 letters and digits, none equal to a "
            "Mail id, messageId or xguid, while the keys of the 4 named files were the mail's row id. "
            "Such a file may belong to a mail the app no longer holds; that is not established. Mail "
            "Date is the mail's dateAndTime, read as in Telekom Mail - Messages. Android User is read "
            "from the database's path; a path that names no user shows 0."),
        "paths": ('*/de.telekom.mail/databases/telekom-database*',
                  '*/de.telekom.mail/files/attachments/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
}

import hashlib
import json
import os
import re
import sqlite3
import urllib.parse
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
from scripts.ilapfuncs import artifact_processor, check_in_media, get_sqlite_db_records, logfunc

PACKAGE = 'de.telekom.mail'
DATABASE = 'telekom-database'
# res/xml/filepaths.xml: the fileprovider's internal_files root, the one the attachments use.
PROVIDER = 'content://de.telekom.mail.fileprovider/'
PROVIDER_ROOTS = {'internal_files': 'files'}
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_BLOCKS = {'br', 'p', 'div', 'tr', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'blockquote'}


def _ms_to_utc(value):
    """Unix milliseconds to UTC, or '' for an empty, zero or out of range value."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        return ''


def _yes_no(value):
    return '' if value is None else 'Yes' if value else 'No'


def _blank(value):
    return '' if value is None else value


def _rows(path, query):
    """The rows of a query, or [] with a log line when the database cannot be read."""
    try:
        return list(get_sqlite_db_records(path, query))
    except sqlite3.DatabaseError as error:
        logfunc(f'Telekom Mail: could not read {path}: {error}')
        return []


class _Text(HTMLParser):
    """The text of an HTML body: tags dropped, script and style content skipped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        elif tag in _BLOCKS:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1
        elif tag in _BLOCKS:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def _html_text(html):
    if not html:
        return ''
    parser = _Text()
    try:
        parser.feed(str(html))
        parser.close()
    except (AssertionError, ValueError):
        pass
    lines = [' '.join(line.split()) for line in ''.join(parser.parts).splitlines()]
    return '\n'.join(line for line in lines if line)


def _json(value):
    if value in (None, ''):
        return None
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def _recipients(value, kind):
    """The addresses of one type in a recipients JSON list, one per line; as stored if not JSON."""
    items = _json(value)
    if not isinstance(items, list):
        return _blank(value) if kind == 'to' else ''
    out = []
    for item in items:
        if isinstance(item, dict) and str(item.get('type', '')).lower() == kind:
            name, address = item.get('name') or '', item.get('address') or ''
            out.append(f'{name} <{address}>' if name and address else name or address)
    return '\n'.join(out)


def _other_recipients(value):
    """Recipients whose type is not to, cc or bcc, as 'type: address' lines."""
    items = _json(value)
    if not isinstance(items, list):
        return ''
    out = []
    for item in items:
        if not isinstance(item, dict):
            out.append(str(item))
        elif str(item.get('type', '')).lower() not in ('to', 'cc', 'bcc'):
            out.append(f"{item.get('type', '')}: {item.get('name') or ''} {item.get('address') or ''}".strip())
    return '\n'.join(out)


def _address(name, address):
    return f'{name} <{address}>' if name and address else name or address or ''


def _user(relative_path):
    """The Android user of an app data path, read from a rollback snapshot path too; 0 if none."""
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK.search(str(relative_path).replace('\\', '/'))
    return match.group(2) if match else '0'


def _container(path):
    parts = os.path.normpath(str(path)).replace('\\', '/').split('/')
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] == PACKAGE:
            return '/'.join(parts[:index + 1])
    return None


def _digest(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            sha.update(block)
    return sha.hexdigest()


def _distinct(paths):
    """The paths with byte-identical copies dropped; files are hashed only when sizes match."""
    if len(paths) < 2:
        return list(paths)
    sizes = {}
    for path in paths:
        try:
            sizes.setdefault(os.path.getsize(path), []).append(path)
        except OSError:
            sizes.setdefault(('unreadable', path), []).append(path)
    kept = set()
    for size, group in sizes.items():
        if len(group) < 2 or isinstance(size, tuple):
            kept.update(group)
            continue
        seen = {}
        for path in group:
            try:
                seen.setdefault(_digest(path), path)
            except OSError:
                seen.setdefault(('unreadable', path), path)
        kept.update(seen.values())
    return [path for path in paths if path in kept]


def _place(context, path):
    """(store key, user, tail below the app folder) of a staged path, or None.

    Read from the evidence name, not the staged path: staging rewrites characters such as the
    colons of the app's mail:: folders."""
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    container = _container(relative)
    if not container:
        return None
    return canonical_path(container)[0], _user(relative), relative[len(container):].strip('/')


def _stores(context):
    """Per app data folder: user, the database copies and the attachment files by their tail.

    Databases come from unique_files, which keeps differing copies. Attachment files are taken
    from every staged file, so a rollback snapshot keeps its own copies even when they match a
    live file byte for byte; within one folder byte-identical copies are dropped."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        place = None if os.path.isdir(path) else _place(context, path)
        if place and place[2] == f'databases/{DATABASE}':
            stores.setdefault(place[0], {'dbs': [], 'files': {}, 'user': place[1]})['dbs'].append(path)
    for file_found in context.get_files_found():
        path = str(file_found)
        place = None if os.path.isdir(path) else _place(context, path)
        if place and place[2].startswith('files/attachments/'):
            entry = stores.setdefault(place[0], {'dbs': [], 'files': {}, 'user': place[1]})
            entry['files'].setdefault(place[2], []).append(path)
    for entry in stores.values():
        entry['files'] = {tail: _distinct(sorted(set(copies))) for tail, copies in entry['files'].items()}
    return dict(sorted(stores.items()))


def _copies(entry, tail):
    """The staged copies of an attachment tail held under the store's own folder."""
    return entry['files'].get(tail, []) if tail else []


def _union(context, entry, query):
    return union_view_rows(context, [(path, _rows(path, query)) for path in entry['dbs']])


def _provider_tail(uri):
    """The path below the app data folder that a fileprovider URI of the app names, or None."""
    if not uri or not str(uri).startswith(PROVIDER):
        return None
    root, _, rest = urllib.parse.unquote(str(uri)[len(PROVIDER):]).partition('/')
    base = PROVIDER_ROOTS.get(root)
    if not base or not rest or '..' in rest.split('/'):
        return None
    return f'{base}/{rest}'


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
    if head[:4] == b'%PDF':
        return 'PDF'
    if head[:4] == b'PK\x03\x04':
        return 'ZIP (Office or archive)'
    if head[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        return 'OLE (older Office)'
    return 'Unknown'


def _media(cache, path, name):
    if path not in cache:
        cache[path] = (check_in_media(path, name) or '', _sniff(path))
    return cache[path]


def _mail_rows(context, entry):
    return _union(context, entry, '''
        SELECT id, dateAndTime, accountId, folderPath, sender_name, sender_address, reply_to_name,
               reply_to_address, recipients, subject, previewText, plain, html, attachments,
               hasAttachments, isRead, isReadLocally, isDeletedLocally, isAnswered, isForwarded,
               outboxState, priority, messageId, xguid
        FROM Mail ORDER BY dateAndTime''')


def _attachment_list(value):
    items = _json(value)
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _part(item, key):
    part = item.get(key)
    return part if isinstance(part, dict) else {}


@artifact_processor
def telekom_mail_messages(context):
    data_list = []
    sources = []
    cache = {}
    for entry in _stores(context).values():
        sources.extend(entry['dbs'])
        # Rows are completed inside each database copy, then the copies are joined.
        per_copy = []
        for path in entry['dbs']:
            one = dict(entry, dbs=[path])
            rows = []
            folders = {(account, path): name for account, path, name in _union(
                context, one, 'SELECT accountId, path, name FROM Folder')}
            accounts = {account: email for account, email in _union(
                context, one, 'SELECT accountId, email FROM Account')}
            for row in _mail_rows(context, one):
                (mail_id, date, account, folder_path, sender_name, sender_address, reply_name,
                 reply_address, recipients, subject, preview, plain, html, attachments, has_att,
                 is_read, read_locally, deleted_locally, answered, forwarded, outbox, priority,
                 message_id, xguid) = row
                listed = _attachment_list(attachments)
                media = ''
                for item in listed:
                    for key in ('full', 'preview'):
                        tail = _provider_tail(_part(item, key).get('path'))
                        copies = _copies(entry, tail)
                        if copies and not media:
                            sources.append(copies[0])
                            media = _media(cache, copies[0], item.get('fileName') or os.path.basename(copies[0]))[0]
                text = plain if plain else _html_text(html)
                rows.append((
                    _ms_to_utc(date), _blank(folder_path), folders.get((account, folder_path), ''),
                    accounts.get(account, ''), _address(sender_name, sender_address),
                    _address(reply_name, reply_address), _recipients(recipients, 'to'),
                    _recipients(recipients, 'cc'), _recipients(recipients, 'bcc'),
                    _other_recipients(recipients), _blank(subject), _blank(preview), _blank(text),
                    'Plain' if plain else 'HTML' if html else '', media, len(listed), _yes_no(has_att),
                    _yes_no(is_read), _yes_no(read_locally), _yes_no(deleted_locally),
                    _yes_no(answered), _yes_no(forwarded), _blank(outbox), _blank(priority),
                    entry['user'], _blank(message_id), _blank(xguid), _blank(mail_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Date', 'datetime'), 'Folder Path', 'Folder Name', 'Account Email', 'Sender', 'Reply To',
        'To', 'Cc', 'Bcc', 'Other Recipients', 'Subject', 'Preview', 'Body Text', 'Body Format',
        ('Attachment', 'media'), 'Attachments Listed', 'Has Attachments', 'Read',
        'Read Locally', 'Deleted Locally', 'Answered', 'Forwarded', 'Outbox State (as stored)',
        'Priority (as stored)', 'Android User', 'Message ID', 'XGUID', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def telekom_mail_attachments(context):
    data_list = []
    sources = []
    cache = {}
    for entry in _stores(context).values():
        sources.extend(entry['dbs'])
        named = set()
        per_copy = []
        for path in entry['dbs']:
            one = dict(entry, dbs=[path])
            rows = []
            for row in _mail_rows(context, one):
                mail_id, date, subject, attachments, folder_path = row[0], row[1], row[9], row[13], row[3]
                for item in _attachment_list(attachments):
                    found = []
                    for key in ('full', 'preview'):
                        part = _part(item, key)
                        tail = _provider_tail(part.get('path'))
                        if tail:
                            named.add(tail)
                        for copy in _copies(entry, tail):
                            found.append((key, copy, part.get('status')))
                    if not found:
                        full = _part(item, 'full')
                        found = [('full', None, full.get('status'))]
                    for key, copy, status in found:
                        if copy:
                            sources.append(copy)
                            media, media_format = _media(cache, copy, item.get('fileName') or os.path.basename(copy))
                            try:
                                file_size = os.path.getsize(copy)
                            except OSError:
                                file_size = ''
                        else:
                            tail = _provider_tail(_part(item, key).get('path'))
                            media, file_size = '', ''
                            media_format = 'File not in extraction' if tail else ''
                        rows.append((
                            _ms_to_utc(date), media, media_format, 'Preview' if key == 'preview' else 'Full',
                            _blank(item.get('fileName')),
                            '/'.join(str(v) for v in (item.get('mediaType'), item.get('subType')) if v),
                            _blank(item.get('sizeInBytes')), file_size, _yes_no(item.get('isInline')),
                            _blank(status), _blank(subject), _blank(folder_path), 'Yes', entry['user'],
                            _blank(mail_id), _blank(item.get('index'))))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
        for tail, copies in sorted(entry['files'].items()):
            if tail in named:
                continue
            parts = tail.split('/')
            kind = 'Preview' if 'previews' in parts else 'Full' if 'fulls' in parts else ''
            folder, index = '', ''
            mail_at = next((i for i, part in enumerate(parts) if part.startswith('mail::')), None)
            if mail_at is not None:
                folder = '/'.join(parts[3:mail_at])
                index = parts[mail_at + 2] if len(parts) > mail_at + 3 else ''
            for copy in copies:
                sources.append(copy)
                media, media_format = _media(cache, copy, parts[-1])
                try:
                    file_size = os.path.getsize(copy)
                except OSError:
                    file_size = ''
                data_list.append((
                    '', media, media_format, kind, parts[-1], '', '', file_size, '', '',
                    '', folder, 'No', entry['user'], '', index))
    data_headers = (
        ('Mail Date', 'datetime'), ('Media', 'media'), 'Media Format', 'Copy', 'File Name',
        'Media Type', 'Size (as stored)', 'File Size (bytes)', 'Inline', 'Status (as stored)',
        'Mail Subject', 'Mail Folder Path', 'Named by a Mail', 'Android User', 'Mail Row ID',
        'Attachment Index')
    return data_headers, data_list, '\n'.join(sources)
