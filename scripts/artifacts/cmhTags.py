__artifacts_v2__ = {
    "cmh_scene_tags": {
        "name": "CMH Scene Tags",
        "description": "Scene and sub-scene labels Samsung's CMH media provider stored against "
                       "image files, joined to the file each label belongs to.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2025-05-05",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Samsung CMH",
        "notes": "Rows come from the tag_map join table in cmh.db: each row is one label the "
                 "provider recorded against one file, with the label text from the tags table "
                 "and the file path and dates from the files table. Tag Type is the tags "
                 "table's own tag_display_name (values such as Scene and SubScene as stored) "
                 "and Tag is its tag_data.\n"
                 "The labels are produced by the device's own image classification. A label "
                 "records what that classification returned for the image; it is not a "
                 "statement that the subject was present, and the provider does not record who "
                 "or what produced any individual label.\n"
                 "Scene Score is reported as stored and was unpopulated in the images tested. "
                 "The companion CMH artifact reports the files table itself.",
        "paths": ('*/cmh.db*',),
        "output_types": "standard",
        "artifact_icon": "tag",
        "sample_data": {
                "anne_a15": "Android 15 | com.samsung.cmh | 2222 rows",
                "sharon_a14": "Android 14 | com.samsung.cmh | 496 rows",
                "samsungs20_a13": "Android 13 | com.samsung.cmh | 22 rows",
                "s20fe_a13": "Android 13 | com.samsung.cmh | 7 rows",
                "galaxys10_a10": "Android 10 | com.samsung.cmh | 41 rows",
                "samsunga53_a14": "Android 14 | com.samsung.cmh | 0 rows",
            },
    },
    "cmh_ocr_text": {
        "name": "CMH Image OCR Text",
        "description": "Text the Samsung CMH media provider recognised inside image files, "
                       "joined to the file it was read from.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2025-05-05",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Samsung CMH",
        "notes": "Rows come from the ocr_tag table in cmh.db, joined to the files table on "
                 "fk_file_id. Recognised Text is the stored image_ocr_tag value; the provider "
                 "separates the segments it read with 0x1F unit separators, which are shown "
                 "here as ' | ' so the row stays readable. The text is the output of the "
                 "device's own recognition and can be partial or wrong; it is not a "
                 "transcription verified by anything.\n"
                 "Tag Added Timestamp is the ocr_tag row's tag_added_date, stored in "
                 "milliseconds and reported as UTC. Recogniser Version is the version string "
                 "the provider wrote for the model that produced the row, as stored.",
        "paths": ('*/cmh.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
                "anne_a15": "Android 15 | com.samsung.cmh | 52 rows",
                "sharon_a14": "Android 14 | com.samsung.cmh | 1007 rows",
                "samsungs20_a13": "Android 13 | com.samsung.cmh | 7 rows",
                "s20fe_a13": "Android 13 | com.samsung.cmh | 2 rows",
                "galaxys10_a10": "Android 10 | com.samsung.cmh | 6 rows",
                "samsunga53_a14": "Android 14 | com.samsung.cmh | 1 row",
            },
    },
    "cmh_qr_barcodes": {
        "name": "CMH QR and Barcode Content",
        "description": "QR code and barcode content the Samsung CMH media provider recorded "
                       "against image files, joined to the file it was read from.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Samsung CMH",
        "notes": "Rows are the tag_map entries whose scene_qr_barcode_info column is "
                 "populated, joined to the files table. The value is reported exactly as "
                 "stored and is not decoded, resolved or requested; a stored URL is text in "
                 "the database, and its presence records what the provider read from an image "
                 "on the device, not that anyone opened it.\n"
                 "The same content can appear on more than one row where the provider "
                 "recorded it against several files or labels.",
        "paths": ('*/cmh.db*',),
        "output_types": "standard",
        "artifact_icon": "maximize",
        "sample_data": {
                "anne_a15": "Android 15 | com.samsung.cmh | 4 rows",
                "sharon_a14": "Android 14 | com.samsung.cmh | 0 rows",
                "samsungs20_a13": "Android 13 | com.samsung.cmh | 0 rows",
                "s20fe_a13": "Android 13 | com.samsung.cmh | 0 rows",
                "galaxys10_a10": "Android 10 | com.samsung.cmh | 0 rows",
                "samsunga53_a14": "Android 14 | com.samsung.cmh | 0 rows",
            },
    },
    "cmh_user_tags": {
        "name": "CMH User Tags",
        "description": "Tags recorded in the Samsung CMH user tag table, with the file each "
                       "one is linked to where the schema carries that link.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2025-05-05",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Samsung CMH",
        "notes": "Rows come from the usertag table in cmh.db. The table has more than one "
                 "generation: newer databases carry fk_sec_media_id and timestamp, which give "
                 "the linked file and a millisecond timestamp reported as UTC; the older "
                 "generation seen on an Android 10 image carries neither, so those rows are "
                 "reported with the tag value alone and no file or time. Absent columns are "
                 "read as NULL rather than assumed.\n"
                 "Tag Value is the stored user_tag_data. The table name and the values "
                 "observed are consistent with tags applied through the gallery, but the "
                 "database does not record how any individual row was created.",
        "paths": ('*/cmh.db*',),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
                "anne_a15": "Android 15 | com.samsung.cmh | 1 row",
                "sharon_a14": "Android 14 | com.samsung.cmh | 0 rows",
                "samsungs20_a13": "Android 13 | com.samsung.cmh | 0 rows",
                "s20fe_a13": "Android 13 | com.samsung.cmh | 0 rows",
                "galaxys10_a10": "Android 10 | com.samsung.cmh | 0 rows (older usertag schema)",
                "samsunga53_a14": "Android 14 | com.samsung.cmh | 0 rows",
            },
    },
}

import datetime
import hashlib
import sqlite3

from scripts.ilapfuncs import (artifact_processor, does_column_exist_in_db,
                               does_table_exist_in_db, logfunc, open_sqlite_db_readonly)

# The provider separates the text segments it read from an image with 0x1F.
_OCR_SEPARATOR = '\x1f'


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _cmh_databases(files_found):
    """Yield each distinct cmh.db worth querying.

    An extraction can hold several copies (one per user profile, plus tool
    mirror folders), so byte-identical copies are only parsed once. This
    mirrors the selection the companion CMH artifact makes.
    """
    seen_hashes = set()
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if '.magisk' in file_found and 'mirror' in file_found:
            continue
        try:
            with open(file_found, 'rb') as db_file:
                file_hash = hashlib.sha256(db_file.read()).hexdigest()
        except OSError as exc:
            logfunc(f'Samsung CMH tags - could not read {file_found}: {exc}')
            continue
        if file_hash in seen_hashes:
            continue
        seen_hashes.add(file_hash)
        yield file_found


def _query(file_found, sql):
    db = open_sqlite_db_readonly(file_found)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.OperationalError as exc:
        logfunc(f'Unable to query {file_found} (unsupported CMH schema version?): {exc}')
        return []
    finally:
        db.close()


def _run(files_found, required_tables, sql, row_builder):
    """Query every distinct cmh.db that carries the tables this artifact needs."""
    data_list = []
    sources = []
    for file_found in _cmh_databases(files_found):
        missing = [t for t in required_tables if not does_table_exist_in_db(file_found, t)]
        if missing:
            logfunc(f'{", ".join(missing)} not present in {file_found}; '
                    'this CMH schema version is not covered for this artifact')
            continue
        rows = _query(file_found, sql)
        if rows:
            sources.append(file_found)
        for row in rows:
            data_list.append(row_builder(row))
    return data_list, ', '.join(sources)


@artifact_processor
def cmh_scene_tags(context):
    files_found = context.get_files_found()
    sql = '''
        SELECT files.datetaken, files.date_added, tags.tag_display_name, tags.tag_data,
               tag_map.scene_score, files.title, files._data, files.bucket_display_name
        FROM tag_map
        LEFT JOIN tags ON tags.tags_id = tag_map.fk_tag_id
        LEFT JOIN files ON files._id = tag_map.fk_file_id
        ORDER BY files.datetaken
    '''
    data_list, source_path = _run(
        files_found, ('tag_map', 'tags', 'files'), sql,
        lambda r: (_ms_to_utc(r[0]), _sec_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7]))
    data_headers = (
        ('Date Taken', 'datetime'), ('Date Added', 'datetime'), 'Tag Type', 'Tag',
        'Scene Score (as stored)', 'File Name', 'File Path', 'Bucket Name')
    return data_headers, data_list, source_path


@artifact_processor
def cmh_ocr_text(context):
    files_found = context.get_files_found()
    sql = '''
        SELECT ocr_tag.tag_added_date, files.datetaken, ocr_tag.image_ocr_tag,
               ocr_tag.version, files.title, files._data, files.bucket_display_name
        FROM ocr_tag
        LEFT JOIN files ON files._id = ocr_tag.fk_file_id
        ORDER BY ocr_tag.tag_added_date
    '''

    def build(row):
        text = row[2] or ''
        # Show the provider's 0x1F segment separators as a readable delimiter.
        text = ' | '.join(part for part in text.split(_OCR_SEPARATOR) if part)
        return (_ms_to_utc(row[0]), _ms_to_utc(row[1]), text, row[3], row[4], row[5], row[6])

    data_list, source_path = _run(files_found, ('ocr_tag', 'files'), sql, build)
    data_headers = (
        ('Tag Added Timestamp', 'datetime'), ('Date Taken', 'datetime'), 'Recognised Text',
        'Recogniser Version', 'File Name', 'File Path', 'Bucket Name')
    return data_headers, data_list, source_path


@artifact_processor
def cmh_qr_barcodes(context):
    files_found = context.get_files_found()
    sql = '''
        SELECT files.datetaken, files.date_added, tag_map.scene_qr_barcode_info,
               files.title, files._data, files.bucket_display_name
        FROM tag_map
        LEFT JOIN files ON files._id = tag_map.fk_file_id
        WHERE tag_map.scene_qr_barcode_info IS NOT NULL
          AND tag_map.scene_qr_barcode_info <> ''
        ORDER BY files.datetaken
    '''
    data_list, source_path = _run(
        files_found, ('tag_map', 'files'), sql,
        lambda r: (_ms_to_utc(r[0]), _sec_to_utc(r[1]), r[2], r[3], r[4], r[5]))
    data_headers = (
        ('Date Taken', 'datetime'), ('Date Added', 'datetime'), 'QR / Barcode Content (as stored)',
        'File Name', 'File Path', 'Bucket Name')
    return data_headers, data_list, source_path


@artifact_processor
def cmh_user_tags(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    for file_found in _cmh_databases(files_found):
        if not does_table_exist_in_db(file_found, 'usertag'):
            logfunc(f'usertag table not present in {file_found}; '
                    'this CMH schema version is not covered for user tags')
            continue
        # The older generation of this table carries neither the file link nor a
        # timestamp, so both are selected only where the columns exist.
        has_link = does_column_exist_in_db(file_found, 'usertag', 'fk_sec_media_id')
        has_time = does_column_exist_in_db(file_found, 'usertag', 'timestamp')
        time_expr = 'usertag.timestamp' if has_time else 'NULL'
        if has_link:
            sql = f'''
                SELECT {time_expr}, usertag.user_tag_data, files.datetaken,
                       files.title, files._data
                FROM usertag
                LEFT JOIN files ON files._id = usertag.fk_sec_media_id
            '''
        else:
            sql = f'''
                SELECT {time_expr}, usertag.user_tag_data, NULL, NULL, NULL
                FROM usertag
            '''
        rows = _query(file_found, sql)
        if rows:
            sources.append(file_found)
        for row in rows:
            data_list.append((_ms_to_utc(row[0]), row[1], _ms_to_utc(row[2]), row[3], row[4]))

    data_headers = (
        ('Timestamp', 'datetime'), 'Tag Value', ('Date Taken', 'datetime'),
        'File Name', 'File Path')
    return data_headers, data_list, ', '.join(sources)
