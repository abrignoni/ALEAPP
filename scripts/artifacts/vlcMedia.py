__artifacts_v2__ = {
    "get_vlcMedia": {
        "name": "VLC",
        "description": "Parses VLC media library entries from vlc_media.db.",
        "author": "@abrignoni",
        "creation_date": "2021-03-01",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "VLC",
        "notes": "One row per entry in the Media table of app_db/vlc_media.db, joined to Folder for the "
                 "containing folder path. Media is the VLC medialibrary's index of the files it has "
                 "scanned, so a row records that the file was present and scanned on the device, and the "
                 "playback columns record whether it was then played. Play Count is the number of times "
                 "the entry was played, and Last Played is empty for a file that was scanned but never "
                 "played. Resume Position is the last_time column, the position playback last stopped "
                 "at, reported in seconds; the medialibrary stores -1 in it and in last_position when "
                 "there is no stored position, and both are reported as empty in that case. Duration is "
                 "the media length in seconds, converted from the stored milliseconds. Type is decoded "
                 "from the medialibrary's own enum, 0 unknown, 1 video, 2 audio (IMedia.h in "
                 "videolan/medialibrary at code.videolan.org); any other value is reported as stored. "
                 "Title is the medialibrary's title for the entry, which is the file name unless the "
                 "media carried its own metadata. Insertion Date and Last Played are Unix seconds and "
                 "are reported as UTC. Is Favorite is the flag on the media entry; the Folder table "
                 "carries a separate is_favorite of its own, which is why the media one is qualified in "
                 "the query. Path comes from Folder and is the folder holding the file, as a file:// "
                 "URL, not the full path to the file itself. Thumbnails are not covered here: releases "
                 "from this generation record them in a Thumbnail table in this same database rather "
                 "than in the medialib folders the separate VLC Thumbnails artifacts look for, and no "
                 "thumbnail was generated on the tested data, so that table is named but left unparsed "
                 "rather than guessed at.",
        "paths": ('*vlc_media.db*',),
        "output_types": "standard",
        "artifact_icon": "film",
    }
}

import datetime

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
    files_found = context.get_files_found()

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('vlc_media.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        if db:
            cursor = db.cursor()
            # is_favorite exists on both Media and Folder in current releases, so
            # the media one is qualified or the query fails as ambiguous.
            cursor.execute('''
                SELECT Media.insertion_date, Media.last_played_date, Media.filename,
                       Folder.path, Media.is_favorite, Media.play_count, Media.last_time,
                       Media.duration, Media.type, Media.title
                FROM Media
                LEFT JOIN Folder ON Media.folder_id = Folder.id_folder
            ''')
            all_rows = cursor.fetchall()
            db.close()

            for row in all_rows:
                data_list.append((
                    _ts_to_utc(row[0]), _ts_to_utc(row[1]), row[2], row[3], row[4],
                    row[5], _seconds(row[6]), _seconds(row[7], 1000),
                    _media_type(row[8]), row[9],
                ))

    data_headers = (
        ('Insertion Date', 'datetime'), ('Last Played', 'datetime'), 'Filename', 'Path',
        'Is Favorite?', 'Play Count', 'Resume Position (seconds)', 'Duration (seconds)',
        'Type', 'Title',
    )
    return data_headers, data_list, source_path
