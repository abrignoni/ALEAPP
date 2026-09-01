__artifacts_v2__ = {
    "loop_habits": {
        "name": "Loop Habit Tracker - Habits",
        "description": "Parses tracked habits from the Loop Habit Tracker Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Loop Habit Tracker",
        "notes": "One row per entry in the Habits table of databases/uhabits.db. Loop Habit Tracker "
                 "is an open source habit tracker. Each row is a habit set up in the app, with its "
                 "Name, the Question the app asks about it, an optional Description, and the "
                 "Target and Unit used by measurable habits. Type is decoded from the app's "
                 "HabitType enum, 0 Yes/No and 1 Numerical (HabitType.kt at iSoron/uhabits tag "
                 "v2.3.1, 516bf394f85a5a3ab25f476da230ae2a93815a40); any other value is reported "
                 "as stored. Frequency is shown as the stored numerator and denominator, so 1/1 is "
                 "every day and 3/7 is three times a week. Archived marks a habit the person "
                 "hid rather than deleted. Reminder Time is built from the stored reminder hour "
                 "and minute and is blank where no reminder was set; it is a local wall-clock time "
                 "the app schedules against, not an instant, so it is reported as stored without "
                 "a timezone. Reminder Days is the stored day bitmask, reported as stored. The "
                 "individual check-ins are in the Check-ins artifact, keyed by Habit ID. A habit's "
                 "Name and Question are text the person wrote, so they can carry personal detail "
                 "beyond the habit itself.",
        "paths": ('*/org.isoron.uhabits/databases/uhabits.db*',),
        "output_types": "standard",
        "artifact_icon": "check-circle",
    },
    "loop_habits_checkins": {
        "name": "Loop Habit Tracker - Check-ins",
        "description": "Parses habit check-ins from the Loop Habit Tracker Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Loop Habit Tracker",
        "notes": "One row per entry in the Repetitions table of databases/uhabits.db, joined to "
                 "its habit. Each row is a check-in recorded against a habit for one day. Value is "
                 "decoded from the app's Entry constants, -1 Unknown, 0 No, 1 Yes (automatic), 2 "
                 "Yes (manual), 3 Skip (Entry.kt at iSoron/uhabits tag v2.3.1, "
                 "516bf394f85a5a3ab25f476da230ae2a93815a40); any other value is reported as "
                 "stored, and for a numerical habit the same column holds the recorded amount "
                 "rather than one of these codes, which is why the stored number is also reported "
                 "in Value Raw. Date is the day the check-in belongs to. The stored timestamp is "
                 "Unix milliseconds and lands on midnight UTC, so it marks a calendar day rather "
                 "than a moment: both check-ins on the tested device were stored at exactly "
                 "00:00:00 UTC, so the date is reported as stored and is deliberately not "
                 "converted into a local timezone, which would move it to the previous day for any "
                 "negative offset. The check-in records the day a habit was marked, not the time "
                 "of day the person marked it, and a Yes (manual) value is one entered in the app "
                 "rather than derived by it. Notes is the optional note attached to a check-in.",
        "paths": ('*/org.isoron.uhabits/databases/uhabits.db*',),
        "output_types": "standard",
        "artifact_icon": "check-square",
    },
}

import datetime

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/uhabits.db'

# HabitType.kt and Entry.kt at iSoron/uhabits tag v2.3.1.
HABIT_TYPES = {0: 'Yes/No', 1: 'Numerical'}
ENTRY_VALUES = {-1: 'Unknown', 0: 'No', 1: 'Yes (automatic)', 2: 'Yes (manual)', 3: 'Skip'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _lookup(table, value):
    if value in table:
        return table[value]
    if value is None or value == '':
        return ''
    return f'{value} (as stored)'


def _day(value):
    """The calendar day a check-in belongs to, as stored (midnight UTC), never converted."""
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return ''
    try:
        return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
    except (ValueError, OverflowError, OSError):
        return ''


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


def _reminder(hour, minute):
    if hour is None or minute is None:
        return ''
    try:
        return f'{int(hour):02d}:{int(minute):02d}'
    except (TypeError, ValueError):
        return ''


@artifact_processor
def loop_habits(context):
    query = '''SELECT name, question, description, type, target_type, target_value, unit,
                      freq_num, freq_den, archived, reminder_hour, reminder_min,
                      reminder_days, position, uuid, id
               FROM Habits ORDER BY position, id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            freq = f'{r[7]}/{r[8]}' if r[7] is not None and r[8] is not None else ''
            data_list.append((r[0] or '', r[1] or '', r[2] or '', _lookup(HABIT_TYPES, r[3]),
                              freq, r[5], r[6] or '', _yesno(r[9]),
                              _reminder(r[10], r[11]), r[12], r[14] or '', r[15],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Name', 'Question', 'Description', 'Type', 'Frequency', 'Target', 'Unit',
                    'Archived', 'Reminder Time', 'Reminder Days', 'UUID', 'Habit ID',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def loop_habits_checkins(context):
    query = '''SELECT r.timestamp, h.name, r.value, r.notes, r.habit, r.id
               FROM Repetitions r
               LEFT JOIN Habits h ON h.id = r.habit
               ORDER BY r.timestamp DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_day(r[0]), r[1] or '', _lookup(ENTRY_VALUES, r[2]), r[2],
                              r[3] or '', r[4], r[5],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Date', 'date'), 'Habit', 'Value', 'Value Raw', 'Notes', 'Habit ID',
                    'Check-in ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
