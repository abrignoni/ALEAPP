__artifacts_v2__ = {
    "orgzly_notes": {
        "name": "Orgzly - Notes",
        "description": "Parses notes and to-dos from the Orgzly Revived Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Orgzly",
        "notes": "One row per entry in the notes table of databases/orgzly.db, joined to its "
                 "notebook and to the scheduled and deadline timestamps the note carries. Orgzly "
                 "Revived is an outliner for Org-mode files, so a note is a heading a person "
                 "wrote, optionally with a to-do State, a Priority, Tags and a Content body. "
                 "Created is Unix milliseconds reported as UTC. It is the column that separates "
                 "what a person wrote from what the app shipped: on the tested device 34 of the "
                 "35 notes were the sample notebook the app installs on first run and carried no "
                 "Created value at all, while the one note added by hand carried it. A blank "
                 "Created therefore suggests a note that arrived with a file or with the app "
                 "rather than one typed on the device, and the Notebook artifact records where "
                 "each notebook came from. "
                 "State is the to-do keyword as stored, TODO, NEXT and DONE on the tested device, "
                 "and is blank on a plain note; the keyword set is configurable, so any value is "
                 "reported as stored. Scheduled and Deadline are the Org timestamps the note "
                 "carries, given both as the raw Org string (which preserves any repeater such as "
                 "'.+2d') and as a UTC time. Level and Parent Note ID describe the note's place "
                 "in the outline, so a reply or sub-task can be tied to its parent. "
                 "The note_ancestors table holds the same tree as a closure table and is not "
                 "reported separately. The searches table held four saved searches on the tested "
                 "device, all of which are the app's shipped defaults, so it is not parsed. "
                 "Title leads this table rather than Created because a note often arrives inside "
                 "an Org file rather than being typed on the device, and only a note the app "
                 "itself created carries a Created value: it was filled on 1 of the 35 tested "
                 "rows, the one note added by hand. Sorting by Created would therefore hide most "
                 "of the notebook.",
        "paths": ('*/com.orgzlyrevived/databases/orgzly.db*', '*/com.orgzly/databases/orgzly.db*'),
        "output_types": "standard",
        "artifact_icon": "check-square",
    },
    "orgzly_notebooks": {
        "name": "Orgzly - Notebooks",
        "description": "Parses notebooks and their sync state from the Orgzly Revived Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Orgzly",
        "notes": "One row per entry in the books table of databases/orgzly.db. A notebook is one "
                 "Org file the app holds, and this artifact records where it came from. Last "
                 "Action Message is the useful column: the app writes a sentence describing the "
                 "last thing that happened to the notebook, and on the tested device it read "
                 "'Loaded from resource Getting Started with Orgzly', which identifies that "
                 "notebook as the sample the app installs rather than a file a person created or "
                 "synced. A notebook loaded from a linked repository names that source instead, "
                 "which is what ties the notes to a synced location. "
                 "Modified is the notebook's mtime and Last Action is the time of that recorded "
                 "action, both Unix milliseconds reported as UTC. Sync Status and Is Modified "
                 "describe whether the app considers the local copy ahead of its remote. Preface "
                 "is the text above the first heading and File Tags are tags applied to the whole "
                 "file. Encoding columns are reported as stored. "
                 "Is Deleted marks a notebook the app has removed but still holds a row for, so a "
                 "row flagged there is a notebook that was deleted rather than one currently in "
                 "the app. Title is the #+TITLE property from inside the Org file and is "
                 "separate from Name, which is the notebook name the app shows; it was empty on "
                 "the tested notebook because that file sets no such property, and Name carried "
                 "the name instead.",
        "paths": ('*/com.orgzlyrevived/databases/orgzly.db*', '*/com.orgzly/databases/orgzly.db*'),
        "output_types": "standard",
        "artifact_icon": "book",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/orgzly.db'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


@artifact_processor
def orgzly_notes(context):
    query = '''SELECT n.created_at, n.title, n.state, n.tags, n.priority, n.content,
                      b.name,
                      sr.string, st.timestamp,
                      dr.string, dt.timestamp,
                      n.level, n.parent_id, n.id, n.book_id
               FROM notes n
               LEFT JOIN books b ON b.id = n.book_id
               LEFT JOIN org_ranges sr ON sr.id = n.scheduled_range_id
               LEFT JOIN org_timestamps st ON st.id = sr.start_timestamp_id
               LEFT JOIN org_ranges dr ON dr.id = n.deadline_range_id
               LEFT JOIN org_timestamps dt ON dt.id = dr.start_timestamp_id
               ORDER BY n.book_id, n.lft'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                r[1] or '', _ms(r[0]), r[2] or '', r[3] or '', r[4] or '',
                r[6] or '', _ms(r[8]), r[7] or '', _ms(r[10]), r[9] or '',
                r[5] or '', r[11], r[12] or '', r[13],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Title', ('Created', 'datetime'), 'State (as stored)', 'Tags', 'Priority',
        'Notebook', ('Scheduled', 'datetime'), 'Scheduled (Org string)',
        ('Deadline', 'datetime'), 'Deadline (Org string)', 'Content', 'Level',
        'Parent Note ID', 'Note ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def orgzly_notebooks(context):
    query = '''SELECT mtime, last_action_timestamp, name, title, last_action_type,
                      last_action_message, sync_status, is_modified, is_deleted,
                      preface, filetags, used_encoding, detected_encoding, id
               FROM books ORDER BY id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _ms(r[1]), r[2] or '', r[3] or '', r[4] or '', r[5] or '',
                r[6] or '', _yesno(r[7]), _yesno(r[8]), r[9] or '', r[10] or '',
                r[11] or '', r[12] or '', r[13],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Modified', 'datetime'), ('Last Action', 'datetime'), 'Name', 'Title',
        'Last Action Type (as stored)', 'Last Action Message', 'Sync Status (as stored)',
        'Is Modified', 'Is Deleted', 'Preface', 'File Tags', 'Used Encoding',
        'Detected Encoding', 'Notebook ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
