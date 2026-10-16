__artifacts_v2__ = {
    "get_atrackerdetect": {
        "name": "atrackerdetect",
        "description": "Preferences from the Apple Tracker Detect Android app's shared_prefs XML, one row per "
                       "preference, reported as stored.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-01-08",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "AirTags",
        "notes": "Preference Name is the name attribute, Value is the value attribute and Element Text is the text "
                 "inside the element, each as stored; a column is blank where the element has no such part. On "
                 "pixel3_a12 the file holds one boolean named terms_and_conditions_read and two string preferences "
                 "named device_, then six colon-separated pairs of hexadecimal characters, then "
                 "_first_seen_timestamp_string_real_time, each with a 9-digit number as its element text. What the "
                 "six pairs identify, and the unit and starting point of the number, are not established: no source "
                 "for the app's preference format was found, so the number is reported as text and no date is "
                 "derived from it. That image carries the file under three storage paths of one app directory, "
                 "which are read once.",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.apple.trackerdetect | 3 rows",
        },
        "paths": ('*/com.apple.trackerdetect/shared_prefs/com.apple.trackerdetect_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "alert-triangle",
    }
}

import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files


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
def get_atrackerdetect(context):
    files_found = unique_files(context)

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        root = _parse_xml(file_found)

        for elem in root.iter():
            attribute = elem.attrib
            if attribute:
                data_list.append((attribute.get('name', ''), attribute.get('value', ''), elem.text or ''))

    data_headers = ('Preference Name', 'Value', 'Element Text')
    return data_headers, data_list, source_path
