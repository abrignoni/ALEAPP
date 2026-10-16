__artifacts_v2__ = {
    "get_appopSetupWiz": {
        "name": "appopSetupWiz",
        "description": "Records selected under com.google.android.setupwizard in appops.xml, with stored t "
                       "and nested XML attributes. Converted dates retain the existing positive-millisecond policy. "
                       "This path does not cover Android 14 and later appops_accesses.xml records.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "Nested tags and attributes are source values, without operation/state code interpretation. "
                 "Blank dates follow the existing nonpositive timestamp policy or indicate missing/invalid text. "
                 "These observations do not establish a wipe or setup event. Version-specific meanings remain unverified.",
        "paths": ('*/system/appops.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 14 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 11 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 26 rows",
            "userb2_a13": "Android 13 | 12 rows",
        },
    }
}

import datetime
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


def _timestamp(raw_t):
    if raw_t is None:
        return '', 'Missing'
    try:
        value = int(raw_t)
    except ValueError:
        return '', 'Invalid integer'
    if value <= 0:
        return '', 'Nonpositive'
    try:
        timestamp = datetime.datetime.fromtimestamp(value / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return '', 'Out of range'
    return timestamp, 'Converted positive milliseconds'


@artifact_processor
def get_appopSetupWiz(context):
    files_found = context.get_files_found()

    data_list = []
    sources = []
    row_sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('appops.xml'):
            continue  # Skip all other files

        source = context.get_relative_path(file_found)
        first_row = len(data_list)
        # check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            root = abxread(file_found, multi_root).getroot()
        else:
            root = _parse_xml(file_found)

        for elem in root.iter('pkg'):
            if elem.attrib['n'] == 'com.google.android.setupwizard':
                pkg = elem.attrib['n']
                for subelem in elem:
                    for subelem2 in subelem:
                        for subelem3 in subelem2:
                            raw_t = subelem3.attrib.get('t')
                            timestamp, status = _timestamp(raw_t)
                            data_list.append((timestamp, raw_t, status, pkg,
                                              subelem.tag, json.dumps(subelem.attrib),
                                              subelem2.tag, json.dumps(subelem2.attrib),
                                              subelem3.tag, json.dumps(subelem3.attrib)))
                            row_sources.append(source)
        if len(data_list) > first_row and file_found not in sources:
            sources.append(file_found)

    data_headers = (('Timestamp', 'datetime'), 'Stored t', 'Timestamp Status', 'Package',
                    'Package Child Tag', 'Package Child Attributes',
                    'Nested Record Tag', 'Nested Record Attributes',
                    'State Record Tag', 'State Record Attributes')
    if len(sources) > 1:
        data_headers += ('Source File',)
        data_list = [row + (source,) for row, source in zip(data_list, row_sources)]
    return data_headers, data_list, '\n'.join(sources)
