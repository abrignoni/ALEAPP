# pylint: disable=W0613
__artifacts_v2__ = {
    "get_rarlabPreferences": {
        "name": "rarlabPreferences",
        "description": "",
        "author": "",
        "creation_date": "2023-03-29",
        "last_update_date": "2023-03-29",
        "requirements": "none",
        "category": "RAR Lab Prefs",
        "notes": "",
        "paths": ('*/com.rarlab.rar_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "html_columns": ['Text'],
    }
}

import json
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx, logfunc


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
def get_rarlabPreferences(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.rarlab.rar_preferences.xml'):
            source_path = file_found

            # check if file is abx
            if (checkabx(file_found)):
                multi_root = False
                root = abxread(file_found, multi_root).getroot()
            else:
                root = _parse_xml(file_found)

            for elem in root.iter():
                name = elem.attrib.get('name')
                value = elem.attrib.get('value')
                text = elem.text
                if name is not None:
                    if name == 'ArcHistory' or name == 'ExtrPathHistory':
                        items = json.loads(text)
                        agg = ''
                        for x in items:
                            agg = agg + f'{x}<br>'
                        data_list.append((name,agg,value))
                    else:
                        data_list.append((name,text,value))

    data_headers = ('Key', 'Text', 'Value')
    return data_headers, data_list, source_path
