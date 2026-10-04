__artifacts_v2__ = {
    "get_googlemapaudioTemp": {
        "name": "Google Maps Voice Guidance (Temp)",
        "description": "Audio files in the Google Maps app_tts-temp folder, with the modification time the extraction records for each file. Empty files are not reported.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-04-27",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Google Maps Voice Guidance",
        "notes": (
            "Timestamp Modified is the modification time the extraction records for the file, shown in UTC: "
            "a tar member's own time, the extended timestamp field of a zip member, or the file's own time "
            "when the input is a folder. The time of the copy the tool stages is not used. "
            "A zip member with no extended timestamp field has only a zone-less date and time in the "
            "archive directory; Timestamp Modified is then blank and that reading is shown as stored in "
            "Archive Time Modified (No Zone), with no zone applied. "
            "Of the five registered zip images with rows, sharon_a14 (13 files) records no extended "
            "timestamp field on these files and the other four record one on every file. "
            "On galaxys10_a10 the staged copy's time, read on a US Eastern machine, was 21,599 or 21,600 "
            "seconds later than the recorded time on each of the 7 files. "
            "What event of the app sets the file's modification time is not established."
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


def _recorded_times(seeker, file_found):
    """Return (recorded modification time as UTC, zone-less zip directory time as stored).

    The staged copy's own time is not used: for a zip member the seeker sets it from the
    member's zone-less date and time read in the examiner machine's zone.
    """
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
        modified, modified_as_stored = _recorded_times(seeker, file_found)
        data_list.append((modified, modified_as_stored, media, name, file_size))

    data_headers = (('Timestamp Modified', 'datetime'), 'Archive Time Modified (No Zone)', ('Audio', 'media'),
                    'Filename', 'File Size')
    return data_headers, data_list, source_path
