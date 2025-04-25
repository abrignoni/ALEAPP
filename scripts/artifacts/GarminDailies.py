# Get Information from the table user_daily_summary from the cache-database in the Garmin Connect App
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_dailies(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin User Dailies")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # SQL query for obtaining data from the table user_daily_summary
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    calendarDate, totalKilocalories, activeKilocalories, bmrKilocalories, wellnessActiveKilocalories, burnedKilocalories, consumedKilocalories, remainingKilocalories,
    totalSteps, totalDistanceMeters, wellnessDistanceMeters, highlyActiveSeconds, activeSeconds, moderateIntensityMinutes, floorsAscendedInMeters, floorsDescendedInMeters, floorsAscendedInMeters,
    floorsDescendedInMeters, minHeartRate, maxHeartRate, restingHeartRate, lastSevenDaysAvgRestingHeartRate, averageStressLevel, maxStressLevel, stressDuration,stressDuration, restStressDuration, activityStressDuration,
    uncategorizedStressDuration, totalStressDuration, lowStressDuration, mediumStressDuration, highStressDuration, stressPercentage, restStressPercentage, activityStressPercentage, uncategorizedStressPercentage,
    lowStressPercentage, mediumStressPercentage, highStressPercentage, bodyBatteryChargedValue, bodyBatteryDrainedValue, bodyBatteryHighestValue, bodyBatteryLowestValue, bodyBatteryMostRecentValue, hydrationValueInML,
    averageSpo2, latestSpo2
    from user_daily_summary
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries")
        report = ArtifactHtmlReport('Dailies')
        report.start_artifact_report(report_folder, 'Dailies')
        report.add_script()
        data_headers = ('Calendar Date', 'Total Kilocalories', 'Active Kilocalories', 'BMR Kilocalories', 'Wellness Active Kilocalories', 'Burned Kilocalories', 'Consumed Kilocalories', 'Remaining Kilocalories',
                        'Total Steps', 'Total Distance Meters', 'Wellness Distance Meters', 'Highly Active Seconds', 'Active Seconds', 'Moderate Intensity Minutes', 'Floors Ascended In Meters', 'Floors Descended In Meters',
                        'Floors Ascended In Meters', 'Floors Descended In Meters', 'Min Heart Rate', 'Max Heart Rate', 'Resting Heart Rate', 'Last Seven Days Avg Resting Heart Rate', 'Average Stress Level', 'Max Stress Level',
                        'Stress Duration', 'Stress Duration', 'Rest Stress Duration', 'Activity Stress Duration', 'Uncategorized Stress Duration', 'Total Stress Duration', 'Low Stress Duration', 'Medium Stress Duration',
                        'High Stress Duration', 'Stress Percentage', 'Rest Stress Percentage', 'Activity Stress Percentage', 'Uncategorized Stress Percentage', 'Low Stress Percentage', 'Medium Stress Percentage',
                        'High Stress Percentage', 'Body Battery Charged Value', 'Body Battery Drained Value', 'Body Battery Highest Value', 'Body Battery Lowest Value', 'Body Battery Most Recent Value', 'Hydration Value In ML',
                        'Average Spo2', 'Latest Spo2')
        data_list = []
        for row in all_rows:
           data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22],
                            row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44],
                            row[45], row[46], row[47]))

        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        table_id = 'Garmin_Dailies'
        report.filter_by_date(table_id, 0)

        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id)
        report.end_artifact_report()

        tsvname = f'Garmin - Dailies'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - Dailies'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Dailies data available')

    db.close()


__artifacts__ = {
    "GarminDailies": (
        "Garmin-Cache",
        ('*/com.garmin.android.apps.connectmobile/databases/cache-database*'),
        get_garmin_dailies)
}
