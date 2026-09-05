__artifacts_v2__ = {
    "mxplayer_watched": {
        "name": "MX Player Watched Media",
        "description": "Media MX Player recorded as played, with resume positions",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "MX Player",
        "sample_data": {
            "emu_a15_oss_v10": "MX Player 3.1.4 | 2 rows",
        },
        "notes": "One row per entry in the VideoFile table of "
                 "com.mxtech.videoplayer.ad/databases/medias.db that carries a LastWatchTime, so "
                 "every row here is a file the player recorded as played. Last Watched, Finished "
                 "and File Modified are Unix milliseconds and are reported as UTC. Finished is "
                 "written when playback reached the end, so a row with a Last Watched and no "
                 "Finished was stopped part way, and Resume Position then holds the point in "
                 "milliseconds where the player would pick the file up again. Both were observed "
                 "on the tested device: a 30 second clip left part way carried a Resume Position of "
                 "29758 and no Finished, and a 15 second clip played to the end carried a Finished "
                 "equal to its Last Watched and a Resume Position of 0, because the player resets "
                 "the position to the start once a file has run out. A Resume Position of 0 "
                 "therefore means the start of the file and not the absence of a value; that case "
                 "is told apart from a file the player never opened by the blank described below. "
                 "Folder comes from the VideoDirectory "
                 "row the file points at, so Folder and File Name together give the path as the "
                 "app stored it. Resume Position is read from the VideoStates table, matched on "
                 "the file URI that table records rather than on any correlation of size or time; "
                 "a file with no VideoStates row shows a blank Resume Position. Decode Mode is "
                 "reported as stored because its values are not documented in anything published. "
                 "A row is evidence the app played the file, not that a person watched it.",
        "paths": ('*/com.mxtech.videoplayer.ad/databases/medias.db*',),
        "output_types": "standard",
        "artifact_icon": "play-circle",
    },
    "mxplayer_media_library": {
        "name": "MX Player Media Library",
        "description": "Media files MX Player has indexed, played or not",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "MX Player",
        "sample_data": {
            "emu_a15_oss_v10": "MX Player 3.1.4 | 4 rows",
        },
        "notes": "One row per entry in the VideoFile table of "
                 "com.mxtech.videoplayer.ad/databases/medias.db, whether or not it was ever "
                 "played, joined to VideoDirectory for the folder that holds it. File Modified is "
                 "the file's own modification time in Unix milliseconds, reported as UTC, and is "
                 "what the app recorded when it indexed the file. Last Watched is blank on a file "
                 "the app scanned but never played, which is the difference between this artifact "
                 "and MX Player Watched Media. Size, Duration, Width, Height and the three track "
                 "counts are the values the app read out of the file itself. The row survives the "
                 "file being deleted from the device, so an entry here whose path no longer "
                 "resolves is a record that the file was once present in a folder MX Player "
                 "scanned. On the tested image two of the four rows were files left by other apps "
                 "and never opened in MX Player, and both carried a Duration and a resolution but "
                 "no track counts, because the player fills the track counts when it opens a file "
                 "for playback. That is also why Video Tracks and Audio Tracks carried the same "
                 "number on every row of that image: the two played files each held one of each "
                 "and the two unopened files held none, so the columns matched by coincidence of "
                 "this sample rather than because one is derived from the other. Subtitle Tracks "
                 "was 0 throughout, since none of the tested files carried a subtitle track. A row "
                 "is evidence the app saw the file, not that a person watched it.",
        "paths": ('*/com.mxtech.videoplayer.ad/databases/medias.db*',),
        "output_types": "standard",
        "artifact_icon": "film",
    },
}

from urllib.parse import unquote

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/medias.db'

FILE_QUERY = '''SELECT f.LastWatchTime, f.FinishTime, f.LastModified, f.FileName, d.Path,
                       f.Duration, f.Size, f.Width, f.Height, f.VideoTrackCount,
                       f.AudioTrackCount, f.SubtitleTrackCount, f.Read, f.Id
                FROM VideoFile f
                LEFT JOIN VideoDirectory d ON d.Id = f.Directory
                ORDER BY f.LastWatchTime DESC, f.Id'''

STATE_QUERY = 'SELECT Uri, Position, DecodeMode, PlaybackSpeed FROM VideoStates'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value < 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _path_key(value):
    """Normalise a stored file URI or a folder+name pair to one comparable path."""
    if not value:
        return ''
    text = unquote(str(value))
    if text.startswith('file://'):
        text = text[len('file://'):]
    return text.rstrip('/')


def _states(db_path):
    """{normalised path: (position, decode mode, playback speed)} from VideoStates."""
    result = {}
    for row in get_sqlite_db_records(db_path, STATE_QUERY):
        key = _path_key(row[0])
        if key:
            result[key] = (row[1], row[2], row[3])
    return result


def _rows(context, watched_only):
    data_list = []
    sources = []
    for db_path in _db_files(context):
        states = _states(db_path)
        records = get_sqlite_db_records(db_path, FILE_QUERY)
        used = False
        for r in records:
            if watched_only and not r[0]:
                continue
            folder = r[4] or ''
            key = _path_key(f'{folder}/{r[3]}' if folder else r[3])
            position, decode_mode, speed = states.get(key, ('', '', ''))
            used = True
            if watched_only:
                data_list.append((
                    _ms(r[0]), _ms(r[1]), _ms(r[2]), r[3] or '', folder,
                    position if position not in (None, '') else '',
                    r[5], decode_mode if decode_mode not in (None, '') else '',
                    speed if speed not in (None, '') else '',
                    r[6], r[13], context.get_relative_path(db_path)))
            else:
                data_list.append((
                    _ms(r[2]), _ms(r[0]), r[3] or '', folder, r[6], r[5],
                    r[7], r[8], r[9], r[10], r[11],
                    'Yes' if r[12] else 'No', r[13],
                    context.get_relative_path(db_path)))
        if used and db_path not in sources:
            sources.append(db_path)
    return data_list, '\n'.join(sources)


@artifact_processor
def mxplayer_watched(context):
    data_list, sources = _rows(context, watched_only=True)
    data_headers = (
        ('Last Watched', 'datetime'), ('Finished', 'datetime'),
        ('File Modified', 'datetime'), 'File Name', 'Folder',
        'Resume Position (ms)', 'Duration (ms)', 'Decode Mode (as stored)',
        'Playback Speed', 'Size (bytes)', 'Media ID', 'Source File')
    return data_headers, data_list, sources


@artifact_processor
def mxplayer_media_library(context):
    data_list, sources = _rows(context, watched_only=False)
    data_headers = (
        ('File Modified', 'datetime'), ('Last Watched', 'datetime'), 'File Name',
        'Folder', 'Size (bytes)', 'Duration (ms)', 'Width', 'Height',
        'Video Tracks', 'Audio Tracks', 'Subtitle Tracks', 'Played', 'Media ID',
        'Source File')
    return data_headers, data_list, sources
