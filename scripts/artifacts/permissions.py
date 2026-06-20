# pylint: disable=W0613
__artifacts_v2__ = {
    "get_permissions_trees": {
        "name": "Permission Trees",
        "description": "",
        "author": "",
        "creation_date": "2021-01-28",
        "last_update_date": "2021-01-28",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
    },
    "get_permissions_list": {
        "name": "Permissions",
        "description": "",
        "author": "",
        "creation_date": "2021-01-28",
        "last_update_date": "2021-01-28",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
    },
    "get_permissions_packages": {
        "name": "Package and Shared User",
        "description": "",
        "author": "",
        "creation_date": "2021-01-28",
        "last_update_date": "2021-01-28",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows, abxread, checkabx


def _iter_roots(files_found):
    '''Yield (root, file_found) for each non-mirror packages.xml that parses.'''
    slash = '\\' if is_platform_windows() else '/'
    for file_found in files_found:
        file_found = str(file_found)
        if 'mirror' in file_found.split(slash):
            continue
        try:
            if (checkabx(file_found)):
                tree = abxread(file_found, False)
            else:
                tree = ET.parse(file_found)
        except ET.ParseError:
            logfunc('Parse error - Non XML file.')
            continue
        yield tree.getroot(), file_found


@artifact_processor
def get_permissions_trees(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for root, file_found in _iter_roots(files_found):
        source_path = file_found
        for elem in root:
            if elem.tag == 'permission-trees':
                for subelem in elem:
                    data_list.append((subelem.attrib.get('name', ''), subelem.attrib.get('package', '')))

    data_headers = ('Name', 'Package')
    return data_headers, data_list, source_path


@artifact_processor
def get_permissions_list(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for root, file_found in _iter_roots(files_found):
        source_path = file_found
        for elem in root:
            if elem.tag == 'permissions':
                for subelem in elem:
                    data_list.append((subelem.attrib.get('name', ''), subelem.attrib.get('package', ''), subelem.attrib.get('protection', '')))

    data_headers = ('Name', 'Package', 'Protection')
    return data_headers, data_list, source_path


@artifact_processor
def get_permissions_packages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for root, file_found in _iter_roots(files_found):
        source_path = file_found
        for elem in root:
            if elem.tag in ('permission-trees', 'permissions'):
                continue
            for subelem in elem:
                if subelem.tag == 'perms':
                    for sub_subelem in subelem:
                        data_list.append((elem.tag, elem.attrib.get('name', ''), sub_subelem.attrib.get('name', ''), sub_subelem.attrib.get('granted', '')))

    data_headers = ('Type', 'Package', 'Permission', 'Granted?')
    return data_headers, data_list, source_path
