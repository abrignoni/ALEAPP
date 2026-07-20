__artifacts_v2__ = {
    "get_googlemapaudioTemp": {
        "name": "Google Maps Voice Guidance (Temp)",
        "description": "Google Maps text-to-speech voice guidance audio (app_tts-temp)",
        "author": "",
        "creation_date": "2023-04-27",
        "last_update_date": "2026-07-12",
        "requirements": "none",
        "category": "Google Maps Voice Guidance",
        "notes": "",
        "paths": ('*/com.google.android.apps.maps/app_tts-temp/**',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 85 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.maps vc 1064201040 | 7 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.maps vc 1067620099 | 6 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.maps vc 1067648704 | 13 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.maps vc 1067057900 | 9 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.maps vc 1067804533 | 3 rows",
        },
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
def get_googlemapaudioTemp(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        # Some archives hold a file and a directory under the same name, so a
        # matched path may exist only in the archive listing, never on disk.
        if not os.path.isfile(file_found):
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
