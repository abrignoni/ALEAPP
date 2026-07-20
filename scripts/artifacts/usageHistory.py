__artifacts_v2__ = {
    "get_usageHistory": {
        "name": "Usagehistory",
        "description": "Parses application usage history (timestamp, package and component) from the usage-history.xml file.",
        "author": "",
        "creation_date": "2022-07-06",
        "last_update_date": "2022-07-06",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/usage-history.xml',),
        "output_types": "standard",
        "artifact_icon": "globe",
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


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
def get_usageHistory(context):
    files_found = context.get_files_found()

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('usage-history.xml'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        root = _parse_xml(source_path)
        for elem in root:
            for subelem in elem:
                pkg = elem.attrib['name']
                subitem = subelem.attrib['name']
                time = subelem.attrib['lrt']
                if time and time != ' ':
                    time = datetime.datetime.fromtimestamp(int(time) / 1000, datetime.timezone.utc)
                else:
                    time = ''
                data_list.append((time, pkg, subitem))

    data_headers = (('Timestamp', 'datetime'), 'Package', 'Subitem')
    return data_headers, data_list, source_path
