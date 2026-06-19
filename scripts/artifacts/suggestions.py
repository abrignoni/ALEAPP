# pylint: disable=W0613
__artifacts_v2__ = {
    "get_suggestions": {
        "name": "suggestions",
        "description": "",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/com.google.android.settings.intelligence/shared_prefs/suggestions.xml',),
        "output_types": "standard",
        "artifact_icon": "clock",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor

SETUP_TIME_KEYS = (
    'com.android.settings.suggested.category.DEFERRED_SETUP_setup_time',
    'com.android.settings/com.android.settings.biometrics.fingerprint.FingerprintEnrollSuggestionActivity_setup_time',
    'com.google.android.setupwizard/com.google.android.setupwizard.deferred.DeferredSettingsSuggestionActivity_setup_time',
)


@artifact_processor
def get_suggestions(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('suggestions.xml'):
            continue  # Skip all other files

        source_path = file_found
        root = ET.parse(file_found).getroot()
        for elem in root:
            item = elem.attrib
            if item['name'] in SETUP_TIME_KEYS:
                timestamp = datetime.datetime.fromtimestamp(int(item['value']) / 1000, datetime.timezone.utc)
                data_list.append((timestamp, item['name']))

    data_headers = (('Timestamp', 'datetime'), 'Name')
    return data_headers, data_list, source_path
