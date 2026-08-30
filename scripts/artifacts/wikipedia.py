__artifacts_v2__ = {
    "wikipedia_reading_history": {
        "name": "Wikipedia - Reading History",
        "description": "Parses the article reading history recorded by the Wikipedia Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Wikipedia",
        "notes": "One row per article visit in the HistoryEntry table of databases/wikipedia.db, "
                 "joined to the PageImage table for the same article. Each row records that the client "
                 "opened an article, with the Timestamp it was last opened, the article title, the "
                 "language edition and the site it was read from. The stored display title carries HTML "
                 "markup, which is stripped here to leave the plain title; the Article column keeps the "
                 "underlying page title as stored. Timestamp is Unix milliseconds and was UTC on the "
                 "tested device (15:58 UTC matched the device's 11:58 local clock), so it is reported "
                 "as UTC. Source is how the article was reached, decoded from the app's own "
                 "constants, for example 1 a search, 2 an internal link, 3 an external link, 8 the main "
                 "page, 9 the places map "
                 "(app/src/main/java/org/wikipedia/history/HistoryEntry.kt at "
                 "wikimedia/apps-android-wikipedia 07777215); any other value is reported as stored. "
                 "Time Spent, the article Description and the article's Latitude and Longitude come "
                 "from PageImage where the app recorded them, and the coordinates are 0 for an article "
                 "with no location. Namespace is the article's namespace and is empty for a main article, which is the usual case, and carries a value only for a Talk, User or other namespace page. The database runs in WAL mode and on the tested device held every "
                 "row in the -wal sidecar with an empty main file, so the sidecar is in the paths and "
                 "is required. The client has no account, so this is a local record of reading on this "
                 "device.",
        "paths": ('*/org.wikipedia*/databases/wikipedia.db*',),
        "output_types": "standard",
        "artifact_icon": "book"
    },
    "wikipedia_search_history": {
        "name": "Wikipedia - Search History",
        "description": "Parses the recent search queries recorded by the Wikipedia Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Wikipedia",
        "notes": "One row per query in the RecentSearch table of databases/wikipedia.db. Each row is a "
                 "term entered into the app's search, with the Timestamp of the last time it was "
                 "run, stored as "
                 "Unix milliseconds and reported as UTC. The table keys on the search text, so a repeat "
                 "of the same term updates the one row rather than adding another. The data lives in "
                 "the wikipedia.db WAL sidecar on the tested device, which is why it is in the paths.",
        "paths": ('*/org.wikipedia*/databases/wikipedia.db*',),
        "output_types": "standard",
        "artifact_icon": "search"
    }
}

import re

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import get_sqlite_db_records

# app/src/main/java/org/wikipedia/history/HistoryEntry.kt at wikimedia/apps-android-wikipedia 07777215.
HISTORY_SOURCES = {
    1: 'Search', 2: 'Internal link', 3: 'External link', 4: 'History',
    6: 'Language link', 7: 'Random', 8: 'Main page', 9: 'Places', 10: 'Disambiguation',
    11: 'Reading list', 13: 'Feed - because you read', 14: 'Feed - most read',
    15: 'Feed - featured', 16: 'News', 17: 'Feed - main page', 18: 'Feed - random',
    19: 'Gallery', 20: 'Shortcut - random', 21: 'Shortcut - continue reading',
    22: 'Feed - most read activity', 23: 'On this day card', 24: 'On this day activity',
    25: 'Notification',
}

DB_SUFFIX = 'databases/wikipedia.db'
_TAG = re.compile(r'<[^>]+>')


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _strip(markup):
    if not markup:
        return ''
    return _TAG.sub('', markup).strip()


def _source(value):
    if value in HISTORY_SOURCES:
        return HISTORY_SOURCES[value]
    return f'{value} (as stored)'


@artifact_processor
def wikipedia_reading_history(context):
    query = '''SELECT h.timestamp, h.displayTitle, h.apiTitle, h.lang, h.authority,
                      h.source, h.namespace, p.timeSpentSec, p.description,
                      p.geoLat, p.geoLon, p.imageName
               FROM HistoryEntry h
               LEFT JOIN PageImage p
                 ON p.lang = h.lang AND p.namespace = h.namespace AND p.apiTitle = h.apiTitle
               ORDER BY h.timestamp DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((
                _ms(r[0]), _strip(r[1]), r[2] or '', r[3] or '', r[4] or '',
                _source(r[5]), r[6] or '', r[7], r[8] or '', r[9], r[10], r[11] or '',
                context.get_relative_path(db_path),
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Timestamp', 'datetime'), 'Title', 'Article', 'Language', 'Site', 'Source',
        'Namespace', 'Time Spent (seconds)', 'Description', 'Latitude', 'Longitude',
        'Thumbnail URL', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def wikipedia_search_history(context):
    query = 'SELECT timestamp, text FROM RecentSearch ORDER BY timestamp DESC'
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', context.get_relative_path(db_path)))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (('Timestamp', 'datetime'), 'Search', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
