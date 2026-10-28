"""Reader for the Samsung recovery history files, read by sRecoveryhist and Bug Report - Recovery History.

The files are plain text kept by the recovery program of the device:

* ``history`` (``/efs/recovery/history``) and, in a bug report, ``last_history`` and ``last_all_history``
  (``/cache/recovery/``): one entry for each start of recovery, in the order written::

      + [CODE | YYYY/MM/DD HH:MM:SS | FIRMWARE] [-]       <- header: a two-letter code, a date, the firmware
      --wipe_data                                          <- the options recovery was started with
      --requested_time=YYYY/MM/DD HH:MM:SS.mmm
      --reason=MasterClearConfirm,...
      NP [-]                                               <- a status line (NP, or RP with more words)
      reboot_reason=...

* ``extra_history`` (``/efs/recovery/``) and ``last_extra_history`` (``/cache/recovery/``): ``Created at <date>``
  and then lines ``[CODE][S] text`` and ``[CODE][E] text``. The code is the one of a history entry.
  ``format_volume : /data`` names a volume that recovery formatted; S and E are the start line and the
  end line of the step as printed.

Nothing here depends on the rest of ALEAPP. Nothing is judged: an entry says that recovery was started with the
options shown, not that the work was done. The date in a header and the ``--requested_time`` value are shown as printed;
no other time is derived from them. On the tested files header dates near 1970 and 2010 occur.
"""
import re
from collections import OrderedDict, namedtuple
from datetime import datetime

HEADER_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
REQUESTED_FORMATS = ('%Y/%m/%d %H:%M:%S.%f', '%Y/%m/%d %H:%M:%S')
# A header date before this year is noted on its row (the tested files showed header dates in 1970 and 2010).
HEADER_NOTE_YEAR = 2012
MAX_ENTRIES = 20000
MAX_EXTRA_LINES = 100000
MAX_TEXT = 400

_CONTROL = re.compile('[\x00-\x08\x0b-\x1f\x7f]')
_HEADER = re.compile(r'^\+\s*\[(?P<inner>[^\]]*)\](?P<tail>.*)$')
# An older header shape without brackets: '+ ... : date'. Any other line that starts with a plus sign is an entry header too.
_PLAIN_HEADER = re.compile(r'^\+(?P<rest>.*)$')
_STATUS = re.compile(r'^(NP|RP)\b')
_EXTRA_LINE = re.compile(r'^\[(?P<code>[^\]]*)\]\[(?P<state>[A-Za-z])\]\s?(?P<text>.*)$')
_SIM_CHANGE = re.compile(r'\[SIMBasedChangeCSC\]\s*(?P<old>\S+)\s*->\s*(?P<new>\S+)')

Entry = namedtuple('Entry', 'code header_text header_time firmware options reason requested requested_time update_package '
                            'status reboot_reason other_lines activity line')
ExtraLine = namedtuple('ExtraLine', 'code state text line')
ExtraHistory = namedtuple('ExtraHistory', 'created lines')

HISTORY_NAMES = ('history', 'last_history', 'last_all_history')
# The extra file that goes with each history file, in the same folder.
EXTRA_FOR = {'history': 'extra_history', 'last_history': 'last_extra_history', 'last_all_history': 'last_extra_history'}
EXTRA_NAMES = tuple(OrderedDict.fromkeys(EXTRA_FOR.values()))


def tidy(value):
    """A text with control characters shown as a space and a cap on the length."""
    return _CONTROL.sub(' ', str(value))[:MAX_TEXT]


def _parse_time(text, formats):
    for form in formats:
        try:
            return datetime.strptime(text.strip(), form)
        except ValueError:
            continue
    return None


def parse_header_time(text):
    """Naive datetime of a header date ``YYYY/MM/DD HH:MM:SS``, or None."""
    return _parse_time(text, (HEADER_DATE_FORMAT,))


def parse_requested_time(text):
    """Naive datetime of a ``--requested_time`` value, or None."""
    return _parse_time(text, REQUESTED_FORMATS)


def header_date_before_floor(moment):
    """True for a header date before HEADER_NOTE_YEAR (it is shown as printed and noted)."""
    return moment is not None and moment.year < HEADER_NOTE_YEAR


def activity_of(options, reason):
    """The activity words for an entry: what recovery was started with, taken from the options.

    ``--wipe_data`` gives "Wipe requested (--wipe_data)", ``--prompt_and_wipe_data`` "Prompt and wipe requested", an
    ``--update_package`` option "Update package", a reason ``[SIMBasedChangeCSC] A -> B`` "SIM region change (A -> B)",
    and an entry with none of these "Other". The words say which options are printed, not what was carried out.
    """
    names = [option.split('=', 1)[0] for option in options]
    found = []
    if '--wipe_data' in names:
        found.append('Wipe requested (--wipe_data)')
    if '--prompt_and_wipe_data' in names:
        found.append('Prompt and wipe requested (--prompt_and_wipe_data)')
    if '--update_package' in names:
        found.append('Update package (--update_package)')
    change = _SIM_CHANGE.search(reason)
    if change:
        found.append('SIM region change (%s -> %s)' % (change.group('old'), change.group('new')))
    return '; '.join(found) if found else 'Other'


def _new_entry(header, line_no):
    if header.groupdict().get('rest') is not None:
        rest = header.group('rest').strip()
        code, date, firmware = '', (rest.split(':', 1)[1].strip() if ':' in rest else rest), ''
    else:
        inner = header.group('inner')
        tail = header.group('tail')
        if '|' not in inner and tail.lstrip().startswith('|'):
            # '+ [tag] | date | build]': the first bracket closes after the tag and the rest of the header follows it.
            inner += tail.partition(']')[0]
        parts = [part.strip() for part in inner.split('|')]
        if len(parts) >= 3:
            code, date, firmware = parts[0], parts[1], '|'.join(parts[2:]).strip()
        else:
            code, date, firmware = '', inner.strip(), ''
    return {'code': code, 'header_text': date, 'firmware': firmware, 'options': [], 'reason': '', 'requested': '',
            'update_package': '', 'status': '', 'reboot_reason': '', 'other': [], 'line': line_no}


def _finish_entry(raw):
    moment = parse_header_time(raw['header_text'])
    return Entry(tidy(raw['code']), tidy(raw['header_text']), moment, tidy(raw['firmware']), tuple(raw['options']),
                 raw['reason'], raw['requested'], parse_requested_time(raw['requested']), raw['update_package'],
                 raw['status'], raw['reboot_reason'], tuple(raw['other']),
                 activity_of(raw['options'], raw['reason']), raw['line'])


def _add_line(raw, text):
    """File one body line of an entry under the field it belongs to."""
    if text.startswith('--'):
        raw['options'].append(tidy(text.rstrip()))
        name, _sep, value = text[2:].partition('=')
        value = value.strip()
        if name == 'reason':
            raw['reason'] = tidy(value)
        elif name == 'requested_time':
            raw['requested'] = tidy(value)
        elif name == 'update_package':
            raw['update_package'] = tidy(value)
    elif text.startswith('reboot_reason='):
        raw['reboot_reason'] = tidy(text[len('reboot_reason='):].strip())
    elif text.lower().startswith('reboot reason:'):
        raw['reboot_reason'] = tidy(text.split(':', 1)[1].strip())
    elif _STATUS.match(text):
        raw['status'] = tidy(text.strip())
    elif text.strip() and text.strip() != '-':      # a lone '-' is the separator that can end a record
        raw['other'].append(tidy(text.strip()))


def parse_history(text):
    """``(entries, warnings)`` for the text of a history file, in the order written.

    A line before the first header is not part of an entry and is counted in the warnings. An entry ends at the next
    header or at the end of the text.
    """
    entries = []
    warnings = []
    raw = None
    stray = 0
    for line_no, line in enumerate(str(text).replace('\r\n', '\n').replace('\r', '\n').split('\n'), 1):
        header = _HEADER.match(line) or _PLAIN_HEADER.match(line)
        if header:
            if raw is not None:
                entries.append(_finish_entry(raw))
            if len(entries) >= MAX_ENTRIES:
                warnings.append('more than %d entries, the rest were not read' % MAX_ENTRIES)
                raw = None
                break
            raw = _new_entry(header, line_no)
            continue
        if not line.strip():
            continue
        if raw is None:
            stray += 1
        else:
            _add_line(raw, line)
    if raw is not None:
        entries.append(_finish_entry(raw))
    if stray:
        warnings.append('%d non-blank lines before the first entry header were not read' % stray)
    return entries, warnings


def parse_extra_history(text):
    """``(ExtraHistory, warnings)`` for the text of an extra history file."""
    created = ''
    lines = []
    warnings = []
    other = 0
    for line_no, line in enumerate(str(text).replace('\r\n', '\n').replace('\r', '\n').split('\n'), 1):
        if line.startswith('Created at '):
            if not created:
                created = tidy(line[len('Created at '):].strip())
            continue
        found = _EXTRA_LINE.match(line)
        if found:
            if len(lines) >= MAX_EXTRA_LINES:
                warnings.append('more than %d lines, the rest were not read' % MAX_EXTRA_LINES)
                break
            lines.append(ExtraLine(tidy(found.group('code')), found.group('state').upper(), tidy(found.group('text').rstrip()), line_no))
        elif line.strip():
            other += 1
    if other:
        warnings.append('%d lines were not in the form [CODE][S|E] text and were not read' % other)
    return ExtraHistory(created, lines), warnings


def formatted_volumes(extra):
    """``{code: [(volume, has start line, has end line), ...]}`` from the ``format_volume : <volume>`` lines, in order."""
    volumes = OrderedDict()
    for item in extra.lines:
        if not item.text.startswith('format_volume'):
            continue
        volume = (item.text.split(':', 1)[1].strip() if ':' in item.text else item.text[len('format_volume'):].strip()) or '(no volume named)'
        per_code = volumes.setdefault(item.code, OrderedDict())
        flags = per_code.setdefault(volume, [False, False])
        if item.state == 'S':
            flags[0] = True
        elif item.state == 'E':
            flags[1] = True
    return OrderedDict((code, [(volume, start, end) for volume, (start, end) in per_code.items()])
                       for code, per_code in volumes.items())


def volumes_text(volumes):
    """The volumes of one code as text: ``/data (start and end lines); /cache (start line only)``."""
    parts = []
    for volume, start, end in volumes:
        if start and end:
            note = 'start and end lines'
        elif start:
            note = 'start line only'
        elif end:
            note = 'end line only'
        else:
            note = 'no start or end line'
        parts.append('%s (%s)' % (volume, note))
    return '; '.join(parts)


def entry_notes(entry, repeated_code):
    """Short notes for an entry's row, as a list of texts."""
    notes = []
    if header_date_before_floor(entry.header_time):
        notes.append('header date is before %d, shown as printed' % HEADER_NOTE_YEAR)
    elif entry.header_time is None:
        notes.append('header date not recognised')
    if entry.requested and entry.requested_time is None:
        notes.append('requested time not recognised')
    if repeated_code:
        notes.append('the code is used by more than one entry of this file: formatted volumes are matched by code only')
    return notes


ROW_KEYS = ('code', 'header_text', 'firmware', 'activity', 'options', 'reason', 'requested', 'volumes',
            'status', 'reboot_reason', 'other', 'notes', 'line', 'source', 'extra_file')


def option_value(entry, name):
    """The text after ``=`` of the first option named ``name`` (for example ``--locale``) of an entry, or ''."""
    for option in entry.options:
        head, sep, value = option.partition('=')
        if sep and head == name:
            return value.strip()
    return ''


def records_for(entries, extra, source_label, extra_label='', orphans=True):
    """Records (dicts with the keys of ROW_KEYS and ``entry``) for the entries of one history file and its extra file.

    ``extra`` is None when there is no extra file. With ``orphans`` an extra file that has format lines for a code with no
    entry gives one more record per code whose fields from the history are blank and whose ``entry`` is None.
    """
    volumes = formatted_volumes(extra) if extra is not None else {}
    counts = {}
    for entry in entries:
        counts[entry.code] = counts.get(entry.code, 0) + 1
    records = []
    for entry in entries:
        notes = entry_notes(entry, bool(entry.code) and counts[entry.code] > 1)
        records.append({'code': entry.code, 'header_text': entry.header_text, 'firmware': entry.firmware, 'activity': entry.activity,
                        'options': '; '.join(entry.options), 'reason': entry.reason, 'requested': entry.requested,
                        'volumes': volumes_text(volumes.get(entry.code, [])),
                        'status': entry.status, 'reboot_reason': entry.reboot_reason, 'other': '; '.join(entry.other_lines),
                        'notes': '; '.join(notes), 'line': entry.line, 'source': source_label,
                        'extra_file': extra_label if extra is not None else '', 'entry': entry})
    if orphans and extra is not None:
        records += orphan_records(extra, {entry.code for entry in entries}, source_label, extra_label)
    return records


def orphan_records(extra, known_codes, source_label, extra_label):
    """One record for each code with format lines in the extra file and no entry among ``known_codes``."""
    records = []
    for code, items in formatted_volumes(extra).items():
        if code not in known_codes:
            records.append({'code': code, 'header_text': '', 'firmware': '', 'activity': 'No entry in the history file for this code',
                            'options': '', 'reason': '', 'requested': '', 'volumes': volumes_text(items),
                            'status': '', 'reboot_reason': '', 'other': '',
                            'notes': 'format lines of the extra history file whose code is not in the history file', 'line': '',
                            'source': extra_label or source_label, 'extra_file': extra_label, 'entry': None})
    return records


def rows_for(entries, extra, source_label, extra_label=''):
    """``records_for`` as tuples in the order of ROW_KEYS (the columns of the bug report artifact)."""
    return [tuple(record[key] for key in ROW_KEYS) for record in records_for(entries, extra, source_label, extra_label)]


def records_from_texts(history_text, extra_text, source_label, extra_label='', warn=None, orphans=True):
    """``records_for`` on the texts of a history file and (or None) its extra file; ``warn`` receives warning texts."""
    entries, warnings = parse_history(history_text)
    extra = None
    if extra_text is not None:
        extra, extra_warnings = parse_extra_history(extra_text)
        warnings += ['extra history: ' + text for text in extra_warnings]
    if warn is not None:
        for text in warnings:
            warn(text)
    return records_for(entries, extra, source_label, extra_label, orphans)


def records_from_files(files, warn=None):
    """Records for several recovery files at once.

    ``files`` is a list of ``(folder, name, label, text)``: the folder keys the files that sit together, ``name`` is the
    file name (``history``, ``last_history``, ``extra_history`` ...), ``label`` is what the Source File column shows and
    ``text`` is the decoded content. Each history file is read with the extra file of its folder (``EXTRA_FOR``). The codes
    of an extra file that no history file next to it names get one record each, once per extra file, however many history
    files share it. ``warn`` receives ``(label, text)`` for each warning.
    """
    index = {}
    for folder, name, label, text in files:
        index.setdefault((folder, name), (label, text))
    records = []
    codes_of = {}          # extra file key -> codes of the entries of the history files that use it
    done = set()
    for folder, name, label, text in files:
        if name not in HISTORY_NAMES or (folder, name) in done:
            continue
        done.add((folder, name))
        extra_key = (folder, EXTRA_FOR[name])
        extra_label, extra_text = index.get(extra_key, ('', None))

        def tell(text_, label_=label):
            if warn is not None:
                warn(label_, text_)
        found = records_from_texts(text, extra_text, label, extra_label, tell, orphans=False)
        records += found
        if extra_text is not None:
            codes_of.setdefault(extra_key, set()).update(record['code'] for record in found)
    for folder, name, label, text in files:
        if name not in EXTRA_NAMES or (folder, name) in done:
            continue
        done.add((folder, name))
        extra, extra_warnings = parse_extra_history(text)
        if warn is not None and (folder, name) not in codes_of:
            for item in extra_warnings:
                warn(label, 'extra history: ' + item)
        records += orphan_records(extra, codes_of.get((folder, name), set()), label, label)
    return records


def rows_from_files(files, warn=None):
    """``records_from_files`` as tuples in the order of ROW_KEYS (the columns of the bug report artifact)."""
    return [tuple(record[key] for key in ROW_KEYS) for record in records_from_files(files, warn)]
