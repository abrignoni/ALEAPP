# pylint: disable=W0613
__artifacts_v2__ = {
    "get_scontextLog": {
        "name": "scontextLog",
        "description": "",
        "author": "",
        "creation_date": "2020-04-18",
        "last_update_date": "2020-04-18",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/com.samsung.android.providers.context/databases/ContextLog.db',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_scontextLog(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT starttime, stoptime, time_zone, app_id, app_sub_id, duration, duration/1000
        FROM use_app
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        start = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] and int(row[0]) > 0 else ''
        stop = datetime.datetime.fromtimestamp(int(row[1]) / 1000, datetime.timezone.utc) if row[1] and int(row[1]) > 0 else ''
        data_list.append((start, stop, row[2], row[3], row[4], row[5], row[6]))

    data_headers = (('Start Time', 'datetime'), ('Stop Time', 'datetime'), 'Timezone', 'App ID', 'APP Sub ID', 'Duration', 'Duration in Secs')
    return data_headers, data_list, source_path
