# pylint: disable=W0702
__artifacts_v2__ = {
    "get_smyfilesStored": {
        "name": "smyfilesStored",
        "description": "Parses cached file records (timestamp, storage, path, size and latest access) from the Samsung My Files FileCache.db.",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
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

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_smyfilesStored(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    all_rows = []
    try:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(date / 1000, "unixepoch"),
        storage,
        path,
        size,
        datetime(latest /1000, "unixepoch")
        from FileCache
        where path is not NULL
        ''')

        all_rows = cursor.fetchall()
    except:
        all_rows = []

    try:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            datetime(date_modified / 1000, "unixepoch"),
            storage,
            _data,
            size,
            datetime(latest /1000, "unixepoch")
            from FileCache
            where _data is not NULL
        ''')

        all_rows = cursor.fetchall()
    except:
        all_rows = []

    data_list = []
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
