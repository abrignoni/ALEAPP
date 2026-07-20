__artifacts_v2__ = {
    "get_sleep_api": {
        "name": "GarminSleepAPI",
        "description": "Get Information related to Garmin Sleep API",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json and datetime",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/garmin.api/sleep*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import datetime
import json

from scripts.ilapfuncs import artifact_processor, logfunc


def _seconds_to_hms(value):
    if value is None:
        return 'N/A'
    return str(datetime.timedelta(seconds=value))


def _ms_to_time(value):
    if value is None:
        return 'N/A'
    return datetime.datetime.fromtimestamp(value / 1000, datetime.timezone.utc).strftime('%H:%M:%S')


@artifact_processor
def get_sleep_api(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Garmin Sleep API")
    source_path = str(files_found[0])
    logfunc("Processing file: " + source_path)
    with open(source_path, "r", encoding='utf-8', errors='replace') as f:
        data = json.load(f)

    data_list = []
    for i in data:
        dto = i['dailySleepDTO']
        date = dto['calendarDate']
        sleep_time = _seconds_to_hms(dto['sleepTimeSeconds'])
        start_time = _ms_to_time(dto['sleepStartTimestampGMT'])
        end_time = _ms_to_time(dto['sleepEndTimestampGMT'])
        deep_sleep = _seconds_to_hms(dto['deepSleepSeconds'])
        light_sleep = _seconds_to_hms(dto['lightSleepSeconds'])
        rem_sleep = _seconds_to_hms(dto['remSleepSeconds'])
        awake_sleep = _seconds_to_hms(dto['awakeSleepSeconds'])
        average_spo2 = dto.get('averageSpO2Value', 'N/A')
        lowest_spo2 = dto.get('lowestSpO2Value', 'N/A')
        highest_spo2 = dto.get('highestSpO2Value', 'N/A')
        data_list.append((date, sleep_time, start_time, end_time, deep_sleep, light_sleep, rem_sleep,
                          awake_sleep, average_spo2, lowest_spo2, highest_spo2))

    data_headers = ('Date', 'Sleep Time', 'Start Time', 'End Time', 'Deep Sleep', 'Light Sleep', 'REM Sleep',
                    'Awake Sleep', 'Average SPo2', 'Lowest SPo2', 'Highest SPo2')
    return data_headers, data_list, source_path
