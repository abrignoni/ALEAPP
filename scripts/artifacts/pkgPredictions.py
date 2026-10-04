__artifacts_v2__ = {
    "get_pkgPredictions": {
        "name": "pkgPredictions",
        "description": "Parses the tbl_Sample table of Samsung's PkgPredictions.db.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2023-05-01",
        "last_update_date": "2026-10-04",
        "requirements": "None",
        "category": "Package Predictions",
        "notes": "launch_time is converted as Unix milliseconds. Screen "
                 "Orientation is screen_orientation as stored; no source for "
                 "its values was found, and the five listed images held 0, 1 "
                 "and 2 (2 on 9 of their 1,786 rows). Hour of Day is "
                 "hour_of_day as stored. No time zone is recorded for it: on "
                 "the listed images it differed from the UTC hour of "
                 "launch_time by a whole number of hours on every row, one "
                 "value on three images and three or five values on the other "
                 "two. Day of Week shows day_of_week 1 to 7 as Sunday to "
                 "Saturday and any other value as stored. That numbering was "
                 "measured, not sourced: on all 1,786 rows it gave the weekday "
                 "of launch_time once shifted by that row's hour difference, "
                 "and it gave the UTC weekday on 1,658. The Previous Launch "
                 "columns are previous_one, previous_two and previous_three "
                 "as stored.",
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
def get_pkgPredictions(context):
    files_found = context.get_files_found()

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
        screen_orientation,
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
            else day_of_week
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

    data_headers = (('Launch Timestamp', 'datetime'), 'Running Package', 'APK Version', 'Activity Name', 'Previous Launch (1)', 'Previous Launch (2)', 'Previous Launch (3)', 'Screen Orientation', 'Wifi Status', 'Bluetooth Status', 'Hour of Day', 'Day of Week', 'Prediction', 'Predict Time', 'User ID', 'ID')
    return data_headers, data_list, source_path
