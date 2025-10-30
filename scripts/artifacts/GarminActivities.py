# Get Information relative to the user activities that are present in the database (cache-database) from the Garmin Connect app, the activities are stored in two different tables (activities_details and activities_summaries)
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher and json
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Activities")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    #This query is selecting all columns (*) from a subquery, which is a combination of two separate SELECT statements
    # joined together with a UNION operator. The first SELECT statement is joining the "activity_details" table with the
    # "activity_summaries" table on the "activityId" column, and the second SELECT statement is doing the reverse, joining
    # the "activity_summaries" table with the "activity_details" table on the "activityId" column. The subquery is then aliased as
    # "t" and a group by is applied on the "activityId" column. This query is likely used to combine information from both the "activity_details"
    # and "activity_summaries" tables, and group the results by "activityId" to ensure that there are no duplicate rows with the same activityId.
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from (
        SELECT activity_details.activityId, abd.json, datetime("lastUpdated"/1000, 'unixepoch'), datetime("lastUpdate"/1000, 'unixepoch'), calendarDate, activityName, activity_details.startTimeGMT, activityTypeKey, distance, duration, movingDuration, elevationGain, elevationLoss, averageSpeed, maxSpeed, startLatitude, startLongitude, ownerId, ownerProfileImageUrlLarge, calories, averageHR, maxHR, averageRunningCadenceInStepsPerMinute, maxRunningCadenceInStepsPerMinute, steps
        from activity_details
        LEFT JOIN activity_summaries abd on activity_details.activityId = abd.activityId
        UNION
        SELECT activity_summaries.activityId, json, datetime("lastUpdated"/1000, 'unixepoch'), datetime("lastUpdate"/1000, 'unixepoch'), calendarDate, activityName, acd.startTimeGMT, activityTypeKey, distance, duration, movingDuration, elevationGain, elevationLoss, averageSpeed, maxSpeed, startLatitude, startLongitude, ownerId, ownerProfileImageUrlLarge, calories, averageHR, maxHR, averageRunningCadenceInStepsPerMinute, maxRunningCadenceInStepsPerMinute, steps
        from activity_summaries
        LEFT JOIN activity_details acd on activity_summaries.activityId = acd.activityId
    ) as t
    group by activityId;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} Garmin Activities")
        report = ArtifactHtmlReport('Activities')
        report.start_artifact_report(report_folder, 'Activities')
        report.add_script()
        data_headers = ('Activity ID', 'Start Time GMT', 'Last Updated', 'Activity Name', 'Activity Type Key', 'Distance', 'Duration', 'Moving Duration', 'Elevation Gain', 'Elevation Loss', 'Average Speed', 'Max Speed', 'Start Latitude', 'Start Longitude', 'Owner ID', 'Owner Profile Image URL Large', 'Calories', 'Average HR', 'Max HR', 'Average Running Cadence In Steps Per Minute', 'Max Running Cadence In Steps Per Minute', 'Steps', 'vO2MaxValue')
        data_list = []
        activity_date = ''
        activity_json = []
        for row in all_rows:
            # If the second column of the row is not null, then the row is from the "activity_summaries" table, the data is then parsed from the json column
            if row[1] is not None:
                activityJson = json.loads(row[1])
                activityId = row[0]
                lastUpdated = row[3]
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
            # If the second column of the row is null, then the row is from the "activity_details" table, the data is obtained from the columns
            else:
                activityId = row[0]
                lastUpdated = row[2]
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

            # extract date from startTimeGMT
            current_date = startTimeGMT.split(' ')[0]
            if current_date != activity_date:
                activity_json.append({
                    'date': current_date,
                    'total': 1,
                })
                activity_date = current_date
            else:
                # Change the total of the last element of the list
                activity_json[-1]['total'] += 1

            data_list.append((activityId, startTimeGMT, lastUpdated, activityName, activityTypeKey, distance, duration, movingDuration, elevationGain, elevationLoss, averageSpeed, maxSpeed, startLatitude, startLongitude, ownerId, ownerProfileImageURLLarge, calories, averageHR, maxHR, averageRunningCadenceInStepsPerMinute, maxRunningCadenceInStepsPerMinute, steps, vO2MaxValue))

        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        tableID = 'garmin_activities'
        report.add_heat_map(json.dumps(activity_json))
        report.filter_by_date(tableID, 1)

        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=tableID)
        report.end_artifact_report()

        tsvname = f'Garmin - Activities'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - Activities'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Activities data available')

    db.close()


__artifacts__ = {
    "GarminActivities": (
        "Garmin-Cache",
        ('*/com.garmin.android.apps.connectmobile/databases/cache-database*'),
        get_garmin_activities)
}