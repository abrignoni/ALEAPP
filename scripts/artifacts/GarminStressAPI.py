__artifacts_v2__ = {
    "get_stress_api": {
        "name": "GarminStressAPI",
        "description": "Get Information from Garmin Stress API",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json and datetime",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/garmin.api/stress*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

# Requires extracting Garmin API data using https://github.com/labcif/Garmin-Connect-API-Extractor

import json

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_stress_api(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Stress API")
    data_list = []
    source_path = ''
    for file in files_found:
        file = str(file)
        source_path = file
        logfunc("Processing file: " + file)
        with open(file, "r", encoding='utf-8', errors='replace') as f:
            data_file = json.load(f)

        if len(data_file) > 0:
            for data in data_file:
                date = data['calendarDate']
                values = data['values']
                if values['overallStressLevel'] == -1:
                    stress_level = 'N/A'
                else:
                    stress_level = values['overallStressLevel']
                high_stress_duration = values['highStressDuration'] if values['highStressDuration'] is not None else 'N/A'
                medium_stress_duration = values['mediumStressDuration'] if values['mediumStressDuration'] is not None else 'N/A'
                low_stress_duration = values['lowStressDuration'] if values['lowStressDuration'] is not None else 'N/A'
                rest_stress_duration = values['restStressDuration'] if values['restStressDuration'] is not None else 'N/A'
                data_list.append((date, stress_level, high_stress_duration, medium_stress_duration, low_stress_duration, rest_stress_duration))

    data_headers = ('Date', 'Stress Level', 'High Stress Duration', 'Medium Stress Duration', 'Low Stress Duration', 'Rest Stress Duration')
    return data_headers, data_list, source_path
