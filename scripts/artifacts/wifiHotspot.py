__artifacts_v2__ = {
    "get_wifiHotspot": {
        "name": "wifiHotspot",
        "description": "Parses the Wi-Fi hotspot (SoftAP) configuration (SSID and passphrase, plus security type where the configuration is in XML form) from the softap configuration files.",
        "author": "",
        "creation_date": "2020-11-18",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "SecurityType is read from a named element and is therefore only populated for the "
                 "WifiConfigStoreSoftAp.xml form; it is blank for the binary softap.conf form.\n"
                 "In the binary softap.conf form SSID and Passphrase are taken by byte position: "
                 "the SSID length is read from byte 5 and the passphrase from the bytes following "
                 "the last null byte in the file. That layout is not documented, no bounds checking "
                 "is performed, and a file laid out differently can yield a truncated or wrong "
                 "value rather than an error.",
        "paths": ('*/misc/wifi/softap.conf', '*/misc**/apexdata/com.android.wifi/WifiConfigStoreSoftAp.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "wifi",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_wifiHotspot(context):
    files_found = context.get_files_found()

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
