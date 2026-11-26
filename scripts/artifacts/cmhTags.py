__artifacts_v2__ = {
    "cmh_scene_tags": {
        "name": "CMH Scene Tags",
        "description": "Labels in Samsung's CMH tag_map table, with each label's "
                       "tag_display_name from the tags table as stored (the tags table's "
                       "separate integer tag_type column is not reported), joined to the file "
                       "each label is recorded against.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2025-05-05",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Rows come from the tag_map join table in cmh.db: each row is one label stored "
                 "against one file, with the label text from the tags table "
                 "and the file path and dates from the files table. Tag Display Name is the "
                 "tags table's own tag_display_name (values such as Scene and SubScene as stored) "
                 "and Tag is its tag_data.\n"
                 "The tag_map and tags tables have no column naming what produced a label. A label records what "
                 "was stored against the file (image or video); it is not a statement that the "
                 "subject was present.\n"
                 "A tag_map row whose fk_file_id has no row in the files table is still "
                 "reported, with the file and date columns empty. This was 54 of 496 rows on "
                 "sharon_a14. Why the file row is absent is not established.\n"
                 "Date Taken and Date Added are the linked file's datetaken and date_added from the files table, not the time the label was recorded; tag_map had no time column in any database examined. datetaken is read as Unix milliseconds and date_added as Unix seconds, reported as UTC. These are the units the companion CMH artifact applies; that the CMH files table uses them was not sourced. Title is files.title as stored.\n"
                 "Scene Score is tag_map.scene_score as stored. It was populated on 2212 of 2222 "
                 "rows on anne_a15 and 469 of 496 rows on sharon_a14. Its scale and meaning are "
                 "not established: values ran from about 0.66 to 1.0 on anne_a15 and from 0.5 to 100 "
                 "on sharon_a14. The column has a schema default of 0.5, so a value of 0.5 may "
                 "be the default. tag_map also holds scene_region and scene_region_ratio, "
                 "populated on some rows. They are not reported here and their meaning is not "
                 "established.\n"
                 "The companion CMH artifact reports the image rows of the files table. Labels "
                 "recorded against video files have no row there.",
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
        "description": "Text stored in the ocr_tag table of Samsung's cmh.db, joined to the "
                       "file each row is recorded against.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2025-05-05",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Rows come from the ocr_tag table in cmh.db, joined to the files table on "
                 "fk_file_id. Recognised Text is the image_ocr_tag value with its 0x1F characters "
                 "shown as ' | '. The stored value contained 0x1F characters on 1,244 of 1,290 "
                 "rows across the nine images that hold ocr_tag rows. Empty pieces between "
                 "them are dropped. What the 0x1F characters delimit is not established. The "
                 "ocr_tag columns read here do not name what produced the text. Apart from "
                 "that replacement the text is not changed. It can be partial or wrong; it is "
                 "not a transcription verified by anything.\nTag "
                 "Added Timestamp is the ocr_tag row's tag_added_date, read as Unix "
                 "milliseconds and reported as UTC; the unit was not sourced. Date Taken "
                 "is the linked file's datetaken, read as Unix milliseconds and reported as UTC, "
                 "the unit the companion CMH artifact applies; that the CMH files table uses it "
                 "was not sourced. Version (as stored) is the ocr_tag row's version column; what "
                 "it versions is not established. Title is files.title as stored.",
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
        "description": "Values held in the scene_qr_barcode_info column of the tag_map table "
                       "in Samsung's cmh.db, joined to the file each one is recorded against.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Rows are the tag_map entries whose scene_qr_barcode_info column is populated, joined to the files table. The value is reported exactly as stored and is not decoded, resolved or requested; a stored URL is text in the database, and its presence records a value held in the scene_qr_barcode_info column against that file; the tag_map table has no column naming what produced the value, and it does not show that anyone opened it.\nThe same content can appear on more than one row where it is stored on several tag_map rows. On anne_a15 each of the 2 values is on 2 rows, for one file under two labels.\nDate Taken and Date Added are the linked file's datetaken and date_added from the files table, not the time the value was recorded; tag_map had no time column in any database examined. datetaken is read as Unix milliseconds and date_added as Unix seconds, reported as UTC. These are the units the companion CMH artifact applies; that the CMH files table uses them was not sourced. Title is files.title as stored.",
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
        "description": "Tags recorded in the Samsung CMH user tag table, with the file each one is linked to where the usertag table carries fk_sec_media_id.",
        "author": "Panagiotis Nakoutis - @4n6equals10, @AlexisBrignoni, Claude",
        "creation_date": "2025-05-05",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Rows come from the usertag table in cmh.db. The table has more than one generation. Newer databases carry fk_sec_media_id and timestamp. fk_sec_media_id is joined to files.sec_media_id, the join cmh.db makes itself in its files_delete_recommendation_view, to give the linked file. On anne_a15 the one row links to a files row this way. timestamp is read as Unix milliseconds and reported as UTC. The unit was not sourced; the one populated row in the corpus holds a 13-digit value. The older generation, seen on Android 10 and Android 11 images, carries neither column. Rows from it would be reported with the tag value alone and no file or time. No older-generation database in the corpus holds a usertag row. That generation links tags to files through tag_map, which this artifact does not follow. Absent columns are read as NULL rather than assumed.\nTag Value is the stored user_tag_data. Title is files.title as stored. This artifact does not report how a row was created. The usertag columns mp_user_tag_id, server_id and dirty (user_tag_type in the older generation) are not reported and their meaning is not established.",
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
                               does_table_exist_in_db, logfunc, open_sqlite_db_readonly, is_sqlite_sidecar)

# The stored OCR value contains 0x1F characters; what they delimit is not established.
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
        if is_sqlite_sidecar(file_found):
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
    return data_list, '\n'.join(sources)


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
        ('Date Taken', 'datetime'), ('Date Added', 'datetime'), 'Tag Display Name', 'Tag',
        'Scene Score (as stored)', 'Title', 'File Path', 'Bucket Name')
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
        # Show the stored 0x1F characters as a readable delimiter.
        text = ' | '.join(part for part in text.split(_OCR_SEPARATOR) if part)
        return (_ms_to_utc(row[0]), _ms_to_utc(row[1]), text, row[3], row[4], row[5], row[6])

    data_list, source_path = _run(files_found, ('ocr_tag', 'files'), sql, build)
    data_headers = (
        ('Tag Added Timestamp', 'datetime'), ('Date Taken', 'datetime'), 'Recognised Text',
        'Version (as stored)', 'Title', 'File Path', 'Bucket Name')
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
        'Title', 'File Path', 'Bucket Name')
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
                LEFT JOIN files ON files.sec_media_id = usertag.fk_sec_media_id
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
        'Title', 'File Path')
    return data_headers, data_list, '\n'.join(sources)
