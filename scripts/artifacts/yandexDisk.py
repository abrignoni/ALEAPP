__artifacts_v2__ = {
    "yandex_disk_cloud_files": {
        "name": "Yandex Disk Cloud Files",
        "description": "Cloud files and folders the Yandex Disk app had listed for each signed-in account",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-21",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the DISK and FOREIGN_DISK tables in "
                 "ru.yandex.disk/databases/<uid>_disk, one database per signed-in account. Account "
                 "UID is the number in the file name, which the app builds from the signed-in "
                 "account's numeric uid. Android User is taken from the storage path the database "
                 "came from, so the same account signed in on two Android users is reported once per "
                 "user.\n"
                 "Field meanings were sourced from the decompiled Yandex Disk 6.90.0 app "
                 "(versionCode 690000, database version 85) and were not exercised against a real "
                 "extraction: the module was run only against synthetic databases built from the app's "
                 "own schema. The app's upgrade step from database version 84 adds two tables this "
                 "artifact does not read; a fresh 6.90.0 install orders the DISK columns differently "
                 "and adds LATITUDE and LONGITUDE to FOREIGN_DISK, so columns are read by name and a missing "
                 "column reads blank.\n"
                 "These rows are what the app had synced from the server, not a record of what was "
                 "on the device. The app deletes DISK rows by folder path, the folder and everything "
                 "below it, and DISK has no deleted flag; which sync events trigger that delete was "
                 "not traced. A file absent here is not evidence it never existed in the account.\n"
                 "Last Modified is the server's modified time for the resource and EXIF Date is the "
                 "EXIF date the server reported for the resource; both are stored in milliseconds "
                 "and reported in UTC, and EXIF Date is blank when the app stored 0. Local Copy Last "
                 "Access is set to the current time when the app touches a cached local copy, and the "
                 "one caller found in 6.90.0 opens the file in an external viewer; the app resets it "
                 "to 0 when it deletes the local copy and orders cached copies by it when freeing "
                 "space. It is blank when 0. PHOTOSLICE_TIME, which places a photo on the app's "
                 "timeline, is not reported.\n"
                 "ETag holds the server's md5 field on rows from the app's REST and album sync, and "
                 "the file index's MD5 field on rows from its index sync. On rows written by its "
                 "WebDAV sync it holds the server's getetag. That these all equal the MD5 of the "
                 "file's content was not established from the app's code; one of the app's own views "
                 "joins the upload queue's content MD5 to this column. Local Copy MD5 is an MD5 the "
                 "app computed over a local copy. The app clears it for rows that are not offline "
                 "marked when it clears its cache. Where local copies are kept was not established, "
                 "so they are not resolved or shown.\n"
                 "Owner UID is blank for the account's own items (DISK). It is filled only for "
                 "FOREIGN_DISK rows, which the app's album sync writes for items whose owner is "
                 "another account; those rows carry no coordinates.\n"
                 "Shared is 1 when the server marked the item shared (a share object on the album "
                 "path, a shared flag on the WebDAV and index paths); the REST update does not write "
                 "it, so it can be stale. On the REST path Read Only is 1 when shared, not owned and "
                 "without rw rights; other sync paths store the server's readonly flag. Share Group "
                 "reads Family (1), Other (0) or blank when no group was recorded. Offline Mark reads "
                 "Not marked (0), Marked (1) or In marked folder (2), from the app's own enum. Public "
                 "URL is reported as stored; the file-index sync writes the literal FAKE LINK when an "
                 "item is public.\n"
                 "Latitude and Longitude are reported as stored. The app's own queries treat -1 as "
                 "missing, so -1 and NULL are reported blank and left out of the KML. Duration (as "
                 "stored) is milliseconds on the WebDAV sync path; its unit on the album path was not "
                 "established. Width and Height are reported as stored; their unit was not "
                 "established.\n"
                 "Not read by this artifact: the upload queue (see Yandex Disk Uploads), the local "
                 "MediaItems, MediaHashes, MediaDownloads and RECENT_AUTOUPLOADS tables, Album and "
                 "AlbumItem, MOMENTS, FEED and SEARCH tables, pending shared-folder invites, and the "
                 "trash, notes, download queue and account stores beside this database.",
        "paths": ('*/ru.yandex.disk/databases/*_disk*',),
        "output_types": "all",
        "artifact_icon": "cloud",
    },
    "yandex_disk_uploads": {
        "name": "Yandex Disk Uploads",
        "description": "Uploads in the Yandex Disk queue: retained camera autoupload history and pending uploads",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-21",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the DISK_QUEUE table in ru.yandex.disk/databases/<uid>_disk, "
                 "joined to DISK_QUEUE_EXT on upload_id. Account UID is the number in the file name "
                 "and Account is the queue's own user column; Android User is taken from the storage "
                 "path the database came from. Field meanings were sourced from the decompiled Yandex "
                 "Disk 6.90.0 app and were not exercised against a real extraction: the module was "
                 "run only against synthetic databases built from the app's own schema.\n"
                 "What the table keeps matters more than any column. The app deletes completed "
                 "manual uploads (from_autoupload 0 with state 3 or higher). That cleanup does not "
                 "touch completed camera autoupload rows, though other paths can remove them, for "
                 "example when the same file is queued again. So this is mostly a history of "
                 "autouploads plus whatever was still pending, and it holds no history of finished "
                 "manual uploads. Rows can also be copied in from another installed Yandex app that "
                 "shares the queue, so a row is not proof that this app performed the upload.\n"
                 "Times are read as milliseconds and reported in UTC. The writers checked for Date "
                 "Taken, Queued, Autoupload Queued and File Modified When Hashed store milliseconds; "
                 "the others were not traced. Uploaded is the time the app wrote when it marked an "
                 "upload done, so Uploaded is blank on every row that had not finished (Status Queued "
                 "or Paused or failed). A row can also carry Done (3) with a blank Uploaded: the app "
                 "writes 3 without a time when it marks queued manual uploads done and for folder "
                 "rows. The stored date column means different things by upload type: for camera "
                 "autoupload it is the MediaStore date taken (or date added), reported as Date Taken; "
                 "for a manual upload it is the time the upload was queued, reported as Queued. For "
                 "any other upload type its meaning was not established and it is reported only as "
                 "Date (ms, as stored). ETIME is reported as stored; when it is 0 at hashing time the "
                 "app fills it from a time reader whose sources were not traced. Autoupload Queued "
                 "and Upload Started come from DISK_QUEUE_EXT. File Modified When Hashed is the local "
                 "file's last modified time recorded when the app hashed it.\n"
                 "Local Path is the absolute device path the app read; for a folder row it is the "
                 "folder name only. Destination is the folder and name as queued; camera autouploads "
                 "use the folder /photostream and are renamed to yyyy-MM-dd HH-mm-ss with the "
                 "extension upper-cased, and the zone of that name was not established. Uploaded Path "
                 "is the server location the upload returned. MD5 and SHA-256 are hashes the app "
                 "computed over the local file's content.\n"
                 "Labels are derived from the code that writes each value, and the stored number is "
                 "kept in brackets. Status: Queued (1), Paused or failed (2), Done (3); 0 and 4 are "
                 "reported as Legacy code, because the app's migrations rewrite them to 3 and no "
                 "current writer of either was found. Upload Type: Manual (0), Camera autoupload (1), "
                 "Re-upload (3); a completed type 3 row is stored as 1, and no writer of 4 was found. "
                 "Error: Generic (0), Name conflict (1), File too big (2), Local file unavailable "
                 "(3), Local file not readable (4), Files limit or paused (5), Shared folder files "
                 "limit (6), Disk read-only (8); no writer of 7 was found. Media Type: Image (100), "
                 "Video (200), Other (0). Local Cleanup is the app's free-up-space state: Unchecked "
                 "(0), Selected for check (1), Local file deleted (2), Not checked again (3), Error "
                 "(4), Waiting for indexing (5). Local file deleted (2) has two writers: the "
                 "free-up-space process after it deletes the local original, and the upload path when "
                 "the local file of an already uploaded duplicate is gone. So 2 shows the local file "
                 "was gone, not which of the two happened. Any code outside these lists is reported "
                 "as Unknown with its number.\n"
                 "The local files are not resolved or shown in this version. A separate "
                 "disk_queue_snapshot database, which the app uses while migrating queue rows, is "
                 "not read. The AUTOUPLOAD_SYNC_V2 tables that database version 85 added are not "
                 "read.",
        "paths": ('*/ru.yandex.disk/databases/*_disk*',),
        "output_types": "standard",
        "artifact_icon": "upload-cloud",
    },
}

import os
import re

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, \
    logfunc
from scripts.artifacts.storagePathViews import canonical_path, unique_files

DISK_DB = re.compile(r'(?:^|/)ru\.yandex\.disk/databases/(\d+)_disk$')
STORAGE_USER = re.compile(r'\x00(?:ce|de):(\d+)\x00')

OFFLINE_MARK = {0: 'Not marked', 1: 'Marked', 2: 'In marked folder'}
SHARE_GROUP = {0: 'Other', 1: 'Family'}
QUEUE_STATE = {0: 'Legacy code', 1: 'Queued', 2: 'Paused or failed', 3: 'Done', 4: 'Legacy code'}
UPLOAD_TYPE = {0: 'Manual', 1: 'Camera autoupload', 3: 'Re-upload'}
ERROR_REASON = {0: 'Generic', 1: 'Name conflict', 2: 'File too big', 3: 'Local file unavailable',
                4: 'Local file not readable', 5: 'Files limit or paused',
                6: 'Shared folder files limit', 8: 'Disk read-only'}
QUEUE_MEDIA_TYPE = {0: 'Other', 100: 'Image', 200: 'Video'}
CLEANUP_STATE = {0: 'Unchecked', 1: 'Selected for check', 2: 'Local file deleted',
                 3: 'Not checked again', 4: 'Error', 5: 'Waiting for indexing'}

DISK_COLUMNS = ('PARENT', 'NAME', 'IS_DIR', 'SIZE', 'ETAG', 'ETAG_LOCAL', 'LAST_MODIFIED', 'ETIME',
                'LAST_ACCESS', 'MIME_TYPE', 'MEDIA_TYPE', 'PUBLIC_URL', 'SHARED', 'READONLY',
                'SHARE_GROUP_TYPE', 'OFFLINE_MARK', 'LATITUDE', 'LONGITUDE', 'WIDTH', 'HEIGHT',
                'DURATION', 'RESOURCE_ID')
QUEUE_COLUMNS = ('_id', 'src_name', 'dest_dir', 'dest_name', 'date', 'uploaded_size', 'state',
                 'error_reason', 'md5', 'md5_time', 'is_dir', 'from_autoupload', 'ETIME', 'SIZE',
                 'MEDIA_TYPE', 'sha256', 'uploaded_time', 'user')
QUEUE_EXT_COLUMNS = ('cleanup_state', 'uploaded_path', 'added_to_queue_time', 'upload_started_time',
                     'enqueued_network')


def _disk_databases(context):
    """(Android user, account uid, path) for every <uid>_disk database, one copy per storage view.

    An Android extraction carries the app's private directory under data/data, data/user/0
    and data_mirror, so the seeker's list would open each database once per view. The
    Android user comes from the storage view, so one Yandex account signed in on two
    Android users (a work profile, for instance) stays two sets of rows.
    """
    found = []
    for path in unique_files(context):
        path = str(path)
        if os.path.isdir(path):
            continue
        match = DISK_DB.search(path.replace('\\', '/'))
        if not match:
            continue
        key, _ = canonical_path(context.get_relative_path(path))
        user = STORAGE_USER.search(key)
        found.append((user.group(1) if user else '', match.group(1), path))
    return sorted(found)


def _columns(db_path, table):
    """The column names a table has in this database, empty when the table is absent."""
    return {r[1] for r in get_sqlite_db_records(db_path, f'PRAGMA table_info("{table}")')}


def _select(present, wanted, alias=''):
    """A select list naming every wanted column, NULL for the ones this schema lacks."""
    prefix = f'{alias}.' if alias else ''
    return ', '.join(f'{prefix}"{c}"' if c in present else 'NULL' for c in wanted)


def _ms(value):
    """A stored millisecond epoch as a UTC datetime, blank for NULL or 0."""
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) / 1000)
    except (TypeError, ValueError, OverflowError):
        return ''


def _label(mapping, value):
    if value is None or value == '':
        return ''
    try:
        code = int(value)
    except (TypeError, ValueError):
        return f'Unknown ({value})'
    return f'{mapping[code]} ({code})' if code in mapping else f'Unknown ({code})'


def _coordinate(value):
    """A stored coordinate, blank for NULL or the app's -1 marker for a missing value."""
    if value is None or value == '' or value == -1:
        return ''
    return value


def _path(parent, name):
    if not parent:
        return name or ''
    return f'{parent.rstrip("/")}/{name or ""}'


@artifact_processor
def yandex_disk_cloud_files(context):
    data_list = []
    sources = []
    for android_user, uid, db_path in _disk_databases(context):
        read_rows = False
        for table in ('DISK', 'FOREIGN_DISK'):
            present = _columns(db_path, table)
            if not present:
                continue
            owner = '"OWNER_UID"' if 'OWNER_UID' in present else 'NULL'
            query = f'SELECT {_select(present, DISK_COLUMNS)}, {owner} FROM "{table}"'
            for r in get_sqlite_db_records(db_path, query):
                read_rows = True
                data_list.append((
                    _ms(r[6]), _ms(r[7]), _ms(r[8]), android_user, uid, r[22] or '',
                    _path(r[0], r[1]), 'Folder' if r[2] else 'File', r[3],
                    r[9] or '', r[10] or '', r[4] or '', r[5] or '', r[11] or '',
                    r[12], r[13], _label(SHARE_GROUP, r[14]), _label(OFFLINE_MARK, r[15]),
                    _coordinate(r[16]), _coordinate(r[17]), r[18], r[19], r[20], r[21] or ''))
        if read_rows:
            sources.append(db_path)
        else:
            logfunc(f'Yandex Disk: no DISK rows read from {os.path.basename(db_path)}')

    data_headers = (
        ('Last Modified', 'datetime'), ('EXIF Date', 'datetime'),
        ('Local Copy Last Access', 'datetime'), 'Android User', 'Account UID', 'Owner UID', 'Path',
        'Type',
        'Size (bytes)', 'MIME Type', 'Media Type', 'ETag', 'Local Copy MD5', 'Public URL',
        'Shared', 'Read Only', 'Share Group', 'Offline Mark', 'Latitude', 'Longitude', 'Width',
        'Height', 'Duration (as stored)', 'Resource ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def yandex_disk_uploads(context):
    data_list = []
    sources = []
    for android_user, uid, db_path in _disk_databases(context):
        present = _columns(db_path, 'DISK_QUEUE')
        if not present:
            continue
        ext = _columns(db_path, 'DISK_QUEUE_EXT')
        if ext and 'upload_id' in ext:
            query = (f'SELECT {_select(present, QUEUE_COLUMNS, "q")}, '
                     f'{_select(ext, QUEUE_EXT_COLUMNS, "e")} '
                     'FROM DISK_QUEUE q LEFT JOIN DISK_QUEUE_EXT e ON e.upload_id = q._id '
                     'ORDER BY q._id')
        else:
            nulls = ', '.join('NULL' for _ in QUEUE_EXT_COLUMNS)
            query = f'SELECT {_select(present, QUEUE_COLUMNS)}, {nulls} FROM DISK_QUEUE ORDER BY _id'
        read_rows = False
        for r in get_sqlite_db_records(db_path, query):
            read_rows = True
            upload_type = r[11]
            stored_date = r[4]
            date_taken = _ms(stored_date) if upload_type == 1 else ''
            queued = _ms(stored_date) if upload_type == 0 else ''
            other_date = stored_date if upload_type not in (0, 1) and stored_date else ''
            destination = _path(r[2], r[3])
            data_list.append((
                _ms(r[16]), date_taken, queued, _ms(r[12]), _ms(r[20]), _ms(r[21]), _ms(r[9]),
                android_user, uid, r[17] or '', _label(UPLOAD_TYPE, upload_type), _label(QUEUE_STATE, r[6]),
                _label(ERROR_REASON, r[7]), 'Folder' if r[10] else 'File',
                _label(QUEUE_MEDIA_TYPE, r[14]), r[1] or '', destination, r[19] or '',
                r[13], r[5], r[8] or '', r[15] or '', _label(CLEANUP_STATE, r[18]),
                r[22] or '', other_date, r[0]))
        if read_rows:
            sources.append(db_path)

    data_headers = (
        ('Uploaded', 'datetime'), ('Date Taken', 'datetime'), ('Queued', 'datetime'),
        ('ETIME', 'datetime'), ('Autoupload Queued', 'datetime'),
        ('Upload Started', 'datetime'), ('File Modified When Hashed', 'datetime'),
        'Android User', 'Account UID', 'Account', 'Upload Type', 'Status', 'Error', 'Type',
        'Media Type',
        'Local Path', 'Destination', 'Uploaded Path', 'Size (bytes)', 'Uploaded (bytes)', 'MD5',
        'SHA-256', 'Local Cleanup', 'Network', 'Date (ms, as stored)', 'Queue ID')
    return data_headers, data_list, '\n'.join(sources)
