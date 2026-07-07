# pylint: disable=W0613
__artifacts_v2__ = {
    "get_googlemapaudio": {
        "name": "Google Maps Voice Guidance",
        "description": "Google Maps text-to-speech voice guidance audio (app_tts-cache)",
        "author": "",
        "creation_date": "2021-12-27",
        "last_update_date": "2021-12-27",
        "requirements": "none",
        "category": "Google Maps Voice Guidance",
        "notes": "",
        "paths": ('*/com.google.android.apps.maps/app_tts-cache/*_*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime
import os
import re
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, check_in_media

NAME_PATTERN = re.compile(r"-?\d+_\d+")


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_googlemapaudio(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'sbin' in file_found:
            continue
        name = Path(file_found).name
        if not NAME_PATTERN.fullmatch(name):
            continue
        file_size = os.path.getsize(file_found)
        if file_size == 0:
            continue
        source_path = os.path.dirname(file_found)
        # filename is <geo>_<timestamp_ms>
        timestamp = _ms_to_utc(name.split('_')[1])
        media = check_in_media(file_found, name)
        data_list.append((timestamp, media, name, file_size))

    data_headers = (('Timestamp', 'datetime'), ('Audio', 'media'), 'Filename', 'File Size')
    return data_headers, data_list, source_path
