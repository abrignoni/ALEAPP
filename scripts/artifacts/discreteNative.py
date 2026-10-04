# pylint: disable=W0612
__artifacts_v2__ = {
    "get_discreteNative": {
        "name": "DiscreteNative",
        "description": "Parses the last discrete app-ops entry recorded for each package and operation in each discrete file of the system appops discrete records: timestamp, package, the at attribute as stored, the operation (named for ops 1, 26 and 27, otherwise the stored number) and the nd value in seconds.",
        "author": "@abrignoni",
        "creation_date": "2022-01-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Privacy Dashboard",
        "notes": "Op 1 is shown as Fine Location, op 26 as Camera and op 27 as Microphone; AOSP "
                 "names them FINE_LOCATION, CAMERA and RECORD_AUDIO. Any other op is shown as its "
                 "stored number. References: AOSP AppOpsManager.java at tag "
                 "android-9.0.0_r1, which writes those op numbers out "
                 "(https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-9.0.0_r1/core/java/android/app/AppOpsManager.java#200), "
                 "and the app-op enum at tag android-12.0.0_r1, which gives the same three "
                 "numbers "
                 "(https://android.googlesource.com/platform/frameworks/proto_logging/+/refs/tags/android-12.0.0_r1/stats/enums/app/enums.proto#111). "
                 "The at, nt and nd attributes are defined in DiscreteRegistry.java at tag "
                 "android-12.0.0_r1 "
                 "(https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-12.0.0_r1/services/core/java/com/android/server/appop/DiscreteRegistry.java#162). "
                 "The module reads nt as Unix milliseconds and divides nd by 1000 to report "
                 "seconds. Only the last entry under each package and op element of a file is "
                 "reported.",
        "paths": ('*/system/appops/discrete/**',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | 1886 rows",
            "kevin_pocox7_a15": "Android 15 | 1720 rows",
            "pixel7a_a14": "Android 14 | 1948 rows",
            "samsunga53_a14": "Android 14 | 13 rows",
            "samsungs20_a13": "Android 13 | 41 rows",
            "sharon_a14": "Android 14 | 281 rows",
            "russell_pixel6a_a13": "Android 13 | 41 rows",
            "userb2_a13": "Android 13 | 13 rows",
        },
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
        "1": "Fine Location",
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
def get_discreteNative(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = str(pathlib.Path(file_found).name)

        if not os.path.isfile(file_found):
            continue

        source_paths.append(file_found)
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
    return data_headers, data_list, '\n'.join(source_paths)
