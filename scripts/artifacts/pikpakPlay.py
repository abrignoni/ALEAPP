__artifacts_v2__ = {
    "get_pikpakPlay": {
        "name": "PikPak Play",
        "description": "Parses PikPak video playback history (last play timestamp, duration, played time and name) from the PikPak greendao.db.",
        "author": "",
        "creation_date": "2023-03-24",
        "last_update_date": "2023-03-24",
        "requirements": "none",
        "category": "PikPak",
        "notes": "",
        "paths": ('*/com.pikcloud.pikpak/databases/greendao.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_pikpakPlay(context):
    files_found = context.get_files_found()

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('greendao.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            SELECT last_play_timestamp, duration, played_time, max_played_time, name
            from VIDEO_PLAY_RECORD
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            last_play = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((last_play, row[1], row[2], row[3], row[4]))

    data_headers = (('Last Play Timestamp', 'datetime'), 'Duration', 'Played Time', 'Max Played Time', 'Name')
    return data_headers, data_list, source_path
