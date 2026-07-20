__artifacts_v2__ = {
    "get_chromeCookies": {
        "name": "Cookies",
        "description": "Parses Cookies from Chromium Based Browsers",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Cookies*', '*/app_sbrowser/Default/Cookies*', '*/app_opera/Cookies*', '*/app_webview/Default/Cookies*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 1777 rows",
            "galaxys10_a10": "Android 10 | 800 rows",
            "hc_pixel8pro_a16": "Android 16 | 474 rows",
            "kevin_pocox7_a15": "Android 15 | 4170 rows",
            "pixel7a_a14": "Android 14 | 1554 rows",
            "samsunga53_a14": "Android 14 | 1491 rows",
            "samsungs20_a13": "Android 13 | 670 rows",
            "sharon_a14": "Android 14 | 1842 rows",
            "russell_pixel6a_a13": "Android 13 | 1420 rows",
            "userb2_a13": "Android 13 | 632 rows",
        },
    }
}

import os

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor, convert_human_ts_to_utc
from scripts.artifacts.chrome import get_browser_name


@artifact_processor
def get_chromeCookies(context):
    files_found = context.get_files_found()
    all_data = []

    data_headers = ['Last Access Date', 'Host', 'Name', 'Value', 'Created Date', 'Expiration Date', 'Path']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    lava_data_headers[4] = (lava_data_headers[4], 'datetime')
    lava_data_headers[5] = (lava_data_headers[5], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Cookies':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        CASE
            last_access_utc
            WHEN
                "0"
            THEN
                ""
            ELSE
                datetime(last_access_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "last_access_utc",
        host_key,
        name,
        value,
        CASE
            creation_utc
            WHEN
                "0"
            THEN
                ""
            ELSE
                datetime(creation_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "creation_utc",
        CASE
            expires_utc
            WHEN
                "0"
            THEN
                ""
            ELSE
                datetime(expires_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "expires_utc",
        path
        FROM
        cookies
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

            data_list = []
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],convert_human_ts_to_utc(row[4]),convert_human_ts_to_utc(row[5]),row[6]))

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Cookies data available')

        db.close()

    return all_data_headers, all_data, report_file
