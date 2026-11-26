"""Reader for the text that ``adb shell content query --uri <uri>`` prints.

On a device without root, the records of the platform providers (SMS, MMS, call log,
contacts, calendar, MediaStore) can be read through the ``content`` shell command. Some
extraction tools keep that output as one text file per URI. This module reads one such
file, says what it holds (rows, ``No result found.``, a provider error, an empty file or
text it does not recognise) and splits the rows into columns. It never writes anything
and does not judge what it reads.

Layout of the text, as the ``content`` command prints it (AOSP
``cmds/content/src/com/android/commands/content/Content.java``)::

    Row: 0 _id=12, address=+15550100001, body=See you at 8, date=1767225600000
    Row: 1 _id=13, address=+15550100002, body=First line
    second line, date=1767229200000

* Every row is one ``println`` of ``Row: <n> `` and the ``name=value`` pairs joined with
  ``, ``. Nothing is quoted or escaped, so a value that holds a line break runs over
  several lines, and a value can hold the text ``, name=``.
* A NULL value prints as the text ``NULL``, a BLOB as the text ``BLOB`` (the bytes are not
  printed) and an empty string as nothing.
* Every row of one dump prints the same columns in the same order, because they are the
  columns of one cursor.
* ``No result found.`` is printed on stdout when the provider returns no cursor or an
  empty one.
* ``Error while accessing provider:<authority>`` and the Java stack trace of the exception
  are printed on stderr. Whether they reach the file depends on how the extraction tool
  captured stderr.

Parsing:

1. Lines are split on ``\\n``, and one carriage return at the end of each line is dropped,
   so a file saved with CRLF line endings reads like one saved with LF.
2. A line opens a row when it is ``Row: <n> <first column>=`` with ``n`` the next row number
   in sequence (0, 1, 2, ...) and the first column the one the first ``Row: 0`` line names
   (the one most such lines start with when there is no ``Row: 0`` line). When ``Row: 0``
   lines name different first columns (a line before the rows, or a value quoting rows),
   the earliest is kept when a ``Row: 1`` line with the same first column follows it. Only
   when it does not, each of the first four is tried and the reading kept has the fewest
   rows that cannot be split, then the least text before its first row, then the earliest
   ``Row: 0``. Every
   other line belongs to the value before it. A value line that is itself exactly
   ``Row: <next number> <first column>=...`` cannot be told apart from a new row.
3. The column list of the dump is the most common ordered list of names found in the rows
   by a plain split at ``, <name>=``. Each row is then split by walking that list: the
   value of a column runs to the first ``, <next column>=``. A value that holds
   ``, <name>=`` for a name of the dump's own column list is flagged on its row, since the
   split there may be off. When that list names a column more than once, which a value
   holding ``, <name>=`` in every row of the dump (or in its only row) also produces, the
   rows are not split and each keeps its text.
4. 'Error while accessing provider:' and an exception line inside the last row are read
   as an error printed after it only when the row without them still holds the column
   list; when the whole row holds it too, the row says the boundary is ambiguous.
"""
import collections
import os
import re
from datetime import datetime, timedelta, timezone

ROW = re.compile(r'Row: (\d+) (.*)\Z', re.S)
FIRST_NAME = re.compile(r'([^\s=,]+)=')
NAME_IN_ROW = re.compile(r'(?:\A|, )([^\s=,]+)=')
# The separator alone (', <name>='), so a value that starts with a plain 'name=' is not flagged.
DELIMITER = re.compile(r', ([^\s=,]+)=')
ERROR_LINE = 'Error while accessing provider:'
NO_RESULT_LINE = 'No result found.'
EXCEPTION_LINE = re.compile(r'(?:Caused by: )?([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+)(?::\s?(.*))?\Z')
SECURITY_EXCEPTION = 'java.lang.SecurityException'
DETAIL_CHARS = 400
CACHE_SIZE = 8
# 'Row: 0' readings tried when several 'Row: 0' lines name different first columns.
MAX_READINGS = 4
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# What a file holds, as reported by the Content Query Files artifact.
ROWS = 'rows'
NO_RESULT = 'No result found.'
ACCESS_DENIED = 'access denied (SecurityException)'
PROVIDER_ERROR = 'provider error'
EMPTY_FILE = 'empty file'
UNRECOGNISED = 'text not recognised'
NO_FILE = 'no file'
UNREADABLE = 'file not readable'

# Notes on a row, shown in its Parse Note column.
NOTE_AMBIGUOUS = 'a value holds ", {name}=", the name of a column of this dump; the split at that point may be off'
NOTE_NOT_SPLIT = 'the row does not hold the columns of this dump in order; values not split. Row text: {text}'
NOTE_REPEATED = ('the column list of this dump names {names} more than once, which a value holding ", <name>=" '
                 'can also cause; values not split. Row text: {text}')
NOTE_ERROR_OR_VALUE = ('the provider error text after this row was read as an error; it could also be the end of '
                       'the last value, which would then be longer')

Record = collections.namedtuple('Record', 'number line pairs note')
Dump = collections.namedtuple('Dump', 'status detail columns records warnings')


class Values:
    """The values of one row, by column name. A column printed twice keeps its first value."""

    def __init__(self, record):
        self.record = record
        self._first = {}
        for name, value in record.pairs:
            self._first.setdefault(name, value)

    def __getitem__(self, name):
        return self._first.get(name, '')

    def has(self, name):
        return name in self._first


def _lines(text):
    if text.startswith('﻿'):
        text = text[1:]
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return [line[:-1] if line.endswith('\r') else line for line in lines]


def _cut(text, size=DETAIL_CHARS):
    text = ' '.join(text.split())
    return text if len(text) <= size else text[:size] + '...'


def _error(lines, start):
    """Status and detail of an error text whose first line is lines[start]."""
    authority = lines[start][len(ERROR_LINE):].strip()
    for line in lines[start + 1:]:
        if not line.strip():
            continue
        match = EXCEPTION_LINE.match(line.strip())
        if match:
            name, message = match.group(1), (match.group(2) or '').strip()
            status = ACCESS_DENIED if name == SECURITY_EXCEPTION else PROVIDER_ERROR
            detail = f'provider {authority}: {name}' + (f': {message}' if message else '')
            return status, _cut(detail)
        break
    return PROVIDER_ERROR, _cut(f'provider {authority}: no exception line after the error line')


def _classify_without_rows(lines):
    """Status and detail of a text that holds no row."""
    if not any(line.strip() for line in lines):
        return EMPTY_FILE, ''
    for index, line in enumerate(lines):
        if line.startswith(ERROR_LINE):
            return _error(lines, index)
    if any(line.strip() == NO_RESULT_LINE for line in lines):
        return NO_RESULT, ''
    first = next(line for line in lines if line.strip())
    return UNRECOGNISED, _cut(first)


def _candidates(lines):
    """(index, number, rest) of every line shaped like 'Row: <n> ...'."""
    candidates = []
    for index, line in enumerate(lines):
        match = ROW.match(line)
        if match:
            candidates.append((index, int(match.group(1)), match.group(2)))
    return candidates


def _row_zero_names(lines):
    """The first-column names of the 'Row: 0' lines, in order, each once."""
    names = []
    for _index, number, rest in _candidates(lines):
        name = FIRST_NAME.match(rest)
        if number == 0 and name and name.group(1) not in names:
            names.append(name.group(1))
    return names


def _row_starts(lines, first=None):
    """Indexes of the lines that open a row (see the module docstring, step 2), with ``first``
    ('<name>=') as the first column when it is given."""
    candidates = _candidates(lines)
    if not candidates:
        return []
    # Without ``first``, the first column is the one the first 'Row: 0' line names: row 0 is
    # printed before any value, so a line inside a value cannot come first. A vote over every
    # candidate is kept only for a text with no 'Row: 0' line.
    if first is None:
        names = _row_zero_names(lines)
        first = names[0] + '=' if names else None
    if first is None:
        first_names = collections.Counter()
        for _index, _number, rest in candidates:
            name = FIRST_NAME.match(rest)
            if name:
                first_names[name.group(1)] += 1
        if not first_names:
            return []
        first = first_names.most_common(1)[0][0] + '='
    starts, expected = [], 0
    for index, number, rest in candidates:
        if number == expected and rest.startswith(first):
            starts.append(index)
            expected += 1
    return starts


def _split(text, columns):
    """The (name, value) pairs of one row text, walking the column list; None if it does not fit."""
    if not text.startswith(columns[0] + '='):
        return None
    position = len(columns[0]) + 1
    pairs = []
    for index, name in enumerate(columns):
        if index + 1 < len(columns):
            separator = ', ' + columns[index + 1] + '='
            end = text.find(separator, position)
            if end < 0:
                return None
            pairs.append((name, text[position:end]))
            position = end + len(separator)
        else:
            pairs.append((name, text[position:]))
    return pairs


def _ambiguous(pairs, names):
    """The first column name of the dump that a value holds as ', <name>=', at any offset, or None."""
    for _name, value in pairs:
        if ', ' not in value:
            continue
        for match in DELIMITER.finditer(value):
            if match.group(1) in names:
                return match.group(1)
    return None


def parse_text(text):
    """Reads the text of one content query output and returns a Dump."""
    lines = _lines(text)
    names = _row_zero_names(lines)
    if len(names) < 2:
        return _parse_lines(lines, _row_starts(lines))
    # The earliest 'Row: 0' line is row 0 when a 'Row: 1' line with the same first column
    # follows it: then the text holds at least two rows that way, and a sequence quoted later
    # inside a value cannot replace them.
    starts = _row_starts(lines, names[0] + '=')
    if len(starts) > 1:
        return _parse_lines(lines, starts)
    # Several 'Row: 0' lines name different first columns: a line before the rows, or a value
    # that quotes rows, looks like row 0 too. Each reading is tried, and the one kept has the
    # fewest rows that cannot be split, then the least text left before its first row; on a
    # tie, the earliest 'Row: 0' line.
    # Each reading parses the whole text, so only the first MAX_READINGS names are tried.
    readings = []
    for order, name in enumerate(names[:MAX_READINGS]):
        starts = _row_starts(lines, name + '=')
        dump = _parse_lines(lines, starts)
        unsplit = sum(1 for record in dump.records if not record.pairs) if dump.records else len(lines)
        before = sum(1 for line in lines[:starts[0]] if line.strip()) if starts else len(lines)
        readings.append(((unsplit, before, order), dump))
    return min(readings, key=lambda reading: reading[0])[1]


def _parse_lines(lines, starts):
    """The Dump of a text split into lines, with ``starts`` the indexes of the lines that open a row."""
    warnings = []
    if not starts:
        status, detail = _classify_without_rows(lines)
        return Dump(status, detail, (), [], warnings)
    if any(line.strip() for line in lines[:starts[0]]):
        warnings.append(f'{starts[0]} line(s) of text before the first row, not read: '
                        + _cut(' '.join(lines[:starts[0]]), 200))

    bounds = list(zip(starts, starts[1:] + [len(lines)]))
    status, detail = ROWS, ''
    last_start, last_end = bounds[-1]
    error_at = None
    for index in range(last_start + 1, last_end):
        if lines[index].startswith(ERROR_LINE):
            following = [line for line in lines[index + 1:last_end] if line.strip()]
            if following and EXCEPTION_LINE.match(following[0].strip()):
                error_at = index
                break

    def row_text(start, end):
        first = ROW.match(lines[start])
        return '\n'.join([first.group(2)] + lines[start + 1:end])

    texts = [(int(ROW.match(lines[start]).group(1)), start + 1, row_text(start, end)) for start, end in bounds]
    columns = _columns(texts)

    last_note = ''
    if error_at is not None:
        # The error text may follow the last row, or be part of its last value. It is read as an
        # error only when the row without it still holds the dump's columns in order.
        cut_text = row_text(last_start, error_at)
        cut_fits = _split(cut_text, columns) is not None
        whole_fits = _split(texts[-1][2], columns) is not None
        if cut_fits:
            error_status, error_detail = _error(lines, error_at)
            detail = f'then {error_status}: {error_detail}'
            warnings.append('the text ends with a provider error after the last row; '
                            'the rows printed before it are read')
            texts[-1] = (texts[-1][0], texts[-1][1], cut_text)
            if whole_fits:
                last_note = NOTE_ERROR_OR_VALUE
                warnings.append('the provider error text after the last row could also be part of its last value')
        else:
            warnings.append('a provider error line inside the last row is kept as part of its values, since the row '
                            'without it does not hold the columns of this dump')

    repeated = sorted(name for name, count in collections.Counter(columns).items() if count > 1)
    names = set(columns)
    records = []
    for number, line, text in texts:
        if repeated:
            records.append(Record(number, line, [], NOTE_REPEATED.format(names=', '.join(repeated), text=text)))
            continue
        pairs = _split(text, columns)
        if pairs is None:
            records.append(Record(number, line, [], NOTE_NOT_SPLIT.format(text=text)))
            continue
        name = _ambiguous(pairs, names)
        notes = [NOTE_AMBIGUOUS.format(name=name)] if name else []
        if last_note and number == texts[-1][0] and line == texts[-1][1]:
            notes.append(last_note)
        records.append(Record(number, line, pairs, '; '.join(notes)))
    if repeated:
        warnings.append(f'the column list of this dump names {", ".join(repeated)} more than once, which a value '
                        f'holding ", <name>=" can also cause; rows are not split')
    else:
        unsplit = sum(1 for record in records if not record.pairs)
        if unsplit:
            warnings.append(f'{unsplit} row(s) do not hold the columns of this dump in order and are not split')
    return Dump(status, detail, columns, records, warnings)


def _columns(texts):
    """The column list of a dump: the most common ordered list of names in its rows (step 3)."""
    orders = collections.Counter()
    for _number, _line, text in texts:
        orders[tuple(match.group(1) for match in NAME_IN_ROW.finditer(text))] += 1
    top = max(orders.values())
    return min((order for order, count in orders.items() if count == top), key=len)


def decode(data):
    """Text of the file bytes, and a warning when they are not all UTF-8."""
    try:
        return data.decode('utf-8'), None
    except UnicodeDecodeError:
        return data.decode('utf-8', errors='replace'), 'bytes that are not UTF-8 are shown as U+FFFD'


def _read(path):
    with open(path, 'rb') as handle:
        data = handle.read()
    text, warning = decode(data)
    dump = parse_text(text)
    if warning:
        dump.warnings.append(warning)
    return dump


# Dumps read in the current processing run, by path. The run is the object the caller passes (the
# run's seeker): it is held here and compared by identity, so a new run, which has a new seeker,
# starts with an empty cache and reads its own staged files, even at the same path.
_CACHE = collections.OrderedDict()
_CACHE_RUN = [None]


def clear_cache():
    """Forget the dumps read so far."""
    _CACHE.clear()
    _CACHE_RUN[0] = None


def read_file(path, run=None):
    """Reads one content query output file and returns a Dump.

    With ``run`` (an object that stands for one processing run, such as its seeker) the dump is kept
    for the other artifacts of the same run, so each file is read once per run; a call with another
    ``run`` clears what was kept. Without it the file is read every time."""
    if run is None:
        return _read(path)
    if _CACHE_RUN[0] is not run:
        clear_cache()
        _CACHE_RUN[0] = run
    key = os.path.abspath(path)
    dump = _CACHE.get(key)
    if dump is None:
        dump = _read(path)
        _CACHE[key] = dump
        while len(_CACHE) > CACHE_SIZE:
            _CACHE.popitem(last=False)
    else:
        _CACHE.move_to_end(key)
    return dump


def epoch_to_utc(text, unit):
    """(datetime or '', note) for a printed integer time in 'ms' or 's'. NULL, empty and 0 give ''."""
    value = text.strip()
    if value in ('', 'NULL', '0'):
        return '', ''
    sign = value[1:] if value.startswith('-') else value
    if not (sign.isascii() and sign.isdigit()):
        return '', f'time value {_cut(value, 40)} is not an integer'
    try:
        # int() raises ValueError past Python's integer string conversion limit (4,300 digits by default).
        number = int(value)
        delta = timedelta(milliseconds=number) if unit == 'ms' else timedelta(seconds=number)
        return EPOCH + delta, ''
    except (OverflowError, ValueError):
        return '', f'time value {_cut(value, 40)} ({len(sign)} digits) is out of range'


# ------------------------------------------------------------------------------------------
# Layouts: where an extraction tool keeps the output of each URI.
# ------------------------------------------------------------------------------------------
# android_triage (RealityNet/android_triage, android_triage.sh, content_provider function):
# <ANDROID_ID>/<YYYYMMDD_HH_MM_SS>_contentprovider/<name>.txt, stdout only (a shell redirect).
# Next to the outputs it keeps its own log (<folder name>.txt) and the dumpsys of the
# providers (content_providers_list.txt), which are not content query output.
# ALEX (prosch88/ALEX, alex.py, query_content; URIs from ressources/content_provider.json):
# content_provider_<serial>/<key>/<key>.txt for content://<key>, and <key>_<sub>.txt for
# content://<key>/<sub> with each '/' of <sub> written as '_'. Up to commit 8f27e7a no file
# is written when the output holds any of: Error while accessing provider, Unsupported
# argument, No result found, command not found. From ed3d41eb the file is written whenever
# the output holds a row. The PRFS zip layout of ed3d41eb (extra/content_provider/) is not read.
TRIAGE = 'android_triage'
ALEX = 'ALEX'
TRIAGE_FOLDER = re.compile(r'\d{8}_\d{2}_\d{2}_\d{2}_contentprovider\Z')
TRIAGE_OWN_FILES = ('content_providers_list.txt',)
ALEX_FOLDER_PREFIX = 'content_provider_'

Uri = collections.namedtuple('Uri', 'key uri triage alex')
URIS = (
    Uri('sms', 'content://sms', None, 'sms/sms.txt'),
    Uri('mms', 'content://mms', None, 'mms/mms.txt'),
    Uri('mms_part', 'content://mms/part', None, 'mms/mms_part.txt'),
    Uri('mms_addr', 'content://mms/addr', None, 'mms/mms_addr.txt'),
    Uri('call_log', 'content://call_log/calls', None, 'call_log/call_log_calls.txt'),
    Uri('contacts', 'content://com.android.contacts/contacts', 'contacts_contacts.txt',
        'com.android.contacts/com.android.contacts_contacts.txt'),
    Uri('contact_phones', 'content://com.android.contacts/data/phones', 'contacts_data_phones.txt',
        'com.android.contacts/com.android.contacts_data_phones.txt'),
    Uri('calendar_events', 'content://com.android.calendar/events', 'calendar_events.txt', None),
    Uri('calendar_event_entities', 'content://com.android.calendar/event_entities', 'calendar_event_entities.txt',
        'com.android.calendar/com.android.calendar_event_entities.txt'),
    Uri('calendars', 'content://com.android.calendar/calendars', 'calendar_calendars.txt',
        'com.android.calendar/com.android.calendar_calendars.txt'),
    Uri('media_files', 'content://media/external/file', 'media_external_file.txt', 'media/media_external_file.txt'),
)
URI_BY_KEY = {uri.key: uri for uri in URIS}


def _parts(path):
    return [part for part in re.split(r'[\\/]', str(path)) if part]


def layout_of(path):
    """(layout, folder) for a content query output file of a known layout, else None.

    The folder is the layout's output folder (the *_contentprovider folder of android_triage
    or the content_provider_<serial> folder of ALEX), as a path of the same spelling."""
    parts = _parts(path)
    if len(parts) < 2 or not parts[-1].endswith('.txt'):
        return None
    name, parent = parts[-1], parts[-2]
    if TRIAGE_FOLDER.match(parent):
        if name in TRIAGE_OWN_FILES or name == parent + '.txt':
            return None
        return TRIAGE, os.path.dirname(str(path))
    if len(parts) >= 3 and parts[-3].startswith(ALEX_FOLDER_PREFIX):
        if name == parent + '.txt' or name.startswith(parent + '_'):
            return ALEX, os.path.dirname(os.path.dirname(str(path)))
    return None


def layout_file(layout, uri):
    """Path of a URI's file inside a layout folder, with '/' separators, or None if the layout does not query it."""
    return uri.triage if layout == TRIAGE else uri.alex


def uri_of(layout, path):
    """The Uri entry a file of a known layout holds, or None for a URI this module does not read."""
    parts = _parts(path)
    relative = parts[-1] if layout == TRIAGE else '/'.join(parts[-2:])
    for uri in URIS:
        if layout_file(layout, uri) == relative:
            return uri
    return None


def missing_file_detail(layout):
    """What a missing file says about the query, per layout."""
    if layout == TRIAGE:
        return ('android_triage creates the file of every URI it queries with a shell redirect, even when the '
                'query prints nothing, so the file was not kept in this extraction or the run stopped '
                'before this query')
    return ('unknown: ALEX writes no file when the query printed no row (No result found. or an error), and up to '
            'commit 8f27e7a also when the output holds one of its four error strings anywhere, including inside '
            'a value')


def status_text(dump):
    """One line saying what a dump holds."""
    if dump.status == ROWS:
        return f'{len(dump.records)} rows' + (f', {dump.detail}' if dump.detail else '')
    return dump.status + (f': {dump.detail}' if dump.detail else '')
