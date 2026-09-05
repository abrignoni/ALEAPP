__artifacts_v2__ = {
    "redreader_cache": {
        "name": "RedReader - Fetch History",
        "description": "Parses the web cache index from the RedReader Android app, which records the Reddit requests it made.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "RedReader",
        "sample_data": {
            "emu_a15_oss_v8": "RedReader 1.26 | 88 rows",
        },
        "notes": "One row per entry in the web table of databases/cache.db. RedReader is an open "
                 "source Reddit client, and this table is the index of its HTTP cache: the "
                 "requests it made and still holds, with the URL, the account it was made for, and Timestamp as "
                 "Unix milliseconds reported as UTC. Account is the Reddit username and is empty "
                 "for the app's anonymous mode, which is what the tested device used. "
                 "File Type is decoded from the app's FileType constants, 100 Subreddit list, 101 "
                 "Subreddit about, 102 Multireddit list, 110 Post list, 120 Comment list, 130 "
                 "User about, 140 Inbox list, 200 Thumbnail, 201 Image, 202 Captcha, 203 Inline "
                 "image preview (Constants.java lines 263 to 275 at QuantumBadger/RedReader tag "
                 "v1.26, c250817d4eba13f5ed2b26d33fbc9044095ff8aa); any other value is reported as "
                 "stored. "
                 "The type is what decides how much weight a row carries. A Subreddit about row and a "
                 "Post list row are fetched when a subreddit is opened, so together they date a "
                 "visit to that subreddit; on the tested device the two subreddits opened produced "
                 "exactly two about rows and four list rows, and the URL names the subreddit. A "
                 "Comment list row is weaker: the app precaches comment threads for the posts it "
                 "lists (the same source file defines a COMMENT_PRECACHE download priority at line "
                 "256), so a comment row records that the thread was fetched, not that anyone "
                 "opened it. The tested device opened two threads and holds seventy comment rows. "
                 "The thread's post id is in the URL, so a row still names a post that was on "
                 "screen in a listing. Thumbnail and preview rows are images fetched to draw the "
                 "listing. Session is the app's per-request identifier. Status was 2 on every "
                 "tested row and is reported as stored. The cache content itself lives in files "
                 "under the app's cache directory named by the id here and is not parsed. This is "
                 "a cache, so the app prunes old entries; an absence here is not evidence a request "
                 "was never made.",
        "paths": ('*/org.quantumbadger.redreader/databases/cache.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
    },
    "redreader_subreddits": {
        "name": "RedReader - Subreddits Opened",
        "description": "Parses the cached subreddit records from the RedReader Android app, one per subreddit that was opened.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "RedReader",
        "sample_data": {
            "emu_a15_oss_v8": "RedReader 1.26 | 2 rows",
        },
        "notes": "One row per entry in the objects table of the per-account subreddit database. "
                 "The database is named for the account: RedditSubredditManager.java line 100 at "
                 "QuantumBadger/RedReader tag v1.26 (c250817d4eba13f5ed2b26d33fbc9044095ff8aa) "
                 "builds the file name as the SHA-1 of the username followed by "
                 "'_subreddits_subreddits.db', so the anonymous account's file begins "
                 "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709, the SHA-1 of an empty string, and a "
                 "signed-in account's file begins with the SHA-1 of its username. The Account Hash "
                 "column carries that prefix, which lets an examiner test a suspected username "
                 "against the file. "
                 "The app writes a row here when a subreddit's details are fetched, which happens "
                 "when the subreddit is opened, so on the tested device the two rows are exactly "
                 "the two subreddits opened, each with a Cached time matching the visit. Cached is "
                 "Unix milliseconds reported as UTC. The remaining columns are the subreddit's own "
                 "public metadata as Reddit returned it: Display Name, Title, Subscribers, whether "
                 "it is marked Over 18, the Created time Reddit records for the subreddit (Unix "
                 "seconds, reported as UTC). Those describe the subreddit, not the person; the "
                 "evidence is the row's existence and its Cached time. The row also stores the "
                 "subreddit's full sidebar text, which is Reddit's own content running to "
                 "several kilobytes per row, so it is not reported.",
        "paths": ('*/org.quantumbadger.redreader/databases/*_subreddits_subreddits.db*',),
        "output_types": "standard",
        "artifact_icon": "list",
    },
    "redreader_accounts": {
        "name": "RedReader - Accounts and Subscriptions",
        "description": "Parses the account list and subreddit subscription list from the RedReader Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "RedReader",
        "sample_data": {
            "emu_a15_oss_v8": "RedReader 1.26 | 2 rows",
        },
        "notes": "Rows from two stores. Kind Account rows come from the accounts_oauth2 table of "
                 "databases/accounts_oauth2.db, one per account the app holds, with the Username "
                 "(empty for the anonymous account, which is how the tested device was used) and "
                 "the app's Priority ordering. The table also holds an OAuth refresh token for a "
                 "signed-in account; that is a credential and is deliberately not reported. "
                 "Kind Subscriptions rows come from the objects table of "
                 "databases/rr_subscriptions.db, one per account, with the subreddit list the app "
                 "holds for it as a semicolon-separated string and Updated as Unix milliseconds "
                 "reported as UTC. For the anonymous account that list is the app's own shipped "
                 "default set of subreddits, not choices anyone made, which is what the tested "
                 "device shows; for a signed-in account it is that account's real subscriptions "
                 "as last synced. The Account Hash column gives the SHA-1 of the username, so the "
                 "row can be tied to the per-account subreddit database described in the "
                 "Subreddits Opened artifact. The rr_multireddit_subscriptions.db store holds the "
                 "same shape for multireddits and was empty apart from a placeholder row on the "
                 "tested device.",
        "paths": ('*/org.quantumbadger.redreader/databases/accounts_oauth2.db*',
                  '*/org.quantumbadger.redreader/databases/rr_subscriptions.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
}

import hashlib
import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

# Constants.java FileType at QuantumBadger/RedReader tag v1.26 (c250817d...).
FILE_TYPES = {
    100: 'Subreddit list', 101: 'Subreddit about', 102: 'Multireddit list',
    110: 'Post list', 120: 'Comment list', 130: 'User about', 140: 'Inbox list',
    200: 'Thumbnail', 201: 'Image', 202: 'Captcha', 203: 'Inline image preview',
}


def _files(context, suffix):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(suffix)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _secs(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(float(value)))
    except (TypeError, ValueError):
        return ''


def _lookup(table, value):
    try:
        key = int(value)
    except (TypeError, ValueError):
        return '' if value in (None, '') else f'{value} (as stored)'
    if key in table:
        return table[key]
    return f'{key} (as stored)'


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


def _account_hash(username):
    return hashlib.sha1((username or '').encode('utf-8')).hexdigest().upper()


@artifact_processor
def redreader_cache(context):
    query = '''SELECT timestamp, url, type, user, mimetype, lengthUncompressed,
                      lengthCompressed, status, session, id
               FROM web ORDER BY timestamp DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, 'databases/cache.db'):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', _lookup(FILE_TYPES, r[2]), r[3] or '',
                r[4] or '', r[5], r[6], r[7], r[8] or '', r[9],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Timestamp', 'datetime'), 'URL', 'File Type', 'Account', 'MIME Type',
        'Length (bytes)', 'Length Compressed (bytes)', 'Status (as stored)', 'Session',
        'Cache ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def redreader_subreddits(context):
    query = '''SELECT RawObjectDB_timestamp, display_name, title, subscribers, over18,
                      created_utc, url, RawObjectDB_id
               FROM objects ORDER BY RawObjectDB_timestamp DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, '_subreddits_subreddits.db'):
        account_hash = os.path.basename(db_path).split('_')[0]
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2] or '', r[3], _yesno(r[4]), _secs(r[5]),
                r[6] or '', account_hash, r[7] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Cached', 'datetime'), 'Display Name', 'Title', 'Subscribers', 'Over 18',
        ('Created', 'datetime'), 'URL', 'Account Hash', 'Record ID',
        'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def redreader_accounts(context):
    data_list = []
    sources = []
    for db_path in _files(context, 'databases/accounts_oauth2.db'):
        records = get_sqlite_db_records(
            db_path, 'SELECT username, priority, uses_new_client_id FROM accounts_oauth2')
        for r in records:
            data_list.append(('Account', '', r[0] or '', _account_hash(r[0]), r[1],
                              _yesno(r[2]), '', context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)
    for db_path in _files(context, 'databases/rr_subscriptions.db'):
        records = get_sqlite_db_records(
            db_path, 'SELECT RawObjectDB_id, RawObjectDB_timestamp, serialised FROM objects')
        for r in records:
            data_list.append(('Subscriptions', _ms(r[1]), r[0] or '', _account_hash(r[0]),
                              '', '', r[2] or '', context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Kind', ('Updated', 'datetime'), 'Username', 'Account Hash', 'Priority',
        'New Client ID', 'Subreddits', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
