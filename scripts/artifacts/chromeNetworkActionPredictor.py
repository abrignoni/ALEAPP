# pylint: disable=W0613
__artifacts_v2__ = {
    "get_chromeNetworkActionPredictor": {
        "name": "Network Action Predictor",
        "description": "Parses the Network Action Predictor from Chromium Based Browsers",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_Chrome/Default/Network Action Predictor*', '*/app_sbrowser/Default/Network Action Predictor*', '*/app_opera/Network Action Predicator*', '*/app_webview/Default/Network Action Predictor*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "wifi",
        "sample_data": {
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser vc 1260103502 | 0 rows",
        },
    }
}

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor
from scripts.artifacts.chrome import get_browser_name


@artifact_processor
def get_chromeNetworkActionPredictor(files_found, report_folder, seeker, wrap_text):
    all_data = []

    data_headers = ['User Text', 'URL', 'Number of Hits', 'Number of Misses']
    lava_data_headers = data_headers.copy()
    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Network Action Predictor'):
            continue  # Skip all other files

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        user_text,
        url,
        number_of_hits,
        number_of_misses
        from network_action_predictor
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Network Action Predictor data available')

        db.close()

    return all_data_headers, all_data, report_file
