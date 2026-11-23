__artifacts_v2__ = {
    "get_torThumbs": {
        "name": "TOR Thumbnails",
        "description": "Thumbnail files from the Tor Browser cache folder "
                       "mozac_browser_thumbnails/thumbnails. File Modified is the modification "
                       "time the tool reads from the input for the file; files that do not open "
                       "as images are not listed.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-12-23",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "TOR",
        "notes": "File Modified is the modification time the tool reads from the input for the "
                 "file as a UTC time, to the whole second, such as from a tar header or a zip "
                 "entry's NTFS or extended timestamp field. When the tool reads no UTC time, File"
                 " Modified is blank and Modified (no zone, as stored) shows the date and time "
                 "the input holds, with no zone conversion. That is the case for a FAT directory "
                 "entry, an exFAT directory entry (its stored UTC offset is not applied or shown "
                 "here) and a zip entry with only its DOS date and time. Both columns are blank "
                 "when the input holds neither, and a recorded time of 0 is treated as no time. "
                 "For a folder or single-file input File Modified is the time the operating "
                 "system reports for that file on the examiner's machine, including any "
                 "conversion it applied, and whatever copied the file there may have set it. The "
                 "staged copy's own time is not reported. File Modified is not read from the "
                 "thumbnail content and depends on the acquisition having kept file times. No "
                 "sample data is recorded for this artifact.",
        "paths": ('*/org.torproject.torbrowser/cache/mozac_browser_thumbnails/thumbnails/*.0',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

import datetime
import io
import os

from PIL import Image, UnidentifiedImageError

from scripts.ilapfuncs import artifact_processor, logfunc, check_in_embedded_media
from scripts.artifacts.storagePathViews import unique_files


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
def get_torThumbs(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        location = os.path.dirname(file_found)
        source_path = location

        # The .0 thumbnail files are image blobs without an extension; decode to
        # PNG bytes and register them as embedded media for the LAVA media store.
        try:
            img = Image.open(file_found)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
        except (UnidentifiedImageError, OSError) as ex:
            logfunc(f'Could not open TOR thumbnail as image: {file_found} ({ex})')
            continue

        media = check_in_embedded_media(file_found, buf.getvalue(), f'{filename}.png')
        modified, no_zone = _file_times(context.get_seeker(), file_found)
        data_list.append((_sec_to_utc(modified), no_zone, media, filename,
                          context.get_relative_path(location)))

    data_headers = (('File Modified', 'datetime'), 'Modified (no zone, as stored)', ('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, source_path
