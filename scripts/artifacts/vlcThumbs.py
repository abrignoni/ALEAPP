__artifacts_v2__ = {
    "get_vlcThumbs": {
        "name": "VLC Thumbnails",
        "description": "Thumbnail images cached by VLC in the medialib folder",
        "author": "",
        "creation_date": "2021-03-01",
        "last_update_date": "2021-03-01",
        "requirements": "none",
        "category": "VLC",
        "notes": "",
        "paths": ('*/org.videolan.vlc/files/medialib/*.jpg',),
        "output_types": "standard",
        "artifact_icon": "photo",
    },
    "get_vlcThumbs_data": {
        "name": "VLC Thumbnail Data",
        "description": "VLC media library entries (play count, dates) with their cached thumbnails",
        "author": "",
        "creation_date": "2021-03-01",
        "last_update_date": "2021-03-01",
        "requirements": "none",
        "category": "VLC",
        "notes": "",
        "paths": ('*/org.videolan.vlc/files/medialib/*.jpg', '*/org.videolan.vlc/app_db/vlc_media.db*'),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_vlcThumbs(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.jpg'):
            continue
        source_path = os.path.dirname(file_found)
        name = os.path.basename(file_found)
        data_list.append((name, check_in_media(file_found, name)))

    data_headers = ('Filename', ('Thumbnail', 'media'))
    return data_headers, data_list, source_path


@artifact_processor
def get_vlcThumbs_data(context):
    files_found = context.get_files_found()
    jpg_by_name = {os.path.basename(str(f)): str(f) for f in files_found if str(f).endswith('.jpg')}
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('vlc_media.db'):
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT last_played_date, insertion_date, id_media, filename, play_count, is_favorite
            FROM media
        ''')
        for row in cursor.fetchall():
            jpg = jpg_by_name.get(f'{row[2]}.jpg')
            thumb = check_in_media(jpg, f'{row[2]}.jpg') if jpg else ''
            data_list.append((_sec_to_utc(row[0]), _sec_to_utc(row[1]), row[2], row[3], row[4], row[5], thumb))
        db.close()

    data_headers = (
        ('Last Played', 'datetime'), ('Insertion Date', 'datetime'), 'ID Media', 'Filename',
        'Play Count', 'Is Favorite', ('Thumbnail', 'media'))
    return data_headers, data_list, source_path
