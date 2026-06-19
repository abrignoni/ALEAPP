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
        "artifact_icon": "download-cloud",
    }
}

import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, get_next_unused_name, open_sqlite_db_readonly, lava_process_artifact, lava_insert_sqlite_data, artifact_processor
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
                    data_list.append((row[0],row[1],(textwrap.fill(row[2], width=75)),row[3],row[4],row[5],row[6]))
                else:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report_name = f'{browser_name} - Offline Pages'
            report = ArtifactHtmlReport(report_name)
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            category = "Chromium"
            module_name = "get_chromeOfflinePages"
            table_name, object_columns, column_map = lava_process_artifact(
                category, module_name, report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Offline Pages data available')

        db.close()

    return all_data_headers, all_data, report_file
