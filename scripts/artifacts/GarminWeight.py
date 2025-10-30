# Get Information relative to the weight data in the database cache-database from the table weight in the Garmin Connect app
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_weight(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Weight")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    #This query is retreiving the data from the table weight, which contains the weight data for the user
    cursor = db.cursor()
    cursor.execute('''
        Select
        samplePk,
        datetime("date"/1000,'unixepoch'),
        weight
        from weight
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} weight entries")
        report = ArtifactHtmlReport('Weight')
        report.start_artifact_report(report_folder, 'Weight')
        report.add_script()
        data_headers = ('samplePk', 'Date', 'Weight')
        data_list = []
        date = []
        weight = []

        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
            # get only the date from the datetime
            date.append(row[1].split(' ')[0])
            # convert weight in kg
            weight.append(row[2] / 1000)



        table_id = "GarminWeight"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id)
        report.add_chart()
        report.add_chart_script("myChart", "bar", weight, date, "Weight over time", "Weight (kg)", "Date")
        report.end_artifact_report()

        tsvname = f'Garmin - Weight'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - Weight'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Weight data available')

    db.close()


__artifacts__ = {
    "GarminWeight": (
        "Garmin-Cache",
        ('*/com.garmin.android.apps.connectmobile/databases/cache-database*'),
        get_garmin_weight)
}
