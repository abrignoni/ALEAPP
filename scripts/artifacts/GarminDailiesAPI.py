# Get Information related to the Daily summaries from the Garmin API using the JSON file extracted
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-28
# Version: 1.0
# Requirements: Python 3.7 or higher, json

import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_dailies_api(files_found, report_folder, seeker, wrap_text):
    fields = ['calendarDate', 'totalKilocalories', 'activeKilocalories', 'bmrKilocalories', 'wellnessActiveKilocalories', 'burnedKilocalories', 'consumedKilocalories', 'remainingKilocalories',
                'totalSteps', 'totalDistanceMeters', 'wellnessDistanceMeters', 'highlyActiveSeconds', 'activeSeconds', 'moderateIntensityMinutes', 'floorsAscendedInMeters', 'floorsDescendedInMeters',
                'floorsAscendedInMeters', 'floorsDescendedInMeters', 'minHeartRate', 'maxHeartRate', 'restingHeartRate', 'lastSevenDaysAvgRestingHeartRate', 'averageStressLevel', 'maxStressLevel',
                'stressDuration', 'stressDuration', 'restStressDuration', 'activityStressDuration', 'uncategorizedStressDuration', 'totalStressDuration', 'lowStressDuration', 'mediumStressDuration',
                'highStressDuration', 'stressPercentage', 'restStressPercentage', 'activityStressPercentage', 'uncategorizedStressPercentage', 'lowStressPercentage', 'mediumStressPercentage',
                'highStressPercentage', 'bodyBatteryChargedValue', 'bodyBatteryDrainedValue', 'bodyBatteryHighestValue', 'bodyBatteryLowestValue', 'bodyBatteryMostRecentValue', 'averageSpo2', 'latestSpo2']
    logfunc("Processing data for Dailies API")
    logfunc("Processing data for Dailies API")
    report = ArtifactHtmlReport('Dailies API')
    report.start_artifact_report(report_folder, 'Dailies API')
    report.add_script()
    data_headers = ('Calendar Date', 'Total Kilocalories', 'Active Kilocalories', 'BMR Kilocalories', 'Wellness Active Kilocalories', 'Burned Kilocalories', 'Consumed Kilocalories', 'Remaining Kilocalories',
                        'Total Steps', 'Total Distance Meters', 'Wellness Distance Meters', 'Highly Active Seconds', 'Active Seconds', 'Moderate Intensity Minutes', 'Floors Ascended In Meters', 'Floors Descended In Meters',
                        'Floors Ascended In Meters', 'Floors Descended In Meters', 'Min Heart Rate', 'Max Heart Rate', 'Resting Heart Rate', 'Last Seven Days Avg Resting Heart Rate', 'Average Stress Level', 'Max Stress Level',
                        'Stress Duration', 'Stress Duration', 'Rest Stress Duration', 'Activity Stress Duration', 'Uncategorized Stress Duration', 'Total Stress Duration', 'Low Stress Duration', 'Medium Stress Duration',
                        'High Stress Duration', 'Stress Percentage', 'Rest Stress Percentage', 'Activity Stress Percentage', 'Uncategorized Stress Percentage', 'Low Stress Percentage', 'Medium Stress Percentage',
                        'High Stress Percentage', 'Body Battery Charged Value', 'Body Battery Drained Value', 'Body Battery Highest Value', 'Body Battery Lowest Value', 'Body Battery Most Recent Value',
                        'Average Spo2', 'Latest Spo2')
    data_list = []
    # file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        # Open JSON file
        with open(file, "r") as f:
            data = json.load(f)

        if len(data) > 0:
            data_row = []
            logfunc("Found Garmin Daily File")
            # Get calendar date
            for field in fields:
                if data['UserDailySummary']['payload'][field] is not None:
                    data_row.append(data['UserDailySummary']['payload'][field])
                else:
                    data_row.append('N/A')
            data_list.append((row for row in data_row))
    report.filter_by_date('GarminDailyAPI', 0)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminDailyAPI')
    report.end_artifact_report()
    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts__ = {
    "GarminDailiesAPI": (
        "Garmin-API",
        ('*/garmin.api/daily*'),
        get_dailies_api)
}