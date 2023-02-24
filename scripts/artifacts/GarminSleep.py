# Get Information relative to the sleep data in the database cache-database from the table sleep_detail in the Garmin Connect app
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_sleep(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Sleep")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    #This query is retreiving the data from the table sleep_details, which contains the sleep data for the user
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        datetime("sleepStartTimeGMT"/1000, 'unixepoch'),
        datetime("sleepEndTimeGMT"/1000, 'unixepoch'),
        sleepTimeInSeconds,
        deepSleepSeconds,
        lightSleepSeconds, 
        remSleepSeconds, 
        awakeSleepSeconds, 
        averageSpO2Value, 
        averageSpO2HRSleep,
        calendarDate
        from sleep_detail
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} sleep entries")
        report = ArtifactHtmlReport('Sleep')
        report.start_artifact_report(report_folder, 'Sleep')
        report.add_script()
        data_headers = ('Sleep Start Time GMT', 'Sleep End Time GMT', 'Sleep Time In Seconds', 'Deep Sleep Seconds', 'Light Sleep Seconds', 'REM Sleep Seconds', 'Awake Sleep Seconds', 'Average SpO2 Value', 'Average SpO2 HR Sleep', 'Graph')
        data_list = []

        for row in all_rows:
            sleepValues = []
            sleepValues.append(row[3])
            sleepValues.append(row[4])
            sleepValues.append(row[5])
            sleepValues.append(row[6])

            sleep_btn = "<button class='btn btn-light btn-sm' onclick=" + '"createPieChart(\'' + str(sleepValues) + '\')">Sleep Graphic</button>'
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], sleep_btn))

        # Add graph to the report

        table_id = 'garmin_sleep'
        report.filter_by_date(table_id, 0)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False, table_id=table_id)
        report.add_chart(200)
        report.end_artifact_report()

        tsvname = f'Garmin - Sleep'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - Sleep'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Sleep data available')

    db.close()


__artifacts__ = {
    "GarminSleep": (
        "Garmin-Cache",
        ('*/com.garmin.android.apps.connectmobile/databases/cache-database*'),
        get_garmin_sleep)
}
