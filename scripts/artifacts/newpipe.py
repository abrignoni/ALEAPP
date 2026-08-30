__artifacts_v2__ = {
    "newpipe_watch_history": {
        "name": "NewPipe - Watch History",
        "description": "Parses the video watch history recorded by the NewPipe Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "NewPipe",
        "notes": "One row per stream_history entry in databases/newpipe.db, joined to the streams "
                 "table it references. Each row records that the client opened a stream, with the "
                 "Access Date it was last opened, a Repeat Count of how many times, and the stream's "
                 "title, uploader, url, duration and type as the client cached them. The database is "
                 "a Room database that runs in WAL mode, and on the tested device the main file held "
                 "no tables while the write ahead log held every row, so the -wal sidecar is included "
                 "in the paths and is required; reading the main file alone returns nothing. Access "
                 "Date is stored as Unix milliseconds and was UTC on the tested device (14:26 UTC "
                 "matched the device's 10:26 local clock at UTC-4), so it is converted as UTC. "
                 "Service is decoded from the service id using NewPipe Extractor's ServiceList "
                 "(extractor/src/main/java/org/schabi/newpipe/extractor/ServiceList.java at "
                 "TeamNewPipe/NewPipeExtractor f9e6bb80): 0 YouTube, 1 SoundCloud, 2 media.ccc.de, "
                 "3 PeerTube, 4 Bandcamp; any other id is reported as stored. Opening a stream is not "
                 "the same as watching it to the end; the Playback Positions artifact records how far "
                 "into a stream the client reached. NewPipe records history only while the "
                 "enable_watch_history preference is set, which it is by default.",
        "paths": ('*/org.schabi.newpipe/databases/newpipe.db*',),
        "output_types": "standard",
        "artifact_icon": "history"
    },
    "newpipe_search_history": {
        "name": "NewPipe - Search History",
        "description": "Parses the search queries recorded by the NewPipe Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "NewPipe",
        "notes": "One row per search_history entry in databases/newpipe.db. Each row is a query the "
                 "user submitted, with its Creation Date and the service it was run against. Creation "
                 "Date is Unix milliseconds and was UTC on the tested device, so it is converted as "
                 "UTC. Service is decoded from the service id per NewPipe Extractor's ServiceList (see "
                 "the Watch History notes for the mapping and pinned source). NewPipe writes a row "
                 "when a search is submitted and the enable_search_history preference is set, which it "
                 "is by default; suggestions shown while typing are not stored. The data lives in the "
                 "newpipe.db WAL sidecar on the tested device, which is why it is in the paths.",
        "paths": ('*/org.schabi.newpipe/databases/newpipe.db*',),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "newpipe_subscriptions": {
        "name": "NewPipe - Subscriptions",
        "description": "Parses the channel subscriptions held by the NewPipe Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "NewPipe",
        "notes": "One row per subscriptions entry in databases/newpipe.db: the channel name, its url, "
                 "avatar url, the subscriber count and description as cached, and the notification "
                 "mode. NewPipe has no account, so a subscription is a local record that the user "
                 "chose to follow that channel on this device. Service is decoded from the service id "
                 "per NewPipe Extractor's ServiceList (see the Watch History notes). The table carries "
                 "no subscribe timestamp, so when the user subscribed cannot be established from it. "
                 "The row lives in the newpipe.db WAL sidecar on the tested device.",
        "paths": ('*/org.schabi.newpipe/databases/newpipe.db*',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "newpipe_playback_positions": {
        "name": "NewPipe - Playback Positions",
        "description": "Parses the saved playback resume positions kept by the NewPipe Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "NewPipe",
        "notes": "One row per stream_state entry in databases/newpipe.db, joined to its stream. "
                 "Progress Time is how far into the stream the client had reached, stored in "
                 "milliseconds, shown here alongside the stream's total duration in seconds so the two "
                 "can be compared. A row is stronger evidence of actual viewing than a watch history "
                 "entry, which only records that the stream was opened. The table carries no timestamp "
                 "of its own; the Access Date for the same stream is in the Watch History artifact. "
                 "The row lives in the newpipe.db WAL sidecar on the tested device.",
        "paths": ('*/org.schabi.newpipe/databases/newpipe.db*',),
        "output_types": "standard",
        "artifact_icon": "player-play"
    },
    "newpipe_playlists": {
        "name": "NewPipe - Playlists",
        "description": "Parses the local playlists created in the NewPipe Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "NewPipe",
        "notes": "One row per stream in each local playlist, from the playlists and "
                 "playlist_stream_join tables of databases/newpipe.db joined to streams, in the "
                 "playlist's stored order. Local playlists are lists the user built on this device. "
                 "This was empty on the tested device, so the join is code-present and exercised "
                 "against no rows here. Two related stores are not parsed by this artifact and are "
                 "named so an examiner knows where they are: remote_playlists holds playlists the user "
                 "bookmarked from a service rather than built locally, and feed_group holds the user's "
                 "own groupings of their subscriptions; both were also empty on the tested device. The "
                 "data lives in the newpipe.db WAL sidecar on the tested device.",
        "paths": ('*/org.schabi.newpipe/databases/newpipe.db*',),
        "output_types": "standard",
        "artifact_icon": "playlist"
    }
}

import os

from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, logfunc,
                              open_sqlite_db_readonly)
from scripts.artifacts.storagePathViews import unique_files

# NewPipe Extractor ServiceList.java at TeamNewPipe/NewPipeExtractor f9e6bb80.
SERVICES = {0: 'YouTube', 1: 'SoundCloud', 2: 'media.ccc.de', 3: 'PeerTube', 4: 'Bandcamp'}
DB_SUFFIX = 'databases/newpipe.db'


def _service(service_id):
    if service_id in SERVICES:
        return SERVICES[service_id]
    return f'{service_id} (as stored)'


def _utc_ms(value):
    """A Unix millisecond value as a UTC datetime, or '' when absent."""
    if value in (None, '', 0):
        return ''
    try:
        # NewPipe stores these columns in milliseconds; convert explicitly rather than
        # relying on magnitude inference.
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _db_files(files_found):
    """The newpipe.db paths from the matched set, sidecars excluded.

    The glob matches newpipe.db and its -wal and -shm sidecars; only the database itself is
    opened (open_sqlite_db_readonly applies the WAL), so a sidecar never becomes a reported
    source path.
    """
    out = []
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if file_found.endswith(DB_SUFFIX) and not os.path.isdir(file_found):
            out.append(file_found)
    return out


def _rows(context, query):
    """(rows, source_paths) for a query run against every newpipe.db container."""
    data = []
    sources = []
    for db_path in _db_files(unique_files(context)):
        connection = open_sqlite_db_readonly(db_path)
        if connection is None:
            continue
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            got = cursor.fetchall()
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'NewPipe: query failed on {db_path}: {error}')
            continue
        finally:
            pass
        if got:
            data.extend((row, db_path) for row in got)
            if db_path not in sources:
                sources.append(db_path)
        connection.close()
    return data, sources


@artifact_processor
def newpipe_watch_history(context):
    query = '''SELECT sh.access_date, s.title, s.uploader, s.url, s.uploader_url,
                      s.duration, sh.repeat_count, s.stream_type, s.service_id
               FROM stream_history sh
               JOIN streams s ON s.uid = sh.stream_id
               ORDER BY sh.access_date DESC'''
    rows, sources = _rows(context, query)
    data_list = []
    for r, db_path in rows:
        data_list.append((_utc_ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4] or '',
                          r[5], r[6], r[7] or '', _service(r[8]),
                          context.get_relative_path(db_path)))
    data_headers = (
        ('Access Date', 'datetime'), 'Title', 'Uploader', 'URL', 'Uploader URL',
        'Duration (seconds)', 'Repeat Count', 'Stream Type', 'Service', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def newpipe_search_history(context):
    query = '''SELECT creation_date, search, service_id FROM search_history
               ORDER BY creation_date DESC'''
    rows, sources = _rows(context, query)
    data_list = []
    for r, db_path in rows:
        data_list.append((_utc_ms(r[0]), r[1] or '', _service(r[2]),
                          context.get_relative_path(db_path)))
    data_headers = (('Creation Date', 'datetime'), 'Search', 'Service', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def newpipe_subscriptions(context):
    query = '''SELECT name, url, avatar_url, subscriber_count, description,
                      notification_mode, service_id FROM subscriptions
               ORDER BY name'''
    rows, sources = _rows(context, query)
    data_list = []
    for r, db_path in rows:
        data_list.append((r[0] or '', r[1] or '', r[2] or '', r[3], r[4] or '',
                          r[5], _service(r[6]), context.get_relative_path(db_path)))
    data_headers = ('Name', 'URL', 'Avatar URL', 'Subscriber Count', 'Description',
                    'Notification Mode (as stored)', 'Service', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def newpipe_playback_positions(context):
    query = '''SELECT st.progress_time, s.title, s.url, s.duration, s.uploader, s.service_id
               FROM stream_state st
               JOIN streams s ON s.uid = st.stream_id
               ORDER BY s.title'''
    rows, sources = _rows(context, query)
    data_list = []
    for r, db_path in rows:
        data_list.append((r[0], r[1] or '', r[2] or '', r[3], r[4] or '', _service(r[5]),
                          context.get_relative_path(db_path)))
    data_headers = ('Progress Time (ms)', 'Title', 'URL', 'Duration (seconds)',
                    'Uploader', 'Service', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def newpipe_playlists(context):
    query = '''SELECT p.name, j.join_index, s.title, s.url, s.uploader, s.service_id
               FROM playlist_stream_join j
               JOIN playlists p ON p.uid = j.playlist_id
               JOIN streams s ON s.uid = j.stream_id
               ORDER BY p.name, j.join_index'''
    rows, sources = _rows(context, query)
    data_list = []
    for r, db_path in rows:
        data_list.append((r[0] or '', r[1], r[2] or '', r[3] or '', r[4] or '',
                          _service(r[5]), context.get_relative_path(db_path)))
    data_headers = ('Playlist', 'Position', 'Title', 'URL', 'Uploader', 'Service',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)
