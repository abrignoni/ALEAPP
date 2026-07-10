# pylint: disable=W0612,W0613
__artifacts_v2__ = {
    "get_discreteNative": {
        "name": "DiscreteNative",
        "description": "Parses discrete app-ops permission usage (timestamp, package, permission module and operation, and usage duration) from the system appops discrete records.",
        "author": "",
        "creation_date": "2022-01-19",
        "last_update_date": "2022-01-19",
        "requirements": "none",
        "category": "Privacy Dashboard",
        "notes": "",
        "paths": ('*/system/appops/discrete/**',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

import datetime
import os
import pathlib
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx, logfunc


def oplist(opvalue):
    thisdict = {
        "26": "Camera",
        "1": "Location",
        "27": "Microphone"
    }
    result = thisdict.get(opvalue)
    if result is None:
        return opvalue
    return result


def timestampcalc(timevalue):
    if timevalue in (None, ''):
        return ''
    return datetime.datetime.fromtimestamp(int(timevalue) / 1000, datetime.timezone.utc)


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
def get_discreteNative(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        filename = str(pathlib.Path(file_found).name)

        if not os.path.isfile(file_found):
            continue

        source_path = file_found
        if (checkabx(file_found)):
            multi_root = False
            root = abxread(file_found, multi_root).getroot()
        else:
            root = _parse_xml(file_found)

        for elem in root:
            for subelem1 in elem:
                ptagattrib = subelem1.attrib["pn"]
                for subelem2 in subelem1:
                    otagattrib = subelem2.attrib['op']
                    ntattrib = ''
                    ndattrib = ''
                    atagattrib = ''
                    for subelem3 in subelem2:
                        atagattrib = subelem3.attrib.get('at', '')
                        for subelem4 in subelem3:
                            etagattrib = subelem4.attrib
                            ntattrib = etagattrib.get('nt')
                            ndattrib = etagattrib.get('nd')
                            if ndattrib is None:
                                ndattrib = ''
                            else:
                                ndattrib = round(int(ndattrib) / 1000, 1)
                    data_list.append((timestampcalc(ntattrib), ptagattrib, atagattrib, oplist(otagattrib), ndattrib, filename))

    data_headers = (('Timestamp', 'datetime'), 'Bundle', 'Module', 'Operation', 'Usage in Seconds', 'Source Filename')
    return data_headers, data_list, source_path
