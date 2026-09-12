__artifacts_v2__ = {
    "applock_locked_apps": {
        "name": "AppLock Locked Applications",
        "description": "Packages AppLock holds in its active lock list",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "AppLock",
        "sample_data": {
            "emu_a15_oss_v17": "AppLock 6.3.3 | 10 rows",
        },
        "notes": "One row per row of the lock table in "
                 "com.domobile.applockwatcher/databases/domobile_elock.db. Package is the app's "
                 "own pname and Type is its type column, reported as stored because no lookup for "
                 "the value was found in the store. The tested image held 10 rows, and four "
                 "sampled packages from them were confirmed installed on that device. The "
                 "neighbouring locks table is NOT parsed here: it held 19 rows naming packages "
                 "including com.google.android.gallery3d, which is not installed on the tested "
                 "device, so its rows are not treated as a record of what is locked and what the "
                 "table holds is not established. Presence of a row is evidence the package is "
                 "in the app's lock list. It "
                 "is not evidence that anyone was ever prompted for the lock, and the store keeps "
                 "no timestamp for when a package was added.",
        "paths": ('*/com.domobile.applockwatcher/databases/domobile_elock.db*',),
        "output_types": "standard",
        "artifact_icon": "lock",
    },
    "applock_vault_media": {
        "name": "AppLock Vault Media",
        "description": "Media hidden in the AppLock vault, recovered and matched to where it came from",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "AppLock",
        "sample_data": {
            "emu_a15_oss_v17": "AppLock 6.3.3 | 3 rows",
        },
        "notes": "One row per row of SMediaTable in "
                 "com.domobile.applockwatcher/databases/domobile_elock.db, which records media the "
                 "app's vault has hidden. Hiding MOVES the file: on the tested device all three "
                 "source files were gone from the paths the rows name. The bytes are kept twice, "
                 "each named by the row's uid. The copy under the app's own "
                 "files/Medias/Photos is the ORIGINAL FILE UNCHANGED, and this artifact renders "
                 "it and reports its staged location. That was measured: for 3 of 3 rows the "
                 "MD5 of that copy equalled the srcMd5 column exactly and its length equalled "
                 "fileSize, and each began with a JPEG signature. The second copy, under "
                 "/storage/emulated/0/.do0mo7bi1le1/medias, is NOT readable: all three began with "
                 "the same 16 byte header followed by high entropy data and hashed differently "
                 "from the original, so it is reported by name only and nothing is claimed about "
                 "its contents. Source Path is relative to the shared storage root, not absolute. "
                 "The two timestamps in this table do NOT share a convention and were measured "
                 "separately. Hidden (UTC) is a true Unix millisecond value: it rendered as "
                 "17:39 UTC against external copies written at 13:39 in the device's "
                 "America/New_York zone. Media Date (Device Local) is NOT UTC: on all three rows "
                 "it sat exactly one UTC offset behind the true value, so it holds the device's "
                 "local wall clock stored in an epoch field. It is rendered here as plain "
                 "text rather than as a datetime column, so nothing downstream applies a "
                 "second zone conversion to a value that never carried a zone. Reading it as "
                 "UTC would move every value by the device's offset. "
                 "The filePath column exists and was empty on every row, so it is not reported. "
                 "An empty result is not evidence that nothing was ever hidden.",
        "paths": ('*/com.domobile.applockwatcher/databases/domobile_elock.db*',
                  '*/com.domobile.applockwatcher/files/Medias/*'),
        "output_types": "standard",
        "artifact_icon": "eye-off",
    },
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

ELOCK_DB = 'databases/domobile_elock.db'


def _files(context, suffix):
    """Storage-view collapsed files whose path ends in suffix, directories excluded."""
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if path.endswith(suffix) and not os.path.isdir(found):
            out.append(found)
    return out


def _ms(value):
    if value in (None, '', 0):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value / 1000)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def applock_locked_apps(context):
    query = 'SELECT pname, type FROM lock ORDER BY pname'
    data_list = []
    sources = []
    for db_path in _files(context, ELOCK_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((r[0] or '', r[1], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Package', 'Type', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


MEDIA_DIR = '/files/Medias/'
_IMAGE_MAGIC = ((b'\xff\xd8\xff', 'image/jpeg', 'jpg'),
                (b'\x89PNG\r\n\x1a\n', 'image/png', 'png'),
                (b'GIF87a', 'image/gif', 'gif'),
                (b'GIF89a', 'image/gif', 'gif'))


def _local_ms(value):
    """Render a millisecond value that carries device local wall clock, with no zone shift."""
    if value in (None, '', 0):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(
            value / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    except (OverflowError, OSError, ValueError):
        return ''


def _stored_media(context):
    """uid to staged path for the copies AppLock keeps in its own files/Medias tree."""
    out = {}
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if MEDIA_DIR not in path or os.path.isdir(found):
            continue
        out.setdefault(os.path.basename(path), found)
    return out


def _sniff(path):
    """Return (mime, extension) when the bytes really are an image, else None."""
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return None
    for magic, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return mime, extension
    return None


@artifact_processor
def applock_vault_media(context):
    stored = _stored_media(context)
    query = '''SELECT uid, dateToken, lastTime, name, albumName, mimeType, srcPath,
                      srcMd5, fileSize, width, height, duration, orientation
               FROM SMediaTable ORDER BY dateToken DESC, name'''
    data_list = []
    sources = []
    for db_path in _files(context, ELOCK_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            uid = r[0] or ''
            found = stored.get(uid)
            media, recovered = '', ''
            if found:
                recovered = context.get_relative_path(found)
                sniffed = _sniff(found)
                if sniffed:
                    media = check_in_media(found, r[3] or uid, force_type=sniffed[0],
                                           force_extension=sniffed[1]) or ''
            data_list.append((_local_ms(r[1]), _ms(r[2]), media, r[3] or '', r[4] or '',
                              r[5] or '', r[6] or '', r[7] or '', r[8], r[9], r[10],
                              r[11], r[12], uid, recovered,
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Media Date (Device Local)', ('Hidden', 'datetime'),
        ('Recovered File', 'media'), 'Name', 'Album', 'MIME Type', 'Source Path',
        'Source MD5', 'Size', 'Width', 'Height', 'Duration', 'Orientation',
        'Stored As', 'Recovered From', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
