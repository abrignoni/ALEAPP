__artifacts_v2__ = {
    "get_googlemapaudioTemp": {
        "name": "Google Maps Voice Guidance (Temp)",
        "description": "Audio files in the Google Maps app_tts-temp folder, with the modification time the extraction records for each file. Empty files are not reported.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-04-27",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Google Maps Voice Guidance",
        "notes": (
            "Timestamp Modified is the modification time the tool reads from the input for the file as a "
            "UTC time, to the whole second, such as from a tar header, a zip entry's NTFS (0x000a) or "
            "extended timestamp (0x5455) field, or the file system of a disk image. When the tool reads "
            "no UTC time, Timestamp Modified is blank and Modified (no zone, as stored) shows the date "
            "and time the input holds, with no zone conversion. That is the case for a FAT directory "
            "entry, an exFAT directory entry (its stored UTC offset is not applied or shown here) and a "
            "zip entry with only its DOS date and time. Which zone such a reading is in is not "
            "established. Both columns are blank when the input holds neither, and a recorded time of 0 "
            "is treated as no time. For a folder or single-file input Timestamp Modified is the time the "
            "operating system reports for that file on the examiner's machine, including any conversion "
            "it applied, and whatever copied the file there may have set it. The staged copy's own time "
            "is not reported. Of the five registered zip images with rows, sharon_a14 (13 files) records "
            "the NTFS field on these files, and the 2026-10-04 check read no extended timestamp from "
            "them, and the other four record the extended timestamp on every file; on a run of 2026-10-23"
            " Timestamp Modified was filled on all 13 sharon_a14 rows. What event of the app sets the "
            "file's modification time is not established."
        ),
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
def get_googlemapaudioTemp(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
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
        recorded, modified_as_stored = _file_times(seeker, file_found)
        modified = _sec_to_utc(recorded)
        data_list.append((modified, modified_as_stored, media, name, file_size))

    data_headers = (('Timestamp Modified', 'datetime'), 'Modified (no zone, as stored)', ('Audio', 'media'),
                    'Filename', 'File Size')
    return data_headers, data_list, source_path
