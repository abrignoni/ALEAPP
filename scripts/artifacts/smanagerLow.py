# pylint: disable=W0613
__artifacts_v2__ = {
    "get_smanagerLow": {
        "name": "smanagerLow",
        "description": "Parses app usage sessions logged by the Samsung low-power context service (start and end time, package and timestamps) from the lowpowercontext-system database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/com.samsung.android.sm/databases/lowpowercontext-system-db',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_smanagerLow(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT start_time, end_time, id, package_name, uploaded, created_at, modified_at
        FROM usage_log
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1]), row[2], row[3], row[4], _ms_to_utc(row[5]), _ms_to_utc(row[6])))

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'ID', 'Package Name', 'Uploaded?', ('Created', 'datetime'), ('Modified', 'datetime'))
    return data_headers, data_list, source_path
