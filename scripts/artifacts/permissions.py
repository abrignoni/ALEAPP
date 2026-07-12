# pylint: disable=W0613
__artifacts_v2__ = {
    "get_permissions_trees": {
        "name": "Permission Trees",
        "description": "Parses declared permission trees (name and package) from the system packages.xml.",
        "author": "",
        "creation_date": "2021-01-28",
        "last_update_date": "2021-01-28",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
    "get_permissions_list": {
        "name": "Permissions",
        "description": "Parses declared permissions (name, package and protection level) from the system packages.xml.",
        "author": "",
        "creation_date": "2021-01-28",
        "last_update_date": "2021-01-28",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | 3060 rows",
            "galaxys10_a10": "Android 10 | 1784 rows",
            "hc_pixel8pro_a16": "Android 16 | 1970 rows",
            "kevin_pocox7_a15": "Android 15 | 2107 rows",
            "pixel7a_a14": "Android 14 | 1629 rows",
            "samsunga53_a14": "Android 14 | 2651 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 2793 rows",
            "russell_pixel6a_a13": "Android 13 | 1260 rows",
            "userb2_a13": "Android 13 | 1263 rows",
        },
    },
    "get_permissions_packages": {
        "name": "Package and Shared User",
        "description": "Parses packages and their shared user IDs with granted permissions from the system packages.xml.",
        "author": "",
        "creation_date": "2021-01-28",
        "last_update_date": "2021-01-28",
        "requirements": "none",
        "category": "Permissions",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 6388 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows, abxread, checkabx


def _iter_roots(files_found):
    '''Yield (root, file_found) for each non-mirror packages.xml that parses.'''
    slash = '\\' if is_platform_windows() else '/'
    for file_found in files_found:
        file_found = str(file_found)
        if 'mirror' in file_found.split(slash):
            continue
        if (checkabx(file_found)):
            root = abxread(file_found, False).getroot()
        else:
            root = _parse_xml(file_found)
        yield root, file_found


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
