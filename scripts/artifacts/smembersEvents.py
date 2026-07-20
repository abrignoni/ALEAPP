# pylint: disable=W0613
__artifacts_v2__ = {
    "get_smembersEvents": {
        "name": "smembersEvents",
        "description": "Parses Samsung Members device events (created time, type, value and snapshot flag) from the com_pocketgeek_sdk database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/com.samsung.oh/databases/com_pocketgeek_sdk.db',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_smembersEvents(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT created_at, type, value, in_snapshot
        FROM device_events
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        created = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
        data_list.append((created, row[1], row[2], row[3]))

    data_headers = (('Created At', 'datetime'), 'Type', 'Value', 'Snapshot?')
    return data_headers, data_list, source_path
