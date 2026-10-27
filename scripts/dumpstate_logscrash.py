"""Readers for the log, crash, reset and vendor sections of an Android bug report text.

These classes plug into the single pass of ``scripts.dumpstate_reader``: each one receives the
lines of one section while the text is read once, keeps a bounded table on the report, and does
not judge what it keeps. Nothing here depends on the rest of ALEAPP, so the parsers can be tested
on their own.

Sections read:

* SYSTEM LOG, SYSTEM LOG AFTER DONE and EVENT LOG: logcat in ``-v threadtime -v uid`` form;
* KERNEL LOG and LAST KMSG: kernel messages with a seconds-since-boot stamp;
* VM TRACES JUST NOW, VM TRACES AT LAST ANR and HISTORICAL ANR: thread dumps (the same dump is
  read from the ``anr_*`` files inside a bug report zip by ``read_trace_text``);
* ``DUMP OF SERVICE dropbox`` and the DROPBOX SYSTEM ... CRASHES command sections;
* AP RESET INFO EXTEND, POWER OFF RESET REASON and POWER OFF RESET REASON BACKUP (Samsung);
* a fixed list of Samsung vendor services that two of the five tested reports print.

The tables hold plain tuples (or lists, where a later line completes a row) and every table stops
at ``MAX_ROWS`` rows with one warning on the report; a message longer than ``MESSAGE_CHARS``
characters is cut. The module has to be imported after ``scripts.dumpstate_reader`` has started
loading (``scripts.dumpstate_reader`` imports it near its end).
"""
import re
import sys
from datetime import timedelta, timezone

from scripts import dumpstate_reader as reader
from scripts.dumpstate_reader import MAX_ROWS, SectionReader, parse_wall_time, tidy, to_int

ATTRIBUTE = 'logscrash'
MESSAGE_CHARS = 2000
DETAIL_CHARS = 400
FRAME_CHARS = 300
VENDOR_LINE_CHARS = 400
VENDOR_MAX_LINES = 20000
MAX_REPORTED_FRAMES = 3

NOTE_PRE_2009 = 'time before 2009: no UTC value'
NOTE_MASKED_YEAR = 'year masked in the report: no UTC value'
NOTE_NO_YEAR = 'printed without a year'


class Tables:
    """The rows of this module's sections for one report."""

    def __init__(self):
        self.system_log = []       # (section, time, uid, pid, tid, level, tag, message, buffer, line)
        self.event_log = []        # same shape
        self.kernel_lines = []     # (section, seconds, level, context, message, line)
        self.anr_threads = []      # see TraceParser.finish_thread
        self.dropbox_entries = []  # lists, see DropboxServiceReader and DropboxPrintReader
        self.reset_events = []     # lists, see ResetReader
        self.vendor_lines = []     # (service, indent, time text, text, line)
        self.cut_sections = set()  # command sections in which the platform printed a "timed out" line
        self.truncated = set()
        self.minute_cache = {}
        self.dropbox_totals = []   # (section, "Drop box contents" text, "Max entries" text)
        self.vendor_counts = {}    # service -> lines kept
        self.vendor_blobs = {}     # service -> encoded blob lines left out
        self.unparsed = {}         # section -> non-blank lines that are not in logcat form


def tables(report):
    """The :class:`Tables` of a report (made on first use)."""
    found = getattr(report, ATTRIBUTE, None)
    if found is None:
        found = Tables()
        setattr(report, ATTRIBUTE, found)
    return found


def warn_full(report, name, limit):
    """Say once on the report that table ``name`` stopped at ``limit`` rows."""
    store = tables(report)
    if name not in store.truncated:
        store.truncated.add(name)
        report.warn('%s: more than %d rows, the rest were not kept' % (name, limit))


def add_row(report, name, row, limit=None):
    """Append to a table of this module unless it holds MAX_ROWS rows (one warning on the report when it is full)."""
    limit = MAX_ROWS if limit is None else limit
    rows = getattr(tables(report), name)
    if len(rows) >= limit:
        warn_full(report, name, limit)
        return False
    rows.append(row)
    return True


def note_cut(report, section_name, text):
    """Remember that the platform printed its time limit line inside a command section."""
    if text.startswith('*** command ') and ' timed out' in text:
        store = tables(report)
        if section_name not in store.cut_sections:
            store.cut_sections.add(section_name)
            report.warn('%s: the command was stopped by a time limit, the rows may be partial' % section_name)
        return True
    return False


# ---------------------------------------------------------------------------------------------
# Times
# ---------------------------------------------------------------------------------------------
_OFFSET_TAIL = re.compile(r'\s*(?:([+-])(\d\d):?(\d\d)|Z)$')


def stamp_utc(report, text):
    """``(UTC datetime or None, note)`` for ``YYYY-MM-DD HH:MM:SS[.fff]`` with or without a trailing ``+HHMM`` offset.

    With an offset the UTC value is exact; without one the report's own zone is used.
    """
    value = str(text).strip()
    if not value:
        return None, ''
    offset = None
    tail = _OFFSET_TAIL.search(value)
    if tail:
        value = value[:tail.start()]
        if tail.group(1):
            minutes = int(tail.group(2)) * 60 + int(tail.group(3))
            offset = timedelta(minutes=-minutes if tail.group(1) == '-' else minutes)
        else:
            offset = timedelta(0)
    naive = parse_wall_time(value)
    if naive is None:
        return None, reader.NOTE_NOT_A_TIME
    if naive.year < 2009:
        return None, NOTE_PRE_2009
    if offset is not None:
        return (naive - offset).replace(tzinfo=timezone.utc), ''
    if not report.clock.known:
        return None, reader.NOTE_NO_ZONE
    moment = report.clock.to_utc(value)
    return moment, ('' if moment is not None else reader.NOTE_NONEXISTENT)


def logcat_utc(report, text):
    """UTC datetime or None for a logcat time ``MM-DD HH:MM:SS.mmm`` (the year is inferred from the report time).

    The year is not printed: it is the latest year, the one of the report time or the one before, that does not
    put the line more than a day after the report time. A time printed with a year (``-v year``) is converted as is.
    """
    if len(text) < 18:
        return None
    if text[4] == '-':
        moment, _note = stamp_utc(report, text)
        return moment
    store = tables(report)
    key = text[:11]
    base = store.minute_cache.get(key)
    if base is None:
        _full, moment = report.setting_change_time(key + ':00.000')
        base = moment if moment is not None else False
        store.minute_cache[key] = base
    if base is False:
        return None
    try:
        return base + timedelta(seconds=int(text[12:14]), microseconds=int(text[15:].ljust(6, '0')[:6]))
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------
# Logcat
# ---------------------------------------------------------------------------------------------
# MM-DD HH:MM:SS.mmm UID PID TID L tag: message  (-v threadtime -v uid), with the year when -v year was used
_LOGCAT_UID = re.compile(r'^((?:\d{4}-)?\d\d-\d\d \d\d:\d\d:\d\d\.\d{3,6}) +(\S+) +(\d+) +(\d+) ([VDIWEFS]) (.*)$')
# the same without the uid column (-v threadtime)
_LOGCAT_PLAIN = re.compile(r'^((?:\d{4}-)?\d\d-\d\d \d\d:\d\d:\d\d\.\d{3,6}) +(\d+) +(\d+) ([VDIWEFS]) (.*)$')


def split_tag(rest):
    """``(tag, message)`` from ``tag    : message`` (the platform pads a short tag to eight characters)."""
    cut = rest.find(': ')
    if cut >= 0:
        return rest[:cut].rstrip(), rest[cut + 2:]
    if rest.endswith(':'):
        return rest[:-1].rstrip(), ''
    return '', rest


def parse_logcat_line(text):
    """``(time, uid, pid, tid, level, tag, message)`` of a logcat line, or None when the line is not one."""
    found = _LOGCAT_UID.match(text)
    if found:
        stamp, uid, pid, tid, level, rest = found.groups()
    else:
        found = _LOGCAT_PLAIN.match(text)
        if not found:
            return None
        stamp, pid, tid, level, rest = found.groups()
        uid = ''
    tag, message = split_tag(rest)
    return stamp, uid, int(pid), int(tid), level, tag, message


class LogcatReader(SectionReader):
    """Lines of a logcat section: one row per line in logcat form. Other lines are counted, not kept."""
    kind = 'command'
    table = ''

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.rows = getattr(tables(report), self.table)
        self.buffer = ''
        self.full = False

    def feed(self, line_no, text):
        if self.full:
            return
        parsed = parse_logcat_line(text)
        if parsed is not None:
            if len(self.rows) >= MAX_ROWS:
                self.full = True
                warn_full(self.report, self.table, MAX_ROWS)
                return
            stamp, uid, pid, tid, level, tag, message = parsed
            self.rows.append((self.name, stamp, sys.intern(uid), pid, tid, level, sys.intern(tidy(tag)),
                              tidy(message)[:MESSAGE_CHARS], self.buffer, line_no))
        elif text.startswith('--------- beginning of '):
            self.buffer = text[len('--------- beginning of '):].strip()
        elif not note_cut(self.report, self.name, text) and text.strip():
            store = tables(self.report)
            store.unparsed[self.name] = store.unparsed.get(self.name, 0) + 1


class SystemLogReader(LogcatReader):
    name = 'SYSTEM LOG'
    table = 'system_log'


class SystemLogAfterDoneReader(LogcatReader):
    name = 'SYSTEM LOG AFTER DONE'
    table = 'system_log'


class EventLogReader(LogcatReader):
    name = 'EVENT LOG'
    table = 'event_log'


# ---------------------------------------------------------------------------------------------
# Kernel log
# ---------------------------------------------------------------------------------------------
# <6>[  123.456789][T123] message   |   [  123.456789] c0 message   |   [  0.78]  [ 2:  kworker/u16:2:   86] message
_KMSG = re.compile(r'^(?:<(\d+)>)?\[\s*(\d+\.\d+)\]\s?(.*)$')
_KMSG_CONTEXT = re.compile(r'^\s*(?:\[\s*([TC]\d+)\]|\[\s*(\d+:[^\]]*)\]|(c\d+)(?=\s))\s?(.*)$')


def parse_kernel_line(text):
    """``(seconds, level, context, message)`` of a kernel message line; the first three are '' when the stamp is missing."""
    found = _KMSG.match(text)
    if not found:
        return '', '', '', text
    level, seconds, rest = found.groups()
    context = ''
    inner = _KMSG_CONTEXT.match(rest)
    if inner:
        context = inner.group(1) or inner.group(2) or inner.group(3)
        rest = inner.group(4)
    return seconds, level or '', context.strip(), rest


class KernelReader(SectionReader):
    """The lines of KERNEL LOG (dmesg) or LAST KMSG, one row per non-blank line."""
    kind = 'command'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.full = False

    def feed(self, line_no, text):
        text = text.rstrip()
        if self.full or not text:
            return
        if note_cut(self.report, self.name, text) or (text.startswith("Skipping '") and text.endswith(' on user build.')):
            return
        seconds, level, context, message = parse_kernel_line(text)
        if not add_row(self.report, 'kernel_lines', (self.name, seconds, level, tidy(context),
                                                      tidy(message)[:MESSAGE_CHARS], line_no)):
            self.full = True


class KernelLogReader(KernelReader):
    name = 'KERNEL LOG'


class LastKmsgReader(KernelReader):
    name = 'LAST KMSG'


# ---------------------------------------------------------------------------------------------
# Thread dumps (VM TRACES, ANR files)
# ---------------------------------------------------------------------------------------------
_DUMP_HEAD = re.compile(r'^----- (?:[A-Za-z ]+: )?pid (\d+) at (.+?) -----$')
_THREAD_HEAD = re.compile(r'^"(.*)" (.*)$')


class TraceParser:
    """Reads a thread dump (ART ``DALVIK THREADS`` and native thread lists) and emits one row per thread.

    Row: ``(source, pid, process, dump time, subject, thread, daemon, priority, tid, state, sys tid, nice, cgroup,
    os state, utm, stm, core, top frame, frames, line)``. ``emit`` receives the tuple.
    """

    def __init__(self, source, emit):
        self.source = source
        self.emit = emit
        self.pid = ''
        self.stamp = ''
        self.process = ''
        self.subject = ''
        self.in_wchan = False
        self.thread = None

    def _finish_thread(self):
        thread = self.thread
        self.thread = None
        if thread is not None:
            self.emit((self.source, self.pid, self.process, self.stamp, self.subject, thread['name'], thread['daemon'],
                       thread['prio'], thread['tid'], thread['state'], thread['sys_tid'], thread['nice'], thread['cgroup'],
                       thread['os_state'], thread['utm'], thread['stm'], thread['core'], thread['top'], thread['frames'],
                       thread['line']))

    def feed(self, line_no, text):
        text = text.rstrip()
        if text.startswith('----- '):
            self._finish_thread()
            head = _DUMP_HEAD.match(text)
            if head:
                self.in_wchan = 'Waiting Channels' in text
                if not self.in_wchan:
                    self.pid, self.stamp, self.process = head.group(1), head.group(2), ''
            else:
                self.in_wchan = False
            return
        if self.in_wchan:
            return
        if text.startswith('"'):
            self._finish_thread()
            self._start_thread(line_no, text)
            return
        thread = self.thread
        if thread is None:
            if text.startswith('Cmd line: ') and not self.process:
                self.process = tidy(text[len('Cmd line: '):].strip())[:DETAIL_CHARS]
            elif text.startswith('Subject: ') and not self.subject:
                self.subject = tidy(text[len('Subject: '):].strip())[:DETAIL_CHARS]
            return
        body = text.strip()
        if body.startswith('| '):
            self._attributes(thread, body[2:])
        elif body.startswith(('at ', 'native: #', '#')):
            thread['frames'] += 1
            if not thread['top']:
                thread['top'] = tidy(body)[:FRAME_CHARS]

    def _start_thread(self, line_no, text):
        found = _THREAD_HEAD.match(text)
        if not found:
            return
        name, rest = found.groups()
        tokens = rest.split()
        values = {token.split('=', 1)[0]: token.split('=', 1)[1] for token in tokens if '=' in token}
        state = ' '.join(token for token in tokens if '=' not in token and token != 'daemon')
        self.thread = {'name': tidy(name)[:DETAIL_CHARS], 'daemon': 'daemon' in tokens[:1], 'prio': to_int(values.get('prio')),
                       'tid': to_int(values.get('tid')), 'state': tidy(state)[:80], 'sys_tid': to_int(values.get('sysTid')),
                       'nice': None, 'cgroup': '', 'os_state': '', 'utm': None, 'stm': None, 'core': None, 'top': '',
                       'frames': 0, 'line': line_no}

    @staticmethod
    def _attributes(thread, body):
        values = reader.key_values(body)
        if 'sysTid' in values and thread['sys_tid'] is None:
            thread['sys_tid'] = to_int(values.get('sysTid'))
        if 'sysTid' in values:
            thread['nice'] = to_int(values.get('nice'))
            thread['cgroup'] = tidy(values.get('cgrp', ''))[:40]
        if 'state' in values:
            thread['os_state'] = tidy(values.get('state', ''))[:20]
            thread['utm'], thread['stm'] = to_int(values.get('utm')), to_int(values.get('stm'))
            thread['core'] = to_int(values.get('core'))

    def finish(self):
        self._finish_thread()


class TraceReader(SectionReader):
    """A VM TRACES or HISTORICAL ANR command section."""
    kind = 'command'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.full = False
        self.parser = TraceParser(self.name, self._emit)

    def _emit(self, row):
        if not self.full and not add_row(self.report, 'anr_threads', row):
            self.full = True

    def feed(self, line_no, text):
        if not self.full:
            if note_cut(self.report, self.name, text):
                self.parser.finish()
                return
            self.parser.feed(line_no, text)

    def finish(self):
        self.parser.finish()


class VmTracesJustNowReader(TraceReader):
    name = 'VM TRACES JUST NOW'


class VmTracesAtLastAnrReader(TraceReader):
    name = 'VM TRACES AT LAST ANR'


class HistoricalAnrReader(TraceReader):
    name = 'HISTORICAL ANR'


def read_trace_text(source, lines, limit=MAX_ROWS):
    """Thread rows of a trace file: ``lines`` yields the text of each line. At most ``limit`` rows are kept."""
    rows = []

    def emit(row):
        if len(rows) < limit:
            rows.append(row)
    parser = TraceParser(source, emit)
    line_no = 0
    for text in lines:
        line_no += 1
        if len(rows) >= limit:
            break
        parser.feed(line_no, text)
    parser.finish()
    return rows, len(rows) >= limit


# ---------------------------------------------------------------------------------------------
# Dropbox
# ---------------------------------------------------------------------------------------------
_DROP_ENTRY = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (\S+) \((.*)\)\s*$')
_DROP_KIND = re.compile(r'^(.*?)(?:, (\d+) bytes)?$')
_DROP_HEADERS = {'Process': 'process', 'PID': 'pid', 'UID': 'uid', 'Foreground': 'foreground', 'Subject': 'subject'}
_DROP_SKIP = ('Service host process', 'Threads in use', 'Client PIDs', 'Unknown argument')
DROP_DIVIDER = '=' * 20


def drop_entry_row(section, stamp, tag, kind_text, line_no):
    """A dropbox entry row (a list that later lines complete)."""
    found = _DROP_KIND.match(kind_text)
    kind = (found.group(1) if found else kind_text).strip()
    size = int(found.group(2)) if found and found.group(2) else None
    return [section, stamp, tidy(tag), tidy(kind), size, '', '', '', '', '', '', '', '', line_no]
    # indexes: 0 section 1 time 2 tag 3 content 4 bytes 5 process 6 pid 7 uid 8 packages 9 foreground 10 subject
    #          11 first body line 12 preview 13 line


class DropboxServiceReader(SectionReader):
    """``dumpsys dropbox``: one line per entry (time, tag, content type and size) and an indented preview."""
    kind = 'service'
    name = 'dropbox'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.last = None
        self.full = False
        self.totals = ['', '']

    def feed(self, line_no, text):
        if self.full:
            return
        body = text.strip()
        if not body or body.startswith(_DROP_SKIP):
            return
        if text[:1] != ' ':
            found = _DROP_ENTRY.match(text.rstrip())
            if found:
                row = drop_entry_row('DUMP OF SERVICE dropbox', found.group(1), found.group(2), found.group(3), line_no)
                self.last = row if add_row(self.report, 'dropbox_entries', row) else None
                self.full = self.last is None
            elif body.startswith('Drop box contents:'):
                self.totals[0] = body
            elif body.startswith('Max entries:'):
                self.totals[1] = body
            return
        if self.last is not None:
            preview = (self.last[12] + ' ' + tidy(body)).strip()
            self.last[12] = preview[:DETAIL_CHARS]

    def finish(self):
        tables(self.report).dropbox_totals.append((self.name, self.totals[0], self.totals[1]))


class DropboxPrintReader(SectionReader):
    """``dumpsys dropbox -p <tag>``: the entries of one tag, each after a divider line, with its header lines and body."""
    kind = 'command'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.row = None
        self.phase = ''          # 'headers' after the entry line, 'body' after the blank line that ends them
        self.full = False
        self.totals = ['', '']

    def feed(self, line_no, text):
        if self.full:
            return
        stripped = text.rstrip()
        if stripped.startswith(DROP_DIVIDER) and not stripped.strip('='):
            self.row = None
            self.phase = 'divider'
            return
        if self.phase == 'divider':
            found = _DROP_ENTRY.match(stripped)
            if found:
                self.row = drop_entry_row(self.name, found.group(1), found.group(2), found.group(3), line_no)
                if not add_row(self.report, 'dropbox_entries', self.row):
                    self.full = True
                    return
                self.phase = 'headers'
            return
        if self.row is None:
            if stripped.startswith('Drop box contents:'):
                self.totals[0] = stripped
            elif stripped.startswith('Max entries:'):
                self.totals[1] = stripped
            return
        if self.phase == 'headers':
            if not stripped:
                self.phase = 'body'
                return
            key, separator, value = stripped.partition(': ')
            if not separator:
                key, separator, value = stripped.partition(':')
            if key == 'Package':
                self.row[8] = (self.row[8] + '; ' + tidy(value.strip())) if self.row[8] else tidy(value.strip())
            elif key in _DROP_HEADERS:
                slot = {'process': 5, 'pid': 6, 'uid': 7, 'foreground': 9, 'subject': 10}[_DROP_HEADERS[key]]
                self.row[slot] = tidy(value.strip())[:DETAIL_CHARS]
            elif not separator:
                self.row[11] = tidy(stripped)[:DETAIL_CHARS]      # no header block: the line is the body
                self.phase = 'done'
        elif self.phase == 'body' and stripped:
            self.row[11] = tidy(stripped)[:DETAIL_CHARS]
            self.phase = 'done'

    def finish(self):
        tables(self.report).dropbox_totals.append((self.name, self.totals[0], self.totals[1]))


class DropboxServerCrashesReader(DropboxPrintReader):
    name = 'DROPBOX SYSTEM SERVER CRASHES'


class DropboxAppCrashesReader(DropboxPrintReader):
    name = 'DROPBOX SYSTEM APP CRASHES'


class DropboxWatchdogReader(DropboxPrintReader):
    name = 'DROPBOX SYSTEM WATCHDOG CRASHES'


# ---------------------------------------------------------------------------------------------
# Reset reasons (Samsung)
# ---------------------------------------------------------------------------------------------
_RESET_RECORD = re.compile(r'^(\d\d)/(\d\d)/(\d\d) (\d\d:\d\d:\d\d)$')
_RESET_EVENT_TIME = re.compile(r'^(?:\d\d:\d\d:\d\d +)?(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(?:[+-]\d{4})?)$')


class ResetReader(SectionReader):
    """The reset history files: ``time | EVENT | flag | detail`` lines and (in the power off files) reset records.

    Row (a list): section, time as printed, form, event, flag, detail, caller frames, line. Form is ``event line`` for a
    pipe-separated line and ``record`` for a ``yy/mm/dd HH:MM:SS`` header with its ``reason :`` line.
    """
    kind = 'command'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.record = None
        self.frames = []
        self.stack = False
        self.full = False

    def _close_record(self):
        record = self.record
        if record is not None and self.frames:
            after = 0
            for position, frame in enumerate(self.frames):
                if 'ShutdownThread.' in frame:
                    after = position + 1
            record[6] = ' | '.join(self.frames[after:after + MAX_REPORTED_FRAMES])
        self.record = None
        self.frames = []
        self.stack = False

    def feed(self, line_no, text):
        if self.full:
            return
        stripped = text.strip()
        if not stripped:
            return
        found = _RESET_RECORD.match(stripped)
        if found:
            self._close_record()
            self.record = [self.name, stripped, 'record', '', '', '', '', line_no]
            self.full = not add_row(self.report, 'reset_events', self.record)
            return
        stamp = _RESET_EVENT_TIME.match(stripped.split('|', 1)[0].strip()) if '|' in stripped else None
        if stamp:
            self._close_record()
            parts = stripped.split('|')
            row = [self.name, stamp.group(1), 'event line', tidy(parts[1].strip()) if len(parts) > 1 else '',
                   tidy(parts[2].strip()) if len(parts) > 2 else '', tidy('|'.join(parts[3:]).strip())[:DETAIL_CHARS],
                   '', line_no]
            self.full = not add_row(self.report, 'reset_events', row)
            return
        record = self.record
        if record is None:
            return
        if stripped.startswith('reason') and ':' in stripped and not record[3]:
            record[3] = 'reason'
            record[5] = tidy(stripped.partition(':')[2].strip())[:DETAIL_CHARS]
        elif stripped.startswith('java.lang.') or stripped.startswith('Caused by'):
            self.stack = True
        elif self.stack and stripped.startswith('at '):
            if len(self.frames) < 40:
                self.frames.append(tidy(stripped[3:])[:FRAME_CHARS])

    def finish(self):
        self._close_record()


class ApResetInfoReader(ResetReader):
    name = 'AP RESET INFO EXTEND'


class PowerOffResetReader(ResetReader):
    name = 'POWER OFF RESET REASON'


class PowerOffResetBackupReader(ResetReader):
    name = 'POWER OFF RESET REASON BACKUP'


def record_time_text(text):
    """``YYYY-MM-DD HH:MM:SS`` for a ``yy/mm/dd HH:MM:SS`` record header (two digit years are read as 20yy), or ''."""
    found = _RESET_RECORD.match(text.strip())
    return '20%s-%s-%s %s' % found.groups() if found else ''


# ---------------------------------------------------------------------------------------------
# Vendor services
# ---------------------------------------------------------------------------------------------
# Samsung services that two of the five tested reports (a Samsung A-series and a Samsung S-series phone, Android 16) print
# with an event history or a policy state. Counters, statistics and parameter lists are not read. knoxguard_service and
# knoxcustom are not in this list: the Security artifacts "knoxguard_service Log" and "knoxcustom State" read them, so each
# fact appears once.
VENDOR_SERVICES = ('SveService', 'secims', 'sec_location', 'sem_wifi', 'nfc SamsungExtension',
                   'advanced_protection', 'application_policy', 'enterprise_policy', 'persona',
                   'motion_recognition', 'PkgPredictorService')
_VENDOR_SKIP = ('Service host process', 'Threads in use', 'Client PIDs', 'Unknown argument')
_VENDOR_TIME = re.compile(
    r'(\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d+)?)'
    r'|(\d{4}/\d\d/\d\d \d\d:\d\d:\d\d(?:[.:]\d+)?)'
    r'|(\d\d/\d\d/\d{4} \d\d:\d\d:\d\d(?:[.:]\d+)?)'
    r'|(\d\d/\d\d/\*\d{3} \d\d:\d\d:\d\d(?:[.:]\d+)?)'
    r'|((?<![\d/-])\d\d-\d\d \d\d:\d\d:\d\d\.\d{3})')
_BLOB = re.compile(r'^[A-Za-z0-9+/=]{60,}$')


def vendor_time(text):
    """The first time printed in the first 80 characters of a line, as printed ('' when there is none)."""
    found = _VENDOR_TIME.search(text[:80])
    return found.group(0) if found else ''


def vendor_time_to_wall(text):
    """``(YYYY-MM-DD HH:MM:SS[.fff] or '', note)`` for a time returned by :func:`vendor_time`."""
    if not text:
        return '', ''
    if '*' in text:
        return '', NOTE_MASKED_YEAR
    if len(text) == 18 and text[2] == '-':
        return '', NOTE_NO_YEAR
    value = text.replace('T', ' ')
    if value[4:5] == '/':
        value = value.replace('/', '-')
    elif value[2:3] == '/':
        value = '%s-%s-%s%s' % (value[6:10], value[0:2], value[3:5], value[10:])
    if len(value) > 19 and value[19] == ':':
        value = value[:19] + '.' + value[20:]
    return value, ''


class VendorLinesReader(SectionReader):
    """Every non-blank line of one vendor service, with its indent and the first time printed in it."""
    kind = 'service'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.lines = 0
        self.full = False

    def feed(self, line_no, text):
        if self.full:
            return
        body = text.strip()
        if not body or body.startswith(_VENDOR_SKIP) or not body.strip('-') or (
                body.startswith('---------') and ' was the duration of ' in body):
            return
        store = tables(self.report)
        if _BLOB.match(body):
            store.vendor_blobs[self.name] = store.vendor_blobs.get(self.name, 0) + 1
            return
        if self.lines >= VENDOR_MAX_LINES:
            self.full = True
            self.report.warn('%s: more than %d lines, the rest were not kept' % (self.name, VENDOR_MAX_LINES))
            return
        self.lines += 1
        store.vendor_counts[self.name] = self.lines
        indent = len(text) - len(text.lstrip(' '))
        add_row(self.report, 'vendor_lines', (self.name, indent, vendor_time(text), tidy(body)[:VENDOR_LINE_CHARS], line_no))


def _vendor_class(service):
    return type('Vendor' + re.sub(r'\W', '', service) + 'Reader', (VendorLinesReader,), {'name': service})


VENDOR_READERS = [_vendor_class(service) for service in VENDOR_SERVICES]

READERS = [SystemLogReader, SystemLogAfterDoneReader, EventLogReader, KernelLogReader, LastKmsgReader,
           VmTracesJustNowReader, VmTracesAtLastAnrReader, HistoricalAnrReader, DropboxServiceReader,
           DropboxServerCrashesReader, DropboxAppCrashesReader, DropboxWatchdogReader, ApResetInfoReader,
           PowerOffResetReader, PowerOffResetBackupReader] + VENDOR_READERS
READ_BY = {
    ('command', 'SYSTEM LOG'): 'System Log',
    ('command', 'SYSTEM LOG AFTER DONE'): 'System Log',
    ('command', 'EVENT LOG'): 'Event Log',
    ('command', 'KERNEL LOG'): 'Kernel Log',
    ('command', 'LAST KMSG'): 'Kernel Log',
    ('command', 'VM TRACES JUST NOW'): 'ANR Trace Threads',
    ('command', 'VM TRACES AT LAST ANR'): 'ANR Trace Threads',
    ('command', 'HISTORICAL ANR'): 'ANR Trace Threads',
    ('service', 'dropbox'): 'Dropbox Entries',
    ('command', 'DROPBOX SYSTEM SERVER CRASHES'): 'Dropbox Entries',
    ('command', 'DROPBOX SYSTEM APP CRASHES'): 'Dropbox Entries',
    ('command', 'DROPBOX SYSTEM WATCHDOG CRASHES'): 'Dropbox Entries',
    ('command', 'AP RESET INFO EXTEND'): 'Reset Reasons',
    ('command', 'POWER OFF RESET REASON'): 'Reset Reasons',
    ('command', 'POWER OFF RESET REASON BACKUP'): 'Reset Reasons',
}
READ_BY.update({('service', service): 'Vendor Service Lines' for service in VENDOR_SERVICES})


def register():
    """Add the readers and the section index entries to the pass of ``dumpstate_reader`` (once, in any import order)."""
    for reader_class in READERS:
        if reader_class not in reader.READERS:
            reader.READERS.append(reader_class)
    for key, value in READ_BY.items():
        reader.READ_BY.setdefault(key, value)


register()
