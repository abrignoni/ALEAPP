# pylint: disable=W0613
__artifacts_v2__ = {
    "get_bittorrentClientpref": {
        "name": "BitTorrent Prefs",
        "description": "Parses BitTorrent client preferences (key, value and text) from the com.bittorrent.client preferences XML.",
        "author": "",
        "creation_date": "2023-03-26",
        "last_update_date": "2023-03-26",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "",
        "paths": ('*/com.bittorrent.client/shared_prefs/com.bittorrent.client_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx, logfunc


def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp


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
def get_bittorrentClientpref(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        # check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            root = abxread(file_found, multi_root).getroot()
        else:
            root = _parse_xml(file_found)


        for elem in root:
            key = elem.attrib['name']
            value = elem.attrib.get('value')
            text = elem.text
            if key == 'BornOn':
                value = timestampcalc(value)
            data_list.append((key, value, text))

    data_headers = ('Key', 'Value', 'Text')
    return data_headers, data_list, source_path
