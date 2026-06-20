# pylint: disable=W0613
__artifacts_v2__ = {
    "get_gmailActive": {
        "name": "GmailActive",
        "description": "gmailActive: Get gmail account information",
        "author": "Joshua James {joshua@dfirscience.org}",
        "creation_date": "2021-11-08",
        "last_update_date": "2021-11-08",
        "requirements": "none",
        "category": "Gmail",
        "notes": "",
        "paths": ('*/com.google.android.gm/shared_prefs/Gmail.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "mail",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_gmailActive(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = str(files_found[0])
    root = ET.parse(source_path).getroot()
    for child in root:
        if child.attrib['name'] == "active-account":
            logfunc("Active gmail account found: " + child.text)
            data_list.append((child.text,))

    data_headers = ('Active Gmail Address',)
    return data_headers, data_list, source_path
