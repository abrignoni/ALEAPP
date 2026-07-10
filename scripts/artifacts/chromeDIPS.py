# pylint: disable=W0613
__artifacts_v2__ = {
    "get_chromeDIPS": {
        "name": "ChromeDIPS",
        "description": "Module Description: Parses Chromium DIPS (Detect Incidental Party State)",
        "author": "@KevinPagano3",
        "creation_date": "2023-04-07",
        "last_update_date": "2023-04-07",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/DIPS*', '*/app_sbrowser/Default/DIPS*', '*/app_opera/DIPS*', '*/app_webview/Default/DIPS*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533 | 13 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 19 rows",
            "pixel7a_a14": "Android 14 | com.android.chrome vc 616710133, com.microsoft.emmx vc 259210005 | 36 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333 | 19 rows",
        },
    }
}

# Thanks to Ryan Benson for awareness https://github.com/obsidianforensics/hindsight/pull/146/commits/015ee189c97c0a4e48deb59568dfe4f536ace8aa

import datetime

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name


def _webkit_to_utc(value):
    if value in (None, 0, ''):
        return ''
    return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=int(value))


@artifact_processor
def get_chromeDIPS(files_found, report_folder, seeker, wrap_text):
    # all_data is a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []

    data_headers = [
        'Site',
        'First Site Storage Timestamp',
        'Last Site Storage Timestamp',
        'First User Interaction Timestamp',
        'Last User Interaction Timestamp',
        'First Stateful Bounce Timestamp',
        'Last Stateful Bounce Timestamp',
        'First Stateless Bounce Timestamp',
        'Last Stateless Bounce Timestamp',
    ]

    lava_data_headers = data_headers.copy()
    for i in range(1, 9):
        lava_data_headers[i] = (lava_data_headers[i], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('DIPS'):
            continue  # Skip all other files
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        columns = [i[1] for i in cursor.execute('PRAGMA table_info(bounces)')]

        stateless = 'first_stateless_bounce_time' in columns
        first_user_col = 'first_user_interaction_time' if 'first_user_interaction_time' in columns else 'first_user_activation_time'
        last_user_col = 'last_user_interaction_time' if 'last_user_interaction_time' in columns else 'last_user_activation_time'
        if stateless:
            first_bounce_col, last_bounce_col = 'first_stateless_bounce_time', 'last_stateless_bounce_time'
        else:
            first_bounce_col, last_bounce_col = 'first_bounce_time', 'last_bounce_time'

        cursor.execute(f'''
            select
            site,
            first_site_storage_time,
            last_site_storage_time,
            {first_user_col},
            {last_user_col},
            first_stateful_bounce_time,
            last_stateful_bounce_time,
            {first_bounce_col},
            {last_bounce_col}
            from bounces
        ''')
        all_rows = cursor.fetchall()
        db.close()

        data_list = []
        for row in all_rows:
            data_list.append((row[0], _webkit_to_utc(row[1]), _webkit_to_utc(row[2]), _webkit_to_utc(row[3]),
                              _webkit_to_utc(row[4]), _webkit_to_utc(row[5]), _webkit_to_utc(row[6]),
                              _webkit_to_utc(row[7]), _webkit_to_utc(row[8])))

        if len(data_list) > 0:
            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Detect Incidental Party State data available')

    return all_data_headers, all_data, report_file
