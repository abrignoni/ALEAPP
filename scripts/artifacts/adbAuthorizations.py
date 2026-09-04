__artifacts_v2__ = {
    "adb_authorizations": {
        "name": "ADB Authorizations",
        "description": "Public keys the device accepted for Android Debug Bridge access, with the "
                       "host name written beside each key where the host supplied one and the "
                       "time each key last connected.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Device Connections",
        "notes": "Read from the adb_temp_keys.xml the platform keeps in its adb folder, ABX "
                 "binary XML on modern releases and plain XML on older ones. One row per adbKey "
                 "element. Last Connection is the lastConnection attribute in Unix milliseconds.\n"
                 "The key attribute holds the host's public key followed, where the host's adb "
                 "wrote one, by whitespace and a user@hostname comment. The platform itself "
                 "splits the value on whitespace and shows the second token as the name of the "
                 "paired computer, and Host reports that token as stored; it was present on 12 of "
                 "the 15 keys on the tested images, two of them with an empty user part. ADB "
                 "Public Key is the first token. A row means the device stored an authorization "
                 "for the host holding the matching private key, which is the key the computer "
                 "sent when the USB debugging prompt was accepted on the device; the key "
                 "identifies the key pair that computer's adb used. The platform's own comment on "
                 "this file says adbd reads only adb_keys for authorization and keeps "
                 "adb_temp_keys.xml to remove unused keys and to manage authorized wireless "
                 "debugging access points, so a device may also carry data/misc/adb/adb_keys, a "
                 "plain text list without timestamps, which this artifact does not read. "
                 "Reference: Android Open Source Project, AdbDebuggingManager.java, "
                 "frameworks/base/services/core/java/com/android/server/adb, class comment and "
                 "getPairedDevices. The path pattern is not anchored on a data/ prefix, because a "
                 "raw userdata partition image carries the same folder without one.",
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
        'Host',
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
            # The attribute is the public key followed, where the host wrote one, by a
            # user@hostname comment. AOSP AdbDebuggingManager.getPairedDevices splits it the same way.
            parts = (key.get('key') or '').split()
            data_list.append((
                _ms(key.get('lastConnection')),
                ' '.join(parts[1:]),
                parts[0] if parts else '',
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
