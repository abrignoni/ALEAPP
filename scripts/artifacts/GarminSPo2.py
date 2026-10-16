__artifacts_v2__ = {
    "get_garmin_spo2": {
        "name": "GarminSPO2",
        "description": "Reads the acclimation_pulse_ox_details table of the Garmin Connect cache-database. Rows with no spo2Value are not reported. spo2Value and spo2ValueAverage are reported separately without fallback; timestamps are as stored.",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-02-24",
        "last_update_date": "2026-10-06",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "Whether a given Garmin Connect version still populates cache-database is not "
                 "established here; gcm_cache.db and garmin.api files are parsed by the "
                 "GarminJson, GarminGcmJsonActivities, garmin and Garmin*API artifacts. "
                 "The registered Pixel 7a cache-database lacks acclimation_pulse_ox_details, "
                 "so its zero count reflects an unsupported schema, not an empty SpO2 table. "
                 "Stored value and average remain distinct; no unit or additional meaning is inferred.",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_garmin_spo2(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Garmin Pulse Ox details")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')
                   and not str(x).endswith('journal')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute('''
            SELECT
            userProfilePk,
            startTimestampGMT,
            endTimestampGMT,
            spo2Value,
            spo2ValueAverage,
            spo2ValuesArray
            from acclimation_pulse_ox_details
            where spo2Value is not null
        ''')
        all_rows = cursor.fetchall()
    except sqlite3.OperationalError as ex:
        # Newer Garmin Connect versions restructured the cache-database
        logfunc(f'Unable to query the Garmin cache-database (unsupported schema version?): {ex}')
        all_rows = []
    db.close()
    logfunc(f'Found {len(all_rows)} Garmin Pulse Ox details')

    data_list = []
    for row in all_rows:
        data_list.append((row[1], row[2], row[0], row[3], row[4], row[5]))

    data_headers = ('Start Timestamp GMT', 'End Timestamp GMT', 'User Profile PK',
                    'SpO2 Value (as stored)', 'SpO2 Value Average (as stored)', 'SPO2 Values Array')
    return data_headers, data_list, source_path
