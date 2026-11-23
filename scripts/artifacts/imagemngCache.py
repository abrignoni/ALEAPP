__artifacts_v2__ = {
    "get_imagemngCache": {
        "name": "Image Manager Cache",
        "description": "Files from app image_manager_disk_cache (Glide) directories and files with a .cnt extension, reported whatever their content. On samsungs20_a13, 2,016 of the 2,109 .cnt files carried an image signature",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-03-05",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Image Manager Cache",
        "notes": "Timestamp Modified is the modification time the tool reads from the input for the file as a "
                 "UTC time, to the whole second, such as from a tar header, a zip entry's NTFS (0x000a) or "
                 "extended timestamp (0x5455) field, or the file system of a disk image. When the tool reads "
                 "no UTC time, Timestamp Modified is blank and Modified (no zone, as stored) shows the date "
                 "and time the input holds, with no zone conversion. That is the case for a FAT directory "
                 "entry, an exFAT directory entry (its stored UTC offset is not applied or shown here) and a "
                 "zip entry from which no UTC modification time is read: one with only its DOS date and time, "
                 "or with an extra field whose time is 0 or unreadable. Which zone such a reading is in is not"
                 " established. Both columns are blank when the tool reads neither. A UTC time recorded as 0 "
                 "is treated as no time. A zip entry's DOS date and time is shown as decoded, with no validity"
                 " check, so an unset one reads 1980-00-00 00:00:00. For a folder or single-file input "
                 "Timestamp Modified is the time the operating system reports for that file on the examiner's "
                 "machine, including any conversion it applied, and whatever copied the file there may have "
                 "set it. The staged copy's own time is not reported. What event sets the modification time of"
                 " a cache file is not established here. The second path pattern matches a file with a .cnt "
                 "extension in any folder of the extraction. Rows are not filtered by content: each file's "
                 "type is read to display it, and a file that is not an image is still reported. On "
                 "samsungs20_a13, of the 2,109 .cnt files, 2,016 carried an image signature, 11 a font header "
                 "and 82 neither. Reference: Glide, 'DiskCache.Factory.DEFAULT_DISK_CACHE_DIR', "
                 "https://github.com/bumptech/glide/blob/36a7b2ecd75d84c86d4238240193ecd5e48d69ce/library/src/main/java/com/bumptech/glide/load/engine/cache/DiskCache.java",
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
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=value // 1)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if _usable(modified):
        return modified, ''
    return None, ''


@artifact_processor
def get_imagemngCache(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
    data_list = []
    source_folders = set()
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        filename = os.path.basename(file_found)
        source_folders.add(os.path.dirname(file_found))
        media = check_in_media(file_found, filename)
        recorded, modified_as_stored = _file_times(seeker, file_found)
        modified = _sec_to_utc(recorded)
        data_list.append((modified, modified_as_stored, media, filename, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Modified (no zone, as stored)', ('Media', 'media'), 'Filename', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_folders))
