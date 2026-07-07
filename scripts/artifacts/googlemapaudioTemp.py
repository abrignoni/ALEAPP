# pylint: disable=W0613
__artifacts_v2__ = {
    "get_googlemapaudioTemp": {
        "name": "Google Maps Voice Guidance (Temp)",
        "description": "Google Maps text-to-speech voice guidance audio (app_tts-temp)",
        "author": "",
        "creation_date": "2023-04-27",
        "last_update_date": "2023-04-27",
        "requirements": "none",
        "category": "Google Maps Voice Guidance",
        "notes": "",
        "paths": ('*/com.google.android.apps.maps/app_tts-temp/**',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
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
def get_googlemapaudioTemp(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        file_size = os.path.getsize(file_found)
        if file_size == 0:
            continue
        name = Path(file_found).name
        source_path = os.path.dirname(file_found)
        media = check_in_media(file_found, name)
        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), media, name, file_size))

    data_headers = (('Timestamp Modified', 'datetime'), ('Audio', 'media'), 'Filename', 'File Size')
    return data_headers, data_list, source_path
