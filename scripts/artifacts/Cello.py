__artifacts_v2__ = {
    "get_Cello": {
        "name": "Cello - Google Drive",
        "description": "Parses the items table of the Google Drive cello.db (dates read as Unix milliseconds, title, MIME type, quota bytes and flags). The Trashed column reports the trashed flag and the Offline column reports an offlineStatus property of 1; a file checked in as Offline File is the blob the item's content metadata names.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2020-12-21",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "The Shared With Me Date, Modified By Me Date and Viewed By Me Date columns are the "
                 "shared_with_me_date, modified_by_me_date and viewed_by_me_date columns of the items "
                 "table; which account the name refers to is not recorded in the row and is not "
                 "established here. The Trashed column is the trashed flag as stored; the table also "
                 "has explicitly_trashed and trashed_date columns that this artifact does not report, "
                 "and no row was flagged trashed on sharon_a14, samsunga53_a14 or pixel7a_a14 "
                 "(20, 17 and 4 rows). Read as Unix milliseconds, the date values on those three "
                 "images fall in 2022 to 2025; no source for the unit was found. A date stored as 0 "
                 "or NULL is reported blank. A cello.db whose query fails is named in the run log "
                 "and adds no rows.",
        "paths": ('*/com.google.android.apps.docs/app_cello/*/cello.db*',
                  '*/com.google.android.apps.docs/files/shiny_blobs/blobs/*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.docs vc 214164863 | 3 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.docs vc 211210540 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.docs vc 214512167 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.docs vc 214173331 | 2 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.docs vc 213440084 | 4 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.docs vc 214258185 | 17 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.docs vc 214207580 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.docs vc 213692448 | 20 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.docs vc 213183212 | 1 row",
            "userb2_a13": "Android 13 | com.google.android.apps.docs vc 213806576 | 4 rows",
        },
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media, logfunc
from scripts.artifacts.storagePathViews import unique_files


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_Cello(context):
    files_found = unique_files(context)
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
        except sqlite3.Error as ex:
            logfunc(f'Cello - Google Drive: could not query items in '
                    f'{context.get_relative_path(file_found)}: {ex}')
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
                              r[7], r[8], r[9], r[10], media_ref, context.get_relative_path(file_found)))

    data_headers = (('Created Date', 'datetime'), 'File Name', ('Modified Date', 'datetime'),
                    ('Shared With Me Date', 'datetime'), ('Modified By Me Date', 'datetime'),
                    ('Viewed By Me Date', 'datetime'), 'Mime Type', 'Offline', 'Quota Size',
                    'Folder', 'User is Owner', 'Trashed', ('Offline File', 'media'), 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
