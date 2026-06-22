# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Cello": {
        "name": "Cello - Google Drive",
        "description": "Parses the Cello db for Google Drive metadata",
        "author": "@KevinPagano3",
        "creation_date": "2020-12-21",
        "last_update_date": "2020-12-21",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "",
        "paths": ('*/com.google.android.apps.docs/app_cello/*/cello.db*',
                  '*/com.google.android.apps.docs/files/shiny_blobs/blobs/*'),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_Cello(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('cello.db'):
            continue
        if '.magisk' in file_found and 'mirror' in file_found:
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT created_date, title, modified_date, shared_with_me_date, modified_by_me_date,
                       viewed_by_me_date, mime_type, Quota_bytes,
                       case is_folder when 1 then 'Yes' else '' end,
                       case is_owner when 1 then 'Yes' else '' end,
                       case trashed when 1 then 'Yes' else '' end,
                       (SELECT value from item_properties
                            where key='offlineStatus' and item_stable_id=stable_id),
                       (SELECT json_extract(value, '$.blobKey') from item_properties
                            where key LIKE 'com.google.android.apps.docs:content_metadata%'
                            and item_stable_id=stable_id)
                FROM items
            ''')
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
        db.close()

        for r in rows:
            is_offline = str(r[11]) == '1'  # offlineStatus value may be int or text affinity
            media_ref = ''
            if is_offline and r[12]:
                blob = next((str(f) for f in files_found if str(f).endswith(str(r[12]))), None)
                if blob:
                    media_ref = check_in_media(blob, r[1] or '') or ''
            data_list.append((_ms_to_utc(r[0]), r[1], _ms_to_utc(r[2]), _ms_to_utc(r[3]),
                              _ms_to_utc(r[4]), _ms_to_utc(r[5]), r[6], 'Yes' if is_offline else 'No',
                              r[7], r[8], r[9], r[10], media_ref, file_found))

    data_headers = (('Created Date', 'datetime'), 'File Name', ('Modified Date', 'datetime'),
                    ('Shared with User Date', 'datetime'), ('Modified by User Date', 'datetime'),
                    ('Viewed by User Date', 'datetime'), 'Mime Type', 'Offline', 'Quota Size',
                    'Folder', 'User is Owner', 'Deleted', ('Offline File', 'media'), 'Source File')
    return data_headers, data_list, source_path
