__artifacts_v2__ = {
    "get_package_info": {
        "name": "package_info",
        "description": "Parses installed package records from the system packages.xml: "
                       "name, the ft, it and ut time attributes (shown as Code Path Modified "
                       "Time (ft), Install Time and Update Time), install originator, "
                       "installer, code path and flags as stored.",
        "author": "@ydkhatri, @AlexisBrignoni, Codex",
        "creation_date": "2020-11-03",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Code Path Modified Time (ft) is the package record's ft attribute, read as "
                 "milliseconds since 1970 UTC. AOSP writes ft from the package setting's last "
                 "modified time, which it sets from the last modified time of the package's "
                 "code path, and it prints the same value as timeStamp in its package dump. It "
                 "is a file time of the installed code, not the time of an install. "
                 "Reference: AOSP, Settings.java at android-13.0.0_r1, "
                 "https://github.com/aosp-mirror/platform_frameworks_base/blob/0d3ff311e6e80dee7fe88a2a2cfa272ce231c3c6/services/core/java/com/android/server/pm/Settings.java#L984-L999 and "
                 "https://github.com/aosp-mirror/platform_frameworks_base/blob/0d3ff311e6e80dee7fe88a2a2cfa272ce231c3c6/services/core/java/com/android/server/pm/Settings.java#L2784-L2785 . "
                 "The same source for ft was read at android-10.0.0_r1 "
                 "(https://github.com/aosp-mirror/platform_frameworks_base/blob/57bb140be9e48cf08acba131f7463e461777bb8e/services/core/java/com/android/server/pm/Settings.java#L624-L631) and at android-16.0.0_r1 "
                 "(https://github.com/aosp-mirror/platform_frameworks_base/blob/99b01a65cc4c104933788b3143285ab6bae65827/services/core/java/com/android/server/pm/Settings.java#L1089-L1113). "
                 "Install Time is the it attribute and Update Time is the ut attribute. "
                 "At android-13.0.0_r1 and android-16.0.0_r1 the package record is written "
                 "with ft and ut and without it, and the first install time is written per "
                 "user to package-restrictions.xml, which this artifact does not read. "
                 "Measured on three registered images: on galaxys10_a10 (Android 10) all 448 "
                 "rows carry ft, it and ut; on pixel7a_a14 (369 rows) and hc_pixel8pro_a16 "
                 "(385 rows) every row carries ft and ut and no row carries it, so Install "
                 "Time is blank on those images. On those two images the earliest ft value "
                 "falls in 1970.",
        "paths": ('*/system/packages.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | 513 rows",
            "galaxys10_a10": "Android 10 | 448 rows",
            "hc_pixel8pro_a16": "Android 16 | 385 rows",
            "kevin_pocox7_a15": "Android 15 | 426 rows",
            "pixel7a_a14": "Android 14 | 369 rows",
            "samsunga53_a14": "Android 14 | 486 rows",
            "sharon_a14": "Android 14 | 499 rows",
            "samsungs20_a13": "Android 13 | 506 rows",
            "russell_pixel6a_a13": "Android 13 | 303 rows",
            "userb2_a13": "Android 13 | 303 rows",
        },
    }
}

import datetime
import os
import xmltodict
import xml.etree.ElementTree as etree
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows, abxread, checkabx

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/'


class Package:
    # Represents an app
    def __init__(self, name, ft, install_time, update_time, install_originator, installer, code_path, public_flags, private_flags):
        self.name = name
        self.ft = ft
        self.install_time = install_time
        self.update_time = update_time
        self.install_originator = install_originator
        self.installer = installer
        self.code_path = code_path
        self.public_flags = public_flags
        self.private_flags = private_flags


def ReadUnixTimeMs(unix_time_ms):  # Unix timestamp is time epoch beginning 1970/1/1
    '''Returns datetime object (tz-aware UTC), or empty string upon error'''
    if unix_time_ms not in (0, None, ''):
        try:
            if isinstance(unix_time_ms, str):
                unix_time_ms = float.fromhex(unix_time_ms)
            return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=unix_time_ms / 1000)
        except (ValueError, OverflowError, TypeError) as ex:
            logfunc("ReadUnixTimeMs() Failed to convert timestamp from value " + str(unix_time_ms) + " Error was: " + str(ex))
    return ''


@artifact_processor
def get_package_info(context):
    files_found = context.get_files_found()
    packages = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif os.path.isdir(file_found):  # skip folders (there shouldn't be any)
            continue

        source_path = file_found
        try:
            if (checkabx(file_found)):
                multi_root = False
                tree = abxread(file_found, multi_root)
                xlmstring = (etree.tostring(tree.getroot()).decode())
                doc = xmltodict.parse(xlmstring)
            else:
                with open(file_found, encoding='utf-8', errors='replace') as fd:
                    doc = xmltodict.parse(fd.read())
        except ExpatError as ex:
            # Some extractions carry a packages.xml that is neither plain XML
            # nor ABX (e.g. encrypted or partially recovered content)
            logfunc(f'Unable to parse {file_found} (not valid XML/ABX): {ex}')
            continue

        package_dict = doc.get('packages', {}).get('package', {})
        for package in package_dict:
            name = package.get('@name', '')
            ft = ReadUnixTimeMs(package.get('@ft', None))
            it = ReadUnixTimeMs(package.get('@it', None))
            ut = ReadUnixTimeMs(package.get('@ut', None))
            install_originator = package.get('@installOriginator', '')
            installer = package.get('@installer', '')
            code_path = package.get('@codePath', '')
            public_flags = hex(int(package.get('@publicFlags', 0)) & (2**32 - 1))
            private_flags = hex(int(package.get('@privateFlags', 0)) & (2**32 - 1))
            packages.append(Package(name, ft, it, ut, install_originator, installer, code_path, public_flags, private_flags))

        if len(packages):
            break

    data_list = []
    for p in packages:
        data_list.append((p.ft, p.name, p.install_time, p.update_time, p.install_originator, p.installer, p.code_path, p.public_flags, p.private_flags))

    data_headers = (('Code Path Modified Time (ft)', 'datetime'), 'Name', ('Install Time', 'datetime'), ('Update Time', 'datetime'), 'Install Originator', 'Installer', 'Code Path', 'Public Flags', 'Private Flags')
    return data_headers, data_list, source_path
