__artifacts_v2__ = {
    "musicolet_library": {
        "name": "Musicolet Library and Play Counts",
        "description": "Audio files Musicolet has indexed, with play counts and last played times",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Musicolet",
        "sample_data": {
            "emu_a15_oss_v12": "Musicolet 6.14.1 | 5 rows",
        },
        "notes": "One row per row of TABLE_SONGS in "
                 "in.krosbits.musicolet/databases/DB_SONGS_LOG, which is the player's own index "
                 "of the audio it has found. Last Played, Date Added and Date Modified are Unix "
                 "milliseconds and are reported as UTC. Date Added and Date Modified come from the "
                 "file rather than from any play, so they are filled on a track that was never "
                 "opened; Last Played and Play Count are 0 on such a track, which is what "
                 "separates a file the app merely indexed from one it played. Both cases were "
                 "produced on the tested device: two tracks were played and three were indexed and "
                 "left alone. Album Artist, Genre and Composer each held the single value "
                 "<unknown> on every row, because the audio this image was built from carries no "
                 "such tags; the app reads them from the file itself and they vary on ordinary "
                 "music. Play Count is the lifetime count, and the app keeps three rolling "
                 "counters beside it, reported here as Plays This Week, Plays This Month and Plays "
                 "This Year. All four held the same value on every row of the tested image, "
                 "because the only plays happened in the same week they were counted in; on a "
                 "device with older history they diverge, and that divergence is what dates "
                 "activity to a window. Resume Position (ms) is the app's COL_LASTPOS and was 0 on "
                 "every row here, since both tracks were played to the end and the app clears the "
                 "position at that point. Storage "
                 "Path is the app's own readable COL_LOGPATH; Media Path is the musicolet:// URI "
                 "it keys the row on, kept because it carries the MediaStore id. Rating is the "
                 "app's own star rating and was 0 throughout, nothing having been rated. A row is "
                 "evidence the app indexed the file, and a non-zero Play Count is evidence it "
                 "played it, neither being evidence a person listened.",
        "paths": ('*/in.krosbits.musicolet/databases/DB_SONGS_LOG*',),
        "output_types": "standard",
        "artifact_icon": "music",
    },
    "musicolet_playlists": {
        "name": "Musicolet Playlists and Favorites",
        "description": "Songs the user grouped into Musicolet playlists or marked as favorites",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Musicolet",
        "sample_data": {
            "emu_a15_oss_v12": "Musicolet 6.14.1 | 3 rows",
        },
        "notes": "One row per song per list, read from the app's own JSON files under "
                 "in.krosbits.musicolet/files. A user playlist is a file named after the playlist "
                 "with an .mpl extension, so the file name is the playlist name; the favourites "
                 "list is 0.favs and is reported with the Playlist column set to Favorites. Both "
                 "hold the same shape: parallel arrays of song paths (S_P), titles (S_T), albums "
                 "(S_AL), artists (S_AR) and durations (S_D), and Position is the index into those "
                 "arrays, which is the order the app shows. There is no timestamp in either file, "
                 "so a row says the song was in the list at acquisition and not when it was added. "
                 "The app also writes 0.names, a Java-serialised list of the playlist names; it is "
                 "not parsed here because the .mpl file names carry the same names in a form that "
                 "needs no decoding, and a playlist whose file is missing while its name is still "
                 "in 0.names would be the one case where that matters. On the tested device one "
                 "playlist of two songs and one favourite were created deliberately.",
        "paths": ('*/in.krosbits.musicolet/files/*.mpl',
                  '*/in.krosbits.musicolet/files/*.favs'),
        "output_types": "standard",
        "artifact_icon": "list",
    },
    "musicolet_queues": {
        "name": "Musicolet Play Queues",
        "description": "The play queues Musicolet had open, and the songs in each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Musicolet",
        "sample_data": {
            "emu_a15_oss_v12": "Musicolet 6.14.1 | 2 rows",
        },
        "notes": "One row per song per queue, read from in.krosbits.musicolet/files/0.qstk, which "
                 "is JSON. Musicolet keeps several named queues at once: S0_PQ is the list of "
                 "them, S0_CPQ is the index of the one playing, and Active marks that queue. "
                 "Within a queue S0_PQ_T is its name, S0_PQ_CPS is the index of the current song, "
                 "reported as Current, and S0_PQ_OQS.S_P is the song order. A queue is the app's "
                 "working state rather than a saved list, so it shows what was cued up at "
                 "acquisition, which the playlists artifact does not. There is no timestamp in "
                 "this file. On the tested device a single queue was present, named after the "
                 "artist whose songs were played into it, so Queue Name held one value and Active "
                 "was Yes on every row. The app writes a second file, a.qstk, which is 20 bytes of "
                 "binary rather than JSON on the tested image and is not parsed.",
        "paths": ('*/in.krosbits.musicolet/files/0.qstk',),
        "output_types": "standard",
        "artifact_icon": "list",
    },
}

import json
import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, \
    logfunc
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/DB_SONGS_LOG'


def _files(context, test):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if test(str(f).replace('\\', '/'))]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value <= 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _load_json(path):
    """Read one of the app's JSON files. Returns None when it will not parse."""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            return json.loads(handle.read())
    except (OSError, ValueError) as error:
        logfunc(f'Musicolet: could not read {path}: {error}')
        return None


def _list_rows(payload):
    """Yield (position, path, title, album, artist, duration) from a .mpl or .favs body."""
    if not isinstance(payload, dict):
        return
    paths = payload.get('S_P') or []
    titles = payload.get('S_T') or []
    albums = payload.get('S_AL') or []
    artists = payload.get('S_AR') or []
    durations = payload.get('S_D') or []
    for index, path in enumerate(paths):
        yield (index,
               path or '',
               titles[index] if index < len(titles) else '',
               albums[index] if index < len(albums) else '',
               artists[index] if index < len(artists) else '',
               durations[index] if index < len(durations) else '')


@artifact_processor
def musicolet_library(context):
    query = '''SELECT COL_LAST_PLAYED, COL_DATE_ADDED, COL_DATE_MODIFIED, COL_TITLE,
                      COL_ARTIST, COL_ALBUM, album_artist, COL_GENRE, COL_COMPOSER,
                      COL_YEAR, COL_TRACK_NO, COL_DURATION, COL_NUM_PLAYED,
                      COL_NUM_PLAYED_W, COL_NUM_PLAYED_M, COL_NUM_PLAYED_Y,
                      COL_LASTPOS, COL_RATING, COL_LOGPATH, COL_PATH
               FROM TABLE_SONGS
               ORDER BY COL_LAST_PLAYED DESC, COL_TITLE'''
    data_list = []
    sources = []
    for db_path in _files(context, lambda p: p.endswith(DB_SUFFIX)):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[1]), _ms(r[0]), _ms(r[2]), r[3] or '', r[4] or '', r[5] or '',
                r[6] or '', r[7] or '', r[8] or '', r[9], r[10], r[11], r[12],
                r[13], r[14], r[15], r[16], r[17], r[18] or '', r[19] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Date Added', 'datetime'), ('Last Played', 'datetime'),
        ('Date Modified', 'datetime'), 'Title', 'Artist', 'Album', 'Album Artist',
        'Genre', 'Composer', 'Year', 'Track No', 'Duration (ms)', 'Play Count',
        'Plays This Week', 'Plays This Month', 'Plays This Year',
        'Resume Position (ms)', 'Rating', 'Storage Path', 'Media Path', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def musicolet_playlists(context):
    data_list = []
    sources = []
    for path in _files(context, lambda p: p.endswith('.mpl') or p.endswith('.favs')):
        payload = _load_json(path)
        if payload is None:
            continue
        name = os.path.basename(path)
        label = 'Favorites' if name.endswith('.favs') else name[:-len('.mpl')]
        seen = False
        for position, song, title, album, artist, duration in _list_rows(payload):
            seen = True
            data_list.append((label, position, title, artist, album, duration, song,
                              context.get_relative_path(path)))
        if seen and path not in sources:
            sources.append(path)

    data_headers = (
        'Playlist', 'Position', 'Title', 'Artist', 'Album', 'Duration (ms)',
        'Media Path', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def musicolet_queues(context):
    data_list = []
    sources = []
    for path in _files(context, lambda p: p.endswith('files/0.qstk')):
        payload = _load_json(path)
        if not isinstance(payload, dict):
            continue
        active = payload.get('S0_CPQ')
        queues = payload.get('S0_PQ') or []
        seen = False
        for index, queue in enumerate(queues):
            if not isinstance(queue, dict):
                continue
            songs = (queue.get('S0_PQ_OQS') or {}).get('S_P') or []
            current = queue.get('S0_PQ_CPS')
            for position, song in enumerate(songs):
                seen = True
                data_list.append((
                    queue.get('S0_PQ_T') or '', index,
                    'Yes' if index == active else 'No',
                    position, 'Yes' if position == current else 'No', song or '',
                    context.get_relative_path(path)))
        if seen and path not in sources:
            sources.append(path)

    data_headers = (
        'Queue Name', 'Queue Index', 'Active', 'Position', 'Current', 'Media Path',
        'Source File')
    return data_headers, data_list, '\n'.join(sources)
