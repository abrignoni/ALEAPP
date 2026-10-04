__artifacts_v2__ = {
    "get_offlinePages": {
        "name": "Offline Pages (MHTML)",
        "description": "Saved offline web pages (MHTML/MHT archives) with the "
                       "Snapshot-Content-Location, Subject and Date headers each file carries and "
                       "the file's modification time as the extraction recorded it",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-01-25",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Offline Pages",
        "notes": "Timestamp Modified is the modification time the extraction recorded for the file as "
                 "an epoch value: the extended timestamp field (0x5455) of a zip member, the mtime of a tar "
                 "member, or the file's own modification time when the input is a folder. It is blank when "
                 "the extraction recorded no such value. Archive Time Modified (No Zone) is filled only in "
                 "that case, for a zip member, with the date and time in the member's zip directory entry, "
                 "shown as stored. A zip directory entry records no time zone, so that reading is not "
                 "converted and which zone it is in is not established. Neither column is a recorded "
                 "capture time. Web Source, Subject and MIME Date are the Snapshot-Content-Location, "
                 "Subject and Date headers the file carries, shown as stored. The paths match any .mhtml "
                 "or .mht file in the extraction, whichever app wrote it. On the registered zip images "
                 "checked on 2026-10-04, every matched member carried the extended timestamp on anne_a15 "
                 "(7), galaxys10_a10 (4), hc_pixel8pro_a16 (2), kevin_pocox7_a15 (2), pixel7a_a14 (8), "
                 "samsunga53_a14 (12) and russell_pixel6a_a13 (9), and no matched member carried it on "
                 "samsungs20_a13 (7) and sharon_a14 (37). Those are counts of matched archive members "
                 "before duplicate storage views of one file are folded, so they can exceed the row "
                 "count.",
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
def get_offlinePages(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        source_paths.append(file_found)

        timestamp, archive_time = _recorded_times(seeker, file_found)
        with open(file_found, 'r', errors='replace', encoding='utf-8') as fp:
            message = email.message_from_file(fp)
            web_source = message['Snapshot-Content-Location']
            subject = message['Subject']
            mime_date = message['Date']

        media = check_in_media(file_found, os.path.basename(file_found))
        data_list.append((timestamp, archive_time, media, web_source, subject, mime_date, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Archive Time Modified (No Zone)', ('File', 'media'), 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
    return data_headers, data_list, ', '.join(context.get_relative_path(p) for p in source_paths)
