# pylint: disable=W0613,W0702
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
    }
}

import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, get_next_unused_name, open_sqlite_db_readonly, lava_process_artifact, lava_insert_sqlite_data, artifact_processor
from scripts.artifacts.chrome import get_browser_name


@artifact_processor
def get_chromeTopSites(files_found, report_folder, seeker, wrap_text):
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

            report_name = f'{browser_name} - Top Sites'
            report = ArtifactHtmlReport(report_name)
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            category = "Chromium"
            module_name = "get_chromeTopSites"
            table_name, object_columns, column_map = lava_process_artifact(
                category, module_name, report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Top Sites data available')

        db.close()

    return all_data_headers, all_data, report_file
