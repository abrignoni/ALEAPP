__artifacts_v2__ = {
    "package_restrictions": {
        "name": "Package State Per User",
        "description": "The state the platform keeps for each package separately for each "
                       "Android user, including the time the package was first installed for "
                       "that user and whether it is stopped, disabled or never launched.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Read from the per-user package-restrictions.xml under the system users folder, "
                 "ABX binary XML on modern releases and plain XML on older ones. One row per pkg "
                 "element per user, and User ID is the folder the file sits in. The pattern is "
                 "not anchored on a data/ prefix, because a raw userdata partition image carries "
                 "the same folder without one.\n"
                 "First Install Time is the first-install-time attribute, which the platform "
                 "writes as hexadecimal Unix milliseconds, the same encoding packages.xml uses "
                 "for its install times. It is the per-user install time the platform keeps, "
                 "distinct from the device-wide install time reported from packages.xml. The "
                 "attribute is written from Android 13: it is absent from the Android 12 release "
                 "of the writer and from every row of the four tested Android 10 to 12 images, "
                 "and present on the fifteen tested Android 13 and later images. A value of 0 is "
                 "reported as blank; on the tested images it was 0 on up to 28 rows of the "
                 "primary user and on most rows of a second user on two images, and this artifact "
                 "does not assert what a zero means. Reference: Android Open Source Project, "
                 "Settings.java, frameworks/base/services/core/java/com/android/server/pm, "
                 "writePackageRestrictions, which writes ATTR_FIRST_INSTALL_TIME with "
                 "attributeLongHex; the attribute is not in the android12-release branch of that "
                 "file.\n"
                 "Stopped, Not Launched and Installed come from the stopped, nl and inst "
                 "attributes. Enabled and Install Reason are integers the platform defines and "
                 "are reported as stored, with an absent Enabled meaning the package is in its "
                 "default state. Enabled Caller is the package the platform recorded as having "
                 "changed that state. Disabled Components and Enabled Components list the "
                 "component names the user's state overrides, joined by a comma; they are blank "
                 "for most packages.\n"
                 "A per-user file that is neither ABX nor XML is logged and skipped; one tested "
                 "image carried such a file for two of its users, so that image reports no rows "
                 "for them. A row is the platform's stored state for that package and user. It "
                 "does not establish that the user opened the app.",
        "paths": ('*/system/users/*/package-restrictions.xml',),
        "output_types": "standard",
        "artifact_icon": "apps",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 419 rows",
            "anne_a15": "Android 15 | 555 rows",
            "cookbook_a11": "Android 11 | 960 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 590 rows",
            "falken_a326u_a13": "Android 13 | 472 rows",
            "galaxys10_a10": "Android 10 | 448 rows",
            "hc_pixel8pro_a16": "Android 16 | 431 rows",
            "hc_pixel8pro_a17": "Android 17 | 444 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 466 rows",
            "pixel3_a11": "Android 11 | 642 rows",
            "pixel3_a12": "Android 12 | 325 rows",
            "pixel7a_a14": "Android 14 | 407 rows",
            "russell_a14": "Android 14 | 766 rows",
            "russell_pixel6a_a13": "Android 13 | 606 rows",
            "s20fe_a13": "Android 13 | 463 rows",
            "samsunga53_a14": "Android 14 | 527 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 506 rows",
            "sharon_a14": "Android 14 | 541 rows",
            "userb2_a13": "Android 13 | 303 rows",
        },
    },
}

import os
import pathlib
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, convert_unix_ts_to_utc, logfunc


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


def _hex_ms(value):
    """Hexadecimal Unix milliseconds as an aware UTC datetime; 0 and empty are blank."""
    text = str(value or '').strip()
    if not text:
        return ''
    try:
        number = int(text, 16)
    except ValueError:
        return ''
    if number <= 0:
        return ''
    return convert_unix_ts_to_utc(number)


def _components(package, tag):
    names = [item.get('name', '') for item in package.findall(f'{tag}/item')]
    if not names:
        names = [(item.text or '').strip() for item in package.findall(f'{tag}/*')]
    return ', '.join(n for n in names if n)


@artifact_processor
def package_restrictions(context):
    data_headers = (
        ('First Install Time', 'datetime'),
        'Package',
        'User ID',
        'Stopped',
        'Not Launched',
        'Installed',
        'Enabled (as stored)',
        'Enabled Caller',
        'Install Reason (as stored)',
        'Virtual Preload',
        'Disabled Components',
        'Enabled Components',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'package-restrictions.xml':
            continue
        user_id = os.path.basename(os.path.dirname(file_found))
        if not user_id.isdigit():
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Package State Per User: could not read user {user_id}: {error}')
            continue
        rows = 0
        for package in root.iter('pkg'):
            data_list.append((
                _hex_ms(package.get('first-install-time')),
                package.get('name', ''),
                user_id,
                package.get('stopped', ''),
                package.get('nl', ''),
                package.get('inst', ''),
                package.get('enabled', ''),
                package.get('enabledCaller', ''),
                package.get('install-reason', ''),
                package.get('virtual-preload', ''),
                _components(package, 'disabled-components'),
                _components(package, 'enabled-components'),
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
