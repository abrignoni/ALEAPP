"""Additional Samsung My Files artifacts.

Newer Samsung My Files (com.sec.android.app.myfiles) splits its data across
several Room databases. The existing modules cover download/recent/cache/trash;
this one adds tables that were not parsed: the local file index, the storage
analyzer inventory, frequently used folders, file search terms, the home screen
items, per-app trash counts, and the file operation log with cleartext paths.

A device can hold more than one copy of each database (for example the main
user and a secure-folder user 150), so every matching database is read and its
rows are combined, with a Source File column naming the copy each row came from.

Where a table holds no data on the registered test corpora it is noted; those
layouts were mapped against a private Android 16 sample supplied by Mattia
Epifani and are corpus-unexercised. Row timestamps are Unix milliseconds unless
noted; operation dates are stored as human strings in the device's local time.
"""
__artifacts_v2__ = {
    "get_smyfiles_local_files": {
        "name": "My Files - Local Files",
        "description": "Local file index (path, name, type, size, timestamps) from the Samsung My Files FileInfo.db local_files table",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "The local_files table is the app's index of local storage. is_hidden and is_trashed "
                 "are integer flags reported as stored. The Cached Thumbnail column shows the app's "
                 "cached preview when FileCache.db links one to the file's path; the preview is a "
                 "cache and its presence does not establish that the original file is still on the "
                 "device.",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileInfo.db*',
                  '*/com.sec.android.app.myfiles/databases/FileCache.db*',
                  '*/com.sec.android.app.myfiles/cache/*.jpg'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 16 rows",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 20 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 13 rows",
        },
    },
    "get_smyfiles_analyze_storage": {
        "name": "My Files - Storage Analysis",
        "description": "File inventory from the Samsung My Files storage analyzer (FileInfo.db analyze_storage table)",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "analyze_storage is the file list the app's storage-analysis feature builds. as_type "
                 "and mediaType are integer category codes reported as stored. The Cached Thumbnail "
                 "column shows the app's cached preview when FileCache.db links one to the file's "
                 "path; the preview is a cache and its presence does not establish that the original "
                 "file is still on the device. Empty on the registered corpora; the layout was mapped "
                 "against a private Android 16 sample.",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileInfo.db*',
                  '*/com.sec.android.app.myfiles/databases/FileCache.db*',
                  '*/com.sec.android.app.myfiles/cache/*.jpg'),
        "output_types": "standard",
        "artifact_icon": "hard-drive",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 0 rows",
        },
    },
    "get_smyfiles_frequent_folders": {
        "name": "My Files - Frequent Folders",
        "description": "Frequently accessed folders with an access count from the Samsung My Files Frequency.db",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "frequently_folder records folders the user opens often; mCount is the access count.",
        "paths": ('*/com.sec.android.app.myfiles/databases/Frequency.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 1 row",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 1 row",
        },
    },
    "get_smyfiles_search_history": {
        "name": "My Files - Search History",
        "description": "File search terms and timestamps from the Samsung My Files FileInfo.db search_history table",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "My Files",
        "notes": "search_history holds the search terms the store records for the My Files "
                 "search box. Empty on the "
                 "registered corpora; the layout was mapped against a private Android 16 sample.",
        "paths": ('*/com.sec.android.app.myfiles/databases/FileInfo.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 0 rows",
        },
    },
    "get_smyfiles_home_items": {
        "name": "My Files - Home Items",
        "description": "Home screen items and categories from the Samsung My Files HomeItem.db",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "home_item holds the categories and shortcuts shown on the My Files home screen. "
                 "item_type is an integer code reported as stored. last_used_time is a small integer "
                 "(observed -1 to 3), an ordering rank rather than a timestamp, so it is reported as "
                 "stored.",
        "paths": ('*/com.sec.android.app.myfiles/databases/HomeItem.db*',),
        "output_types": "standard",
        "artifact_icon": "home",
        "sample_data": {
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 48 rows (two user containers, 24 each)",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 24 rows",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 24 rows",
        },
    },
    "get_smyfiles_trash_apps": {
        "name": "My Files - Trash by App",
        "description": "Per-app trashed-item counts from the Samsung My Files TrashAppInfo.db",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "trash_apps records how many items each app has in the trash and their size. Empty on "
                 "the registered corpora; the layout was mapped against a private Android 16 sample.",
        "paths": ('*/com.sec.android.app.myfiles/databases/TrashAppInfo.db*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
        "sample_data": {
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 0 rows",
        },
    },
    "get_smyfiles_operations": {
        "name": "My Files - File Operations",
        "description": "File operations (move to trash, decompress, etc.) with cleartext source and destination paths from OperationHistory.db",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "My Files",
        "notes": "Joins operation_history (date, operation type, page) to operation_history_data (source "
                 "and destination paths, in cleartext). This is separate from the My Files Operation "
                 "History artifact, whose paths are encoded and which is limited to Android 10-12: the "
                 "paths here are stored in cleartext and read on newer versions too. The operation date "
                 "is reported exactly as stored; its timezone has not been verified. Empty on the "
                 "registered corpora; the layout was mapped against a private Android 16 sample.",
        "paths": ('*/com.sec.android.app.myfiles/databases/OperationHistory.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.myfiles | 0 rows",
        },
    },
}

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly,
                               does_table_exist_in_db, null_absent_columns,
                               convert_unix_ts_to_utc, check_in_media)

_MYFILES = 'com.sec.android.app.myfiles'


def _thumbnail_map(files_found):
    """Map an original file path to its cached thumbnail file on disk.

    FileCache.db records, per cached preview, the original file path (_data) and
    an index; the preview itself is <container>/cache/<index>.jpg. The index is
    only unique within one app container, so a preview is matched to its
    FileCache within the same container.
    """
    jpg_by_key = {}
    marker = f'/{_MYFILES}/cache/'
    for file_found in files_found:
        nf = str(file_found).replace('\\', '/')
        if marker in nf and nf.endswith('.jpg') and '/mirror/' not in nf:
            container = nf[:nf.index(marker)] + f'/{_MYFILES}'
            jpg_by_key[(container, nf.rsplit('/', 1)[1])] = str(file_found)

    thumb_by_path = {}
    db_marker = f'/{_MYFILES}/databases/FileCache.db'
    for file_found in files_found:
        nf = str(file_found).replace('\\', '/')
        if not nf.endswith(db_marker) or '/mirror/' in nf:
            continue
        container = nf[:nf.index(db_marker)] + f'/{_MYFILES}'
        db = open_sqlite_db_readonly(str(file_found))
        if db is None:
            continue
        try:
            if not does_table_exist_in_db(str(file_found), 'FileCache'):
                continue
            for index, data in db.execute(
                    'SELECT _index, _data FROM FileCache WHERE _data IS NOT NULL'):
                jpg = jpg_by_key.get((container, f'{index}.jpg'))
                if jpg:
                    thumb_by_path[data] = jpg
        finally:
            db.close()
    return thumb_by_path


def _dbs(files_found, basename):
    """Every extracted copy of basename (e.g. main user and user 150), skipping
    -wal/-shm sidecars and mirror copies."""
    out = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(basename):
            continue
        if '/mirror/' in file_found.replace('\\', '/'):
            continue
        out.append(file_found)
    return out


def _rows(db_path, table, query):
    """Rows for query when db_path opens and table exists, else an empty list."""
    if not does_table_exist_in_db(db_path, table):
        return []
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(null_absent_columns(db_path, query))
        rows = cursor.fetchall()
    finally:
        db.close()
    return rows


def _collect(context, basename, table, query, shape):
    """Run query over every copy of basename, mapping each row through shape and
    appending the row's relative source path."""
    data_list = []
    sources = []
    for db_path in _dbs(context.get_files_found(), basename):
        rel_path = context.get_relative_path(db_path)
        seen = False
        for row in _rows(db_path, table, query):
            data_list.append(shape(row) + (rel_path,))
            seen = True
        if seen:
            sources.append(rel_path)
    return data_list, ', '.join(dict.fromkeys(sources))


@artifact_processor
def get_smyfiles_local_files(context):
    data_headers = (
        ('Date Modified', 'datetime'), 'Name', ('Cached Thumbnail', 'media'), 'Ext.', 'MIME Type',
        'Size', 'Path', 'Data', 'Is Hidden', 'Is Trashed', 'Source File')
    thumbs = _thumbnail_map(context.get_files_found())

    def shape(r):
        jpg = thumbs.get(r[6])   # r[6] = _data (the absolute file path)
        media = check_in_media(jpg, r[1]) if jpg else ''
        return (convert_unix_ts_to_utc(r[0]), r[1], media, r[2], r[3], r[4], r[5], r[6], r[7], r[8])

    data_list, source = _collect(
        context, 'FileInfo.db', 'local_files',
        '''SELECT date_modified, name, ext, mime_type, size, path, _data, is_hidden, is_trashed
           FROM local_files''', shape)
    return data_headers, data_list, source


@artifact_processor
def get_smyfiles_analyze_storage(context):
    data_headers = (
        ('Date Modified', 'datetime'), 'Name', ('Cached Thumbnail', 'media'), 'Ext.', 'MIME Type',
        'Size', 'Path', 'Storage Type (as stored)', 'Media Type (as stored)', 'Source File')
    thumbs = _thumbnail_map(context.get_files_found())

    def shape(r):
        jpg = thumbs.get(r[6])   # r[6] = _data (the absolute file path)
        media = check_in_media(jpg, r[1]) if jpg else ''
        return (convert_unix_ts_to_utc(r[0]), r[1], media, r[2], r[3], r[4], r[5], r[7], r[8])

    data_list, source = _collect(
        context, 'FileInfo.db', 'analyze_storage',
        '''SELECT date_modified, name, ext, mime_type, size, path, _data, as_type, mediaType
           FROM analyze_storage''', shape)
    return data_headers, data_list, source


@artifact_processor
def get_smyfiles_frequent_folders(context):
    data_headers = (
        ('Date Modified', 'datetime'), 'Access Count', 'Name', 'Path', 'Size', 'Source File')
    data_list, source = _collect(
        context, 'Frequency.db', 'frequently_folder',
        'SELECT date_modified, mCount, name, path, size FROM frequently_folder',
        lambda r: (convert_unix_ts_to_utc(r[0]), r[1], r[2], r[3], r[4]))
    return data_headers, data_list, source


@artifact_processor
def get_smyfiles_search_history(context):
    data_headers = (
        ('Date', 'datetime'), 'Search Term', 'Item Type (as stored)', 'Domain Type (as stored)',
        'Source File')
    data_list, source = _collect(
        context, 'FileInfo.db', 'search_history',
        'SELECT date_modified, name, item_type, domain_type FROM search_history',
        lambda r: (convert_unix_ts_to_utc(r[0]), r[1], r[2], r[3]))
    return data_headers, data_list, source


@artifact_processor
def get_smyfiles_home_items(context):
    data_headers = (
        'Name', 'Item Type (as stored)', 'Is Active', 'Is Visible', 'Rail Priority',
        'Usage Rank (as stored)', 'Source File')
    data_list, source = _collect(
        context, 'HomeItem.db', 'home_item',
        '''SELECT name, item_type, is_active_item, item_visibility, navigation_rail_priority,
                  last_used_time
           FROM home_item''',
        lambda r: (r[0], r[1], r[2], r[3], r[4], r[5]))
    return data_headers, data_list, source


@artifact_processor
def get_smyfiles_trash_apps(context):
    data_headers = (
        'Package Name', 'Item Count', 'Size', 'App Data Size', 'Intent Action', 'Source File')
    data_list, source = _collect(
        context, 'TrashAppInfo.db', 'trash_apps',
        'SELECT package_name, item_count, size, app_data_size, intent_action FROM trash_apps',
        lambda r: (r[0], r[1], r[2], r[3], r[4]))
    return data_headers, data_list, source


@artifact_processor
def get_smyfiles_operations(context):
    data_headers = (
        'Operation Date (timezone unverified)', 'Operation', 'Source Path', 'Destination Path',
        'Page Type', 'File Type (as stored)', 'Source File')
    data_list = []
    sources = []
    for db_path in _dbs(context.get_files_found(), 'OperationHistory.db'):
        if not (does_table_exist_in_db(db_path, 'operation_history')
                and does_table_exist_in_db(db_path, 'operation_history_data')):
            continue
        rel_path = context.get_relative_path(db_path)
        seen = False
        for row in _rows(db_path, 'operation_history', '''
                SELECT h.mDate, h.mOperationType, d.src_path, d.dst_path, h.mPageType, d.file_type
                FROM operation_history h
                JOIN operation_history_data d ON d.operation_id = h._id'''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], rel_path))
            seen = True
        if seen:
            sources.append(rel_path)
    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
