# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_smyfilesStored": {
        "name": "smyfilesStored",
        "description": "",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileCache.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_smyfilesStored(files_found, report_folder, seeker, wrap_text):

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
        data_list.append((row[0],row[1],row[2],row[3],row[4]))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Storage',
        'Path',
        'Size',
        ('Latest', 'datetime'),
    )
    return data_headers, data_list, source_path
