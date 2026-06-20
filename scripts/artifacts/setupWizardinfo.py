# pylint: disable=W0613
__artifacts_v2__ = {
    "get_setupWizardinfo": {
        "name": "setupWizardinfo",
        "description": "",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/com.google.android.settings.intelligence/shared_prefs/setup_wizard_info.xml',),
        "output_types": "standard",
        "artifact_icon": "info",
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
def get_setupWizardinfo(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('setup_wizard_info.xml'):
            continue  # Skip all other files

        source_path = file_found
        root = _parse_xml(file_found)
        for elem in root:
            item = elem.attrib
            if item['name'] == 'suw_finished_time_ms':
                timestamp = datetime.datetime.fromtimestamp(int(item['value']) / 1000, datetime.timezone.utc)
                data_list.append((timestamp, item['name']))

    data_headers = (('Timestamp', 'datetime'), 'Name')
    return data_headers, data_list, source_path
