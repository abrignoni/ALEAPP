__artifacts_v2__ = {
    "get_browserCachefirefox": {
        "name": "Firefox Browser Cache",
        "description": "Cached web resources extracted from the Firefox browser disk cache "
                       "(cache2). Timestamp Modified is the modification time the tool reads from"
                       " the input for the cache file. Source URL is the text after the first "
                       "partitionKey=%28 marker, up to one byte before the first necko text in "
                       "the file. It is blank when either is absent or out of order",
        "author": "@abrignoni",
        "creation_date": "2023-01-30",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Browser Cache",
        "notes": "Timestamp Modified is the modification time the tool reads from the input for "
                 "the file as a UTC time, to the whole second, such as from a tar header or a zip"
                 " entry's NTFS or extended timestamp field. When the tool reads no UTC time, "
                 "Timestamp Modified is blank and Modified (no zone, as stored) shows the date "
                 "and time the input holds, with no zone conversion. That is the case for a FAT "
                 "directory entry, an exFAT directory entry (its stored UTC offset is not applied"
                 " or shown here) and a zip entry with only its DOS date and time. Both columns "
                 "are blank when the input holds neither, and a recorded time of 0 is treated as "
                 "no time. For a folder or single-file input Timestamp Modified is the time the "
                 "operating system reports for that file on the examiner's machine, including any"
                 " conversion it applied, and whatever copied the file there may have set it. The"
                 " staged copy's own time is not reported. The Source URL cell begins with the "
                 "partition key text, so it holds more than the URL.",
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
    for value in (getattr(times, 'modified', None), getattr(info, 'modification_date', None)):
        if isinstance(value, (int, float)) and value:
            return value, ''
    return None, getattr(times, 'modified_no_zone', None) or ''


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

        modified, no_zone = _file_times(context.get_seeker(), file_found)
        data_list.append((_sec_to_utc(modified), no_zone, filename, mime, media, url,
                          context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp Modified', 'datetime'), 'Modified (no zone, as stored)', 'Filename', 'Mime Type',
        ('Cached File', 'media'),
        'Source URL', 'Source')
    return data_headers, data_list, context.get_relative_path(source_path)
