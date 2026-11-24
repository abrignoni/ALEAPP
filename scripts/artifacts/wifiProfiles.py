__artifacts_v2__ = {
    "get_wifiProfiles": {
        "name": "wifiProfiles",
        "description": "Wi-Fi network entries (SSID, keys, gateway MAC address, randomized MAC address, the apps that created and last changed each network and, where stored, timestamps) from WifiConfigStore.xml",
        "author": "@abrignoni",
        "creation_date": "2020-03-23",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "DefaultGwMacAddress is reported as stored. AOSP documents the "
                 "WifiConfiguration field defaultGwMacAddress as 'default Gateway MAC "
                 "address if known' (framework/java/android/net/wifi/WifiConfiguration.java "
                 "line 1345 at tag android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/framework/java/android/net/wifi/WifiConfiguration.java#1345). "
                 "The AOSP writer stores that field under the name DefaultGwMacAddress "
                 "(service/java/com/android/server/wifi/util/XmlUtil.java lines 351 and 646 at the same tag, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/util/XmlUtil.java#351). "
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
                 "WEPKeys is the element's text. AOSP writes WEP keys as item child elements or as an encrypted section (XmlUtil.java lines 416 to 442 at android-14.0.0_r1), which this module does not show, so an empty cell does not prove the network had no WEP key. On the 36 images all 148 WEPKeys elements are null and the column is empty on all 151 rows. "
                 "HiddenSSID, HasEverConnected, CreatorName, CreatorUid, LastUpdateName, LastUpdateUid, RandomizedMacAddress and MacRandomizationSetting "
                 "are the values the AOSP writer stores under those names (XmlUtil.java lines 569, 656-659, 666-669 and 1397 at the same tag), shown as stored. "
                 "AOSP documents hiddenSSID as a network that does not broadcast its SSID (WifiConfiguration.java lines 1225-1229), "
                 "creatorUid and lastUpdateUid as the uid of the app that created and last modified the configuration, and creatorName and "
                 "lastUpdateName as that app's name from PackageManager.getNameForUid (lines 1374-1409). "
                 "hasEverConnected is set to true on a successful connection, and to false when no earlier value was stored or the credentials change, such as a password change (lines 2440-2446). "
                 "RandomizedMacAddress is the randomized MAC address the framework keeps for the network. AOSP says the device may or may not use it, "
                 "depending on the user's preference (lines 1885-1897), so read it with MacRandomizationSetting. "
                 "MacRandomizationSetting is the stored number followed by the name of the AOSP constant it equals (lines 1799-1818): "
                 "0 none (the factory MAC), 1 persistent, 2 non-persistent and 3 auto. Any other number is shown alone. "
                 "On the 36 images these eight columns are filled on 148 of the 151 rows and empty on the 3 WakeupConfigStoreData rows. "
                 "MacRandomizationSetting is 3 on 141 rows, 1 on 6 and 0 on 1. "
                 "Store is User <n> for a file under misc_ce/<n> or data_mirror/misc_ce/<volume>/<n>, the per-user store, and Shared for any other path. "
                 "AOSP keeps one shared store and one store per user (framework/java/android/net/wifi/util/Environment.java lines 48-61 at the same tag). "
                 "Shared also covers the older misc/wifi path, whose writer was not traced. "
                 "A data_mirror copy is not read when the misc_ce copy for the same user was also found and holds the same bytes. "
                 "On the 39 images 35 data_mirror copies were found and each matched its misc_ce copy. 148 rows are Shared and 3 are User 0.",
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
    },
    "get_wifiPasspointProviders": {
        "name": "Wi-Fi Passpoint Providers",
        "description": "Passpoint provider entries (FQDN, friendly name, realm, credential and creating package) from WifiConfigStore.xml",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-24",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "Each row is a Provider element of WifiConfigStore.xml, which AOSP writes from PasspointConfigUserStoreData "
                 "(service/java/com/android/server/wifi/hotspot2/PasspointConfigUserStoreData.java lines 183-213 at tag android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/hotspot2/PasspointConfigUserStoreData.java#198). "
                 "PackageName, CreatorUID and HasEverConnected are the provider's values of those names (lines 201-210). "
                 "FQDN and FriendlyName come from its HomeSP section, which AOSP documents as the fully qualified domain name and friendly name of the home service provider "
                 "(framework/java/android/net/wifi/hotspot2/pps/HomeSp.java lines 61-85; service/java/com/android/server/wifi/hotspot2/PasspointXmlUtils.java lines 315-316). "
                 "Realm and the two credential times come from its Credential section (PasspointXmlUtils.java lines 341-344). "
                 "Username and Password come from the UserCredential section inside it (lines 401-403) and IMSI from the SimCredential section (line 450). "
                 "The Username and Password values of the subscription and policy update sections are not reported. "
                 "AOSP documents the stored password as Base64-encoded (framework/java/android/net/wifi/hotspot2/pps/Credential.java lines 195-198). "
                 "Password (as stored) is the stored text. On the 8 providers that hold one it ends with a line break. "
                 "Password (Base64 decoded) is that text decoded as Base64 and read as UTF-8 text, and is blank when it is not valid Base64 or not UTF-8. "
                 "IMSI is shown as stored. AOSP expects digits that may end with an asterisk for prefix matching (Credential.java lines 818-821). "
                 "The four time columns are read as milliseconds since 1970 in UTC, as AOSP documents them (Credential.java lines 59-83; "
                 "framework/java/android/net/wifi/hotspot2/PasspointConfiguration.java lines 269-295). AOSP uses Long.MIN_VALUE for an unset time. "
                 "That value, zero and any negative value are shown blank. On the 39 images every provider held Long.MIN_VALUE in all four, "
                 "so the time columns are empty and no row has a time. "
                 "Store is User <n> for a file under misc_ce/<n> or data_mirror/misc_ce/<volume>/<n> and Shared for any other path, "
                 "and an identical data_mirror copy is not read, as in the wifiProfiles artifact. "
                 "Of the 39 images run, 10 held providers, 13 in all, every one in a User 0 store: 8 with a UserCredential and 5 with a SimCredential. "
                 "A provider in a store for a user other than 0 is not exercised on real data.",
        "paths": ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "wifi",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "userb2_a13": "Android 13 | 2 rows",
        },
    },
}

import base64
import binascii
import datetime
import filecmp
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor

TEXT_FIELDS = ('PreSharedKey', 'WEPKeys', 'LoginUrl', 'IpAssignment', 'Identity', 'Password', 'DefaultGwMacAddress',
               'CreatorName', 'LastUpdateName', 'RandomizedMacAddress')
VALUE_FIELDS = ('HiddenSSID', 'HasEverConnected', 'CreatorUid', 'LastUpdateUid', 'MacRandomizationSetting')
# WifiConfiguration.RANDOMIZATION_* constants (WifiConfiguration.java lines 1802-1818 at android-14.0.0_r1).
MAC_RANDOMIZATION = {'0': 'none', '1': 'persistent', '2': 'non-persistent', '3': 'auto'}
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


_USER_STORE = re.compile(r'(?:^|/)misc_ce/(\d+)/(.*)$')
_MIRROR_STORE = re.compile(r'(?:^|/)data_mirror/misc_ce/[^/]+/(\d+)/(.*)$')


def _store(relative_path):
    '''User <n> for a store under misc_ce/<n> or data_mirror/misc_ce/<volume>/<n>; Shared otherwise.'''
    path = relative_path.replace('\\', '/')
    match = _MIRROR_STORE.search(path) or _USER_STORE.search(path)
    return f'User {match.group(1)}' if match else 'Shared'


def _store_files(context):
    '''The matched files, leaving out a data_mirror copy whose live misc_ce copy was also
    found and holds the same bytes.'''
    files = [str(f) for f in context.get_files_found()]
    live = {}
    for file_found in files:
        path = context.get_relative_path(file_found).replace('\\', '/')
        match = _USER_STORE.search(path)
        if match and not _MIRROR_STORE.search(path):
            live.setdefault(match.groups(), []).append(file_found)
    kept = []
    for file_found in files:
        match = _MIRROR_STORE.search(context.get_relative_path(file_found).replace('\\', '/'))
        if match and any(filecmp.cmp(file_found, other, shallow=False) for other in live.get(match.groups(), [])):
            continue
        kept.append(file_found)
    return kept


def _value(elem):
    '''A typed XmlUtil value: the value attribute, else the element text; blank for a null element.'''
    if elem is None or elem.tag == 'null':
        return ''
    return elem.attrib['value'] if 'value' in elem.attrib else (elem.text or '')


def _named(section, name):
    '''The direct child of section that carries name="<name>", or None.'''
    if section is None:
        return None
    return next((child for child in section if child.attrib.get('name') == name), None)


def _decoded_password(stored):
    '''The Base64 decoding of a stored Passpoint password, blank when it is not Base64 or not UTF-8 text.'''
    if not stored:
        return ''
    try:
        return base64.b64decode(stored.strip(), validate=True).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError, ValueError):
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
    data_list = []
    source_paths = []
    for file_found in _store_files(context):
        file_found = str(file_found)
        source_paths.append(file_found)
        root = _parse_xml(file_found)
        store = _store(context.get_relative_path(file_found))

        for node in root.iter('Network'):
            # Reset every field per network so values don't bleed between profiles
            fields = {k: '' for k in ('SecurityMode', 'SSID', 'CaptivePortal') + TEXT_FIELDS + VALUE_FIELDS + TIME_FIELDS}
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
                elif name in VALUE_FIELDS:
                    fields[name] = elem.attrib.get('value', '')
                elif name in TIME_FIELDS:
                    fields[name] = _ms_to_utc(elem.attrib.get('value'))
                elif name == 'CaptivePortal':
                    fields['CaptivePortal'] = elem.attrib.get('value', '')

            if any(fields.values()):
                setting = fields['MacRandomizationSetting']
                if setting in MAC_RANDOMIZATION:
                    setting = f'{setting} ({MAC_RANDOMIZATION[setting]})'
                data_list.append((
                    fields['LastConnectedTime'], fields['semCreationTime'], fields['semUpdateTime'],
                    fields['SecurityMode'], fields['SSID'], fields['PreSharedKey'], fields['WEPKeys'],
                    fields['Password'], fields['Identity'], fields['DefaultGwMacAddress'],
                    fields['CaptivePortal'], fields['LoginUrl'], fields['IpAssignment'],
                    fields['HiddenSSID'], fields['HasEverConnected'], fields['RandomizedMacAddress'], setting,
                    fields['CreatorName'], fields['CreatorUid'], fields['LastUpdateName'], fields['LastUpdateUid'],
                    store))

    data_headers = (
        ('LastConnectedTime', 'datetime'), ('semCreationTime', 'datetime'), ('semUpdateTime', 'datetime'),
        'SecurityMode', 'SSID', 'PreSharedKey', 'WEPKeys', 'Password', 'Identity', 'DefaultGwMacAddress',
        'CaptivePortal', 'LoginUrl', 'IpAssignment', 'HiddenSSID', 'HasEverConnected', 'RandomizedMacAddress',
        'MacRandomizationSetting', 'CreatorName', 'CreatorUid', 'LastUpdateName', 'LastUpdateUid', 'Store')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_wifiPasspointProviders(context):
    data_list = []
    source_paths = []
    for file_found in _store_files(context):
        root = _parse_xml(file_found)
        providers = list(root.iter('Provider'))
        if not providers:
            continue
        source_paths.append(file_found)
        store = _store(context.get_relative_path(file_found))
        for provider in providers:
            config = provider.find('Configuration')
            home = config.find('HomeSP') if config is not None else None
            credential = config.find('Credential') if config is not None else None
            user = credential.find('UserCredential') if credential is not None else None
            sim = credential.find('SimCredential') if credential is not None else None
            password = _value(_named(user, 'Password'))
            data_list.append((
                _ms_to_utc(_value(_named(credential, 'CreationTime'))),
                _ms_to_utc(_value(_named(credential, 'ExpirationTime'))),
                _ms_to_utc(_value(_named(config, 'SubscriptionCreationTime'))),
                _ms_to_utc(_value(_named(config, 'SubscriptionExpirationTime'))),
                _value(_named(home, 'FQDN')),
                _value(_named(home, 'FriendlyName')),
                _value(_named(credential, 'Realm')),
                _value(_named(provider, 'PackageName')),
                _value(_named(provider, 'CreatorUID')),
                _value(_named(provider, 'HasEverConnected')),
                _value(_named(user, 'Username')),
                password,
                _decoded_password(password),
                _value(_named(sim, 'IMSI')),
                store,
            ))

    data_headers = (
        ('Credential CreationTime', 'datetime'), ('Credential ExpirationTime', 'datetime'),
        ('SubscriptionCreationTime', 'datetime'), ('SubscriptionExpirationTime', 'datetime'),
        'FQDN', 'FriendlyName', 'Realm', 'PackageName', 'CreatorUID', 'HasEverConnected', 'Username',
        'Password (as stored)', 'Password (Base64 decoded)', 'IMSI', 'Store')
    return data_headers, data_list, '\n'.join(source_paths)
