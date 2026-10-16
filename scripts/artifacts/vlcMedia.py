__artifacts_v2__ = {
    "get_vlcMedia": {
        "name": "VLC",
        "description": "Parses VLC media library entries from vlc_media.db.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-03-01",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "VLC",
        "sample_data": {
            "emu_a15_oss_v4": "VLC 3.7.1 | 2 rows",
        },
        "notes": "One row per Media entry in each matched vlc_media.db, with duplicate storage "
                 "views collapsed. Folder.path is joined using Media.folder_id. last_time, "
                 "last_position and import_type are reported under their stored field names; "
                 "the report does not infer a unit or import category for them. A last_time of "
                 "-1 is shown blank. last_position and import_type are blank when the database "
                 "schema lacks those columns. Duration is converted from milliseconds to seconds. "
                 "Insertion Date and Last Played are read as Unix seconds and shown in UTC. "
                 "Type uses the medialibrary enum in include/medialibrary/IMedia.h "
                 "(videolan/medialibrary at code.videolan.org): 0 unknown, 1 video, 2 audio. "
                 "The revision VLC 3.7.1 builds against was not checked. Thumbnails are reported "
                 "by the separate VLC Thumbnail Data artifact.",
        "paths": ('*vlc_media.db*',),
        "output_types": "standard",
        "artifact_icon": "film",
    }
}

import datetime

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

# IMedia.h, enum class Type, in videolan/medialibrary at code.videolan.org.
MEDIA_TYPES = {0: 'Unknown', 1: 'Video', 2: 'Audio'}

# The medialibrary stores -1 in last_time and last_position when it has no
# stored playback position for an entry.
NO_POSITION = -1


def _ts_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


def _seconds(value, divisor=1):
    if value is None or value == NO_POSITION:
        return ''
    try:
        return round(int(value) / divisor, 3) if divisor != 1 else int(value)
    except (TypeError, ValueError):
        return ''


def _media_type(value):
    if value in MEDIA_TYPES:
        return MEDIA_TYPES[value]
    return f'{value} (as stored)'


@artifact_processor
def get_vlcMedia(context):
    files_found = unique_files(context)

    source_paths = []
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if not source_path.endswith('vlc_media.db'):
            continue
        source_paths.append(source_path)
        db = open_sqlite_db_readonly(source_path)
        if db:
            cursor = db.cursor()
            columns = {column[1] for column in cursor.execute('PRAGMA table_info(Media)')}
            last_position = 'Media.last_position' if 'last_position' in columns else 'NULL'
            import_type = 'Media.import_type' if 'import_type' in columns else 'NULL'
            # is_favorite exists on both Media and Folder in current releases, so
            # the media one is qualified or the query fails as ambiguous.
            cursor.execute(f'''
                SELECT Media.insertion_date, Media.last_played_date, Media.filename,
                       Folder.path, Media.is_favorite, Media.play_count, Media.last_time,
                       Media.duration, Media.type, Media.title, {last_position}, {import_type}
                FROM Media
                LEFT JOIN Folder ON Media.folder_id = Folder.id_folder
            ''')
            all_rows = cursor.fetchall()
            db.close()

            for row in all_rows:
                data_list.append((
                    _ts_to_utc(row[0]), _ts_to_utc(row[1]), row[2], row[3], row[4],
                    row[5], _seconds(row[6]), _seconds(row[7], 1000),
                    _media_type(row[8]), row[9], row[10], row[11], context.get_relative_path(source_path),
                ))

    data_headers = (
        ('Insertion Date', 'datetime'), ('Last Played', 'datetime'), 'Filename', 'Path',
        'Is Favorite?', 'Play Count', 'last_time (as stored)', 'Duration (seconds)',
        'Type', 'Title', 'last_position (as stored)', 'import_type (as stored)', 'Source File',
    )
    return data_headers, data_list, '\n'.join(source_paths)
