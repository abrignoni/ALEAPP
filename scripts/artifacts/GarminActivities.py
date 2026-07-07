# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_activities": {
        "name": "GarminActivities",
        "description": "Get Information related to Garmin activities from the cache-database",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_garmin_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Activities")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    # Combine activity_details and activity_summaries (grouped by activityId to drop duplicates)
    cursor.execute('''
    Select *
    from (
        SELECT activity_details.activityId, abd.json, lastUpdated, lastUpdate, calendarDate, activityName, activity_details.startTimeGMT, activityTypeKey, distance, duration, movingDuration, elevationGain, elevationLoss, averageSpeed, maxSpeed, startLatitude, startLongitude, ownerId, ownerProfileImageUrlLarge, calories, averageHR, maxHR, averageRunningCadenceInStepsPerMinute, maxRunningCadenceInStepsPerMinute, steps
        from activity_details
        LEFT JOIN activity_summaries abd on activity_details.activityId = abd.activityId
        UNION
        SELECT activity_summaries.activityId, json, lastUpdated, lastUpdate, calendarDate, activityName, acd.startTimeGMT, activityTypeKey, distance, duration, movingDuration, elevationGain, elevationLoss, averageSpeed, maxSpeed, startLatitude, startLongitude, ownerId, ownerProfileImageUrlLarge, calories, averageHR, maxHR, averageRunningCadenceInStepsPerMinute, maxRunningCadenceInStepsPerMinute, steps
        from activity_summaries
        LEFT JOIN activity_details acd on activity_summaries.activityId = acd.activityId
    ) as t
    group by activityId;
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} Garmin Activities")

    data_list = []
    for row in all_rows:
        if row[1] is not None:
            # row is from activity_summaries; parse the json column
            activityJson = json.loads(row[1])
            activityId = row[0]
            lastUpdated = _ms_to_utc(row[3])
            activityName = activityJson['activityName']
            startTimeGMT = activityJson['startTimeGMT']
            activityTypeKey = activityJson['activityType']['typeKey']
            distance = activityJson['distance']
            duration = activityJson['duration']
            movingDuration = activityJson['movingDuration']
            elevationGain = activityJson['elevationGain']
            elevationLoss = activityJson['elevationLoss']
            averageSpeed = activityJson['averageSpeed']
            maxSpeed = activityJson['maxSpeed']
            startLatitude = activityJson['startLatitude']
            startLongitude = activityJson['startLongitude']
            ownerId = activityJson['ownerId']
            ownerProfileImageURLLarge = activityJson['ownerProfileImageUrlLarge']
            calories = activityJson['calories']
            averageHR = activityJson['averageHR']
            maxHR = activityJson['maxHR']
            averageRunningCadenceInStepsPerMinute = activityJson['averageRunningCadenceInStepsPerMinute']
            maxRunningCadenceInStepsPerMinute = activityJson['maxRunningCadenceInStepsPerMinute']
            steps = activityJson['steps']
            vO2MaxValue = activityJson['vO2MaxValue']
        else:
            # row is from activity_details; use the columns
            activityId = row[0]
            lastUpdated = _ms_to_utc(row[2])
            activityName = row[5]
            startTimeGMT = row[6]
            activityTypeKey = row[7]
            distance = row[8]
            duration = row[9]
            movingDuration = row[10]
            elevationGain = row[11]
            elevationLoss = row[12]
            averageSpeed = row[13]
            maxSpeed = row[14]
            startLatitude = row[15]
            startLongitude = row[16]
            ownerId = row[17]
            ownerProfileImageURLLarge = row[18]
            calories = row[19]
            averageHR = row[20]
            maxHR = row[21]
            averageRunningCadenceInStepsPerMinute = row[22]
            maxRunningCadenceInStepsPerMinute = row[23]
            steps = row[24]
            vO2MaxValue = None

        data_list.append((activityId, startTimeGMT, lastUpdated, activityName, activityTypeKey, distance, duration,
                          movingDuration, elevationGain, elevationLoss, averageSpeed, maxSpeed, startLatitude,
                          startLongitude, ownerId, ownerProfileImageURLLarge, calories, averageHR, maxHR,
                          averageRunningCadenceInStepsPerMinute, maxRunningCadenceInStepsPerMinute, steps, vO2MaxValue))

    data_headers = ('Activity ID', 'Start Time GMT', ('Last Updated', 'datetime'), 'Activity Name', 'Activity Type Key',
                    'Distance', 'Duration', 'Moving Duration', 'Elevation Gain', 'Elevation Loss', 'Average Speed',
                    'Max Speed', 'Start Latitude', 'Start Longitude', 'Owner ID', 'Owner Profile Image URL Large',
                    'Calories', 'Average HR', 'Max HR', 'Average Running Cadence In Steps Per Minute',
                    'Max Running Cadence In Steps Per Minute', 'Steps', 'vO2MaxValue')
    return data_headers, data_list, source_path
