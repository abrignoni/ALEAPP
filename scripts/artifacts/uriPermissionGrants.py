__artifacts_v2__ = {
    "uri_permission_grants": {
        "name": "URI Permission Grants",
        "description": "Persisted URI permission grants Android kept in "
                       "/data/system/urigrants.xml: which app was given lasting read or write"
                       " access to which content URI, which app's content provider serves it,"
                       " and the time the persisted access was last taken.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Read from /data/system/urigrants.xml, in ABX or plain XML (every tested "
                 "file was ABX; the plain XML path was not exercised), with the element and "
                 "attribute names UriGrantsManagerService reads and writes (frameworks/base "
                 "services/core/java/com/android/server/uri/UriGrantsManagerService.java at "
                 "android-16.0.0_r1, L140-L150, L183, L878-L914 and L1626-L1672). Only "
                 "persisted grants are written to the file: a grant enters it when a "
                 "persistable URI permission is taken for the receiving app "
                 "(takePersistableUriPermission, L394-L440), by the app itself or by a caller"
                 " holding FORCE_PERSISTABLE_URI_PERMISSIONS, and grants that were never "
                 "persisted are not in it. One row per uri-grant element. 'Created' is "
                 "createdTime, which UriPermission sets to the current time in Unix "
                 "milliseconds each time the grant's persisted modes are taken "
                 "(UriPermission.java at android-16.0.0_r1, L158-L176), shown in UTC; when an"
                 " entry has no createdTime the service uses the time of reading (L899), and "
                 "a later rewrite of the file stores that time, so a time can be later than "
                 "the grant. 'Target Package' is the app given access (targetPkg), 'Source "
                 "Package' the app whose content provider serves the URI (sourcePkg), and "
                 "'URI' the content URI as stored. 'Access' decodes modeFlags with the two "
                 "bits takePersistableModes keeps, 1 Read and 2 Write "
                 "(Intent.FLAG_GRANT_READ_URI_PERMISSION and "
                 "FLAG_GRANT_WRITE_URI_PERMISSION); any other bit is shown as other bits, and"
                 " 'Mode Flags (as stored)' keeps the number. 'Prefix' is the stored prefix "
                 "boolean, true when the grant covers every URI under the one stored. 'Source"
                 " User' and 'Target User' are sourceUserId and targetUserId, or userHandle "
                 "in older files, which the service reads as both and which wins when "
                 "present. 'Other Attributes (as stored)' holds any other attribute. When the"
                 " service loads the file at boot it skips a grant whose provider no longer "
                 "belongs to the source package, or whose target package has no UID "
                 "(L901-L924); a skipped grant is left out the next time the file is written,"
                 " so a removed app's grants may not be in the file. The service also prunes "
                 "the oldest persisted grants above 512 per app (L127, L606-L632). On the 12 "
                 "images listed in sample_data (64 rows; two pairs of images hold the same "
                 "file, so 10 distinct files) 'Mode Flags (as stored)' held 1 ('Access' Read)"
                 " on every row except on the Android 15 emulator, where it held 3 (Read, "
                 "Write) on every row; 'Prefix' was false on every row except 2 of the 3 "
                 "emulator rows; 'Source User' and 'Target User' held 0 on every row of every"
                 " image; 'Other Attributes (as stored)' held no value and every row carried "
                 "sourceUserId and targetUserId. A missing or non-numeric createdTime is "
                 "shown blank in 'Created'.",
        "paths": ('*/system/urigrants.xml',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | system_server | 6 rows",
            "emu_a15_oss_v17": "Android 15 | system_server | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | system_server | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | system_server | 4 rows",
            "hickman_a13": "Android 13 | system_server | 7 rows",
            "kevin_pocox7_a15": "Android 15 | system_server | 2 rows",
            "pixel3_a12": "Android 12 | system_server | 5 rows",
            "pixel7a_a14": "Android 14 | system_server | 11 rows",
            "russell_a14": "Android 14 | system_server | 9 rows",
            "russell_pixel6a_a13": "Android 13 | system_server | 9 rows",
            "samsunga53_a14": "Android 14 | system_server | 2 rows",
            "userb2_a13": "Android 13 | system_server | 2 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# Attributes shown in their own columns; any other is reported in 'Other Attributes'.
_SHOWN = ('createdTime', 'sourcePkg', 'targetPkg', 'uri', 'modeFlags', 'prefix',
          'sourceUserId', 'targetUserId', 'userHandle')
# Intent.FLAG_GRANT_READ_URI_PERMISSION and FLAG_GRANT_WRITE_URI_PERMISSION, the only bits
# UriPermission.takePersistableModes keeps.
_MODES = ((1, 'Read'), (2, 'Write'))


def _utc_ms(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.fromtimestamp(number / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _access(value):
    try:
        flags = int(value)
    except (TypeError, ValueError):
        return ''
    names = [name for bit, name in _MODES if flags & bit]
    rest = flags & ~3
    if rest:
        names.append(f'other bits {rest:#x}')
    return ', '.join(names)


def _root(path):
    try:
        if checkabx(path):
            return abxread(path, False).getroot()
        return ET.parse(path).getroot()
    # abxread raises an AbxDecodeError defined inside the function, so it cannot be named.
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'URI Permission Grants: could not read urigrants.xml: {type(error).__name__}')
        return None


@artifact_processor
def uri_permission_grants(context):
    data_headers = (
        ('Created', 'datetime'), 'Target Package', 'Source Package', 'URI', 'Access',
        'Mode Flags (as stored)', 'Prefix', 'Source User', 'Target User',
        'Other Attributes (as stored)')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'urigrants.xml':
            continue
        root = _root(path)
        if root is None:
            continue
        sources.append(path)
        for grant in root.iter('uri-grant'):
            attrs = dict(grant.attrib)
            # A userHandle, written by older releases, stands for both users (as the service
            # reads it).
            source_user = attrs.get('userHandle', attrs.get('sourceUserId', ''))
            target_user = attrs.get('userHandle', attrs.get('targetUserId', ''))
            other = '; '.join(f'{k}={v}' for k, v in attrs.items() if k not in _SHOWN)
            data_list.append((
                _utc_ms(attrs.get('createdTime')), attrs.get('targetPkg', ''),
                attrs.get('sourcePkg', ''), attrs.get('uri', ''),
                _access(attrs.get('modeFlags')), attrs.get('modeFlags', ''),
                attrs.get('prefix', ''), source_user, target_user, other,
            ))
    return data_headers, data_list, '\n'.join(sources)
