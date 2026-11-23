__artifacts_v2__ = {
    "get_browserCachechrome": {
        "name": "Chrome Browser Cache",
        "description": "Cached web resources extracted from the _0 files of the Chrome browser disk cache. The time columns are the cache file's modification time as the extraction recorded it, not a time stored inside the entry",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-01-28",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Browser Cache",
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
                 "cache entry. Source URL is the entry's key as stored, which on most rows holds other text "
                 "before the URL. Mime Type is worked out from the body's leading bytes, after gunzip where "
                 "the body is gzip. It is blank when no signature is recognised. It is not a stored header. On"
                 " the registered zip images checked on 2026-10-04, every matched member carried the extended "
                 "timestamp on anne_a15 (21956), galaxys10_a10 (847), hc_pixel8pro_a16 (1289), pixel7a_a14 "
                 "(3035) and samsunga53_a14 (1701), and no matched member carried it on samsungs20_a13 (44) "
                 "and sharon_a14 (13958). Those two zips record the NTFS field instead: on runs of 2026-10-23 "
                 "Timestamp Modified was filled on all 44 rows of samsungs20_a13 and all 13957 rows of "
                 "sharon_a14, and the zip directory reading was 5 hours (samsungs20_a13) or 4 hours "
                 "(sharon_a14) earlier than it to within 1 second.",
        "paths": ('*/data/com.android.chrome/cache/Cache/*_0',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533 | 21956 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 847 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433 | 1289 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 39865 rows",
            "pixel7a_a14": "Android 14 | com.android.chrome vc 616710133 | 3035 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133 | 1701 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233 | 44 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333 | 13957 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033 | 11054 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 1257 rows",
        },
    }
}

import datetime
import gzip
import os
import struct
from io import BytesIO

from scripts.filetype import guess_mime, guess_extension
from scripts.ilapfuncs import artifact_processor, logfunc, check_in_embedded_media

EOF_MARKER = b'\xD8\x41\x0D\x97\x45\x6F\xFA\xF4'


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
def get_browserCachechrome(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_0'):
            continue
        filename = os.path.basename(file_found)
        source_path = os.path.dirname(file_found)

        with open(file_found, 'rb') as f:
            data = f.read()
        try:
            eofloc = data.index(EOF_MARKER)
        except ValueError:
            logfunc(f'Skipping {file_found}: expected byte pattern not found')
            continue

        ab = BytesIO(data)
        ab.read(8)   # header
        ab.read(4)   # version
        url_length = struct.unpack_from("<i", ab.read(4))[0]
        ab.read(8)   # dismiss
        header_length = url_length + 8 + 4 + 4 + 8

        url = ab.read(url_length).decode(errors='replace')
        filedata = ab.read(eofloc - header_length)

        ext = guess_extension(filedata)
        if ext == 'x-gzip':
            try:
                filedata = gzip.decompress(filedata)
            except (OSError, EOFError) as ex:
                logfunc(f'Could not gunzip {file_found}: {ex}')
        mime = guess_mime(filedata)
        ext = guess_extension(filedata)

        name = f'{filename}.{ext}' if ext else filename
        media = check_in_embedded_media(file_found, filedata, name, force_type=mime, force_extension=ext)

        recorded, modified_as_stored = _file_times(seeker, file_found)
        modified = _sec_to_utc(recorded)
        data_list.append((modified, modified_as_stored, filename, mime, media, url, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Modified (no zone, as stored)', 'Filename', 'Mime Type', ('Cached File', 'media'),
        'Source URL', 'Source')
    return data_headers, data_list, context.get_relative_path(source_path)
