__artifacts_v2__ = {
    "moonreader_reading_sessions": {
        "name": "Moon+ Reader Reading Sessions",
        "description": "Books Moon+ Reader recorded time in, with the reading time, words read and progress it stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Moon+ Reader",
        "sample_data": {
            "emu_a15_oss_v15": "Moon+ Reader 10.7 | 1 row",
        },
        "notes": "One row per row of the statistics table in "
                 "com.flyersoft.moonreader/databases/mrbooks.db. The app writes a row when it has "
                 "recorded reading time against a file, and the row carries the file's full path, "
                 "the accumulated reading time in milliseconds, the number of words it counted as "
                 "read, and a per-day breakdown. "
                 "Per-day Detail is the dates column reported as stored, because its encoding was "
                 "read from one day's data and not from any source: on the tested image it held "
                 "'20701|16323@1048 #19.64%', where 20701 is a count of days from the Unix "
                 "epoch in the device's own local zone, 16323 and 1048 repeat that day's "
                 "milliseconds and words, and 19.64% is how far through the file the reader had "
                 "reached. The day number being local rather than UTC was measured: the reading "
                 "was done at 03:04 UTC, which was 23:04 the previous evening in the device's "
                 "America/New_York zone, and the app filed it under the previous day. Day (first "
                 "entry) is therefore rendered as a plain date with no zone conversion, since "
                 "converting a local day count as though it were UTC would move it. "
                 "day's milliseconds and words, and 19.64% is how far through the file the reader "
                 "had reached. A file read across several days carries several such groups, which "
                 "was not exercised here, so the column is passed through rather than split. "
                 "Reading Time (ms) and Words Read are the whole-file totals. "
                 "There is no absolute timestamp in this table, so a row dates reading only to "
                 "the day numbers inside Per-day Detail, and the Day (first entry) column is that "
                 "first day number converted to a date for convenience. "
                 "A row is evidence the app had the file open long enough to count time against "
                 "it, not that a person read it. "
                 "Other tables in the same database are not parsed here and were all empty on the "
                 "tested image: books is the library shelf, and the tested book was read without "
                 "being added to it, which is worth knowing because it means statistics records "
                 "reading for a file that never appears in books; notes holds highlights and "
                 "annotations; tmpbooks is a scratch list; covers2 holds cover images. Each would "
                 "carry data on a device that used those features.",
        "paths": ('*/com.flyersoft.moonreader/databases/mrbooks.db*',),
        "output_types": "standard",
        "artifact_icon": "book-open",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'com.flyersoft.moonreader/databases/mrbooks.db'
SECONDS_PER_DAY = 86400


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _first_day(dates):
    """The date of the first day group in the app's dates string, blank when it will not read.

    The string is groups separated by ';', each starting with a day number counted from the
    Unix epoch in the DEVICE'S LOCAL zone, proven by a read at 03:04 UTC being filed under the
    previous day. It is a date, not an instant, so it is rendered straight rather than
    converted. Mapped from one day of data created for the purpose, so anything that does not
    match that shape is left alone rather than guessed at.
    """
    if not dates:
        return ''
    head = str(dates).split(';')[0].split('|')[0].strip()
    if not head.isdigit():
        return ''
    try:
        return convert_unix_ts_to_utc(int(head) * SECONDS_PER_DAY)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def moonreader_reading_sessions(context):
    query = '''SELECT filename, usedTime, readWords, dates
               FROM statistics
               ORDER BY usedTime DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _first_day(r[3]),
                r[0] or '',
                r[1],
                r[2],
                (r[3] or '').strip(),
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Day (first entry)', 'date'), 'Book Path', 'Reading Time (ms)',
        'Words Read', 'Per-day Detail (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
