# pylint: disable=W0613
__artifacts_v2__ = {
    "get_torThumbs": {
        "name": "TOR Thumbnails",
        "description": "Page thumbnails cached by the Tor Browser (mozac_browser_thumbnails)",
        "author": "",
        "creation_date": "2021-12-23",
        "last_update_date": "2021-12-23",
        "requirements": "none",
        "category": "TOR",
        "notes": "",
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


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_torThumbs(files_found, report_folder, seeker, wrap_text):
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
        data_list.append((_sec_to_utc(os.path.getmtime(file_found)), media, filename, location))

    data_headers = (('Modified Time', 'datetime'), ('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, source_path
