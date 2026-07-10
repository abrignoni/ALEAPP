# pylint: disable=W0613
__artifacts_v2__ = {
    "get_bluetoothConnections": {
        "name": "Bluetooth Connections",
        "description": "Parses previously connected Bluetooth devices (first connected timestamp, device name, MAC address and link key) from bt_config.conf.",
        "author": "",
        "creation_date": "2021-06-23",
        "last_update_date": "2021-06-23",
        "requirements": "none",
        "category": "Bluetooth Connections",
        "notes": "",
        "paths": ('*/misc/bluedroid/bt_config.conf', '*/bt_config.conf'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "anne_a15": "Android 15 | 2 rows",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 4 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 1 row",
        },
    },
    "get_bluetoothAdapter": {
        "name": "Bluetooth Adapter Information",
        "description": "Parses the local Bluetooth adapter information (key and value) from bt_config.conf.",
        "author": "",
        "creation_date": "2021-06-23",
        "last_update_date": "2021-06-23",
        "requirements": "none",
        "category": "Bluetooth Connections",
        "notes": "",
        "paths": ('*/misc/bluedroid/bt_config.conf', '*/bt_config.conf'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "anne_a15": "Android 15 | 14 rows",
            "galaxys10_a10": "Android 10 | 14 rows",
            "hc_pixel8pro_a16": "Android 16 | 9 rows",
            "kevin_pocox7_a15": "Android 15 | 11 rows",
            "pixel7a_a14": "Android 14 | 10 rows",
            "samsunga53_a14": "Android 14 | 14 rows",
            "samsungs20_a13": "Android 13 | 14 rows",
            "sharon_a14": "Android 14 | 14 rows",
        },
    }
}

import datetime
import re

from scripts.ilapfuncs import artifact_processor

MAC_RE = re.compile(r'(\[[0-9a-f]{2}(?::[0-9a-f]{2}){5}\])', re.IGNORECASE)


@artifact_processor
def get_bluetoothConnections(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = str(files_found[0])

    name_value = timestamp_value = linkkey_value = macaddrf = ''
    first_round = True
    with open(source_path, "r", encoding='utf-8', errors='replace') as f:
        for line in f:
            if re.findall(MAC_RE, line):
                if first_round:
                    first_round = False
                else:
                    data_list.append((timestamp_value, name_value, macaddrf, linkkey_value))
                    name_value = timestamp_value = linkkey_value = ''
                macaddrf = re.findall(MAC_RE, line)[0].strip('[]').upper()

            splits = line.split(' = ')
            if len(splits) < 2:
                continue
            if splits[0] == 'Name':
                name_value = splits[1].strip()
            elif splits[0] == 'Timestamp':
                ts = splits[1].strip()
                timestamp_value = datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc) if ts else ''
            elif splits[0] == 'LinkKey':
                linkkey_value = splits[1].strip()

    if not first_round:  # at least one device was parsed
        data_list.append((timestamp_value, name_value, macaddrf, linkkey_value))

    data_headers = (('First Connected Timestamp', 'datetime'), 'Device Name', 'MAC Address', 'Link Key')
    return data_headers, data_list, source_path


@artifact_processor
def get_bluetoothAdapter(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "r", encoding='utf-8', errors='replace') as f:
        for line in f:
            if re.findall(MAC_RE, line):
                break  # adapter info is the block before the first device
            if ' = ' in line:
                splits = line.split(' = ')
                data_list.append((splits[0], splits[1].strip()))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
