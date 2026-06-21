# pylint: disable=W0613
__artifacts_v2__ = {
    "get_imagemngCache": {
        "name": "Image Manager Cache",
        "description": "Cached images from app image_manager_disk_cache (Glide) and .cnt cache files",
        "author": "",
        "creation_date": "2022-03-05",
        "last_update_date": "2022-03-05",
        "requirements": "none",
        "category": "Image Manager Cache",
        "notes": "",
        "paths": ('*/cache/image_manager_disk_cache/*.*', '*/*.cnt'),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, check_in_media


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_imagemngCache(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        filename = os.path.basename(file_found)
        source_path = os.path.dirname(file_found)
        media = check_in_media(file_found, filename)
        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), media, filename, file_found))

    data_headers = (
        ('Timestamp Last Modified', 'datetime'), ('Media', 'media'), 'Filename', 'Source File')
    return data_headers, data_list, source_path
