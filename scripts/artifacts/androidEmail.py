import datetime
import hashlib
import os
import re
import sqlite3

from scripts.artifacts.gmailEmails import body_text_and_links
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

__artifacts_v2__ = {
    "androidEmailMessages": {
        "name": "Android Email - Messages",
        "description": "Messages of the stock Android Email app (com.android.email): one row per row of the Message table of EmailProvider.db, with its mailbox, account, addresses, subject, read and favorite flags, load state, attachment names and the body text and HTML, read from the body files under files/body or, when it holds them, from EmailProviderBody.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Email",
        "notes": "One row per row of the Message table of each distinct EmailProvider.db in com.android.email's databases folder (a byte-identical copy is read once), the AOSP Email app (source cited at tag android-7.1.1_r1). Timestamp (UTC) is timeStamp, described in the source as the time in milliseconds shown in the message list (https://android.googlesource.com/platform/packages/apps/Email/+/97363531d7a81e09dace3f0875d42acd049994bd/emailcommon/src/com/android/emailcommon/provider/EmailContent.java#642), read as milliseconds since 1970. For a synced message the app sets it to the message's sent date (its Date header) when there is one, else the server's internal date (https://android.googlesource.com/platform/packages/apps/Email/+/97363531d7a81e09dace3f0875d42acd049994bd/provider_src/com/android/email/LegacyConversions.java#93). It is not the time the device received the message. Mailbox is the displayName of the Mailbox row the message's mailboxKey names, and Mailbox Type its type named from Mailbox.TYPE_* (https://android.googlesource.com/platform/packages/apps/Email/+/97363531d7a81e09dace3f0875d42acd049994bd/emailcommon/src/com/android/emailcommon/provider/Mailbox.java#307); only INBOX (0), SENT (5) and TRASH (6) occurred in the known data. Account is the emailAddress of the Account row its accountKey names. From, To, CC, BCC and Reply-To are the address lists as stored. Body Text and the HTML body are read from the Body table of EmailProviderBody.db when it holds them, else from the files that EmailProvider.getBodyFile names: files/body/<id / 100 % 100>/<id % 100>/<id>.txt and .html beside the databases (https://android.googlesource.com/platform/packages/apps/Email/+/97363531d7a81e09dace3f0875d42acd049994bd/provider_src/com/android/email/provider/EmailProvider.java#2387). The Body table read is unexercised: the provider at this tag writes the content to the files, and no Body row in the known data held any. HTML Body (as text) and HTML Links are that HTML read as in the Gmail artifacts (body_text_and_links). Attachments lists the fileName of each Attachment row of the message; the Attachment table was empty in the known data, so this column is unexercised. Read (flagRead) is flagRead as stored, 1 read and 0 unread in the source (https://android.googlesource.com/platform/packages/apps/Email/+/97363531d7a81e09dace3f0875d42acd049994bd/emailcommon/src/com/android/emailcommon/provider/EmailContent.java#646); Favorite (flagFavorite) is flagFavorite as stored; Load State is flagLoaded named from FLAG_LOADED_* (https://android.googlesource.com/platform/packages/apps/Email/+/97363531d7a81e09dace3f0875d42acd049994bd/emailcommon/src/com/android/emailcommon/provider/EmailContent.java#938). Message-ID is the messageId column and Server ID the syncServerId, as stored. Android User is taken from the store's evidence path: the number after data/user/, or 0 for a store under data/data. Known data emu_a7_email_known_20261116 (per its mint record: Android 7.1.1 emulator, stock Email 7.1.1, one IMAP test account on lab servers): 4 rows. The three messages appended to the server showed the mint record's append times to the second (two from the README, one from the mint log); the mint stamped the Date header at append, so this run does not separate the header time from the receipt time. The one opened in the app had Read 1; the one deleted in the app was still a row, in the Trash mailbox (TRASH (6)); the one sent from the app was in the Sent mailbox (SENT (5)) with no Message-ID; the last received was unread. Every Body table row held no text, and all four bodies came from the files; the sent message also had an HTML file. In this one run, on an IMAP account, the message deleted in the app was still a row under the Trash mailbox when the data was captured about two minutes later. Whether and when the app or a server sync removes it was not tested. Load State held COMPLETE (1) on all 4 rows, Favorite (flagFavorite) held 0 on all 4 rows, CC, BCC, Reply-To and Attachments had no value on any row, Android User held 0 on all 4 rows, Account held one value on all 4 rows (the one test account) and HTML Links had no value on any row of the known data. No other registered Android corpus image holds a com.android.email file (member lists of all 64 keys checked). The 20 other images with an EmailProvider.db hold it under com.google.android.gm, which the Gmail artifacts read. The paths here are anchored to com.android.email. A vendor build that uses the same package name is matched by these paths; its schema was not tested. Tested only with the known data and a folder tree built from it, where byte-identical copies of a store under data/data and data/user/0 were read once and a changed copy under data/user/10 added its own rows with Android User 10. Not reported: the Message_Updates, Message_Deletes, MessageMove and MessageStateChange tables (empty on the known data), the Message syncServerTimeStamp column, the Policy and Credential tables (empty on the known data), Mailbox sync fields, QuickResponse and the suggestions.db.",
        "paths": ('*/com.android.email/databases/EmailProvider.db*',
                  '*/com.android.email/databases/EmailProviderBody.db*',
                  '*/com.android.email/files/body/*'),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "emu_a7_email_known_20261116": "Android 7.1.1 | com.android.email 7.1.1 | 4 rows (known data)",
            "pixel7a_a14": "Android 14 | 0 rows (no com.android.email file matched)",
        },
    },
    "androidEmailAccounts": {
        "name": "Android Email - Accounts",
        "description": "Accounts of the stock Android Email app (com.android.email): the Account table of "
                       "EmailProvider.db joined to its HostAuth rows, one row per account and host record, "
                       "with the protocol, server, port, login and password as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Email",
        "notes": "One row per Account row and each HostAuth row its hostAuthKeyRecv or hostAuthKeySend names (Host Record Receive or Send), from each distinct EmailProvider.db in com.android.email's databases folder (a byte-identical copy is read once). An account whose keys name no HostAuth row gets no row; that case is unexercised. Email Address, Account Name and Sender Name are the Account emailAddress, displayName and senderName columns as stored, and Account Row ID is its _id. Protocol, Server, Port, Login and Password (as stored) are the HostAuth protocol, address, port, login and password columns as stored; Sync Interval (as stored) is the account's syncInterval. Android User is taken from the store's evidence path: the number after data/user/, or 0 for a store under data/data. Known data emu_a7_email_known_20261116: 2 rows for its one account, an imap Receive record and an smtp Send record, whose server, port, login and password match the values the mint record says were entered in the app; Android User held 0 on both rows. The known data's accounts_ce.db holds one account row of type com.android.email; the accounts_ce artifacts read that database and were not run in this test. No other registered Android corpus image holds a com.android.email file (member lists of all 64 keys checked). The 20 other images with an EmailProvider.db hold it under com.google.android.gm, which the Gmail artifacts read. The paths here are anchored to com.android.email. A vendor build that uses the same package name is matched by these paths; its schema was not tested. Tested only with the known data and the folder tree built from it.",
        "paths": ('*/com.android.email/databases/EmailProvider.db*',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "user",
        "sample_data": {
            "emu_a7_email_known_20261116": "Android 7.1.1 | com.android.email 7.1.1 | 2 rows (known data)",
            "pixel7a_a14": "Android 14 | 0 rows (no com.android.email file matched)",
        },
    },
}

# Mailbox.java TYPE_* (packages/apps/Email, android-7.1.1_r1)
_MAILBOX_TYPES = {-1: 'NONE', 0: 'INBOX', 1: 'MAIL', 2: 'PARENT', 3: 'DRAFTS', 4: 'OUTBOX', 5: 'SENT', 6: 'TRASH',
                  7: 'JUNK', 8: 'SEARCH', 9: 'STARRED', 10: 'UNREAD', 0x40: 'NOT_EMAIL', 0x41: 'CALENDAR',
                  0x42: 'CONTACTS', 0x43: 'TASKS', 0x44: 'EAS_ACCOUNT_MAILBOX', 0x45: 'UNKNOWN'}
# EmailContent.java Message FLAG_LOADED_*
_LOAD_STATES = {0: 'UNLOADED', 1: 'COMPLETE', 2: 'PARTIAL', 3: 'DELETED', 4: 'UNKNOWN'}
_USER = re.compile(r'/data/user/(\d+)/')


def _label(mapping, value):
    if value is None or value == '':
        return ''
    name = mapping.get(value)
    return f'{name} ({value})' if name else str(value)


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return None
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return None


def _android_user(path):
    '''n for a path under data/user/<n>, 0 under data/data, else blank; path is evidence-relative.'''
    norm = '/' + path.replace(os.sep, '/').lstrip('/')
    match = _USER.search(norm)
    if match:
        return int(match.group(1))
    return 0 if '/data/data/' in norm else ''


def _stores(files_found):
    '''{databases folder: {'provider': path, 'body': path}}, byte-identical providers read once.'''
    folders = {}
    for path in sorted(files_found):
        norm = path.replace(os.sep, '/')
        for kind, name in (('provider', '/EmailProvider.db'), ('body', '/EmailProviderBody.db')):
            if norm.endswith(name):
                folders.setdefault(norm[:-len(name)], {})[kind] = path
    seen = set()
    unique = {}
    for folder in sorted(folders, key=lambda f: ('/data/user/' in f, f)):
        provider = folders[folder].get('provider')
        if not provider:
            continue
        try:
            with open(provider, 'rb') as handle:
                digest = hashlib.sha1(handle.read()).hexdigest()
        except OSError as ex:
            logfunc(f'Android Email: could not hash {provider}: {ex}')
            digest = provider
        if digest in seen:
            continue
        seen.add(digest)
        unique[folder] = folders[folder]
    return unique


def _body_file(files, data_dir, msg_id, ext):
    '''EmailProvider.getBodyFile: files/body/<id / 100 % 100>/<id % 100>/<id>.<ext> beside the databases.'''
    rel = f'{data_dir}/files/body/{msg_id // 100 % 100}/{msg_id % 100}/{msg_id}.{ext}'
    path = files.get(rel)
    if not path:
        return '', None
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            return handle.read(), path
    except OSError as ex:
        logfunc(f'Android Email: could not read {path}: {ex}')
        return '', None


def _tables(db):
    return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _bodies(path):
    '''{messageKey: (textContent, htmlContent)} from EmailProviderBody.db, or {} when unreadable.'''
    db = open_sqlite_db_readonly(path) if path else None
    if db is None:
        return {}
    try:
        if 'Body' not in _tables(db):
            return {}
        return {key: (text, html) for key, text, html in
                db.execute('SELECT messageKey, textContent, htmlContent FROM Body')}
    except sqlite3.Error as ex:
        logfunc(f'Android Email: could not read {path}: {ex}')
        return {}
    finally:
        db.close()


@artifact_processor
def androidEmailMessages(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    files = {path.replace(os.sep, '/'): path for path in files_found}
    for folder, store in _stores(files_found).items():
        provider = store['provider']
        user = _android_user(context.get_relative_path(provider))
        data_dir = folder[:-len('/databases')] if folder.endswith('/databases') else folder
        bodies = _bodies(store.get('body'))
        db = open_sqlite_db_readonly(provider)
        if db is None:
            logfunc(f'Android Email - Messages: could not open {provider}')
            continue
        try:
            tables = _tables(db)
            if 'Message' not in tables:
                logfunc(f'Android Email - Messages: no Message table in {provider}')
                sources.append(provider)
                continue
            mailboxes = {}
            if 'Mailbox' in tables:
                mailboxes = {i: (n, t) for i, n, t in db.execute('SELECT _id, displayName, type FROM Mailbox')}
            accounts = dict(db.execute('SELECT _id, emailAddress FROM Account')) if 'Account' in tables else {}
            attachments = {}
            if 'Attachment' in tables:
                for key, name in db.execute('SELECT messageKey, fileName FROM Attachment ORDER BY _id'):
                    attachments.setdefault(key, []).append(name or '')
            for row in db.execute(
                    'SELECT _id, timeStamp, mailboxKey, accountKey, fromList, toList, ccList, bccList, '
                    'replyToList, subject, flagRead, flagFavorite, flagLoaded, messageId, syncServerId '
                    'FROM Message ORDER BY timeStamp, _id'):
                (msg_id, stamp, mailbox_key, account_key, from_list, to_list, cc_list, bcc_list, reply_to,
                 subject, flag_read, flag_favorite, flag_loaded, message_id, server_id) = row
                mailbox_name, mailbox_type = mailboxes.get(mailbox_key, ('', None))
                text, html = bodies.get(msg_id, ('', ''))
                if not text:
                    text, text_path = _body_file(files, data_dir, msg_id, 'txt')
                    if text_path:
                        sources.append(text_path)
                if not html:
                    html, html_path = _body_file(files, data_dir, msg_id, 'html')
                    if html_path:
                        sources.append(html_path)
                html_text, links = body_text_and_links(html) if html else ('', '')
                data_list.append((
                    _ms_to_utc(stamp), user, accounts.get(account_key, ''), mailbox_name or '',
                    _label(_MAILBOX_TYPES, mailbox_type), from_list or '', to_list or '', cc_list or '',
                    bcc_list or '', reply_to or '', subject or '', text or '', html_text, links,
                    '\n'.join(attachments.get(msg_id, [])), flag_read if flag_read is not None else '',
                    flag_favorite if flag_favorite is not None else '', _label(_LOAD_STATES, flag_loaded),
                    message_id or '', server_id or '', msg_id))
            sources.append(provider)
            if store.get('body'):
                sources.append(store['body'])
        except sqlite3.Error as ex:
            logfunc(f'Android Email - Messages: could not read {provider}: {ex}')
        finally:
            db.close()

    data_headers = (('Timestamp (UTC)', 'datetime'), 'Android User', 'Account', 'Mailbox', 'Mailbox Type',
                    'From', 'To', 'CC', 'BCC', 'Reply-To', 'Subject', 'Body Text', 'HTML Body (as text)',
                    'HTML Links', 'Attachments', 'Read (flagRead)', 'Favorite (flagFavorite)', 'Load State',
                    'Message-ID', 'Server ID', 'Message Row ID')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def androidEmailAccounts(context):
    data_list = []
    sources = []
    for _folder, store in _stores(context.get_files_found()).items():
        provider = store['provider']
        user = _android_user(context.get_relative_path(provider))
        db = open_sqlite_db_readonly(provider)
        if db is None:
            logfunc(f'Android Email - Accounts: could not open {provider}')
            continue
        try:
            tables = _tables(db)
            sources.append(provider)
            if 'Account' not in tables or 'HostAuth' not in tables:
                logfunc(f'Android Email - Accounts: no Account or HostAuth table in {provider}')
                continue
            for row in db.execute(
                    'SELECT a._id, a.emailAddress, a.displayName, a.senderName, a.syncInterval, '
                    'h._id, h.protocol, h.address, h.port, h.login, h.password, '
                    'CASE WHEN h._id = a.hostAuthKeyRecv THEN \'Receive\' WHEN h._id = a.hostAuthKeySend '
                    'THEN \'Send\' ELSE \'\' END '
                    'FROM Account a JOIN HostAuth h ON h._id IN (a.hostAuthKeyRecv, a.hostAuthKeySend) '
                    'ORDER BY a._id, h._id'):
                (acc_id, address, display, sender, interval, _host_id, protocol, server, port, login, password,
                 role) = row
                data_list.append((user, address or '', display or '', sender or '', role, protocol or '',
                                  server or '', port if port is not None else '', login or '', password or '',
                                  interval if interval is not None else '', acc_id))
        except sqlite3.Error as ex:
            logfunc(f'Android Email - Accounts: could not read {provider}: {ex}')
        finally:
            db.close()

    data_headers = ('Android User', 'Email Address', 'Account Name', 'Sender Name', 'Host Record', 'Protocol',
                    'Server', 'Port', 'Login', 'Password (as stored)', 'Sync Interval (as stored)',
                    'Account Row ID')
    return data_headers, data_list, '\n'.join(sources)
