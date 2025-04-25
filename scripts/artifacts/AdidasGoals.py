# Get Information related to user defined goals from the Adidas Running app stored in goals
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-04-21
# Version: 1.0
# Requirements: Python 3.7 or higher
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_adidas_goals(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Adidas Goals")
    files_found = [x for x in files_found if not x.endswith('-journal')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select *
        from goalV2
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in user.db")
        report = ArtifactHtmlReport('User')
        report.start_artifact_report(report_folder, 'Adidas Goals')
        report.add_script()
        data_headers = ('ID', 'Metric', 'Remote ID', 'User ID', 'Version', 'Target', 'Recurrence', 'Start Date', 'End Date', 'Sport Types', 'Created At', 'Updated At', 'Deleted At')
        data_list = []
        for row in all_rows:
            id = row[0]
            metric = row[1]
            remote_id = row[2]
            user_id = row[3]
            version = row[4]
            target = row[5]
            recurrence = row[6]
            start_date = row[8]
            start_date = str(start_date)
            start_date = start_date[:4] + '-' + start_date[4:6] + '-' + start_date[6:]
            end_date = row[9]
            if end_date:
                end_date = str(end_date)
                end_date = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:]
            sport_types = row[10]
            created_at = row[11]
            created_at = int(created_at)
            created_at = datetime.datetime.utcfromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
            updated_at = row[12]
            if updated_at:
                updated_at = int(updated_at)
                updated_at = datetime.datetime.utcfromtimestamp(updated_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
            deleted_at = row[13]
            if deleted_at:
                deleted_at = int(deleted_at)
                deleted_at = datetime.datetime.utcfromtimestamp(deleted_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
        data_list.append((id, metric, remote_id, user_id, version, target, recurrence, start_date, end_date, sport_types, created_at, updated_at, deleted_at))

        table_id = "AdidasGoals"
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Adidas - Goals'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Adidas - Goals'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Adidas Goals data available')

    db.close()


__artifacts__ = {
    "AdidasGoals": (
        "Adidas-Running",
        ('*/com.runtastic.android/databases/goals*'),
        get_adidas_goals)
}
