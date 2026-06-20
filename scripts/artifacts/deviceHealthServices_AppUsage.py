# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Turbo_AppUsage": {
        "name": "Turbo_AppUsage",
        "description": "Parses application usage via Device Health Services",
        "author": "@KevinPagano3",
        "creation_date": "2021-06-29",
        "last_update_date": "2021-06-29",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "",
        "paths": ('*/com.google.android.apps.turbo/shared_prefs/app_usage_stats.xml',),
        "output_types": "standard",
        "artifact_icon": "bar-chart-2",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_Turbo_AppUsage(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        tree = ET.parse(file_found)

        for elem in tree.iter(tag='string'):
            splits = elem.text.split('#')
            app_name = splits[0]
            timesplitter = splits[1].split(',')

            for ts in timesplitter:
                timestamp_split = datetime.datetime.fromtimestamp(int(ts) / 1000, datetime.timezone.utc)
                data_list.append((timestamp_split, app_name))

    data_headers = (('App Launch Timestamp', 'datetime'), 'App Name')
    return data_headers, data_list, source_path
