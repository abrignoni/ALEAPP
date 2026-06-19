# pylint: disable=W0613
__artifacts_v2__ = {
    "get_setupWizardinfo": {
        "name": "setupWizardinfo",
        "description": "",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/com.google.android.settings.intelligence/shared_prefs/setup_wizard_info.xml',),
        "output_types": "standard",
        "artifact_icon": "info",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_setupWizardinfo(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('setup_wizard_info.xml'):
            continue  # Skip all other files

        source_path = file_found
        root = ET.parse(file_found).getroot()
        for elem in root:
            item = elem.attrib
            if item['name'] == 'suw_finished_time_ms':
                timestamp = datetime.datetime.fromtimestamp(int(item['value']) / 1000, datetime.timezone.utc)
                data_list.append((timestamp, item['name']))

    data_headers = (('Timestamp', 'datetime'), 'Name')
    return data_headers, data_list, source_path
