__artifacts_v2__ = {
    "companion_device_associations": {
        "name": "Companion Device Associations",
        "description": "Companion devices that the Android Companion Device Manager "
                       "associated with an app, and when each association was approved. On "
                       "the tested images the stored profiles were the watch and automotive "
                       "projection roles, or none.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Smart Home & Connected Devices",
        "notes": "Read from /data/system_de/<user>/companion_device_manager.xml (Android 13 "
                 "and later, persistence version 1) and the earlier "
                 "/data/system/users/<user>/companion_device_manager_associations.xml "
                 "(version 0), in ABX or plain XML; on the tested images the version 1 files "
                 "were ABX and the version 0 files plain XML. Attribute and file names are "
                 "the ones AOSP's AssociationDiskStore reads and writes (frameworks/base "
                 "services/companion/java/com/android/server/companion/association/AssociationDiskStore.java"
                 " at android-16.0.0_r1, L77-L158, L166-L193, L448-L521 and L548-L571). One "
                 "row per association element. 'MAC Address' is mac_address, or device in the"
                 " version 0 file. 'Time Approved' is time_approved, set to the current time "
                 "in Unix milliseconds when the association is created "
                 "(AssociationRequestsProcessor.java at android-16.0.0_r1, L311-L316), shown "
                 "in UTC, blank when absent, 0 or not a valid time; the version 0 file on "
                 "pixel3_a11 carries no time_approved. 'Last Time Connected' is "
                 "last_time_connected. At android-16.0.0_r1 it is set to the current time "
                 "each time a self-managed device's app reports the device appeared or "
                 "disappeared (DevicePresenceProcessor.java L835-L855); AssociationInfo "
                 "describes it both as the last time connected (AssociationInfo.java L81-L82)"
                 " and as the last time reported disconnected (L270-L273), and earlier "
                 "releases were not read for this. A new association is created with "
                 "Long.MAX_VALUE (AssociationRequestsProcessor.java L316) and an absent "
                 "attribute is read as that value (AssociationDiskStore.java L509-L510); it "
                 "is shown blank. On the tested images it held a value only on rows whose "
                 "Self Managed is true. 'Self Managed', 'Notify Device Nearby', 'Revoked' and"
                 " 'Pending' are the stored booleans; AssociationInfo documents revoked as "
                 "removed with the record kept for clean up and pending as waiting for its "
                 "app to be installed (L67-L78). 'Profile' is the device profile role as "
                 "stored, blank when the association has none. 'Other Attributes (as stored)'"
                 " holds every other attribute of the association element, and the attributes"
                 " of any child element (such as device_id) as element.name=value, in the "
                 "text form the XML or ABX reader returns; no tested association had a child "
                 "element. The dragna_pixel9a_a16 file carries trusted, transport_flags and "
                 "time_metadata_sent, which AssociationDiskStore.java at android-16.0.0_r1 "
                 "does not name; transport_flags is written by AssociationDiskStore at "
                 "android-16.0.0_r4, trusted and time_metadata_sent were not found in the "
                 "AOSP revisions read, and the meaning of all three is not established here. "
                 "'User' is the Android user from the folder. 'File Format' is the stored "
                 "persistence-version, or 'v0 (legacy file)' for the legacy file name. Not "
                 "read: previously-used-ids, which version 1 files carry (package and earlier"
                 " association IDs), and last_removed_association.txt, which the store writes"
                 " with the last removed association; no tested image holds the latter (one "
                 "Android 16 image tested). On the tested images 'Revoked' and 'Pending' held"
                 " false wherever stored; files that omit them show blank "
                 "(AssociationDiskStore reads an absent revoked or pending as false, "
                 "L506-L507), and the version 0 rows carry neither.",
        "paths": (
            '*/system_de/*/companion_device_manager.xml',
            '*/system/users/*/companion_device_manager_associations.xml',
        ),
        "output_types": "standard",
        "artifact_icon": "watch",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | system_server | 2 rows",
            "anne_a15": "Android 15 | system_server | 2 rows",
            "hickman_a13": "Android 13 | system_server | 5 rows",
            "kevin_pocox7_a15": "Android 15 | system_server | 2 rows",
            "pixel3_a11": "Android 11 | system_server | 3 rows",
            "pixel3_a12": "Android 12 | system_server | 3 rows",
            "pixel7a_a14": "Android 14 | system_server | 4 rows",
            "russell_a14": "Android 14 | system_server | 2 rows",
            "russell_pixel6a_a13": "Android 13 | system_server | 3 rows",
            "samsunga53_a14": "Android 14 | system_server | 1 row",
            "userb2_a13": "Android 13 | system_server | 1 row",
        },
    },
}

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# Attributes shown in their own columns; every other attribute, including ones
# AssociationDiskStore reads such as system_data_sync_flags, is reported as stored in
# 'Other Attributes (as stored)'.
_SHOWN = ('id', 'package', 'mac_address', 'device', 'display_name', 'profile',
          'self_managed', 'notify_device_nearby', 'revoked', 'pending', 'time_approved',
          'last_time_connected')
_LONG_MAX = 9223372036854775807
_USER = re.compile(r'(?:^|/)(?:system_de|system/users)/(\d+)/')


def _utc_ms(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0 or number == _LONG_MAX:
        return ''
    try:
        return datetime.fromtimestamp(number / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _root(path):
    try:
        if checkabx(path):
            return abxread(path, False).getroot()
        return ET.parse(path).getroot()
    # abxread raises an AbxDecodeError defined inside the function, so it cannot be named.
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'Companion Device Associations: could not read {os.path.basename(path)}: '
                f'{type(error).__name__}')
        return None


@artifact_processor
def companion_device_associations(context):
    data_headers = (
        ('Time Approved', 'datetime'), ('Last Time Connected', 'datetime'), 'Package',
        'Display Name', 'MAC Address', 'Profile', 'Self Managed', 'Notify Device Nearby',
        'Revoked', 'Pending', 'Association ID', 'Other Attributes (as stored)', 'User',
        'File Format')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.isdir(path):
            continue
        root = _root(path)
        if root is None:
            continue
        sources.append(path)
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        match = _USER.search(relative)
        user = match.group(1) if match else ''
        legacy = os.path.basename(path) == 'companion_device_manager_associations.xml'
        version = root.get('persistence-version', '')
        file_format = 'v0 (legacy file)' if legacy else f'persistence-version {version}'
        for association in root.iter('association'):
            attrs = dict(association.attrib)
            parts = [f'{key}={value}' for key, value in attrs.items() if key not in _SHOWN]
            for child in association.iter():
                if child is not association:
                    parts.extend(f'{child.tag}.{key}={value}'
                                 for key, value in child.attrib.items())
            other = '; '.join(parts)
            data_list.append((
                _utc_ms(attrs.get('time_approved')),
                _utc_ms(attrs.get('last_time_connected')),
                attrs.get('package', ''),
                attrs.get('display_name', ''),
                attrs.get('mac_address') or attrs.get('device', ''),
                attrs.get('profile', ''),
                attrs.get('self_managed', ''),
                attrs.get('notify_device_nearby', ''),
                attrs.get('revoked', ''),
                attrs.get('pending', ''),
                attrs.get('id', ''),
                other,
                user,
                file_format,
            ))
    return data_headers, data_list, '\n'.join(sources)
