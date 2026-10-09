__artifacts_v2__ = {
    "get_roles": {
        "name": "roles",
        "description": "Parses the roles in the roles.xml file, one row per returned direct-child name occurrence, with the source path variant, user and role. A role with no returned child name has one blank row.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-01-25",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "App Roles",
        "notes": "Source Path Variant records the collected path, not an Android version. "
                 "Every direct child with a name attribute is reported in XML order, including "
                 "blank names, duplicates and named children with other tags. A blank Holder row "
                 "means no child name was returned, not proof that no holder exists. Missing child "
                 "or role name attributes are diagnosed; malformed children or roles alone are "
                 "skipped. Source File is included only when rows come from multiple distinct "
                 "evidence-relative origins. Historical Anne, HC Pixel and Samsung A53 runs had no "
                 "multiple-holder role; that boundary uses constructed XML. Files under a path component named "
                 "mirror are skipped. A copy under data_mirror/misc_de/<volume>/<user> is not read when "
                 "the extraction also holds data/misc_de/<user> roles.xml for the same user beside it; "
                 "the skip is written to the run log and the two copies are not compared. On "
                 "samsunga53_a14 the archive listing gives both copies the same size and CRC-32, and "
                 "the artifact returned 76 rows before this rule and 38 with it. Any other copy "
                 "under data_mirror is read.",
        "paths": ('*/system/users/*/roles.xml', '*/misc_de/*/apexdata/com.android.permission/roles.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | 40 rows",
            "galaxys10_a10": "Android 10 | 8 rows",
            "hc_pixel8pro_a16": "Android 16 | 44 rows",
            "kevin_pocox7_a15": "Android 15 | 40 rows",
            "pixel7a_a14": "Android 14 | 38 rows",
            "samsunga53_a14": "Android 14 | 38 rows",
            "samsungs20_a13": "Android 13 | 63 rows",
            "sharon_a14": "Android 14 | 38 rows",
            "russell_pixel6a_a13": "Android 13 | 66 rows",
            "userb2_a13": "Android 13 | 33 rows",
        },
    }
}

import json
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows


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


_MISC_DE = re.compile(r'(^|.*/)data/misc_de/(\d+)/apexdata/com\.android\.permission/roles\.xml$')
_MISC_DE_MIRROR = re.compile(
    r'(^|.*/)data_mirror/misc_de/[^/]+/(\d+)/apexdata/com\.android\.permission/roles\.xml$')


def _mirror_duplicates(context, files_found):
    """Files under data_mirror/misc_de whose data/misc_de counterpart for the same user is present.

    An extraction can hold misc_de a second time under data_mirror (samsunga53_a14 does), so
    one roles.xml is matched at two paths. The data/misc_de spelling is the one kept.
    """
    kept = set()
    mirrors = {}
    for file_found in files_found:
        relative = str(context.get_relative_path(str(file_found))).replace('\\', '/')
        match = _MISC_DE.match(relative)
        if match:
            kept.add((match.group(1), match.group(2)))
            continue
        match = _MISC_DE_MIRROR.match(relative)
        if match:
            mirrors[str(file_found)] = (match.group(1), match.group(2))
    return {path for path, key in mirrors.items() if key in kept}


def _role_diagnostic(value):
    text = str(value)
    return json.dumps(text[:240], ensure_ascii=True) + (' [truncated]' if len(text) > 240 else '')


@artifact_processor
def get_roles(context):
    files_found = context.get_files_found()

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_paths = []
    origins = []
    contributors = []
    duplicates = _mirror_duplicates(context, files_found)

    for file_found in files_found:
        file_found = str(file_found)
        if file_found in duplicates:
            logfunc('Roles: not read, the same user\'s data/misc_de copy is present: '
                    f'{_role_diagnostic(context.get_relative_path(file_found))}')
            continue

        parts = file_found.split(slash)
        # Which path the file was collected from, not an OS version: both forms occur
        # across Android releases, so the path cannot establish one.
        path_variant = ''
        if 'mirror' in parts:
            continue
        elif 'users' in parts:
            user = parts[-2]
            path_variant = 'system/users/*/roles.xml'
        elif 'misc_de' in parts:
            user = parts[-4]
            path_variant = 'misc_de/*/apexdata/com.android.permission/roles.xml'
        else:
            continue

        source_paths.append(file_found)
        root = _parse_xml(file_found)
        relative = context.get_relative_path(file_found)
        first_row = len(data_list)
        for role_ordinal, elem in enumerate(root, 1):
            if 'name' not in elem.attrib:
                logfunc(f'Roles: missing role name at {_role_diagnostic(relative)}; role ordinal {role_ordinal}')
                continue
            role = elem.attrib['name']
            holders = []
            for child_ordinal, subelem in enumerate(elem, 1):
                if 'name' not in subelem.attrib:
                    logfunc(f'Roles: missing child name at {_role_diagnostic(relative)}; role ordinal {role_ordinal}; child ordinal {child_ordinal}')
                    continue
                holders.append(subelem.attrib['name'])
            for holder in holders or ['']:
                data_list.append((path_variant, user, role, holder))
                origins.append(relative)
        if len(data_list) > first_row and relative not in contributors:
            contributors.append(relative)

    data_headers = ('Source Path Variant', 'User', 'Role', 'Holder')
    if len(contributors) > 1:
        data_headers += ('Source File',)
        data_list = [row + (origin,) for row, origin in zip(data_list, origins)]
    return data_headers, data_list, '\n'.join(source_paths)
