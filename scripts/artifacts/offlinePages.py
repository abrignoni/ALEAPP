__artifacts_v2__ = {
    "get_offlinePages": {
        "name": "Offline Pages (MHTML)",
        "description": "Saved offline web pages (MHTML/MHT archives) with the "
                       "Snapshot-Content-Location, Subject and Date headers each file carries and "
                       "the file's modification time as the extraction recorded it",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-01-25",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Offline Pages",
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
                 "set it. The staged copy's own time is not reported. Neither column is read from inside the "
                 "file. Whether the file's modification time is the capture time is not established. Web "
                 "Source, Subject and MIME Date are the Snapshot-Content-Location, Subject and Date headers "
                 "the file carries, shown as the parser returns them: the first header of each name, with "
                 "bytes that are not UTF-8 replaced. The paths match any .mhtml or .mht file in the "
                 "extraction, whichever app wrote it. On the registered zip images checked on 2026-10-04, "
                 "every matched member carried the extended timestamp on anne_a15 (7), galaxys10_a10 (4), "
                 "hc_pixel8pro_a16 (2), kevin_pocox7_a15 (2), pixel7a_a14 (8), samsunga53_a14 (12) and "
                 "russell_pixel6a_a13 (9), and no matched member carried it on samsungs20_a13 (7) and "
                 "sharon_a14 (37). Those two zips record the NTFS field instead, and on runs of 2026-10-23 "
                 "Timestamp Modified was filled on every row of both. Those member counts are counts of "
                 "matched archive members before duplicate storage views of one file are folded, so they can "
                 "exceed the row count.",
        "paths": ('*/*.mhtml', '*/*.mht'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533 | 7 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 2 rows",
            "pixel7a_a14": "Android 14 | com.android.chrome vc 616710133, com.brave.browser vc 426712324, com.microsoft.emmx vc 259210005 | 8 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133 | 4 rows",
            "samsungs20_a13": "Android 13 | com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 7 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333 | 37 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 9 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 4 rows",
        },
    }
}

import datetime
import email
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
def get_offlinePages(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        source_paths.append(file_found)

        recorded, archive_time = _file_times(seeker, file_found)
        timestamp = _sec_to_utc(recorded)
        with open(file_found, 'r', errors='replace', encoding='utf-8') as fp:
            message = email.message_from_file(fp)
            web_source = message['Snapshot-Content-Location']
            subject = message['Subject']
            mime_date = message['Date']

        media = check_in_media(file_found, os.path.basename(file_found))
        data_list.append((timestamp, archive_time, media, web_source, subject, mime_date, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Modified (no zone, as stored)', ('File', 'media'), 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in source_paths)
