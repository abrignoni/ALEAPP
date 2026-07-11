# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_weight": {
        "name": "GarminWeight",
        "description": "Get Information relative to the weight data in the database cache-database from the table weight in the Garmin Connect app",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2026-07-10",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "Newer Garmin Connect versions no longer populate cache-database; current app data lives in gcm_cache.db and garmin.api files (parsed by the GarminJson, GarminGcmJsonActivities, garmin and Garmin*API artifacts).",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_garmin_weight(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Weight")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute('''
            Select samplePk, "date", weight
            from weight
        ''')
        all_rows = cursor.fetchall()
    except sqlite3.OperationalError as ex:
        # Newer Garmin Connect versions restructured the cache-database
        logfunc(f'Unable to query the Garmin cache-database (unsupported schema version?): {ex}')
        all_rows = []
    db.close()
    logfunc(f"Found {len(all_rows)} weight entries")

    data_list = []
    for row in all_rows:
        date = datetime.datetime.fromtimestamp(int(row[1]) / 1000, datetime.timezone.utc) if row[1] else ''
        data_list.append((row[0], date, row[2]))

    data_headers = ('samplePk', ('Date', 'datetime'), 'Weight')
    return data_headers, data_list, source_path
