# pylint: disable=W0613
__artifacts_v2__ = {
    "get_wifiConfigstore": {
        "name": "WiFi Config Store",
        "description": "Saved Wi-Fi network configuration details from WifiConfigStore.xml",
        "author": "",
        "creation_date": "2023-05-11",
        "last_update_date": "2023-05-11",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "",
        "paths": ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
        "output_types": "standard",
        "artifact_icon": "wifi",
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx

TEXT_FIELDS = {
    'ConfigKey': 'ConfigKey', 'SSID': 'SSID', 'BSSID': 'BSSID', 'PreSharedKey': 'PreSharedKey',
    'WEPKeys': 'WEPKeys', 'HiddenSSID': 'HiddenSSID', 'RandomizedMacAddress': 'RandomizedMacAddress',
    'CreatorName': 'CreatorName', 'CreationTime': 'CreationTime', 'ConnectChoice': 'ConnectChoice',
    'IpAssignment': 'IpAssignment',
}
COLUMNS = ['ConfigKey', 'SSID', 'BSSID', 'PreSharedKey', 'WEPKeys', 'HiddenSSID', 'RandomizedMacAddress',
           'CreatorName', 'CreationTime', 'ConnectChoice', 'ConnectChoiceTimeStamp', 'HasEverConnected',
           'IpAssignment', 'ProxySettings']


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _parse_xml(file_found):
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


def _xml_root(file_found):
    if checkabx(file_found):
        return abxread(file_found, False).getroot()
    return _parse_xml(file_found)


@artifact_processor
def get_wifiConfigstore(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('WifiConfigStore.xml'):
            continue
        source_paths.append(file_found)
        root = _xml_root(file_found)

        for network in root.iter('WifiConfiguration'):
            fields = {k: '' for k in COLUMNS}
            # iterate all descendant field elements (IpAssignment/ProxySettings can be nested)
            for elem in network.iter():
                name = elem.attrib.get('name')
                if not name:
                    continue
                value = elem.attrib.get('value', '')
                text = elem.text or ''
                if name in TEXT_FIELDS:
                    fields[name] = text
                elif name == 'ConnectChoiceTimeStamp':
                    fields['ConnectChoiceTimeStamp'] = _ms_to_utc(value) if value.isdigit() and int(value) > 1 else ''
                elif name == 'HasEverConnected':
                    fields['HasEverConnected'] = value
                elif name == 'ProxySettings':
                    fields['ProxySettings'] = f'{text} - {value}' if value else text

            if any(fields.values()):
                data_list.append(tuple(fields[c] for c in COLUMNS))

    data_headers = (
        'ConfigKey', 'SSID', 'BSSID', 'PreSharedKey', 'WEPKeys', 'HiddenSSID', 'RandomizedMacAddress',
        'CreatorName', 'CreationTime', 'ConnectChoice', ('ConnectChoiceTimeStamp', 'datetime'),
        'HasEverConnected', 'IpAssignment', 'ProxySettings')
    return data_headers, data_list, ', '.join(source_paths)
