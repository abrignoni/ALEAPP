__artifacts_v2__ = {
    "get_imagemngCache": {
        "name": "Image Manager Cache",
        "description": "Files from app image_manager_disk_cache (Glide) directories and files with a .cnt extension, reported without checking their content; .cnt files held cached image data in the samples examined",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-03-05",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Image Manager Cache",
        "notes": "Timestamp Modified is the modification time the extraction recorded for the file as "
                 "an epoch value (a tar member time, a zip extended timestamp field, or the time of the "
                 "file in an input folder), shown in UTC. It is blank when the extraction recorded no "
                 "such value. Archive Time Modified (No Zone) is filled only in that case, from the zip "
                 "directory entry, which carries a wall clock reading with no time zone; it is reported "
                 "as stored and no instant is asserted for it. What event sets the modification time of "
                 "a cache file is not established here. The second path pattern matches a file with a "
                 ".cnt extension in any folder of the extraction, and no file is tested for image "
                 "content. Reference: Glide, 'DiskCache.Factory.DEFAULT_DISK_CACHE_DIR', https://github.com/bumptech/glide/blob/36a7b2ecd75d84c86d4238240193ecd5e48d69ce/library/src/main/java/com/bumptech/glide/load/engine/cache/DiskCache.java",
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


def _recorded_times(seeker, file_found):
    """Return (epoch modification time as UTC, zone-less zip directory time as stored)."""
    info = seeker.file_infos.get(file_found) if seeker else None
    if not info:
        return '', ''
    if info.modification_date:
        return _sec_to_utc(info.modification_date), ''
    zip_file = getattr(seeker, 'zip_file', None)
    # A name stored more than once with different content is staged from a
    # chosen entry, which getinfo() does not necessarily return.
    if zip_file is None or info.source_path in getattr(seeker, '_chosen', {}):
        return '', ''
    try:
        stored = zip_file.getinfo(info.source_path).date_time
    except KeyError:
        return '', ''
    return '', '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*stored)


@artifact_processor
def get_imagemngCache(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        filename = os.path.basename(file_found)
        source_path = os.path.dirname(file_found)
        media = check_in_media(file_found, filename)
        modified, modified_as_stored = _recorded_times(seeker, file_found)
        data_list.append((modified, modified_as_stored, media, filename, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Archive Time Modified (No Zone)', ('Media', 'media'), 'Filename', 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
