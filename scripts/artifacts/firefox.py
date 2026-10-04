__artifacts_v2__ = {
    "get_firefox_history": {
        "name": "Firefox - Web History",
        "description": "Firefox places.sqlite web history",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Reference: Mozilla application-services, 'places Timestamp is milliseconds on "
                 "Android', "
                 "https://github.com/mozilla/application-services/blob/71d8b70bf62e6911d9d439a559aab56d8bef38b9/components/support/types/src/lib.rs. "
                 "This artifact is not limited to org.mozilla.firefox: the path pattern is "
                 "anchored on the files/places.sqlite layout rather than on a package, so "
                 "Gecko-based forks that use that layout are read too, and the Browser column "
                 "names the package each row came from. Tor Browser also uses this layout and "
                 "its bookmarks are additionally reported by the dedicated Tor Browser artifact. "
                 "On the tested emulator Firefox 154.0.1 and Fennec F-Droid 154.0.0 were "
                 "installed side by side and both are reported. "
                 "One row per moz_places page that has at least one row in moz_historyvisits, "
                 "matched on moz_historyvisits.place_id, which the table declares as its foreign "
                 "key to moz_places(id). Reference: Mozilla application-services, "
                 "'create_shared_schema.sql', "
                 "https://github.com/mozilla/application-services/blob/71d8b70bf62e6911d9d439a559aab56d8bef38b9/components/places/sql/create_shared_schema.sql#L74-L86. "
                 "A page in moz_places with no visit row is not reported; Firefox - Web Visits "
                 "lists each visit. On pixel7a_a14 moz_places held 8 pages, each with a visit row, and all 8 are reported. On emu_a15_oss_v5 "
                 "all 8 pages are reported (5 in org.mozilla.firefox and 3 in "
                 "org.mozilla.fennec_fdroid). Last Visit Date and Visit Count are the "
                 "last_visit_date_local and visit_count_local columns. Hidden and Typed show No "
                 "or Yes for a stored 0 or 1 and any other stored value as stored; every page on "
                 "both tested images stored 0 in both.",
        "paths": ('*/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "emu_a15_oss_v5": "Android 15 | org.mozilla.firefox vc 2016180578, org.mozilla.fennec_fdroid vc 1540020 | 8 rows",
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 8 rows",
        },
    },
    "get_firefox_visits": {
        "name": "Firefox - Web Visits",
        "description": "Firefox places.sqlite individual page visits",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Reference: Mozilla application-services, 'places Timestamp is milliseconds on "
                 "Android', "
                 "https://github.com/mozilla/application-services/blob/71d8b70bf62e6911d9d439a559aab56d8bef38b9/components/support/types/src/lib.rs. "
                 "Reference: Mozilla, 'nsINavHistoryService TRANSITION_* constants', "
                 "https://github.com/mozilla-firefox/firefox/blob/6d751cf5d0af4b7fcc1b232b6c2ba0551afabe1d/toolkit/components/places/nsINavHistoryService.idl#L929-L977. "
                 "Any other stored visit_type is shown as stored, and Typed shows a stored "
                 "value other than 0 or 1 as stored; the tested images stored visit types 1, 5 "
                 "and 6 and a typed value of 0 only. "
                 "This artifact is not limited to org.mozilla.firefox: the path pattern is "
                 "anchored on the files/places.sqlite layout rather than on a package, so "
                 "Gecko-based forks that use that layout are read too, and the Browser column "
                 "names the package each row came from. Tor Browser also uses this layout and "
                 "its bookmarks are additionally reported by the dedicated Tor Browser artifact. "
                 "On the tested emulator Firefox 154.0.1 and Fennec F-Droid 154.0.0 were "
                 "installed side by side and both are reported.",
        "paths": ('*/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "emu_a15_oss_v5": "Android 15 | org.mozilla.firefox vc 2016180578, org.mozilla.fennec_fdroid vc 1540020 | 8 rows",
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 8 rows",
        },
    },
    "get_firefox_bookmarks": {
        "name": "Firefox - Bookmarks",
        "description": "Firefox places.sqlite bookmarks",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Reference: Mozilla application-services, 'places Timestamp is milliseconds on "
                 "Android', "
                 "https://github.com/mozilla/application-services/blob/71d8b70bf62e6911d9d439a559aab56d8bef38b9/components/support/types/src/lib.rs. "
                 "This artifact is not limited to org.mozilla.firefox: the path pattern is "
                 "anchored on the files/places.sqlite layout rather than on a package, so "
                 "Gecko-based forks that use that layout are read too, and the Browser column "
                 "names the package each row came from. Tor Browser also uses this layout and "
                 "its bookmarks are additionally reported by the dedicated Tor Browser artifact. "
                 "On the tested emulator Firefox 154.0.1 and Fennec F-Droid 154.0.0 were "
                 "installed side by side and both are reported. "
                 "Bookmark Type shows URL, Folder or Separator for a stored type of 1, 2 or 3, "
                 "following BookmarkType in components/places/src/types.rs at the same "
                 "application-services commit (Bookmark = 1, Folder = 2, Separator = 3); any other "
                 "stored value is shown as stored. Every bookmark row on the tested images stored "
                 "type 2.",
        "paths": ('*/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "emu_a15_oss_v5": "Android 15 | org.mozilla.firefox vc 2016180578, org.mozilla.fennec_fdroid vc 1540020, org.torproject.torbrowser vc 2016179194 | 15 rows",
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 5 rows",
        },
    },
    "get_firefox_searches": {
        "name": "Firefox - Search Terms",
        "description": "Firefox places.sqlite search queries",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Firefox",
        "notes": "This artifact is not limited to org.mozilla.firefox: the path pattern is "
                 "anchored on the files/places.sqlite layout rather than on a package, so "
                 "Gecko-based forks that use that layout are read too, and the Browser column "
                 "names the package each row came from. Tor Browser also uses this layout and "
                 "its bookmarks are additionally reported by the dedicated Tor Browser artifact. "
                 "On the tested emulator Firefox 154.0.1 and Fennec F-Droid 154.0.0 were "
                 "installed side by side and both are reported.",
        "paths": ('*/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "emu_a15_oss_v5": "Android 15 | org.mozilla.firefox vc 2016180578, org.mozilla.fennec_fdroid vc 1540020 | 0 rows, checked: moz_places_metadata_search_queries is empty in both stores",
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 2 rows",
        },
    }
}

import datetime
import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _dbs(context):
    """Every places.sqlite the extraction holds, one per Gecko browser installed.

    Storage views are collapsed first: an extraction carries the same app directory
    under more than one path, so reading each match would report every row per view.
    """
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found).replace('\\', '/')
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if os.path.basename(file_found) == 'places.sqlite':
            found.append(file_found)
    return found


def _browser(file_found):
    """The package directory the store sits in, which is what names the browser."""
    match = re.search(r'/([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)/files/places\.sqlite',
                      str(file_found).replace('\\', '/'))
    return match.group(1) if match else ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_firefox_history(context):
    data_list = []
    sources = []
    for source_path in _dbs(context):
        browser = _browser(source_path)
        # A page is reported when moz_historyvisits holds a visit for it, through
        # place_id, the column the table declares as its foreign key to moz_places.
        rows = _run(source_path, '''
        SELECT moz_places.last_visit_date_local, moz_places.url, moz_places.title,
        moz_places.visit_count_local, moz_places.description,
        CASE moz_places.hidden WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' ELSE moz_places.hidden END,
        CASE moz_places.typed WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' ELSE moz_places.typed END,
        moz_places.frecency, moz_places.preview_image_url
        FROM moz_places
        WHERE EXISTS (SELECT 1 FROM moz_historyvisits
                      WHERE moz_historyvisits.place_id = moz_places.id)
        ORDER BY moz_places.last_visit_date_local ASC
    ''')
        data_list.extend((_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], browser)
                         for r in rows)
        if rows:
            sources.append(context.get_relative_path(source_path))

    data_headers = (('Last Visit Date', 'datetime'), 'URL', 'Title', 'Visit Count', 'Description',
                    'Hidden', 'Typed', 'Frecency', 'Preview Image URL', 'Browser')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_firefox_visits(context):
    data_list = []
    sources = []
    for source_path in _dbs(context):
        browser = _browser(source_path)
        rows = _run(source_path, '''
        SELECT moz_historyvisits.visit_date, moz_places.url, moz_places.title,
        moz_historyvisits.id, moz_historyvisits.from_visit,
        CASE moz_historyvisits.visit_type
            WHEN 1 THEN 'TRANSITION_LINK' WHEN 2 THEN 'TRANSITION_TYPED'
            WHEN 3 THEN 'TRANSITION_BOOKMARK' WHEN 4 THEN 'TRANSITION_EMBED'
            WHEN 5 THEN 'TRANSITION_REDIRECT_PERMANENT' WHEN 6 THEN 'TRANSITION_REDIRECT_TEMPORARY'
            WHEN 7 THEN 'TRANSITION_DOWNLOAD' WHEN 8 THEN 'TRANSITION_FRAMED_LINK'
            WHEN 9 THEN 'TRANSITION_RELOAD'
            ELSE moz_historyvisits.visit_type END,
        CASE moz_places.typed WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' ELSE moz_places.typed END
        FROM moz_historyvisits
        INNER JOIN moz_places ON moz_places.id = moz_historyvisits.place_id
        ORDER BY moz_historyvisits.visit_date ASC
    ''')
        data_list.extend((_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], browser)
                         for r in rows)
        if rows:
            sources.append(context.get_relative_path(source_path))

    data_headers = (('Visit Date', 'datetime'), 'URL', 'Title', 'Visit ID', 'From Visit ID',
                    'Visit Type', 'Typed', 'Browser')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_firefox_bookmarks(context):
    data_list = []
    sources = []
    for source_path in _dbs(context):
        browser = _browser(source_path)
        rows = _run(source_path, '''
        SELECT moz_bookmarks.dateAdded, moz_bookmarks.lastModified, moz_bookmarks.title, moz_places.url,
        CASE moz_bookmarks.type WHEN 1 THEN 'URL' WHEN 2 THEN 'Folder' WHEN 3 THEN 'Separator'
            ELSE moz_bookmarks.type END,
        moz_bookmarks.id, moz_bookmarks.parent, moz_bookmarks.position, moz_bookmarks.syncStatus
        FROM moz_bookmarks
        LEFT JOIN moz_places ON moz_bookmarks.fk = moz_places.id
        ORDER BY moz_bookmarks.id ASC
    ''')
        data_list.extend((_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7],
                          r[8], browser) for r in rows)
        if rows:
            sources.append(context.get_relative_path(source_path))

    data_headers = (('Added Timestamp', 'datetime'), ('Modified Timestamp', 'datetime'), 'Title',
                    'URL', 'Bookmark Type', 'ID', 'Parent', 'Position', 'Sync Status', 'Browser')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_firefox_searches(context):
    data_list = []
    sources = []
    for source_path in _dbs(context):
        browser = _browser(source_path)
        # Older Firefox databases have no search-queries table (community report,
        # PR #628).
        if not does_table_exist_in_db(source_path, 'moz_places_metadata_search_queries'):
            logfunc(f'moz_places_metadata_search_queries not present in {browser}; '
                    'this Firefox generation records no search terms table')
            continue
        rows = _run(source_path, '''
            SELECT id, term FROM moz_places_metadata_search_queries ORDER BY id ASC
        ''')
        data_list.extend((r[0], r[1], browser) for r in rows)
        if rows:
            sources.append(context.get_relative_path(source_path))

    data_headers = ('ID', 'Search Term', 'Browser')
    return data_headers, data_list, '\n'.join(sources)
