# Get Information from Garmin Stress API
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json and datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_stress_api(files_found, report_folder, seeker, wrap_text):

    logfunc("Processing data for Stress API")
    report = ArtifactHtmlReport('Stress API')
    report.start_artifact_report(report_folder, 'Stress API')
    report.add_script()
    data_headers = ('Date', 'Stress Level', 'High Stress Duration', 'Medium Stress Duration', 'Low Stress Duration', 'Rest Stress Duration')
    data_list = []
    stress = []
    dates = []
    #file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        #Open JSON file
        with open(file, "r") as f:
            data_file = json.load(f)

        if len(data_file) > 0:
            logfunc("Found Garmin Stress API data")
            for data in data_file:
                # Get calendar date
                date = data['calendarDate']
                dates.append(date)
                # Get stress level
                if data['values']['overallStressLevel'] == -1:
                    stress_level = 'N/A'
                    stress.append(0)
                else:
                    stress_level = data['values']['overallStressLevel']
                    stress.append(stress_level)
                # Get max hearth rate if none set to 'N/A'
                if data['values']['highStressDuration'] is not None:
                    high_stress_duration = data['values']['highStressDuration']
                else:
                    high_stress_duration = 'N/A'
                # Get min hearth rate
                if data['values']['mediumStressDuration'] is not None:
                    medium_stress_duration = data['values']['mediumStressDuration']
                else:
                    medium_stress_duration = 'N/A'
                # Get resting hearth rate
                if data['values']['lowStressDuration'] is not None:
                    low_stress_duration = data['values']['lowStressDuration']
                else:
                   low_stress_duration = 'N/A'
                # Get average hearth rate
                if data['values']['restStressDuration'] is not None:
                    rest_stress_duration = data['values']['restStressDuration']
                else:
                    rest_stress_duration = 'N/A'
                data_list.append((date, stress_level, high_stress_duration, medium_stress_duration, low_stress_duration, rest_stress_duration))
    report.filter_by_date('GarminStressAPI', 0)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminStressAPI')
    report.add_chart()
    report.add_chart_script('myChart', 'line', stress, dates, 'Stress Level', 'Date', 'Stress Level')
    report.end_artifact_report()
    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts__ = {
    "GarminStressAPI": (
        "Garmin-API",
        ('*/garmin.api/stress*'),
        get_stress_api)
}
