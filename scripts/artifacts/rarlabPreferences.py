# pylint: disable=W0613
__artifacts_v2__ = {
    "get_rarlabPreferences": {
        "name": "rarlabPreferences",
        "description": "",
        "author": "",
        "creation_date": "2023-03-29",
        "last_update_date": "2023-03-29",
        "requirements": "none",
        "category": "RAR Lab Prefs",
        "notes": "",
        "paths": ('*/com.rarlab.rar_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "html_columns": ['Text'],
    }
}

import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx


@artifact_processor
def get_rarlabPreferences(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.rarlab.rar_preferences.xml'):
            source_path = file_found

            # check if file is abx
            if (checkabx(file_found)):
                multi_root = False
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            root = tree.getroot()

            for elem in root.iter():
                name = elem.attrib.get('name')
                value = elem.attrib.get('value')
                text = elem.text
                if name is not None:
                    if name == 'ArcHistory' or name == 'ExtrPathHistory':
                        items = json.loads(text)
                        agg = ''
                        for x in items:
                            agg = agg + f'{x}<br>'
                        data_list.append((name,agg,value))
                    else:
                        data_list.append((name,text,value))

    data_headers = ('Key', 'Text', 'Value')
    return data_headers, data_list, source_path
