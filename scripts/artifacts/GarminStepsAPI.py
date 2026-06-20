# pylint: disable=W0613
__artifacts_v2__ = {
    "get_steps_api": {
        "name": "GarminStepsAPI",
        "description": "Get Information related to the daily steps from the Garmin API using the JSON file extracted",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/garmin.api/steps*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import json

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_steps_api(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Steps API")
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
            date = payload['calendarDate']
            steps = payload['totalSteps'] if payload['totalSteps'] is not None else 'N/A'
            cal = payload['totalKilocalories'] if payload['totalKilocalories'] is not None else 'N/A'
            distance = payload['totalDistanceMeters'] if payload['totalDistanceMeters'] is not None else 'N/A'
            floors_asc = int(payload['floorsAscended']) if payload['floorsAscended'] is not None else 'N/A'
            floors_desc = int(payload['floorsDescended']) if payload['floorsDescended'] is not None else 'N/A'
            data_list.append((date, steps, cal, distance, floors_asc, floors_desc))

    data_headers = ('Date', 'Steps', 'Calories', 'Distance', 'Floors Asc', 'Floors Desc')
    return data_headers, data_list, source_path
