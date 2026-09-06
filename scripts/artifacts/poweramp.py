__artifacts_v2__ = {
    "poweramp_library": {
        "name": "Poweramp Library and Play History",
        "description": "Audio files Poweramp has indexed, with play counts, last played times and resume positions",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Poweramp",
        "sample_data": {
            "emu_a15_oss_v15": "Poweramp build-1025-bundle-play | 4 rows",
        },
        "notes": "One row per row of folder_files in "
                 "com.maxmpz.audioplayer/databases/folders.db, which is the player's own index of "
                 "the audio in the folders it was pointed at. The file name is in folder_files "
                 "and the directory is in the folders table, so Storage Path is the two joined; "
                 "the module does not use folder_files.file_path, which was empty on every row of "
                 "the tested image. "
                 "The table carries two different time units and they were separated by "
                 "measurement, not assumption: Last Played and Played Fully At are Unix "
                 "milliseconds, while Date Indexed and File Created are Unix seconds, and on the "
                 "tested image a millisecond value and a second value written moments apart both "
                 "resolved to the same minute. All four are reported as UTC. "
                 "Last Played, Play Count and Played Fully At mean different things, which was "
                 "established by driving the app rather than inferred. Last Played is stamped when "
                 "a track STARTS: two tracks skipped after a few seconds carry it and their Play "
                 "Count stayed 0. Play Count, Total Play Count and Played Fully At move only when "
                 "a track reaches its end: one track played to completion took Play Count from 0 "
                 "to 1 and gained a Played Fully At stamp. So a row with Last Played set and Play "
                 "Count 0 records a track that was started and not finished, and that distinction "
                 "is the artifact's main value. "
                 "Resume Position (ms) is the offset the app would resume from and is reset to 0 "
                 "by a complete play, so a non-zero value marks a track left part way through. "
                 "Artist, Album and Rating were empty or 0 on every row of the tested image "
                 "because the audio it was built from carries no such tags and nothing was rated; "
                 "the app reads them from the file and they populate on ordinary music. Year read "
                 "10000 on every row, which is the app's own placeholder for a file with no year "
                 "tag rather than a date, and it is reported as stored. "
                 "A row is evidence the app indexed the file, and a non-zero Play Count is "
                 "evidence it played it to the end; neither is evidence a person was listening. "
                 "Tables in the same database that are not parsed here: eq_presets (17,730 rows) "
                 "and milk_presets (263) are visualisation and equaliser presets the app ships, "
                 "reverb_presets and milk_preset_containers likewise; playlists, playlist_entries, "
                 "queue, bookmarks, search_history, settings_search_history, cat_stats, "
                 "known_devices and lrc_files were all empty on the tested image and hold user "
                 "activity worth parsing on a device that has used those features; albums, "
                 "artists, genres, composers and years are lookup rows the library builds from the "
                 "same files this artifact already reports.",
        "paths": ('*/com.maxmpz.audioplayer/databases/folders.db*',),
        "output_types": "standard",
        "artifact_icon": "music",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'com.maxmpz.audioplayer/databases/folders.db'


def _db_files(context):
    """The folders.db files, one per container, sidecars excluded."""
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if path.endswith(DB_SUFFIX):
            out.append(path)
    return out


def _ms(value):
    """A Unix millisecond stamp as UTC. Blank for the app's 0 default."""
    return _seconds(value, 1000)


def _sec(value):
    """A Unix second stamp as UTC. Blank for the app's 0 default."""
    return _seconds(value, 1)


def _seconds(value, divisor):
    if not value:
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value // divisor)
    except (OverflowError, OSError, ValueError):
        return ''


def _path(folder, name):
    """Storage Path from the folder row and the file name, which is where the app keeps it."""
    folder = (folder or '').replace('\\', '/')
    name = name or ''
    if folder and not folder.endswith('/'):
        folder += '/'
    return folder + name


@artifact_processor
def poweramp_library(context):
    query = '''SELECT f.played_at, f.played_fully_at, f.created_at, f.file_created_at,
                      f.title_tag, f.name, f.artist_tag, f.album_tag, f.duration,
                      f.played_times, f.total_played_times, f.last_pos, f.rating,
                      f.year, f.bit_rate, o.path
               FROM folder_files f
               LEFT JOIN folders o ON o._id = f.folder_id
               ORDER BY f.played_at DESC, f.name'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _ms(r[1]), _sec(r[2]), _sec(r[3]),
                r[4] or r[5] or '', r[6] or '', r[7] or '',
                r[8], r[9], r[10], r[11], r[12], r[13], r[14],
                _path(r[15], r[5]),
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Last Played', 'datetime'), ('Played Fully At', 'datetime'),
        ('Date Indexed', 'datetime'), ('File Created', 'datetime'),
        'Title', 'Artist', 'Album', 'Duration (ms)', 'Play Count',
        'Total Play Count', 'Resume Position (ms)', 'Rating', 'Year (as stored)',
        'Bit Rate', 'Storage Path', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
