__artifacts_v2__ = {
    "freenet_mail_messages": {
        "name": "freenet Mail - Messages",
        "description": "Mails held in emaildb.db by the freenet Mail app, with their folder and account.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the freenet Mail APK held in the extraction, version code "
            "2025006235 as the device's packages.xml records it, decompiled with jadx; its class names "
            "are obfuscated, so they hold for that build only. The app opens emaildb.db as its Room "
            "database (us1.java:116). One row per row of the message table. Date is the date column, "
            "stored as Unix milliseconds (f12.java:21-27, v6.java:310-314). For a row written from a "
            "server response it is the response's date field (ad6.java:40, v32.java:213); another "
            "builder of the same model sets it from the device clock (tz3.java:242-244), and whether "
            "that path reaches the insert was not traced. Later updates can rewrite it (w6.java:544). "
            "From Name and From Email are from_name and from_email. To, Cc and Bcc are the JSON lists "
            "the columns hold, one name and address per line; the image URL an entry carries is not "
            "shown. Folder and Folder Type are display_name and type of the folders row named by "
            "message_folder_id, and Account Email is the email of the accounts row named by "
            "message_folder_account_id. Seen is is_seen: the seen flag of the server response when the "
            "row is written (pf3.java:23, v32.java:215-219, icb.java:638, v6.java:319), and later "
            "updates can change it (bf6.java:113, w6.java:542). When a message_local_flags row holds a "
            "seen value the app shows that value instead of is_seen (l42.java:145-149); that table is "
            "not read. Answered and Forwarded are is_answered and is_forwarded: the entity built from a "
            "message model has both false (icb.java:638) and the insert binds them (v6.java:317-318); a "
            "copy of an existing entity keeps its values (MessagesDaoImpl.java:126), and whether that "
            "copy is inserted was not traced. Separately, a later refresh update can set them from the "
            "response's answered and forwarded flags (RefreshMessagesWorker.java:43, rf6.java:107, "
            "w6.java:542). Has Attachments is has_attachments. Body Text is the body column; when "
            "is_html is set, tags are removed, script and style content is dropped, character "
            "references are decoded, whitespace is collapsed and line breaks are placed at block tags, "
            "so the text is not the HTML as stored and nothing in it is rendered or linked. The "
            "database copied into the report's data folder holds the HTML as stored. Body Format is "
            "HTML when is_html is set and Plain otherwise; only HTML was present in the test data. "
            "Status (as stored) is status: the row written from a server response gets DOWNLOADED "
            "(v32.java:267); FAILED and PENDING (qd6.java:16-20) are written by paths not fully traced, "
            "and a locally built message starts as PENDING (qq0.java:319). Message Type (as stored) is "
            "message_type: for a row written from a server response it is the action field of the "
            "response mapped to forward, reply, reply_all, draft or new, and unknown when the field is "
            "absent or another value (ud6.java:19-24, vl0.java:191-209); a locally built message and "
            "later updates set it by other paths (qq0.java:319, w6.java:542). The attachments, "
            "message_local_flags, contacts and contact_local_flags tables are not read; they had no "
            "rows in the test data. folder_local_flags (a last refresh time per folder) is not read "
            "either. Each database copy is read on its own, with its own lookup rows, and the copies "
            "are then joined: a copy under another storage spelling is read when it differs, and a row "
            "both hold appears once. A rollback snapshot that differs from the live copy is read "
            "separately, so a row both hold appears twice. Neither case was present in the test data. "
            "Android User is read from the database's path; a path that names no user shows 0."),
        "paths": ('*/de.freenet.mail/databases/emaildb.db*',),
        "output_types": "standard",
        "multiline_columns": ["To", "Cc", "Bcc", "Body Text"],
        "artifact_icon": "mail",
    },
    "freenet_mail_legacy_messages": {
        "name": "freenet Mail - Messages (mail.db)",
        "description": (
            "Mails held in mail.db, a store for which no reference was found in the examined build's "
            "decompiled code, with their bodies, folder and first saved attachment file."),
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the freenet Mail APK held in the extraction, version code "
            "2025006235 as the device's packages.xml records it, decompiled with jadx; its class names "
            "are obfuscated, so they hold for that build only. No reference to mail.db or its column "
            "names was found in that build's decompiled code (jadx reported errors on some methods, so "
            "the search is not complete). The database is taken to be from an earlier version of the "
            "app; no code for it was examined, and no column meaning is sourced from code. Text columns "
            "are shown as stored, 0 and 1 flag columns as No and Yes, and address lists are "
            "reformatted. One row per row of the mail table, and one more for each further mail_body "
            "row naming the same mail (not present in the test data). Received (received_date) and Sent "
            "(send_date) are read as Unix seconds, a reading taken from the values (ten digits) and not "
            "from code; a 0 is shown blank. From, To, Cc, Bcc and Reply To are the JSON lists the "
            "columns hold, one name and address per line. Account Email is the email column; the name "
            "is this module's, since the column is the folder table's key with folder_id and its "
            "meaning is not sourced from code. Folder is the title of the folder row with the mail's "
            "email and folder_id. Body Text is the plain column of the mail_body rows whose "
            "mail_hash_id is the mail's _id (a match taken from the column name and the values, 16 of "
            "17 body rows in the test data, not from code), or, when plain is empty, the html column, "
            "of which tags are removed, script and style content is dropped, character references are "
            "decoded, whitespace is collapsed and line breaks are placed at block tags, so the text is "
            "not the HTML as stored and nothing in it is rendered or linked. A mail_body row whose "
            "mail_hash_id names no mail row gets its own row with In mail Table No. Attachment is the "
            "first saved attachment file found for the mail, as in freenet Mail - Attachments "
            "(mail.db), and Attachment Count counts the mail's attachment rows. Store (as stored) is "
            "the store column; the meaning of its values is not established, and MAIL_AD was not found "
            "in that build's decompiled code. The email_account and customer tables are not read. The "
            "contact, contact_email, mail_tracking, pending_mail_action and unseen_push_mail tables are "
            "not read either; they had no rows in the test data. Each database copy is read on its own, "
            "with its own lookup rows, and the copies are then joined: a copy under another storage "
            "spelling is read when it differs, and a row both hold appears once. A rollback snapshot "
            "that differs from the live copy is read separately, so a row both hold appears twice. "
            "Neither case was present in the test data. Android User is read from the database's path; "
            "a path that names no user shows 0."),
        "paths": ('*/de.freenet.mail/databases/mail.db*',),
        "output_types": "standard",
        "multiline_columns": ["From", "To", "Cc", "Bcc", "Reply To", "Body Text"],
        "artifact_icon": "mail",
    },
    "freenet_mail_legacy_attachments": {
        "name": "freenet Mail - Attachments (mail.db)",
        "description": (
            "Attachments listed in mail.db, a store for which no reference was found in the examined "
            "build's decompiled code, with the saved file where the extraction holds it."),
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the freenet Mail APK held in the extraction, version code "
            "2025006235 as the device's packages.xml records it, decompiled with jadx; its class names "
            "are obfuscated, so they hold for that build only. No reference to mail.db or its column "
            "names was found in that build's decompiled code (jadx reported errors on some methods, so "
            "the search is not complete). The database is taken to be from an earlier version of the "
            "app; no code for it was examined, and no column meaning is sourced from code. Text columns "
            "are shown as stored, 0 and 1 flag columns as No and Yes. Content Type is the type column. "
            "One row per row of the attachment table, and one more for each further copy of its saved "
            "file found (not present in the test data). It is joined to the mail row whose _id is its "
            "mail column, a match taken from the column name and the values (11 of 12 attachment rows "
            "in the test data), not from code; Mail in mail Table is No when none is. Saved File URI is "
            "local_file_path with percent-escapes decoded. When it is a file:// URI into shared storage "
            "(/storage/emulated/<user>/...), a file whose path in the extraction ends in <user>/<the "
            "rest of that path> is looked up, and Media shows it. Media Format is read from the file's "
            "first bytes, and File not in extraction marks a URI for which no file was found at that "
            "path in the extraction (not present in the test data). That file can have been changed or "
            "replaced after the app saved it; nothing ties its bytes to the mail. Mail Received "
            "(received_date) is read as in freenet Mail - Messages (mail.db). Each database copy is "
            "read on its own, with its own lookup rows, and the copies are then joined: a copy under "
            "another storage spelling is read when it differs, and a row both hold appears once. A "
            "rollback snapshot that differs from the live copy is read separately, so a row both hold "
            "appears twice. Neither case was present in the test data. Android User is read from the "
            "database's path; a path that names no user shows 0."),
        "paths": ('*/de.freenet.mail/databases/mail.db*',),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
}

import glob
import json
import os
import re
import sqlite3
import urllib.parse
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
from scripts.ilapfuncs import (artifact_processor, check_in_media, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc)

PACKAGE = 'de.freenet.mail'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_STORAGE = re.compile(r'^/storage/emulated/(\d+)/(.+)$')
_BLOCKS = {'br', 'p', 'div', 'tr', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'blockquote'}


def _to_utc(value, unit_ms):
    """Unix milliseconds or seconds to UTC, or '' for an empty, zero or out of range value."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + (timedelta(milliseconds=value) if unit_ms else timedelta(seconds=value))
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
        logfunc(f'freenet Mail: could not read {path}: {error}')
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
    text = '\n'.join(line for line in lines if line)
    return text


def _addresses(value):
    """A JSON list of address objects as 'name <email>' lines; the value as stored otherwise."""
    if value in (None, ''):
        return ''
    try:
        items = json.loads(value)
    except (TypeError, ValueError):
        return value
    if not isinstance(items, list):
        return value
    out = []
    for item in items:
        if not isinstance(item, dict):
            out.append(str(item))
            continue
        email = item.get('email') or ''
        name = item.get('name') or item.get('realname') or ''
        out.append(f'{name} <{email}>' if name and email else name or email)
    return '\n'.join(out)


def _user(relative_path):
    """The Android user of an app data path, read from a rollback snapshot path too; 0 if none."""
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK.search(str(relative_path).replace('\\', '/'))
    return match.group(2) if match else '0'


def _databases(context, name):
    """{(store key, user): [copies of the database]} for the app's databases of this name."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.basename(path) != name or is_sqlite_sidecar(path):
            continue
        relative = context.get_relative_path(path)
        key = canonical_path(os.path.dirname(relative))[0]
        stores.setdefault((key, _user(relative)), []).append(path)
    return dict(sorted(stores.items()))


def _union(context, paths, query):
    return union_view_rows(context, [(path, _rows(path, query)) for path in paths])


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


def _saved_file(context, uri):
    """The staged copies of the shared-storage file a file:// URI names, and whether it names one.

    The file is looked up in the extraction by its path below the user's shared storage, so no
    pattern of this module has to match the whole Download folder."""
    if not uri or not str(uri).startswith('file://'):
        return [], False
    text = urllib.parse.unquote(str(uri)[len('file://'):])
    match = _STORAGE.match(text)
    if not match:
        return [], False
    user, below = match.groups()
    pattern = f'*/{user}/{glob.escape(below)}'
    found = context.get_seeker().search(pattern)
    found = [str(path) for path in (found or []) if os.path.isfile(str(path))]
    return sorted(set(found)), True


def _media(cache, path, name):
    if path not in cache:
        cache[path] = (check_in_media(path, name) or '', _sniff(path))
    return cache[path]


@artifact_processor
def freenet_mail_messages(context):
    data_list = []
    sources = []
    for (_key, user), paths in _databases(context, 'emaildb.db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            folders = {fid: (name, ftype) for fid, name, ftype in _union(
                context, one_copy, 'SELECT folder_id, display_name, type FROM folders')}
            accounts = {aid: email for aid, email in _union(
                context, one_copy, 'SELECT account_id, email FROM accounts')}
            for row in _union(context, one_copy, '''
                    SELECT date, message_folder_id, message_folder_account_id, from_name, from_email,
                           "to", cc, bcc, subject, preview, body, is_html, is_seen, has_attachments,
                           is_answered, is_forwarded, status, message_type, message_uid
                    FROM message ORDER BY date'''):
                (date, folder_id, account_id, from_name, from_email, to, cc, bcc, subject, preview,
                 body, is_html, seen, has_att, answered, forwarded, status, mtype, uid) = row
                folder, ftype = folders.get(folder_id, ('', ''))
                text = _html_text(body) if is_html else _blank(body)
                rows.append((
                    _to_utc(date, True), folder, ftype, accounts.get(account_id, ''),
                    _blank(from_name), _blank(from_email), _addresses(to), _addresses(cc),
                    _addresses(bcc), _blank(subject), _blank(preview), text,
                    'HTML' if is_html else 'Plain' if is_html is not None else '',
                    _yes_no(seen), _yes_no(has_att), _yes_no(answered), _yes_no(forwarded),
                    _blank(status), _blank(mtype), user,
                    _blank(uid), _blank(folder_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Date', 'datetime'), 'Folder', 'Folder Type', 'Account Email', 'From Name', 'From Email',
        'To', 'Cc', 'Bcc', 'Subject', 'Preview', 'Body Text', 'Body Format', 'Seen',
        'Has Attachments', 'Answered', 'Forwarded', 'Status (as stored)',
        'Message Type (as stored)', 'Android User',
        'Message UID', 'Folder ID')
    return data_headers, data_list, '\n'.join(sources)


def _legacy_attachments(context, paths):
    return _union(context, paths, '''
        SELECT mail, _id, name, type, size, is_inline, download_finished, local_file_path
        FROM attachment ORDER BY mail, part_id, _id''')


@artifact_processor
def freenet_mail_legacy_messages(context):
    data_list = []
    sources = []
    cache = {}
    for (_key, user), paths in _databases(context, 'mail.db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            folders = {(email, fid): title for email, fid, title in _union(
                context, one_copy, 'SELECT email, folder_id, title FROM folder')}
            bodies = {}
            for mail_id, html, plain in _union(
                    context, one_copy, 'SELECT mail_hash_id, html, plain FROM mail_body ORDER BY _id'):
                bodies.setdefault(mail_id, []).append((html, plain))
            media_by_mail = {}
            count_by_mail = {}
            for mail_id, _att, name, _type, _size, _inline, _done, uri in \
                    _legacy_attachments(context, one_copy):
                count_by_mail[mail_id] = count_by_mail.get(mail_id, 0) + 1
                copies, _named = _saved_file(context, uri)
                if copies and mail_id not in media_by_mail:
                    sources.append(copies[0])
                    media_by_mail[mail_id] = _media(cache, copies[0], name or os.path.basename(copies[0]))[0]
            mail_ids = set()
            for row in _union(context, one_copy, '''
                    SELECT received_date, send_date, email, folder_id, "from", "to", cc, bcc, replyto,
                           subject, unseen, answered, deleted, has_attachment, store, size, _id
                    FROM mail ORDER BY received_date'''):
                (received, sent, email, folder_id, sender, to, cc, bcc, reply_to, subject, unseen,
                 answered, deleted, has_att, store, size, mail_id) = row
                mail_ids.add(mail_id)
                texts = bodies.get(mail_id) or [(None, None)]
                for html, plain in texts:
                    text = plain if plain else _html_text(html)
                    rows.append((
                        _to_utc(received, False), _to_utc(sent, False), folders.get((email, folder_id), ''),
                        _blank(email), _addresses(sender), _addresses(to), _addresses(cc), _addresses(bcc),
                        _addresses(reply_to), _blank(subject), _blank(text),
                        media_by_mail.get(mail_id, ''), count_by_mail.get(mail_id, 0),
                        _yes_no(unseen), _yes_no(answered), _yes_no(deleted), _yes_no(has_att),
                        _blank(store), _blank(size), 'Yes', user, _blank(mail_id)))
            for mail_id, texts in bodies.items():
                if mail_id in mail_ids:
                    continue
                for html, plain in texts:
                    text = plain if plain else _html_text(html)
                    rows.append((
                        '', '', '', '', '', '', '', '', '', '', _blank(text), '', '', '', '', '', '', '',
                        '', 'No', user, _blank(mail_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Received (received_date)', 'datetime'), ('Sent (send_date)', 'datetime'), 'Folder',
        'Account Email', 'From', 'To', 'Cc', 'Bcc', 'Reply To', 'Subject', 'Body Text',
        ('Attachment', 'media'), 'Attachment Count', 'Unseen', 'Answered',
        'Deleted', 'Has Attachment', 'Store (as stored)',
        'Size (as stored)', 'In mail Table', 'Android User', 'Mail ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def freenet_mail_legacy_attachments(context):
    data_list = []
    sources = []
    cache = {}
    for (_key, user), paths in _databases(context, 'mail.db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            mails = {mail_id: (received, subject) for mail_id, received, subject in _union(
                context, one_copy, 'SELECT _id, received_date, subject FROM mail')}
            for mail_id, att_id, name, ctype, size, inline, done, uri in \
                    _legacy_attachments(context, one_copy):
                received, subject = mails.get(mail_id, (None, ''))
                copies, named = _saved_file(context, uri)
                for copy in copies or [None]:
                    if copy:
                        sources.append(copy)
                        media, media_format = _media(cache, copy, name or os.path.basename(copy))
                        try:
                            file_size = os.path.getsize(copy)
                        except OSError:
                            file_size = ''
                    else:
                        media, file_size = '', ''
                        media_format = 'File not in extraction' if named else ''
                    rows.append((
                        _to_utc(received, False), media, media_format, _blank(name), _blank(ctype),
                        _blank(size), file_size, _yes_no(inline), _yes_no(done),
                        urllib.parse.unquote(str(uri)) if uri else '', _blank(subject),
                        'Yes' if mail_id in mails else 'No', user, _blank(mail_id), _blank(att_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Mail Received (received_date)', 'datetime'), ('Media', 'media'), 'Media Format', 'Name',
        'Content Type', 'Size (as stored)', 'File Size (bytes)', 'Inline',
        'Download Finished', 'Saved File URI', 'Mail Subject', 'Mail in mail Table',
        'Android User', 'Mail ID', 'Attachment ID')
    return data_headers, data_list, '\n'.join(sources)
