__artifacts_v2__ = {
    "get_chromeNetworkActionPredictor": {
        "name": 'Network Action Predictor',
        "description": 'Parses the Network Action Predictor from Chromium Based Browsers',
        "author": 'Kevin Pagano (@stark4n6)',
        "creation_date": '2020-03-19',
        "last_update_date": '2026-09-11',
        "requirements": 'none',
        "category": 'Chromium',
        "notes": 'Reads the network_action_predictor table from the Chromium profiles the declared paths match, one '
                  'storage view per file, and reports user_text, url, number_of_hits and number_of_misses as stored. '
                  'A Magisk mirror copy is skipped as a duplicate; 1 registered corpus carries a Magisk mirror path '
                  'and it holds no copy of this file, so that branch is unexercised. Measured over all 42 registered '
                  'Android corpora on 2026-09-11: 34 carry a file named Network Action Predictor and every copy sits '
                  'under app_chrome/Default or app_sbrowser/Default. No copy sits under app_opera or app_webview on '
                  'any of them, although 3 carry an app_opera directory and 39 carry an app_webview directory, so '
                  'both of those declared patterns are unexercised. Row counts come from profile-driven runs over the '
                  '20 registered zip corpora, cross-checked against a direct read of the same databases; the two '
                  'agree on all 20. Nine of them reported rows, 1,172 rows from com.android.chrome and 2,029 from '
                  'com.microsoft.emmx. The com.brave.browser copy held the table and no rows on all 7 run corpora '
                  'carrying it, and of the 9 Samsung Browser copies read 6 hold no network_action_predictor table and '
                  '3 hold it empty, so no Brave or Samsung Browser row was observed. An absent browser here is not '
                  'evidence that browser was unused. Where a device carries more than one Android user each profile '
                  'is reported separately: on russell_pixel6a_a13 the Android user 0 Chrome profile holds 273 rows '
                  'and the user 10 profile holds none.',
        "paths": ('*/app_chrome/Default/Network Action Predictor*', '*/app_sbrowser/Default/Network Action Predictor*', '*/app_opera/Network Action Predictor*', '*/app_webview/Default/Network Action Predictor*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": 'wifi',
        "sample_data": {
            "galaxys10_a10": 'Android 10 | com.android.chrome vc 438910534 | 7 rows',
            "pixel3_a12": 'Android 12 | com.android.chrome vc 463805033, com.brave.browser vc 413211224, com.microsoft.emmx vc 96108015 | 483 rows',
            "russell_pixel6a_a13": 'Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 273 rows',
            "s20fe_a13": 'Android 13 | com.android.chrome vc 787112833, com.sec.android.app.sbrowser vc 1300067502 | 203 rows',
            "pixel7a_a14": 'Android 14 | com.android.chrome vc 616710133, com.brave.browser vc 426712324, com.microsoft.emmx vc 259210005 | 414 rows',
            "samsunga53_a14": 'Android 14 | com.android.chrome vc 744417133 | 0 rows',
            "sharon_a14": 'Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 0 rows',
            "anne_a15": 'Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 23 rows',
            "hc_pixel8pro_a16": 'Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 0 rows',
        },
    }
}

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor
from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def get_chromeNetworkActionPredictor(context):
    files_found = unique_files(context)
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
        columns = [i[1] for i in cursor.execute('PRAGMA table_info(network_action_predictor)')]

        if not columns:
            # Some browser variants keep only resource_prefetch_predictor tables here
            logfunc(f'No network_action_predictor table available in {file_found}')
            db.close()
            continue

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
