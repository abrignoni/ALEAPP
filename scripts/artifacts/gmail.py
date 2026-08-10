__artifacts_v2__ = {
    "get_gmailActive": {
        "name": "GmailActive",
        "description": "gmailActive: Get gmail account information",
        "author": "Joshua James {joshua@dfirscience.org}",
        "creation_date": "2021-11-08",
        "last_update_date": "2021-11-08",
        "requirements": "none",
        "category": "Gmail",
        "notes": "",
        "paths": ('*/com.google.android.gm/shared_prefs/Gmail.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "mail",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 1 row",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.gm vc 64361093 | 1 row",
            "samsunga53_a14": "Android 14 | com.google.android.gm vc 65429598 | 1 row",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 1 row",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 1 row",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 1 row",
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
def get_gmailActive(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = str(files_found[0])
    root = _parse_xml(source_path)
    for child in root:
        if child.attrib['name'] == "active-account":
            logfunc("Active gmail account found: " + child.text)
            data_list.append((child.text,))

    data_headers = ('Active Gmail Address',)
    return data_headers, data_list, source_path
