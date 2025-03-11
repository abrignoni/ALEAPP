# Get Information related to the Heart Rate from the Garmin API using the JSON file extracted
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_hr_api(files_found, report_folder, seeker, wrap_text):

    logfunc("Processing data for Heart Rate API")
    report = ArtifactHtmlReport('Heart Rate API')
    report.start_artifact_report(report_folder, 'Heart Rate API')
    report.add_script()
    data_headers = ('Date', 'Max Hearth Rate', 'Min Hearth Rate', 'Resting Hearth Rate', 'Average Hearth Rate', 'Graphic')
    data_list = []
    #file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        #Open JSON file
        with open(file, "r") as f:
            data = json.load(f)

        if len(data) > 0:
            logfunc("Found Garmin Presistent file")
            # Get calendar date
            date = data['AllDayHR']['payload']['calendarDate']
            # Get max hearth rate if none set to 'N/A'
            if data['AllDayHR']['payload']['maxHeartRate'] is not None:
                max_hr = data['AllDayHR']['payload']['maxHeartRate']
            else:
                max_hr = 'N/A'
            # Get min hearth rate
            if data['AllDayHR']['payload']['minHeartRate'] is not None:
                min_hr = data['AllDayHR']['payload']['minHeartRate']
            else:
                min_hr = 'N/A'
            # Get resting hearth rate
            if data['AllDayHR']['payload']['restingHeartRate'] is not None:
                resting_hr = data['AllDayHR']['payload']['restingHeartRate']
            else:
                resting_hr = 'N/A'
            # Get average hearth rate
            if data['AllDayHR']['payload']['lastSevenDaysAvgRestingHeartRate'] is not None:
                average_hr = data['AllDayHR']['payload']['lastSevenDaysAvgRestingHeartRate']
            else:
                average_hr = 'N/A'
            # check if data['AllDayHR']['payload']['heartRateValues'] exists
            if data['AllDayHR']['payload']['heartRateValues'] is not None:
                hr_values = json.dumps(data['AllDayHR']['payload']['heartRateValues'])
                # convert to list
                hr_values = hr_values.replace('[', '').replace(']', '').split(',')
                #logfunc(str(hr_values))
                x_list = []
                y_list = []
                # from hr_values get x and y values
                for i in range(len(hr_values)):
                    if i % 2 == 0:
                        x_list.append(float(hr_values[i]))
                    else:
                        #if value is null set to 0
                        if 'null' in hr_values[i]:
                            y_list.append(0)
                        else:
                            y_list.append(float(hr_values[i]))

                #convert timestamp to hh:mm
                #logfunc(str(x_list))
                #logfunc(str(y_list))
                hr_btn = '<button class="btn btn-light btn-sm" onclick="createLineChart(\'' + str(y_list) + '\', \'' + str(x_list) + '\', true, \'Heart Rate Variation\', \'Time\', \'BPM\')">View</button>'
            else:
                hr_btn = 'N/A'
            data_list.append((date, max_hr, min_hr, resting_hr, average_hr, hr_btn))
    report.filter_by_date('GarminHRAPI', 0)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminHRAPI')
    report.add_chart()
    report.end_artifact_report()
    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts__ = {
    "GarminHRAPI": (
        "Garmin-API",
        ('*/garmin.api/heart_rate*'),
        get_hr_api)
}
