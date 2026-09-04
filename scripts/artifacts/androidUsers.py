__artifacts_v2__ = {
    "android_users": {
        "name": "Android Users and Profiles",
        "description": "The Android users and profiles that exist on the device, with each "
                       "one's name, type, creation time and the times it was last logged in "
                       "and last brought to the foreground.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Device Users",
        "notes": "Read from the user records the platform keeps under the system users folder: the "
                 "userlist.xml index and one <id>.xml file per user, both ABX binary XML on "
                 "modern releases and plain XML on older ones. One row per user file. The glob "
                 "reaches every .xml under that folder because a pattern segment also crosses "
                 "path separators, so a file is used only when its name is a number and its "
                 "root element is a user record; anything else, including the per-user "
                 "package-restrictions.xml and settings_ssaid.xml, is skipped. The pattern is not "
                 "anchored on a data/ prefix, because a raw userdata partition image carries the "
                 "same folder without one.\n"
                 "Created, Last Logged In and Last Entered Foreground are Unix milliseconds. "
                 "The system user is created with the device and records a creation value of 0, "
                 "which is reported as blank rather than as 1970. User Type and Flags are "
                 "reported as stored; the type string is the platform's own, such as a full "
                 "secondary user or a managed profile. User Name is blank where the record carries "
                 "no name element. User ID and Serial Number were identical on every tested image and are "
                 "both reported because the platform assigns them separately, the serial being the "
                 "value that is not reused when a user id is. In Userlist is True when the userlist "
                 "index also names the user, and a user file present without an index entry, or "
                 "the reverse, is reported as it was found.\n"
                 "A user other than 0 means a second data tenant on the device, with its own "
                 "copies of app storage under data/user/<id>, and its presence here does not "
                 "establish who used it.",
        "paths": ('*/system/users/*.xml',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 1 row",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 2 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 2 rows",
            "falken_a326u_a13": "Android 13 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "russell_a14": "Android 14 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, convert_unix_ts_to_utc, logfunc


def _root(path):
    """The XML root, reading ABX binary XML or plain XML as the file requires."""
    if checkabx(path):
        return abxread(path, False).getroot()
    return ET.parse(path).getroot()


def _ms(value):
    """Unix milliseconds as an aware UTC datetime; 0 and empty are reported as blank."""
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    return convert_unix_ts_to_utc(number)


def _child_text(element, tag):
    found = element.find(tag)
    if found is None:
        return ''
    return (found.text or '').strip()


@artifact_processor
def android_users(context):
    data_headers = (
        ('Created', 'datetime'),
        ('Last Logged In', 'datetime'),
        ('Last Entered Foreground', 'datetime'),
        'User ID',
        'User Name',
        'User Type (as stored)',
        'Serial Number',
        'Flags (as stored)',
        'Profile Badge (as stored)',
        'In Userlist',
        'Last Logged In Fingerprint',
        'Source File',
    )
    data_list = []
    sources = []
    listed = set()
    user_files = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        name = os.path.basename(file_found)
        parent = os.path.basename(os.path.dirname(file_found))
        if parent != 'users':
            continue
        if name == 'userlist.xml':
            try:
                root = _root(file_found)
            except Exception as error:  # pylint: disable=broad-except
                logfunc(f'Android Users: could not read {name}: {error}')
                continue
            if root.tag == 'users':
                for entry in root.findall('user'):
                    if entry.get('id'):
                        listed.add(str(entry.get('id')))
                sources.append(file_found)
        elif name[:-4].isdigit() and name.endswith('.xml'):
            user_files.append(file_found)

    for file_found in sorted(user_files):
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Android Users: could not read {os.path.basename(file_found)}: {error}')
            continue
        if root.tag != 'user':
            continue
        user_id = str(root.get('id', os.path.basename(file_found)[:-4]))
        data_list.append((
            _ms(root.get('created')),
            _ms(root.get('lastLoggedIn')),
            _ms(root.get('lastEnteredForeground')),
            user_id,
            _child_text(root, 'name'),
            root.get('type', ''),
            root.get('serialNumber', ''),
            root.get('flags', ''),
            root.get('profileBadge', ''),
            user_id in listed,
            root.get('lastLoggedInFingerprint', ''),
            context.get_relative_path(file_found),
        ))
        sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
