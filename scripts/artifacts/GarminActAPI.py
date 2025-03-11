# Get the activities from the Garmin API using the JSON extracted from the Garmin API
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_act_api(files_found, report_folder, seeker, wrap_text):

    logfunc("Processing data for Garmin Activity API")
    report = ArtifactHtmlReport('Activity API')
    report.start_artifact_report(report_folder, 'Activity API')
    report.add_script()
    data_headers = (
    'Activity ID', 'Start Time GMT', 'Activity Name', 'Description', 'Activity Type Key', 'Distance (m)', 'Duration (s)',
    'Elevation Gain', 'Elevation Loss', 'Average Speed', 'Max Speed', 'Start Latitude',
    'Start Longitude', 'Owner ID', 'Owner Name','Owner Profile Image URL Large', 'Calories', 'Average HR', 'Max HR',
    'Steps', 'vO2MaxValue')

    data_list = []
    #file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        activity_date = ''
        activity_json = []
        #Open JSON file
        # if decode error, try to decode with utf-8-sig
        try:
            with open(file, "r") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            with open(file, "r", encoding="latin-1") as f:
                data = json.load(f)

        if len(data) > 0:
            logfunc("Found Garmin Activity file")
            # Get Activity ID
            for data in data:
                activity_id = data['activityId']
                # Get Start Time GMT
                start_time_gmt = data['startTimeGMT']
                # Get Activity Name
                activity_name = data['activityName']
                # Get Description
                description = data['description']
                # Get Activity Type Key
                activity_type_key = data['activityType']['typeKey']
                # Get Distance
                distance = round(float(data['distance']), 2)
                # Get Duration
                duration = round(float(data['duration']), 2)
                # Get Elevation Gain
                if data['elevationGain'] is None:
                    elevation_gain = 0
                else:
                    elevation_gain = round(float(data['elevationGain']), 2)
                # Get Elevation Loss
                if data['elevationLoss'] is None:
                    elevation_loss = 0
                else:
                    elevation_loss = round(float(data['elevationLoss']), 2)
                # Get Average Speed
                if data['averageSpeed'] is None:
                    average_speed = 0
                else:
                    average_speed = round(float(data['averageSpeed']), 2)
                # Get Max Speed
                if data['maxSpeed'] is None:
                    max_speed = 0
                else:
                    max_speed = round(float(data['maxSpeed']), 2)
                # Get Start Latitude
                if data['startLatitude'] is None:
                    start_latitude = 0
                else:
                    start_latitude = round(float(data['startLatitude']), 2)
                # Get Start Longitude
                if data['startLongitude'] is None:
                    start_longitude = 0
                else:
                    start_longitude = round(float(data['startLongitude']), 2)
                # Get Owner ID
                owner_id = data['ownerId']
                # Get Owner Name
                owner_name = data['ownerFullName']
                # Get Owner Profile Image URL Large
                owner_profile_image_url_large = data['ownerProfileImageUrlLarge']
                # Get Calories
                calories = data['calories']
                # Get Average HR
                average_hr = data['averageHR']
                # Get Max HR
                max_hr = data['maxHR']
                # Get Steps
                steps = data['steps']
                # Get vO2MaxValue
                vO2MaxValue = data['vO2MaxValue']

                # extract date from startTimeGMT
                current_date = start_time_gmt.split(' ')[0]
                if current_date != activity_date:
                    activity_json.append({
                        'date': current_date,
                        'total': 1,
                    })
                    activity_date = current_date
                else:
                    # Change the total of the last element of the list
                    activity_json[-1]['total'] += 1

                data_list.append((activity_id, start_time_gmt, activity_name, description, activity_type_key, distance, duration,
                elevation_gain, elevation_loss, average_speed, max_speed, start_latitude, start_longitude, owner_id, owner_name,
                owner_profile_image_url_large, calories, average_hr, max_hr, steps, vO2MaxValue))

    report.add_heat_map(json.dumps(activity_json))
    report.filter_by_date('GarminActAPI', 1)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminActAPI')
    report.end_artifact_report()
    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts__ = {
    "GarminActAPI": (
        "Garmin-API",
        ('*/garmin.api/activities*'),
        get_act_api)
}
