import datetime
import hashlib
import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

__artifacts_v2__ = {
    "androidBrowserHistory": {
        "name": "Android Browser - History",
        "description": "Rows of the history table of browser2.db under com.android.browser (the AOSP Browser's package): title and URL, the date and created columns converted to UTC, and the visits and user_entered columns as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Browsers",
        "notes": "The history table is created by the stock Browser's BrowserProvider2 in browser2.db (https://android.googlesource.com/platform/packages/apps/Browser/+/ec090f9c44460676cc5760c309cbee0eba92de9a/src/com/android/browser/provider/BrowserProvider2.java#429, tag android-6.0.0_r1). The column meanings cited below are from BrowserContract at the same tag. Other Android versions and vendor builds that use this package name were not examined. The database is read with its -wal applied when the -wal is beside it. Without one the database file alone is read and the run log says so. On the known data two of the four history rows were only in the -wal. A browser2.db whose bytes equal one already read is read once (data/data and data/user/0 on the test tree); the -wal is not compared. Android User is taken from the path: n under data/user/<n>, 0 under data/data, blank for any other path. No other image in the Android corpus registry holds a browser2.db under com.android.browser (64 other keys, member lists searched; two of them are raw partition images whose files are not listed), so the artifacts are tested only with the known data emu_a6_browser_known_20261116 (Android 6.0 emulator and stock Browser 6.0 per its mint record) and a folder tree built from it, where a changed copy under data/user/10 added its own rows and a browser2.db of another package was not read. One row per history row. Date (UTC) is the date column, which BrowserContract documents as the date of the item's last visit in milliseconds since the epoch (https://android.googlesource.com/platform/frameworks/base/+/c02a10d8b626469ea64babebfd88fb96ea9ececf/core/java/android/provider/BrowserContract.java#211); Created (UTC) is created (a stored 0 or NULL is shown blank); Visit Count (as stored) is the visits column, which BrowserContract documents as a count (https://android.googlesource.com/platform/frameworks/base/+/c02a10d8b626469ea64babebfd88fb96ea9ececf/core/java/android/provider/BrowserContract.java#217); user_entered (as stored) is that column, which the contract does not document. On the known data the three pages opened at times recorded in the mint log had a Date (UTC) within one second of those times (0.15 to 0.58 seconds earlier) and a Visit Count (as stored) of 1, and a phrase searched from the address bar appeared as a fourth row whose URL is the search engine's results address with the phrase in its q parameter. Created (UTC) had no value (0) on all 4 rows, Visit Count (as stored) held 1 on all 4 rows, user_entered (as stored) held 0 on all 4 rows and Android User held 0 on all 4 rows.",
        "paths": ('*/com.android.browser/databases/browser2.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "emu_a6_browser_known_20261116": "Android 6.0 | com.android.browser 6.0 | 4 rows (known data)",
        },
    },
    "androidBrowserBookmarks": {
        "name": "Android Browser - Bookmarks",
        "description": "Rows of the bookmarks table of browser2.db under com.android.browser (the AOSP Browser's package): title, URL, folder flag, the parent row's title, deleted flag, account, and the created and modified columns converted to UTC.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Browsers",
        "notes": "The bookmarks table is created by the stock Browser's BrowserProvider2 in browser2.db (https://android.googlesource.com/platform/packages/apps/Browser/+/ec090f9c44460676cc5760c309cbee0eba92de9a/src/com/android/browser/provider/BrowserProvider2.java#404, tag android-6.0.0_r1). The column meanings cited below are from BrowserContract at the same tag. Other Android versions and vendor builds that use this package name were not examined. The database is read with its -wal applied when the -wal is beside it. Without one the database file alone is read and the run log says so. On the known data two of the four history rows, and one of the 16 bookmarks rows, were only in the -wal. A browser2.db whose bytes equal one already read is read once (data/data and data/user/0 on the test tree); the -wal is not compared. Android User is taken from the path: n under data/user/<n>, 0 under data/data, blank for any other path. No other image in the Android corpus registry holds a browser2.db under com.android.browser (64 other keys, member lists searched; two of them are raw partition images whose files are not listed), so the artifacts are tested only with the known data emu_a6_browser_known_20261116 (Android 6.0 emulator and stock Browser 6.0 per its mint record) and a folder tree built from it, where a changed copy under data/user/10 added its own rows and a browser2.db of another package was not read. One row per bookmarks row, folders included. Created (UTC) and Modified (UTC) are created and modified in milliseconds (https://android.googlesource.com/platform/frameworks/base/+/c02a10d8b626469ea64babebfd88fb96ea9ececf/core/java/android/provider/BrowserContract.java#175 and #148); Folder (as stored) is folder; Parent Folder is the title of the row its parent names; Deleted (as stored) is deleted, non-zero for a deleted item (https://android.googlesource.com/platform/frameworks/base/+/c02a10d8b626469ea64babebfd88fb96ea9ececf/core/java/android/provider/BrowserContract.java#395); Account Name and Account Type are as stored. On the known data 16 rows: the Bookmarks root folder, 14 default bookmarks that BrowserProvider2 inserts when it creates the database (https://android.googlesource.com/platform/packages/apps/Browser/+/ec090f9c44460676cc5760c309cbee0eba92de9a/src/com/android/browser/provider/BrowserProvider2.java#465 and #658), which shared one Created (UTC) within one second of the first recorded page opening and had no Modified (UTC), and the one page bookmarked from the menu, whose Created (UTC) and Modified (UTC) were equal and within one second of the time recorded in the mint log. A default bookmark row says nothing about use. Deleted (as stored) held 0 on all 16 rows, Account Name and Account Type had no value on any row, and Android User held 0 on all 16 rows.",
        "paths": ('*/com.android.browser/databases/browser2.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "emu_a6_browser_known_20261116": "Android 6.0 | com.android.browser 6.0 | 16 rows (known data)",
        },
    },
    "androidBrowserSearches": {
        "name": "Android Browser - Search Terms",
        "description": "Rows of the searches table of browser2.db under com.android.browser (the AOSP Browser's package): the search text and its date converted to UTC.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Browsers",
        "notes": "The searches table is created by the stock Browser's BrowserProvider2 in browser2.db (https://android.googlesource.com/platform/packages/apps/Browser/+/ec090f9c44460676cc5760c309cbee0eba92de9a/src/com/android/browser/provider/BrowserProvider2.java#448, tag android-6.0.0_r1). The column meanings cited below are from BrowserContract at the same tag. Other Android versions and vendor builds that use this package name were not examined. The database is read with its -wal applied when the -wal is beside it. Without one the database file alone is read and the run log says so. On the known data two of the four history rows were only in the -wal. A browser2.db whose bytes equal one already read is read once (data/data and data/user/0 on the test tree); the -wal is not compared. Android User is taken from the path: n under data/user/<n>, 0 under data/data, blank for any other path. No other image in the Android corpus registry holds a browser2.db under com.android.browser (64 other keys, member lists searched; two of them are raw partition images whose files are not listed), so the artifacts are tested only with the known data emu_a6_browser_known_20261116 (Android 6.0 emulator and stock Browser 6.0 per its mint record) and a folder tree built from it, where a changed copy under data/user/10 added its own rows and a browser2.db of another package was not read. One row per searches row: Search is search and Date (UTC) is date in milliseconds (https://android.googlesource.com/platform/frameworks/base/+/c02a10d8b626469ea64babebfd88fb96ea9ececf/core/java/android/provider/BrowserContract.java#491 and #497). The searches table was empty on the known data although a phrase was searched from the address bar; that search is in Android Browser - History as the results URL. So this artifact is unexercised: an empty table is not evidence that nothing was searched.",
        "paths": ('*/com.android.browser/databases/browser2.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "emu_a6_browser_known_20261116": "Android 6.0 | com.android.browser 6.0 | 0 rows (known data; searches table empty)",
        },
    },
}

_USER = re.compile(r'/data/user/(\d+)/')


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


def _databases(files_found):
    '''Each browser2.db once: byte-identical copies (data/data and data/user/0) are read once.'''
    seen = set()
    found = []
    candidates = [p for p in files_found if p.replace(os.sep, '/').endswith('/browser2.db')]
    for path in sorted(candidates, key=lambda p: ('/data/user/' in p.replace(os.sep, '/'), p)):
        try:
            with open(path, 'rb') as handle:
                digest = hashlib.sha1(handle.read()).hexdigest()
        except OSError as ex:
            logfunc(f'Android Browser: could not hash {path}: {ex}')
            digest = path
        if digest not in seen:
            seen.add(digest)
            found.append(path)
    return found


def _rows(context, label, table, query):
    data_list = []
    sources = []
    for path in _databases(context.get_files_found()):
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'{label}: could not open {path}')
            continue
        try:
            sources.append(path)
            if table not in {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
                logfunc(f'{label}: no {table} table in {path}')
                continue
            for row in db.execute(query):
                data_list.append((_android_user(context.get_relative_path(path)), row))
        except sqlite3.Error as ex:
            logfunc(f'{label}: could not read {path}: {ex}')
        finally:
            db.close()
    return data_list, '\n'.join(sources)


def _value(value):
    return value if value is not None else ''


@artifact_processor
def androidBrowserHistory(context):
    rows, source = _rows(context, 'Android Browser - History', 'history',
                         'SELECT _id, title, url, date, created, visits, user_entered FROM history ORDER BY date, _id')
    data_list = [(_ms_to_utc(date), _ms_to_utc(created), user, _value(title), _value(url), _value(visits),
                  _value(entered), row_id)
                 for user, (row_id, title, url, date, created, visits, entered) in rows]
    data_headers = (('Date (UTC)', 'datetime'), ('Created (UTC)', 'datetime'), 'Android User', 'Title',
                    'URL', 'Visit Count (as stored)', 'user_entered (as stored)', 'Row ID')
    return data_headers, data_list, source


@artifact_processor
def androidBrowserBookmarks(context):
    rows, source = _rows(context, 'Android Browser - Bookmarks', 'bookmarks',
                         'SELECT b._id, b.title, b.url, b.folder, p.title, b.deleted, b.account_name, '
                         'b.account_type, b.created, b.modified FROM bookmarks b '
                         'LEFT JOIN bookmarks p ON p._id = b.parent ORDER BY b._id')
    data_list = [(_ms_to_utc(created), _ms_to_utc(modified), user, _value(title), _value(url), _value(folder),
                  _value(parent), _value(deleted), _value(account), _value(account_type), row_id)
                 for user, (row_id, title, url, folder, parent, deleted, account, account_type, created,
                            modified) in rows]
    data_headers = (('Created (UTC)', 'datetime'), ('Modified (UTC)', 'datetime'), 'Android User', 'Title', 'URL',
                    'Folder (as stored)', 'Parent Folder', 'Deleted (as stored)', 'Account Name', 'Account Type',
                    'Row ID')
    return data_headers, data_list, source


@artifact_processor
def androidBrowserSearches(context):
    rows, source = _rows(context, 'Android Browser - Search Terms', 'searches',
                         'SELECT _id, search, date FROM searches ORDER BY date, _id')
    data_list = [(_ms_to_utc(date), user, _value(search), row_id) for user, (row_id, search, date) in rows]
    data_headers = (('Date (UTC)', 'datetime'), 'Android User', 'Search', 'Row ID')
    return data_headers, data_list, source
