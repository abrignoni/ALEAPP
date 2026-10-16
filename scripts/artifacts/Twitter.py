__artifacts_v2__ = {
    "get_Twitter": {
        "name": "twitter",
        "description": "Rows of the search_queries table of each distinct main database whose name ends in "
                       "-search.db found for the Twitter app. Whether a row is a search entered "
                       "on the device or a suggestion the app stored is not established.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2023-04-26",
        "last_update_date": "2026-10-06",
        "requirements": "None",
        "category": "Twitter",
        "notes": "Canonical aliases collapse only when main, WAL and journal bytes agree; "
                 "conflicting states and independent users remain separate. Per-row Source File "
                 "is included only when rows combine distinct database sources. Unsupported "
                 "sources are logged and skipped without changing the fixed query.",
        "paths": ('*/com.twitter.android/databases/*-search.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.twitter.android vc 310480000 | 2 rows",
            "samsungs20_a13": "Android 13 | com.twitter.android vc 311550000 | 2 rows",
            "sharon_a14": "Android 14 | com.twitter.android vc 310542000 | 0 rows",
        },
    }
}

import datetime
import hashlib
import sqlite3
from pathlib import Path
from scripts.artifacts.storagePathViews import canonical_path

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc


def _twitter_sources(context):
    """Keep independent database states, collapsing proven canonical aliases only."""
    paths = []
    seen = set()
    for candidate in context.get_files_found():
        path = str(candidate)
        if not Path(path).name.endswith('-search.db'):
            continue
        relative = context.get_relative_path(path)
        try:
            with open(path, 'rb') as handle:
                if handle.read(16) != b'SQLite format 3\x00':
                    logfunc(f'Twitter: unsupported SQLite header in {relative}; skipping source')
                    continue
            state = []
            for suffix in ('', '-wal', '-journal'):
                try:
                    with open(path + suffix, 'rb') as handle:
                        digest = hashlib.sha256()
                        for chunk in iter(lambda handle=handle: handle.read(1024 * 1024), b''):
                            digest.update(chunk)
                    state.append(digest.hexdigest())
                except FileNotFoundError:
                    if not suffix:
                        raise
                    state.append(None)
            identity = (canonical_path(relative)[0], tuple(state))
        except OSError as error:
            logfunc(f'Twitter: unreadable database {relative}: {error}')
            continue
        if identity not in seen:
            seen.add(identity)
            paths.append(path)
    return paths


@artifact_processor
def get_Twitter(context):
    data_list = []
    sources = set()
    for source_path in _twitter_sources(context):
        relative = context.get_relative_path(source_path)
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            logfunc(f'Twitter: unavailable database {relative}; skipping source')
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
            select time, name, query, query_id, user_search_suggestion, topic_search_suggestion,
            latitude, longitude, radius, location, priority, score
            from search_queries
        ''')
            all_rows = cursor.fetchall()
        except sqlite3.Error as error:
            logfunc(f'Twitter: unsupported search schema in {relative}: {error}; skipping source')
            continue
        finally:
            db.close()
        for r in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(r[0]) / 1000, datetime.timezone.utc) if r[0] else ''
            data_list.append((timestamp, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], relative))
            sources.add(source_path)

    data_headers = (('Timestamp', 'datetime'), 'Name', 'Query', 'Query ID', 'User Search Suggestion', 'Topic Search Suggestion', 'Latitude', 'Longitude', 'Radius', 'Location', 'Priority', 'Score')
    if len(sources) > 1:
        data_headers += ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return data_headers, data_list, '\n'.join(sorted(sources))
