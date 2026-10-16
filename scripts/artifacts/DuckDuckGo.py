# pylint: disable=W0631
__artifacts_v2__ = {
    "duckduckgo_bookmarks": {
        "name": "DuckDuckGo - Bookmarks",
        "description": "Parses DuckDuckGo Bookmarks",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-05-21",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested by the module author on app version 5.237.0 (3 June 2025). The two images listed in sample_data produced no rows, so the query is not exercised on registered data.",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bookmark",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 0 rows",
        }
    },
    "duckduckgo_favorites": {
        "name": "DuckDuckGo - Favorited Sites",
        "description": "Parses DuckDuckGo favorite Sites",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-05-30",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested by the module author on app version 5.237.0 (3 June 2025). The two images listed in sample_data produced no rows, so the query is not exercised on registered data.",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "star",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 0 rows",
        }
    },
    "duckduckgo_history": {
        "name": "DuckDuckGo - Web Browser History",
        "description": "Parses DuckDuckGo Web Browsing History",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-05-21",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": (
            "Tested by the module author on app version 5.237.0 (3 June 2025). Visit Date "
            "is the stored visits_list.timestamp string as recorded, reported as text "
            "and not as a UTC date and time, because the store records no time zone "
            "for it. "
            "DuckDuckGo's DatabaseDateFormatter.timestamp formats a LocalDateTime with "
            "the pattern yyyy-MM-dd'T'HH:mm:ss and takes LocalDateTime.now() when no "
            "value is passed, so the string is a wall clock reading with no zone "
            "written beside it ("
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/common/common-utils/src/main/java/com/duckduckgo/common/utils/formatters/time/DatabaseDateFormatter.kt#L30-L42"
            "). "
            "The history writer passes LocalDateTime.now() ("
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/history/history-impl/src/main/java/com/duckduckgo/history/impl/HistoryRepository.kt#L76-L83"
            "; "
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/history/history-impl/src/main/java/com/duckduckgo/history/impl/store/HistoryDao.kt#L43-L61"
            "). That source was read at one commit of the develop branch, which is "
            "newer than the app versions on the two images in sample_data. All 12 "
            "stored values on each of those images have the shape "
            "YYYY-MM-DDTHH:MM:SS. Which zone the device was set to when a value was "
            "written is not recorded in this table. "
            "History Type shows the stored isSerp flag as 'DuckDuckGo Search' for "
            "1 and 'Web Page Visit' for 0."
        ),
        "paths": ('*/com.duckduckgo.mobile.android/databases/history.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 12 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 12 rows",
        }
    },
    "duckduckgo_opentabs": {
        "name": "DuckDuckGo - Open Tabs",
        "description": "Parses DuckDuckGo Open Tab Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-05-21",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": (
            "Tested on version 5.255.0 (Oct, 31st 2025). Cached Tab Preview Time (UTC) is "
            "decoded from the tab preview file name, which is a number read as a Unix time in "
            "milliseconds; that reading is not documented and the file name is its only "
            "basis. It is rendered in UTC. Tab Last Accessed is the stored "
            "tabs.lastAccessTime string as recorded, reported as text and not as a UTC "
            "date and time, because the store records no time zone for it. "
            "DuckDuckGo's DatabaseDateFormatter.timestamp formats a LocalDateTime with "
            "the pattern yyyy-MM-dd'T'HH:mm:ss and takes LocalDateTime.now() when no "
            "value is passed, so the string is a wall clock reading with no zone "
            "written beside it ("
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/common/common-utils/src/main/java/com/duckduckgo/common/utils/formatters/time/DatabaseDateFormatter.kt#L30-L42"
            "). "
            "The tab writer passes LocalDateTime.now() through a converter that calls "
            "that function ("
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/common/common-utils/src/main/java/com/duckduckgo/common/utils/CurrentTimeProvider.kt#L39"
            "; "
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/app/src/main/java/com/duckduckgo/app/tabs/model/TabDataRepository.kt#L331-L333"
            "; "
            "https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/browser-api/src/main/java/com/duckduckgo/app/tabs/model/TabEntitiy.kt#L65-L67"
            "). That source was read at one commit of the develop branch, which is "
            "newer than the app versions on the two images in sample_data. On "
            "hc_pixel8pro_a16 both tabs store a Tab Last Accessed value 4 hours "
            "behind that tab's Cached Tab Preview Time (UTC), to within 2 seconds, so "
            "on that image the stored value is not a UTC reading. Which zone the "
            "device was set to when a value was written is not recorded in this "
            "table. Tab Last Accessed is reported as 'Unavailable' on versions "
            "whose tabs table has no lastAccessTime column, which is the case on "
            "pixel7a_a14."
        ),
        "paths": (
            '*/com.duckduckgo.mobile.android/databases/app.db*',
            '*/com.duckduckgo.mobile.android/cache/tabPreviews/*/*.jpg'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "book",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 2 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 3 rows",
        }
    },
    "duckduckgo_fireproof": {
        "name": "DuckDuckGo - FireProof Sites",
        "description": "Parses DuckDuckGo FireProof Sites",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested by the module author on app version 5.255.0 (31 October 2025). The two images listed in sample_data produced no rows, so the query is not exercised on registered data.",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 0 rows",
        }
    },
    "duckduckgo_downloads": {
        "name": "DuckDuckGo - Downloads",
        "description": "Parses DuckDuckGo Downloads",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-13",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested by the module author on app version 5.255.0 (31 October 2025). The two images listed in sample_data produced no rows, so the query is not exercised on registered data. Reference: DuckDuckGo Android, 'DownloadStatus (STARTED=0, FINISHED=1)', https://github.com/duckduckgo/Android/blob/ce9fb1ffde1f76cea97f78bbc97fab05e5e74ea9/downloads/downloads-store/src/main/java/com/duckduckgo/downloads/store/DownloadStatus.kt#L20-L21. Download Date is the stored downloads.createdAt string as recorded, reported as text and not as a UTC date and time, because the store records no time zone for it. The app's DownloadEntity gives createdAt the default DatabaseDateFormatter.timestamp() (https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/downloads/downloads-store/src/main/java/com/duckduckgo/downloads/store/DownloadEntity.kt#L32), which formats LocalDateTime.now() with the pattern yyyy-MM-dd'T'HH:mm:ss, a wall clock reading with no zone written beside it (https://github.com/duckduckgo/Android/blob/b523dd8fd563ecc7248a14a8dfa9245371343055/common/common-utils/src/main/java/com/duckduckgo/common/utils/formatters/time/DatabaseDateFormatter.kt#L30-L42). That source was read at one commit of the develop branch. Neither image in sample_data holds a downloads row, so the stored shape was not observed.",
        "paths": ('*/com.duckduckgo.mobile.android/databases/downloads.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 0 rows",
        }
    },
    "duckduckgo_thumbnails": {
        "name": "DuckDuckGo - Tab Thumbnails",
        "description": "Parses DuckDuckGo Tab thumbnail Information",
        "author": "@abrignoni & @stark4n6, @AlexisBrignoni, Codex",
        "creation_date": "2022-05-28",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": (
            "Timestamp (UTC) is decoded from the thumbnail file name, which is a number read "
            "as a Unix time in milliseconds; that reading is not documented and the "
            "file name is its only basis. It is rendered in UTC. Referenced In Tabs Table "
            "records whether the file name appears in the tabs table of app.db; it describes "
            "that reference only and does not establish whether a tab is open or closed. "
            "A nonnumeric or out-of-range file name is retained with a blank timestamp and logged."
        ),
        "paths": (
            '*/com.duckduckgo.mobile.android/cache/tabPreviews/*/*.jpg',
            '*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 5 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 5 rows",
        }
    },
    "duckduckgo_duckai": {
        "name": "DuckDuckGo - Duck AI",
        "description": "Parses Duck AI conversations stored in the WebView Local Storage LevelDB",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested by the module author on app version 5.255.0 (31 October 2025). The two images listed in sample_data produced no rows, so the reader is not exercised on registered data.",
        "paths": ('*com.duckduckgo.mobile.android/app_webview/Default/Local Storage/leveldb/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 0 rows",
        }
    },
    "duckduckgo_cookies": {
        "name": "DuckDuckGo - Cookies",
        "description": "Parses DuckDuckGo Cookies",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-14",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested by the module author on app version 5.255.0 (31 October 2025). Reads main Cookies or cookies files, excluding sidecars; Source File identifies each row.",
        "paths": ('*/com.duckduckgo.mobile.android/app_webview/Default/cookies',
                  '*/com.duckduckgo.mobile.android/app_webview/Default/Cookies'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.duckduckgo.mobile.android vc 52831000 | 116 rows",
            "pixel7a_a14": "Android 14 | com.duckduckgo.mobile.android vc 52072000 | 73 rows",
        }
    },
}

import json
import datetime
import pathlib
from pathlib import Path
from scripts.ilapfuncs import (
    artifact_processor, check_in_media, does_column_exist_in_db, get_sqlite_db_records, get_file_path, logfunc)
from scripts.ccl import ccl_leveldb


@artifact_processor
def duckduckgo_bookmarks(context):
    files_found = context.get_files_found()
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break

    query = '''
        -- CTE to rebuild bookmark folder path
        WITH RECURSIVE folder_paths AS (
            SELECT
                entities.entityId AS folderId,
                entities.title AS path
            FROM entities
            WHERE entities.type = 'FOLDER'
              AND entities.entityId NOT IN (SELECT entityId FROM relations)

            UNION ALL

            SELECT
                child.entityId AS folderId,
                folder_paths.path || ' > ' || child.title AS path
            FROM entities AS child
            JOIN relations ON child.entityId = relations.entityId
            JOIN folder_paths ON relations.folderId = folder_paths.folderId
            WHERE child.type = 'FOLDER'
        ),

        -- CTE to store bookmark and folder information
        bookmark_locations AS (
            SELECT
                entities.rowid,
                entities.entityId,
                entities.type,
                entities.title,
                entities.url,
                entities.lastModified,
                entities.deleted,
                relations.folderId
            FROM entities
            LEFT JOIN relations ON entities.entityId = relations.entityId
        )
        -- Main Query
        SELECT
            bookmark_locations.entityId AS "Entity ID",
            CASE bookmark_locations.deleted
                WHEN 1 THEN 'YES'
                ELSE 'NO'
            END AS Deleted,
            folder_paths.path AS "Folder Path",
            bookmark_locations.title AS "Title",
            bookmark_locations.url,
            SUBSTR(REPLACE(REPLACE(bookmark_locations.lastModified, 'T', ' '), 'Z', ''), 1, 19) AS "Last Modified"
        FROM bookmark_locations
        LEFT JOIN folder_paths ON bookmark_locations.folderId = folder_paths.folderId
        WHERE bookmark_locations.type LIKE 'BOOKMARK'
        GROUP BY bookmark_locations.entityId
        ORDER BY bookmark_locations.ROWID;
        '''

    data_headers = ('Entity ID', 'Deleted', 'Folder Path', 'Title', 'URL', ('Last Modified', 'datetime'))
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def duckduckgo_favorites(context):
    files_found = context.get_files_found()
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break

    query = '''
    -- CTE to identify folder name using the folderId

    WITH folder_titles AS (
        SELECT
            entities.entityId AS folderId,
            entities.title AS folderTitle
        FROM entities
        WHERE entities.type = 'FOLDER'
    ),
    -- CTE to identify bookmark favorites
    bookmark_favorites AS (
        SELECT
            relations.entityId
        FROM relations
        WHERE relations.folderId = 'favorites_root'
    )
    -- Main Query
    SELECT
        entities.entityId,
        entities.title,
        entities.url
    FROM entities
    LEFT JOIN relations ON entities.entityId = relations.entityId
    LEFT JOIN folder_titles ON relations.folderId = folder_titles.folderId
    LEFT JOIN bookmark_favorites ON entities.entityId = bookmark_favorites.entityId
    WHERE entities.type LIKE 'BOOKMARK' AND bookmark_favorites.entityId IS NOT NULL
    GROUP BY entities.entityId
    '''

    data_headers = ('Entity ID', 'Title', 'URL')
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def duckduckgo_history(context):
    files_found = context.get_files_found()
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break

    query = '''
        SELECT
            visits_list.rowid,
            history_entries.url,
            history_entries.title,
            visits_list.timestamp AS 'Visit Date',
            CASE history_entries.isSerp
                WHEN 1 THEN 'DuckDuckGo Search'
                WHEN 0 THEN 'Web Page Visit'
            END AS 'History Type',
            history_entries.query
        FROM visits_list
        LEFT JOIN history_entries ON visits_list.historyEntryId = history_entries.id;
        '''

    data_headers = ('Visit ID', 'URL', 'Title', 'Visit Date', 'History Type', 'Search Query')
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def duckduckgo_opentabs(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'app.db')
    thumb_lookup = {}
    for file_found in files_found:
        p = Path(file_found)
        if p.is_file() and p.suffix.lower() in ('.jpg'):
            thumb_lookup[p.name] = file_found

    if does_column_exist_in_db(source_path, 'tabs', 'lastAccessTime'):
        query = '''
            SELECT
                tabs.tabid,
                CASE
                    WHEN tab_selection.tabid IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS 'Current Tab',
                tabs.title,
                tabs.url,
                tabs.tabPreviewFile,
                DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch')
                 AS 'Cached Tab Preview Time (UTC)',
                tabs.lastAccessTime AS 'Tab Last Accessed'
            FROM tabs
            LEFT JOIN tab_selection ON tabs.tabid = tab_selection.tabid;
        '''
    else:
        query = '''
            SELECT
                tabs.tabid,
                CASE
                    WHEN tab_selection.tabid IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS 'Current Tab',
                tabs.title,
                tabs.url,
                tabs.tabPreviewFile,
                DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch')
                 AS 'Cached Tab Preview Time (UTC)',
                'Unavailable' AS 'Tab Last Accessed'
            FROM tabs
            LEFT JOIN tab_selection ON tabs.tabid = tab_selection.tabid;
        '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        tab_id = row[0]  # Tab ID
        current_tab = row[1]  # Current Tab
        title = row[2]  # Title
        url = row[3]  # URL
        cached_filename = row[4]  # Cached Tab Filename
        cached_time = row[5]  # Cached Tab Preview Time (UTC)
        last_accessed = row[6]  # Tab Last Accessed

        tab_thumbnail_media = None

        if cached_filename:
            thumb_path = thumb_lookup.get(cached_filename)
            if thumb_path:
                tab_thumbnail_media = check_in_media(
                    thumb_path,
                    cached_filename
                )

        data_list.append(
            (tab_id, current_tab, title, url, last_accessed, cached_filename, cached_time, tab_thumbnail_media))

    data_headers = (
        'Tab ID',
        'Current Tab',
        'Title',
        'URL',
        'Tab Last Accessed',
        'Cached Tab Filename',
        ('Cached Tab Preview Time (UTC)', 'datetime'),
        ('Cached Tab Preview', 'media')
    )

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def duckduckgo_fireproof(context):
    files_found = context.get_files_found()
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break

    query = '''
        SELECT
            fireproofWebsites.domain
        FROM fireProofWebsites;
    '''

    data_headers = ('Fireproof Site',)
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def duckduckgo_downloads(context):
    files_found = context.get_files_found()
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except OSError:
            return False

    source_path = None
    for f in files_found:
        p = Path(f)
        if p.name.endswith("-wal") or p.name.endswith("-shm"):
            continue
        if is_sqlite_db(f):
            source_path = str(f)
            break

    if not source_path:
        return (), [], ''

    query = '''
        SELECT
            downloads.downloadId AS "Download ID",
            CASE downloads.downloadStatus
                WHEN 0 THEN 'Download Started'
                WHEN 1 THEN 'Download Completed'
                ELSE 'Unknown (' || downloads.downloadStatus || ')'
            END AS "Download Status",
            downloads.fileName AS "File Name",
            downloads.contentLength,
            downloads.filePath AS "Download Path",
            downloads.createdAt AS "Download Date"
        FROM downloads;
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        download_id = row[0]
        download_status = row[1]
        file_name = row[2]
        size_bytes = row[3]
        download_path = row[4]
        download_date = row[5]

        data_list.append((download_id, download_status, file_name, size_bytes, download_path, download_date))

    data_headers = ('Download ID', 'Download Status', 'File Name', 'Size (Bytes)', 'Download Path',
                    'Download Date')

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def duckduckgo_thumbnails(context):
    files_found = context.get_files_found()
    data_list = []

    source_paths = set()

    source_path = next((str(p) for p in files_found if Path(p).name == 'app.db'), '')
    open_preview_files = set()
    if source_path:
        source_paths.add(source_path)
        query = '''
            SELECT
                tabs.tabPreviewFile
            FROM tabs;
        '''
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            if row[0]:
                open_preview_files.add(Path(str(row[0])).name)

    for file_found in files_found:
        media_path = Path(file_found)
        if media_path.suffix.lower() not in ('.jpg'):
            continue
        source_paths.add(str(file_found))
        filename = (media_path.name)
        timestamp = None
        try:
            utctime = int(media_path.stem)
            timestamp = datetime.datetime.fromtimestamp(
                utctime/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, OverflowError, OSError):
            logfunc(f'DuckDuckGo thumbnail: timestamp unavailable for '
                    f'{context.get_relative_path(str(file_found))}')
        media_item = check_in_media(file_found, filename)

        if media_item:
            referenced_in_tabs = 'Yes' if filename in open_preview_files else 'No'

            data_list.append(
                (timestamp, referenced_in_tabs, media_item, filename,
                 context.get_relative_path(str(file_found))))

    data_headers = (
        ('Timestamp (UTC)', 'datetime'), 'Referenced In Tabs Table', ('Thumbnail', 'media'),
        'File Name', 'Location')

    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def duckduckgo_duckai(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = set()

    duckchats = "_https://duckduckgo.com savedAIChats"

    def clean_iso_timestamp(ts):
        if not ts:
            return ts

        ts = ts.rstrip("Z")

        try:
            dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def clean_key_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            s = value.decode('utf-8', errors='replace')
        else:
            s = str(value)

        if s and ord(s[0]) < 32:
            s = s[1:]

        cleaned = []
        for ch in s:
            if ch.isprintable():
                cleaned.append(ch)
            elif ch in '\t\n\r':
                cleaned.append(ch)
            else:
                cleaned.append(' ')

        s = ''.join(cleaned)

        s = ' '.join(s.split())

        return s

    def decode_json_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            b = bytes(value)
        else:
            b = str(value).encode('utf-8', errors='ignore')

        if b and b[0] < 32:
            b = b[1:]

        return b.decode('utf-8', errors='ignore')

    for source_path in files_found:
        source_path = set(pathlib.Path(x).parent for x in files_found)

    for in_db_dir in source_path:
        try:
            leveldb_records = ccl_leveldb.RawLevelDb(in_db_dir)
        except Exception:  # pylint: disable=broad-exception-caught
            continue

        for record in leveldb_records.iterate_records_raw():
            record_sequence = record.seq
            record_key_raw = record.user_key
            record_value_raw = record.value
            origin = str(record.origin_file)

            record_key = clean_key_bytes(record_key_raw)
            if record_key != duckchats:
                continue

            json_text = decode_json_bytes(record_value_raw)
            try:
                parsed = json.loads(json_text)
            except ValueError:
                continue

            source_paths.add(origin)
            chats = parsed.get("chats", [])
            parent_folder = pathlib.Path(origin).parent.name
            origin_filename = pathlib.Path(origin).name
            origin_path_short = f"{parent_folder}/{origin_filename}"

            for chat in chats:
                chat_id = chat.get("chatId")
                title = chat.get("title")
                model = chat.get("model")
                messages = chat.get("messages", [])

                for m in messages:
                    role = m.get("role")
                    created_at_raw = m.get("createdAt")
                    created_at = clean_iso_timestamp(created_at_raw)
                    content = m.get("content", "") or ""
                    if not content and isinstance(m.get("parts"), list):
                        text_parts = [
                            p.get("text", "")
                            for p in m["parts"]
                            if isinstance(p, dict) and p.get("type") == "text"
                        ]
                        content = " ".join(tp for tp in text_parts if tp)

                    data_list.append((
                        chat_id,            # Chat ID
                        title,              # Title
                        model,              # LLM Model
                        role,               # Message Role
                        created_at,         # Message Time
                        content,            # Message Content
                        origin_path_short,  # Origin File
                        record_sequence     # Sequence Number
                    ))

    data_headers = (
        "Chat ID",
        "Title",
        "Model",
        "Message Role",
        ("Message Time", "datetime"),
        "Message Content",
        "Origin File",
        "Sequence Number"
    )

    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def duckduckgo_cookies(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []

    query = '''
        SELECT
            CASE cookies.last_access_utc
                WHEN "0" THEN ""
                ELSE datetime(cookies.last_access_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "last_access_utc",
            cookies.host_key,
            cookies.name,
            cookies.value,
            CASE cookies.creation_utc
                WHEN "0" THEN ""
                ELSE datetime(cookies.creation_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "creation_utc",
            CASE cookies.expires_utc
                WHEN "0" THEN ""
                ELSE datetime(cookies.expires_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "expires_utc",
            cookies.path
        FROM cookies
        '''

    for file_found in dict.fromkeys(str(p) for p in files_found):
        if Path(file_found).name not in ('Cookies', 'cookies'):
            continue
        source_paths.append(file_found)
        db_records = get_sqlite_db_records(file_found, query)
        for row in db_records:
            data_list.append((row[0], row[4], row[5], row[1], row[2], row[3], row[6],
                              context.get_relative_path(file_found)))

    data_headers = (('Last Accessed', 'datetime'), ('Creation Time', 'datetime'),
                    ('Expiry', 'datetime'), 'Host', 'Name', 'Value', 'Path', 'Source File')

    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in source_paths)
