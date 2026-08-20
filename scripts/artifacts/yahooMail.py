__artifacts_v2__ = {
    "yahoo_mail_messages": {
        "name": "Yahoo Mail - Messages",
        "description": "Parses messages cached by the Yahoo Mail Android app, including "
                       "sender and recipient addresses, subject, snippet, folder, read "
                       "and flagged state and the message body where the app cached it.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Yahoo Mail",
        "notes": "One row per cached message. The app stores its state in flux_database.db, "
                 "where every table shares the same shape, a mailboxYid naming the account, "
                 "a key naming the record and a JSON document in value, so one message is "
                 "assembled from several tables joined on the message id. Date and Server "
                 "Sync Time are Unix milliseconds. Subject and Snippet are stored once per "
                 "list query rather than once per message; the values are read from the "
                 "message's own record and identical text was stored under every list query "
                 "on the tested device. Snippet is the preview the app keeps rather than the "
                 "message text, and the app caps it: four of the six on the tested device were "
                 "exactly 512 bytes and ended mid word, while the two shorter ones ended on a "
                 "sentence, so a snippet ending mid word is that cap rather than the end of "
                 "the message. Decorations and Category are reported as stored: the "
                 "extraction carries no app binary, so no mapping for those codes could be "
                 "sourced. Folder names the folder the cached record carries, resolved "
                 "through the Folders table of the same account. Message Body is the HTML the "
                 "app cached, as stored, and is present only for messages whose body was "
                 "fetched; on the tested device 1 of 6 messages carried one, so an empty "
                 "column means the body was not cached rather than that the message was "
                 "empty. No message on the tested device carried an attachment: every "
                 "attachmentIds list was empty and the Attachments table held no rows, so "
                 "nothing could be linked to cached bytes and no media column is offered. "
                 "The app records no user-entered search terms here; RecentSearches held no "
                 "rows and the eight SavedSearches rows are the app's own filter and "
                 "classification definitions, carrying empty userQueries, so they are not "
                 "reported as searches the user ran. Field mapping was done against a "
                 "private sample provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.yahoo.mobile.client.android.mail/databases/flux_database.db*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "mail"
    },
    "yahoo_mail_folders": {
        "name": "Yahoo Mail - Folders",
        "description": "Parses the mail folders recorded by the Yahoo Mail Android app, "
                       "with the message and unread counts held for each.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Yahoo Mail",
        "notes": "One row per folder record. Total Messages and Unread Messages are the "
                 "counts the folder record carries, which the app receives from the server, "
                 "while Cached Messages counts the messages this database holds against that "
                 "folder. The two answer different questions and can disagree: on the tested "
                 "device five cached messages carried the Trash folder id while that folder's "
                 "own record reported a total of zero. Why they disagree is not established "
                 "here, because a server side removal, a later re-sync and a local eviction "
                 "all leave the same result. Folder Name is reported as stored. Where the "
                 "stored name decodes from base64 to printable text the decode is offered in "
                 "its own column, which on the tested device filled for one user created "
                 "folder and stayed empty for the rest; no source establishes which names the "
                 "app encodes, so the stored value is the one to rely on. Folder Types is "
                 "reported as stored. Field mapping was done against a private sample "
                 "provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.yahoo.mobile.client.android.mail/databases/flux_database.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "folder"
    },
    "yahoo_mail_accounts": {
        "name": "Yahoo Mail - Accounts and Device",
        "description": "Parses the signed in Yahoo Mail account together with the device "
                       "and installation identifiers the Android app records.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Yahoo Mail",
        "notes": "One row per account listed in the app's Mailboxes record. The account "
                 "fields come from that record, and the device name, Android version and "
                 "push state from the app's own phoenix_preferences and fluxStartupData "
                 "preference files, which are read only from the same app data directory as "
                 "the database. Mailbox Setup is Unix milliseconds. Region, GDPR and EECC are "
                 "the values the mailbox configuration record carries, as stored. Session "
                 "count is reported by two records written by different parts of the app, the "
                 "mailbox configuration and the app configuration; the column names the "
                 "mailbox value and both held the same number on the tested device. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/com.yahoo.mobile.client.android.mail/databases/flux_database.db*',
            '*/com.yahoo.mobile.client.android.mail/shared_prefs/phoenix_preferences.xml',
            '*/com.yahoo.mobile.client.android.mail/shared_prefs/fluxStartupData.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "yahoo_mail_app_usage": {
        "name": "Yahoo Mail - App Usage",
        "description": "Parses the install, update and session record the Yahoo Mail "
                       "Android app keeps for itself, with its message open and delete "
                       "counters.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Yahoo Mail",
        "notes": "One row per app configuration record, which is one per account on the "
                 "tested device. Every timestamp is Unix milliseconds. The counters are the "
                 "running totals the app maintains, so they describe the whole life of the "
                 "install rather than a single session, and Emails Deleted is the app's own "
                 "counter rather than a count of recoverable deleted messages. First Install "
                 "is the app's record of its own first run and matched the mailbox setup "
                 "timestamp exactly on the tested device. Field mapping was done against a "
                 "private sample provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.yahoo.mobile.client.android.mail/databases/flux_database.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "activity"
    },
    "yahoo_mail_contacts": {
        "name": "Yahoo Mail - Contacts",
        "description": "Parses the contact records the Yahoo Mail Android app holds for "
                       "addresses seen in the mailbox.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Yahoo Mail",
        "notes": "One row per contact record. These records are built by the app from "
                 "addresses it has seen rather than entered by the user: every record on the "
                 "tested device carried isUserCurated false, and each one corresponded to a "
                 "sender of a cached message. User Curated and Known Entity are reported as "
                 "stored so that distinction stays visible. Attributes is the record's own "
                 "attribute list, as stored. On the tested device one of the three records "
                 "carried five attributes including the app's machine generated marker, and "
                 "the other two carried none. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/com.yahoo.mobile.client.android.mail/databases/flux_database.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
}

import base64
import binascii
import json
import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.yahoo.mobile.client.android.mail'
_DATABASE = 'flux_database.db'


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate. Every
    index this module builds is keyed on it, because an index keyed on a bare file name
    would merge two app data directories into one.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context):
    '''{container key: [path]} for the files this artifact matched.

    Every caller iterates the containers rather than taking the first database that
    opens, so a second app data directory contributes its own rows instead of being
    dropped.
    '''
    grouped = {}
    for file_found in unique_files(context):
        grouped.setdefault(_container(context, file_found), []).append(str(file_found))
    return grouped


def _named(paths, name):
    '''The matched paths whose file name is name.'''
    return [path for path in paths if os.path.basename(path) == name]


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _prefs(source_path):
    '''{name: text} for an Android shared preferences file.'''
    values = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Yahoo Mail: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _document(text):
    '''The JSON document held in a value column, or None when it does not parse.'''
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return None


def _table(database, table):
    '''[(mailboxYid, key, document, timestamp)] for one Flux table.

    A table absent from an older or newer release is logged and yields nothing, so a
    schema change costs the artifact that table rather than every row it would have
    returned.
    '''
    rows = []
    try:
        cursor = database.cursor()
        cursor.execute(f'SELECT mailboxYid, key, value, timestamp FROM "{table}"')
        fetched = cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Yahoo Mail: could not read {table}: {ex}')
        return rows
    for mailbox, key, value, stamp in fetched:
        rows.append((mailbox, key, _document(value), stamp))
    return rows


def _keyed(database, table):
    '''{(mailboxYid, key): document} for one Flux table.

    Keyed on the account as well as the record, because one database holds every account
    signed in on the device and two accounts can carry the same record key.
    '''
    return {(mailbox, key): document
            for mailbox, key, document, _ in _table(database, table)
            if document is not None}


def _addresses(entries):
    '''An address list as "Name <address>" text, or '' when the list is empty.'''
    if not isinstance(entries, list):
        return ''
    parts = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        address = entry.get('email') or ''
        name = entry.get('name') or ''
        parts.append(f'{name} <{address}>' if name and address else (address or name))
    return '; '.join(part for part in parts if part)


def _joined(values, field=None):
    '''A list of scalars, or of one field of a list of records, as text.'''
    if not isinstance(values, list):
        return ''
    if field is None:
        return '; '.join(str(value) for value in values)
    return '; '.join(str(value.get(field, '')) for value in values
                     if isinstance(value, dict) and value.get(field))


def _decoded_name(name):
    '''A stored folder name decoded from base64, when that yields printable text.

    Offered beside the stored value rather than in place of it. Nothing in the extraction
    establishes which names the app encodes, so a name that does not decode to printable
    text is left blank rather than guessed at.
    '''
    if not name or len(name) % 4:
        return ''
    try:
        raw = base64.b64decode(name, validate=True)
    except (binascii.Error, ValueError):
        return ''
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return ''
    if not text or not text.isprintable():
        return ''
    return text


def _setting(config, mailbox, name):
    '''One MailBoxConfig or AppConfig value for an account, as text, or ''.

    A module level helper rather than a closure over the loop variables, so the account
    a value is read for is the one passed in rather than whichever the loop last bound.
    '''
    value = config.get((mailbox, name), '')
    return '' if value is None else value


def _databases(paths):
    '''[(source path, open database)] for each flux database in one container.'''
    opened = []
    for path in _named(paths, _DATABASE):
        try:
            database = open_sqlite_db_readonly(get_sqlite_db_path(path))
        except sqlite3.Error as ex:
            logfunc(f'Yahoo Mail: could not open {_DATABASE}: {ex}')
            continue
        opened.append((path, database))
    return opened


@artifact_processor
def yahoo_mail_messages(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            data = _keyed(database, 'MessagesData')
            recipients = _keyed(database, 'MessagesRecipients')
            flags = _keyed(database, 'MessagesFlags')
            folder_ids = _keyed(database, 'MessagesFolderId')
            references = _keyed(database, 'MessagesRefV2')
            subjects = _keyed(database, 'MessagesSubjectSnippet')
            attachments = _keyed(database, 'MessagesAttachments')
            bodies = _keyed(database, 'MessagesBody')

            # Folder names are resolved inside the same account, so one account's folder
            # list cannot name another account's folder.
            folders = {}
            for mailbox, key, document, _ in _table(database, 'Folders'):
                if isinstance(document, dict):
                    folders[(mailbox, str(document.get('folderId', key)))] = document

            for (mailbox, message_id), document in sorted(data.items()):
                if not isinstance(document, dict):
                    continue
                flag = flags.get((mailbox, message_id)) or {}
                reference = references.get((mailbox, message_id)) or {}
                recipient = recipients.get((mailbox, message_id)) or {}
                attachment = attachments.get((mailbox, message_id)) or {}
                body = bodies.get((mailbox, message_id)) or {}

                # The subject and snippet are stored once per list query the message
                # appeared in. Every query held the same text on the tested device, so the
                # first is taken and the record is read from the message's own row.
                subject = snippet = ''
                stored = subjects.get((mailbox, message_id))
                if isinstance(stored, dict):
                    for entry in stored.values():
                        if isinstance(entry, dict):
                            subject = entry.get('subject') or ''
                            snippet = entry.get('snippet') or ''
                            break

                folder_id = folder_ids.get((mailbox, message_id))
                folder_name = ''
                if folder_id is not None:
                    folder = folders.get((mailbox, str(folder_id)))
                    if folder:
                        folder_name = folder.get('folderName') or ''
                        folder_name = _decoded_name(folder_name) or folder_name

                attachment_ids = attachment.get('attachmentIds')
                source_files.append(relative)
                data_list.append((
                    _ms(document.get('date')),
                    _ms(document.get('serverSyncTimestamp')),
                    folder_name,
                    str(folder_id) if folder_id is not None else '',
                    subject,
                    snippet,
                    _addresses(recipient.get('fromList')),
                    _addresses(recipient.get('toList')),
                    _addresses(recipient.get('ccList')),
                    _addresses(recipient.get('bccList')),
                    _addresses(recipient.get('replyToList')),
                    str(flag.get('isRead', '')),
                    str(flag.get('isFlagged', '')),
                    len(attachment_ids) if isinstance(attachment_ids, list) else '',
                    body.get('htmlBody') or '',
                    str(reference.get('conversationId', '')),
                    _joined(reference.get('decoIds')),
                    _joined(document.get('categoryInfo'), 'name'),
                    str(document.get('isNewslettersEmail', '')),
                    message_id,
                    mailbox,
                    relative,
                ))
            database.close()

    # Most recent message first, with the message id breaking ties so the order is the
    # same on every run rather than depending on the order the rows were read.
    data_list.sort(key=lambda row: (str(row[0]), row[19]), reverse=True)

    data_headers = (
        ('Date', 'datetime'),
        ('Server Sync Time', 'datetime'),
        'Folder',
        'Folder ID',
        'Subject',
        'Snippet',
        'From',
        'To',
        'Cc',
        'Bcc',
        'Reply To',
        'Read',
        'Flagged',
        'Attachment Count',
        'Message Body (as stored)',
        'Conversation ID',
        'Decorations (as stored)',
        'Category (as stored)',
        'Newsletter',
        'Message ID',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def yahoo_mail_folders(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)

            # Counted per account, so a folder id that exists for two accounts does not
            # collect the other account's cached messages.
            cached = {}
            for mailbox, _, document, _ in _table(database, 'MessagesFolderId'):
                if document is not None:
                    cached[(mailbox, str(document))] = cached.get((mailbox, str(document)), 0) + 1

            for mailbox, key, document, stamp in _table(database, 'Folders'):
                if not isinstance(document, dict):
                    continue
                folder_id = str(document.get('folderId', key))
                stored_name = document.get('folderName') or ''
                source_files.append(relative)
                data_list.append((
                    _ms(stamp),
                    folder_id,
                    stored_name,
                    _decoded_name(stored_name),
                    _joined(document.get('folderTypes')),
                    document.get('total', ''),
                    document.get('unread', ''),
                    cached.get((mailbox, folder_id), 0),
                    str(document.get('accountId', '')),
                    mailbox,
                    relative,
                ))
            database.close()

    data_headers = (
        ('Record Timestamp', 'datetime'),
        'Folder ID',
        'Folder Name (as stored)',
        'Folder Name (base64 decoded)',
        'Folder Types (as stored)',
        'Total Messages',
        'Unread Messages',
        'Cached Messages',
        'Account ID',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def yahoo_mail_accounts(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        # Preferences are read only from the same app data directory as the database, so
        # a second Android user's device name cannot be reported against this account.
        startup = _prefs(_named(paths, 'fluxStartupData.xml')[0]) if _named(paths, 'fluxStartupData.xml') else {}
        phoenix = _prefs(_named(paths, 'phoenix_preferences.xml')[0]) if _named(paths, 'phoenix_preferences.xml') else {}

        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            config = _keyed(database, 'MailBoxConfig')
            settings = _keyed(database, 'MailSettings')

            for mailbox, _, document, _ in _table(database, 'Mailboxes'):
                if not isinstance(document, dict):
                    continue
                theme = ''
                for (owner, name), value in settings.items():
                    if owner == mailbox and name.startswith('MAILBOX_THEME') and isinstance(value, dict):
                        theme = value.get('themeName', '')
                for account in document.get('accountsList') or []:
                    if not isinstance(account, dict):
                        continue
                    source_files.append(relative)
                    data_list.append((
                        _ms(_setting(config, mailbox, 'MAILBOX_SETUP_TIMESTAMP')),
                        mailbox,
                        account.get('email', ''),
                        account.get('accountName', ''),
                        str(account.get('accountId', '')),
                        account.get('accountDomain', ''),
                        str(account.get('authType', '')),
                        str(account.get('isPrimary', '')),
                        str(account.get('isSelected', '')),
                        str(account.get('isInitialized', '')),
                        phoenix.get('device_name', ''),
                        phoenix.get('android_system_version', ''),
                        str(_setting(config, mailbox, 'CP_REGION')),
                        str(_setting(config, mailbox, 'IS_GDPR')),
                        str(_setting(config, mailbox, 'IS_EECC')),
                        str(_setting(config, mailbox, 'MAILBOX_SESSION_COUNT')),
                        str(_setting(config, mailbox, 'DEVICE_MAILBOX_IDENTIFIER')),
                        startup.get('firebase_id', ''),
                        theme,
                        str(startup.get('is_mail_plus', '')),
                        str(phoenix.get('push_enabled', '')),
                        relative,
                    ))
            database.close()

    data_headers = (
        ('Mailbox Setup', 'datetime'),
        'Account',
        'Email',
        'Account Name',
        'Account ID',
        'Account Domain',
        'Auth Type (as stored)',
        'Primary',
        'Selected',
        'Initialized',
        'Device Name',
        'Android Version',
        'Region (as stored)',
        'GDPR',
        'EECC',
        'Mailbox Session Count',
        'Device Mailbox Identifier',
        'Firebase Identifier',
        'Theme',
        'Mail Plus',
        'Push Enabled',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def yahoo_mail_app_usage(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            config = _keyed(database, 'AppConfig')
            mailbox_config = _keyed(database, 'MailBoxConfig')

            accounts = sorted({mailbox for mailbox, _ in config})
            for mailbox in accounts:
                source_files.append(relative)
                data_list.append((
                    _ms(_setting(config, mailbox, 'FIRST_INSTALL_TIMESTAMP')),
                    _ms(_setting(config, mailbox, 'LATEST_UPDATE_TIMESTAMP')),
                    _ms(_setting(config, mailbox, 'PREVIOUS_UPDATE_TIMESTAMP')),
                    _ms(_setting(config, mailbox, 'LAST_APP_SESSION_TIMESTAMP')),
                    _ms(_setting(config, mailbox, 'LAST_USER_SESSION_TIMESTAMP')),
                    _ms(_setting(config, mailbox, 'LAST_APP_HIDDEN_TIMESTAMP')),
                    _ms(_setting(config, mailbox, 'FIRST_USER_SESSION_RECORDED_TIME')),
                    _ms(_setting(mailbox_config, mailbox, 'SEGMENT_INACTIVE_SINCE_TIMESTAMP')),
                    str(_setting(config, mailbox, 'USER_APP_SESSION_COUNT')),
                    str(_setting(config, mailbox, 'USER_SESSION_COUNT')),
                    str(_setting(mailbox_config, mailbox, 'MAILBOX_SESSION_COUNT')),
                    str(_setting(config, mailbox, 'MILESTONE_MESSAGE_OPEN_COUNT')),
                    str(_setting(config, mailbox, 'EMAILS_DELETED')),
                    str(_setting(config, mailbox, 'FIRST_DELETE_EVENT')),
                    str(_setting(config, mailbox, 'FIRST_INSTALL_APP_VERSION_CODE')),
                    str(_setting(config, mailbox, 'LATEST_UPDATE_APP_VERSION_CODE')),
                    str(_setting(config, mailbox, 'IS_FRESH_INSTALL')),
                    str(_setting(config, mailbox, 'MAIL_NOTIFICATION_TYPE')),
                    str(_setting(config, mailbox, 'DEVICE_IDENTIFIER')),
                    mailbox,
                    relative,
                ))
            database.close()

    data_headers = (
        ('First Install', 'datetime'),
        ('Latest Update', 'datetime'),
        ('Previous Update', 'datetime'),
        ('Last App Session', 'datetime'),
        ('Last User Session', 'datetime'),
        ('Last App Hidden', 'datetime'),
        ('First User Session Recorded', 'datetime'),
        ('Inactive Since', 'datetime'),
        'App Session Count',
        'User Session Count',
        'Mailbox Session Count',
        'Messages Opened Count',
        'Emails Deleted Count',
        'First Delete Event',
        'First Install Version Code',
        'Latest Update Version Code',
        'Fresh Install',
        'Notification Type (as stored)',
        'Device Identifier',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def yahoo_mail_contacts(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            for mailbox, _, document, stamp in _table(database, 'ContactInfo'):
                if not isinstance(document, dict):
                    continue
                attributes = document.get('attributes')
                rendered = ''
                if isinstance(attributes, list):
                    rendered = '; '.join(
                        f"{entry.get('key', '')}={entry.get('value', '')}"
                        for entry in attributes if isinstance(entry, dict))
                source_files.append(relative)
                data_list.append((
                    _ms(stamp),
                    document.get('name', ''),
                    _joined(document.get('emails'), 'email'),
                    _joined(document.get('numbers'), 'number'),
                    str(document.get('isUserCurated', '')),
                    str(document.get('isKnownEntity', '')),
                    str(document.get('isList', '')),
                    rendered,
                    str(document.get('xobniId', '')),
                    mailbox,
                    relative,
                ))
            database.close()

    data_headers = (
        ('Record Timestamp', 'datetime'),
        'Name',
        'Email Addresses',
        'Phone Numbers',
        'User Curated',
        'Known Entity',
        'Is List',
        'Attributes (as stored)',
        'Contact Identifier',
        'Account',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
