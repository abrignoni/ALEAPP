__artifacts_v2__ = {
    "fossify_notes": {
        "name": "Fossify Notes",
        "description": "Parses notes stored by the Fossify Notes Android app and its Simple Mobile Tools predecessor.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Fossify Notes",
        "notes": "One row per entry in the notes table of databases/notes.db. Each row is a note the app "
                 "holds, with its Title, the note content in the Note column as stored, the Type, the "
                 "Path, and the note-lock state in Protection. Type is decoded from the app's NoteType "
                 "enum, 0 a plain text note and 1 a checklist; for a checklist the Note column holds the "
                 "app's serialised list of items rather than plain text (NoteType.kt at FossifyOrg/Notes "
                 "786fc41f68d1aed8d82144a6de0127ed4dbe8b61). Path is the file the note is backed by when "
                 "the note is linked to a file on the device, and is empty for a note kept only in the "
                 "database. Protection is decoded from protection_type using the shared Fossify Commons "
                 "constants, -1 none, 0 pattern, 1 PIN, 2 fingerprint (Constants.kt at FossifyOrg/Commons "
                 "92aef4c0ee9d0134f9c44440c96a7b1c733767e0); a value other than none means the note is "
                 "locked in the app. The note's protection_hash column stores the hash of that lock and "
                 "is never read or reported here. The notes table carries no created or modified "
                 "timestamp, so none is reported. The widgets table in the same database holds "
                 "home-screen widget settings and is not evidential. The app is the maintained successor "
                 "to Simple Mobile Tools Notes and uses the identical schema, so the paths cover both "
                 "org.fossify.notes (tested) and com.simplemobiletools.notes.pro (same schema, from the "
                 "shared source, not exercised here).",
        "paths": (
            '*/org.fossify.notes/databases/notes.db*',
            '*/com.simplemobiletools.notes.pro/databases/notes.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | org.fossify.notes vc 13 | 1 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/notes.db'

# NoteType.kt at FossifyOrg/Notes 786fc41f68d1aed8d82144a6de0127ed4dbe8b61.
NOTE_TYPES = {0: 'Text', 1: 'Checklist'}
# Constants.kt at FossifyOrg/Commons 92aef4c0ee9d0134f9c44440c96a7b1c733767e0.
PROTECTION = {-1: 'None', 0: 'Pattern', 1: 'PIN', 2: 'Fingerprint'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _lookup(table, value):
    if value in table:
        return table[value]
    return f'{value} (as stored)'


@artifact_processor
def fossify_notes(context):
    query = '''SELECT title, value, type, path, protection_type
               FROM notes ORDER BY id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((
                r[0] or '', r[1] or '', _lookup(NOTE_TYPES, r[2]), r[3] or '',
                _lookup(PROTECTION, r[4]), context.get_relative_path(db_path),
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = ('Title', 'Note', 'Type', 'Path', 'Protection', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
