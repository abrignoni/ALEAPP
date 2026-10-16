__artifacts_v2__ = {
    "get_browserCachechrome": {
        "name": "Chrome Browser Cache",
        "description": "Cached web resources extracted from the _0 files of the Chrome browser disk cache. The time columns are the cache file's modification time as the extraction recorded it, not a time stored inside the entry",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-01-28",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Browser Cache",
        "notes": "Timestamp Modified is the modification time the extraction recorded for the cache file as "
                 "an epoch value: the extended timestamp field (0x5455) of a zip member, the mtime of a tar "
                 "member, or the file's own modification time when the input is a folder. It is blank when "
                 "the extraction recorded no such value. Archive Time Modified (No Zone) is filled only in "
                 "that case, for a zip member, with the date and time in the member's zip directory entry, "
                 "shown as stored. A zip directory entry records no time zone, so that reading is not "
                 "converted and which zone it is in is not established. Neither column is read from inside "
                 "the cache entry. On the registered zip images checked on 2026-10-04, every matched "
                 "member carried the extended timestamp on anne_a15 (21956), galaxys10_a10 (847), "
                 "hc_pixel8pro_a16 (1289), pixel7a_a14 (3035) and samsunga53_a14 (1701), and no matched "
                 "member carried it on samsungs20_a13 (44) and sharon_a14 (13958).",
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

        modified, modified_as_stored = _recorded_times(seeker, file_found)
        data_list.append((modified, modified_as_stored, filename, mime, media, url, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Archive Time Modified (No Zone)', 'Filename', 'Mime Type', ('Cached File', 'media'),
        'Source URL', 'Source')
    return data_headers, data_list, context.get_relative_path(source_path)
