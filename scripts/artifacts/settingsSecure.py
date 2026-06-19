# pylint: disable=W0613
__artifacts_v2__ = {
    "get_settingsSecure": {
        "name": "settingsSecure",
        "description": "Filter for path xxx/yyy/system_ce/0",
        "author": "",
        "creation_date": "2020-04-02",
        "last_update_date": "2020-04-02",
        "requirements": "none",
        "category": "Device Info",
        "notes": "",
        "paths": ('*/system/users/*/settings_secure.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
    }
}

import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logdevinfo, is_platform_windows, abxread, checkabx


@artifact_processor
def get_settingsSecure(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-2]
        try:
            int(uid)
        except ValueError:
            continue  # uid was not a number
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            continue  # Skip mirror, it should be duplicate data

        if (checkabx(file_found)):
            multi_root = True
            root = abxread(file_found, multi_root).getroot()
        else:
            try:
                root = ET.parse(file_found).getroot()
            except ET.ParseError:  # Fix for android 11 invalid XML file (no root element present)
                with open(file_found, encoding='utf-8', errors='replace') as f:
                    xml = f.read()
                    root = ET.fromstring(re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>")

        source_path = file_found
        for setting in root.iter('setting'):
            nme = setting.get('name')
            val = setting.get('value')
            if nme == 'bluetooth_name':
                data_list.append((uid, nme, val))
                logdevinfo(f"<b>Bluetooth name: </b>{val}")
            elif nme == 'mock_location':
                data_list.append((uid, nme, val))
            elif nme == 'android_id':
                data_list.append((uid, nme, val))
            elif nme == 'bluetooth_address':
                data_list.append((uid, nme, val))
                logdevinfo(f"<b>Bluetooth address: </b>{val}")

    data_headers = ('User', 'Name', 'Value')
    return data_headers, data_list, source_path
