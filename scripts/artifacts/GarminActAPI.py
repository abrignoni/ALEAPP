# pylint: disable=W0613
__artifacts_v2__ = {
    "get_act_api": {
        "name": "GarminActAPI",
        "description": "Get Information related to activities from the Garmin API using the JSON file extracted",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/garmin.api/activity*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import json

from scripts.ilapfuncs import artifact_processor, logfunc


def _round2(value):
    return round(float(value), 2) if value is not None else 0


@artifact_processor
def get_act_api(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Activity API")
    data_list = []
    source_path = ''
    for file in files_found:
        file = str(file)
        source_path = file
        logfunc("Processing file: " + file)
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            with open(file, "r", encoding="latin-1") as f:
                data = json.load(f)

        for item in data:
            data_list.append((
                item['activityId'],
                item['startTimeGMT'],
                item['activityName'],
                item['description'],
                item['activityType']['typeKey'],
                _round2(item['distance']),
                _round2(item['duration']),
                _round2(item['elevationGain']),
                _round2(item['elevationLoss']),
                _round2(item['averageSpeed']),
                _round2(item['maxSpeed']),
                _round2(item['startLatitude']),
                _round2(item['startLongitude']),
                item['ownerId'],
                item['ownerFullName'],
                item['ownerProfileImageUrlLarge'],
                item['calories'],
                item['averageHR'],
                item['maxHR'],
                item['steps'],
                item['vO2MaxValue'],
            ))

    data_headers = (
        'Activity ID', 'Start Time GMT', 'Activity Name', 'Description', 'Activity Type Key', 'Distance (m)',
        'Duration (s)', 'Elevation Gain', 'Elevation Loss', 'Average Speed', 'Max Speed', 'Start Latitude',
        'Start Longitude', 'Owner ID', 'Owner Name', 'Owner Profile Image URL Large', 'Calories', 'Average HR',
        'Max HR', 'Steps', 'vO2MaxValue')
    return data_headers, data_list, source_path
