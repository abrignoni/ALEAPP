__artifacts_v2__ = {
    "settings_ssaid": {
        "name": "SSAID Per App",
        "description": "Values from the platform per-user SSAID store, including the "
                       "identifier each app reads back as its Android ID, with the package "
                       "and uid each is stored against.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Read from the per-user settings_ssaid.xml and its fallback copy under the "
                 "system users folder. The files are ABX binary XML on modern releases and "
                 "plain XML on older ones, and in either form one can hold more than one root "
                 "element, so a single-root read is retried in the multiple-root mode. One row "
                 "per distinct setting rather than per setting element, because a setting held "
                 "by both copies is one row and not two, and User ID is the folder the files sit "
                 "in. The patterns are not anchored on a data/ prefix, because a raw userdata "
                 "partition image carries the same folder without one.\n"
                 "Package is the package the value was issued to and UID is the setting's name "
                 "attribute, which the platform uses to hold that package's uid. SSAID is the "
                 "value, which is what the app reads back as its Android ID. Android scopes that "
                 "identifier per app signing key, per user and per device from Android 8.0, and "
                 "on the tested images every package present under two users carried a different "
                 "value under each. Reference: Android Developers, 'Android 8.0 Behavior "
                 "Changes', Privacy, "
                 "https://developer.android.com/about/versions/oreo/android-8.0-changes\n"
                 "One row per user is named userkey against the android package. That is the "
                 "per-user seed the platform keeps rather than an identifier issued to an app, "
                 "and it is reported as stored. Setting ID and Default Set By System are reported "
                 "as stored. There is no timestamp in either file, so a row does not date when "
                 "the value was issued.\n"
                 "Both settings_ssaid.xml and settings_ssaid.xml.fallback are read, and Present "
                 "In says which of the two held the row. The fallback is a copy the platform "
                 "makes of the same file on a periodic job, scheduled once a day and only while "
                 "the device is charging, so it lags the live file rather than mirroring it. "
                 "Reference: Android Open Source Project, SettingsProvider.java in "
                 "packages/SettingsProvider/src/com/android/providers/settings, methods "
                 "scheduleWriteFallbackFilesJob, which builds the job with setPeriodic of one "
                 "day and setRequiresCharging(true), and writeFallBackSettingsFiles, which "
                 "copies the file to one named with the .fallback suffix; read from the main "
                 "branch 2026-09-06.\n"
                 "A row present only in the fallback copy was in the file when that copy was "
                 "taken and is not in it now. That was produced deliberately on a test emulator "
                 "by uninstalling an app: its entry left the live file while the fallback kept "
                 "it, giving 26 entries in both copies, none in the live file alone and one in "
                 "the fallback alone, and a second Android user on that device had no fallback "
                 "file at all. On the 23 registered images this artifact records, reading the "
                 "fallback added no rows at all, so a divergence between the two copies did not "
                 "occur on any of them and should be treated as uncommon. What such a row means "
                 "is not fixed: an uninstall produced it in the constructed case, and this "
                 "artifact does not assert that every such row is an uninstalled app.\n"
                 "Setting ID is reported but is deliberately not part of what makes a row "
                 "distinct. The platform assigns it from a counter it advances whenever a "
                 "setting is written, so the same package can carry a different id in the two "
                 "copies while its package, uid and SSAID are identical. One registered image "
                 "does exactly that, and keying on the id would have split that app into two "
                 "rows and reported a change that had not happened. Reference: Android Open "
                 "Source Project, SettingsState.java in the same folder, which writes the "
                 "attribute from mNextId++ when a setting is initialised.",
        "paths": ('*/system/users/*/settings_ssaid.xml',
                  '*/system/users/*/settings_ssaid.xml.fallback'),
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


LIVE_NAME = 'settings_ssaid.xml'
FALLBACK_NAME = 'settings_ssaid.xml.fallback'


@artifact_processor
def settings_ssaid(context):
    data_headers = (
        'Package',
        'UID',
        'SSAID',
        'User ID',
        'Setting ID',
        'Default Set By System',
        'Present In',
        'Source File',
    )
    data_list = []
    sources = []

    # Collect both copies per user first, so an entry held by both is one row rather than two.
    per_user = {}
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        name = os.path.basename(file_found)
        if name not in (LIVE_NAME, FALLBACK_NAME):
            continue
        user_id = os.path.basename(os.path.dirname(file_found))
        if not user_id.isdigit():
            continue
        per_user.setdefault(user_id, {})[name] = file_found

    for user_id in sorted(per_user, key=int):
        found = {}
        for name in (LIVE_NAME, FALLBACK_NAME):
            path = per_user[user_id].get(name)
            if not path:
                continue
            try:
                root = _root(path)
            except Exception as error:  # pylint: disable=broad-except
                logfunc(f'SSAID Per App: could not read {name} for user {user_id}: {error}')
                continue
            read_any = False
            for setting in root.iter('setting'):
                # The id attribute is a counter the platform reassigns whenever a setting is
                # rewritten, so it is reported but deliberately not part of the identity.
                key = (setting.get('package', ''), setting.get('name', ''),
                       setting.get('value', ''), setting.get('defaultSysSet', ''))
                entry = found.setdefault(
                    key, {'names': [], 'paths': [], 'id': setting.get('id', '')})
                if name not in entry['names']:
                    entry['names'].append(name)
                    entry['paths'].append(path)
                read_any = True
            if read_any and path not in sources:
                sources.append(path)

        for key, entry in found.items():
            if len(entry['names']) > 1:
                present = 'Live file and fallback copy'
            elif entry['names'][0] == LIVE_NAME:
                present = 'Live file only'
            else:
                present = 'Fallback copy only'
            data_list.append((
                key[0], key[1], key[2], user_id, entry['id'], key[3], present,
                '\n'.join(context.get_relative_path(x) for x in entry['paths']),
            ))

    return data_headers, data_list, '\n'.join(sources)
