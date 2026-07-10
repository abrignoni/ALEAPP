# pylint: disable=W0613
__artifacts_v2__ = {
    "get_smyFiles2": {
        "name": "My Files - Download History (FileInfo)",
        "description": "Download history recorded by Samsung My Files (FileInfo.db)",
        "author": "",
        "creation_date": "2020-12-17",
        "last_update_date": "2020-12-17",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileInfo.db',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.app.myfiles vc 1150303551 | 13 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles vc 1500405000 | 0 rows",
        },
    },
    "get_smyFiles2_gdrive": {
        "name": "My Files - Google Drive",
        "description": "Google Drive entries cached by Samsung My Files (FileInfo.db) with thumbnails",
        "author": "",
        "creation_date": "2020-12-17",
        "last_update_date": "2020-12-17",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileInfo.db',
                  '*/com.sec.android.app.myfiles/cache/*.*'),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.app.myfiles vc 1150303551 | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles vc 1500405000 | 0 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _db_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('FileInfo.db'):
            return file_found
    return ''


def _rows(db_path, sql):
    if not db_path:
        return []
    db = open_sqlite_db_readonly(db_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_smyFiles2(files_found, report_folder, seeker, wrap_text):
    db_path = _db_path(files_found)
    rows = _rows(db_path, '''
        SELECT date_modified, name, path, is_hidden, is_trashed, _source, _description
        FROM download_history
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
    data_headers = (
        ('Timestamp', 'datetime'), 'Name', 'Full Path', 'Is Hidden', 'Trashed?', 'Source', 'Description')
    return data_headers, data_list, db_path


@artifact_processor
def get_smyFiles2_gdrive(files_found, report_folder, seeker, wrap_text):
    cache = [str(f) for f in files_found if '/cache/' in str(f).replace('\\', '/')]
    cache_by_name = {os.path.basename(f): f for f in cache}
    cache_by_stem = {os.path.splitext(os.path.basename(f))[0]: f for f in cache}

    db_path = _db_path(files_found)
    rows = _rows(db_path, '''
        SELECT date_modified, file_id, _data, size, mime_type, is_trashed, is_hidden, weblink
        FROM googledrive
    ''')
    data_list = []
    for r in rows:
        fid = str(r[1])
        path = cache_by_name.get(fid) or cache_by_name.get(f'{fid}.jpg') or cache_by_stem.get(fid)
        thumb = check_in_media(path, os.path.basename(path)) if path else ''
        data_list.append((_ms_to_utc(r[0]), thumb, r[1], r[2], r[3], r[4], r[5], r[6], r[7]))

    data_headers = (
        ('Date Modified', 'datetime'), ('Thumbnail', 'media'), 'File ID', 'Data', 'Size', 'MIME Type',
        'Trashed?', 'Hidden?', 'Weblink')
    return data_headers, data_list, db_path
