# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_sync": {
        "name": "Garmin - Sync",
        "description": "Get Information related to the sync process stored in the sync_cache database file",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin-Sync",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/sync_cache*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    }
}

# Get Information related to the sync process stored in the sync_cache database file
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_garmin_sync(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Sync")
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select
        device_info,
        audit_text,
        app_version,
        datetime("created_timestamp"/1000,'unixepoch')
        from device_sync_audit
    ''')

    all_rows = cursor.fetchall()
    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3]))

    db.close()

    data_headers = (
        'Device Info',
        'Audit Text',
        'App Version',
        ('Created Timestamp', 'datetime'),
    )
    return data_headers, data_list, source_path
