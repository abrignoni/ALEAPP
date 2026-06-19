# pylint: disable=W0613
__artifacts_v2__ = {
    "get_urluser": {
        "name": "ULR User Prefs",
        "description": "ULR User Prefs",
        "author": "Alexis 'Brigs' Brignoni",
        "creation_date": "2024-06-21",
        "last_update_date": "2024-06-21",
        "requirements": "",
        "category": "App Semantic Locations",
        "notes": "Thanks to Josh Hickman for the research",
        "paths": ('*/com.google.android.gms/shared_prefs/ULR_USER_PREFS.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_urluser(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('ULR_USER_PREFS.xml'):
            continue

        source_path = file_found
        root = ET.parse(file_found).getroot()
        for child in root:
            jsondata = child.attrib
            name = jsondata['name']
            value = jsondata.get('value', '')
            data_list.append((name, value))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
