__artifacts_v2__ = {
    "samsung_gallery_hidden_album": {
        "name": "Samsung Gallery Hidden Album",
        "description": "Rows of the files table in the Samsung Gallery secured.db, with the media file each "
                       "row's _data path points at when that file was extracted from sec_pass storage",
        "author": "@Snoop168, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-25",
        "requirements": "none",
        "category": "Samsung Gallery",
        "notes": "The contributor reports that secured.db and the sec_pass media were only present in an "
                 "extraction taken while the Hidden Album was unlocked. Developed against one contributor "
                 "case that cannot be shared. The contributor supplied the files table schema and the path "
                 "layout from that case (PR #1434); the committed fixture is synthetic, built on that "
                 "schema with invented values, so it exercises the parsing logic and not real content. No "
                 "public corpus image is known to carry the store. Date Added, Date Modified, Datetime and "
                 "Date Deleted are converted by value magnitude (seconds, milliseconds or microseconds) "
                 "because their stored unit has not been confirmed. Is Trashed and Is Favorite are the "
                 "stored integers, not interpreted. The media column is filled only when an extracted "
                 "file's path ends with the row's _data path, compared exactly first and then ignoring "
                 "case, since the schema declares _data COLLATE NOCASE; it is not matched by file name "
                 "alone, so a same-named file in another sec_pass folder is never shown in its place. A row "
                 "with no match keeps its _data value in Stored Path (_data). Files in sec_pass storage that "
                 "no row references are not reported.",
        "paths": ('*/sec/gallery/secured/databases/secured.db*', '*/data/sec_pass/*'),
        "output_types": "standard",
        "artifact_icon": "photo"
    }
}

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc, \
    open_sqlite_db_readonly

# (column, header) in output order; a column missing from a given secured.db reports blank.
COLUMNS = (
    ('date_added', ('Date Added', 'datetime')),
    ('date_modified', ('Date Modified', 'datetime')),
    ('datetime', ('Datetime', 'datetime')),
    ('date_deleted', ('Date Deleted', 'datetime')),
    ('_data', ('Media', 'media')),
    ('_data', 'Stored Path (_data)'),
    ('_size', 'Size'),
    ('mime_type', 'MIME Type'),
    ('width', 'Width'),
    ('height', 'Height'),
    ('_display_name', 'Display Name'),
    ('bucket_display_name', 'Bucket Display Name'),
    ('original_path', 'Original Path'),
    ('captured_url', 'Captured URL'),
    ('captured_app', 'Captured App'),
    ('captured_original_path', 'Captured Original Path'),
    ('cam_model', 'Cam Model'),
    ('latitude', 'Latitude'),
    ('longitude', 'Longitude'),
    ('is_trashed', 'Is Trashed (as stored)'),
    ('is_favorite', 'Is Favorite (as stored)'),
    ('original_file_hash', 'Original File Hash'),
    ('owner_package_name', 'Owner Package Name'),
)


def _to_utc(value):
    if value in (None, '', 0):
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (ValueError, TypeError, OverflowError):
        return ''


def _find_media(data_path, media_files):
    """The extracted file whose path ends with the row's _data path, or None.

    An exact match wins; otherwise case is ignored, as the files table compares _data NOCASE.
    """
    if not data_path:
        return None
    suffix = '/' + str(data_path).replace('\\', '/').lstrip('/')
    normalized = [(media_file, media_file.replace('\\', '/')) for media_file in media_files]
    for media_file, path in normalized:
        if path.endswith(suffix):
            return media_file
    folded = suffix.casefold()
    for media_file, path in normalized:
        if path.casefold().endswith(folded):
            return media_file
    return None


@artifact_processor
def samsung_gallery_hidden_album(context):
    data_list = []
    data_headers = tuple(header for _, header in COLUMNS)
    source_paths = []
    files_found = [str(f) for f in context.get_files_found()]
    media_files = [f for f in files_found if '/sec_pass/' in f.replace('\\', '/')]
    wanted = list(dict.fromkeys(col for col, _ in COLUMNS))

    for file_found in files_found:
        if not file_found.endswith('secured.db'):
            continue
        source_paths.append(file_found)

        db = open_sqlite_db_readonly(file_found)
        if not db:
            continue
        cursor = db.cursor()
        cursor.execute("SELECT name FROM pragma_table_info('files')")
        present = {row[0] for row in cursor.fetchall()}
        if not present:
            logfunc(f'Samsung Gallery Hidden Album: no files table in {file_found}')
            db.close()
            continue

        select = ', '.join(f'"{col}"' if col in present else 'NULL' for col in wanted)
        cursor.execute(f'SELECT {select} FROM files')
        for row in cursor.fetchall():
            record = dict(zip(wanted, row))
            out = []
            for col, header in COLUMNS:
                value = record[col]
                if header == ('Media', 'media'):
                    media_file = _find_media(value, media_files)
                    out.append(check_in_media(media_file, record['_display_name'] or '') if media_file else '')
                elif isinstance(header, tuple) and header[1] == 'datetime':
                    out.append(_to_utc(value))
                else:
                    out.append('' if value is None else value)
            data_list.append(tuple(out))
        db.close()

    return data_headers, data_list, '\n'.join(source_paths)
