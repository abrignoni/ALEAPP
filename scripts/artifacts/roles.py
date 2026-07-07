# pylint: disable=W0613
__artifacts_v2__ = {
    "get_roles": {
        "name": "roles",
        "description": "",
        "author": "",
        "creation_date": "2021-01-25",
        "last_update_date": "2021-01-25",
        "requirements": "none",
        "category": "App Roles",
        "notes": "",
        "paths": ('*/system/users/*/roles.xml', '*/misc_de/*/apexdata/com.android.permission/roles.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
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
def get_roles(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        parts = file_found.split(slash)
        ver = ''
        if 'mirror' in parts:
            continue
        elif 'users' in parts:
            user = parts[-2]
            ver = 'Android 10'
        elif 'misc_de' in parts:
            user = parts[-4]
            ver = 'Android 11'
        else:
            continue

        source_path = file_found
        root = _parse_xml(file_found)
        for elem in root:
            holder = ''
            role = elem.attrib['name']
            for subelem in elem:
                holder = subelem.attrib['name']
            data_list.append((ver, user, role, holder))

    data_headers = ('Android Version', 'User', 'Role', 'Holder')
    return data_headers, data_list, source_path
