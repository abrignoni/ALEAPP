__artifacts_v2__ = {
    "get_runtimePerms": {
        "name": "runtimePerms",
        "description": "Parses granted runtime permissions (user, type, name, permission, granted state and flags) from the runtime-permissions.xml file.",
        "author": "",
        "creation_date": "2021-01-25",
        "last_update_date": "2021-01-25",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/users/*/runtime-permissions.xml', '*/misc_de/*/apexdata/com.android.permission/runtime-permissions.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | 12258 rows",
            "galaxys10_a10": "Android 10 | 1005 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 6661 rows",
            "samsunga53_a14": "Android 14 | 21634 rows",
            "samsungs20_a13": "Android 13 | 19872 rows",
            "sharon_a14": "Android 14 | 11562 rows",
            "russell_pixel6a_a13": "Android 13 | 9423 rows",
            "userb2_a13": "Android 13 | 4528 rows",
        },
    }
}

import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_runtimePerms(context):
    files_found = context.get_files_found()

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        parts = file_found.split(slash)
        if 'mirror' in parts:
            continue
        elif 'system' in parts:
            user = parts[-2]
        elif 'misc_de' in parts:
            user = parts[-4]
        else:
            continue

        source_path = file_found
        root = _parse_xml(file_found)
        for elem in root:
            usagetype = elem.tag
            name = elem.attrib['name']
            for subelem in elem:
                permission = subelem.attrib['name']
                granted = subelem.attrib['granted']
                flags = subelem.attrib['flags']
                data_list.append((user, usagetype, name, permission, granted, flags))

    data_headers = ('User', 'Type', 'Name', 'Permission', 'Granted?', 'Flag')
    return data_headers, data_list, source_path
