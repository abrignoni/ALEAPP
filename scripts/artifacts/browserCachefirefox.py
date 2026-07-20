__artifacts_v2__ = {
    "get_browserCachefirefox": {
        "name": "Firefox Browser Cache",
        "description": "Cached web resources extracted from the Firefox browser disk cache (cache2)",
        "author": "",
        "creation_date": "2023-01-30",
        "last_update_date": "2023-01-30",
        "requirements": "none",
        "category": "Browser Cache",
        "notes": "",
        "paths": ('*/data/org.mozilla.firefox/cache/*/cache2/entries/**',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 3702 rows",
        },
    }
}

import datetime
import gzip
import os
from io import BytesIO

from scripts.filetype import guess_mime, guess_extension
from scripts.ilapfuncs import artifact_processor, logfunc, check_in_media, check_in_embedded_media


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_browserCachefirefox(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        filename = os.path.basename(file_found)
        source_path = os.path.dirname(file_found)
        with open(file_found, 'rb') as f:
            data = f.read()

        # The source URL sits between the partitionKey marker and 'necko'
        try:
            start = data.index(b'partitionKey=%28') + 16
            end = data.index(b'necko') - 1
            url = data[start:end].decode(errors='replace')
        except ValueError:
            url = ''

        ext = guess_extension(file_found)
        if ext == 'x-gzip':
            try:
                with gzip.GzipFile(fileobj=BytesIO(data)) as gz:
                    body = gz.read()
                mime = guess_mime(body)
                ext = guess_extension(body)
                name = f'{filename}.{ext}' if ext else filename
                media = check_in_embedded_media(file_found, body, name, force_type=mime, force_extension=ext)
            except (OSError, EOFError) as ex:
                logfunc(f'Could not gunzip {file_found}: {ex}')
                mime = guess_mime(file_found)
                media = check_in_media(file_found, filename)
        else:
            mime = guess_mime(file_found)
            name = f'{filename}.{ext}' if ext else filename
            media = check_in_media(file_found, name)

        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), filename, mime, media, url, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Filename', 'Mime Type', ('Cached File', 'media'),
        'Source URL', 'Source')
    return data_headers, data_list, context.get_relative_path(source_path)
