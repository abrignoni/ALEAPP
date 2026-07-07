# pylint: disable=W0613
__artifacts_v2__ = {
    "get_installedappsLibrary": {
        "name": "InstalledappsLibrary",
        "description": "",
        "author": "",
        "creation_date": "2020-03-01",
        "last_update_date": "2020-03-01",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.android.vending/databases/library.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_installedappsLibrary(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('library.db'):
            continue

        user = Path(file_found).parts[-4]
        if user == 'data':
            user = '0'

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT purchase_time, account, doc_id
            FROM ownership
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            purchase_time = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((user, purchase_time, row[1], row[2]))

    data_headers = ('User', ('Purchase Time', 'datetime'), 'Account', 'Doc ID')
    return data_headers, data_list, source_path
