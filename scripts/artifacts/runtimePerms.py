# pylint: disable=W0613
__artifacts_v2__ = {
    "get_runtimePerms": {
        "name": "runtimePerms",
        "description": "",
        "author": "",
        "creation_date": "2021-01-25",
        "last_update_date": "2021-01-25",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/users/*/runtime-permissions.xml', '*/misc_de/*/apexdata/com.android.permission/runtime-permissions.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows


@artifact_processor
def get_runtimePerms(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        parts = file_found.split(slash)
        if 'mirror' in parts:
            continue
        elif 'system' in parts:
            user = parts[-2]
        elif 'misc_de' in parts:
            user = parts[-4]
        else:
            continue

        try:
            tree = ET.parse(file_found)
        except ET.ParseError:
            logfunc('Parse error - Non XML file.')
            continue

        source_path = file_found
        root = tree.getroot()
        for elem in root:
            usagetype = elem.tag
            name = elem.attrib['name']
            for subelem in elem:
                permission = subelem.attrib['name']
                granted = subelem.attrib['granted']
                flags = subelem.attrib['flags']
                data_list.append((user, usagetype, name, permission, granted, flags))

    data_headers = ('User', 'Type', 'Name', 'Permission', 'Granted?', 'Flag')
    return data_headers, data_list, source_path
