# pylint: disable=W0718
__artifacts_v2__ = {
    "ornetbrowser_bookmarks": {
        "name": "Ornet Browser - Bookmarks",
        "description": "Parses Ornet Browser Bookmarks",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": "Tested on version 1.9.26 (Oct, 22nd 2025)",
        "paths": ('*/com.ornet.torbrowser/databases/appDatabase'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bookmark"
    },
    "ornetbrowser_suggestions": {
        "name": "Ornet Browser - Suggestions",
        "description": "Parses the Ornet Browser suggestions table",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": (
            "Tested on version 1.9.26 (Oct, 22nd 2025). Rows are read from the suggestions "
            "table of appDatabase. What the app stores in that table is not established, so "
            "the entries are reported as stored."
        ),
        "paths": ('*/com.ornet.torbrowser/databases/appDatabase'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "star"
    },
    "ornetbrowser_history": {
        "name": "Ornet Browser - Web Browser History",
        "description": "Parses Ornetbrowser Web Browsing History",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": (
            "Tested on version 1.9.26 (Oct, 22nd 2025). Visit Date joins the stored "
            "history.date and history.time strings and reproduces them as recorded; the "
            "file carries no time zone for them."
        ),
        "paths": ('*/com.ornet.torbrowser/databases/appDatabase'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    "ornetbrowser_opentabs": {
        "name": "Ornet Browser - Open Tabs",
        "description": "Parses Ornet Browser Open Tab Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": (
            "Tested on version 1.9.26 (Oct, 22nd 2025). Tab Preview File Name Time is "
            "decoded from the tab preview file name, which is a number read as a Unix time "
            "in milliseconds; that reading was established through testing and the file name "
            "is its only basis. It is rendered in UTC."
        ),
        "paths": (
            '*/com.ornet.torbrowser/databases/appDatabase',
            '*/com.ornet.torbrowser/cache/tabPreviews/*/*.jpg'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "book"
    },
    "ornetbrowser_frequents": {
        "name": "Ornet Browser - Frequents",
        "description": "Parses the Ornet Browser frequents table",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": (
            "Tested on version 1.9.26 (Oct, 22nd 2025). Rows are read from the frequents "
            "table of appDatabase. Count is the stored count value; what increments it is "
            "not established, so it is reported as stored."
        ),
        "paths": ('*/com.ornet.torbrowser/databases/appDatabase'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    "ornetbrowser_downloads": {
        "name": "Ornet Browser - Downloads",
        "description": "Parses Ornet Browser Downloads",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": (
            "Tested on version 1.9.26 (Oct, 22nd 2025). Last Modified is the stored "
            "downloads.last_modified_at value rendered in UTC; the column name is the "
            "field's own name and what the app updates it for is not established."
        ),
        "paths": ('*/com.ornet.torbrowser/databases/kdownloader.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download"
    },
    "ornetbrowser_thumbnails": {
        "name": "Ornet Browser - Tab Thumbnails",
        "description": "Parses Ornet Browser Tab thumbnail Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": (
            "Tested on version 1.9.26 (Oct, 22nd 2025). Timestamp is decoded from the "
            "thumbnail file name, which is a number read as a Unix time in milliseconds; "
            "that reading was established through testing and the file name is its only "
            "basis. It is rendered in UTC."
        ),
        "paths": (
            '*/com.ornet.torbrowser/cache/tabPreviews/*/*.jpg',
            '*/com.ornet.torbrowser/databases/appDatabase'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "photo"
    },
    "ornetbrowser_searchhistory": {
        "name": "Ornet Browser - Search History",
        "description": "Parses Ornet Browser Search History",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": "Tested on version 1.9.26 (Oct, 22nd 2025)",
        "paths": ('*/com.ornet.torbrowser/databases/appDatabase'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "ornetbrowser_cookies": {
        "name": "Ornet Browser - Cookies",
        "description": "Parses Ornet Browser Cookies",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": "Tested on version 1.9.26 (Oct, 22nd 2025)",
        "paths": ('*/com.ornet.torbrowser/files/mozilla/*/cookies.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    "ornetbrowser_usageinfo": {
        "name": "Ornet Browser - Usage Info",
        "description": "Parses Ornet Browser Usage Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Ornet Browser",
        "notes": "Tested on version 1.9.26 (Oct, 22nd 2025)",
        "paths": ('*/com.ornet.torbrowser/shared_prefs/com.ornet.torbrowser_preferences.xml'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "info-circle"
    }
}

import datetime
import os
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from scripts.ilapfuncs import artifact_processor, check_in_media, get_sqlite_db_records, logfunc

INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def ornetbrowser_bookmarks(context):
    files_found = context.get_files_found()
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
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
        return (), [], "appDatabase not found"

    query = '''
        SELECT
            bookmarks.id,
            bookmarks.title,
            bookmarks.url,
            folders.name
        FROM bookmarks
        LEFT JOIN folders ON bookmarks.folderId = folders.id;
        '''

    data_headers = ('Bookmark ID', 'Title', 'URL', 'Bookmark Folder')
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_suggestions(context):
    files_found = context.get_files_found()
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
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
        return (), [], "appDatabase not found"

    query = '''
        SELECT
            suggestions.id,
            suggestions.url,
            suggestions.title
        FROM suggestions;
    '''

    data_headers = ('ID', 'URL', 'Title')
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_history(context):
    files_found = context.get_files_found()
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
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
        return (), [], "appDatabase not found"

    query = '''
        SELECT
            history.id,
            history.url,
            history.title,
            CONCAT(history.date, ' ', history.time) AS 'Visit Date'
        FROM history;
        '''

    data_headers = ('ID', 'URL', 'Title', ('Visit Date', 'datetime'))
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_opentabs(context):
    files_found = context.get_files_found()

    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
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
        return (), [], "appDatabase not found"

    thumb_lookup = {}
    for file_found in files_found:
        p = Path(file_found)
        if p.is_file() and p.suffix.lower() == '.jpg':
            thumb_lookup[p.name] = file_found

    query = '''
        SELECT
            tabs.tabid,
            tabs.url,
            tabs.title,
            tabs.tabPreviewFile,
            DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch')
                AS "Tab Preview File Name Time (UTC)"
        FROM tabs;
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        tab_id = row[0]  # Tab ID
        url = row[1]  # URL
        title = row[2]  # Title
        cached_filename = row[3]  # Cached Tab Filename
        cached_time = row[4]  # Tab Preview File Name Time (UTC)

        tab_thumbnail_media = None

        if cached_filename:
            thumb_path = thumb_lookup.get(cached_filename)
            if thumb_path:
                tab_thumbnail_media = check_in_media(
                    thumb_path,
                    cached_filename
                )

        data_list.append((
            tab_id,
            url,
            title,
            cached_filename,
            cached_time,
            tab_thumbnail_media
        ))

    data_headers = (
        'Tab ID',
        'URL',
        'Title',
        'Cached Tab Filename',
        ('Tab Preview File Name Time (UTC)', 'datetime'),
        ('Cached Tab Preview', 'media')
    )

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_frequents(context):
    files_found = context.get_files_found()
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
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
        return (), [], "appDatabase not found"

    query = '''
        SELECT
            frequents.url,
            frequents.title,
            frequents.count
        FROM frequents
    '''

    data_headers = ('URL', 'Title', 'Count')
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_downloads(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break

    query = '''
        SELECT
            downloads.id AS "Download ID",
            downloads.status,
            downloads.file_name,
            downloads.url,
            downloads.downloaded_bytes,
            downloads.total_bytes,
            downloads.dir_path AS "Download Path",
            DATETIME(downloads.last_modified_at/1000, 'unixepoch') AS "Last Modified (UTC)"
        FROM downloads
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        download_id = row[0]
        download_status = row[1]
        file_name = row[2]
        download_url = row[3]
        downloaded_bytes = row[4]
        total_bytes = row[5]
        download_path = row[6]
        last_modified = row[7]

        data_list.append(
            (download_id, download_status, file_name, download_url, downloaded_bytes,
             total_bytes, last_modified, download_path))

    data_headers = ('Download ID', 'Download Status', 'File Name', 'Download URL', 'Downloaded Bytes',
                    'Total Bytes', ('Last Modified (UTC)', 'datetime'), 'Download Path',)

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_thumbnails(context):
    files_found = context.get_files_found()
    data_list = []

    for file_found in files_found:
        media_path = Path(file_found)
        if media_path.suffix.lower() not in ('.jpg'):
            continue
        filename = (media_path.name)
        utctime = int(media_path.stem)

        timestamp = (datetime.datetime.fromtimestamp(utctime/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
        media_item = check_in_media(file_found, filename)

        if media_item:
            data_list.append((timestamp, media_item, filename, context.get_relative_path(str(file_found))))

    data_headers = (('Timestamp', 'datetime'), ('Thumbnail', 'media'), ' File Name', 'Location')

    return data_headers, data_list, 'See source path(s) below'


@artifact_processor
def ornetbrowser_searchhistory(context):
    files_found = context.get_files_found()
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
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
        return (), [], "appDatabase not found"

    query = '''
        SELECT
            searchHistory.id,
            searchHistory.title AS 'User Search'
        FROM searchHistory;
    '''

    data_headers = ('id', 'Search Query')
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_cookies(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.sqlite'):
            break

    query = '''
        SELECT
            DATETIME(moz_cookies.lastAccessed/1000000,'unixepoch'),
            DATETIME(moz_cookies.creationTime/1000000,'unixepoch'),
            moz_cookies.host,
            moz_cookies.name,
            moz_cookies.value,
            DATETIME(moz_cookies.expiry,'unixepoch'),
            moz_cookies.path
        from moz_cookies
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        lastaccessed = row[0]
        creationtime = row[1]
        host = row[2]
        name = row[3]
        value = row[4]
        expiry = row[5]
        path = row[6]

        data_list.append((lastaccessed, creationtime, host, name, value, expiry, path))

    data_headers = (
        ('Last Accessed', 'datetime'), ('Creation Time', 'datetime'), 'Host', 'Name', 'Value',
        ('Expiry', 'datetime'), 'Path')

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def ornetbrowser_usageinfo(context):
    files_found = context.get_files_found()

    usage_keys = {
        "currentTab",
        "privateCurrentTab",
        "last_app_close_time",
        "selectedSearchEngine"
    }

    data_list = []
    source_path = ""

    for fp in files_found:
        source_path = str(fp)
        if not source_path.lower().endswith(".xml"):
            continue
        if not os.path.isfile(source_path):
            continue

        root = _parse_xml(source_path)

        filename = Path(source_path).name
        path = source_path

        for elem in root.iter():
            key_name = elem.get("name")
            if key_name not in usage_keys:
                continue

            value_raw = elem.text.strip() if elem.text else elem.get("value", "").strip()

            value_out = value_raw
            if key_name == "last_app_close_time":
                try:
                    ts = int(value_raw)
                    dt = datetime.datetime.fromtimestamp(ts / 1000.0, datetime.timezone.utc)
                    value_out = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass

            data_list.append((key_name, value_out, filename, context.get_relative_path(path)))

    data_headers = ("Key", "Value", "File Name", "Path")

    return data_headers, data_list, context.get_relative_path(source_path)
