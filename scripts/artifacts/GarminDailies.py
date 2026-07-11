# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_dailies": {
        "name": "GarminDailies",
        "description": "Get Information from the table user_daily_summary from the cache-database in the Garmin Connect App",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2026-07-10",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

# (column, header) pairs - duplicates from the original query/headers removed so LAVA column names stay unique
FIELDS = [
    ('calendarDate', 'Calendar Date'),
    ('totalKilocalories', 'Total Kilocalories'),
    ('activeKilocalories', 'Active Kilocalories'),
    ('bmrKilocalories', 'BMR Kilocalories'),
    ('wellnessActiveKilocalories', 'Wellness Active Kilocalories'),
    ('burnedKilocalories', 'Burned Kilocalories'),
    ('consumedKilocalories', 'Consumed Kilocalories'),
    ('remainingKilocalories', 'Remaining Kilocalories'),
    ('totalSteps', 'Total Steps'),
    ('totalDistanceMeters', 'Total Distance Meters'),
    ('wellnessDistanceMeters', 'Wellness Distance Meters'),
    ('highlyActiveSeconds', 'Highly Active Seconds'),
    ('activeSeconds', 'Active Seconds'),
    ('moderateIntensityMinutes', 'Moderate Intensity Minutes'),
    ('floorsAscendedInMeters', 'Floors Ascended In Meters'),
    ('floorsDescendedInMeters', 'Floors Descended In Meters'),
    ('minHeartRate', 'Min Heart Rate'),
    ('maxHeartRate', 'Max Heart Rate'),
    ('restingHeartRate', 'Resting Heart Rate'),
    ('lastSevenDaysAvgRestingHeartRate', 'Last Seven Days Avg Resting Heart Rate'),
    ('averageStressLevel', 'Average Stress Level'),
    ('maxStressLevel', 'Max Stress Level'),
    ('stressDuration', 'Stress Duration'),
    ('restStressDuration', 'Rest Stress Duration'),
    ('activityStressDuration', 'Activity Stress Duration'),
    ('uncategorizedStressDuration', 'Uncategorized Stress Duration'),
    ('totalStressDuration', 'Total Stress Duration'),
    ('lowStressDuration', 'Low Stress Duration'),
    ('mediumStressDuration', 'Medium Stress Duration'),
    ('highStressDuration', 'High Stress Duration'),
    ('stressPercentage', 'Stress Percentage'),
    ('restStressPercentage', 'Rest Stress Percentage'),
    ('activityStressPercentage', 'Activity Stress Percentage'),
    ('uncategorizedStressPercentage', 'Uncategorized Stress Percentage'),
    ('lowStressPercentage', 'Low Stress Percentage'),
    ('mediumStressPercentage', 'Medium Stress Percentage'),
    ('highStressPercentage', 'High Stress Percentage'),
    ('bodyBatteryChargedValue', 'Body Battery Charged Value'),
    ('bodyBatteryDrainedValue', 'Body Battery Drained Value'),
    ('bodyBatteryHighestValue', 'Body Battery Highest Value'),
    ('bodyBatteryLowestValue', 'Body Battery Lowest Value'),
    ('bodyBatteryMostRecentValue', 'Body Battery Most Recent Value'),
    ('hydrationValueInML', 'Hydration Value In ML'),
    ('averageSpo2', 'Average Spo2'),
    ('latestSpo2', 'Latest Spo2'),
]


@artifact_processor
def get_garmin_dailies(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin User Dailies")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(f'''
            SELECT {", ".join(col for col, _ in FIELDS)}
            from user_daily_summary
        ''')
        all_rows = cursor.fetchall()
    except sqlite3.OperationalError as ex:
        # Newer Garmin Connect versions restructured the cache-database
        logfunc(f'Unable to query the Garmin cache-database (unsupported schema version?): {ex}')
        all_rows = []
    db.close()
    logfunc(f"Found {len(all_rows)} entries")

    data_list = [tuple(row) for row in all_rows]
    data_headers = tuple(header for _, header in FIELDS)
    return data_headers, data_list, source_path
