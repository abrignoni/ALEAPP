# pylint: disable=W0613
__artifacts_v2__ = {
    "get_hr_api": {
        "name": "GarminHRAPI",
        "description": "Get Information related to the Heart Rate from the Garmin API using the JSON file extracted",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/garmin.api/heart_rate*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import json

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_hr_api(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Heart Rate API")
    data_list = []
    source_path = ''
    for file in files_found:
        file = str(file)
        source_path = file
        logfunc("Processing file: " + file)
        with open(file, "r", encoding='utf-8', errors='replace') as f:
            data = json.load(f)

        if len(data) > 0:
            payload = data['AllDayHR']['payload']
            date = payload['calendarDate']
            max_hr = payload['maxHeartRate'] if payload['maxHeartRate'] is not None else 'N/A'
            min_hr = payload['minHeartRate'] if payload['minHeartRate'] is not None else 'N/A'
            resting_hr = payload['restingHeartRate'] if payload['restingHeartRate'] is not None else 'N/A'
            average_hr = payload['lastSevenDaysAvgRestingHeartRate'] if payload['lastSevenDaysAvgRestingHeartRate'] is not None else 'N/A'
            data_list.append((date, max_hr, min_hr, resting_hr, average_hr))

    data_headers = ('Date', 'Max Hearth Rate', 'Min Hearth Rate', 'Resting Hearth Rate', 'Average Hearth Rate')
    return data_headers, data_list, source_path
