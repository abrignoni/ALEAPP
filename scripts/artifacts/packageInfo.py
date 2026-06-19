# pylint: disable=W0613
__artifacts_v2__ = {
    "get_package_info": {
        "name": "package_info",
        "description": "Represents an app",
        "author": "",
        "creation_date": "2020-11-03",
        "last_update_date": "2020-11-03",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime
import os
import xmltodict
import xml.etree.ElementTree as etree

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
def get_package_info(files_found, report_folder, seeker, wrap_text):
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
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
            xlmstring = (etree.tostring(tree.getroot()).decode())
            doc = xmltodict.parse(xlmstring)
        else:
            with open(file_found) as fd:
                doc = xmltodict.parse(fd.read())

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

    data_headers = (('ft', 'datetime'), 'Name', ('Install Time', 'datetime'), ('Update Time', 'datetime'), 'Install Originator', 'Installer', 'Code Path', 'Public Flags', 'Private Flags')
    return data_headers, data_list, source_path
