__artifacts_v2__ = {
    "factory_reset": {
        "name": "Factory Reset",
        "description": "Reports the factory_reset bootstat record; AOSP stores the event value in the file's modification time. bootstat writes this record with the device's current time when it runs and finds no factory_reset record (RecordFactoryReset in bootstat.cpp at tag android-14.0.0_r1, lines 1428 to 1431), so the value is the time of that run by the device clock. The time shown is the modification time the extraction recorded for the file.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2022-01-05",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "Timestamp is the modification time the tool reads from the input for the file as a UTC time,"
                 " to the whole second, such as from a tar header, a zip entry's NTFS (0x000a) or extended "
                 "timestamp (0x5455) field, or the file system of a disk image. When the tool reads no UTC "
                 "time, Timestamp is blank and Modified (no zone, as stored) shows the date and time the input"
                 " holds, with no zone conversion. That is the case for a FAT directory entry, an exFAT "
                 "directory entry (its stored UTC offset is not applied or shown here) and a zip entry with "
                 "only its DOS date and time. Which zone such a reading is in is not established. Both columns"
                 " are blank when the input holds neither, and a recorded time of 0 is treated as no time. For"
                 " a folder or single-file input Timestamp is the time the operating system reports for that "
                 "file on the examiner's machine, including any conversion it applied, and whatever copied the"
                 " file there may have set it. The staged copy's own time is not reported. One row is reported"
                 " per matched file. On the registered images checked on 2026-10-04, each held one matched "
                 "file; the zip member carried the extended timestamp on anne_a15, galaxys10_a10, "
                 "hc_pixel8pro_a16, kevin_pocox7_a15, pixel7a_a14, samsunga53_a14 and russell_pixel6a_a13, "
                 "where the zip directory reading was within 1 second of a whole number of hours from it (2 "
                 "hours later on galaxys10_a10, 4 or 5 hours earlier on the other six); it carried none on "
                 "samsungs20_a13 and sharon_a14, whose zips record the NTFS field instead, and on runs of "
                 "2026-10-23 the zip directory reading there was 4 hours earlier than it to within 1 second; "
                 "userb2_a13 is a tar. Extraction and acquisition handling can disturb file timestamps, so "
                 "validate the value against other sources. Reference: AOSP bootstat, "
                 "'boot_event_record_store.cpp (event values are stored in the file mtime attribute)', "
                 "https://android.googlesource.com/platform/system/core/+/refs/tags/android-14.0.0_r1/bootstat/boot_event_record_store.cpp"
                 " (lines 66 to 91)",
        "paths": ('*/misc/bootstat/factory_reset'),
        "output_types": "standard",
        "artifact_icon": "loader",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
            "emu_a15_reset_known_20261116": "Android 15 | 1 row (known data; same second as the boot completion in the mint record, after a wipe by that record)",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logdevinfo


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
def factory_reset(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source_paths = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('factory_reset'):
            continue # Skip all other files

        file_name = 'factory_reset'

        recorded, reset_time_as_stored = _file_times(seeker, file_found)
        reset_time = _sec_to_utc(recorded)

        if reset_time:
            logdevinfo(f"<b>Factory Reset Timestamp: </b>{reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
        elif reset_time_as_stored:
            logdevinfo(f"<b>Factory Reset Modified (No Zone): </b>{reset_time_as_stored}")
        data_list.append((reset_time, reset_time_as_stored, file_name))
        source_paths.append(context.get_relative_path(file_found))

    data_headers = (('Timestamp', 'datetime'), 'Modified (no zone, as stored)', 'File Name')
    return data_headers, data_list, '\n'.join(source_paths)
