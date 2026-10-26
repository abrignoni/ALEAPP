"""Reader for the main text of an Android bug report (the dumpstate file).

An Android bug report is a zip (``adb bugreport``, or the zip the Shell app keeps on the
device) whose main text, ``dumpstate.txt`` or ``bugreport-<device>-<build>-<date>.txt``,
is 30 to 250 MB of command output and ``dumpsys`` service dumps. This module reads that
text once, in one pass, and keeps only the few sections that the bug report artifacts
present. It never writes anything and it does not judge what it reads.

Layout of the text, as far as this reader relies on it::

    ========================================================
    == dumpstate: 2026-10-25 06:43:00          <- report time, device wall clock
    ========================================================
    Build: ...                                 <- header lines ("Key: value")
    ------ SYSTEM PROPERTIES (getprop) ------  <- a command section
    [persist.sys.timezone]: [Africa/Accra]
    ------ 0.1s was the duration of 'SYSTEM PROPERTIES' ------
    DUMP OF SERVICE package:                   <- a dumpsys service section
    ...
    --------- 0.3s was the duration of dumpsys package, ending at: 2026-10-25 06:43:10

A section ends at its duration line when one is printed, and otherwise at the next
section header. Line numbers are counted on ``\\n`` only (a lone carriage return or form
feed inside a line does not start a new line), so they match what a text editor shows.

Nothing here depends on the rest of ALEAPP, so the functions can be tested on their own.
Times in the text are device wall-clock times without a zone: they are converted to UTC
with the zone the report itself records (``persist.sys.timezone``) and are left without a
UTC value when the report does not record one.
"""
import collections
import io
import os
import re
import zipfile
import zlib
from datetime import datetime, timezone

import pytz

BANNER = b'== dumpstate:'
HEAD_BYTES = 8192
MAX_LINE_CHARS = 65536
MAX_LINE_BYTES = 1 << 20
# Rows kept per table. A real report holds up to a few thousand rows of each kind; the cap only
# bounds memory for a damaged or hostile text and is reported when it is reached.
MAX_ROWS = 500000
CACHE_SIZE = 6

# Errors that reading a damaged archive or text can raise. Anything else is a bug and propagates.
READ_ERRORS = (OSError, EOFError, zipfile.BadZipFile, zlib.error, RuntimeError, NotImplementedError,
               ValueError, OverflowError)

# The platform's "no time" value as it is printed in zone-less wall clock text.
UNSET_WALL_TIMES = frozenset({'1970-01-01 00:00:00', '1969-12-31 23:59:59'})
NOTE_UNSET = 'time not set on the device (shown as printed)'
NOTE_NO_ZONE = 'no time zone in the report: no UTC value'
NOTE_NOT_A_TIME = 'time text not recognised: no UTC value'
NOTE_NONEXISTENT = 'time falls in a clock change of the time zone: no UTC value'

HEADER_KEYS = ('Build', 'Build fingerprint', 'Bootloader', 'Radio', 'Network', 'Module Metadata version',
               'Android SDK version', 'SDK extensions', 'Kernel', 'Uptime', 'Bugreport format version')
# Properties that are reported. Serial numbers, IMEIs, advertising and account identifiers are not
# in this list on purpose; neither is the kernel command line, which can carry a serial number.
PROPERTY_ALLOW = (
    'ro.product.manufacturer', 'ro.product.brand', 'ro.product.model', 'ro.product.device', 'ro.product.name',
    'ro.build.fingerprint', 'ro.build.version.release', 'ro.build.version.sdk', 'ro.build.version.security_patch',
    'ro.build.version.incremental', 'ro.build.type', 'ro.build.tags', 'ro.build.date.utc', 'ro.debuggable',
    'ro.secure', 'ro.adb.secure', 'ro.boot.verifiedbootstate', 'ro.boot.flash.locked', 'ro.boot.vbmeta.device_state',
    'ro.crypto.state', 'ro.crypto.type', 'persist.sys.timezone', 'ro.product.locale', 'persist.sys.locale',
    'ro.build.characteristics', 'ro.hardware', 'ro.board.platform', 'sys.usb.config', 'persist.sys.usb.config',
    'service.adb.root', 'ro.build.version.codename', 'ro.build.version.base_os', 'ro.vendor.build.fingerprint',
    'ro.build.display.id', 'ro.boot.hardware',
)
TIMEZONE_PROPERTY = 'persist.sys.timezone'

# Lines that can open or close a section start with one of these bytes: '-' ('------ ', '--------- '),
# 'D' ('DUMP OF SERVICE '), '=' ('== ') or '*' ('*** SERVICE '). Every other line is only decoded
# when a section that is being read is open.
_BOUNDARY_FIRST = frozenset(b'-D=*')

_CONTROL = re.compile('[\x00-\x08\x0b-\x1f\x7f]')

Source = collections.namedtuple('Source', 'path member')
Fact = collections.namedtuple('Fact', 'name value origin line')
PackageRecord = collections.namedtuple(
    'PackageRecord', 'block package app_id_key app_id shared_user version_code version_name min_sdk target_sdk '
                     'code_path flags installer initiating originating package_source users_installed user_states line')
# One printed package time, before it is converted: ``wall`` is the text as printed.
PackageTime = collections.namedtuple('PackageTime', 'package event wall user installer block line resident')


def tidy(value):
    """A text value with control characters (NUL, lone carriage returns, form feeds) shown as a space."""
    if value is None:
        return ''
    return _CONTROL.sub(' ', str(value))


def to_int(text, default=None):
    """Integer value of a printed number (decimal or 0x hex), or ``default``."""
    if text is None:
        return default
    value = str(text).strip().rstrip(',')
    try:
        if value.lower().startswith(('0x', '-0x')):
            return int(value, 16)
        return int(value)
    except ValueError:
        return default


def key_values(text):
    """Split ``a=1 b=two c="x y"`` into a dict. Quoted values keep their spaces; a repeated key keeps its first value."""
    found = {}
    size = len(text)
    pos = 0
    while pos < size:
        while pos < size and text[pos] == ' ':
            pos += 1
        stop = pos
        while stop < size and text[stop] not in ' =':
            stop += 1
        if stop >= size or text[stop] == ' ':
            pos = stop + 1
            continue
        key = text[pos:stop]
        stop += 1
        if stop < size and text[stop] == '"':
            end = text.find('"', stop + 1)
            if end < 0:
                end = size
            value = text[stop + 1:end]
            pos = end + 1
        else:
            end = stop
            while end < size and text[end] != ' ':
                end += 1
            value = text[stop:end]
            pos = end
        if key and key not in found:
            found[key] = value
    return found


# ---------------------------------------------------------------------------------------------
# Times
# ---------------------------------------------------------------------------------------------
def parse_wall_time(text):
    """A naive datetime from ``YYYY-MM-DD HH:MM:SS[.fff]`` (a ``T`` separator also works), or None."""
    value = str(text).strip()
    if len(value) < 19 or value[4] != '-' or value[7] != '-' or value[10] not in ' T' \
            or value[13] != ':' or value[16] != ':':
        return None
    try:
        micro = 0
        if len(value) > 19 and value[19] in '.,':
            digits = ''
            for char in value[20:26]:
                if not char.isdigit():
                    break
                digits += char
            micro = int(digits.ljust(6, '0')) if digits else 0
        return datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]),
                        int(value[11:13]), int(value[14:16]), int(value[17:19]), micro)
    except ValueError:
        return None


class ZoneClock:
    """Converts the device's wall-clock text to UTC with the zone the report records."""

    def __init__(self, zone_name):
        self.name = zone_name or ''
        self._zone = None
        if self.name:
            try:
                self._zone = pytz.timezone(self.name)
            except (pytz.exceptions.UnknownTimeZoneError, ValueError):
                self._zone = None

    @property
    def known(self):
        return self._zone is not None

    def to_utc(self, text):
        """UTC datetime for a printed wall time, or None when the zone is unknown or the text is not a time.

        A wall time that occurs twice (clocks set back) is read with the daylight-saving offset; one that
        does not occur (clocks set forward) gets no value.
        """
        naive = parse_wall_time(text)
        if naive is None or self._zone is None:
            return None
        try:
            local = self._zone.localize(naive, is_dst=None)
        except pytz.exceptions.AmbiguousTimeError:
            local = self._zone.localize(naive, is_dst=True)
        except pytz.exceptions.NonExistentTimeError:
            return None
        return local.astimezone(timezone.utc)


# ---------------------------------------------------------------------------------------------
# Factory image stamps in package times
# ---------------------------------------------------------------------------------------------
# A phone image is built once and flashed onto every unit. The package manager reads the install and
# update time of an app that sits on the read-only system partitions from the image, so one fixed
# value can be printed for hundreds of unrelated packages. That value is a property of the image, not
# the time anybody installed or updated the app. Three tests mark such a value (a package name is
# never used to decide):
#   1. a fixed placeholder: a wall time whose minute is 00, 30 or 45 and second is 00 within 14 hours
#      of 2009-01-01 00:00:00 (the same midnight written for any builder or device zone), or exactly
#      2022-01-01 00:00:00;
#   2. a time shared by at least 20 different packages that sit on the image;
#   3. times that follow each other no more than 2 seconds apart, within 30 seconds in all, shared by
#      at least 20 different packages that sit on the image together (a first scan after a flash).
# A value that passes one test is marked on every row that prints it. A value that passes none (for
# example an update burst of user-installed apps) is never marked.
NOTE_FACTORY_STAMP = 'factory image stamp, not an install time'
STAMP_MIN_PACKAGES = 20
STAMP_BURST_GAP_SECONDS = 2
STAMP_BURST_SPAN_SECONDS = 30
_PLACEHOLDER_CONSTANTS = frozenset({'2022-01-01 00:00:00'})
_PLACEHOLDER_FIRST = datetime(2008, 12, 31, 10, 0, 0)
_PLACEHOLDER_LAST = datetime(2009, 1, 1, 14, 0, 0)
_USER_DATA_PREFIXES = ('/data/', '/mnt/', '/sdcard/', '/storage/')


def normal_wall_text(text):
    """``YYYY-MM-DD HH:MM:SS`` from a printed wall time, or '' when the text is not that shape."""
    value = str(text or '').strip().replace('T', ' ')[:19]
    return value if len(value) == 19 and parse_wall_time(value) is not None else ''


def is_placeholder_time(text):
    """Test 1: a fixed placeholder wall time."""
    value = normal_wall_text(text)
    if not value:
        return False
    if value in _PLACEHOLDER_CONSTANTS:
        return True
    moment = parse_wall_time(value)
    return (_PLACEHOLDER_FIRST <= moment <= _PLACEHOLDER_LAST
            and moment.second == 0 and moment.minute in (0, 30, 45))


def sits_on_image(code_path, hidden_system=False):
    """True for a package from the hidden system block, or one whose code path is outside the user data mounts."""
    if hidden_system:
        return True
    path = str(code_path or '').strip()
    return bool(path) and not path.startswith(_USER_DATA_PREFIXES)


def find_shared_stamps(entries):
    """The set of wall times (tests 2 and 3) that are factory stamps.

    ``entries`` are ``(package, wall_text, on_image)`` for every printed time of one report.
    """
    packages_at = {}
    for package, text, on_image in entries:
        value = normal_wall_text(text)
        if on_image and package and value and parse_wall_time(value).year >= 1980:
            packages_at.setdefault(value, set()).add(package)
    stamps = set()
    chain = []

    def close_chain():
        if not chain:
            return
        members = set()
        for value in chain:
            members |= packages_at[value]
        span = (parse_wall_time(chain[-1]) - parse_wall_time(chain[0])).total_seconds()
        if len(members) >= STAMP_MIN_PACKAGES and span <= STAMP_BURST_SPAN_SECONDS:
            stamps.update(chain)
        else:
            stamps.update(value for value in chain if len(packages_at[value]) >= STAMP_MIN_PACKAGES)
        del chain[:]

    for value in sorted(packages_at):
        if chain and (parse_wall_time(value) - parse_wall_time(chain[-1])).total_seconds() > STAMP_BURST_GAP_SECONDS:
            close_chain()
        chain.append(value)
    close_chain()
    return stamps


# ---------------------------------------------------------------------------------------------
# Finding the report text
# ---------------------------------------------------------------------------------------------
def _has_banner(head):
    return BANNER in head


def _zip_main_member(archive):
    """The name of the main text of an opened bug report zip, or ''."""
    infos = {info.filename: info for info in archive.infolist() if not info.is_dir()}
    if 'main_entry.txt' in infos:
        try:
            with archive.open('main_entry.txt') as handle:
                named = handle.read(4096).decode('utf-8', 'replace').splitlines()
        except READ_ERRORS:
            named = []
        if named and named[0].strip() in infos:
            return named[0].strip()
    top = [name for name in infos if '/' not in name and name.lower().endswith('.txt')]
    for prefix in ('bugreport', 'dumpstate'):
        hits = [name for name in top if name.lower().startswith(prefix)
                and not name.lower().startswith(('dumpstate_log', 'dumpstate_board'))]
        if hits:
            return max(hits, key=lambda name: infos[name].file_size)
    return ''


def find_sources(paths):
    """The bug report texts among ``paths`` (the files a search matched), and a list of notes on the others.

    A path is a source when it is a text whose first bytes carry the ``== dumpstate:`` banner, or a zip whose
    main text does (the zip the Shell app keeps on the device, or one copied from ``adb bugreport``).
    """
    sources = []
    notes = []
    seen = set()
    for path in paths:
        name = os.path.basename(path)
        try:
            if name.lower().endswith('.zip'):
                with zipfile.ZipFile(path) as archive:
                    member = _zip_main_member(archive)
                    head = b''
                    if member:
                        with archive.open(member) as handle:
                            head = handle.read(HEAD_BYTES)
                source = Source(path, member)
            elif os.path.isfile(path):
                with open(path, 'rb') as handle:
                    head = handle.read(HEAD_BYTES)
                source = Source(path, '')
            else:
                continue
        except READ_ERRORS as error:
            notes.append('%s could not be opened as a bug report: %s' % (name, error))
            continue
        if not _has_banner(head):
            notes.append('%s has no dumpstate banner in its first %d bytes and was not read' % (name, HEAD_BYTES))
            continue
        key = (os.path.realpath(path), source.member)
        if key not in seen:
            seen.add(key)
            sources.append(source)
    return sources, notes


def _open_binary(source):
    """A readable binary stream and a close function for a source."""
    if source.member:
        archive = zipfile.ZipFile(source.path)
        stream = io.BufferedReader(archive.open(source.member), buffer_size=1 << 20)

        def close():
            stream.close()
            archive.close()
        return stream, close
    handle = open(source.path, 'rb', buffering=1 << 20)
    return handle, handle.close


def _line_text(raw):
    """Text of one raw line without its line ending (``\n`` or ``\r\n``); a lone ``\r`` stays in the text."""
    if raw.endswith(b'\n'):
        raw = raw[:-1]
        if raw.endswith(b'\r'):
            raw = raw[:-1]
    if len(raw) > MAX_LINE_CHARS:
        raw = raw[:MAX_LINE_CHARS]
    return raw.decode('utf-8', 'replace')


def iter_lines(stream):
    """The lines of a binary stream, split on ``\n`` only, each cut to MAX_LINE_BYTES.

    The rest of a longer line is skipped without being held in memory, so a text with a
    multi-megabyte line, or with no line breaks at all, costs the same as any other.
    """
    while True:
        raw = stream.readline(MAX_LINE_BYTES)
        if not raw:
            return
        if len(raw) == MAX_LINE_BYTES and not raw.endswith(b'\n'):
            while True:
                rest = stream.readline(MAX_LINE_BYTES)
                if not rest or rest.endswith(b'\n'):
                    break
            raw += b'\n'
        yield raw


# ---------------------------------------------------------------------------------------------
# The report and its section readers
# ---------------------------------------------------------------------------------------------
class Report:
    """What one pass over one report text found. Tables are lists of named tuples in the order printed."""

    def __init__(self, source):
        self.source = source
        self.total_lines = 0
        self.warnings = []
        self.timeouts = {}            # service name -> milliseconds of the "DUMP TIMEOUT" marker printed inside it
        self.sections = []            # every preamble, command and service section, in the order printed
        self.sections_seen = set()    # names of the sections that a reader was run on
        self.report_wall = ''         # "== dumpstate:" time as printed
        self.facts = []
        self.properties = {}          # property -> (value, line), for the properties that are reported
        self.packages = []
        self.package_times = []
        self.zone_name = ''
        self.clock = ZoneClock('')
        self.factory_stamps = frozenset()
        self._truncated = set()

    def warn(self, message):
        if len(self.warnings) < 100:
            self.warnings.append(message)

    def add(self, table, row):
        """Append to a table unless it holds MAX_ROWS rows."""
        rows = getattr(self, table)
        if len(rows) >= MAX_ROWS:
            if table not in self._truncated:
                self._truncated.add(table)
                self.warn('%s: more than %d rows, the rest were not kept' % (table, MAX_ROWS))
            return
        rows.append(row)

    def finish(self):
        """Derive what needs the whole text (the zone, the factory stamps) once the pass is done."""
        self.zone_name = self.properties.get(TIMEZONE_PROPERTY, ('', 0))[0].strip()
        self.clock = ZoneClock(self.zone_name)
        if self.zone_name and not self.clock.known:
            self.warn('time zone %r is not known to this tool: no UTC values' % self.zone_name)
        self.factory_stamps = frozenset(find_shared_stamps(
            (t.package, t.wall, t.resident) for t in self.package_times if t.wall not in UNSET_WALL_TIMES))

    def report_utc(self):
        return self.clock.to_utc(self.report_wall)

    def time_value(self, text):
        """``(UTC datetime or None, note)`` for a device wall time printed in the report."""
        value = str(text).strip()
        notes = []
        moment = None
        if value in UNSET_WALL_TIMES:
            notes.append(NOTE_UNSET)
        elif parse_wall_time(value) is None:
            notes.append(NOTE_NOT_A_TIME)
        else:
            if not self.clock.known:
                notes.append(NOTE_NO_ZONE)
            else:
                moment = self.clock.to_utc(value)
                if moment is None:
                    notes.append(NOTE_NONEXISTENT)
            if normal_wall_text(value) in self.factory_stamps or is_placeholder_time(value):
                notes.append(NOTE_FACTORY_STAMP)
        return moment, '; '.join(notes)


class Section:
    """A section of the text: ``kind`` is preamble, command or service; ``end_line`` is the first line that is not in it."""

    def __init__(self, kind, name, line, group=False):
        self.kind = kind
        self.name = name
        self.line = line
        self.group = group      # a command that runs the dumpsys binary and holds service sections
        self.end_line = 0
        self.duration = None    # seconds, when the text prints the duration line of the section


class SectionReader:
    """Base of the readers that receive the lines of one kind of section."""
    kind = ''
    name = ''

    def __init__(self, report, section):
        self.report = report
        self.section = section

    def feed(self, line_no, text):
        """One line of the section body (the header line is not included)."""

    def finish(self):
        """The section ended."""


class PreambleReader(SectionReader):
    """The banner and the header lines before the first section."""
    kind = 'preamble'
    name = 'preamble'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.seen = set()

    def feed(self, line_no, text):
        if text.startswith('== dumpstate: '):
            if not self.report.report_wall:
                self.report.report_wall = text[len('== dumpstate: '):].strip()
                self.report.add('facts', Fact('Report time (as printed)', tidy(self.report.report_wall), 'header', line_no))
            return
        key, separator, value = text.partition(':')
        if separator and key in HEADER_KEYS and key not in self.seen:
            self.seen.add(key)
            self.report.add('facts', Fact(key, tidy(value.strip().strip("'"))[:400], 'header', line_no))
        elif text.startswith('Dumpstate info:'):
            self.report.add('facts', Fact('Dumpstate info', tidy(text[len('Dumpstate info:'):].strip())[:400],
                                          'header', line_no))


class PropertiesReader(SectionReader):
    """``getprop`` output: ``[name]: [value]``. A value can continue over several lines."""
    kind = 'command'
    name = 'SYSTEM PROPERTIES'
    max_value_lines = 600

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.pending = None           # (name, first line number, value lines)

    def _store(self, name, line_no, value):
        if name in PROPERTY_ALLOW and name not in self.report.properties:
            self.report.properties[name] = (value, line_no)
            self.report.add('facts', Fact(name, tidy(value)[:400], 'getprop', line_no))

    def feed(self, line_no, text):
        text = text.rstrip()
        if self.pending is not None:
            self.pending[2].append(text)
            if text.endswith(']') or len(self.pending[2]) > self.max_value_lines:
                name, first, lines = self.pending
                self.pending = None
                if text.endswith(']'):
                    lines[-1] = text[:-1]
                    self._store(name, first, ' '.join(lines))
            return
        if not text.startswith('['):
            return
        close = text.find(']: [')
        if close < 0:
            return
        name = text[1:close]
        value = text[close + 4:]
        if value.endswith(']'):
            self._store(name, line_no, value[:-1])
        else:
            self.pending = (name, line_no, [value])


class PackageReader(SectionReader):
    """``dumpsys package``: one record per ``Package [name]`` of the Packages and Hidden system packages blocks."""
    kind = 'service'
    name = 'package'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.top = ''
        self.block = ''
        self.current = None
        self.times = []
        self.user = None
        self.users = []

    def _close_package(self):
        record = self.current
        if record is None:
            return
        self.current = None
        users_installed = ','.join(str(user) for user, state in self.users if state.get('installed') == 'true')
        user_states = '; '.join('%s: %s' % (user, ' '.join('%s=%s' % (k, v) for k, v in state.items()))
                                for user, state in self.users)
        record['users_installed'] = users_installed
        record['user_states'] = user_states
        self.report.add('packages', PackageRecord(
            record['block'], record['package'], record['app_id_key'], record['app_id'], record['shared_user'],
            record['version_code'], record['version_name'], record['min_sdk'], record['target_sdk'],
            record['code_path'], record['flags'], record['installer'], record['initiating'], record['originating'],
            record['package_source'], users_installed, user_states, record['line']))
        resident = sits_on_image(record['code_path'], record['block'] == 'Hidden system packages')
        for event, wall, user, line_no in self.times:
            self.report.add('package_times', PackageTime(record['package'], event, wall, user, record['installer'],
                                                         record['block'], line_no, resident))
        self.times = []
        self.users = []
        self.user = None

    def feed(self, line_no, text):
        if not text.strip():
            return
        indent = len(text) - len(text.lstrip(' '))
        body = text.strip()
        if indent == 0:
            if text.startswith('***'):
                return
            self._close_package()
            self.top = text.rstrip(':') if text.endswith(':') else text
            self.block = self.top if self.top in ('Packages', 'Hidden system packages') else ''
            return
        if not self.block:
            return
        if indent == 2:
            if body.startswith('Package [') and body.endswith('):'):
                self._close_package()
                name = body[body.find('[') + 1:body.find(']')]
                self.current = {
                    'block': self.block, 'package': tidy(name), 'app_id_key': '', 'app_id': None, 'shared_user': '',
                    'version_code': None, 'version_name': '', 'min_sdk': None, 'target_sdk': None, 'code_path': '',
                    'flags': '', 'installer': '', 'initiating': '', 'originating': '', 'package_source': '',
                    'line': line_no}
                self.times = []
                self.users = []
                self.user = None
            return
        record = self.current
        if record is None:
            return
        if indent == 4:
            self._attribute(record, body, line_no)
        elif indent == 6 and self.user is not None and body.startswith('firstInstallTime='):
            self.times.append(('firstInstallTime', body.split('=', 1)[1], self.user, line_no))

    def _attribute(self, record, body, line_no):
        if body == 'install permissions:':
            self.user = None
            return
        if body.startswith('User ') and ':' in body:
            head, _, rest = body.partition(':')
            user = to_int(head[5:])
            if user is not None and head[5:].strip().isdigit():
                self.user = user
                state = key_values(rest)
                kept = collections.OrderedDict()
                for key in ('installed', 'stopped', 'hidden', 'suspended', 'enabled'):
                    if key in state:
                        kept[key] = tidy(state[key])
                self.users.append((user, kept))
            return
        key, separator, value = body.partition('=')
        if not separator:
            return
        if key in ('appId', 'userId'):
            record['app_id_key'], record['app_id'] = key, to_int(value)
        elif key == 'sharedUser':
            inner = value[value.find('SharedUserSetting{') + 18:].rstrip('}') if 'SharedUserSetting{' in value else value
            record['shared_user'] = tidy(inner.split(' ', 1)[-1])
        elif key == 'codePath':
            record['code_path'] = tidy(value)
        elif key == 'versionCode':
            parts = key_values(body)
            record['version_code'] = to_int(parts.get('versionCode'))
            record['min_sdk'] = to_int(parts.get('minSdk'))
            record['target_sdk'] = to_int(parts.get('targetSdk'))
        elif key == 'versionName':
            record['version_name'] = tidy(value)
        elif key in ('flags', 'pkgFlags'):
            if not record['flags']:
                record['flags'] = tidy(value.strip('[] ').strip())
        elif key == 'installerPackageName':
            record['installer'] = '' if value == 'null' else tidy(value)
        elif key == 'initiatingPackageName':
            record['initiating'] = '' if value == 'null' else tidy(value)
        elif key == 'originatingPackageName':
            record['originating'] = '' if value == 'null' else tidy(value)
        elif key == 'packageSource':
            record['package_source'] = tidy(value)
        elif key in ('timeStamp', 'lastUpdateTime', 'firstInstallTime'):
            self.times.append((key, value.strip(), None, line_no))

    def finish(self):
        self._close_package()


READERS = [PreambleReader, PropertiesReader, PackageReader]
# Which artifacts present each section, for the section index.
READ_BY = {
    ('preamble', 'preamble'): 'Device Facts',
    ('command', 'SYSTEM PROPERTIES'): 'Device Facts',
    ('service', 'package'): 'Installed Packages; Package Times',
}


def readers_by_section():
    """``{(kind, name): [reader classes]}`` for the section readers above."""
    table = {}
    for reader in READERS:
        table.setdefault((reader.kind, reader.name), []).append(reader)
    return table


# ---------------------------------------------------------------------------------------------
# The pass
# ---------------------------------------------------------------------------------------------
def scan_lines(raw_lines, report):
    """Feed every line of a report text to the section readers (one pass, nothing is stored but the tables)."""
    table = readers_by_section()
    state = {'cmd': None, 'svc': None, 'active': []}

    def end_active():
        for reader in state['active']:
            reader.finish()
        state['active'] = []

    def open_section(kind, name, line_no, group=False):
        classes = table.get((kind, name), ())
        section = Section(kind, name, line_no, group)
        report.sections.append(section)
        state['active'] = [cls(report, section) for cls in classes]
        if classes:
            report.sections_seen.add(name)
        return section

    def close_service(line_no, duration=None):
        section = state['svc']
        if section is not None:
            section.end_line, section.duration = line_no, duration
            end_active()
            state['svc'] = None

    def close_command(line_no, duration=None):
        section = state['cmd']
        if section is not None and section.kind != 'marker':
            section.end_line, section.duration = line_no, duration
        end_active()
        state['cmd'] = None

    # the preamble is open from the first line to the first command header
    state['cmd'] = open_section('preamble', 'preamble', 1)

    line_no = 0
    for raw in raw_lines:
        line_no += 1
        report.total_lines = line_no
        if line_no == 1 and raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        if raw and raw[0] in _BOUNDARY_FIRST:
            text = _line_text(raw)
            if text.startswith('------ ') and text.endswith(' ------'):
                inner = text[7:-7]
                if " was the duration of '" in inner and inner.split(' ', 1)[0].endswith('s'):
                    title = inner.partition("'")[2].rpartition("'")[0]
                    command = state['cmd']
                    if command is not None and command.name == title:
                        seconds = _seconds(inner.split(' ', 1)[0])
                        close_service(line_no)
                        close_command(line_no, seconds)
                    continue
                title, separator, rest = inner.partition(' (')
                command_text = rest[:-1] if separator and rest.endswith(')') else rest
                close_service(line_no)
                close_command(line_no)
                is_group = command_text == '/system/bin/dumpsys' and title.startswith('DUMPSYS')
                state['cmd'] = open_section('command', title.strip(), line_no, is_group)
                if is_group:
                    state['active'] = []
                continue
            if text.startswith('DUMP OF SERVICE ') and text.rstrip().endswith(':'):
                name = text[len('DUMP OF SERVICE '):].rstrip()[:-1]
                for prefix in ('CRITICAL ', 'HIGH '):
                    if name.startswith(prefix):
                        name = name[len(prefix):]
                        break
                close_service(line_no)
                end_active()
                state['svc'] = open_section('service', name, line_no)
                continue
            if text.startswith("*** SERVICE '") and ' DUMP TIMEOUT (' in text:
                milliseconds = text.partition(' DUMP TIMEOUT (')[2].partition('ms)')[0]
                if state['svc'] is not None and milliseconds.isdigit():
                    report.timeouts[state['svc'].name] = int(milliseconds)
            elif text.startswith('--------- ') and ' was the duration of dumpsys ' in text:
                name = text.partition(' was the duration of dumpsys ')[2].partition(', ending at: ')[0].strip()
                if state['svc'] is not None and state['svc'].name == name:
                    close_service(line_no, _seconds(text[10:].split(' ', 1)[0]))
                    continue
            elif text.startswith('== ') and state['svc'] is None and not text.rstrip().endswith('=='):
                if not (text.startswith('== dumpstate: ') and state['cmd'] is not None
                        and state['cmd'].kind == 'preamble' and not text.startswith('== dumpstate: done')):
                    close_command(line_no)
                    state['cmd'] = Section('marker', text[3:].strip(), line_no)
                    continue
            if state['active']:
                for reader in state['active']:
                    reader.feed(line_no, text)
            continue
        if state['active']:
            text = _line_text(raw)
            for reader in state['active']:
                reader.feed(line_no, text)
    close_service(line_no + 1)
    close_command(line_no + 1)


def _seconds(text):
    """Seconds from a printed duration such as ``0.346s``, or None."""
    if not text.endswith('s'):
        return None
    try:
        return float(text[:-1])
    except ValueError:
        return None


_CACHE = collections.OrderedDict()
_LOGGED = set()


def read_report(source):
    """The :class:`Report` of a source, read once per run and kept for the artifacts that follow."""
    path = source.path
    try:
        stat = os.stat(path)
        key = (os.path.realpath(path), source.member, stat.st_size, stat.st_mtime_ns)
    except OSError:
        key = (path, source.member, 0, 0)
    report = _CACHE.get(key)
    if report is not None:
        _CACHE.move_to_end(key)
        return report
    report = Report(source)
    stream = close = None
    try:
        stream, close = _open_binary(source)
        scan_lines(iter_lines(stream), report)
    except READ_ERRORS as error:
        report.warn('reading stopped at line %d: %s' % (report.total_lines, error))
    finally:
        if close is not None:
            close()
    report.finish()
    _CACHE[key] = report
    while len(_CACHE) > CACHE_SIZE:
        _CACHE.popitem(last=False)
    return report


def clear_cache():
    """Forget the reports read so far (the tests use this)."""
    _CACHE.clear()
    _LOGGED.clear()

def source_label(source, relative_path):
    """The name shown in the Source File column: the staged path inside the extraction, plus the member for a zip."""
    label = relative_path(source.path)
    return label + '!/' + source.member if source.member else label


def load_reports(paths, relative_path, log):
    """``[(label, Report)]`` for the bug report texts among ``paths``, in path order.

    ``relative_path`` turns a staged path into the path inside the extraction; ``log`` receives one
    line for each file that was not read and for each warning a report carries.
    """
    sources, notes = find_sources(sorted(str(path) for path in paths))
    loaded = []
    messages = ['Bug report: ' + note for note in notes]
    for source in sources:
        report = read_report(source)
        label = source_label(source, relative_path)
        messages.extend('Bug report %s: %s' % (os.path.basename(label), warning) for warning in report.warnings)
        loaded.append((label, report))
    for message in messages:
        if message not in _LOGGED:       # the artifacts of one run read the same files: say each thing once
            _LOGGED.add(message)
            log(message)
    return loaded

