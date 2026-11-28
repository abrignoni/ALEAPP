__artifacts_v2__ = {
    "ui_mail_messages": {
        "name": "WEB.DE, GMX and 1&1 Mail - Messages",
        "description": "Rows of the mail table of the WEB.DE, GMX and 1&1 mail apps' mail_room.db, "
                       "with the folder, the account and one cached attachment file or thumbnail "
                       "on the row.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Email",
        "notes": (
            (
            "Reads the mail table of databases/mail_room.db for de.web.mobile.android.mail, "
            "de.gmx.mobile.android.mail and de.eue.mobile.android.mail; App is the package. Class and line "
            "references are to the WEB.DE Mail 9.21.1 APK (version code 405221, base.apk SHA-256 "
            "d6479f844639452f981341c44d363e1bb0fbd1fab1a44d3619869870c0ea00a1) decompiled with jadx 1.5.6, "
            "in com/unitedinternet/portal unless named in full. The GMX and 1&1 apps' mail_room.db has the "
            "same Room identity hash and schema version 30 as WEB.DE's in the test data, so the citations "
            "are read as covering all three; their own APKs were not decompiled. A write-ahead log beside a "
            "database is applied; a database with no log beside it is read alone. When one database is "
            "present under more than one storage path (data/data and data/user/0), a copy is also read when "
            "its database file, or the content of its -wal or -journal, matches no copy already read; a row "
            "equal in every column the query reads is reported once, and a row that differs in any of them "
            "once per version, with no column naming the copy. Folder, Account Email and Attachment come "
            "from lookups in which the first version read wins. Values are compared as read. When a copy "
            "cannot be read as a SQLite database, the failed read is logged, it gives no rows, and the "
            "other copies are still reported; a zero-byte copy gives no rows and the run log gets a no such "
            "table error (read from the code, not run). A rollback snapshot that differs from the live "
            "database is read separately, so a row both hold appears twice. Android User is read from the "
            "path, including a rollback snapshot under data/misc_ce/<n>/rollback or "
            "data/misc_de/<n>/rollback; a path that names no user is read as user 0. The copy handling was "
            "run only on made-up databases in the module's tests. Header Date is the date column, the date "
            "field of the mail header object the server returned, which the app's code calls the sent date "
            "(android/mail/mailsync/data/MessageDataExtractor.java:126-132, "
            "android/mail/mailsync/data/RestMessageHeaderResponseConverter.java:38 and 58). The app stores "
            "0 when the field is absent, shown blank; whether the server copies the mail's Date header "
            "unchanged was not established. Server Internal Date is internalDate, an attribute the server "
            "returns with the mail (MessageDataExtractor.java:134-136, "
            "RestMessageHeaderResponseConverter.java:49). Both are read as Unix milliseconds, which the "
            "stored 13-digit values fit. Sender is sender, the sender address in display form, and From is "
            "email_from, the same address in full form, both from the header's from field "
            "(MessageDataExtractor.java:31-52 and 180-191); when the header has no from value the app "
            "stores a fixed no-sender text in both. At sync the app sets isUnread to the inverse of the "
            "server's seen flag and isAnswered, isForwarded and isStarred to its replied, forwarded and "
            "flagged flags (RestMessageHeaderResponseConverter.java:54-58), shown as Unread, Answered, "
            "Forwarded and Starred. The app also updates these four columns with its own statements "
            "(android/database/room/dao/MailDao_Impl.java:5070-5331); what calls them was not traced, so a "
            "value can be the server's or the app's. None of them records who acted on the mail or when. "
            "Folder and Folder Type are the name and type of the folder row the mail's folderId names; "
            "Folder Type is the folder's type number with the name FolderType gives it "
            "(android/mail/types/FolderType.java:128-136, 187-367, 768 and 797-801): 0 Inbox, 1 Drafts, 2 "
            "Sent, 3 Trash, 4 Outbox, 5 Spam, 6 Unknown, 7 Default, 8 Archive, 9 Favorites; any other "
            "number is shown as stored. Both are blank when the database holds no folder row with that id. "
            "Account Email is the email of the account's default sender identity in identitiy_db (the file "
            "name is spelled so), or of its first identity when none is marked default; it is blank when "
            "that database or identity is absent. Text Body is textbody and Preview is preview, both as "
            "stored; whether textbody holds the whole plain-text part or a shortened text was not traced. "
            "In the test data preview was at most 300 characters and matched the start of textbody in 116 "
            "of 591 rows that have one. HTML Body is Found or File not in extraction when the body column "
            "names a file in the app's folder, and blank otherwise; the file is the one BodyFileHelper "
            "writes (core/BodyFileHelper.java:17 and 69-83), and WEB.DE, GMX and 1&1 Mail - Body Files "
            "lists those files. Attachment is the file of the mail's first attachment row that has a cached "
            "file or thumbnail in the extraction: the file when present, else that row's first thumbnail, "
            "as in WEB.DE, GMX and 1&1 Mail - Attachments. Attachment Count counts the mail's attachment "
            "rows. Mail Type is mailType as stored. Synced mail is written as email "
            "(RestMessageHeaderResponseConverter.java:58); the other values in the test data are names in "
            "the app's MessageType list (model/MessageType.java:17-26), which its inbox advertising code "
            "also reads (android/mail/advertising/data/network/inboxad/InboxAdResponseConverterKt.java:14 "
            "and 20). What writes those rows was not traced, so they are reported with the mails. Priority "
            "is as stored. Not reported, with the reason: the drafts and outbox databases, user content "
            "that held no rows in the test data, so there was nothing to check a reader against; the "
            "cloud storage databases (<account>_resources.db, <account>_timeline.db, transfer.db), "
            "which belong to the provider's online storage feature and are left for an artifact of "
            "their own; the full-text index mailSearch, which repeats mail fields and was empty; the "
            "virtual folder tables, which group the same mails into app views such as unread and "
            "favorites; and the app's advertising, in-app purchase, monitoring and tracking stores, "
            "which hold app content and telemetry rather than mail. Other databases in the folder, "
            "among them mail_search_suggestions.db, track_and_trace_v3.db, mail_pcl.db, "
            "operation_store.db and draft_operation_store.db, were not examined.")),
        "paths": ('*/de.web.mobile.android.mail/databases/mail_room.db*',
                  '*/de.gmx.mobile.android.mail/databases/mail_room.db*',
                  '*/de.eue.mobile.android.mail/databases/mail_room.db*',
                  '*/de.web.mobile.android.mail/databases/identitiy_db*',
                  '*/de.gmx.mobile.android.mail/databases/identitiy_db*',
                  '*/de.eue.mobile.android.mail/databases/identitiy_db*',
                  '*/de.web.mobile.android.mail/cache/attachment_*',
                  '*/de.gmx.mobile.android.mail/cache/attachment_*',
                  '*/de.eue.mobile.android.mail/cache/attachment_*',
                  '*/de.web.mobile.android.mail/cache/room_mail_bodies/*',
                  '*/de.gmx.mobile.android.mail/cache/room_mail_bodies/*',
                  '*/de.eue.mobile.android.mail/cache/room_mail_bodies/*'),
        "output_types": "standard",
        "artifact_icon": "mail",
    },
    "ui_mail_attachments": {
        "name": "WEB.DE, GMX and 1&1 Mail - Attachments",
        "description": "Attachment rows of the WEB.DE, GMX and 1&1 mail apps' mail_room.db with the "
                       "cached file and thumbnail, and cached attachment files no row names.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Email",
        "notes": (
            (
            "Class and line references and the reading of database copies are as in WEB.DE, GMX and 1&1 "
            "Mail - Messages. One row per attachment row, then one row per cached attachment or thumbnail "
            "file no attachment row names (In mail_room.db No). Media is the file the attachment's "
            "localPathUri names, looked up below the same app data folder; the app downloads attachments to "
            "its cache folder under an attachment_ prefix and stores that path in localPathUri "
            "(commands/mail/rest/DownloadAttachmentRestCommand.java:33, 98-104 and 127-128). Thumbnail is "
            "the cached thumbnail the app names from the attachment's uri: attachment_thumbnail_, the uri "
            "with ../ and Mail/ removed and / turned into _, then the width and height "
            "(android/mail/compose/rest/ComposeNetworkExecutor.java:43 and 259-268, "
            "commands/mail/rest/DownloadAttachmentThumbnailCommand.java:33 and 94-100). An attachment row is "
            "listed once for each cached thumbnail file: each size, and each copy whose bytes differ. Media Format is read from the file's first bytes. "
            "File not in extraction means the row names a file that was not found; a blank means the row "
            "names no file inside the app's data folder. Name, Content Type and Size are as stored; Inline "
            "is the stored 0 or 1 shown as No or Yes. Status is as stored; in the test data the rows with a "
            "local file had status 2 and the rest 1, and the download code writes 2 with the local path and "
            "1 after a failed download (DownloadAttachmentRestCommand.java:78, 85 and 104), but what each "
            "value means was not traced further. Copies of one file under more than one storage path are "
            "each listed when their bytes differ; their rows can differ in Media, Media Format and File "
            "Size, and no column shows the storage path. No unnamed cached file was in the test data.")),
        "paths": ('*/de.web.mobile.android.mail/databases/mail_room.db*',
                  '*/de.gmx.mobile.android.mail/databases/mail_room.db*',
                  '*/de.eue.mobile.android.mail/databases/mail_room.db*',
                  '*/de.web.mobile.android.mail/databases/identitiy_db*',
                  '*/de.gmx.mobile.android.mail/databases/identitiy_db*',
                  '*/de.eue.mobile.android.mail/databases/identitiy_db*',
                  '*/de.web.mobile.android.mail/cache/attachment_*',
                  '*/de.gmx.mobile.android.mail/cache/attachment_*',
                  '*/de.eue.mobile.android.mail/cache/attachment_*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
    "ui_mail_body_files": {
        "name": "WEB.DE, GMX and 1&1 Mail - Body Files",
        "description": "Cached HTML mail bodies of the WEB.DE, GMX and 1&1 mail apps, with the mail "
                       "that names each.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Email",
        "notes": (
            (
            (
            "Class and line references and the reading of database copies are as in WEB.DE, GMX and 1&1 "
            "Mail - Messages. One row per file in cache/room_mail_bodies/<account uuid>/, the folder the "
            "app writes mail bodies to as .html files (core/BodyFileHelper.java:17 and 69-83). The app "
            "names a body file by the last segment of the mail's remote_mail_uid "
            "(commands/mail/rest/DownloadBodyRestCommand.java:85 and 156-159, BodyFileHelper.java:81-83), "
            "19 digits in the test data. BodyFileHelper also has a method that names a file by the current "
            "time (BodyFileHelper.java:77-79); no caller was found. The name is not read as a date. Named "
            "by a Mail is Yes when a row of the mail table names the file in its body column, and Mail "
            "Header Date, Mail Subject and Mail ID are then that mail's; No marks a file that no row of the "
            "mail table read names. The HTML is not rendered here and the report does not link to it; every "
            "value is escaped, so no link or image in a body is live in the report. The files are copied "
            "into the report's data folder as evidence. In the test data 122 of the 142 files referenced "
            "remote addresses, so opening one directly in a browser can contact those hosts; open them with "
            "remote content blocked. Size is the file size."))),
        "paths": ('*/de.web.mobile.android.mail/databases/mail_room.db*',
                  '*/de.gmx.mobile.android.mail/databases/mail_room.db*',
                  '*/de.eue.mobile.android.mail/databases/mail_room.db*',
                  '*/de.web.mobile.android.mail/cache/room_mail_bodies/*',
                  '*/de.gmx.mobile.android.mail/cache/room_mail_bodies/*',
                  '*/de.eue.mobile.android.mail/cache/room_mail_bodies/*'),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "ui_mail_accounts": {
        "name": "WEB.DE, GMX and 1&1 Mail - Identities",
        "description": "Sender identities the WEB.DE, GMX and 1&1 mail apps stored in identitiy_db.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Email",
        "notes": (
            (
            "Rows of the Identity table of databases/identitiy_db (the file name is spelled so), read with "
            "the copy handling described in WEB.DE, GMX and 1&1 Mail - Messages. Account ID is accountId, "
            "which in the test data matched the account_id of the mail rows; Name, Email and Type are as "
            "stored, and Default Sender, Default Receiver and Deletable are the stored 0 or 1 shown as No "
            "or Yes. Entry Date is entryDate as stored text; the app code that writes it was not traced. "
            "The id, uri, hasPGPEnabled and signature columns are not reported.")),
        "paths": ('*/de.web.mobile.android.mail/databases/identitiy_db*',
                  '*/de.gmx.mobile.android.mail/databases/identitiy_db*',
                  '*/de.eue.mobile.android.mail/databases/identitiy_db*'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "ui_mail_known_receivers": {
        "name": "WEB.DE, GMX and 1&1 Mail - Known Receivers",
        "description": "Addresses the WEB.DE, GMX and 1&1 mail apps stored in their known_receivers "
                       "database.",
        "author": "@AlexisBrignoni, @BrunoFischerGermany, Claude",
        "creation_date": "2026-11-27",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Email",
        "notes": (
            "Rows of the contacts table of databases/known_receivers, read with the copy handling "
            "described in WEB.DE, GMX and 1&1 Mail - Messages. Address is data1 and Display Name is "
            "display_name; Times Contacted and Flags are as stored. The app code that writes the "
            "table was not traced, so what adds an address and what the count counts are not "
            "established."),
        "paths": ('*/de.web.mobile.android.mail/databases/known_receivers*',
                  '*/de.gmx.mobile.android.mail/databases/known_receivers*',
                  '*/de.eue.mobile.android.mail/databases/known_receivers*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}

import hashlib
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import (android_user, canonical_path, union_view_rows,
                                                unique_files)
from scripts.ilapfuncs import (artifact_processor, check_in_media, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc)

PACKAGES = ('de.web.mobile.android.mail', 'de.gmx.mobile.android.mail', 'de.eue.mobile.android.mail')
DATABASES = ('mail_room.db', 'identitiy_db', 'known_receivers')
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ROLLBACK = re.compile(r'(^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_THUMB_SIZE = re.compile(r'_\d+x\d+\.temp$')

# FolderType.ImapFolder and FolderType.Filter values (android/mail/types/FolderType.java).
FOLDER_TYPES = {0: 'Inbox', 1: 'Drafts', 2: 'Sent', 3: 'Trash', 4: 'Outbox', 5: 'Spam',
                6: 'Unknown', 7: 'Default', 8: 'Archive', 9: 'Favorites'}


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


def _rows(path, query):
    """The rows of a query, or [] with a log line when the database cannot be read."""
    try:
        return list(get_sqlite_db_records(path, query))
    except sqlite3.DatabaseError as error:
        logfunc(f'WEB.DE/GMX/1&1 Mail: could not read {path}: {error}')
        return []


def _container(path):
    """(app data folder, package) a staged path belongs to, or (None, None)."""
    parts = os.path.normpath(str(path)).replace('\\', '/').split('/')
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] in PACKAGES:
            return '/'.join(parts[:index + 1]), parts[index]
    return None, None


def _user(relative_path):
    """The Android user of an app data path, read from a rollback snapshot path too; 0 if none."""
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK.search(str(relative_path).replace('\\', '/'))
    return match.group(2) if match else '0'


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


def _stores(context):
    """Per app data folder: package, user, every copy of each database and the cache files.

    A database copy under another storage spelling is kept when it reads differently; the
    artifacts join the rows read from the copies with union_view_rows. Cache files are keyed
    by their path below the app data folder, with byte-identical copies dropped."""
    stores = {}
    for file_found in unique_files(context, keep_differing_views=True):
        path = str(file_found)
        if os.path.isdir(path) or is_sqlite_sidecar(path):
            continue
        container, package = _container(path)
        if not container:
            continue
        tail = path[len(container):].replace('\\', '/').strip('/')
        key = canonical_path(context.get_relative_path(container))[0]
        entry = stores.setdefault(key, {'package': package, 'dbs': {}, 'files': {},
                                        'user': _user(context.get_relative_path(path))})
        parts = tail.split('/')
        if len(parts) == 2 and parts[0] == 'databases' and parts[1] in DATABASES:
            entry['dbs'].setdefault(parts[1], []).append(path)
        elif parts[0] == 'cache' and (
                (len(parts) == 2 and parts[1].startswith('attachment_'))
                or (len(parts) == 4 and parts[1] == 'room_mail_bodies')):
            entry['files'].setdefault(tail, []).append(path)
    for entry in stores.values():
        entry['files'] = {tail: _distinct(paths) for tail, paths in entry['files'].items()}
    return dict(sorted(stores.items()))


def _union(context, entry, name, query):
    return union_view_rows(context, [(path, _rows(path, query)) for path in entry['dbs'].get(name, [])])


def _local_tail(uri, package):
    """The path below the app data folder that a file:// URI into the package names."""
    if not uri or not str(uri).startswith('file://'):
        return None
    marker = f'/{package}/'
    text = str(uri)[len('file://'):]
    if marker not in text:
        return None
    return text.split(marker, 1)[1]


def _thumbnail_prefix(attachment_uri):
    """attachment_thumbnail_ and the uri as the app writes it into the thumbnail's file name."""
    if not attachment_uri:
        return None
    clean = str(attachment_uri).replace('../', '').replace('Mail/', '').replace('/', '_')
    return f'cache/attachment_thumbnail_{clean}'


def _thumbnails(entry, attachment_uri):
    prefix = _thumbnail_prefix(attachment_uri)
    if not prefix:
        return []
    return sorted(tail for tail in entry['files']
                  if tail.startswith(prefix) and _THUMB_SIZE.fullmatch(tail[len(prefix):]))


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


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return ''


def _media(cache, path, name):
    if path not in cache:
        cache[path] = (check_in_media(path, name) or '', _sniff(path))
    return cache[path]


def _identities(context, entry):
    """{account id: email of its default sender identity, else of its first identity}."""
    emails = {}
    for account, email, _default in sorted(
            _union(context, entry, 'identitiy_db',
                   'SELECT accountId, email, isDefaultSender FROM Identity ORDER BY id'),
            key=lambda row: (row[0], not row[2])):
        emails.setdefault(account, email)
    return emails


def _attachment_rows(context, entry):
    return _union(context, entry, 'mail_room.db', '''
        SELECT _id, mailId, name, contentType, size, inline, status, localPathUri, uri
        FROM attachment ORDER BY mailId, _id''')


@artifact_processor
def ui_mail_messages(context):
    data_list = []
    sources = []
    cache = {}
    for entry in _stores(context).values():
        sources.extend(path for name in ('mail_room.db', 'identitiy_db')
                       for path in entry['dbs'].get(name, []))
        emails = _identities(context, entry)
        folders = {}
        for folder_id, name, folder_type in _union(
                context, entry, 'mail_room.db', 'SELECT _id, name, type FROM folder'):
            folders.setdefault(folder_id, (name, folder_type))
        attachments = {}
        for _att_id, mail_id, name, _ctype, _size_value, _inline, _status, local, uri in \
                _attachment_rows(context, entry):
            attachments.setdefault(mail_id, []).append((name, local, uri))
        for (mail_id, header, internal, account_id, folder_id, subject, sender, from_, to, cc,
             bcc, reply_to, text, preview, body, unread, answered, forwarded, starred, mail_type,
             priority) in _union(context, entry, 'mail_room.db', '''
                SELECT _id, date, internalDate, account_id, folderId, subject, sender, email_from,
                       email_to, cc, bcc, replyTo, textbody, preview, body, isUnread, isAnswered,
                       isForwarded, isStarred, mailType, priority
                FROM mail ORDER BY date'''):
            folder_name, folder_type = folders.get(folder_id, ('', None))
            media = ''
            for name, local, uri in attachments.get(mail_id, []):
                tail = _local_tail(local, entry['package'])
                copies = entry['files'].get(tail, []) if tail else []
                if not copies:
                    thumbs = _thumbnails(entry, uri)
                    copies = entry['files'][thumbs[0]] if thumbs else []
                if copies:
                    sources.append(copies[0])
                    media = _media(cache, copies[0], name or os.path.basename(copies[0]))[0]
                    break
            body_tail = _local_tail(body, entry['package'])
            html = ('' if not body_tail else 'Found' if entry['files'].get(body_tail)
                    else 'File not in extraction')
            data_list.append((
                _ms_to_utc(header), _ms_to_utc(internal), entry['package'],
                emails.get(account_id, ''), folder_name or '',
                FOLDER_TYPES.get(folder_type, '' if folder_type is None else str(folder_type)),
                sender or '', from_ or '', to or '', cc or '', bcc or '', reply_to or '',
                subject or '', text or '', preview or '', media, len(attachments.get(mail_id, [])),
                html,
                _yes_no(unread), _yes_no(answered), _yes_no(forwarded), _yes_no(starred),
                mail_type or '', '' if priority is None else priority, entry['user'], mail_id))
    data_list.sort(key=lambda row: (row[0] == '', row[0] or _EPOCH))
    data_headers = (
        ('Header Date', 'datetime'), ('Server Internal Date', 'datetime'), 'App', 'Account Email',
        'Folder', 'Folder Type', 'Sender', 'From', 'To', 'Cc', 'Bcc', 'Reply To', 'Subject',
        'Text Body', 'Preview', ('Attachment', 'media'), 'Attachment Count', 'HTML Body', 'Unread',
        'Answered', 'Forwarded', 'Starred', 'Mail Type (as stored)', 'Priority (as stored)',
        'Android User', 'Mail ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ui_mail_attachments(context):
    data_list = []
    sources = []
    cache = {}
    for entry in _stores(context).values():
        sources.extend(path for name in ('mail_room.db', 'identitiy_db')
                       for path in entry['dbs'].get(name, []))
        emails = _identities(context, entry)
        mails = {}
        for mail_id, header, subject, account_id in _union(
                context, entry, 'mail_room.db', 'SELECT _id, date, subject, account_id FROM mail'):
            mails.setdefault(mail_id, (header, subject, account_id))
        named = set()
        for att_id, mail_id, name, ctype, size_value, inline, status, local, uri in \
                _attachment_rows(context, entry):
            header, subject, account_id = mails.get(mail_id, (None, '', None))
            tail = _local_tail(local, entry['package'])
            copies = entry['files'].get(tail, []) if tail else []
            thumbs = _thumbnails(entry, uri)
            named.update(thumbs)
            if tail:
                named.add(tail)
            # Every cached size and every differing copy of the thumbnail gets a row.
            thumb_copies = [copy for thumb_tail in thumbs for copy in entry['files'][thumb_tail]]
            for copy in copies or [None]:
                if copy:
                    sources.append(copy)
                    media, media_format = _media(cache, copy, name or os.path.basename(copy))
                    file_size = _size(copy)
                else:
                    media, file_size = '', ''
                    media_format = 'File not in extraction' if tail else ''
                for thumb_copy in thumb_copies or [None]:
                    thumb = ''
                    if thumb_copy:
                        sources.append(thumb_copy)
                        thumb = _media(cache, thumb_copy, os.path.basename(thumb_copy))[0]
                    data_list.append((
                        _ms_to_utc(header), media, thumb, media_format, name or '', ctype or '',
                        '' if size_value is None else size_value, file_size, _yes_no(inline),
                        '' if status is None else status, subject or '', entry['package'],
                        emails.get(account_id, ''), 'Yes', entry['user'], mail_id, att_id))
        for tail, copies in sorted(entry['files'].items()):
            if tail in named or not tail.startswith('cache/attachment_'):
                continue
            for copy in copies:
                sources.append(copy)
                media, media_format = _media(cache, copy, os.path.basename(copy))
                data_list.append((
                    '', media, '', media_format, os.path.basename(copy), '', '', _size(copy), '',
                    '', '', entry['package'], '', 'No', entry['user'], '', ''))
    data_headers = (
        ('Mail Header Date', 'datetime'), ('Media', 'media'), ('Thumbnail', 'media'),
        'Media Format', 'Name', 'Content Type', 'Size (as stored)', 'File Size (bytes)', 'Inline',
        'Status (as stored)', 'Mail Subject', 'App', 'Account Email', 'In mail_room.db',
        'Android User', 'Mail ID', 'Attachment ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ui_mail_body_files(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry['dbs'].get('mail_room.db', []))
        named = {}
        for mail_id, header, subject, body in _union(
                context, entry, 'mail_room.db',
                "SELECT _id, date, subject, body FROM mail WHERE body LIKE 'file://%'"):
            tail = _local_tail(body, entry['package'])
            if tail:
                named.setdefault(tail, (mail_id, header, subject))
        for tail, copies in sorted(entry['files'].items()):
            if not tail.startswith('cache/room_mail_bodies/'):
                continue
            mail_id, header, subject = named.get(tail, ('', None, ''))
            for copy in copies:
                sources.append(copy)
                data_list.append((
                    _ms_to_utc(header), os.path.basename(copy), tail.split('/')[2], _size(copy),
                    'Yes' if tail in named else 'No', subject or '', entry['package'],
                    entry['user'], mail_id))
    data_headers = (
        ('Mail Header Date', 'datetime'), 'File Name', 'Account UUID', 'Size (bytes)',
        'Named by a Mail', 'Mail Subject', 'App', 'Android User', 'Mail ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ui_mail_accounts(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry['dbs'].get('identitiy_db', []))
        for (account_id, name, email, default_sender, default_receiver, kind, entry_date,
             deletable) in _union(context, entry, 'identitiy_db', '''
                SELECT accountId, name, email, isDefaultSender, isDefaultReceiver, type, entryDate,
                       isDeletable
                FROM Identity ORDER BY accountId, id'''):
            data_list.append((
                entry_date or '', entry['package'], account_id, name or '', email or '',
                _yes_no(default_sender), _yes_no(default_receiver), kind or '', _yes_no(deletable),
                entry['user']))
    data_headers = ('Entry Date (as stored)', 'App', 'Account ID', 'Name', 'Email',
                    'Default Sender', 'Default Receiver', 'Type (as stored)', 'Deletable',
                    'Android User')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ui_mail_known_receivers(context):
    data_list = []
    sources = []
    for entry in _stores(context).values():
        sources.extend(entry['dbs'].get('known_receivers', []))
        for address, display, times, flags in _union(context, entry, 'known_receivers', '''
                SELECT data1, display_name, times_contacted, flags FROM contacts ORDER BY _id'''):
            data_list.append((address or '', display or '', times, flags, entry['package'],
                              entry['user']))
    data_headers = ('Address', 'Display Name', 'Times Contacted (as stored)', 'Flags (as stored)',
                    'App', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
