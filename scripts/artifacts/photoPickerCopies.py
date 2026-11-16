__artifacts_v2__ = {
    "get_photo_picker_copies": {
        "name": "Photo Picker Cached Copies",
        "description": "Files the system Photo Picker wrote under .transforms/synthetic when it handed a photo "
                       "or video to an app, with their recorded file times, and the original's MediaStore or "
                       "picker.db record and, when the extraction holds it, the original file.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Media",
        "notes": "One row per file under .transforms/synthetic/picker*/<user>/<provider>/media/ on primary"
                 " shared storage. MediaProvider names the folder from the picker session: "
                 "picker_get_content when the picker was opened with ACTION_GET_CONTENT, picker otherwise "
                 "( "
                 "https://android.googlesource.com/platform/packages/providers/MediaProvider/+/a183e2b92c71d86ec7b104c116ef3f4dbcbb523f/src/com/android/providers/media/PickerUriResolver.java#339"
                 " ). Media ID is the file's name without its extension. For the on-device provider "
                 "(com.android.providers.media.photopicker) it is looked up as _id in the files table of "
                 "the same Android user's external.db and, when absent there, as old_id in its "
                 "deleted_media table; for any other provider (Google Photos' cloudpicker in the samples) "
                 "as cloud_id in picker.db media. Original Matched In names the table that matched. "
                 "'deleted_media only (no files row)' reports that the ID is listed in deleted_media and "
                 "no files row has it; what writes deleted_media was not established (deleting a picked "
                 "photo's file on a test emulator added no row). The same file reached through several "
                 "storage views (data/media/<n> and mnt/pass_through/<n>/emulated/<n>) is reported once. "
                 "Rollback snapshots of external.db and picker.db are not read. Copy Content is what the "
                 "file's bytes are. It was 'all zero bytes' on all 42 corpus rows, at the original's size,"
                 " and on the test emulator, where the file read as root on the device was also "
                 "zero-filled, so the file is not a source for the picture. Original Media shows the "
                 "original instead: the file at the path MediaStore records (_data, "
                 "/storage/emulated/<n>/... searched as media/<n>/... in the extraction), shown only when "
                 "its bytes are an image or video. Original File says whether that file was found and what"
                 " it is. Copy Modified and Copy Accessed are the times the extraction records for the "
                 "file; neither is taken from the staged file. Known data (Android 15 emulator, a Chrome "
                 "file input, one photo picked three times): each confirmed pick rewrote the file, so Copy"
                 " Modified was the most recent pick (17:25:19.96 UTC for a pick logged at 17:25:20.25), "
                 "while Copy Accessed stayed at the first pick through both re-picks; /data was mounted "
                 "noatime on that emulator. Not tested: the picker folder (apps that request the picker "
                 "directly), cloud picks and real devices. On the 6 corpus images in sample_data (Android "
                 "13 to 17, 42 rows): 33 matched external.db files, 4 matched picker.db media, 4 were "
                 "listed only in deleted_media, and 1 Google Photos copy on kevin_pocox7_a15 matched "
                 "nothing. Original Media showed the original on 32 of the 33 files rows; on the other the"
                 " extraction held no file at the recorded path. Copy Size equalled Original Size on all "
                 "37 matched rows. Original Date Taken was blank on 30 of the 37 because the matched row "
                 "held no value. Copy Accessed was recorded only on hc_pixel8pro_a17, where it was at or "
                 "before Copy Modified on all 8 rows. Copy Accessed had no value on any row of "
                 "hc_pixel8pro_a16, kevin_pocox7_a15, pixel7a_a14, russell_a14 and russell_pixel6a_a13: "
                 "those extractions record no accessed time. On pixel7a_a14 Provider (as stored) held one "
                 "value on all 19 rows, and Original Date Added and Original Date Modified were identical "
                 "on all 19 rows as stored. On russell_a14 and russell_pixel6a_a13 the one row is listed "
                 "only in deleted_media, so Original Date Added, Original Date Modified, Original Size, "
                 "Original Name, Original Path, Original File, Original Media and Original Owner Package "
                 "have no value on it. Copy Content held 'all zero bytes' on every row of every image. "
                 "Android User held 0 on all 42 rows; it is kept because it selects which user's "
                 "external.db is used. Not read: media_grants (empty on hc_pixel8pro_a16; it is in "
                 "external.db on Android 15 and picker.db on Android 16) and the Google Keep and Files by "
                 "Google caches. Suggested by an examiner on a mailing list.",
        "paths": ('*/.transforms/synthetic/picker*/*/media/*',
                  '*/com.google.android.providers.media.module/databases/external.db*',
                  '*/com.android.providers.media.module/databases/external.db*',
                  '*/com.google.android.providers.media.module/databases/picker.db*',
                  '*/com.android.providers.media.module/databases/picker.db*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 8 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.providers.media.module | 8 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 5 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 19 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 1 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 1 rows",
        },
    },
}

import datetime
import os
import re
import sqlite3

from scripts.context import Context
from scripts.ilapfuncs import (artifact_processor, check_in_media, open_sqlite_db_readonly,
                               does_table_exist_in_db, logfunc)
from scripts.artifacts.storagePathViews import canonical_path, snapshot_key, unique_files
from scripts.filetype import guess_mime

# .transforms/synthetic/<folder>/<user>/<authority>/media/<name>
_COPY = re.compile(r'(?:^|/)\.transforms/synthetic/(picker[^/]*)/(\d+)/([^/]+)/media/([^/]+)$')
_DB_USER = re.compile(r'\x00(?:ce|de):(\d+)\x00')
_LOCAL_AUTHORITY = 'com.android.providers.media.photopicker'
_DELETED_ONLY = 'listed_in_deleted_media_only'
_SHARED = re.compile(r'^/storage/emulated/(\d+)/(.+)$')
_GLOB_SPECIAL = str.maketrans({'[': '[[]', ']': '[]]', '*': '[*]', '?': '[?]'})


def _content(path):
    """What the file's bytes are: 'empty', 'all zero bytes', a detected type, or 'not recognised'."""
    with open(path, 'rb') as handle:
        data = handle.read()
    if not data:
        return 'empty'
    if data.count(0) == len(data):
        return 'all zero bytes'
    return guess_mime(data) or 'not recognised'


def _original_file(seeker, data_path):
    """(staged path or None, status) for the file at a MediaStore _data path."""
    match = _SHARED.match(data_path or '')
    if not match:
        return None, 'recorded path is not on shared storage' if data_path else ''
    if seeker is None:
        return None, 'not searched'
    pattern = f'*/media/{match.group(1)}/{match.group(2).translate(_GLOB_SPECIAL)}'
    found = [str(p) for p in seeker.search(pattern) if not os.path.isdir(str(p))]
    if not found:
        return None, 'no file at the recorded path in the extraction'
    staged = sorted(found)[0]
    kind = _content(staged)
    if kind.startswith(('image/', 'video/')):
        return staged, f'in the extraction ({kind})'
    return None, f'in the extraction, not shown ({kind})'


def _utc(seconds):
    if seconds is None:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(seconds), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _times(seeker, file_found):
    info = seeker.file_infos.get(file_found) if seeker else None
    return getattr(info, 'times', None) if info else None


def _external_rows(db_path):
    """{_id: row} for the files table of one external.db."""
    if not does_table_exist_in_db(db_path, 'files'):
        return {}
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return {}
    db.row_factory = sqlite3.Row
    try:
        cols = {r[1] for r in db.execute('PRAGMA table_info(files)')}
        wanted = [c for c in ('_id', '_display_name', '_data', 'date_added', 'date_modified',
                              'datetaken', 'owner_package_name', '_size') if c in cols]
        rows = db.execute(f'SELECT {", ".join(wanted)} FROM files').fetchall()
    except sqlite3.Error as error:
        logfunc(f'Photo Picker Cached Copies: could not read {db_path}: {error}')
        rows = []
    finally:
        db.close()
    found = {str(r['_id']): dict(r) for r in rows}
    if does_table_exist_in_db(db_path, 'deleted_media'):
        db = open_sqlite_db_readonly(db_path)
        if db is not None:
            try:
                for (old_id,) in db.execute('SELECT old_id FROM deleted_media WHERE old_id IS NOT NULL'):
                    found.setdefault(str(old_id), {_DELETED_ONLY: True})
            except sqlite3.Error as error:
                logfunc(f'Photo Picker Cached Copies: could not read deleted_media in {db_path}: {error}')
            finally:
                db.close()
    return found


def _picker_cloud_rows(db_path):
    """{cloud_id: row} for the media table of one picker.db."""
    if not does_table_exist_in_db(db_path, 'media'):
        return {}
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return {}
    db.row_factory = sqlite3.Row
    try:
        rows = db.execute('SELECT cloud_id, date_taken_ms, size_bytes, mime_type FROM media '
                          'WHERE cloud_id IS NOT NULL').fetchall()
    except sqlite3.Error as error:
        logfunc(f'Photo Picker Cached Copies: could not read {db_path}: {error}')
        rows = []
    finally:
        db.close()
    return {r['cloud_id']: dict(r) for r in rows}


def _ms(value):
    return _utc(int(value) // 1000) if value not in (None, '') else ''


@artifact_processor
def get_photo_picker_copies(context):
    seeker = Context.get_seeker()
    files = sorted(unique_files(context), key=str)
    copies = {}
    databases = {'external.db': {}, 'picker.db': {}}
    for file_found in files:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        match = _COPY.search(relative)
        if match:
            copies.setdefault(match.groups(), file_found)
            continue
        base = relative.rsplit('/', 1)[-1]
        if base not in databases or snapshot_key(relative) is not None:
            continue
        user = _DB_USER.search(canonical_path(relative)[0])
        if user:
            databases[base].setdefault(user.group(1), file_found)

    local = {user: _external_rows(path) for user, path in databases['external.db'].items()}
    cloud = {user: _picker_cloud_rows(path) for user, path in databases['picker.db'].items()}
    source_paths = []
    data_list = []
    for (folder, user, authority, name), file_found in sorted(copies.items()):
        source_paths.append(file_found)
        times = _times(seeker, file_found)
        stem = os.path.splitext(name)[0]
        row = {}
        matched_in = ''
        taken, size, db_path = '', '', None
        if authority == _LOCAL_AUTHORITY and stem.isdigit():
            row = local.get(user, {}).get(stem, {})
            if row.get(_DELETED_ONLY):
                matched_in = 'external.db deleted_media only (no files row)'
                db_path = databases['external.db'][user]
                row = {}
            elif row:
                matched_in = 'external.db files'
                taken = _ms(row.get('datetaken'))
                size = row.get('_size', '')
                db_path = databases['external.db'][user]
        elif authority != _LOCAL_AUTHORITY:
            row = cloud.get(user, {}).get(stem, {})
            if row:
                matched_in = 'picker.db media'
                taken = _ms(row.get('date_taken_ms'))
                size = row.get('size_bytes', '')
                db_path = databases['picker.db'][user]
        original_path, original_status = _original_file(seeker, row.get('_data'))
        if db_path and db_path not in source_paths:
            source_paths.append(db_path)
        if original_path:
            source_paths.append(original_path)
        data_list.append((
            _utc(times.modified) if times else '',
            _utc(times.accessed) if times else '',
            taken,
            _utc(row.get('date_added')),
            _utc(row.get('date_modified')),
            check_in_media(original_path, row.get('_display_name', '')) if original_path else '',
            folder,
            authority,
            user,
            stem,
            os.path.getsize(file_found),
            _content(file_found),
            size,
            row.get('_display_name', ''),
            row.get('_data', ''),
            original_status,
            row.get('owner_package_name', '') or '',
            matched_in,
        ))

    data_headers = (
        ('Copy Modified', 'datetime'),
        ('Copy Accessed', 'datetime'),
        ('Original Date Taken', 'datetime'),
        ('Original Date Added', 'datetime'),
        ('Original Date Modified', 'datetime'),
        ('Original Media', 'media'),
        'Picker Folder',
        'Provider (as stored)',
        'Android User',
        'Media ID',
        ('Copy Size', 'number'),
        'Copy Content',
        ('Original Size', 'number'),
        'Original Name',
        'Original Path',
        'Original File',
        'Original Owner Package',
        'Original Matched In',
    )
    return data_headers, data_list, '\n'.join(source_paths)
