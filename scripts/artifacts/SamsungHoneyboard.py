# pylint: disable=W0613
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
        "html_columns": ['Thumbnail'],
    }
}

import datetime
import os

from PIL import Image, UnidentifiedImageError

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, media_to_html


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
def get_Honeyboard_Clipboard(files_found, report_folder, seeker, wrap_text):
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
    return data_headers, data_list, source_path


@artifact_processor
def get_honeyboard_screenshot(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        dirname = os.path.basename(os.path.dirname(file_found))
        if dirname == "remote_send":
            continue

        try:
            img = Image.open(file_found)
        except (UnidentifiedImageError, OSError) as ex:
            logfunc(f'Could not open Honeyboard clip as image: {file_found} ({ex})')
            continue

        newfilename = f'{dirname}_{os.path.basename(file_found)}.png'
        savepath = os.path.join(report_folder, newfilename)
        img.save(savepath, 'png')
        thumb = media_to_html(savepath, (savepath,), report_folder)

        modifiedtime = _sec_to_utc(os.path.getmtime(file_found))
        data_list.append((modifiedtime, thumb, file_found))
        source_path = os.path.dirname(os.path.dirname(file_found))

    data_headers = (('File Modified Time', 'datetime'), 'Thumbnail', 'Screenshot Path')
    return data_headers, data_list, source_path
