__artifacts_v2__ = {
    "mailru_messages": {
        "name": "Mail.ru Mail - Messages",
        "description": (
            "Mails held in mailbox_db by the Mail.ru Mail app, with their folder, body text and the "
            "first saved attachment file."),
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the Mail.ru Mail APK held in the extraction, version code "
            "141709 as the device's packages.xml records it, decompiled with jadx; the entity classes "
            "under ru/mail/data/entities are not obfuscated. The app's mail database is mailbox_db "
            "(SqliteHelper.java:44), written through ORMLite. One row per row of the mail_message "
            "table, joined to the mail_message_content row with the same account and _id and to the "
            "folder row with the same account whose _id is mFolder (MailMessage.java:113 and 139, "
            "MailBoxFolder.java:109 and 116). Date is date, which the app names COL_NAME_DATE_SERV "
            "(MailMessage.java:54) and stores as a Date in Unix milliseconds (ORMLite DATE_LONG, "
            "MailMessage.java:128-129); in the test data it equalled the content table's date_full on "
            "every mail. Folder and Folder Type are the folder row's name and type "
            "(MailBoxFolder.java:143 and 173). From is from_full (MailMessage.java:116); To, Cc, Bcc "
            "and Reply To are the content table's to, copy, blind_copy and reply_to, all as stored. "
            "Subject is the content table's subject, or the mail_message theme (MailMessage.java:94) "
            "when there is no content row or its subject is NULL; every mail in the test data had a "
            "content row. Snippet is snippet (MailMessage.java:251). Body Text is let_body_plain, or "
            "when it is empty let_body_html with tags removed, script and style content dropped, "
            "character references decoded, whitespace collapsed and line breaks placed at block tags; "
            "nothing is rendered or linked, and the database copied into the report's data folder holds "
            "the HTML as stored. In the test data let_body_plain held text on every mail, so the HTML "
            "path was not exercised there. Unread is is_new, the value the app's isUnread() returns "
            "(MailMessage.java:835-836). Flagged, Replied, Forwarded, Pinned and Newsletter are "
            "is_flagged, is_replied, is_forwarded, is_pinned and is_newsletter (MailMessage.java:171, "
            "201, 174, 195 and 186), 0 and 1 shown as No and Yes, and Has Content (as stored) is "
            "has_content as stored; what sets them was not traced. In the test data has_content was 0 "
            "on 14 of 19 mails that each had a content row with body text, so it does not show whether "
            "a body is stored. Message ID and Thread ID are _id and mail_thread_id as stored. "
            "Attachment shows the first saved file of the mail's attachments, found as in Mail.ru Mail "
            "- Attachments, and Attachment Count counts the mails_attachments rows of its content row. "
            "Not read: mail_message send_date (0 on every mail in the test data), the content table's "
            "is_unreaded (1 on every mail in the test data) and formatted_html_body and amp_body, and "
            "the mail_thread, mail_thread_representation, push_filter_item, push_filter_group, "
            "profile_data and mail_entity_reference tables, and the accounts table. Each database copy "
            "is read on its own, with its own lookup rows, and the copies are then joined: a copy under "
            "another storage spelling is read when it differs, and a row both hold appears once. A "
            "rollback snapshot that differs from the live copy is read separately, so a row both hold "
            "appears twice. The test data held one copy of each database, so neither case was "
            "exercised. Android User is read from the database's path; a path that names no user shows "
            "0, and in the test data every row shows 0 that way."),
        "paths": ('*/ru.mail.mailapp/databases/mailbox_db*',
                  '*/Android/data/ru.mail.mailapp/files/accounts/*/attachments/*',
                  '*/Android/data/ru.mail.mailapp/cache/accounts/*/attachments/*'),
        "output_types": "standard",
        "multiline_columns": ["Body Text"],
        "artifact_icon": "mail",
    },
    "mailru_attachments": {
        "name": "Mail.ru Mail - Attachments",
        "description": "Attachments listed in mailbox_db by the Mail.ru Mail app, and the attachment "
                       "files it saved, including files no row names.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the Mail.ru Mail APK held in the extraction, version code "
            "141709 as the device's packages.xml records it, decompiled with jadx; the entity classes "
            "under ru/mail/data/entities are not obfuscated. The app's mail database is mailbox_db "
            "(SqliteHelper.java:44), written through ORMLite. One row per row of the mails_attachments "
            "table for each saved copy of its file found, or one row when none is, joined to its "
            "mail_message_content row by mMessageContent_id (Attach.java:31 and 85) and from it to the "
            "mail_message row for Mail Date; and one row per file under the app's "
            "accounts/.../attachments folders that no row names. The app saves an incoming attachment "
            "under accounts/<hash of the account>/attachments/<hash>/... "
            "(AndroidDirectoryRepository.java:314-327) and computes that path when it parses a mail's "
            "attachments (AttachParser.java:67, AttachmentHelper.java:196-197), storing it in "
            "path_to_prefetch (PrefetchableAttach.java:6), so a value there does not show the file was "
            "saved; it is relative to the app's external files folder on Android 10 or later and to its "
            "external cache folder before that (AndroidDirectoryRepository.java:309, "
            "DirectoryUtils.java:79-80), so both are looked up. Name, Content Type, Size (as stored) "
            "and Disposition (as stored) are name, content_type, content_length and disposition "
            "(Attach.java:61-74). Media Format is read from the file's first bytes. File not in "
            "extraction marks a row whose path_to_prefetch names no file among those this artifact "
            "matched; it does not show the file was ever saved, and no row was in that state in the "
            "test data. The test data held no file without a row. The .nomedia files the app writes "
            "beside them are not listed. For a file no row names, Name is the file's own name and Saved "
            "Path its path below the app's external folder. Not read: the app's images folder (an image "
            "cache), remote (the app's outgoing attachments folder, "
            "AndroidDirectoryRepository.java:43), ext_attachments (temporary thumbnails, "
            "AndroidDirectoryRepository.java:50) and shared folders. Each database copy is read on its "
            "own, with its own lookup rows, and the copies are then joined: a copy under another "
            "storage spelling is read when it differs, and a row both hold appears once. A rollback "
            "snapshot that differs from the live copy is read separately, so a row both hold appears "
            "twice. The test data held one copy of each database, so neither case was exercised. "
            "Android User is read from the database's path, and for a file no row names from the shared "
            "storage user folder in the file's path (media/<n>/ or storage/emulated/<n>/); saved files "
            "are matched to a database row of the same user. A path that names no user shows 0."),
        "paths": ('*/ru.mail.mailapp/databases/mailbox_db*',
                  '*/Android/data/ru.mail.mailapp/files/accounts/*/attachments/*',
                  '*/Android/data/ru.mail.mailapp/cache/accounts/*/attachments/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
    "mailru_send_message_records": {
        "name": "Mail.ru Mail - Send Message Records",
        "description": (
            "Rows of the send_message_persist_parameters table of the Mail.ru Mail app: a message with "
            "its recipients and body, the names of the files listed for it, and the first of those "
            "files found."),
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the Mail.ru Mail APK held in the extraction, version code "
            "141709 as the device's packages.xml records it, decompiled with jadx; the entity classes "
            "under ru/mail/data/entities are not obfuscated. The app's mail database is mailbox_db "
            "(SqliteHelper.java:44), written through ORMLite. One row per row of the "
            "send_message_persist_parameters table, the table the app's SendMessagePersistParamsImpl "
            "entity maps to (SendMessagePersistParamsImpl.java:35); whether a row was sent, saved as a "
            "draft or is waiting was not established beyond its state. Created is create_date, which "
            "the app sets from the device clock in Unix milliseconds each time "
            "InsertSendMessageParamsCmd writes the row (InsertSendMessageParamsCmd.java:52-53, "
            "SendMessagePersistParamsImpl.java:95-96); that command creates or updates, so the value is "
            "the time of the last such write. State (as stored) is state, an enum stored by name "
            "(SendMessagePersistParamsImpl.java:185), and Send Type (as stored) is send_message_type. "
            "From, To, Cc, Bcc and Subject are as stored, and Body Text is message_body_plain, or when "
            "it is empty message_body_html with tags removed, script and style content dropped, "
            "character references decoded, whitespace collapsed and line breaks placed at block tags; "
            "nothing is rendered or linked, and the database copied into the report's data folder holds "
            "the HTML as stored. The one row in the test data held message_body_plain, so the HTML path "
            "was not exercised there. Attachment Count and Attachment Names come from the "
            "attach_persist_info rows whose send_params_id is the row's id "
            "(AttachPersistInfo.java:46-67); Attachment Names are full_name, or the file name of "
            "file_path when full_name is empty, and Attachment shows the first of their file_path files "
            "the extraction holds: a /storage/emulated/<user>/... path is looked up as a file whose "
            "path in the extraction ends in <user>/<the rest of that path>. That file can have been "
            "changed after the row was written. Sending Error is sending_error_message. Each database "
            "copy is read on its own, with its own lookup rows, and the copies are then joined: a copy "
            "under another storage spelling is read when it differs, and a row both hold appears once. "
            "A rollback snapshot that differs from the live copy is read separately, so a row both hold "
            "appears twice. The test data held one copy of each database, so neither case was "
            "exercised. Android User is read from the database's path; a path that names no user shows "
            "0, and in the test data every row shows 0 that way."),
        "paths": ('*/ru.mail.mailapp/databases/mailbox_db*',),
        "output_types": "standard",
        "multiline_columns": ["Body Text", "Attachment Names"],
        "artifact_icon": "send",
    },
    "mailru_contacts": {
        "name": "Mail.ru Mail - Contacts",
        "description": "Contacts held in mail_contacts_v2.db by the Mail.ru Mail app.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Class and line references are to the Mail.ru Mail APK held in the extraction, version code "
            "141709 as the device's packages.xml records it, decompiled with jadx; the cited classes "
            "are not obfuscated. The app opens mail_contacts_v2.db as a Room database "
            "(ContactsRoomDb.java:32 and 46). One row per row of the contact table, each reported "
            "column as stored; Name is the name column. Not read: _id, email_words, name_words, _data, "
            "gender and boss, and the contact_phone and socials_table_name tables, which were empty in "
            "the test data. What sets priority and which contacts the table receives were not traced. "
            "In the test data, of the columns reported, only display_name, email, priority, account and "
            "server_id held values. Each database copy is read on its own, with its own lookup rows, "
            "and the copies are then joined: a copy under another storage spelling is read when it "
            "differs, and a row both hold appears once. A rollback snapshot that differs from the live "
            "copy is read separately, so a row both hold appears twice. The test data held one copy of "
            "each database, so neither case was exercised. Android User is read from the database's "
            "path; a path that names no user shows 0, and in the test data every row shows 0 that way."),
        "paths": ('*/ru.mail.mailapp/databases/mail_contacts_v2.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}

import glob
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
from scripts.ilapfuncs import (artifact_processor, check_in_media, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc)

PACKAGE = 'ru.mail.mailapp'
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_STORAGE = re.compile(r'^/storage/emulated/(\d+)/(.+)$')
# The user folder of shared storage in an extraction path: media/<n>/ or storage/emulated/<n>/.
_SHARED_USER = re.compile(r'(?:^|/)(?:media|storage/emulated)/(\d+)/Android/data/')
_BLOCKS = {'br', 'p', 'div', 'tr', 'td', 'th', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'blockquote'}


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
        logfunc(f'Mail.ru Mail: could not read {path}: {error}')
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


def _user(relative_path):
    """The Android user of a path, read from a rollback snapshot path too; 0 if none."""
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK.search(str(relative_path).replace('\\', '/'))
    return match.group(2) if match else '0'


def _databases(context, name):
    """{(store key, user): [copies]} for the app's databases of this name."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.basename(path) != name or is_sqlite_sidecar(path):
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        key = canonical_path(os.path.dirname(relative))[0]
        stores.setdefault((key, _user(relative)), []).append(path)
    return dict(sorted(stores.items()))


def _attachment_files(context):
    """{(user, path below the app's external folder): [staged copies]} for saved attachments.

    Keyed by the evidence name, since staging rewrites some characters of a path."""
    files = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.isdir(path) or os.path.basename(path) == '.nomedia':
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        marker = f'/Android/data/{PACKAGE}/'
        if marker not in relative:
            continue
        below = relative.split(marker, 1)[1]
        parts = below.split('/')
        if len(parts) < 4 or parts[0] not in ('files', 'cache') or parts[1] != 'accounts' \
                or parts[3] != 'attachments':
            continue
        match = _SHARED_USER.search(relative)
        files.setdefault((match.group(1) if match else _user(relative), below), []).append(path)
    return files


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


def _media(cache, path, name):
    if path not in cache:
        cache[path] = (check_in_media(path, name) or '', _sniff(path))
    return cache[path]


def _prefetched(files, user, prefetch_path):
    """The saved copies a path_to_prefetch value names, below files/ and cache/, and their keys."""
    if not prefetch_path:
        return [], []
    rel = str(prefetch_path).lstrip('/')
    keys = [(user, f'{base}/{rel}') for base in ('files', 'cache') if (user, f'{base}/{rel}') in files]
    return [copy for key in keys for copy in files[key]], keys


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return ''


def _attachment_rows(context, paths):
    return _union(context, paths, '''
        SELECT a.mMessageContent_id, a._id, a.name, a.content_type, a.content_length, a.disposition,
               a.path_to_prefetch, COALESCE(c.account, a.account), c._id, c.subject, m.date
        FROM mails_attachments a
        LEFT JOIN mail_message_content c ON c.id = a.mMessageContent_id
        LEFT JOIN mail_message m ON m.account = c.account AND m._id = c._id
        ORDER BY a.mMessageContent_id, a.id''')


@artifact_processor
def mailru_messages(context):
    data_list = []
    sources = []
    cache = {}
    files = _attachment_files(context)
    for (_key, user), paths in _databases(context, 'mailbox_db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            media_by_content = {}
            count_by_content = {}
            for row in _attachment_rows(context, one_copy):
                content_id, name, prefetch = row[0], row[2], row[6]
                count_by_content[content_id] = count_by_content.get(content_id, 0) + 1
                copies, _found = _prefetched(files, user, prefetch)
                if copies and content_id not in media_by_content:
                    sources.append(copies[0])
                    media_by_content[content_id] = _media(cache, copies[0], name or os.path.basename(copies[0]))[0]
            for row in _union(context, one_copy, '''
                    SELECT m.date, f.name, f.type, m.account, m.from_full, c."to", c.copy, c.blind_copy,
                           c.reply_to, COALESCE(c.subject, m.theme), m.snippet, c.let_body_plain,
                           c.let_body_html, c.id, m.is_new, m.is_flagged, m.is_replied, m.is_forwarded,
                           m.is_pinned, m.is_newsletter, m.has_content, m._id, m.mail_thread_id
                    FROM mail_message m
                    LEFT JOIN mail_message_content c ON c.account = m.account AND c._id = m._id
                    LEFT JOIN folder f ON f.account = m.account AND f._id = m.mFolder
                    ORDER BY m.date'''):
                (date, folder, ftype, account, sender, to, cc, bcc, reply_to, subject, snippet, plain,
                 html, content_id, unread, flagged, replied, forwarded, pinned, newsletter, has_content,
                 message_id, thread_id) = row
                text = plain if plain else _html_text(html)
                rows.append((
                    _ms_to_utc(date), _blank(folder), _blank(ftype), _blank(account), _blank(sender),
                    _blank(to), _blank(cc), _blank(bcc), _blank(reply_to), _blank(subject),
                    _blank(snippet), _blank(text), media_by_content.get(content_id, ''),
                    count_by_content.get(content_id, 0) if content_id is not None else '',
                    _yes_no(unread), _yes_no(flagged), _yes_no(replied), _yes_no(forwarded),
                    _yes_no(pinned), _yes_no(newsletter), _blank(has_content), user,
                    _blank(message_id), _blank(thread_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Date', 'datetime'), 'Folder', 'Folder Type', 'Account', 'From', 'To', 'Cc', 'Bcc',
        'Reply To', 'Subject', 'Snippet', 'Body Text', ('Attachment', 'media'), 'Attachment Count',
        'Unread', 'Flagged', 'Replied', 'Forwarded', 'Pinned', 'Newsletter', 'Has Content (as stored)',
        'Android User', 'Message ID', 'Thread ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mailru_attachments(context):
    data_list = []
    sources = []
    cache = {}
    files = _attachment_files(context)
    named = set()
    for (_key, user), paths in _databases(context, 'mailbox_db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            for row in _attachment_rows(context, one_copy):
                (_content_id, att_id, name, ctype, length, disposition, prefetch, account, message_id,
                 subject, date) = row
                copies, found = _prefetched(files, user, prefetch)
                named.update(found)
                for copy in copies or [None]:
                    if copy:
                        sources.append(copy)
                        media, media_format = _media(cache, copy, name or os.path.basename(copy))
                        file_size = _size(copy)
                    else:
                        media, file_size = '', ''
                        media_format = 'File not in extraction' if prefetch else ''
                    rows.append((
                        _ms_to_utc(date), media, media_format, _blank(name), _blank(ctype), _blank(length),
                        file_size, _blank(disposition), _blank(prefetch), _blank(subject),
                        _blank(account), 'Yes', user, _blank(message_id), _blank(att_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    for key, copies in sorted(files.items()):
        if key in named:
            continue
        user, below = key
        for copy in copies:
            sources.append(copy)
            name = below.rsplit('/', 1)[-1]
            media, media_format = _media(cache, copy, name)
            data_list.append((
                '', media, media_format, name, '', '', _size(copy), '', below, '', '', 'No', user, '',
                ''))
    data_headers = (
        ('Mail Date', 'datetime'), ('Media', 'media'), 'Media Format', 'Name', 'Content Type',
        'Size (as stored)', 'File Size (bytes)', 'Disposition (as stored)', 'Saved Path',
        'Mail Subject', 'Account', 'Named by a Row', 'Android User', 'Message ID', 'Attachment ID')
    return data_headers, data_list, '\n'.join(sources)


def _shared_storage_file(context, path):
    """The staged copies of a /storage/emulated/<user>/... file, looked up by that path's tail."""
    match = _STORAGE.match(str(path or ''))
    if not match:
        return [], False
    user, below = match.groups()
    found = context.get_seeker().search(f'*/{user}/{glob.escape(below)}')
    return sorted({str(p) for p in (found or []) if os.path.isfile(str(p))}), True


@artifact_processor
def mailru_send_message_records(context):
    data_list = []
    sources = []
    cache = {}
    for (_key, user), paths in _databases(context, 'mailbox_db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            attached = {}
            for params_id, file_path, full_name, size in _union(context, one_copy, '''
                    SELECT send_params_id, file_path, full_name, size FROM attach_persist_info
                    ORDER BY send_params_id, id'''):
                attached.setdefault(params_id, []).append((file_path, full_name, size))
            for row in _union(context, one_copy, '''
                    SELECT create_date, state, send_message_type, account, "from", "to", cc, bcc, subject,
                           message_body_plain, message_body_html, sending_error_message, id
                    FROM send_message_persist_parameters ORDER BY create_date'''):
                (created, state, mtype, account, sender, to, cc, bcc, subject, plain, html, error,
                 params_id) = row
                files = attached.get(params_id, [])
                media, names = '', []
                for file_path, full_name, _size_value in files:
                    names.append(full_name or os.path.basename(str(file_path or '')))
                    copies, _named = _shared_storage_file(context, file_path)
                    if copies and not media:
                        sources.append(copies[0])
                        media = _media(cache, copies[0], full_name or os.path.basename(copies[0]))[0]
                rows.append((
                    _ms_to_utc(created), _blank(state), _blank(mtype), _blank(account), _blank(sender),
                    _blank(to), _blank(cc), _blank(bcc), _blank(subject),
                    _blank(plain) if plain else _html_text(html), media, len(files), '\n'.join(names),
                    _blank(error), user, _blank(params_id)))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        ('Created', 'datetime'), 'State (as stored)', 'Send Type (as stored)', 'Account', 'From', 'To',
        'Cc', 'Bcc', 'Subject', 'Body Text', ('Attachment', 'media'), 'Attachment Count',
        'Attachment Names', 'Sending Error', 'Android User', 'Row ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mailru_contacts(context):
    data_list = []
    sources = []
    for (_key, user), paths in _databases(context, 'mail_contacts_v2.db').items():
        sources.extend(paths)
        # Rows are completed inside each copy, then the copies are joined.
        per_copy = []
        for path in paths:
            rows = []
            one_copy = [path]
            for row in _union(context, one_copy, '''
                    SELECT display_name, name, lastname, email, company, job_title, birthday, address,
                           comment, labels, priority, account, server_id
                    FROM contact ORDER BY account, priority DESC, _id'''):
                rows.append(tuple(_blank(value) for value in row) + (user,))
            per_copy.append((path, rows))
        data_list.extend(union_view_rows(context, per_copy))
    data_headers = (
        'Display Name', 'Name', 'Last Name', 'Email', 'Company', 'Job Title', 'Birthday',
        'Address', 'Comment', 'Labels', 'Priority (as stored)', 'Account', 'Server ID', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
