# pylint: disable=W0613
__artifacts_v2__ = {
    "get_vlcMedia": {
        "name": "VLC",
        "description": "Parses VLC media library entries (insertion and last played dates, filename, path and favorite flag) from vlc_media.db.",
        "author": "",
        "creation_date": "2021-03-01",
        "last_update_date": "2021-03-01",
        "requirements": "none",
        "category": "VLC",
        "notes": "",
        "paths": ('*vlc_media.db*',),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ts_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_vlcMedia(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('vlc_media.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            SELECT insertion_date, last_played_date, filename, path, is_favorite
            from Media
            left join Folder on Media.folder_id = Folder.id_folder
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((_ts_to_utc(row[0]), _ts_to_utc(row[1]), row[2], row[3], row[4]))

    data_headers = (('Insertion Date', 'datetime'), ('Last Played Date', 'datetime'), 'Filename', 'Path', 'Is Favorite?')
    return data_headers, data_list, source_path
