# pylint: disable=W0613
__artifacts_v2__ = {
    "get_wifiHotspot": {
        "name": "wifiHotspot",
        "description": "Parses the Wi-Fi hotspot (SoftAP) configuration (SSID, passphrase and security type) from the softap configuration files.",
        "author": "",
        "creation_date": "2020-11-18",
        "last_update_date": "2020-11-18",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "",
        "paths": ('*/misc/wifi/softap.conf', '*/misc**/apexdata/com.android.wifi/WifiConfigStoreSoftAp.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "wifi",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_wifiHotspot(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        ssid = ''
        security_type = ''
        passphrase = ''

        if file_found.endswith('.conf'):
            with open(file_found, 'rb') as f:
                data = f.read()
                ssid_len = data[5]
                ssid = data[6: 6 + ssid_len].decode('utf8', 'ignore')

                data_len = len(data)
                start_pos = -1
                while data[start_pos] != 0 and (-start_pos < data_len):
                    start_pos -= 1
                passphrase = data[start_pos + 2:].decode('utf8', 'ignore')
        else:
            tree = ET.parse(file_found)
            for node in tree.iter('SoftAp'):
                for elem in node.iter():
                    if elem.tag != node.tag:
                        data = elem.attrib
                        name = data.get('name', '')
                        if name in ('SSID', 'WifiSsid'):
                            ssid = elem.text
                        elif name == 'SecurityType':
                            security_type = data.get('value', '')
                        elif name == 'Passphrase':
                            passphrase = elem.text

        if ssid:
            data_list.append((ssid, passphrase, security_type))

    data_headers = ('SSID', 'Passphrase', 'SecurityType')
    return data_headers, data_list, source_path
