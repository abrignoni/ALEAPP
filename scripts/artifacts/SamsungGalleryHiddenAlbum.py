__artifacts_v2__ = {
    "samsung_gallery_hidden_album": {
        "name": "Samsung Gallery Hidden Album",
        "description": "Rows of the files table in the Samsung Gallery secured.db, with the media file each "
                       "row's _data path points at when that file was extracted from sec_pass storage",
        "author": "@Snoop168, Claude",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-24",
        "requirements": "none",
        "category": "Samsung Gallery",
        "notes": "The contributor reports that secured.db and the sec_pass media were only present in an "
                 "extraction taken while the Hidden Album was unlocked. Developed against one contributor "
                 "case that cannot be shared; the committed fixture is synthetic, built to the column names "
                 "and path layout this module reads, so it exercises the parsing logic and not Samsung's "
                 "real schema. No public corpus image is known to carry the store. Date Added, Date "
                 "Modified and Datetime are converted by value magnitude (seconds, milliseconds or "
                 "microseconds) because their stored unit has not been confirmed against Samsung's source. "
                 "The media column is filled only when an extracted file's path ends with the row's _data "
                 "path; it is not matched by file name alone, so a same-named file in another sec_pass folder "
                 "is never shown in its place. A row with no match keeps its _data value in Stored Path "
                 "(_data). Files in sec_pass storage that no row references are not reported.",
        "paths": ('*/sec/gallery/secured/databases/secured.db*', '*/data/sec_pass/*'),
        "output_types": "standard",
        "artifact_icon": "photo"
    }
}

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc, \
    open_sqlite_db_readonly

# Column order of each output row; a column missing from a given secured.db reports blank.
QUERY_COLUMNS = ('date_added', 'date_modified', 'datetime', '_data', '_size', '_display_name',
                 'captured_url', 'original_path', 'cam_model', 'owner_package_name')


def _to_utc(value):
    if value in (None, '', 0):
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (ValueError, TypeError, OverflowError):
        return ''


def _find_media(data_path, media_files):
    """The extracted file whose path ends with the row's _data path, or None."""
    if not data_path:
        return None
    suffix = '/' + str(data_path).replace('\\', '/').lstrip('/')
    for media_file in media_files:
        if media_file.replace('\\', '/').endswith(suffix):
            return media_file
    return None


@artifact_processor
def samsung_gallery_hidden_album(context):
    data_list = []
    data_headers = (
        ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Datetime', 'datetime'), ('Media', 'media'),
        'Stored Path (_data)', 'Size', 'Display Name', 'Captured URL', 'Original Path', 'Cam Model',
        'Owner Package Name')
    source_paths = []
    files_found = [str(f) for f in context.get_files_found()]
    media_files = [f for f in files_found if '/sec_pass/' in f.replace('\\', '/')]

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

        select = ', '.join(f'"{col}"' if col in present else 'NULL' for col in QUERY_COLUMNS)
        cursor.execute(f'SELECT {select} FROM files')
        for row in cursor.fetchall():
            data_path = row[3]
            media_file = _find_media(data_path, media_files)
            media_ref = check_in_media(media_file, row[5] or '') if media_file else ''
            data_list.append((_to_utc(row[0]), _to_utc(row[1]), _to_utc(row[2]), media_ref, data_path or '')
                             + tuple('' if value is None else value for value in row[4:]))
        db.close()

    return data_headers, data_list, '\n'.join(source_paths)
