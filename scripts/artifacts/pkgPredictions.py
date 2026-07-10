# pylint: disable=W0613
__artifacts_v2__ = {
    "get_pkgPredictions": {
        "name": "pkgPredictions",
        "description": "Package Predictions - Parses Samsung package prediction details",
        "author": "Kevin Pagano (https://startme.stark4n6.com)",
        "creation_date": "2023-05-01",
        "last_update_date": "2023-05-01",
        "requirements": "None",
        "category": "Package Predictions",
        "notes": "",
        "paths": ('*/system/PkgPredictions.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | 483 rows",
            "galaxys10_a10": "Android 10 | 295 rows",
            "samsunga53_a14": "Android 14 | 158 rows",
            "samsungs20_a13": "Android 13 | 407 rows",
            "sharon_a14": "Android 14 | 443 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_pkgPredictions(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('PkgPredictions.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
        select
        launch_time,
        running_pkg,
        apk_version,
        activity_name,
        previous_one,
        previous_two,
        previous_three,
        case screen_orientation
            when 0 then 'Vertical'
            when 1 then 'Horizontal'
        end as "Screen Orientation",
        wifi_status,
        bt_status,
        hour_of_day,
        case day_of_week
            when 1 then 'Sunday'
            when 2 then 'Monday'
            when 3 then 'Tuesday'
            when 4 then 'Wednesday'
            when 5 then 'Thursday'
            when 6 then 'Friday'
            when 7 then 'Saturday'
        end as "Day of Week",
        prediction,
        predict_time,
        user_id,
        id
        from tbl_Sample
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            launch_ts = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            predictions = row[12].replace('0_&_', '').replace(';', '\n') if row[12] else row[12]
            data_list.append((launch_ts, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], predictions, row[13], row[14], row[15]))

    data_headers = (('Launch Timestamp', 'datetime'), 'Running Package', 'APK Version', 'Activity Name', 'Previous Launch (1)', 'Previous Launch (2)', 'Previous Launch (3)', 'Screen Orientation', 'Wifi Status', 'Bluetooth Status', 'Hour of Launch (Local)', 'Day of Launch', 'Prediction', 'Predict Time', 'User ID', 'ID')
    return data_headers, data_list, source_path
