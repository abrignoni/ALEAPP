# Get Information relative to the notifications stored in the database of the Garmin Connect Mobile application
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_notifications(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Notifications")
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
        Select
        status,
        datetime("statusTimestamp"/1000,'unixepoch'),
        title, 
        message, 
        type, 
        category, 
        packageName
        from notification_info
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} notifications")
        report = ArtifactHtmlReport('Garmin - Notifications')
        report.start_artifact_report(report_folder, 'Garmin - Notifications')
        report.add_script()
        data_headers = ('Status', 'Status Timestamp', 'Title', 'Message', 'Type', 'Category', 'Package Name')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

        table_id = "garmin_notifications"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id)
        report.end_artifact_report()

        tsvname = f'Notifications'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Notifications'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Notifications data available')

    db.close()


__artifacts__ = {
    "GarminNotifications": (
        "Garmin-Notifications",
        ('*/com.garmin.android.apps.connectmobile/databases/notification-database*'),
        get_garmin_notifications)
}
