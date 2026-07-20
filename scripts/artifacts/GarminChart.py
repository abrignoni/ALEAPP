__artifacts_v2__ = {
    "get_garmin_chart": {
        "name": "GarminCharts",
        "description": "Get Information from the table activity_charts and activity_details in the database cache-database from Garmin Connect",
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


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_garmin_chart(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Garmin Chart")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute('''
            Select
            activity_details.activityId,
            activity_details.lastUpdated,
            activityName,
            startTimeGMT,
            activityTypeKey,
            round(distance, 0),
            round(duration/60, 0),
            steps,
            acd.lastUpdated,
            chartType,
            chartXList,
            chartYList
            from activity_details
            left join activity_chart_data acd on activity_details.activityId = acd.activityId
            where activity_details.activityId = acd.activityId
        ''')
        all_rows = cursor.fetchall()
    except sqlite3.OperationalError as ex:
        # Newer Garmin Connect versions restructured the cache-database
        logfunc(f'Unable to query the Garmin cache-database (unsupported schema version?): {ex}')
        all_rows = []
    db.close()
    logfunc(f'Found {len(all_rows)} activity details')

    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[3], _ms_to_utc(row[1]), row[2], row[4], row[5], row[6], row[7],
                          _ms_to_utc(row[8]), row[9], row[10], row[11]))

    data_headers = ('Activity ID', 'Start Time GMT', ('Activity Last Updated', 'datetime'), 'Activity Name',
                    'Activity Type Key', 'Distance', 'Duration', 'Steps', ('Chart Last Updated', 'datetime'),
                    'Chart Type', 'Chart X List', 'Chart Y List')
    return data_headers, data_list, source_path
