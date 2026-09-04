__artifacts_v2__ = {
    "adb_authorizations": {
        "name": "ADB Authorizations",
        "description": "Public keys the device accepted for Android Debug Bridge access, with "
                       "the time each key last connected.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Device Connections",
        "notes": "Read from the adb_temp_keys.xml the platform keeps in its adb folder, ABX binary "
                 "XML on modern releases "
                 "and plain XML on older ones. One row per adbKey element. Last Connection is "
                 "the lastConnection attribute in Unix milliseconds.\n"
                 "A row means the device stored an authorization for the host holding the "
                 "matching private key, which is the key the computer sent when the user "
                 "accepted the USB debugging prompt. The key is the host's public key and "
                 "identifies that computer across devices; it does not name the computer. This "
                 "file holds the authorizations the platform tracks with a last-connection "
                 "time. A device may also carry data/misc/adb/adb_keys, a plain text list "
                 "without timestamps, which this artifact does not read. The path pattern is not "
                 "anchored on a data/ prefix, because a raw userdata partition image carries the "
                 "same folder without one.",
        "paths": ('*/misc/adb/adb_temp_keys.xml',),
        "output_types": "standard",
        "artifact_icon": "plug-connected",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 1 row",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, convert_unix_ts_to_utc, logfunc


def _root(path):
    if checkabx(path):
        return abxread(path, False).getroot()
    return ET.parse(path).getroot()


def _ms(value):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    return convert_unix_ts_to_utc(number)


@artifact_processor
def adb_authorizations(context):
    data_headers = (
        ('Last Connection', 'datetime'),
        'ADB Public Key',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or os.path.basename(file_found) != 'adb_temp_keys.xml':
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'ADB Authorizations: could not read {os.path.basename(file_found)}: {error}')
            continue
        rows = 0
        for key in root.iter('adbKey'):
            data_list.append((
                _ms(key.get('lastConnection')),
                key.get('key', ''),
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
