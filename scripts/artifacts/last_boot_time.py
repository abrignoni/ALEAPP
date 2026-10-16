__artifacts_v2__ = {
    "last_boot_time": {
        "name": "Last Boot Time",
        "description": "Reports the last_boot_time_utc bootstat record; AOSP stores the event value in the file's modification time. bootstat writes this record with the device's current time each time its RecordBootComplete function runs (bootstat.cpp at tag android-15.0.0_r1, lines 1310 to 1319), so the value is the time of that run by the device clock. The time shown is the modification time the extraction recorded for the file.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2022-01-05",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Power Events",
        "notes": "Timestamp is the modification time the extraction recorded for the file as an "
                 "epoch value, shown in UTC: the extended timestamp field (0x5455) of a zip member, the mtime "
                 "of a tar member, or the file's own modification time when the input is a folder. It is "
                 "blank when the extraction recorded no such value. Archive Time Modified (No Zone) is "
                 "filled only in that case, for a zip member, with the date and time in the member's zip "
                 "directory entry, shown as stored. A zip directory entry records no time zone, so that "
                 "reading is not converted and which zone it is in is not established. One row is "
                 "reported per matched file. On the registered images checked on 2026-10-04, each held "
                 "one matched file; the zip member carried the extended timestamp on anne_a15, "
                 "galaxys10_a10, hc_pixel8pro_a16, kevin_pocox7_a15, pixel7a_a14, samsunga53_a14 and "
                 "russell_pixel6a_a13, where the zip directory reading was within 1 second of a whole "
                 "number of hours from it (2 hours later on galaxys10_a10, 4 or 5 hours earlier on the "
                 "other six); it carried none on samsungs20_a13 and sharon_a14; userb2_a13 is a tar. "
                 "Extraction and acquisition handling can disturb file timestamps, so validate the value "
                 "against other sources. Reference: AOSP bootstat, 'boot_event_record_store.cpp (event "
                 "values are stored in the file mtime attribute)', "
                 "https://android.googlesource.com/platform/system/core/+/refs/tags/android-15.0.0_r1/bootstat/boot_event_record_store.cpp#49 "
                 "(line 49 reads the value from st_mtime; line 89 sets it with utime())",
        "paths": ('*/misc/bootstat/last_boot_time_utc'),
        "output_types": "standard",
        "artifact_icon": "power",
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
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logdevinfo


def _recorded_times(seeker, file_found):
    """Return (epoch modification time as UTC, zone-less zip directory time as stored)."""
    info = seeker.file_infos.get(file_found) if seeker else None
    if not info:
        return '', ''
    if info.modification_date:
        try:
            return datetime.datetime.fromtimestamp(
                int(info.modification_date), datetime.timezone.utc), ''
        except (ValueError, OverflowError, OSError, TypeError):
            return '', ''
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
def last_boot_time(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source_paths = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('last_boot_time_utc'):
            continue # Skip all other files

        file_name = 'last_boot_time_utc'

        boot_time, boot_time_as_stored = _recorded_times(seeker, file_found)

        if boot_time:
            logdevinfo(f"<b>Last Boot Timestamp: </b>{boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        elif boot_time_as_stored:
            logdevinfo(f"<b>Last Boot Archive Time (No Zone): </b>{boot_time_as_stored}")
        data_list.append((boot_time, boot_time_as_stored, file_name))
        source_paths.append(context.get_relative_path(file_found))

    data_headers = (('Timestamp', 'datetime'), 'Archive Time Modified (No Zone)', 'File Name')
    return data_headers, data_list, '\n'.join(source_paths)
