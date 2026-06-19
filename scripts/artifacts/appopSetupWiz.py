# pylint: disable=W0613
__artifacts_v2__ = {
    "get_appopSetupWiz": {
        "name": "appopSetupWiz",
        "description": "Setup Wizard app-op timestamps from appops.xml",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/system/appops.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx


@artifact_processor
def get_appopSetupWiz(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('appops.xml'):
            continue  # Skip all other files

        source_path = file_found
        # check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
        else:
            tree = ET.parse(file_found)
        root = tree.getroot()

        for elem in root.iter('pkg'):
            if elem.attrib['n'] == 'com.google.android.setupwizard':
                pkg = elem.attrib['n']
                for subelem in elem:
                    for subelem2 in subelem:
                        for subelem3 in subelem2:
                            test = subelem3.attrib.get('t', 0)
                            if int(test) > 0:
                                timestamp = datetime.datetime.fromtimestamp(int(subelem3.attrib['t'])/1000, datetime.timezone.utc)
                            else:
                                timestamp = ''
                            data_list.append((timestamp, pkg))

    data_headers = (('Timestamp', 'datetime'), 'Package')
    return data_headers, data_list, source_path
