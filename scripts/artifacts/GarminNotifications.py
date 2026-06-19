# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_notifications": {
        "name": "Garmin - Notifications",
        "description": "Get Information relative to the notifications stored in the database of the Garmin Connect Mobile application",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/notification-database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    }
}

# Get Information relative to the notifications stored in the database of the Garmin Connect Mobile application
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_garmin_notifications(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Notifications")
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)

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
    data_list = []
    for row in all_rows:
        data_list.append((row[0], convert_human_ts_to_utc(row[1]), row[2], row[3], row[4], row[5], row[6]))

    db.close()

    data_headers = (
        'Status',
        ('Status Timestamp', 'datetime'),
        'Title',
        'Message',
        'Type',
        'Category',
        'Package Name',
    )
    return data_headers, data_list, source_path
