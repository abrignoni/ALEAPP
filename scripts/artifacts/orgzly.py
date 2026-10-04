__artifacts_v2__ = {
    "orgzly_notes": {
        "name": "Orgzly - Notes",
        "description": "Parses notes and to-dos from the Orgzly Revived Android app "
                       "(com.orgzlyrevived). The com.orgzly package is also matched "
                       "and was not tested.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Orgzly",
        "sample_data": {
            "emu_a15_oss_v7": "Orgzly Revived 1.23.0 | 35 rows, of which 34 are the notebook the app installs on first run",
        },
        "notes": "One row per entry in the notes table of databases/orgzly.db, joined to its "
                 "notebook and to the scheduled and deadline timestamps the note carries. Orgzly "
                 "Revived is an outliner for Org-mode files, so a note is an Org heading, "
                 "optionally with a to-do State, a Priority, Tags and a Content body. Created is "
                 "Unix milliseconds reported as UTC. On the tested device 34 of the 35 "
                 "notes were the sample notebook the app installs on first run and carried no "
                 "Created value at all, while the one note added by hand carried it. On the "
                 "tested device a blank Created coincided with the shipped notes and a filled "
                 "one with the note added by hand; what else can leave it blank was not "
                 "established. The Notebook artifact records where each notebook came from. "
                 "State is the to-do keyword as stored, TODO, NEXT and DONE on the tested "
                 "device, and is blank on a plain note; the keyword set is configurable, so any "
                 "value is reported as stored. Scheduled (Org string) and Deadline (Org string) are "
                 "the Org timestamps the note carries, as stored, which preserves any repeater "
                 "such as '.+2d'. An Org timestamp is a date, or a date and time, with no time "
                 "zone. Scheduled Timestamp and Deadline Timestamp are the timestamp column of "
                 "org_timestamps, a millisecond value reported as the stored number and not "
                 "converted to a date. The app fills it from a calendar built from the Org "
                 "string: OrgTimestampMapper.kt line 33 "
                 "(https://github.com/orgzly-revived/orgzly-android-revived/blob/"
                 "2b56fe4c1a0c9426a1bb1313b4c757a8e66a48d0/app/src/main/java/com/orgzly/android/"
                 "db/mappers/OrgTimestampMapper.kt#L33, tag v1.23.0) takes the calendar's time "
                 "in milliseconds, and org-java 1.3.6, the version that tag builds with, creates "
                 "that calendar with Calendar.getInstance() "
                 "(https://github.com/orgzly-revived/org-java/blob/"
                 "71960c30ccd0e1a0ec24cee9e7530d6338407097/src/main/java/com/orgzly/org/datetime/"
                 "OrgDateTime.java#L234), which uses the default time zone of the device at the "
                 "moment the row was written. The database does not record that zone. On "
                 "emu_a15_oss_v7 the three stored values (two scheduled, one deadline) each read "
                 "as UTC came out 5 hours after the date and time in the Org string, and the two "
                 "date-only entries read 05:00. On a device ahead of UTC a date-only entry read "
                 "as UTC would fall on the previous day; that case was not on the tested device. "
                 "Read the date from the Org string. Level and Parent "
                 "Note ID describe the "
                 "note's place in the outline, so a reply or sub-task can be tied to its parent. "
                 "The note_ancestors table holds the same tree as a closure table and is not "
                 "reported separately. The searches table held four saved searches on the tested "
                 "device, all of which are the app's shipped defaults, so it is not parsed. "
                 "Title leads this table rather than Created because a note can carry no Created "
                 "value, and Created was filled on 1 "
                 "of the 35 tested "
                 "rows, the one note added by hand. Sorting by Created would therefore hide most "
                 "of the notebook.",
        "paths": ('*/com.orgzlyrevived/databases/orgzly.db*', '*/com.orgzly/databases/orgzly.db*'),
        "output_types": "standard",
        "artifact_icon": "check-square",
    },
    "orgzly_notebooks": {
        "name": "Orgzly - Notebooks",
        "description": "Parses notebooks and their sync state from the Orgzly Revived Android app.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Orgzly",
        "sample_data": {
            "emu_a15_oss_v7": "Orgzly Revived 1.23.0 | 1 rows",
        },
        "notes": "One row per entry in the books table of databases/orgzly.db. A notebook is one "
                 "Org file the app holds, and this artifact records where it came from. Last "
                 "Action Message is the useful column: the app writes a sentence describing the "
                 "last thing that happened to the notebook. On the tested device it read "
                 "'Loaded from resource Getting Started with Orgzly', and that notebook was the "
                 "one the app installed on first run. A notebook loaded from a linked repository "
                 "was not exercised on the "
                 "tested device. Modified is the notebook's mtime and Last Action is the time of "
                 "that recorded action, both Unix milliseconds reported as UTC. Sync Status is "
                 "reported as stored. Is Modified and Is Deleted show a stored 1 as Yes and 0 as "
                 "No; any other stored value is shown blank. Preface is the text above the first "
                 "heading and File Tags are tags applied to the whole file. Encoding columns are "
                 "reported as stored. What the app sets Is Deleted for "
                 "was not established. Title is the #+TITLE property from inside the Org file "
                 "and is "
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


def _stored(value):
    return '' if value is None else str(value)


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
                r[6] or '', r[7] or '', _stored(r[8]), r[9] or '', _stored(r[10]),
                r[5] or '', r[11], r[12] or '', r[13],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Title', ('Created', 'datetime'), 'State (as stored)', 'Tags', 'Priority',
        'Notebook', 'Scheduled (Org string)', 'Scheduled Timestamp (ms, as stored)',
        'Deadline (Org string)', 'Deadline Timestamp (ms, as stored)', 'Content', 'Level',
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
