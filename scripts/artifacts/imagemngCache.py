__artifacts_v2__ = {
    "get_imagemngCache": {
        "name": "Image Manager Cache",
        "description": "Cached images from app image_manager_disk_cache (Glide) directories, plus files with a .cnt extension observed holding cached image data in the samples examined",
        "author": "@abrignoni",
        "creation_date": "2022-03-05",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Image Manager Cache",
        "notes": "Reference: Glide, 'DiskCache.Factory.DEFAULT_DISK_CACHE_DIR', https://github.com/bumptech/glide/blob/36a7b2ecd75d84c86d4238240193ecd5e48d69ce/library/src/main/java/com/bumptech/glide/load/engine/cache/DiskCache.java",
        "paths": ('*/cache/image_manager_disk_cache/*.*', '*/*.cnt'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | 1895 rows",
            "galaxys10_a10": "Android 10 | 1140 rows",
            "hc_pixel8pro_a16": "Android 16 | 1219 rows",
            "kevin_pocox7_a15": "Android 15 | 19294 rows",
            "pixel7a_a14": "Android 14 | 6018 rows",
            "samsunga53_a14": "Android 14 | 2348 rows",
            "samsungs20_a13": "Android 13 | 3164 rows",
            "sharon_a14": "Android 14 | 2597 rows",
            "russell_pixel6a_a13": "Android 13 | 7123 rows",
            "userb2_a13": "Android 13 | 458 rows",
        },
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, check_in_media
from scripts.artifacts.storagePathViews import unique_files


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_imagemngCache(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        filename = os.path.basename(file_found)
        source_path = os.path.dirname(file_found)
        media = check_in_media(file_found, filename)
        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), media, filename, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Last Modified', 'datetime'), ('Media', 'media'), 'Filename', 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
