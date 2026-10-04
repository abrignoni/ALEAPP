__artifacts_v2__ = {
    "get_vlcthumbsADB": {
        "name": "VLC Thumbnails (ADB)",
        "description": "Files under org.videolan.vlc/ef/medialib/thumbnails",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-08-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "VLC",
        "notes": "One row per file matched. Staged Copy mtime is the numeric modification time of the "
                 "extracted copy, reported as text without an asserted evidence time zone. This artifact lists "
                 "no sample_data, so no test image is recorded as exercising it.",
        "paths": ('*/org.videolan.vlc/ef/medialib/thumbnails/*.*',),
        "output_types": "standard",
        "artifact_icon": "photo",
    },
    "get_vlcthumbsADB_medialib": {
        "name": "VLC Media Lib (ADB)",
        "description": "Files under org.videolan.vlc/ef/medialib",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-08-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "VLC",
        "notes": "One row per file matched outside the thumbnails folder; the file type is not "
                 "checked. Only paths under the app's medialib/thumbnails directory are "
                 "left out. Staged Copy mtime is the numeric modification time of the extracted "
                 "copy, reported as text without an asserted evidence time zone. This artifact lists no sample_data, so no test image is "
                 "recorded as exercising it.",
        "paths": ('*/org.videolan.vlc/ef/medialib/*.*',),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

import os
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, check_in_media


def _is_thumbnail(context, path):
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    return '/org.videolan.vlc/ef/medialib/thumbnails/' in '/' + relative.lstrip('/')


@artifact_processor
def get_vlcthumbsADB(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _is_thumbnail(context, file_found):
            continue
        filename = Path(file_found).name
        source_path = str(Path(file_found).parents[1])
        media = check_in_media(file_found, filename)
        data_list.append((str(os.path.getmtime(file_found)), media, filename, context.get_relative_path(file_found)))

    data_headers = ('Staged Copy mtime (seconds as stored)', ('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_vlcthumbsADB_medialib(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if _is_thumbnail(context, file_found):
            continue
        filename = Path(file_found).name
        source_path = str(Path(file_found).parents[1])
        media = check_in_media(file_found, filename)
        data_list.append((str(os.path.getmtime(file_found)), media, filename, context.get_relative_path(file_found)))

    data_headers = ('Staged Copy mtime (seconds as stored)', ('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)
