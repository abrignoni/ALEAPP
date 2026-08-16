__artifacts_v2__ = {
    "get_firefoxCookies": {
        "name": "Firefox - Cookies",
        "description": "Parses Firefox cookies (host, name, value, path, created, last accessed and expiration timestamps) from cookies.sqlite.",
        "author": "@stark4n6",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Firefox",
        "notes": "Mozilla converted moz_cookies.expiry from seconds to milliseconds in cookies schema 16, shipped with Firefox 142, so the expiry is divided by 1000 when the database reports schema version 16 or later in PRAGMA user_version. When that version cannot be read, the expiry falls back to a magnitude test: a value above 100000000000 is read as milliseconds, because an expiry expressed in seconds is around 1e9 to 2e9 while the same date in milliseconds is around 1e12 to 2e12. The lastAccessed and creationTime columns are microseconds in every schema and are decoded as such. Reference: Mozilla, 'CookiePersistentStorage.cpp schema 15->16 migration (expiry converted to milliseconds)', https://github.com/mozilla-firefox/firefox/blob/6d751cf5d0af4b7fcc1b232b6c2ba0551afabe1d/netwerk/cookie/CookiePersistentStorage.cpp",
        "paths": ('*/org.mozilla.firefox/files/mozilla/*.default/cookies.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 95 rows",
        },
    }
}

import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc
from scripts.artifacts.storagePathViews import unique_files

# Cookies schema 16 (Firefox 142) rewrote expiry from seconds to milliseconds
EXPIRY_IN_MS_SCHEMA = 16
# Above this, a value cannot be an expiry in seconds, so it is one in milliseconds
EXPIRY_IN_MS_THRESHOLD = 100000000000


def _cookies_schema_version(cursor):
    '''Cookies schema version from PRAGMA user_version, or None when unreadable.'''
    try:
        row = cursor.execute('PRAGMA user_version').fetchone()
        return int(row[0]) if row and row[0] else None
    except (sqlite3.Error, TypeError, ValueError):
        return None


def _expiry_in_seconds(schema_version):
    '''SQL expression turning the expiry column into seconds for this schema.'''
    if schema_version is None:
        # Version unavailable, so fall back to the magnitude of each stored value
        return f'CASE WHEN expiry > {EXPIRY_IN_MS_THRESHOLD} THEN expiry/1000 ELSE expiry END'
    if schema_version >= EXPIRY_IN_MS_SCHEMA:
        return 'expiry/1000'
    return 'expiry'


@artifact_processor
def get_firefoxCookies(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'cookies.sqlite':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        expiry_seconds = _expiry_in_seconds(_cookies_schema_version(cursor))
        cursor.execute(f'''
        SELECT
        datetime(lastAccessed/1000000,'unixepoch') AS LastAccessedDate,
        datetime(creationTime/1000000,'unixepoch') AS CreationDate,
        host AS Host,
        name AS Name,
        value AS Value,
        datetime({expiry_seconds},'unixepoch') AS ExpirationDate,
        path AS Path
        from moz_cookies
        ORDER BY lastAccessedDate ASC
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),convert_human_ts_to_utc(row[1]),row[2],row[3],row[4],convert_human_ts_to_utc(row[5]),row[6]))

        db.close()

    data_headers = (
        ('Last Accessed Timestamp', 'datetime'),
        ('Created Timestamp', 'datetime'),
        'Host',
        'Name',
        'Value',
        ('Expiration Timestamp', 'datetime'),
        'Path',
    )
    return data_headers, data_list, source_path
