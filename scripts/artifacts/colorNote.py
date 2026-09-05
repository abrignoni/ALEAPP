__artifacts_v2__ = {
    "colornote_notes": {
        "name": "ColorNote Notes",
        "description": "Notes and checklists held by the ColorNote notepad app",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "ColorNote",
        "sample_data": {
            "emu_a15_oss_v10": "ColorNote 4.8.8 | 6 rows",
        },
        "notes": "One row per row of the notes table in "
                 "com.socialnmobile.dictapps.notepad.color.note/databases/colornote.db. Created, "
                 "Modified, Minor Modified and Reminder are Unix milliseconds and are reported as "
                 "UTC. Minor Modified moves when something other than the text changes, such as "
                 "the colour or the archive state, so a row whose Minor Modified is later than "
                 "its Modified was touched without its text being edited. A checklist keeps its "
                 "items inside the same Note column, one per line, with a ticked item written as "
                 "[V] and an unticked item as [ ]. Note Type, Status, Storage and Reminder Type "
                 "report the stored integer beside the label. Those labels were read from a "
                 "decompiled build of the installed version, ColorNote 4.8.8, and are not "
                 "published source. Four of them are also proven by known data, because the note "
                 "in question was created that way on the tested device: Note Type 16 Checklist, "
                 "Status 16 Trash, Storage 16 Archived and Reminder Type 32 Time alarm. Status 32 "
                 "and 256 and Reminder Type 16 and 128 appear in the app's own queries and were "
                 "not exercised here. A note pinned to the status bar is written with a "
                 "reminder_date of -1 rather than a time, so Reminder is reported blank on that "
                 "row and Reminder Type is what identifies it. Encrypted, Latitude and Longitude "
                 "held no value on any row "
                 "of the tested image. Encrypted marks a password-locked note, whose Title stays "
                 "readable in this table while its Note text does not. Latitude and Longitude are "
                 "filled by a location reminder rather than by anything the note itself holds. "
                 "Neither a locked note nor a location reminder was created, so all three are "
                 "reported as checked absences and not as evidence the features are missing. The "
                 "folder_id, tags and importance columns are left unparsed: each was constant on "
                 "the tested image and none carries content the note does not already show. A row "
                 "is evidence the note was in the store, not that anyone read it.",
        "paths": ('*/com.socialnmobile.dictapps.notepad.color.note/databases/colornote.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/colornote.db'

# Read from a decompiled build of ColorNote 4.8.8 with jadx 1.5.6, class
# com.socialnmobile.colornote.data.i. active_state 0 is the ordinary note list (i.java:297),
# 16 is what the trash listing selects (i.java:360), and 32 and 256 appear in the app's own
# sync and template queries (i.java:257, i.java:395).
NOTE_STATES = {0: 'Active', 16: 'Trash', 32: 'Deleted', 256: 'Template'}

# space 0 is the ordinary list; the archive helper writes 16 (i.java:592).
NOTE_SPACES = {0: 'Normal', 16: 'Archived'}

# type 0 is a text note and 16 a checklist (i.java:454 selects checklists with type = 16).
NOTE_TYPES = {0: 'Text', 16: 'Checklist'}

# reminder_type write sites in i.java lines 40 to 100: 0 clears the reminder, 16 stores a
# date normalised to a day boundary, 32 stores a wall-clock alarm, and 128 pins the note to
# the status bar.
REMINDER_TYPES = {0: 'None', 16: 'Date', 32: 'Time alarm', 128: 'Pinned to status bar'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value < 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _label(value, table):
    if value is None:
        return ''
    if value in table:
        return f'{table[value]} ({value})'
    return f'Unknown ({value})'


def _coord(value):
    if value in (None, '', 0):
        return ''
    return value


@artifact_processor
def colornote_notes(context):
    query = '''SELECT created_date, modified_date, minor_modified_date, reminder_date,
                      title, note, type, active_state, space, reminder_type,
                      color_index, encrypted, latitude, longitude, uuid
               FROM notes
               ORDER BY created_date'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _ms(r[1]), _ms(r[2]), _ms(r[3]),
                r[4] or '', r[5] or '',
                _label(r[6], NOTE_TYPES), _label(r[7], NOTE_STATES),
                _label(r[8], NOTE_SPACES), _label(r[9], REMINDER_TYPES),
                r[10] if r[10] is not None else '',
                'Yes' if r[11] else 'No',
                _coord(r[12]), _coord(r[13]), r[14] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'),
        ('Minor Modified', 'datetime'), ('Reminder', 'datetime'),
        'Title', 'Note', 'Note Type', 'Status', 'Storage', 'Reminder Type',
        'Colour Index', 'Encrypted', 'Latitude', 'Longitude', 'UUID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
