__artifacts_v2__ = {
    "get_settingsGlobal": {
        "name": "Settings Global",
        "description": "Device-wide settings (name, value and owning package) parsed "
                       "from the settings_global.xml file of each Android user.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "More info: https://blog.digital-forensics.it/2024/01/analysis-of-android-settings-during.html",
        "paths": ('*/system/users/*/settings_global.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | 397 rows",
            "galaxys10_a10": "Android 10 | 254 rows",
            "hc_pixel8pro_a16": "Android 16 | 280 rows",
            "kevin_pocox7_a15": "Android 15 | 511 rows",
            "pixel7a_a14": "Android 14 | 247 rows",
            "samsunga53_a14": "Android 14 | 336 rows",
            "samsungs20_a13": "Android 13 | 311 rows",
            "sharon_a14": "Android 14 | 379 rows",
            "russell_pixel6a_a13": "Android 13 | 260 rows",
            "userb2_a13": "Android 13 | 244 rows",
        },
    },
    "get_settingsSystem": {
        "name": "Settings System",
        "description": "Per-user settings (name, value and owning package) parsed "
                       "from the settings_system.xml file of each Android user.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "More info: https://blog.digital-forensics.it/2024/01/analysis-of-android-settings-during.html",
        "paths": ('*/system/users/*/settings_system.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | 366 rows",
            "galaxys10_a10": "Android 10 | 345 rows",
            "hc_pixel8pro_a16": "Android 16 | 53 rows",
            "kevin_pocox7_a15": "Android 15 | 323 rows",
            "pixel7a_a14": "Android 14 | 52 rows",
            "samsunga53_a14": "Android 14 | 317 rows",
            "samsungs20_a13": "Android 13 | 472 rows",
            "sharon_a14": "Android 14 | 671 rows",
            "russell_pixel6a_a13": "Android 13 | 99 rows",
            "userb2_a13": "Android 13 | 43 rows",
        },
    },
}

from scripts.artifacts.settingsSecure import parse_settings_root
from scripts.ilapfuncs import artifact_processor, logdevinfo, is_platform_windows


def _parse_settings_files(context, artifact_label):
    files_found = context.get_files_found()

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        uid = file_found.split(slash)[-2]
        try:
            int(uid)
        except ValueError:
            continue  # uid was not a number
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            continue  # Skip mirror, it should be duplicate data

        root = parse_settings_root(file_found, artifact_label)
        if root is None:
            continue

        source_path = file_found
        for setting in root.iter('setting'):
            data_list.append((uid, setting.get('name'), setting.get('value'), setting.get('package')))

    return data_list, source_path


@artifact_processor
def get_settingsGlobal(context):
    data_list, source_path = _parse_settings_files(context, 'settingsGlobal')

    for uid, name, value, _package in data_list:
        if name == 'device_name':
            logdevinfo(f"<b>Device name (user {uid}): </b>{value}")

    data_headers = ('User', 'Name', 'Value', 'Package')
    return data_headers, data_list, source_path


@artifact_processor
def get_settingsSystem(context):
    data_list, source_path = _parse_settings_files(context, 'settingsSystem')

    data_headers = ('User', 'Name', 'Value', 'Package')
    return data_headers, data_list, source_path
