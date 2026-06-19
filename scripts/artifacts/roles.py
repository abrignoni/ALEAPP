# pylint: disable=W0613
__artifacts_v2__ = {
    "get_roles": {
        "name": "roles",
        "description": "",
        "author": "",
        "creation_date": "2021-01-25",
        "last_update_date": "2021-01-25",
        "requirements": "none",
        "category": "App Roles",
        "notes": "",
        "paths": ('*/system/users/*/roles.xml', '*/misc_de/*/apexdata/com.android.permission/roles.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows


@artifact_processor
def get_roles(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        parts = file_found.split(slash)
        ver = ''
        if 'mirror' in parts:
            continue
        elif 'users' in parts:
            user = parts[-2]
            ver = 'Android 10'
        elif 'misc_de' in parts:
            user = parts[-4]
            ver = 'Android 11'
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
            holder = ''
            role = elem.attrib['name']
            for subelem in elem:
                holder = subelem.attrib['name']
            data_list.append((ver, user, role, holder))

    data_headers = ('Android Version', 'User', 'Role', 'Holder')
    return data_headers, data_list, source_path
