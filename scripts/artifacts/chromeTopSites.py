# pylint: disable=W0702
__artifacts_v2__ = {
    "get_chromeTopSites": {
        "name": "Top Sites",
        "description": "Parses Top Sites from Chromium Based Browsers",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Top Sites*', '*/app_sbrowser/Default/Top Sites*', '*/app_opera/Top Sites*', '*/app_webview/Default/Top Sites*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 0 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 0 rows",
            "pixel7a_a14": "Android 14 | com.android.chrome vc 616710133, com.brave.browser vc 426712324, com.microsoft.emmx vc 259210005 | 0 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133 | 0 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233, com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 0 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 0 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 0 rows",
        },
    }
}

import os

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor
from scripts.artifacts.chrome import get_browser_name


@artifact_processor
def get_chromeTopSites(context):
    files_found = context.get_files_found()
    all_data = []

    data_headers = ['URL', 'Rank', 'Title', 'Redirects']
    lava_data_headers = data_headers.copy()
    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Top Sites':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
            select
            url,
            url_rank,
            title,
            redirects
            FROM
            top_sites ORDER by url_rank asc
            ''')
            all_rows = cursor.fetchall()
        except:
            all_rows = []

        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Top Sites data available')

        db.close()

    return all_data_headers, all_data, report_file
