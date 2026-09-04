__artifacts_v2__ = {
    "settings_ssaid": {
        "name": "SSAID Per App",
        "description": "The SSAID the platform issued to each app for an Android user, the "
                       "value an app reads as its Android ID, with the package and uid it was "
                       "issued to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Read from the per-user settings_ssaid.xml under the system users folder. The "
                 "file is ABX binary XML on modern releases and plain XML on older ones, and in either "
                 "form it can hold more than one root element, so a single-root read is retried "
                 "in the multiple-root mode. One row per setting element, and User ID is the folder the "
                 "file sits in. The pattern is not anchored on a data/ prefix, because a raw "
                 "userdata partition image carries the same folder without one.\n"
                 "Package is the package the value was issued to and UID is the setting's name "
                 "attribute, which the platform uses to hold that package's uid. SSAID is the "
                 "value, which is what the app reads back as its Android ID; the same package on "
                 "a different user has a different value, so a value ties an app to one user on "
                 "one device.\n"
                 "One row per user is named userkey against the android package. That is the "
                 "per-user seed the platform keeps rather than an identifier issued to an app, "
                 "and it is reported as stored. Setting ID and Default Set By System are "
                 "reported as stored. There is no timestamp in this file, so a row does not date "
                 "when the value was issued.",
        "paths": ('*/system/users/*/settings_ssaid.xml',),
        "output_types": "standard",
        "artifact_icon": "fingerprint",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 30 rows",
            "anne_a15": "Android 15 | 61 rows",
            "cookbook_a11": "Android 11 | 371 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 5 rows",
            "falken_a326u_a13": "Android 13 | 37 rows",
            "galaxys10_a10": "Android 10 | 51 rows",
            "hc_pixel8pro_a16": "Android 16 | 33 rows",
            "hc_pixel8pro_a17": "Android 17 | 36 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 46 rows",
            "pixel3_a11": "Android 11 | 79 rows",
            "pixel3_a12": "Android 12 | 61 rows",
            "pixel7a_a14": "Android 14 | 50 rows",
            "russell_a14": "Android 14 | 265 rows",
            "russell_pixel6a_a13": "Android 13 | 273 rows",
            "s20fe_a13": "Android 13 | 31 rows",
            "samsunga53_a14": "Android 14 | 48 rows",
            "samsungs20_a13": "Android 13 | 69 rows",
            "sharon_a13": "Android 13 | 61 rows",
            "sharon_a14": "Android 14 | 78 rows",
            "userb2_a13": "Android 13 | 16 rows",
        },
    },
}

import os
import pathlib
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc


def _root(path):
    """The XML root, reading ABX binary XML or plain XML, and tolerating a file that carries
    more than one root element, which both forms do for some of these records."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        text = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
        if text.lstrip().startswith('<?xml'):
            text = text.split('?>', 1)[1]
        return ET.fromstring(f'<root>{text}</root>')


@artifact_processor
def settings_ssaid(context):
    data_headers = (
        'Package',
        'UID',
        'SSAID',
        'User ID',
        'Setting ID',
        'Default Set By System',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'settings_ssaid.xml':
            continue
        user_id = os.path.basename(os.path.dirname(file_found))
        if not user_id.isdigit():
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'SSAID Per App: could not read user {user_id}: {error}')
            continue
        rows = 0
        for setting in root.iter('setting'):
            data_list.append((
                setting.get('package', ''),
                setting.get('name', ''),
                setting.get('value', ''),
                user_id,
                setting.get('id', ''),
                setting.get('defaultSysSet', ''),
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
