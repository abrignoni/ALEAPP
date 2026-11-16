__artifacts_v2__ = {
    "samsung_internet_bookmarks": {
        "name": "Samsung Internet - Bookmarks",
        "description": "Bookmarks from the Samsung Internet BOOKMARKS table in SBrowser.db, with the folder each "
                       "sits in.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per BOOKMARKS row in com.sec.android.app.sbrowser/databases/SBrowser.db that is not a '
            'folder (FOLDER 1); Folder is the TITLE of the row PARENT names, or PARENT as stored when no '
            'folder row has that id. Created and Modified are CREATED and MODIFIED read as Unix milliseconds. '
            'A stored 0, a NULL, a negative or a non-integer time is shown blank. On '
            'samsung_a166u_a16_known_20261116 the two bookmarks added in the session (15:37:29 and 15:40:42 '
            'UTC in the mint log) had Created 15:37:28 and 15:40:41 UTC and bookmark_type 2, and the four '
            'rows not added in the session had CREATED 0 and bookmark_type 1. What bookmark_type means is not '
            'established. Modified held 17:37:39 UTC on 3 of the 6 rows and a stored 0 on the other 3. On the '
            'known-data image BOOKMARKS MODIFIED (3 rows), READINGLIST modified, and TABS DATE_CREATED and '
            'DATE_MODIFIED held times of 17:37:39 to 17:37:59 UTC, while most of the items were made between '
            '15:19 and 15:41 UTC (mint log); those four columns do not by themselves record when the item was '
            'made. Folder held Samsung account, Deleted (as stored) held 0 and Tags (as stored) had no value '
            'on all 6 rows of the known-data image; a NULL TAGS is shown blank. Rows with DELETED other than '
            '0 are kept and shown; no image checked had such a row. Only the columns shown are read; the '
            'FAVICON and TOUCH_ICON blobs and the sync, account, device, position and guid columns are among '
            'those not reported. app_sbrowser/Default/Bookmarks, which the Bookmarks artifact '
            '(chromeBookmarks.py) reads, was not present on the known-data image. Created leads the table '
            'because on the two known-data bookmarks it matched the time the bookmark was added; Created is '
            'blank on 4 of 6 rows there.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SBrowser.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 6 rows",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 2 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 1 row",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 0 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 1 row",
            "samsunga53_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 4 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 4 rows",
        },
    },
    "samsung_internet_saved_pages": {
        "name": "Samsung Internet - Saved Pages",
        "description": "Pages saved in Samsung Internet (READINGLIST table in SBrowser.db), with the saved "
                       "page file the row records.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per READINGLIST row in SBrowser.db, the list Samsung Internet showed as Saved pages in '
            "the known-data session. Saved Page links the file the row's dir_path records, matched on that "
            'recorded path inside the same app container under files/readinglist/; the copy is given an '
            '.mhtml extension when its own headers say MIME multipart/related. Created and Modified are '
            'created and modified read as Unix milliseconds. A stored 0, a NULL, a negative or a non-integer '
            'time is shown blank. On samsung_a166u_a16_known_20261116 the one page saved at 15:41:09 UTC '
            "(mint log) had created 15:41:06 UTC, and the saved file's own Date header gives the same time. "
            'Modified held 17:37:39 UTC. On the known-data image BOOKMARKS MODIFIED (3 rows), READINGLIST '
            'modified, and TABS DATE_CREATED and DATE_MODIFIED held times of 17:37:39 to 17:37:59 UTC, while '
            'most of the items were made between 15:19 and 15:41 UTC (mint log); those four columns do not by '
            'themselves record when the item was made. is_deleted (as stored) and isReadingItem (as stored) '
            'held 0; their meaning is not established. Only the columns shown are read; the path, '
            'description, favicon, device, sync and account columns are among those not reported. The Offline '
            'Pages artifact (chromeOfflinePages.py) lists app_sbrowser/Default/Offline Pages in its paths; '
            'that folder was not present on the known-data image. No other image checked had a READINGLIST '
            'row.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SBrowser.db*',
                  '*/com.sec.android.app.sbrowser/files/readinglist/*'),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 1 row",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 0 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 0 rows",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 0 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
        },
    },
    "samsung_internet_tabs": {
        "name": "Samsung Internet - Tabs",
        "description": "Tabs listed in the Samsung Internet TABS table in SBrowser.db, with the tab's cached "
                       "page thumbnail where one is in the extraction.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per TABS row in SBrowser.db. Thumbnail renders cache/Bitmap/Thumbnail/<w>/<n>.0 in the '
            'same app container for the tab whose TAB_ID is <w>_<n>. That link is by name: on '
            'samsung_a166u_a16_known_20261116 each of the four thumbnails (tabs 1_1, 1_3, 1_5 and 1_6) showed '
            'the page its tab row names, and tabs 1_2 and 1_7 had none. On sharon_a13 5 of 5 and on '
            'sharon_a14 3 of 4 tabs had a thumbnail by that name, not checked against the pages. On the '
            'known-data image the LiteThumbnail and FullScreen folders beside it hold files keyed the same '
            'way; they are not reported. Date Created and Date Modified are DATE_CREATED and DATE_MODIFIED '
            'read as Unix milliseconds. A stored 0, a NULL, a negative or a non-integer time is shown blank. '
            'Date Modified leads the table; what event either column records is not established. The mint log '
            'records four tabs left open at 15:41:55 UTC and two pages opened at 17:37:37 and 17:37:50 UTC, '
            'and TABS held six rows, one per page. No row has TAB_ID 1_4; the Tab Records artifact holds a '
            'closed record for tab 4 (closing time 15:41:54 UTC) and the mint log records one tab closed at '
            '15:41:55 UTC. Five tabs whose pages the mint log places between 15:19 (intents sent before first '
            'run) and 17:37:37 UTC all had Date Created 17:37:39 UTC, and the tab opened at 17:37:50 UTC had '
            'Date Created 17:37:50 UTC. On the known-data image BOOKMARKS MODIFIED (3 rows), READINGLIST '
            'modified, and TABS DATE_CREATED and DATE_MODIFIED held times of 17:37:39 to 17:37:59 UTC, while '
            'most of the items were made between 15:19 and 15:41 UTC (mint log); those four columns do not by '
            'themselves record when the item was made. TAB_ACTIVATE (as stored) held true on one row (TAB_ID '
            '1_6) on the known-data image. IS_DELETED (as stored) and IS_INCOGNITO (as stored) held 0 and '
            'Group Name had no value on every row of the images checked. Not reported: the per-tab files '
            'files/<w>_tab<n> and <w>tab_state, whose format is not parsed here (on the known-data image the '
            'file for tab 1_5 contained the URLs of the three pages that tab had loaded, per the mint log), '
            'the TAB_FAV_ICON blob, TAB_GROUP_COLOR, TAB_USAGE and the sync, device and account columns.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SBrowser.db*',
                  '*/com.sec.android.app.sbrowser/cache/Bitmap/Thumbnail/*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 6 rows",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 1 row",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 1 row",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 0 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 5 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 4 rows",
        },
    },
    "samsung_internet_tab_records": {
        "name": "Samsung Internet - Tab Records (SmartTabDelete)",
        "description": "Per-tab records from the SMARTTABDELETE table of SmartTabDelete.db, including tabs that "
                       "were closed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per SMARTTABDELETE row in com.sec.android.app.sbrowser/databases/SmartTabDelete.db. '
            'Column names are the stored ones because their meanings are not sourced; the three times are '
            'read as Unix milliseconds. A stored 0, a NULL, a negative or a non-integer time is shown blank. '
            'On samsung_a166u_a16_known_20261116 the table held one row per tab number 1 to 7, including tab '
            '4, which is not in TABS: its TAB_CLOSED_STATUS was 1 and its TAB_CLOSING_TIME 15:41:54 UTC, '
            'against the tab closed at 15:41:55 UTC in the mint log; the other six rows had TAB_CLOSED_STATUS '
            '0 and a TAB_CLOSING_TIME of 0, shown blank. TAB_URL holds a host name, not a full URL. '
            'TAB_CREATION_TIME ran from 15:19:53 to 17:37:59 UTC; for the tabs opened by intent at 17:37:37 '
            'and 17:37:50 UTC it was 17:37:45 and 17:37:59 UTC, and for tab 5, whose page changed twice in '
            'the session, it was 15:40:30 UTC, so what event sets it is not established. TAB_LAUNCHED_TYPE, '
            'CUMULATIVE_COUNT and TAB_CUMULATIVE_TIME are shown as stored; their meanings are not '
            'established. The period, training, refresh and EXTRA columns are not reported. Rows were present '
            'on hc_pixel8pro_a16 (4), hc_pixel8pro_a17 (4) and s20fe_a13 (1), not checked against known data.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SmartTabDelete.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 7 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 4 rows",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
        },
    },
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_PACKAGE = '/com.sec.android.app.sbrowser/'


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _split(context, file_found):
    """(container, path inside the package) for a file, using the storage-neutral key."""
    key, _rank = canonical_path(context.get_relative_path(file_found))
    key = key.replace('\x00de:', '\x00ce:')  # one app's DE and CE copies are one container here
    if _PACKAGE not in key:
        return key, ''
    container, inner = key.split(_PACKAGE, 1)
    return container, inner


def _sniffed_extension(path):
    """An extension for the media copy, from the file's own bytes, or None."""
    try:
        with open(path, 'rb') as handle:
            head = handle.read(4096)
    except OSError:
        return None, None
    if head.startswith(b'\xff\xd8\xff'):
        return '.jpg', None
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png', None
    if b'MIME-Version:' in head and b'multipart/related' in head:
        return '.mhtml', 'multipart/related'
    return None, None


def _check_in(path, name):
    extension, mime = _sniffed_extension(path)
    return check_in_media(path, name, force_extension=extension, force_type=mime) or ''


def _select(db, table, wanted):
    present = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    columns = ', '.join(f'"{name}"' if name in present else f'NULL AS "{name}"' for name in wanted)
    return [dict(zip(wanted, row)) for row in db.execute(f'SELECT {columns} FROM "{table}"').fetchall()]


def _read_table(file_found, table, wanted):
    db = open_sqlite_db_readonly(file_found)
    if db is None:
        return None
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if table not in tables:
            return []
        return _select(db, table, wanted)
    except sqlite3.Error as ex:
        logfunc(f'Samsung Internet: {table} not read from {file_found}: {ex}')
        return None
    finally:
        db.close()


def _databases(context):
    for file_found in unique_files(context):
        file_found = str(file_found)
        if file_found.endswith('/databases/SBrowser.db') or file_found.endswith('\\databases\\SBrowser.db'):
            yield file_found


_BOOKMARK_COLUMNS = ('_ID', 'URL', 'TITLE', 'FOLDER', 'PARENT', 'DELETED', 'CREATED', 'MODIFIED',
                     'bookmark_type', 'TAGS')


@artifact_processor
def samsung_internet_bookmarks(context):
    data_list = []
    source_paths = []
    for file_found in _databases(context):
        rows = _read_table(file_found, 'BOOKMARKS', _BOOKMARK_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        folders = {row['_ID']: row['TITLE'] for row in rows if row['FOLDER'] == 1}
        for row in rows:
            if row['FOLDER'] == 1:
                continue
            data_list.append((
                _ms_to_utc(row['CREATED']),
                _ms_to_utc(row['MODIFIED']),
                row['TITLE'] or '',
                row['URL'] or '',
                folders.get(row['PARENT'], row['PARENT']),
                row['bookmark_type'],
                row['DELETED'],
                row['TAGS'] or '',
                row['_ID'],
            ))
    data_headers = (('Created', 'datetime'), ('Modified', 'datetime'), 'Title', 'URL', 'Folder',
                    'bookmark_type (as stored)', 'Deleted (as stored)', 'Tags (as stored)', 'Row ID')
    return data_headers, data_list, '\n'.join(source_paths)


_READINGLIST_COLUMNS = ('_id', 'title', 'url', 'dir_path', 'created', 'modified', 'is_deleted', 'isReadingItem')


@artifact_processor
def samsung_internet_saved_pages(context):
    files_found = [str(f) for f in unique_files(context)]
    saved = {}
    for file_found in files_found:
        if '/files/readinglist/' in file_found.replace('\\', '/') and not os.path.isdir(file_found):
            saved[_split(context, file_found)] = file_found

    data_list = []
    source_paths = []
    for file_found in files_found:
        if not (file_found.endswith('/databases/SBrowser.db') or file_found.endswith('\\databases\\SBrowser.db')):
            continue
        rows = _read_table(file_found, 'READINGLIST', _READINGLIST_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        container, _inner = _split(context, file_found)
        for row in rows:
            media_ref = ''
            name = os.path.basename(str(row['dir_path'] or ''))
            match = None
            stored = str(row['dir_path'] or '').replace('\\', '/')
            if _PACKAGE in stored:
                match = saved.get((container, stored.split(_PACKAGE, 1)[1]))
            if match:
                source_paths.append(match)
                media_ref = _check_in(match, name)
            data_list.append((
                _ms_to_utc(row['created']),
                _ms_to_utc(row['modified']),
                row['title'] or '',
                row['url'] or '',
                media_ref,
                name,
                row['is_deleted'],
                row['isReadingItem'],
                row['_id'],
            ))
    data_headers = (('Created', 'datetime'), ('Modified', 'datetime'), 'Title', 'URL', ('Saved Page', 'media'),
                    'Saved Page File', 'is_deleted (as stored)', 'isReadingItem (as stored)', 'Row ID')
    return data_headers, data_list, '\n'.join(source_paths)


_TAB_COLUMNS = ('_ID', 'TAB_ID', 'TAB_INDEX', 'TAB_URL', 'TAB_TITLE', 'TAB_GROUP_NAME', 'TAB_ACTIVATE',
                'IS_DELETED', 'IS_INCOGNITO', 'DATE_CREATED', 'DATE_MODIFIED')


@artifact_processor
def samsung_internet_tabs(context):
    files_found = [str(f) for f in unique_files(context)]
    thumbnails = {}
    for file_found in files_found:
        container, inner = _split(context, file_found)
        parts = inner.split('/')
        # cache/Bitmap/Thumbnail/<window>/<tab number>.0
        if len(parts) == 5 and parts[:3] == ['cache', 'Bitmap', 'Thumbnail'] and parts[4].endswith('.0'):
            thumbnails[(container, f'{parts[3]}_{parts[4][:-2]}')] = file_found

    data_list = []
    source_paths = []
    for file_found in files_found:
        if not (file_found.endswith('/databases/SBrowser.db') or file_found.endswith('\\databases\\SBrowser.db')):
            continue
        rows = _read_table(file_found, 'TABS', _TAB_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        container, _inner = _split(context, file_found)
        for row in rows:
            media_ref = ''
            thumbnail = thumbnails.get((container, str(row['TAB_ID'])))
            if thumbnail:
                media_ref = _check_in(thumbnail, f'tab {row["TAB_ID"]} thumbnail')
            data_list.append((
                _ms_to_utc(row['DATE_MODIFIED']),
                _ms_to_utc(row['DATE_CREATED']),
                row['TAB_TITLE'] or '',
                row['TAB_URL'] or '',
                media_ref,
                row['TAB_ID'],
                row['TAB_INDEX'],
                row['TAB_ACTIVATE'],
                row['IS_DELETED'],
                row['IS_INCOGNITO'],
                row['TAB_GROUP_NAME'] or '',
            ))
    data_headers = (('Date Modified', 'datetime'), ('Date Created', 'datetime'), 'Title', 'URL',
                    ('Thumbnail', 'media'), 'Tab ID', 'Tab Index', 'TAB_ACTIVATE (as stored)',
                    'IS_DELETED (as stored)', 'IS_INCOGNITO (as stored)', 'Group Name')
    return data_headers, data_list, '\n'.join(source_paths)


_TAB_RECORD_COLUMNS = ('AUTO_CLOSE_KEY', 'TAB_ID', 'TAB_URL', 'TAB_LAUNCHED_TYPE', 'TAB_CREATION_TIME',
                       'TAB_LAST_ACTIVE_START_TIME', 'TAB_CLOSED_STATUS', 'TAB_CLOSING_TIME', 'CUMULATIVE_COUNT',
                       'TAB_CUMULATIVE_TIME')


@artifact_processor
def samsung_internet_tab_records(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.replace('\\', '/').endswith('/databases/SmartTabDelete.db'):
            continue
        rows = _read_table(file_found, 'SMARTTABDELETE', _TAB_RECORD_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        for row in sorted(rows, key=lambda r: (r['TAB_CREATION_TIME'] or 0, str(r['AUTO_CLOSE_KEY']))):
            data_list.append((
                _ms_to_utc(row['TAB_CREATION_TIME']),
                _ms_to_utc(row['TAB_LAST_ACTIVE_START_TIME']),
                _ms_to_utc(row['TAB_CLOSING_TIME']),
                row['TAB_URL'] or '',
                row['TAB_ID'],
                row['TAB_CLOSED_STATUS'],
                row['TAB_LAUNCHED_TYPE'] or '',
                row['CUMULATIVE_COUNT'],
                row['TAB_CUMULATIVE_TIME'],
                row['AUTO_CLOSE_KEY'] or '',
            ))
    data_headers = (('TAB_CREATION_TIME', 'datetime'), ('TAB_LAST_ACTIVE_START_TIME', 'datetime'),
                    ('TAB_CLOSING_TIME', 'datetime'), 'TAB_URL (as stored)', 'TAB_ID', 'TAB_CLOSED_STATUS (as stored)',
                    'TAB_LAUNCHED_TYPE (as stored)', 'CUMULATIVE_COUNT (as stored)', 'TAB_CUMULATIVE_TIME (as stored)',
                    'AUTO_CLOSE_KEY')
    return data_headers, data_list, '\n'.join(source_paths)
