# pylint: disable=W0613
__artifacts_v2__ = {
    "get_smyfilescache": {
        "name": "My Files Cache",
        "description": "Media cached by Samsung My Files (FileCache.db) with the cached thumbnails",
        "author": "",
        "creation_date": "2022-06-23",
        "last_update_date": "2022-06-23",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileCache.db*',
                  '*/com.sec.android.app.myfiles/cache/*.*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.myfiles vc 1520402000 | 2048 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.app.myfiles vc 1150303551 | 1024 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 2048 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles vc 1500405000 | 2048 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media

# FileCache schema varies by version: newer uses date_modified/_data, older uses date/path
SQL_VARIANTS = (
    'SELECT date_modified, _index, _data, size, latest FROM FileCache',
    'SELECT date, _index, path, size, latest FROM FileCache',
)


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_smyfilescache(files_found, report_folder, seeker, wrap_text):
    jpg_by_name = {os.path.basename(str(f)): str(f) for f in files_found if str(f).endswith('.jpg')}

    db_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.db'):
            db_path = file_found
            break

    data_list = []
    if db_path:
        db = open_sqlite_db_readonly(db_path)
        cursor = db.cursor()
        rows = []
        for sql in SQL_VARIANTS:
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
                break
            except sqlite3.Error:
                continue
        for row in rows:
            jpg = jpg_by_name.get(f'{row[1]}.jpg')
            thumb = check_in_media(jpg, f'{row[1]}.jpg') if jpg else ''
            data_list.append((_ms_to_utc(row[0]), thumb, row[1], row[2], row[3], _ms_to_utc(row[4])))
        db.close()

    data_headers = (
        ('Timestamp Modified', 'datetime'), ('Media', 'media'), 'Media Cache ID', 'Path', 'Size',
        ('Latest', 'datetime'))
    return data_headers, data_list, db_path
