# pylint: disable=W0613
__artifacts_v2__ = {
    "get_smanagerCrash": {
        "name": "smanagerCrash",
        "description": "",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/com.samsung.android.sm/databases/sm.db',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_smanagerCrash(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT crash_time, package_name
        FROM crash_info
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
        data_list.append((timestamp, row[1]))

    data_headers = (('Timestamp', 'datetime'), 'Package Name')
    return data_headers, data_list, source_path
