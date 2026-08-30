__artifacts_v2__ = {
    "fossify_gallery_media": {
        "name": "Fossify Gallery - Media",
        "description": "Parses the media index kept by the Fossify Gallery Android app and its Simple Mobile Tools predecessor.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Fossify Gallery",
        "notes": "One row per entry in the media table of databases/gallery.db. This table is the app's "
                 "own index of the images and videos it has seen, and it keeps three things a plain "
                 "media scan does not: whether the user favourited a file, when a file was moved to the "
                 "app's recycle bin, and the file's recorded date taken. Each row carries the Filename "
                 "and Full Path as stored, the Type, the Size in bytes, the Video Duration in seconds, "
                 "the Favorite flag, and three times. Type is decoded from the app's media-type "
                 "constants, 1 image, 2 video, 4 GIF, 8 raw, 16 SVG, 32 portrait (Constants.kt at "
                 "FossifyOrg/Gallery b28299dc33821eee8d108a9880ce87876cf31443); on the tested files it "
                 "was image on every row. Video Duration is 0 for a still image and was 0 on every "
                 "tested row. Deleted is set from deleted_ts, which is non-zero only when the file is in "
                 "the app's recycle bin, and records when it was deleted; for a recycled file the Full "
                 "Path is stored with a recycle_bin/ prefix and the file's bytes are kept under the "
                 "app's files/.recycle_bin folder, so a non-empty Deleted value marks a file the user "
                 "removed but that may still be recoverable. Date Taken, Last Modified and Deleted are "
                 "all Unix milliseconds and are reported as UTC; on the tested device the deletion time "
                 "18:00 UTC matched the device's 2:00 PM local action. The Favorite flag was confirmed "
                 "against a favourited file, and the deleted state against a file moved to the recycle "
                 "bin. Three related tables are not parsed here: favorites duplicates the favourite list "
                 "the is_favorite flag already carries, date_takens holds corrected date-taken values, "
                 "and directories is a per-folder cache. The app is the maintained successor to Simple "
                 "Mobile Tools Gallery and uses the identical schema, so the paths cover both "
                 "org.fossify.gallery (tested) and com.simplemobiletools.gallery.pro (same schema, from "
                 "the shared source, not exercised here).",
        "paths": (
            '*/org.fossify.gallery/databases/gallery.db*',
            '*/com.simplemobiletools.gallery.pro/databases/gallery.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/gallery.db'

# Constants.kt at FossifyOrg/Gallery b28299dc33821eee8d108a9880ce87876cf31443.
MEDIA_TYPES = {1: 'Image', 2: 'Video', 4: 'GIF', 8: 'Raw', 16: 'SVG', 32: 'Portrait'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _type(value):
    if value in MEDIA_TYPES:
        return MEDIA_TYPES[value]
    return f'{value} (as stored)'


@artifact_processor
def fossify_gallery_media(context):
    query = '''SELECT filename, full_path, type, size, video_duration, is_favorite,
                      deleted_ts, date_taken, last_modified
               FROM media ORDER BY deleted_ts DESC, filename'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            favorite = 'Yes' if r[5] else 'No'
            data_list.append((
                r[0] or '', r[1] or '', _type(r[2]), r[3], r[4], favorite,
                _ms(r[6]), _ms(r[7]), _ms(r[8]), context.get_relative_path(db_path),
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Filename', 'Full Path', 'Type', 'Size', 'Video Duration', 'Favorite',
        ('Deleted', 'datetime'), ('Date Taken', 'datetime'),
        ('Last Modified', 'datetime'), 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
