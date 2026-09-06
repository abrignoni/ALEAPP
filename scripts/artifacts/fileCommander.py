__artifacts_v2__ = {
    "file_commander_recycle_bin": {
        "name": "File Commander Recycle Bin",
        "description": "Files deleted through File Commander, with the path each one came from",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "File Commander",
        "sample_data": {
            "emu_a15_oss_v17": "File Commander 10.7.54240 | 1 row",
        },
        "notes": "One row per row of trash_entries in "
                 "com.mobisystems.fileman/databases/TrashBin.db, joined to trash_folders on "
                 "trash_folder_id to build the location the deleted bytes were moved to. The app "
                 "renames a file when it deletes it, so Original Name and Original Location come "
                 "from the database while Name In Trash is what the file is called on disk, and "
                 "Recovered From is root_path, relative_path and Name In Trash concatenated. That "
                 "mapping is one the store recorded, not a match on size or time. Measured on the "
                 "tested device by creating a file, deleting it through the app and choosing the "
                 "Recycle Bin rather than Delete permanently: the row named the original path "
                 "under Download, the file was present in the app's trash folder under a new name, "
                 "and its bytes and modification time were unchanged. There is no deletion "
                 "timestamp in either table, so a row does not say when the deletion happened. "
                 "Choosing Delete permanently in the same dialog was not exercised, so whether "
                 "that writes a row here was not established.",
        "paths": ('*/com.mobisystems.fileman/databases/TrashBin.db*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
    },
    "file_commander_favorites": {
        "name": "File Commander Favorites",
        "description": "Locations recorded in the app's bookmarks store",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "File Commander",
        "sample_data": {
            "emu_a15_oss_v17": "File Commander 10.7.54240 | 0 rows",
        },
        "notes": "One row per row of the bookmarks table in "
                 "com.mobisystems.fileman/databases/bookmarks.db. Time is Unix milliseconds "
                 "rendered as UTC where present. This produced no rows on the tested device, and "
                 "the reason was measured rather than assumed: the Add to favorites action exists "
                 "in the app's selection menu, and using it opens an upgrade screen reading "
                 "Favorites, part of File Commander Premium, so the table stays empty on an "
                 "install without the paid tier. The database and the table are created regardless. "
                 "An empty result is therefore not evidence that no location was ever of interest "
                 "to a person, and the columns here are reported as stored because no populated "
                 "example was available to check them against.",
        "paths": ('*/com.mobisystems.fileman/databases/bookmarks.db*',),
        "output_types": "standard",
        "artifact_icon": "star",
    },
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

TRASH_DB = 'databases/TrashBin.db'
BOOKMARKS_DB = 'databases/bookmarks.db'


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


def _join(root, relative, name):
    """Rebuild the on-disk location of a trashed file from the parts the store holds."""
    root = (root or '').rstrip('/')
    relative = (relative or '')
    if relative and not relative.startswith('/'):
        relative = '/' + relative
    relative = relative.rstrip('/')
    if not name:
        return f'{root}{relative}'
    return f'{root}{relative}/{name}'


@artifact_processor
def file_commander_recycle_bin(context):
    query = '''SELECT e.original_name, e.original_location, e.name_in_trash,
                      f.root_path, f.relative_path
               FROM trash_entries e
               LEFT JOIN trash_folders f ON f._id = e.trash_folder_id
               ORDER BY e._id'''
    data_list = []
    sources = []
    for db_path in _files(context, TRASH_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((r[0] or '', r[1] or '', r[2] or '',
                              _join(r[3], r[4], r[2]),
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Original Name', 'Original Location', 'Name In Trash', 'Recovered From',
        'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def file_commander_favorites(context):
    query = '''SELECT time, name, uri, ext, isDir, size, isShared, isSynced,
                      isAvailableOffline, is_user_deleted
               FROM bookmarks ORDER BY time DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, BOOKMARKS_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4], r[5],
                              r[6], r[7], r[8], r[9], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Added', 'datetime'), 'Name', 'URI', 'Extension', 'Is Directory', 'Size',
        'Is Shared', 'Is Synced', 'Available Offline', 'User Deleted', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
