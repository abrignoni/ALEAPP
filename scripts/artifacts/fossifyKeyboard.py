__artifacts_v2__ = {
    "fossify_keyboard_clips": {
        "name": "Fossify Keyboard - Clipboard Items",
        "description": "Parses saved clipboard items from the Fossify Keyboard Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Fossify Keyboard",
        "sample_data": {
            "emu_a15_oss_v4": "Fossify Keyboard 1.9.1 | 1 rows",
        },
        "notes": "One row per entry in the clips table of databases/clips.db. Fossify Keyboard is a "
                 "keyboard app with a clipboard manager, and this table holds the clips saved into it, "
                 "which are the pinned entries kept for reuse rather than the transient recent "
                 "clipboard. Each row is the saved text (Clip Text), and clip text often carries "
                 "addresses, phone numbers, links, codes or passwords a person copied and chose to "
                 "keep. The table stores only an auto-increment id and the text (Clip.kt at "
                 "FossifyOrg/Keyboard 1a2ecdff4e07826d8673576c82637541abbe5264), so there is no "
                 "timestamp for when a clip was saved and none is reported. Fossify Keyboard is the "
                 "maintained successor to Simple Keyboard (com.simplemobiletools.keyboard); that app's "
                 "clip store was not available to verify here, so the path targets the tested "
                 "org.fossify.keyboard only.",
        "paths": ('*/org.fossify.keyboard/databases/clips.db*',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/clips.db'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


@artifact_processor
def fossify_keyboard_clips(context):
    query = 'SELECT value FROM clips ORDER BY id'
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((r[0] or '', context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Clip Text', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
