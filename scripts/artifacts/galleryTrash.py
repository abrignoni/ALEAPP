# pylint: disable=W0613
__artifacts_v2__ = {
    "get_galleryTrash": {
        "name": "Gallery Trash",
        "description": "Deleted media held in the Samsung Gallery trash (local.db trash table)",
        "author": "",
        "creation_date": "2023-04-25",
        "last_update_date": "2023-04-25",
        "requirements": "none",
        "category": "Gallery Trash",
        "notes": "",
        "paths": ('*/data/com.sec.android.gallery3d/databases/local.db*',
                  '*/data/com.sec.android.gallery3d/files/.Trash/**'),
        "output_types": "all",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.gallery3d vc 1550500003 | 0 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.gallery3d | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.gallery3d | 0 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.gallery3d vc 1450000033 | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.gallery3d vc 1500100001 | 0 rows",
        },
    }
}

import datetime
import json
import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_galleryTrash(files_found, report_folder, seeker, wrap_text):
    # Map basename -> path for the trashed media files so each row can resolve its thumbnail
    trash_files = {os.path.basename(str(f)): str(f) for f in files_found if '.Trash' in str(f)}

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('local.db'):
            continue
        source_path = file_found

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT __deleteTime, __Title, __absPath, __originTitle, __originPath, __expiredPeriod, __restoreExtra
            FROM trash
        ''')
        for row in cursor.fetchall():
            try:
                extra = json.loads(row[6]) if row[6] else {}
            except (ValueError, TypeError):
                extra = {}
            datetaken = _ms_to_utc(extra.get('__dateTaken'))
            latitude = extra.get('latitude', '')
            longitude = extra.get('longitude', '')
            extra_str = '; '.join(f'{k}: {v}' for k, v in extra.items())

            media_path = trash_files.get(row[1])
            thumb = check_in_media(media_path, row[1]) if media_path else ''

            data_list.append((datetaken, _ms_to_utc(row[0]), thumb, row[1], row[3], row[2], row[4],
                              extra_str, latitude, longitude))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'), ('Date Deleted', 'datetime'), ('Deleted Media', 'media'),
        'Trash Title', 'Original Title', 'Trash Path', 'Original Path', 'Extra Data', 'Latitude', 'Longitude')
    return data_headers, data_list, source_path
