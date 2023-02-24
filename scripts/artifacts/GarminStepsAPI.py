# Get Information related to the Heart Rate from the Garmin API using the JSON file extracted
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_steps_api(files_found, report_folder, seeker, wrap_text):

    logfunc("Processing data for Steps API")
    report = ArtifactHtmlReport('Steps API')
    report.start_artifact_report(report_folder, 'Steps API')
    report.add_script()
    data_headers = ('Date', 'Steps', 'Calories', 'Distance', 'Floors Asc', 'Floors Desc', 'Graphic')
    data_list = []
    #file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        #Open JSON file
        with open(file, "r") as f:
            data = json.load(f)

        if len(data) > 0:
            logfunc("Found Garmin Steps file")
            # Get calendar date
            date = data['UserDailySummary']['payload']['calendarDate']
            # Get max hearth rate if none set to 'N/A'
            if data['UserDailySummary']['payload']['totalSteps'] is not None:
                steps = data['UserDailySummary']['payload']['totalSteps']
            else:
                steps = 'N/A'
            # Get min hearth rate
            if data['UserDailySummary']['payload']['totalKilocalories'] is not None:
                cal = data['UserDailySummary']['payload']['totalKilocalories']
            else:
                cal = 'N/A'
            # Get resting hearth rate
            if data['UserDailySummary']['payload']['totalDistanceMeters'] is not None:
                distance = data['UserDailySummary']['payload']['totalDistanceMeters']
            else:
                distance = 'N/A'
            # Get average hearth rate
            if data['UserDailySummary']['payload']['floorsAscended'] is not None:
                floors_asc = int(data['UserDailySummary']['payload']['floorsAscended'])
            else:
                floors_asc = 'N/A'
            # Get floors descended
            if data['UserDailySummary']['payload']['floorsDescended'] is not None:
                floors_desc = int(data['UserDailySummary']['payload']['floorsDescended'])
            else:
                floors_desc = 'N/A'
            # check if data['AllDayHR']['payload']['heartRateValues'] exists
            if data['DailyMovement']['payload']['movementValues'] is not None:
                mv_values = json.dumps(data['DailyMovement']['payload']['movementValues'])
                # convert to list
                mv_values = mv_values.replace('[', '').replace(']', '').split(',')
                #logfunc(str(hr_values))
                x_list = []
                y_list = []
                # from hr_values get x and y values
                for i in range(len(mv_values)):
                    if i % 2 == 0:
                        x_list.append(float(mv_values[i]))
                    else:
                        #if value is null set to 0
                        if 'null' in mv_values[i]:
                            y_list.append(0)
                        else:
                            y_list.append(float(mv_values[i]))
                #logfunc(str(x_list))
                #logfunc(str(y_list))
                mv_btn = '<button class="btn btn-light btn-sm" onclick="createLineChart(\'' + str(y_list) + '\', \'' + str(x_list) + '\', true, \'Daily Movement\', \'Time\', \'Movement\')">View</button>'
            else:
                mv_btn = 'N/A'
            data_list.append((date, steps, cal, distance, floors_asc, floors_desc, mv_btn))
    report.filter_by_date('GarminStepsAPI', 0)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminStepsAPI')
    report.add_chart()
    report.end_artifact_report()
    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts__ = {
    "GarminStepsAPI": (
        "Garmin-API",
        ('*/garmin.api/steps*'),
        get_steps_api)
}
