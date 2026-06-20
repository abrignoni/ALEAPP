# pylint: disable=W0613
__artifacts_v2__ = {
    "get_dailies_api": {
        "name": "GarminDailiesAPI",
        "description": "Get Information related to the Daily summaries from the Garmin API using the JSON file extracted",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-28",
        "last_update_date": "2023-02-28",
        "requirements": "Python 3.7 or higher, json",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/garmin.api/daily*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import json

from scripts.ilapfuncs import artifact_processor, logfunc

# (field, header) pairs - duplicates from the original list removed so LAVA column names stay unique
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
    ('averageSpo2', 'Average Spo2'),
    ('latestSpo2', 'Latest Spo2'),
]


@artifact_processor
def get_dailies_api(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Dailies API")
    data_list = []
    source_path = ''
    for file in files_found:
        file = str(file)
        source_path = file
        logfunc("Processing file: " + file)
        with open(file, "r", encoding='utf-8', errors='replace') as f:
            data = json.load(f)

        if len(data) > 0:
            payload = data['UserDailySummary']['payload']
            data_row = [payload[field] if payload.get(field) is not None else 'N/A' for field, _ in FIELDS]
            data_list.append(tuple(data_row))

    data_headers = tuple(header for _, header in FIELDS)
    return data_headers, data_list, source_path
