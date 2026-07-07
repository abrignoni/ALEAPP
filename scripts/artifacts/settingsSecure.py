# pylint: disable=W0613
__artifacts_v2__ = {
    "get_settingsSecure": {
        "name": "settingsSecure",
        "description": "Filter for path xxx/yyy/system_ce/0",
        "author": "",
        "creation_date": "2020-04-02",
        "last_update_date": "2020-04-02",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/system/users/*/settings_secure.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
    }
}

import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo, is_platform_windows, abxread, checkabx

# Characters that are invalid in XML 1.0 (raw control chars) and cause "not well-formed (invalid token)"
INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
# A bare '&' not already part of a valid entity
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_root(file_found):
    '''Return the XML root, tolerating ABX, Android-11 rootless files, and invalid XML tokens.

    settings_secure.xml occasionally contains raw control characters or unescaped
    ampersands inside setting values, which make a plain ET.parse() raise
    "not well-formed (invalid token)". We recover by sanitizing the text; if it is
    still unparseable the file is skipped (None) rather than erroring the artifact.
    '''
    if (checkabx(file_found)):
        return abxread(file_found, True).getroot()
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = f.read()
        xml = INVALID_XML_CHARS.sub('', xml)
        xml = BARE_AMPERSAND.sub('&amp;', xml)
        # Android 11 stores these without a single enclosing root element
        if '<root>' not in xml:
            xml = re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>"
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'settingsSecure: skipping unparseable {file_found}: {ex}')
            return None


@artifact_processor
def get_settingsSecure(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-2]
        try:
            int(uid)
        except ValueError:
            continue  # uid was not a number
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            continue  # Skip mirror, it should be duplicate data

        root = _parse_root(file_found)
        if root is None:
            continue

        source_path = file_found
        for setting in root.iter('setting'):
            nme = setting.get('name')
            val = setting.get('value')
            if nme == 'bluetooth_name':
                data_list.append((uid, nme, val))
                logdevinfo(f"<b>Bluetooth name: </b>{val}")
            elif nme == 'mock_location':
                data_list.append((uid, nme, val))
            elif nme == 'android_id':
                data_list.append((uid, nme, val))
            elif nme == 'bluetooth_address':
                data_list.append((uid, nme, val))
                logdevinfo(f"<b>Bluetooth address: </b>{val}")

    data_headers = ('User', 'Name', 'Value')
    return data_headers, data_list, source_path
