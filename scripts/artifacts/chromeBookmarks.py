# pylint: disable=W0612,W0613
__artifacts_v2__ = {
    "get_chromeBookmarks": {
        "name": "Bookmarks",
        "description": "Parses Bookmarks from Chromium Based Browsers",
        "author": "",
        "creation_date": "2020-03-20",
        "last_update_date": "2020-03-20",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Bookmarks*', '*/app_sbrowser/Default/Bookmarks*', '*/app_opera/Bookmarks*', '*/app_webview/Default/Bookmarks*'),
        "output_types": "standard",
        "artifact_icon": "bookmark",
    }
}

import datetime
import json
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, get_next_unused_name, lava_process_artifact, lava_insert_sqlite_data, artifact_processor
from scripts.artifacts.chrome import get_browser_name


@artifact_processor
def get_chromeBookmarks(files_found, report_folder, seeker, wrap_text):
    # all_data is a consolidated list of all browsers with an extra column to discriminate the browser
    all_data = []

    data_headers = ['Added Date', 'URL', 'Name', 'Parent', 'Type']

    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')

    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Bookmarks':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        with open(file_found, "r", encoding='utf-8') as f:
            dataa = json.load(f)
        data_list = []
        for x, y in dataa.items():
            children_items = list()
            if isinstance(y, dict):
                for key, value in y.items():
                    if isinstance(value, dict):
                        for keyb, valueb in value.items():
                            if keyb == 'children':
                                if len(valueb) > 0:
                                    for index in range(len(valueb)):
                                        url = valueb[index].get('url', '')
                                        dateadd = valueb[index].get('date_added', '')
                                        dateaddconv = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=int(dateadd))
                                        name = valueb[index].get('name', '')
                                        typed = valueb[index].get('type', '')
                                        children_items.append((url, dateaddconv, name, typed))
                            if keyb == 'name' and len(children_items) > 0:
                                parent = valueb
                                for (url, dateaddconv, name, typed) in children_items:
                                    data_list.append((dateaddconv, url, name, parent, typed))
                                children_items = list()

        if len(data_list) > 0:
            report_name = f'{browser_name} - Bookmarks'
            report = ArtifactHtmlReport(report_name)
            # check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            # Per-browser LAVA table
            category = "Chromium"
            module_name = "get_chromeBookmarks"
            table_name, object_columns, column_map = lava_process_artifact(
                category, module_name, report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            # Add the browser name column and accumulate for the combined output
            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Bookmarks data available')

    return all_data_headers, all_data, report_file
