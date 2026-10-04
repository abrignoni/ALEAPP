__artifacts_v2__ = {
    "camscanner_documents": {
        "name": "CamScanner Documents",
        "description": "Documents held by CamScanner, with their titles and times",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "CamScanner",
        "sample_data": {
            "emu_a15_oss_v12": "CamScanner 7.24.5 | 1 rows",
        },
        "notes": "One row per row of the documents table in "
                 "com.intsig.camscanner/databases/documents.db. Created, Modified and Last "
                 "Accessed are Unix milliseconds and are reported as UTC. Previous Titles is read "
                 "from the row's own history_titles column, a JSON array of titles; the current "
                 "title is also in that array and is listed there as the app stores it. On the "
                 "tested device a document was created and then renamed, and both names are "
                 "present. Created From is the doc_create_from column, reported as stored; the "
                 "tested document, which was made by importing images, reads import_pic_cs_home, "
                 "and the value a camera scan writes was not observed. Tags lists the title value "
                 "of each element of the latent_tag column, a JSON array. The other keys of each "
                 "element are not reported, and what produces its labels was not established. "
                 "Password "
                 "Set and PDF Password Set report only whether those columns hold a value; no "
                 "password is printed. Neither was set here. Author is the create_author column as "
                 "stored; on the tested row it named the app and its version. A row is "
                 "evidence the document existed in the app, not that anyone opened or sent it.",
        "paths": ('*/com.intsig.camscanner/databases/documents.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "camscanner_pages": {
        "name": "CamScanner Pages",
        "description": "Individual pages of CamScanner documents, with the page image",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "CamScanner",
        "sample_data": {
            "emu_a15_oss_v12": "CamScanner 7.24.5 | 13 rows",
        },
        "notes": "One row per row of the images table in "
                 "com.intsig.camscanner/databases/documents.db, joined to the document it belongs "
                 "to through the images.document_id column, which is the link the database itself "
                 "records. Created and Last Modified are Unix milliseconds and are reported as "
                 "UTC. The page image is shown inline. It is resolved from the row's own _data "
                 "column, which holds the full path the app wrote, so the image is looked up by "
                 "that recorded path; when only one matched file carries the file name, it is taken "
                 "by name without the path being compared. That path is written as the device sees "
                 "it, under /storage/emulated, and is respelled to the data/media form an "
                 "extraction holds before it is looked up. Three paths are reported per page: "
                 "Processed Path is the _data column and is the path rendered, Original Path is the "
                 "raw_data column and Thumbnail Path is the thumb_data column. On the tested device "
                 "the three pointed under .images, .originals and .afterOCRs. What the app does to "
                 "produce each file was not established, and the three header names are this "
                 "parser's reading of the column and folder names. OCR Text, OCR Paragraphs and "
                 "Note were empty on every row of the tested image, since no OCR was run there and "
                 "no note typed; they are the ocr_string, ocr_paragraph and note columns, and what "
                 "they hold when filled was not observed. Document Title and Document ID each held "
                 "one value across the table, because the tested device had a single document of "
                 "thirteen pages; a device with more than one document was not tested. Enhance Mode "
                 "and Image Border are reported as stored, because no source for their values was "
                 "found. A row is evidence the page was in the document, not that "
                 "anyone read it.",
        "paths": ('*/com.intsig.camscanner/databases/documents.db*',
                  '*/com.intsig.camscanner/files/CamScanner/.images/*.jpg'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
}

import json
import re

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/documents.db'

# CamScanner records a page's path as the device sees it, under /storage/emulated/<user>.
# An extraction carries the same bytes under data/media/<user>, so the recorded path has to
# be respelled before it will resolve. It cannot simply be reduced to a file name: the app
# keeps the processed page, the original and the thumbnail under one name in three
# directories, so a name on its own is ambiguous three ways and matches none of them.
SHARED_STORAGE = re.compile(r'^/(?:storage/emulated|sdcard)/?(\d*)/')


def _extraction_path(recorded):
    """Respell a recorded /storage/emulated/<user> path the way an extraction holds it."""
    if not recorded:
        return ''
    text = str(recorded).replace('\\', '/')
    match = SHARED_STORAGE.match(text)
    if not match:
        return text
    user = match.group(1) or '0'
    return f'data/media/{user}/' + text[match.end():]


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value <= 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _titles(raw):
    """history_titles is a JSON array of the names the document has carried."""
    if not raw:
        return ''
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return str(raw)
    if isinstance(parsed, list):
        return ', '.join(str(item) for item in parsed if item)
    return str(raw)


def _tags(raw):
    """latent_tag is a JSON array of {tag_type, title} the app derives from the content."""
    if not raw:
        return ''
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return str(raw)
    if isinstance(parsed, list):
        names = [str(item.get('title')) for item in parsed
                 if isinstance(item, dict) and item.get('title')]
        return ', '.join(names)
    return str(raw)


@artifact_processor
def camscanner_documents(context):
    query = '''SELECT created, modified, access_time, title, history_titles, pages,
                      doc_create_from, latent_tag, create_author, password,
                      password_pdf, sync_doc_id, _id
               FROM documents
               ORDER BY created DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _ms(r[1]), _ms(r[2]), r[3] or '', _titles(r[4]), r[5],
                r[6] or '', _tags(r[7]), r[8] or '',
                'Yes' if r[9] else 'No', 'Yes' if r[10] else 'No',
                r[11] or '', r[12], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'),
        ('Last Accessed', 'datetime'), 'Title', 'Previous Titles', 'Pages',
        'Created From', 'Tags', 'Author', 'Password Set', 'PDF Password Set',
        'Sync Document ID', 'Document ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def camscanner_pages(context):
    query = '''SELECT i.created_time, i.last_modified, d.title, i.page_num, i._data,
                      i.raw_data, i.thumb_data, i.ocr_string, i.ocr_paragraph, i.note,
                      i.enhance_mode, i.image_border, i.sync_image_id, i.document_id
               FROM images i
               LEFT JOIN documents d ON d._id = i.document_id
               ORDER BY i.document_id, i.page_num'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            title = r[2] or ''
            page = r[3]
            resolved = _extraction_path(r[4])
            media = check_in_media(resolved, f'{title} page {page}') if resolved else None
            data_list.append((
                _ms(r[0]), _ms(r[1]), title, page, media or '',
                r[4] or '', r[5] or '', r[6] or '',
                r[7] or '', r[8] or '', r[9] or '',
                r[10], r[11] or '', r[12] or '', r[13],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Last Modified', 'datetime'), 'Document Title',
        'Page', ('Page Image', 'media'), 'Processed Path', 'Original Path',
        'Thumbnail Path', 'OCR Text', 'OCR Paragraphs', 'Note',
        'Enhance Mode (as stored)', 'Image Border (as stored)', 'Image ID',
        'Document ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
