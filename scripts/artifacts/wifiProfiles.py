__artifacts_v2__ = {
    "get_wifiProfiles": {
        "name": "wifiProfiles",
        "description": "Wi-Fi network entries (SSID, keys, gateway MAC address and, where stored, timestamps) from WifiConfigStore.xml",
        "author": "@abrignoni",
        "creation_date": "2020-03-23",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "DefaultGwMacAddress is reported as stored. AOSP documents the "
                 "WifiConfiguration field defaultGwMacAddress as 'default Gateway MAC "
                 "address if known' (framework/java/android/net/wifi/WifiConfiguration.java "
                 "line 1345 at tag android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/tags/android-14.0.0_r1/framework/java/android/net/wifi/WifiConfiguration.java#1345). "
                 "The AOSP writer stores that field under the name DefaultGwMacAddress "
                 "(service/java/com/android/server/wifi/util/XmlUtil.java lines 351 and 646 at the same tag, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/tags/android-14.0.0_r1/service/java/com/android/server/wifi/util/XmlUtil.java#351). "
                 "Vendor builds were not traced. "
                 "Counts below are from the 36 corpus images that produced rows (151 rows). "
                 "SecurityMode is not a stored field. It is the text after the second double quote in ConfigKey, "
                 "so it is empty when ConfigKey is missing or has no quoted SSID, and an SSID holding a double quote would shift it. "
                 "AOSP builds ConfigKey from getKey(), which adds a hyphen and user id for networks that are not shared "
                 "and returns a Passpoint id as is (XmlUtil.java line 564, WifiConfiguration.java lines 3714-3727 at the same tag). "
                 "None of the 148 stored ConfigKey values had either form. "
                 "The other 3 rows have no ConfigKey: each is a Network element under WakeupConfigStoreData "
                 "(hc_pixel8pro_a16, hc_pixel8pro_a17, russell_pixel6a_a13). "
                 "The SecurityType values a network stores are not shown. 144 of the 151 networks store two, 1 stores one and 6 store none. "
                 "SSID is shown with its surrounding double quotes removed. PreSharedKey is shown as stored: "
                 "54 rows hold a value inside double quotes, and the quotes are in the cell. "
                 "The 4 values on galaxys10_a10 are unquoted uppercase hex of 76 or 88 characters. "
                 "Their encoding is not established, so do not read them as the passphrase. "
                 "An empty PreSharedKey cell does not prove the network had no key: AOSP can store the key as an encrypted section "
                 "with no name attribute (XmlUtil.java lines 469-474 at the same tag), which this module does not show. "
                 "None of the 36 images stored one; the 93 empty cells are 90 null elements and the 3 rows above. "
                 "If the XML does not parse, the module retries after removing control characters, replacing undecodable bytes and escaping bare ampersands, so a value on that path may differ from what is stored. If the retry also fails the file gives no rows. "
                 "That retry was not needed on any of the 36 images. "
                 "The three time columns are read from elements of those names as Unix milliseconds and shown in UTC. A zero, negative or non-numeric value is shown as empty. "
                 "Those names are not in the AOSP XmlUtil.java at that tag, and their writer, epoch and meaning are not established. "
                 "They are filled on cookbook_a11 and galaxys10_a10 only (5 rows, every value 13 digits) and empty on the other 34 images. "
                 "Timeline output is off: 146 of the 151 rows have no time. "
                 "CaptivePortal is the value attribute of an element of that name. Its writer and meaning are not established. "
                 "It is filled on galaxys10_a10 only (4 rows). AOSP writes a different element, CaptivePortalNeverDetected "
                 "(XmlUtil.java lines 1376 and 1398-1399 at the same tag), which this module does not show, so an empty cell says nothing about captive portal history. "
                 "LoginUrl is the text of an element of that name. Its writer is not established and it is empty on all 151 rows. "
                 "WEPKeys is the element's text. AOSP writes WEP keys as item child elements or as an encrypted section (XmlUtil.java lines 416 to 442 at android-14.0.0_r1), which this module does not show, so an empty cell does not prove the network had no WEP key. On the 36 images all 148 WEPKeys elements are null and the column is empty on all 151 rows.",
        "paths": ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
        "output_types": ["html", "tsv", "lava"],
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
                    fields['LastConnectedTime'], fields['semCreationTime'], fields['semUpdateTime'],
                    fields['SecurityMode'], fields['SSID'], fields['PreSharedKey'], fields['WEPKeys'],
                    fields['Password'], fields['Identity'], fields['DefaultGwMacAddress'],
                    fields['CaptivePortal'], fields['LoginUrl'], fields['IpAssignment']))

    data_headers = (
        ('LastConnectedTime', 'datetime'), ('semCreationTime', 'datetime'), ('semUpdateTime', 'datetime'),
        'SecurityMode', 'SSID', 'PreSharedKey', 'WEPKeys', 'Password', 'Identity', 'DefaultGwMacAddress',
        'CaptivePortal', 'LoginUrl', 'IpAssignment')
    return data_headers, data_list, '\n'.join(source_paths)
