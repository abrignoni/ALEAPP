# pylint: disable=W0613
__artifacts_v2__ = {
    "get_urluser": {
        "name": "ULR User Prefs",
        "description": "ULR User Prefs",
        "author": "Alexis 'Brigs' Brignoni",
        "creation_date": "2024-06-21",
        "last_update_date": "2024-06-21",
        "requirements": "",
        "category": "App Semantic Locations",
        "notes": "Thanks to Josh Hickman for the research",
        "paths": ('*/com.google.android.gms/shared_prefs/ULR_USER_PREFS.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 15 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 13 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 15 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 15 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 14 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 81 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 28 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 15 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 25 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 30 rows",
        },
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
def get_urluser(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('ULR_USER_PREFS.xml'):
            continue

        source_path = file_found
        root = _parse_xml(file_found)
        for child in root:
            jsondata = child.attrib
            name = jsondata['name']
            value = jsondata.get('value', '')
            data_list.append((name, value))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
