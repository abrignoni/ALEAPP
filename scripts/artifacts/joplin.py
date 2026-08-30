__artifacts_v2__ = {
    "joplin_notes": {
        "name": "Joplin - Notes",
        "description": "Parses the notes and to-dos stored by the Joplin Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Joplin",
        "notes": "One row per note in the notes table of databases/joplin.sqlite. Each row carries the "
                 "note's title and body, the notebook it lives in resolved from the parent folder, its "
                 "created and updated times, and its geolocation. The times are Unix milliseconds and "
                 "were UTC on the tested device, so they are reported as UTC. Latitude and Longitude "
                 "hold the position Joplin recorded for the note when the user enabled saving "
                 "geolocation; they are 0 when it was not recorded. Altitude completes the recorded position and is 0 "
                 "when no altitude was captured, as on the tested notes. A note can be a to-do, in which "
                 "case Is To-Do is set and the To-Do Due and To-Do Completed times are populated when "
                 "present. Deleted holds the time a note was moved to the trash, so a value there means "
                 "the note was deleted and is recoverable from this table. Markup is decoded from the "
                 "app's own MarkupLanguage values, 1 Markdown and 2 HTML "
                 "(packages/renderer/types.ts at laurent22/joplin 3f23202e); any other value is "
                 "reported as stored. Joplin can end to end encrypt notes when synchronisation "
                 "encryption is enabled, and a note whose Encryption Applied flag is set has its body "
                 "held in an encrypted field that is not readable here; the Body column reports that it "
                 "is encrypted for those rows. Source URL and Author are reported where the note "
                 "carries them. Older versions of a note are kept in the revisions table, which is not "
                 "parsed here.",
        "paths": ('*/net.cozic.joplin/databases/joplin.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "notes",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | net.cozic.joplin vc 2097810 | 6 rows",
        },
    },
    "joplin_notebooks": {
        "name": "Joplin - Notebooks",
        "description": "Parses the notebooks (folders) created in the Joplin Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Joplin",
        "notes": "One row per notebook in the folders table of databases/joplin.sqlite. Notebooks are "
                 "the containers the user organises notes into, and can be nested, so the Parent "
                 "Notebook column resolves the parent id to its title where the notebook sits inside "
                 "another. Created and Updated are Unix milliseconds reported as UTC. Deleted holds the "
                 "time a notebook was moved to the trash when set. The Note Count is the number of "
                 "notes whose parent is this notebook.",
        "paths": ('*/net.cozic.joplin/databases/joplin.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "folders",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | net.cozic.joplin vc 2097810 | 1 rows",
        },
    },
    "joplin_resources": {
        "name": "Joplin - Attachments",
        "description": "Parses the attachments (resources) stored by the Joplin Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Joplin",
        "notes": "One row per resource in the resources table of databases/joplin.sqlite. A resource is "
                 "a file the user attached to a note, an image, a document or a recording. Each row "
                 "gives the resource's title, original file name, mime type, file extension and size, "
                 "and its created and updated times as UTC. OCR Text holds any text Joplin extracted "
                 "from the attachment by optical character recognition, which can carry the readable "
                 "text of an image; it is reported as stored. The attachment bytes are stored on disk "
                 "under the app's files directory named by the resource id and are not surfaced here. A "
                 "resource whose Encryption Applied flag is set is end to end encrypted.",
        "paths": ('*/net.cozic.joplin/databases/joplin.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | net.cozic.joplin vc 2097810 | 3 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

# packages/renderer/types.ts at laurent22/joplin 3f23202e.
MARKUP_LANGUAGES = {1: 'Markdown', 2: 'HTML', 3: 'Any'}

DB_SUFFIX = 'databases/joplin.sqlite'


def _db_files(context):
    out = []
    for file_found in unique_files(context):
        file_found = str(file_found).replace('\\', '/')
        if file_found.endswith(DB_SUFFIX):
            out.append(file_found)
    return out


def _ms(value):
    """A Unix millisecond value as a UTC datetime, or '' when zero or absent."""
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _markup(value):
    if value in MARKUP_LANGUAGES:
        return MARKUP_LANGUAGES[value]
    return f'{value} (as stored)' if value else ''


@artifact_processor
def joplin_notes(context):
    query = '''SELECT n.created_time, n.updated_time, n.title, n.body, f.title,
                      n.latitude, n.longitude, n.altitude, n.is_todo, n.todo_due,
                      n.todo_completed, n.deleted_time, n.source_url, n.author,
                      n.markup_language, n.encryption_applied, n.id
               FROM notes n LEFT JOIN folders f ON f.id = n.parent_id
               ORDER BY n.updated_time DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            encrypted = r[15] == 1
            data_list.append((
                _ms(r[0]), _ms(r[1]), r[2] or '',
                '(encrypted)' if encrypted else (r[3] or ''),
                r[4] or '', r[5], r[6], r[7],
                'Yes' if r[8] else '',
                _ms(r[9]), _ms(r[10]), _ms(r[11]),
                r[12] or '', r[13] or '', _markup(r[14]),
                'Yes' if encrypted else '', r[16] or '',
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Updated', 'datetime'), 'Title', 'Body', 'Notebook',
        'Latitude', 'Longitude', 'Altitude', 'Is To-Do',
        ('To-Do Due', 'datetime'), ('To-Do Completed', 'datetime'), ('Deleted', 'datetime'),
        'Source URL', 'Author', 'Markup', 'Encryption Applied', 'Note ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def joplin_notebooks(context):
    query = '''SELECT f.created_time, f.updated_time, f.title, p.title, f.deleted_time,
                      (SELECT count(*) FROM notes n WHERE n.parent_id = f.id), f.id
               FROM folders f LEFT JOIN folders p ON p.id = f.parent_id
               ORDER BY f.title'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((_ms(r[0]), _ms(r[1]), r[2] or '', r[3] or '',
                              _ms(r[4]), r[5], r[6] or ''))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (('Created', 'datetime'), ('Updated', 'datetime'), 'Notebook',
                    'Parent Notebook', ('Deleted', 'datetime'), 'Note Count', 'Notebook ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def joplin_resources(context):
    query = '''SELECT created_time, updated_time, title, filename, mime, file_extension,
                      size, ocr_text, encryption_applied, id
               FROM resources ORDER BY created_time DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((_ms(r[0]), _ms(r[1]), r[2] or '', r[3] or '', r[4] or '',
                              r[5] or '', r[6], r[7] or '',
                              'Yes' if r[8] == 1 else '', r[9] or ''))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (('Created', 'datetime'), ('Updated', 'datetime'), 'Title', 'File Name',
                    'Mime Type', 'File Extension', 'Size', 'OCR Text', 'Encryption Applied',
                    'Resource ID')
    return data_headers, data_list, '\n'.join(sources)
