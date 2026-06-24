__artifacts_v2__ = {
    "get_vlcthumbsADB": {
        "name": "VLC Thumbnails (ADB)",
        "description": "VLC thumbnail cache from an ADB extraction (ef/medialib/thumbnails)",
        "author": "",
        "creation_date": "2022-08-23",
        "last_update_date": "2022-08-23",
        "requirements": "none",
        "category": "VLC",
        "notes": "",
        "paths": ('*/org.videolan.vlc/ef/medialib/thumbnails/*.*',),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "get_vlcthumbsADB_medialib": {
        "name": "VLC Media Lib (ADB)",
        "description": "VLC media library images from an ADB extraction (ef/medialib)",
        "author": "",
        "creation_date": "2022-08-23",
        "last_update_date": "2022-08-23",
        "requirements": "none",
        "category": "VLC",
        "notes": "",
        "paths": ('*/org.videolan.vlc/ef/medialib/*.*',),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import datetime
import os
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, check_in_media


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_vlcthumbsADB(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'thumbnails' not in file_found:
            continue
        filename = Path(file_found).name
        source_path = str(Path(file_found).parents[1])
        media = check_in_media(file_found, filename)
        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), media, filename, context.get_relative_path(file_found)))

    data_headers = (('Modified Timestamp', 'datetime'), ('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_vlcthumbsADB_medialib(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'thumbnails' in file_found:
            continue
        filename = Path(file_found).name
        source_path = str(Path(file_found).parents[1])
        media = check_in_media(file_found, filename)
        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), media, filename, context.get_relative_path(file_found)))

    data_headers = (('Modified Timestamp', 'datetime'), ('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)
