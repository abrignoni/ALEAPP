# pylint: disable=W0613
__artifacts_v2__ = {
    "get_atrackerdetect": {
        "name": "atrackerdetect",
        "description": "",
        "author": "",
        "creation_date": "2022-01-08",
        "last_update_date": "2022-01-08",
        "requirements": "none",
        "category": "AirTags",
        "notes": "",
        "paths": ('*/com.apple.trackerdetect/shared_prefs/com.apple.trackerdetect_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "alert-triangle",
    }
}

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
def get_atrackerdetect(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        root = _parse_xml(file_found)

        for elem in root.iter():
            attribute = elem.attrib
            if attribute:
                data = attribute.get('name')
                if data.startswith('device'):
                    mac = data.split('_', 2)[1]
                    desc = data.split('_', 2)[2]
                    data_list.append((desc, mac, elem.text))
                else:
                    data_list.append((data, attribute.get('value'), ''))

    data_headers = ('Key', 'Value', 'Milliseconds from Last Boot Time')
    return data_headers, data_list, source_path
