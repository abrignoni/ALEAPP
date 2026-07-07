# pylint: disable=W0613
__artifacts_v2__ = {
    "get_chromeOfflinePages": {
        "name": "Offline Pages",
        "description": "Parses Offline Pages from Chromium Based Browsers",
        "author": "",
        "creation_date": "2020-04-02",
        "last_update_date": "2020-04-02",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Offline Pages/metadata/OfflinePages.db*', '*/app_sbrowser/Default/Offline Pages/metadata/OfflinePages.db*', '*/app_webview/Default/Offline Pages/metadata/OfflinePages.db*'),
        "output_types": "standard",
        "artifact_icon": "cloud-download",
    }
}

import os
import textwrap

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor, convert_human_ts_to_utc
from scripts.artifacts.chrome import get_browser_name


@artifact_processor
def get_chromeOfflinePages(files_found, report_folder, seeker, wrap_text):
    all_data = []

    data_headers = ['Creation Time', 'Last Access Time', 'Online URL', 'File Path', 'Title', 'Access Count', 'File Size']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    lava_data_headers[1] = (lava_data_headers[1], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'OfflinePages.db':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(creation_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch") as creation_time,
        datetime(last_access_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch") as last_access_time,
        online_url,
        file_path,
        title,
        access_count,
        file_size
        from offlinepages_v1
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            data_list = []
            for row in all_rows:
                if wrap_text:
                    data_list.append((convert_human_ts_to_utc(row[0]),convert_human_ts_to_utc(row[1]),(textwrap.fill(row[2], width=75)),row[3],row[4],row[5],row[6]))
                else:
                    data_list.append((convert_human_ts_to_utc(row[0]),convert_human_ts_to_utc(row[1]),row[2],row[3],row[4],row[5],row[6]))

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Offline Pages data available')

        db.close()

    return all_data_headers, all_data, report_file
