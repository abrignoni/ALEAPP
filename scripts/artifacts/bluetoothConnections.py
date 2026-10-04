__artifacts_v2__ = {
    "get_bluetoothConnections": {
        "name": "Bluetooth Connections",
        "description": "Sections of bt_config.conf that are named by a MAC address: the Timestamp key "
                       "read as Unix seconds, Name, the MAC address and LinkKey. A section is not by "
                       "itself proof of a connection.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2021-06-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Bluetooth Connections",
        "notes": "Reads every bt_config.conf the path matches; the report's located at line lists each "
                 "file read, and rows are not marked with their file. The nine registered zip images "
                 "checked on 2026-10-04 (anne_a15, galaxys10_a10, hc_pixel8pro_a16, kevin_pocox7_a15, "
                 "pixel7a_a14, samsunga53_a14, samsungs20_a13, sharon_a14, russell_pixel6a_a13) each "
                 "hold one such file. "
                 "Timestamp: in AOSP the key is written as time(NULL), Unix seconds, by "
                 "btif_storage_set_remote_device_property "
                 "(https://android.googlesource.com/platform/system/bt/+/"
                 "0f203f6d1e89e93686944d8589e869a4c2c129a0/btif/src/btif_storage.cc#202), which "
                 "btif_storage_add_remote_device calls each time it saves a device (same file, lines "
                 "793 to 799). At android-10.0.0_r1, android-13.0.0_r1 and android-14.0.0_r1 the one "
                 "call of btif_storage_add_remote_device in btif_dm.cc is in the device discovery "
                 "result handler (other files were not searched for callers) "
                 "(https://android.googlesource.com/platform/system/bt/+/"
                 "0f203f6d1e89e93686944d8589e869a4c2c129a0/btif/src/btif_dm.cc#1348), so that call "
                 "rewrites the value each time a discovery result for the address is saved. No "
                 "source read ties the key to a first connection or to a pairing. Vendor Bluetooth stacks were not "
                 "read, so what the key records on a Samsung or Xiaomi build is not established. A "
                 "section with no Timestamp key gives a blank Timestamp: 6 of the 17 sections on "
                 "those images have none.",
        "paths": ('*/bt_config.conf',),
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
            "russell_pixel6a_a13": "Android 13 | 4 rows",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
    "get_bluetoothAdapter": {
        "name": "Bluetooth Adapter Information",
        "description": "Each key and value line that comes before the first MAC address section of bt_config.conf, whichever section it is in.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2021-06-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Bluetooth Connections",
        "notes": "Reads every bt_config.conf the path matches; the report's located at line lists each "
                 "file read, and rows are not marked with their file. The nine registered zip images "
                 "checked on 2026-10-04 each hold one such file.",
        "paths": ('*/bt_config.conf',),
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
            "russell_pixel6a_a13": "Android 13 | 10 rows",
            "userb2_a13": "Android 13 | 10 rows",
        },
    }
}

import datetime
import os
import re

from scripts.ilapfuncs import artifact_processor
from scripts.artifacts.storagePathViews import unique_files

MAC_RE = re.compile(r'(\[[0-9a-f]{2}(?::[0-9a-f]{2}){5}\])', re.IGNORECASE)


@artifact_processor
def get_bluetoothConnections(context):
    data_list = []
    source_paths = []

    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        source_paths.append(file_found)

        name_value = timestamp_value = linkkey_value = macaddrf = ''
        first_round = True
        with open(file_found, "r", encoding='utf-8', errors='replace') as f:
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

    data_headers = (('Timestamp', 'datetime'), 'Device Name', 'MAC Address', 'Link Key')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_bluetoothAdapter(context):
    data_list = []
    source_paths = []

    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        source_paths.append(file_found)

        with open(file_found, "r", encoding='utf-8', errors='replace') as f:
            for line in f:
                if re.findall(MAC_RE, line):
                    break  # adapter info is the block before the first device
                if ' = ' in line:
                    splits = line.split(' = ')
                    data_list.append((splits[0], splits[1].strip()))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, '\n'.join(source_paths)
