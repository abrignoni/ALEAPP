# Get Information relative to the notifications stored in the database of the Nike Run Club Mobile application
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-18
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_nike_notifications(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nike Notifications")
    files_found = [x for x in files_found if not x.endswith('-journal')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
        Select
        _id,
        sender_user_id,
        sender_app_id,
         datetime("notification_timestamp"/1000,'unixepoch'), 
        notification_type,
        message, 
        read,
        deleted
        from inbox
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} notifications")
        report = ArtifactHtmlReport('Nike - Notifications')
        report.start_artifact_report(report_folder, 'Nike - Notifications')
        report.add_script()
        data_headers = ('ID', 'Sender User ID', 'Sender App ID', 'Notification Timestamp', 'Notification Type', 'Message', 'Read', 'Deleted')
        data_list = []
        for row in all_rows:
            read = row[6]
            if read == 0:
                read = 'No'
            else:
                read = 'Yes'
            deleted = row[7]
            if deleted == 0:
                deleted = 'No'
            else:
                deleted = 'Yes'

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], read, deleted))

        table_id = "nike_notifications"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id)
        report.end_artifact_report()

        tsvname = f'Notifications'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Notifications'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Nike Notifications data available')

    db.close()


__artifacts__ = {
    "NikeNotifications": (
        "Nike-Run",
        ('*/com.nike.plusgps/databases/ns_inbox.db*'),
        get_nike_notifications)
}
