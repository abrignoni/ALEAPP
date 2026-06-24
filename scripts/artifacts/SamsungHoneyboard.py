__artifacts_v2__ = {
    "get_Honeyboard_Clipboard": {
        "name": "Samsung Honeyboard - Clipboard History",
        "description": "Parses the text clipboard history.",
        "author": "@segumarc",
        "creation_date": "2024-05-30",
        "last_update_date": "2024-05-30",
        "requirements": "",
        "category": "Clipboard",
        "notes": "",
        "paths": ('*/com.samsung.android.honeyboard/databases/ClipItem*',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
    },
    "get_honeyboard_screenshot": {
        "name": "Samsung Honeyboard - Clipboard Screenshot",
        "description": "Parses the Samsung Honeyboard clipboard screenshots.",
        "author": "@segumarc",
        "creation_date": "2024-05-30",
        "last_update_date": "2024-05-30",
        "requirements": "",
        "category": "Clipboard",
        "notes": "",
        "paths": ('*/com.samsung.android.honeyboard/clipboard/*/clip',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
    }
}

import datetime
import io
import os

from PIL import Image, UnidentifiedImageError

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, check_in_embedded_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_Honeyboard_Clipboard(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('wal') or file_found.endswith('shm'):
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('SELECT time_stamp, id, type, text, caller_app_uid FROM clip_table')
        for row in cursor.fetchall():
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], row[4]))
        db.close()

    data_headers = (('Timestamp', 'datetime'), 'ID', 'Type', 'Clipboard Content', 'Application UID')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_honeyboard_screenshot(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        dirname = os.path.basename(os.path.dirname(file_found))
        if dirname == "remote_send":
            continue

        # clip files are extensionless image blobs; decode to PNG bytes and
        # register them as embedded media so LAVA handles the thumbnail/media store
        try:
            img = Image.open(file_found)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
        except (UnidentifiedImageError, OSError) as ex:
            logfunc(f'Could not open Honeyboard clip as image: {file_found} ({ex})')
            continue

        name = f'{dirname}_{os.path.basename(file_found)}.png'
        thumb = check_in_embedded_media(file_found, buf.getvalue(), name)

        modifiedtime = _sec_to_utc(os.path.getmtime(file_found))
        data_list.append((modifiedtime, thumb, context.get_relative_path(file_found)))
        source_path = os.path.dirname(os.path.dirname(file_found))

    data_headers = (('File Modified Time', 'datetime'), ('Thumbnail', 'media'), 'Screenshot Path')
    return data_headers, data_list, context.get_relative_path(source_path)
