__artifacts_v2__ = {
    "tasks_org_tasks": {
        "name": "Tasks.org - Tasks",
        "description": "Parses tasks from the Tasks.org (org.tasks) Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Tasks.org",
        "notes": "One row per entry in the tasks table of databases/database, the app's Room "
                 "database. Tasks.org is an open source to-do and task manager. Each row is a "
                 "task, with its Title, Description (the notes field), Priority, the List it "
                 "belongs to, and timestamps. Priority is decoded from the app's Priority "
                 "constants, 0 High, 1 Medium, 2 Low, 3 None (Task.kt at tasks/tasks tag 15.10, "
                 "b4b8c9dfb4864a2fd74ea8e75043b6df86c4aa4b); any other value is reported as "
                 "stored. Created, Modified, Due Date, Start Date, Completed and Deleted are Unix "
                 "milliseconds and are reported as UTC (the tested device was set to "
                 "America/New_York and a due date entered as tomorrow 1 PM local stored as "
                 "1788282001000, which is 17:00:01 UTC, matching 13:00 EDT). Completed and Deleted "
                 "are the completion and soft-delete times; a value of 0 means not completed or "
                 "not deleted and is reported blank. Due Time Set is derived from the app's own "
                 "hasDueTime rule, which flags a due date as carrying a time when its millisecond "
                 "value is not on a whole-minute boundary (dueDate modulo 60000 is greater than "
                 "zero); the tested due date carried a time and this read Yes, and a date-only due "
                 "date would read No with the time component not meaningful. Recurrence is the "
                 "task's repeat rule as an RRULE string. Parent Task ID is the _id of the parent "
                 "task for a subtask and is blank for a top-level task. Time Estimated and Time "
                 "Tracked are seconds from the app's timer feature. On the tested single-task "
                 "device Start Date, Completed, Deleted, Recurrence and Parent Task ID were empty "
                 "because those features were not used. The app keeps a second database at "
                 "databases/tasks.db (a dmfs OpenTasks/CalDAV content-provider store), which was "
                 "present but held no task rows on the tested no-sync device and is not parsed "
                 "here.",
        "paths": ('*/org.tasks/databases/database*',),
        "output_types": "standard",
        "artifact_icon": "check-square",
    },
    "tasks_org_locations": {
        "name": "Tasks.org - Locations",
        "description": "Parses saved places and location reminders from the Tasks.org Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Tasks.org",
        "notes": "One row per entry in the places table of databases/database, left joined to the "
                 "geofences table and, through it, to the task the place is attached to. A place "
                 "is a location added in the app, with a Place Name, Address, Latitude, Longitude, "
                 "and a Radius in metres (the geofence radius, default 250). On the tested device "
                 "an address searched in the app's location picker was stored as 1600 Pennsylvania "
                 "Avenue Northwest at 38.897684, -77.036574 with a 250 m radius. Arrival and "
                 "Departure are the geofence trigger flags from the geofences table, Yes when the "
                 "app is set to remind on arriving at or leaving the place; both were No on the "
                 "tested device (a place was attached to a task but neither trigger was enabled). "
                 "Task and Task ID name the task the place is attached to; a saved place with no "
                 "geofence has these blank. Phone and URL are place fields and were empty on the "
                 "tested device. KML output is produced from the coordinates. A place is a "
                 "location the person added to the app, not a position the device was "
                 "independently measured at.",
        "paths": ('*/org.tasks/databases/database*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "tasks_org_reminders": {
        "name": "Tasks.org - Reminders",
        "description": "Parses task reminders (alarms) from the Tasks.org Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Tasks.org",
        "notes": "One row per entry in the alarms table of databases/database, left joined to its "
                 "task. Each row is a reminder configured for a task. Type is decoded from the "
                 "app's Alarm type constants, 0 Date/time, 1 Relative to start, 2 Relative to due, "
                 "3 Random, 4 Snooze, 5 Geofence enter, 6 Geofence exit (Alarm.kt at tasks/tasks "
                 "tag 15.10, b4b8c9dfb4864a2fd74ea8e75043b6df86c4aa4b); any other value is "
                 "reported as stored. The meaning of the Time value depends on Type, so When is "
                 "derived from both: for Date/time and Snooze the Time is a Unix millisecond epoch "
                 "and is shown as a UTC time; for Relative to start or due it is a millisecond "
                 "offset shown as a duration before or after that anchor (a Relative to due alarm "
                 "with Time 0 is 'at due time'); for the geofence types it names the trigger. "
                 "Repeat Count and Interval (ms) are the app's repeat settings for the reminder. "
                 "Time Raw is the stored Time value. On the tested device setting a due date added "
                 "two Relative to due reminders automatically (one at the due time and one that "
                 "repeats after it), which are the app's default due reminders rather than "
                 "manually configured alarms.",
        "paths": ('*/org.tasks/databases/database*',),
        "output_types": "standard",
        "artifact_icon": "bell",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/database'

# Task.kt Priority at tasks/tasks tag 15.10 (b4b8c9dfb4864a2fd74ea8e75043b6df86c4aa4b).
PRIORITIES = {0: 'High', 1: 'Medium', 2: 'Low', 3: 'None'}
# Alarm.kt type constants at the same commit.
ALARM_TYPES = {0: 'Date/time', 1: 'Relative to start', 2: 'Relative to due',
               3: 'Random', 4: 'Snooze', 5: 'Geofence enter', 6: 'Geofence exit'}


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


def _lookup(table, value):
    if value in table:
        return table[value]
    if value is None or value == '':
        return ''
    return f'{value} (as stored)'


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


def _has_due_time(value):
    # Task.hasDueTime: a due date carries a time when dueDate % 60000 > 0.
    try:
        v = int(value)
    except (TypeError, ValueError):
        return ''
    if v <= 0:
        return ''
    return 'Yes' if v % 60000 > 0 else 'No'


def _duration(ms):
    # Express a millisecond offset as a signed day/hour/minute string.
    try:
        v = int(ms)
    except (TypeError, ValueError):
        return str(ms)
    if v == 0:
        return '0'
    sign = '-' if v < 0 else ''
    total = abs(v) // 1000
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f'{days}d')
    if hours:
        parts.append(f'{hours}h')
    if mins:
        parts.append(f'{mins}m')
    if secs:
        parts.append(f'{secs}s')
    return sign + ' '.join(parts)


def _alarm_when(alarm_type, time_value):
    try:
        t = int(time_value)
    except (TypeError, ValueError):
        t = 0
    if alarm_type in (0, 4):  # Date/time, Snooze -> absolute epoch
        return _ms(time_value)
    if alarm_type == 1:  # relative to start
        return 'at start' if t == 0 else f'{_duration(t)} from start'
    if alarm_type == 2:  # relative to due
        return 'at due time' if t == 0 else f'{_duration(t)} from due'
    if alarm_type == 3:  # random
        return f'random within {_duration(t)}'
    if alarm_type == 5:
        return 'on arrival at location'
    if alarm_type == 6:
        return 'on departure from location'
    return ''


@artifact_processor
def tasks_org_tasks(context):
    query = '''SELECT t._id, t.title, t.notes, t.importance, t.created, t.modified,
                      t.dueDate, t.hideUntil, t.completed, t.deleted, t.recurrence,
                      t.parent, t.estimatedSeconds, t.elapsedSeconds, cl.cdl_name
               FROM tasks t
               LEFT JOIN caldav_tasks ct ON ct.cd_task = t._id
               LEFT JOIN caldav_lists cl ON cl.cdl_uuid = ct.cd_calendar
               ORDER BY t._id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[4]), _ms(r[5]), r[1] or '', r[2] or '',
                _lookup(PRIORITIES, r[3]), r[14] or '',
                _ms(r[6]), _has_due_time(r[6]), _ms(r[7]),
                _ms(r[8]), _ms(r[9]), r[10] or '',
                r[11] or '', r[12], r[13],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), 'Title', 'Description',
        'Priority', 'List', ('Due Date', 'datetime'), 'Due Time Set',
        ('Start Date', 'datetime'), ('Completed', 'datetime'), ('Deleted', 'datetime'),
        'Recurrence', 'Parent Task ID', 'Time Estimated (s)', 'Time Tracked (s)',
        'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tasks_org_locations(context):
    query = '''SELECT t.title, g.task, p.name, p.address, p.latitude, p.longitude,
                      p.radius, g.arrival, g.departure, p.phone, p.url
               FROM places p
               LEFT JOIN geofences g ON g.place = p.uid
               LEFT JOIN tasks t ON t._id = g.task
               ORDER BY p.place_id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                r[0] or '', r[1] or '', r[2] or '', r[3] or '',
                r[4], r[5], r[6], _yesno(r[7]), _yesno(r[8]),
                r[9] or '', r[10] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Task', 'Task ID', 'Place Name', 'Address', 'Latitude', 'Longitude',
        'Radius (m)', 'Arrival', 'Departure', 'Phone', 'URL', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tasks_org_reminders(context):
    query = '''SELECT a._id, a.task, a.time, a.type, a.repeat, a.interval, t.title
               FROM alarms a
               LEFT JOIN tasks t ON t._id = a.task
               ORDER BY a._id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                r[6] or '', r[1], _lookup(ALARM_TYPES, r[3]),
                _alarm_when(r[3], r[2]), r[4], r[5], r[2],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Task', 'Task ID', 'Type', 'When', 'Repeat Count', 'Interval (ms)',
        'Time Raw', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
