# pylint: disable=W0613
__artifacts_v2__ = {
    "get_usageHistory": {
        "name": "Usagehistory",
        "description": "",
        "author": "",
        "creation_date": "2022-07-06",
        "last_update_date": "2022-07-06",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/usage-history.xml',),
        "output_types": "standard",
        "artifact_icon": "globe",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_usageHistory(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('usage-history.xml'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        root = ET.parse(source_path).getroot()
        for elem in root:
            for subelem in elem:
                pkg = elem.attrib['name']
                subitem = subelem.attrib['name']
                time = subelem.attrib['lrt']
                if time and time != ' ':
                    time = datetime.datetime.fromtimestamp(int(time) / 1000, datetime.timezone.utc)
                else:
                    time = ''
                data_list.append((time, pkg, subitem))

    data_headers = (('Timestamp', 'datetime'), 'Package', 'Subitem')
    return data_headers, data_list, source_path
