__artifacts_v2__ = {
    "get_browserCachechrome": {
        "name": "Chrome Browser Cache",
        "description": "Cached web resources extracted from the Chrome browser disk cache",
        "author": "",
        "creation_date": "2023-01-28",
        "last_update_date": "2023-01-28",
        "requirements": "none",
        "category": "Browser Cache",
        "notes": "",
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


@artifact_processor
def get_browserCachechrome(context):
    files_found = context.get_files_found()
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

        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), filename, mime, media, url, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Filename', 'Mime Type', ('Cached File', 'media'),
        'Source URL', 'Source')
    return data_headers, data_list, context.get_relative_path(source_path)
