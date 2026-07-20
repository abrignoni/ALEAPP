# pylint: disable=W0613
__artifacts_v2__ = {
    "get_firefoxPermissions": {
        "name": "Firefox - Permissions",
        "description": "Parses Firefox site permissions (origin, permission type, status, modification and expiration timestamps) from permissions.sqlite.",
        "author": "",
        "creation_date": "2022-01-12",
        "last_update_date": "2022-01-12",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/files/mozilla/*.default/permissions.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 5 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_firefoxPermissions(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'permissions.sqlite':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(modificationTime/1000,'unixepoch') AS ModDate,
        origin AS Origin,
        type AS PermType,
        CASE permission
            WHEN 1 THEN 'Allow'
            WHEN 2 THEN 'Block'
        END AS PermState,
        CASE expireTime
            WHEN 0 THEN ''
            else datetime(expireTime/1000,'unixepoch')
        END AS ExpireDate
        FROM moz_perms
        ORDER BY ModDate ASC
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],convert_human_ts_to_utc(row[4])))

        db.close()

    data_headers = (
        ('Modification Timestamp', 'datetime'),
        'Origin Site',
        'Permission Type',
        'Status',
        ('Expiration Timestamp', 'datetime'),
    )
    return data_headers, data_list, source_path
