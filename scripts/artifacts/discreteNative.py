# pylint: disable=W0612,W0613
__artifacts_v2__ = {
    "get_discreteNative": {
        "name": "DiscreteNative",
        "description": "",
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
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx


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
            tree = abxread(file_found, multi_root)
        else:
            tree = ET.parse(file_found)
        root = tree.getroot()

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
