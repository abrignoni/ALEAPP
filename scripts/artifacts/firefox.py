__artifacts_v2__ = {
    "get_firefox_history": {
        "name": "Firefox - Web History",
        "description": "Firefox places.sqlite web history",
        "author": "@stark4n6",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Reference: Mozilla application-services, 'places Timestamp is milliseconds on Android (desktop PRTime is microseconds)', https://github.com/mozilla/application-services/blob/main/components/support/types/src/lib.rs",
        "paths": ('*/org.mozilla.firefox/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 7 rows",
        },
    },
    "get_firefox_visits": {
        "name": "Firefox - Web Visits",
        "description": "Firefox places.sqlite individual page visits",
        "author": "@stark4n6",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Reference: Mozilla application-services, 'places Timestamp is milliseconds on Android (desktop PRTime is microseconds)', https://github.com/mozilla/application-services/blob/main/components/support/types/src/lib.rs. Reference: Mozilla, 'nsINavHistoryService TRANSITION_* constants', https://searchfox.org/mozilla-central/source/toolkit/components/places/nsINavHistoryService.idl",
        "paths": ('*/org.mozilla.firefox/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 8 rows",
        },
    },
    "get_firefox_bookmarks": {
        "name": "Firefox - Bookmarks",
        "description": "Firefox places.sqlite bookmarks",
        "author": "@stark4n6",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Reference: Mozilla application-services, 'places Timestamp is milliseconds on Android (desktop PRTime is microseconds)', https://github.com/mozilla/application-services/blob/main/components/support/types/src/lib.rs",
        "paths": ('*/org.mozilla.firefox/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 5 rows",
        },
    },
    "get_firefox_searches": {
        "name": "Firefox - Search Terms",
        "description": "Firefox places.sqlite search queries",
        "author": "@stark4n6",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/files/places.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 2 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if os.path.basename(file_found) == 'places.sqlite':
            return file_found
    return ''


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
    files_found = context.get_files_found()
    source_path = _db(files_found)
    # Older Firefox databases have no moz_places_metadata table, and the inner
    # join silently returned nothing on them (community report, PR #628). The
    # join selects no columns, so it is only applied where the table exists.
    metadata_join = ('INNER JOIN moz_places_metadata ON moz_places.id = moz_places_metadata.id'
                     if source_path and does_table_exist_in_db(source_path, 'moz_places_metadata')
                     else '')
    rows = _run(source_path, f'''
        SELECT moz_places.last_visit_date_local, moz_places.url, moz_places.title,
        moz_places.visit_count_local, moz_places.description,
        CASE moz_places.hidden WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        CASE moz_places.typed WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END,
        moz_places.frecency, moz_places.preview_image_url
        FROM moz_places
        INNER JOIN moz_historyvisits ON moz_places.origin_id = moz_historyvisits.id
        {metadata_join}
        ORDER BY moz_places.last_visit_date_local ASC
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]) for r in rows]
    data_headers = (('Last Visit Date', 'datetime'), 'URL', 'Title', 'Visit Count', 'Description',
                    'Hidden', 'Typed', 'Frecency', 'Preview Image URL')
    return data_headers, data_list, source_path


@artifact_processor
def get_firefox_visits(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT moz_historyvisits.visit_date, moz_places.url, moz_places.title,
        moz_historyvisits.id, moz_historyvisits.from_visit,
        CASE moz_historyvisits.visit_type
            WHEN 1 THEN 'TRANSITION_LINK' WHEN 2 THEN 'TRANSITION_TYPED'
            WHEN 3 THEN 'TRANSITION_BOOKMARK' WHEN 4 THEN 'TRANSITION_EMBED'
            WHEN 5 THEN 'TRANSITION_REDIRECT_PERMANENT' WHEN 6 THEN 'TRANSITION_REDIRECT_TEMPORARY'
            WHEN 7 THEN 'TRANSITION_DOWNLOAD' WHEN 8 THEN 'TRANSITION_FRAMED_LINK'
            WHEN 9 THEN 'TRANSITION_RELOAD' END,
        CASE moz_places.typed WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END
        FROM moz_historyvisits
        INNER JOIN moz_places ON moz_places.id = moz_historyvisits.place_id
        ORDER BY moz_historyvisits.visit_date ASC
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
    data_headers = (('Visit Date', 'datetime'), 'URL', 'Title', 'Visit ID', 'From Visit ID',
                    'Visit Type', 'Typed')
    return data_headers, data_list, source_path


@artifact_processor
def get_firefox_bookmarks(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT moz_bookmarks.dateAdded, moz_bookmarks.lastModified, moz_bookmarks.title, moz_places.url,
        CASE moz_bookmarks.type WHEN 1 THEN 'URL' WHEN 2 THEN 'Folder' WHEN 3 THEN 'Separator' END,
        moz_bookmarks.id, moz_bookmarks.parent, moz_bookmarks.position, moz_bookmarks.syncStatus
        FROM moz_bookmarks
        LEFT JOIN moz_places ON moz_bookmarks.fk = moz_places.id
        ORDER BY moz_bookmarks.id ASC
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8])
                 for r in rows]
    data_headers = (('Added Timestamp', 'datetime'), ('Modified Timestamp', 'datetime'), 'Title',
                    'URL', 'Bookmark Type', 'ID', 'Parent', 'Position', 'Sync Status')
    return data_headers, data_list, source_path


@artifact_processor
def get_firefox_searches(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    # Older Firefox databases have no search-queries table (community report,
    # PR #628).
    if source_path and not does_table_exist_in_db(source_path, 'moz_places_metadata_search_queries'):
        logfunc('moz_places_metadata_search_queries not present; this Firefox generation records no search terms table')
        source_path_rows = []
        rows = source_path_rows
    else:
        rows = _run(source_path, '''
            SELECT id, term FROM moz_places_metadata_search_queries ORDER BY id ASC
        ''')
    data_list = [(r[0], r[1]) for r in rows]
    data_headers = ('ID', 'Search Term')
    return data_headers, data_list, source_path
