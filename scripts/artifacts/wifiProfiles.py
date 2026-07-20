__artifacts_v2__ = {
    "get_wifiProfiles": {
        "name": "wifiProfiles",
        "description": "Saved Wi-Fi network profiles (SSID, keys, MAC, timestamps) from WifiConfigStore.xml",
        "author": "",
        "creation_date": "2020-03-23",
        "last_update_date": "2020-03-23",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "",
        "paths": ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "anne_a15": "Android 15 | 12 rows",
            "galaxys10_a10": "Android 10 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | 20 rows",
            "pixel7a_a14": "Android 14 | 11 rows",
            "samsunga53_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 18 rows",
            "russell_pixel6a_a13": "Android 13 | 9 rows",
            "userb2_a13": "Android 13 | 1 row",
        },
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor

TEXT_FIELDS = ('PreSharedKey', 'WEPKeys', 'LoginUrl', 'IpAssignment', 'Identity', 'Password', 'DefaultGwMacAddress')
TIME_FIELDS = ('semCreationTime', 'semUpdateTime', 'LastConnectedTime')


def _ms_to_utc(value):
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return ''
    if ms <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


def _parse_xml(file_found):
    '''Parse XML, recovering from invalid tokens (stray control chars / bare &).'''
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)', '&amp;', text)
        try:
            return ET.fromstring(text)
        except ET.ParseError:
            return ET.Element('empty')


@artifact_processor
def get_wifiProfiles(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        source_paths.append(file_found)
        root = _parse_xml(file_found)

        for node in root.iter('Network'):
            # Reset every field per network so values don't bleed between profiles
            fields = {k: '' for k in ('SecurityMode', 'SSID', 'CaptivePortal') + TEXT_FIELDS + TIME_FIELDS}
            for elem in node.iter():
                if elem.tag == node.tag:
                    continue
                name = elem.attrib.get('name')
                if not name:
                    continue
                if name == 'ConfigKey':
                    cut = (elem.text or '').split('"')
                    fields['SecurityMode'] = cut[2] if len(cut) > 2 else ''
                elif name == 'SSID':
                    fields['SSID'] = (elem.text or '').strip('"')
                elif name in TEXT_FIELDS:
                    fields[name] = elem.text or ''
                elif name in TIME_FIELDS:
                    fields[name] = _ms_to_utc(elem.attrib.get('value'))
                elif name == 'CaptivePortal':
                    fields['CaptivePortal'] = elem.attrib.get('value', '')

            if any(fields.values()):
                data_list.append((
                    fields['SecurityMode'], fields['SSID'], fields['PreSharedKey'], fields['WEPKeys'],
                    fields['Password'], fields['Identity'], fields['DefaultGwMacAddress'],
                    fields['semCreationTime'], fields['semUpdateTime'], fields['LastConnectedTime'],
                    fields['CaptivePortal'], fields['LoginUrl'], fields['IpAssignment']))

    data_headers = (
        'SecurityMode', 'SSID', 'PreSharedKey', 'WEPKeys', 'Password', 'Identity', 'DefaultGwMacAddress',
        ('semCreationTime', 'datetime'), ('semUpdateTime', 'datetime'), ('LastConnectedTime', 'datetime'),
        'CaptivePortal', 'LoginUrl', 'IpAssignment')
    return data_headers, data_list, ', '.join(source_paths)
