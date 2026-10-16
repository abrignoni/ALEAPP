__artifacts_v2__ = {
    "get_sleep_api": {
        "name": "GarminSleepAPI",
        "description": "Daily sleep records (dailySleepDTO) from the sleep JSON files in a garmin.api folder, with the sleep start and end as UTC date and time.",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-02-24",
        "last_update_date": "2026-10-04",
        "requirements": "Python 3.7 or higher, json and datetime",
        "category": "Garmin",
        "notes": "The garmin.api folder is written by the Garmin-Connect-API-Extractor tool named in this module, "
                 "not by the app on the device. Every matched sleep file is read, one row per entry of each "
                 "file. Start Time and End Time are read from sleepStartTimestampGMT and "
                 "sleepEndTimestampGMT as milliseconds since 1970-01-01 UTC and shown as a full UTC date and time. "
                 "The field names state GMT; that the stored values are UTC was not checked against a device, "
                 "and the 22 zip archives in the Android corpus registry hold no garmin.api folder, so this "
                 "artifact has not been run on a registered corpus. Date is calendarDate as stored, a date "
                 "with no zone, and can differ from the UTC date of Start Time. A missing or unreadable "
                 "timestamp leaves its cell blank.",
        "paths": ('*/garmin.api/sleep*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import datetime
import json
import os

from scripts.ilapfuncs import artifact_processor, logfunc


def _seconds_to_hms(value):
    if value is None:
        return 'N/A'
    return str(datetime.timedelta(seconds=value))


def _ms_to_utc(value):
    # Milliseconds since the Unix epoch, returned as an aware UTC datetime so the
    # date is kept. Added to the epoch so a value the platform cannot convert
    # leaves the cell blank instead of ending the artifact.
    if value is None:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except (TypeError, ValueError, OverflowError):
        return ''


@artifact_processor
def get_sleep_api(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Garmin Sleep API")
    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        logfunc("Processing file: " + context.get_relative_path(file_found))
        try:
            with open(file_found, "r", encoding='utf-8', errors='replace') as f:
                data = json.load(f)
        except (OSError, ValueError) as ex:
            logfunc(f"Garmin Sleep API - could not read {context.get_relative_path(file_found)}: {ex}")
            continue
        sources.append(context.get_relative_path(file_found))

        for i in data:
            dto = i['dailySleepDTO']
            date = dto['calendarDate']
            sleep_time = _seconds_to_hms(dto['sleepTimeSeconds'])
            start_time = _ms_to_utc(dto['sleepStartTimestampGMT'])
            end_time = _ms_to_utc(dto['sleepEndTimestampGMT'])
            deep_sleep = _seconds_to_hms(dto['deepSleepSeconds'])
            light_sleep = _seconds_to_hms(dto['lightSleepSeconds'])
            rem_sleep = _seconds_to_hms(dto['remSleepSeconds'])
            awake_sleep = _seconds_to_hms(dto['awakeSleepSeconds'])
            average_spo2 = dto.get('averageSpO2Value', 'N/A')
            lowest_spo2 = dto.get('lowestSpO2Value', 'N/A')
            highest_spo2 = dto.get('highestSpO2Value', 'N/A')
            data_list.append((start_time, end_time, date, sleep_time, deep_sleep, light_sleep, rem_sleep,
                              awake_sleep, average_spo2, lowest_spo2, highest_spo2))

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Date', 'Sleep Time', 'Deep Sleep',
                    'Light Sleep', 'REM Sleep', 'Awake Sleep', 'Average SPo2', 'Lowest SPo2', 'Highest SPo2')
    return data_headers, data_list, '\n'.join(sources)
