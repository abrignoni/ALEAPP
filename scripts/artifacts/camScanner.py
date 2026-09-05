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
                 "from the row's own history_titles column, a JSON array the app appends to when a "
                 "document is renamed, so it shows what the document used to be called; the "
                 "current title is also in that array and is listed there as the app stores it. On "
                 "the tested device a document was created and then renamed, and both names are "
                 "present. Created From is the doc_create_from column and records how the document "
                 "came into being, which separates a scan taken with the camera from images "
                 "imported out of the gallery; the tested document reads import_pic_cs_home, "
                 "because it was made by importing images. Tags is the latent_tag column, a JSON "
                 "array of labels the app derives from the content itself rather than from "
                 "anything a user typed, so it is the app's classification and not a user's. "
                 "Password Set and PDF Password Set report only whether those columns hold a "
                 "value; no password is printed. Neither was set here. Author is the app's own "
                 "create_author string and carries the writing app and its version. A row is "
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
                 "column, which holds the full path the app wrote, so the image is matched by a "
                 "recorded path and not by correlating a name, a size or a time. That path is "
                 "written as the device sees it, under /storage/emulated, and is respelled to the "
                 "data/media form an extraction holds before it is looked up. The respelling is "
                 "what makes the match exact: the app keeps the processed page, the original and "
                 "the thumbnail under one file name in three directories, so the name alone is "
                 "ambiguous three ways. The app keeps up "
                 "to three copies of a page and all three paths are reported: _data is the "
                 "processed page and is the one rendered, Original Path is the untouched import or "
                 "capture under .originals, and Thumbnail Path is the smaller copy under "
                 ".afterOCRs. The originals matter because the processed page can be cropped, "
                 "rotated or enhanced away from what the camera or the imported file actually "
                 "held. OCR Text, OCR Paragraphs and Note were empty on every row of the tested "
                 "image, since no OCR was run there and no note typed; they are the columns that "
                 "carry recognised text and a per-page comment when either has been produced. "
                 "Document Title and Document ID each held one value across the table, because "
                 "the tested device had a single document of thirteen pages; both vary as soon as "
                 "a second document exists and are what group the pages. "
                 "Enhance Mode and Image Border are reported as stored, being undocumented in "
                 "anything published. A row is evidence the page was in the document, not that "
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
