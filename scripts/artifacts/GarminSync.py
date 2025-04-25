# Get Information related to the sync process stored in the sync_cache database file
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_sync(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Sync")
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select
        device_info,
        audit_text,
        app_version,
        datetime("created_timestamp"/1000,'unixepoch')
        from device_sync_audit
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in device_sync_audit")
        report = ArtifactHtmlReport('Sync')
        report.start_artifact_report(report_folder, 'Sync')
        report.add_script()
        data_headers = ('Device Info', 'Audit Text', 'App Version', 'Created Timestamp')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3]))

        # Filter by date
        table_id = "GarminSync"
        report.filter_by_date(table_id, 3)
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id)
        report.end_artifact_report()

        tsvname = f'Garmin - Sync'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - Sync'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Sync data available')

    db.close()


__artifacts__ = {
    "GarminSync": (
        "Garmin-Sync",
        ('*/com.garmin.android.apps.connectmobile/databases/sync_cache*'),
        get_garmin_sync)
}
