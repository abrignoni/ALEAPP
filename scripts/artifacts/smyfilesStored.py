__artifacts_v2__ = {
    "get_smyfilesStored": {
        "name": "smyfilesStored",
        "description": "Parses cached file records (timestamp, storage, path, size and latest access) from the Samsung My Files FileCache.db.",
        "author": "@abrignoni",
        "creation_date": "2020-03-19",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileCache.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.myfiles vc 1520402000 | 2048 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.app.myfiles vc 1150303551 | 1024 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 2048 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles vc 1500405000 | 2048 rows",
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc

# Newer FileCache uses date_modified/_data, older uses date/path. Try newer first
# and fall back only when it yields nothing, so a failed second query cannot wipe
# a good result from the first.
SQL_VARIANTS = (
    '''SELECT datetime(date_modified / 1000, "unixepoch"), storage, _data, size,
              datetime(latest / 1000, "unixepoch")
       FROM FileCache WHERE _data IS NOT NULL''',
    '''SELECT datetime(date / 1000, "unixepoch"), storage, path, size,
              datetime(latest / 1000, "unixepoch")
       FROM FileCache WHERE path IS NOT NULL''',
)


@artifact_processor
def get_smyfilesStored(context):
    files_found = context.get_files_found()

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        # The glob also collects -wal/-shm sidecars; open the database itself.
        if file_found.endswith('FileCache.db'):
            source_path = file_found
            break

    data_list = []
    all_rows = []
    db = open_sqlite_db_readonly(source_path) if source_path else None
    if db is not None:
        cursor = db.cursor()
        for sql in SQL_VARIANTS:
            try:
                cursor.execute(sql)
                all_rows = cursor.fetchall()
                if all_rows:
                    break
            except sqlite3.Error:
                continue
        db.close()

    for row in all_rows:
        data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],convert_human_ts_to_utc(row[4])))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Storage',
        'Path',
        'Size',
        ('Latest', 'datetime'),
    )
    return data_headers, data_list, source_path
