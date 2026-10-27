"""Readers for the location, sensor, camera, audio, media, accessibility, input method, display and window sections.

These readers plug into the single pass of :mod:`scripts.dumpstate_reader`: each is a
``SectionReader`` that receives the lines of one dumpsys service section while the shared
reader walks the text once. They keep a bounded number of rows per table, cut long lines and
never judge what they read; the column meaning is stated in the notes of the artifacts in
``scripts/artifacts/bugreportSensorsMedia.py``.

Import order: ``scripts.dumpstate_reader`` imports this module at its end (to register the
readers), so import the reader module first, never this one alone.

The tables are created on the ``Report`` object when a reader first runs (``Report`` itself is
not changed); ``rows(report, name)`` returns the list of a table, empty when the section was
not in the text.
"""
import re
from collections import namedtuple

from scripts import dumpstate_reader as base

# ---------------------------------------------------------------------------------------------
# Row types
# ---------------------------------------------------------------------------------------------
LocationProvider = namedtuple(
    'LocationProvider', 'provider service allowed useable enabled identity properties listeners target_service connected '
                        'stationary started line')
LocationLast = namedtuple('LocationLast', 'source provider user text enabled line')
LocationRequest = namedtuple(
    'LocationRequest', 'source provider uid package tag listener flags request work_source state line')
LocationEvent = namedtuple('LocationEvent', 'time_text provider event client detail line')
LocationUsage = namedtuple(
    'LocationUsage', 'source provider client min_interval max_interval total active foreground locations detail line')
TimeZoneState = namedtuple('TimeZoneState', 'component item index elapsed value line')

Sensor = namedtuple(
    'Sensor', 'handle name vendor version type permission flags mode capabilities active_count sampling selected_sampling '
              'batching selected_batching connections line')
SensorConnection = namedtuple(
    'SensorConnection', 'number mode label uid access sensor handle status first_flush pending_flush line')
SensorRegistration = namedtuple(
    'SensorRegistration', 'clock action handle pid uid sampling batching result sensor package line')
SensorEvent = namedtuple('SensorEvent', 'sensor event ts wall values line')

CameraEvent = namedtuple('CameraEvent', 'time_text event device package pid priority detail line')
CameraDevice = namedtuple(
    'CameraDevice', 'part device state opened package pid uid priority device_status line')

AudioEvent = namedtuple('AudioEvent', 'log time_text uid pid text line')
AudioClient = namedtuple('AudioClient', 'kind pid uid name session count line')

MediaSession = namedtuple(
    'MediaSession', 'role tag key user owner_pid owner_uid package active flags state audio_attributes volume metadata line')
AudioPlayback = namedtuple('AudioPlayback', 'position uid packages line')
MediaMetric = namedtuple('MediaMetric', 'form number key time_text package pid uid properties line')

AccessibilityService = namedtuple('AccessibilityService', 'user list index component tags line')

InputMethod = namedtuple(
    'InputMethod', 'index method_id settings_activity package service uid version_code permission current line')
StartInput = namedtuple(
    'StartInput', 'entry time_text reason restarting ime target_window soft_input_mode input_type ime_options field_id '
                  'field_name line')
SoftInputToggle = namedtuple(
    'SoftInputToggle', 'entry time_text reason uid pid focused_window ime_target input_type line')

DisplayState = namedtuple('DisplayState', 'source display state brightness sdr_brightness name size line')
BrightnessEvent = namedtuple(
    'BrightnessEvent', 'time_text kind display state policy brightness nits lux reason strategy text line')
WindowFocus = namedtuple('WindowFocus', 'display item value package line')
WindowRow = namedtuple(
    'WindowRow', 'number title display uid package session_pid view_visibility has_surface ready on_screen visible line')
SfLayer = namedtuple('SfLayer', 'display name z window_type composition transform focused line')

TABLES = ('location_providers', 'location_last', 'location_requests', 'location_events', 'location_usage', 'time_zone_states',
          'sensors', 'sensor_connections', 'sensor_registrations', 'sensor_events', 'camera_events', 'camera_devices',
          'audio_events', 'audio_clients', 'media_sessions', 'audio_playback', 'media_metrics', 'accessibility_services',
          'input_methods', 'start_inputs', 'soft_input_toggles', 'display_states', 'brightness_events', 'window_focus',
          'windows', 'sf_layers')

TEXT_CAP = 600
PROPERTY_CAP = 1500


def rows(report, name):
    """The rows of one of this module's tables on a Report (an empty list when the section was not read)."""
    return report.__dict__.get(name) or []


def put(report, name, row):
    """Append to a table of this module, bounded by the MAX_ROWS rule of Report.add."""
    if name not in report.__dict__:
        report.__dict__[name] = []
    report.add(name, row)


def clean(text, cap=TEXT_CAP):
    return base.tidy(text).strip()[:cap]


def indent_of(text):
    return len(text) - len(text.lstrip(' '))


_CLOCK = re.compile(r'^(?:(\d{4})-)?(\d\d-\d\d \d\d:\d\d:\d\d)[.:](\d{1,3})(?=\D|$)')


def split_clock(text):
    """``(time text, rest)`` for a line that starts with ``MM-DD HH:MM:SS.mmm`` (or ``:mmm``, or with a year), else ``('', text)``.

    The time text is ``MM-DD HH:MM:SS.mmm`` or ``YYYY-MM-DD HH:MM:SS.mmm``.
    """
    match = _CLOCK.match(text)
    if not match:
        return '', text
    year, stamp, millis = match.groups()
    shown = '%s%s.%s' % (year + '-' if year else '', stamp, millis.ljust(3, '0'))
    return shown, text[match.end():].lstrip(' :-')


def utc_for(report, time_text):
    """UTC datetime or None for a time text of split_clock: with a year it is converted as printed, without one the year rule of the settings history is used."""
    if not time_text:
        return None
    if len(time_text) > 15 and time_text[4] == '-':
        moment = base.parse_wall_time(time_text)
        if moment is None or moment.year < 2009:
            return None
        return report.clock.to_utc(time_text)
    return report.setting_change_time(time_text)[1]


def _hex_int(text):
    value = str(text).strip()
    try:
        return int(value, 16) if value.lower().startswith('0x') else int(value)
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------
# location
# ---------------------------------------------------------------------------------------------
_LISTENER = re.compile(r'^(\d+)/([^/\[\s]+)(?:\[([^\]]*)\])?/(\S+)\s*(.*)$')
_PROVIDER_HEAD = re.compile(r'^(\S+) provider:$')
_USAGE_NEW = re.compile(r'^(.*?): min/max interval = (\S+?)/(\S+?), total/active/foreground duration = (\S+?)/(\S+?)/(\S+?), '
                        r'locations = (\d+)$')
_RECORD_OLD = re.compile(r'^UpdateRecord\[(\S+) (.+?)\((\d+) ([^)]*)\) (Request\[[^\]]*\])\s*(.*?)\]?$')


def request_work_source(text):
    """The text after the Request[...] part of a listener line, the WorkSource if there is one."""
    at = text.find('WorkSource{')
    return text[at:].split('}', 1)[0] + '}' if at >= 0 else ''


class LocationReader(base.SectionReader):
    """The location service dump: providers, listeners, last known locations, aggregate usage and the event log."""
    kind = 'service'
    name = 'location'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.layout = ''
        self.part = ''
        self.provider = ''
        self.fields = None
        self.sub = ''
        self.user = None
        self.listeners = 0
        self.pending = None
        self.old_list = ''

    # --- helpers
    def _flush_last(self):
        pending, self.pending = self.pending, None
        if pending is not None and (pending['text'] or pending['enabled']):
            put(self.report, 'location_last', LocationLast(
                pending['source'], pending['provider'], pending['user'], pending['text'], pending['enabled'], pending['line']))

    def _flush_provider(self):
        self._flush_last()
        fields, self.fields = self.fields, None
        self.sub = ''
        self.user = None
        if fields is not None:
            put(self.report, 'location_providers', LocationProvider(
                fields['provider'], fields.get('service', ''), fields.get('allowed', ''), fields.get('useable', ''),
                fields.get('enabled', ''), fields.get('identity', ''), fields.get('properties', ''), fields['listeners'],
                fields.get('target', ''), fields.get('connected', ''), fields.get('stationary', ''), fields.get('started', ''),
                fields['line']))

    def _add_request(self, source, provider, text, line_no):
        match = _LISTENER.match(text)
        if not match:
            return
        uid, package, tag, listener, rest = match.groups()
        head, _sep, tail = rest.partition('Request[')
        request = ('Request[' + tail.split(']', 1)[0] + ']') if _sep else ''
        flags = ' '.join(word for word in head.split() if word.startswith(('(', '{')))
        put(self.report, 'location_requests', LocationRequest(
            source, provider, to_uid(uid), clean(package, 200), clean(tag or '', 200), clean(listener, 40), clean(flags, 80),
            clean(request, 400), clean(request_work_source(rest), 200), '', line_no))

    # --- the pass
    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if indent == 0:
            if body == 'Location Manager State:':
                self.layout = 'new'
            elif body == 'Current Location Manager state:':
                self.layout = 'old'
            return
        if self.layout == 'new':
            self._feed_new(line_no, body, indent)
        elif self.layout == 'old':
            self._feed_old(line_no, body, indent)

    def _feed_new(self, line_no, body, indent):
        if indent == 2:
            self._flush_provider()
            self.provider = ''
            self.part = {'Location Providers:': 'providers', 'Historical Aggregate Location Provider Data:': 'usage',
                         'Event Log:': 'events'}.get(body, '')
            return
        if self.part == 'events':
            if indent == 4:
                stamp, rest = split_clock(body)
                if stamp:
                    self._event(line_no, stamp, rest)
            return
        if self.part == 'usage':
            if indent == 4 and body.endswith(':'):
                self.provider = body[:-1]
            elif indent == 6:
                match = _USAGE_NEW.match(body)
                if match:
                    client, low, high, total, active, foreground, count = match.groups()
                    put(self.report, 'location_usage', LocationUsage(
                        'Historical Aggregate Location Provider Data', self.provider, clean(client, 300), low, high, total,
                        active, foreground, int(count), '', line_no))
            return
        if self.part != 'providers':
            return
        if indent == 4:
            match = _PROVIDER_HEAD.match(body)
            self._flush_provider()
            if match:
                self.provider = match.group(1)
                self.fields = {'provider': self.provider, 'listeners': 0, 'line': line_no}
            return
        if self.fields is None:
            return
        if indent == 6:
            if body.startswith('enabled=') and self.pending is not None and self.pending['user'] is None and self.sub == 'last':
                self.pending['enabled'] = clean(body[len('enabled='):], 40)
                return
            self.sub = ''
            self._flush_last()
            if body == 'listeners:':
                self.sub = 'listeners'
            elif body.startswith('user ') and body.endswith(':') and base.is_digits(body[5:-1]):
                self.sub = 'user'
                self.user = int(body[5:-1])
                self.pending = {'source': 'Location Providers', 'provider': self.provider, 'user': self.user, 'text': '',
                                'enabled': '', 'line': line_no}
            elif body.startswith('last location='):
                self.user = None
                self.pending = {'source': 'Location Providers', 'provider': self.provider, 'user': None,
                                'text': clean(body[len('last location='):], 900), 'enabled': '', 'line': line_no}
                self.sub = 'last'
            else:
                key, sep, value = body.partition('=')
                if body.startswith('service: '):
                    self.fields['service'] = clean(body[len('service: '):], 300)
                elif not sep:
                    return
                elif key in ('allowed', 'identity', 'connected'):
                    self.fields[key] = clean(value, 300)
                elif key == 'properties':
                    self.fields['properties'] = clean(value, 400)
                elif key == 'target service':
                    self.fields['target'] = clean(value, 300)
                elif key == 'stationary throttled':
                    self.fields['stationary'] = clean(value, 120)
                elif key == 'mStarted':
                    self.fields['started'] = clean(value, 120)
                elif key == 'enabled' and self.pending is None:
                    self.fields['enabled'] = clean(value, 40)
            return
        if indent == 8:
            if self.sub == 'listeners':
                self.fields['listeners'] += 1
                self._add_request('Location Providers', self.provider, body, line_no)
            elif self.sub in ('user', 'last') and self.pending is not None:
                if body.startswith('last location='):
                    self.pending['text'] = clean(body[len('last location='):], 900)
                    self.pending['line'] = line_no
                elif body.startswith('enabled='):
                    self.pending['enabled'] = clean(body[len('enabled='):], 40)

    def _event(self, line_no, stamp, rest):
        provider = ''
        match = re.match(r'^(\S+) provider (.*)$', rest)
        if match:
            provider, rest = match.groups()
        client, detail, event = '', '', rest
        for mark in ('+registration', '-registration'):
            if rest.startswith(mark + ' ') or rest == mark:
                event = mark
                after = rest[len(mark):].strip()
                client, _sep, detail = after.partition(' -> ')
                break
        else:
            if rest.startswith('client '):
                words = rest.split(' ', 2)
                event, client = 'client', words[1] if len(words) > 1 else ''
                detail = words[2].lstrip('-> ') if len(words) > 2 else ''
            elif ' = ' in rest and rest.split(' = ', 1)[0] in ('request',):
                event, detail = 'request', rest.split(' = ', 1)[1]
            elif rest.startswith('delivered ') and ' to ' in rest:
                event, _sep, client = rest.partition(' to ')
        put(self.report, 'location_events', LocationEvent(
            stamp, clean(provider, 60), clean(event, 400), clean(client, 300), clean(detail, 600), line_no))

    def _feed_old(self, line_no, body, indent):
        if indent == 2:
            if body.startswith('mStarted=') and self.fields is not None:
                self.fields['started'] = clean(body.partition('=')[2], 120)
                return
            self._flush_provider()
            match = _PROVIDER_HEAD.match(body)
            if match:
                self.part = 'old_provider'
                self.provider = match.group(1)
                self.fields = {'provider': self.provider, 'listeners': 0, 'line': line_no}
                return
            self.part = {'Active Records by Provider:': 'old_active', 'Historical Records by Provider:': 'old_usage',
                         'Last Known Locations:': 'old_last',
                         'Last Known Locations Coarse Intervals:': 'old_last'}.get(body, '')
            self.old_list = body[:-1] if self.part == 'old_last' else ''
            return
        if self.part == 'old_provider' and self.fields is not None and indent == 4:
            key, sep, value = body.partition('=')
            if sep and key in ('useable', 'enabled'):
                self.fields[key] = clean(value, 40)
            return
        if self.part == 'old_active':
            if indent == 4 and body.endswith(':'):
                self.provider = body[:-1]
            elif indent == 6:
                match = _RECORD_OLD.match(body)
                if match:
                    _kind, package, uid, state, request, rest = match.groups()
                    put(self.report, 'location_requests', LocationRequest(
                        'Active Records by Provider', self.provider, to_uid(uid), clean(package, 200), '', '', '',
                        clean(request, 400), clean(request_work_source(rest), 200), clean(state, 40), line_no))
            return
        if self.part == 'old_usage' and indent == 4:
            match = re.match(r'^(\S+): (\S+): (.*)$', body)
            if match:
                client, provider, detail = match.groups()
                put(self.report, 'location_usage', LocationUsage(
                    'Historical Records by Provider', provider, clean(client, 300), '', '', '', '', '', None,
                    clean(detail, 400), line_no))
            return
        if self.part == 'old_last' and indent == 4:
            provider, sep, text = body.partition(': ')
            if sep and text.startswith('Location['):
                put(self.report, 'location_last', LocationLast(self.old_list, provider, None, clean(text, 900), '', line_no))

    def finish(self):
        self._flush_provider()
        if self.layout == 'old':
            self.fields = None


def to_uid(text):
    return base.to_int(text)


_LOCATION_TEXT = re.compile(r'Location\[(\S+) ([^,\s]+),([^\s\]]+)(.*)')


def parse_location_text(text):
    """``(provider, latitude, longitude, accuracy, elapsed)`` as printed in a Location[...] text, empty where not printed."""
    match = _LOCATION_TEXT.match(text)
    if not match:
        return '', '', '', '', ''
    provider, latitude, longitude, rest = match.groups()
    accuracy = re.search(r'\bhAcc=(\S+)', rest)
    elapsed = re.search(r'\bet=(\S+)', rest)
    return (provider, latitude, longitude, accuracy.group(1) if accuracy else '', elapsed.group(1) if elapsed else '')


class TimeZoneReader(base.SectionReader):
    """The location_time_zone_manager dump: provider configuration, controller state and the state histories."""
    kind = 'service'
    name = 'location_time_zone_manager'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.component = ''
        self.history = False

    def _row(self, item, value, line_no, index=None, elapsed=''):
        put(self.report, 'time_zone_states', TimeZoneState(self.component, item, index, elapsed, clean(value, 900), line_no))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if indent == 2:
            self.history = False
            if body in ('Primary provider config:', 'Secondary provider config:'):
                self.component = body[:-1]
            elif body == 'LocationTimeZoneProviderController:':
                self.component = 'Controller'
            return
        if indent == 4 and self.component.endswith('provider config'):
            key, sep, value = body.partition('=')
            if sep and key in ('getMode()', 'getPackageName()'):
                self._row('config mode' if key == 'getMode()' else 'config package', value, line_no)
            return
        if indent == 4:
            self.history = False
            if body in ('Primary Provider:', 'Secondary Provider:'):
                self.component = body[:-1]
                return
            if body == 'State history:':
                self.history = True
                return
            key, sep, value = body.partition('=')
            if sep and self.component == 'Controller' and key in ('mState', 'mCurrentUserConfiguration'):
                self._row('controller ' + key, value, line_no)
            return
        if indent >= 6 and self.component in ('Primary Provider', 'Secondary Provider'):
            if indent == 6:
                self.history = body == 'State history:'
            key, sep, value = body.partition('=')
            if sep and key in ('mCurrentState', 'connected', 'target service'):
                self._row('provider ' + key, value, line_no)
                return
        if self.history:
            match = re.match(r'^(\d+)@(\S+): (.*)$', body)
            if match:
                index, elapsed, value = match.groups()
                item = 'controller state history' if self.component == 'Controller' else 'provider state history'
                self._row(item, value, line_no, int(index), elapsed)


# ---------------------------------------------------------------------------------------------
# sensors
# ---------------------------------------------------------------------------------------------
_SENSOR_HEAD = re.compile(r'^(0x[0-9a-fA-F]+|\d+)\) (.*?)\s*\| (.*?)\s*\| ver: (\S+) \| type: (.*?) \| perm: (.*?) \| flags: (\S+)')
_DEVICE_STATE = re.compile(r'(?:\(handle=(0x[0-9a-fA-F]+)\)\s*|^(0x[0-9a-fA-F]+|\d+)\) ?)active-count = (\d+); sampling_period\(ms\) = '
                           r'\{(.*?)\}, selected = (\S+) ms; batching_period\(ms\) = \{(.*?)\}, selected = (\S+) ms')
_ACTIVE_SENSOR = re.compile(r'\(handle=(0x[0-9a-fA-F]+|\d+), connections=(\d+)\)')
_EVENT_HEAD = re.compile(r'^(.+): last (\d+) events?:?$')
_EVENT_ROW = re.compile(r'^(\d+) \(ts=([\d.]+), wall=(.*?)\)\s*(.*)$')
# The clock is HH:MM:SS, or MM-DD HH:MM:SS.mmm on Samsung's Android 13 report, which also ends a line with [ sensor ].
_REGISTRATION = re.compile(r'^((?:\d\d-\d\d )?\d\d:\d\d:\d\d(?:\.\d+)?) ([+-]) (0x[0-9a-fA-F]+|\d+) pid=\s*(-?\d+) '
                           r'uid=\s*(-?\d+)(?: package=(\S+))?'
                           r'(?: samplingPeriod=\s*(N/A|-?\d+)\s*us\s+batchingPeriod=\s*(N/A|-?\d+)\s*us)?'
                           r'(?:\s+result=(\S+)(?: \(sensor, package\): \((.*)\))?)?'
                           r'(?:\s+\[ (.*?) \])?')


class SensorReader(base.SectionReader):
    """The sensorservice dump: the sensor list with its active state, connections, previous registrations and recent events."""
    kind = 'service'
    name = 'sensorservice'
    max_events_per_sensor = 100

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.part = ''
        self.sensors = {}
        self.order = []
        self.states = {}
        self.connections = {}
        self.last_sensor = None
        self.event_sensor = ''
        self.event_count = 0
        self.connection = None

    def _flush_connection(self):
        conn, self.connection = self.connection, None
        if conn is None:
            return
        entries = conn['entries'] or [('', '', '', '', '')]
        for sensor, handle, status, first, pending in entries:
            put(self.report, 'sensor_connections', SensorConnection(
                conn['number'], conn['mode'], conn['label'], conn['uid'], conn['access'], sensor, handle, status, first, pending,
                conn['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if text[0] not in ' \t':
            self._heading(line_no, body)
            return
        part = self.part
        if part == 'device':
            match = _DEVICE_STATE.search(body)
            if match:
                handle = _hex_int(match.group(1) or match.group(2))
                self.states[handle] = (int(match.group(3)), clean(match.group(4), 120), match.group(5), clean(match.group(6), 120),
                                       match.group(7))
        elif part == 'list' and self.last_sensor is not None and text[0] == '\t':
            sensor = self.sensors[self.last_sensor]
            mode = body.split('|', 1)[0].strip()
            self.sensors[self.last_sensor] = sensor._replace(mode=clean(mode, 60), capabilities=clean(body, 300))
            self.last_sensor = None
        elif part == 'events':
            if text[0] == '\t' or indent > 0:
                match = _EVENT_ROW.match(body)
                if match and self.event_sensor and self.event_count < self.max_events_per_sensor:
                    self.event_count += 1
                    number, stamp, wall, values = match.groups()
                    put(self.report, 'sensor_events', SensorEvent(
                        clean(self.event_sensor, 200), int(number), stamp, clean(wall, 40), clean(values.rstrip(', '), 200), line_no))
        elif part == 'connections':
            if body.startswith('Operating Mode:') and self.connection is not None:
                self.connection['mode'] = clean(body.partition(':')[2], 60)
            elif '| WakeLockRefCount' in body and self.connection is not None:
                label, _sep, rest = body.partition(' | WakeLockRefCount')
                self.connection['label'] = clean(label, 300)
                match = re.search(r'\|\s*uid (-?\d+)', rest)
                self.connection['uid'] = int(match.group(1)) if match else None
                match = re.search(r'has sensor access: (\w+)', rest)
                self.connection['access'] = match.group(1) if match else ''
            elif self.connection is not None and ('| status:' in body or '| first flush pending:' in body
                                                  or '| pending flush events' in body):
                left, _sep, right = body.partition('|')
                pieces = left.strip().rsplit(' ', 1)
                name, handle = (pieces[0].strip(), pieces[1].strip()) if len(pieces) == 2 else (left.strip(), '')
                status = re.search(r'status:\s*([^|]*)', right)
                first = re.search(r'first flush pending:\s*([^|]*)', right)
                pending = re.search(r'pending flush events\s*([^|]*)', right)
                self.connection['entries'].append((
                    clean(name, 200), handle, clean(status.group(1), 40) if status else '',
                    clean(first.group(1), 20) if first else '', clean(pending.group(1), 20) if pending else ''))
        elif part == 'registrations':
            match = _REGISTRATION.match(body)
            if match:
                clock, action, handle, pid, uid, package, sampling, batching, result, tail, bracket = match.groups()
                sensor = bracket or ''
                if tail:
                    sensor, _sep, package = tail.rpartition(', ')
                    if not _sep:
                        sensor, package = tail, ''
                put(self.report, 'sensor_registrations', SensorRegistration(
                    clock, action, handle, int(pid), int(uid), sampling or '', batching or '', result or '', clean(sensor, 200),
                    clean(package or '', 300), line_no))

    def _heading(self, line_no, body):
        if self.part == 'connections':
            self._flush_connection()
        if body == 'Sensor Device:':
            self.part = 'device'
        elif body == 'Sensor List:':
            self.part = 'list'
        elif body == 'Recent Sensor events:':
            self.part = 'events'
            self.event_sensor = ''
        elif body == 'Active sensors:':
            self.part = 'active'
        elif body == 'Previous Registrations:':
            self.part = 'registrations'
        elif body.startswith('Connection Number:'):
            self.part = 'connections'
            self.connection = {'number': base.to_int(body.partition(':')[2]), 'mode': '', 'label': '', 'uid': None, 'access': '',
                               'entries': [], 'line': line_no}
        elif self.part == 'list':
            match = _SENSOR_HEAD.match(body)
            if match:
                handle_text, name, vendor, version, kind, permission, flags = match.groups()
                handle = _hex_int(handle_text)
                self.sensors[handle] = Sensor(handle_text, clean(name, 200), clean(vendor, 120), clean(version, 40), clean(kind, 200),
                                              clean(permission, 200), flags, '', '', None, '', '', '', '', None, line_no)
                self.order.append(handle)
                self.last_sensor = handle
        elif self.part == 'events':
            match = _EVENT_HEAD.match(body)
            if match:
                self.event_sensor = match.group(1)
                self.event_count = 0
        elif self.part == 'active':
            match = _ACTIVE_SENSOR.search(body)
            if match:
                self.connections[_hex_int(match.group(1))] = int(match.group(2))
        elif self.part == 'device':
            match = _DEVICE_STATE.search(body)
            if match:
                handle = _hex_int(match.group(1) or match.group(2))
                self.states[handle] = (int(match.group(3)), clean(match.group(4), 120), match.group(5), clean(match.group(6), 120),
                                       match.group(7))
        elif body.startswith(('Socket Buffer', 'WakeLock', 'Mode', 'Sensor Privacy', 'Fusion States')):
            self.part = ''
        elif self.part == 'registrations':
            self.feed(line_no, ' ' + body)

    def finish(self):
        self._flush_connection()
        for handle in self.order:
            sensor = self.sensors[handle]
            state = self.states.get(handle)
            count, sampling, selected_s, batching, selected_b = state if state else (None, '', '', '', '')
            put(self.report, 'sensors', sensor._replace(
                active_count=count, sampling=sampling, selected_sampling=selected_s, batching=batching,
                selected_batching=selected_b, connections=self.connections.get(handle)))


# ---------------------------------------------------------------------------------------------
# camera
# ---------------------------------------------------------------------------------------------
_CAMERA_EVENT = re.compile(r'^(\d\d-\d\d \d\d:\d\d:\d\d) : (\S+)\s*(.*)$')
_CAMERA_HEAD = re.compile(r'^== Camera device (\S+)(?: status \d+)? dynamic info: ==$')
_DEVICE_OPEN = re.compile(r'^(?:(\d\d-\d\d \d\d:\d\d:\d\d) : )?Device (\S+) is (closed|open)')


class CameraReader(base.SectionReader):
    """The media.camera dump: the service events log and the open or closed state of each camera device."""
    kind = 'service'
    name = 'media.camera'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.part = ''
        self.session = 'current'
        self.device = None

    def _flush_device(self):
        device, self.device = self.device, None
        if device is not None:
            put(self.report, 'camera_devices', CameraDevice(
                device['part'], device['device'], device['state'], device['opened'], device['package'], device['pid'],
                device['uid'], device['priority'], device['status'], device['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        if body.startswith('**********Dumpsys from previous open session'):
            self._flush_device()
            self.session = 'previous open session'
            self.part = ''
            return
        if text.startswith('== '):
            self._flush_device()
            head = _CAMERA_HEAD.match(body)
            if head:
                self.part = 'device'
                self.device = {'part': self.session, 'device': head.group(1), 'state': '', 'opened': '', 'package': '',
                               'pid': None, 'uid': None, 'priority': '', 'status': '', 'line': line_no}
            else:
                self.part = 'events' if 'events log' in body else ''
            return
        indent = indent_of(text)
        if self.part == 'events':
            match = _CAMERA_EVENT.match(body)
            if match:
                stamp, event, rest = match.groups()
                device = re.search(r'\bdevice (\S+?)[,\s]', rest + ' ')
                package = re.search(r'\bpackage (\S+)', rest)
                pid = re.search(r'\(PID (\d+)', rest)
                priority = re.search(r'priority (-?\d+)', rest)
                put(self.report, 'camera_events', CameraEvent(
                    stamp, clean(event, 60), device.group(1) if device else '', clean(package.group(1), 200) if package else '',
                    int(pid.group(1)) if pid else None, int(priority.group(1)) if priority else None, clean(rest, 400), line_no))
            return
        if self.part != 'device' or self.device is None:
            return
        match = _DEVICE_OPEN.match(body)
        if match and indent <= 2:
            self.device['state'] = match.group(3)
            self.device['opened'] = match.group(1) or ''
            return
        if body.startswith('Client priority score:'):
            self.device['priority'] = clean(body.partition(':')[2], 80)
        elif body.startswith('Client PID:'):
            self.device['pid'] = base.to_int(body.partition(':')[2])
        elif body.startswith('Client package:'):
            self.device['package'] = clean(body.partition(':')[2], 200)
        elif body.startswith('Current client UID') and self.device['uid'] is None:
            self.device['uid'] = base.to_int(body.rsplit(' ', 1)[-1])
        elif body.startswith('Device status:') and not self.device['status']:
            self.device['status'] = clean(body.partition(':')[2], 60)

    def finish(self):
        self._flush_device()


# ---------------------------------------------------------------------------------------------
# audio
# ---------------------------------------------------------------------------------------------
_AUDIO_LOG = re.compile(r'^(?:Audio )?[Ee]vents? log: ?(.*)$')


class AudioReader(base.SectionReader):
    """The audio service dump: the timestamped lines of its event logs (focus, playback, recording, devices, volume)."""
    kind = 'service'
    name = 'audio'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.log = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        head = _AUDIO_LOG.match(text)
        if head:
            self.log = clean(head.group(1), 160)
            return
        stamp, rest = split_clock(text)
        if not stamp:
            if text[0] not in ' \t' and (body.endswith(':') or body.startswith(('Events log', 'Event logs', 'Audio event log'))):
                self.log = ''
            return
        if not self.log:
            return
        uid = pid = None
        match = re.search(r'\buid/pid:? ?(\d+)/(\d+)', rest)
        if match:
            uid, pid = int(match.group(1)), int(match.group(2))
        else:
            match = re.search(r'\buid:(\d+)', rest)
            if match:
                uid = int(match.group(1))
        put(self.report, 'audio_events', AudioEvent(self.log, stamp, uid, pid, clean(rest, TEXT_CAP), line_no))


class AudioFlingerReader(base.SectionReader):
    """The media.audio_flinger dump: the clients registered for notifications and the global session references."""
    kind = 'service'
    name = 'media.audio_flinger'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.part = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            self.part = ''
            return
        if text[0] != ' ':
            self.part = 'clients' if body == 'Notification Clients:' else 'sessions' if body == 'Global session refs:' else ''
            return
        if body.startswith(('pid ', 'session ')):
            return
        if self.part == 'clients':
            match = re.match(r'^(\d+)\s+(\d+)\s+(\S.*)$', body)
            if match:
                put(self.report, 'audio_clients', AudioClient('Notification Clients', int(match.group(1)), int(match.group(2)),
                                                              clean(match.group(3), 200), None, None, line_no))
        elif self.part == 'sessions':
            match = re.match(r'^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S.*)$', body)
            if match:
                put(self.report, 'audio_clients', AudioClient('Global session refs', int(match.group(3)), int(match.group(4)),
                                                              clean(match.group(5), 200), int(match.group(1)),
                                                              int(match.group(2)), line_no))


# ---------------------------------------------------------------------------------------------
# media sessions and metrics
# ---------------------------------------------------------------------------------------------
_SESSION_HEAD = re.compile(r'^(.+?) ([\w.$]+/.+) \(userId=(\d+)\)$')


class MediaSessionReader(base.SectionReader):
    """The media_session dump: the sessions it lists and the order in which uids last played audio."""
    kind = 'service'
    name = 'media_session'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.global_key = ''
        self.button_key = ''
        self.current = None
        self.playback = False
        self.position = 0

    def _flush(self):
        session, self.current = self.current, None
        if session is None:
            return
        role = []
        if session['key'] == self.global_key:
            role.append('global priority session')
        if session['key'] == self.button_key:
            role.append('media button session')
        put(self.report, 'media_sessions', MediaSession(
            '; '.join(role), session['tag'], session['key'], session['user'], session['owner_pid'], session['owner_uid'],
            session['package'], session['active'], session['flags'], session['state'], session['audio'], session['volume'],
            session['metadata'], session['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if body.startswith('Global priority session is '):
            self.global_key = self._key_of(body[len('Global priority session is '):])
            return
        if body.startswith('Media button session is '):
            self.button_key = self._key_of(body[len('Media button session is '):])
            return
        if indent == 0 and body.startswith('Audio playback'):
            self._flush()
            self.playback = True
            self.position = 0
            return
        if indent == 0:
            self._flush()
            self.playback = False
            return
        if self.playback:
            if body.startswith('uid='):
                head, _sep, packages = body.partition(' packages=')
                uid = base.to_int(head[4:])
                self.position += 1
                put(self.report, 'audio_playback', AudioPlayback(self.position, uid, clean(packages, 600), line_no))
            return
        match = _SESSION_HEAD.match(body)
        if match and not body.startswith(('Record for', 'Sessions Stack')):
            self._flush()
            tag, key, user = match.groups()
            self.current = {'tag': clean(tag, 200), 'key': clean(key, 300), 'user': int(user), 'owner_pid': None,
                            'owner_uid': None, 'package': '', 'active': '', 'flags': '', 'state': '', 'audio': '', 'volume': '',
                            'metadata': '', 'line': line_no}
            return
        session = self.current
        if session is None:
            return
        if body.startswith('ownerPid='):
            values = base.key_values(body.replace(', ', ' '))
            session['owner_pid'], session['owner_uid'] = base.to_int(values.get('ownerPid')), base.to_int(values.get('ownerUid'))
        elif body.startswith('package='):
            session['package'] = clean(body[len('package='):], 200)
        elif body.startswith('active='):
            session['active'] = clean(body[len('active='):], 40)
        elif body.startswith('flags='):
            session['flags'] = clean(body[len('flags='):], 40)
        elif body.startswith('state='):
            session['state'] = clean(body[len('state='):], 400)
        elif body.startswith('audioAttrs='):
            session['audio'] = clean(body[len('audioAttrs='):], 300)
        elif body.startswith('volumeType='):
            session['volume'] = clean(body, 300)
        elif body.startswith('metadata:'):
            session['metadata'] = clean(body[len('metadata:'):], 400)

    @staticmethod
    def _key_of(text):
        match = _SESSION_HEAD.match(text.strip())
        if match:
            return clean(match.group(2), 300)
        key = text.strip().rsplit(' (userId=', 1)[0]
        return clean(key, 300)

    def finish(self):
        self._flush()


_METRIC_NEW = re.compile(r'^(\d+): \{(\S+?), \((\d\d-\d\d \d\d:\d\d:\d\d\.\d+)\), \((.*?), (-?\d+), (-?\d+)\), \((.*)\)\}$')
_METRIC_OLD = re.compile(r'^(\d+): \[(\d+):([^:]+):(\d+):(\d+):([^:]*):(\d+):(\d+):(\d+):(\d+):(\d+):(.*)\]$')


class MediaMetricsReader(base.SectionReader):
    """The media.metrics dump: the records the media metrics service kept (audio tracks, codecs, extractors, recorders)."""
    kind = 'service'
    name = 'media.metrics'

    def feed(self, line_no, text):
        body = text.strip()
        if not body or not body[0].isdigit():
            return
        match = _METRIC_NEW.match(body)
        if match:
            number, key, stamp, package, pid, uid, props = match.groups()
            put(self.report, 'media_metrics', MediaMetric(
                'name, time, owner', int(number), clean(key, 100), stamp, clean(package, 200), int(pid), int(uid),
                clean(props, PROPERTY_CAP), line_no))
            return
        match = _METRIC_OLD.match(body)
        if match:
            number, _version, key, _record, uid, package, _pkg_version, pid, _flag, nanos, _count, props = match.groups()
            put(self.report, 'media_metrics', MediaMetric(
                'colon separated', int(number), clean(key, 100), nanos, clean(package, 200), int(pid), int(uid),
                clean(props, PROPERTY_CAP), line_no))


# ---------------------------------------------------------------------------------------------
# accessibility and input methods
# ---------------------------------------------------------------------------------------------
class AccessibilityReader(base.SectionReader):
    """The accessibility dump: the installed, bound, enabled, binding and crashed service lists of the current user."""
    kind = 'service'
    name = 'accessibility'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.user = None
        self.installed = False

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        if body.startswith('currentUserId='):
            self.user = base.to_int(body.partition('=')[2])
            return
        if body.startswith('installed services:'):
            self.installed = True
            return
        if self.installed:
            if body.startswith('}'):
                self.installed = False
                return
            match = re.match(r'^(\d+) : (\S+)\s*(.*)$', body)
            if match:
                put(self.report, 'accessibility_services', AccessibilityService(
                    self.user, 'installed', int(match.group(1)), clean(match.group(2), 300), clean(match.group(3), 100), line_no))
            return
        for label in ('Bound', 'Enabled', 'Binding', 'Crashed'):
            if body.startswith(label + ' services:'):
                content = body[len(label + ' services:'):].strip()
                inner = content[1:-1] if content.startswith('{') and content.rstrip(']').endswith('}') else content.rstrip(']')
                components = re.findall(r'[\w.$]+/[\w.$]+', inner)
                for number, component in enumerate(components):
                    put(self.report, 'accessibility_services', AccessibilityService(
                        self.user, label.lower(), number, clean(component, 300), '', line_no))
                if not components:
                    self.report.__dict__.setdefault('accessibility_empty', set()).add(label.lower())
                return


class InputMethodReader(base.SectionReader):
    """The input_method dump: the input methods, the start-input history and the soft-input show and hide history.

    The layout moved between Android versions (the lists are nested deeper on Android 16 and their entries carry a
    ``[n]`` index), so the headings are recognised at any indentation and a list ends at the first line that is not
    indented deeper than its heading.
    """
    kind = 'service'
    name = 'input_method'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.part = ''
        self.part_indent = 0
        self.method = None
        self.methods = []
        self.current_id = ''
        self.entry = None
        self.toggle = None

    def _flush_method(self):
        method, self.method = self.method, None
        if method is not None:
            self.methods.append(method)

    def _flush_entry(self):
        entry, self.entry = self.entry, None
        if entry is not None:
            put(self.report, 'start_inputs', StartInput(
                entry['entry'], entry['time'], entry['reason'], entry['restarting'], entry['ime'], entry['target'],
                entry['mode'], entry['input_type'], entry['ime_options'], entry['field_id'], entry['field_name'], entry['line']))
        toggle, self.toggle = self.toggle, None
        if toggle is not None:
            put(self.report, 'soft_input_toggles', SoftInputToggle(
                toggle['entry'], toggle['time'], toggle['reason'], toggle['uid'], toggle['pid'], toggle['focused'],
                toggle['ime_target'], toggle['input_type'], toggle['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if body.startswith('InputMethod #') and body.endswith(':'):
            self._flush_entry()
            self._flush_method()
            self.method = {'index': base.to_int(body[len('InputMethod #'):-1]), 'id': '', 'settings': '', 'package': '',
                           'service': '', 'uid': None, 'version': None, 'permission': '', 'line': line_no, 'stage': ''}
            self.part, self.part_indent = 'method', indent
            return
        if body in ('mStartInputHistory:', 'mSoftInputShowHideHistory:'):
            self._flush_entry()
            self._flush_method()
            self.part = 'start' if body == 'mStartInputHistory:' else 'toggle'
            self.part_indent = indent
            return
        if self.part in ('method', 'start', 'toggle') and indent <= self.part_indent:
            self._flush_entry()
            self._flush_method()
            self.part = ''
        if body.startswith(('mCurMethodId=', 'mSelectedMethodId=')) and not self.current_id:
            self.current_id = clean(body.partition('=')[2], 300)
        if self.part == 'method' and self.method is not None:
            self._method_line(body)
        elif self.part == 'start':
            self._start_line(line_no, body)
        elif self.part == 'toggle':
            self._toggle_line(line_no, body)

    def _method_line(self, body):
        method = self.method
        if body.startswith('mId='):
            values = base.key_values(body)
            method['id'] = clean(values.get('mId', ''), 300)
            method['settings'] = clean(values.get('mSettingsActivityName', ''), 300)
            return
        if body == 'ServiceInfo:':
            method['stage'] = 'service'
        elif body == 'ApplicationInfo:':
            method['stage'] = 'application'
        elif body.startswith('name=') and method['stage'] == 'service' and not method['service']:
            method['service'] = clean(body[5:], 300)
        elif body.startswith('packageName=') and method['stage'] == 'service' and not method['package']:
            method['package'] = clean(body[len('packageName='):], 200)
        elif body.startswith('permission=') and method['stage'] == 'service':
            method['permission'] = clean(body[len('permission='):], 120)
        elif method['stage'] == 'application':
            if body.startswith('uid=') and method['uid'] is None:
                method['uid'] = base.to_int(body[4:].split(' ', 1)[0])
            if ' versionCode=' in body and method['version'] is None:
                method['version'] = base.to_int(body.partition(' versionCode=')[2].split(' ', 1)[0])

    def _start_line(self, line_no, body):
        head = re.match(r'^StartInput(?:\[\d+\])? #(\d+):$', body)
        if head:
            self._flush_entry()
            self.entry = {'entry': int(head.group(1)), 'time': '', 'reason': '', 'restarting': '',
                          'ime': '', 'target': '', 'mode': '', 'input_type': '', 'ime_options': '', 'field_id': '',
                          'field_name': '', 'line': line_no}
            return
        entry = self.entry
        if entry is None:
            return
        if body.startswith('time='):
            entry['time'] = body[5:28].strip() if body[5:6].isdigit() else ''
            values = base.key_values(body)
            entry['reason'] = clean(values.get('reason', ''), 80)
            entry['restarting'] = clean(values.get('restarting', ''), 20)
        elif body.startswith('imeToken='):
            match = re.search(r'\[([^\]]*)\]', body)
            entry['ime'] = clean(match.group(1), 300) if match else ''
        elif body.startswith('targetWin='):
            match = re.search(r'\[([^\]]*)\]', body)
            entry['target'] = clean(match.group(1), 300) if match else ''
        elif body.startswith('softInputMode='):
            entry['mode'] = clean(body.partition('=')[2], 200)
        elif body.startswith('inputType='):
            values = base.key_values(body)
            entry['input_type'] = clean(values.get('inputType', ''), 40)
            entry['ime_options'] = clean(values.get('imeOptions', ''), 40)
            entry['field_id'] = clean(values.get('fieldId', ''), 60)
            entry['field_name'] = clean(values.get('fieldName', ''), 200)

    def _toggle_line(self, line_no, body):
        head = re.match(r'^SoftInputShowHide(?:\[\d+\])? #(\d+):$', body)
        if head:
            self._flush_entry()
            self.toggle = {'entry': int(head.group(1)), 'time': '', 'reason': '',
                           'uid': None, 'pid': None, 'focused': '', 'ime_target': '', 'input_type': '', 'line': line_no}
            return
        toggle = self.toggle
        if toggle is None:
            return
        if body.startswith('time='):
            toggle['time'] = body[5:28].strip() if body[5:6].isdigit() else ''
        elif body.startswith('reason='):
            values = base.key_values(body)
            toggle['reason'] = clean(values.get('reason', ''), 80)
        elif body.startswith('requestClient='):
            match = re.search(r'(?:mUid|uid)=(\d+) (?:mPid|pid)=(\d+)', body)
            if match:
                toggle['uid'], toggle['pid'] = int(match.group(1)), int(match.group(2))
        elif body.startswith('focusedWindowName='):
            toggle['focused'] = clean(body.partition('=')[2], 300)
        elif body.startswith('imeControlTargetName='):
            toggle['ime_target'] = clean(body.partition('=')[2], 300)
        elif body.startswith('editorInfo:'):
            toggle['input_type'] = clean(body.partition(':')[2], 200)

    def finish(self):
        self._flush_method()
        self._flush_entry()
        for method in self.methods:
            current = 'true' if self.current_id and method['id'] == self.current_id else ('false' if self.current_id else '')
            put(self.report, 'input_methods', InputMethod(
                method['index'], method['id'], method['settings'], method['package'], method['service'], method['uid'],
                method['version'], method['permission'], current, method['line']))


# ---------------------------------------------------------------------------------------------
# display, window and SurfaceFlinger
# ---------------------------------------------------------------------------------------------
_BRIGHTNESS_KEYS = (('disp', 'display'), ('displayState', 'state'), ('state', 'state'), ('displayPolicy', 'policy'),
                    ('brt', 'brightness'), ('brtNits', 'nits'), ('nits', 'nits'), ('lux', 'lux'), ('reason', 'reason'),
                    ('strat', 'strategy'))


class DisplayReader(base.SectionReader):
    """The display dump: the display states, the logical displays and the brightness event lists."""
    kind = 'service'
    name = 'display'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.part = ''
        self.current = None
        self.logical = None

    def _flush_state(self):
        current, self.current = self.current, None
        if current is not None:
            put(self.report, 'display_states', DisplayState(
                'Display States', current['id'], current['state'], current['brightness'], current['sdr'], '', '', current['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if body.startswith('Logical Displays:'):
            self._flush_state()
            self.part = 'logical'
            return
        if indent == 0:
            if body.startswith('---'):
                return
            self._flush_state()
            self.part = 'states' if body.startswith('Display States:') else 'logical' if body.startswith('Logical Displays:') else ''
            if body.startswith(('Automatic Brightness Adjustments', 'BrightnessTracker')) or body.endswith('Events:') \
                    or 'Brightness' in body and body.endswith(':'):
                self.part = self.part or 'other'
            return
        if self.part == 'states':
            if body.startswith('Display Id='):
                self._flush_state()
                self.current = {'id': base.to_int(body.partition('=')[2]), 'state': '', 'brightness': '', 'sdr': '', 'line': line_no}
            elif self.current is not None:
                key, sep, value = body.partition('=')
                if sep and key == 'Display State':
                    self.current['state'] = clean(value, 40)
                elif sep and key == 'Display Brightness':
                    self.current['brightness'] = clean(value, 40)
                elif sep and key == 'Display SdrBrightness':
                    self.current['sdr'] = clean(value, 40)
                elif indent <= 2 and not sep:
                    self._flush_state()
        elif self.part == 'logical':
            if re.match(r'^Display \d+:$', body):
                self.logical = {'id': base.to_int(body[8:-1]), 'line': line_no, 'done': False}
            elif self.logical is not None and not self.logical['done'] and body.startswith('mBaseDisplayInfo=DisplayInfo{'):
                name = re.match(r'mBaseDisplayInfo=DisplayInfo\{"([^"]*)"', body)
                state = re.search(r'\bstate (\w+)', body)
                size = re.search(r'\breal (\d+ x \d+)', body)
                put(self.report, 'display_states', DisplayState(
                    'Logical Displays', self.logical['id'], clean(state.group(1), 40) if state else '', '', '',
                    clean(name.group(1), 120) if name else '', size.group(1) if size else '', self.logical['line']))
                self.logical['done'] = True
        match = re.match(r'^(\d\d-\d\d \d\d:\d\d:\d\d\.\d+)\s*(?:-|,)\s*(BrightnessEvent:)?\s*(.*)$', body)
        if match and (match.group(2) or 'isUserSetBrightness=' in body):
            stamp, event, rest = match.groups()
            fields = {}
            if event:
                for key, value in re.findall(r'([A-Za-z()%]+)=([^,]*)', rest):
                    fields.setdefault(key, value.strip())
            out = {name: '' for name in ('display', 'state', 'policy', 'brightness', 'nits', 'lux', 'reason', 'strategy')}
            for key, name in _BRIGHTNESS_KEYS:
                if key in fields and not out[name]:
                    out[name] = clean(fields[key], 120)
            put(self.report, 'brightness_events', BrightnessEvent(
                stamp, 'BrightnessEvent' if event else 'brightness change', out['display'], out['state'], out['policy'],
                out['brightness'], out['nits'], out['lux'], out['reason'], out['strategy'], clean(rest, 900), line_no))

    def finish(self):
        self._flush_state()


_FOCUS_KEYS = ('mCurrentFocus', 'mFocusedApp', 'mTopFocusedDisplayId', 'mInputMethodWindow', 'mInputMethodTarget')
_WINDOW_HEAD = re.compile(r'^Window #(\d+) Window\{(\S+) u(\d+) (.*)\}:$')


class WindowReader(base.SectionReader):
    """The window dump: the focus lines of each display and the window list."""
    kind = 'service'
    name = 'window'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.part = ''
        self.display = ''
        self.current = None

    def _flush(self):
        window, self.current = self.current, None
        if window is not None:
            put(self.report, 'windows', WindowRow(
                window['number'], window['title'], window['display'], window['uid'], window['package'], window['pid'],
                window['visibility'], window['surface'], window['ready'], window['screen'], window['visible'], window['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if indent == 0:
            self._flush()
            if body.startswith('WINDOW MANAGER '):
                self.part = ('displays' if '(dumpsys window displays)' in body else
                             'windows' if '(dumpsys window windows)' in body else '')
            return
        if indent == 2 and body.split('=', 1)[0] in _FOCUS_KEYS:
            key, _sep, value = body.partition('=')
            match = re.search(r'(?:^|\W)u\d+ ([\w$]+(?:\.[\w$]+)+)[/}]', value)
            shown = self.display if self.part == 'displays' and key in ('mCurrentFocus', 'mFocusedApp') else ''
            put(self.report, 'window_focus', WindowFocus(
                shown, key, clean(value, 400), match.group(1) if match else '', line_no))
        elif self.part == 'displays':
            if indent == 2 and body.startswith('Display: mDisplayId='):
                self.display = body[len('Display: mDisplayId='):].split(' ', 1)[0]
        elif self.part == 'windows':
            match = _WINDOW_HEAD.match(body) if indent == 2 else None
            if match:
                self._flush()
                self.current = {'number': int(match.group(1)), 'title': clean(match.group(4), 300), 'display': '', 'uid': None,
                                'package': '', 'pid': None, 'visibility': '', 'surface': '', 'ready': '', 'screen': '',
                                'visible': '', 'line': line_no}
                return
            window = self.current
            if window is None:
                return
            if body.startswith('mDisplayId=') and not window['display']:
                window['display'] = body[len('mDisplayId='):].split(' ', 1)[0]
                found = re.search(r'mSession=Session\{\S+ (\d+):', body)
                window['pid'] = int(found.group(1)) if found else None
            elif body.startswith('mOwnerUid='):
                window['uid'] = base.to_int(body[len('mOwnerUid='):].split(' ', 1)[0])
                found = re.search(r'\bpackage=(\S+)', body)
                window['package'] = clean(found.group(1), 200) if found else ''
            elif body.startswith('mViewVisibility=') and not window['visibility']:
                window['visibility'] = body[len('mViewVisibility='):].split(' ', 1)[0]
            elif body.startswith('mHasSurface=') and not window['surface']:
                values = re.findall(r'(mHasSurface|isReadyForDisplay\(\))=(\w+)', body)
                for key, value in values:
                    window['surface' if key == 'mHasSurface' else 'ready'] = value
            elif body.startswith('isOnScreen=') and not window['screen']:
                window['screen'] = body.partition('=')[2]
            elif body.startswith('isVisible=') and not window['visible']:
                window['visible'] = body.partition('=')[2]

    def finish(self):
        self._flush()


class SurfaceFlingerReader(base.SectionReader):
    """The SurfaceFlinger dump: the HWC layer list of each display (name, z, window type, composition type, focus mark).

    The columns are located from the header line the list prints, because the columns differ between builds.
    """
    kind = 'service'
    name = 'SurfaceFlinger'

    def __init__(self, report, section):
        base.SectionReader.__init__(self, report, section)
        self.display = None
        self.columns = None
        self.focus_column = False
        self.name_line = None

    def feed(self, line_no, text):
        stripped = text.rstrip()
        if not stripped.strip():
            return
        match = re.match(r'^Display (\S+).* HWC layers[^:]*:$', stripped)
        if match:
            self.display = match.group(1)
            self.columns = None
            self.name_line = None
            return
        if self.display is None:
            return
        if stripped.startswith(('Display ', 'Displays (', 'SurfaceFlinger global state', 'h/w composer')):
            self.display = None
            return
        if stripped.lstrip().startswith(('---', '- - -', 'Layer name')):
            return
        if ' | ' not in stripped and '|' not in stripped:
            self.name_line = (clean(stripped, 300), line_no)
            return
        parts = [piece.strip() for piece in stripped.split('|')]
        if self.columns is None:
            if 'Window Type' in parts and 'Comp Type' in parts:
                self.columns = {name: parts.index(name) for name in ('Z', 'Window Type', 'Comp Type', 'Transform') if name in parts}
                self.focus_column = '[Focused]' in stripped
            return
        if self.name_line is None:
            return
        index = self.columns
        def part(name):
            return parts[index[name]] if name in index and index[name] < len(parts) else ''
        put(self.report, 'sf_layers', SfLayer(
            self.display, self.name_line[0], ' '.join(part('Z').split()), base.to_int(part('Window Type')), clean(part('Comp Type'), 40),
            base.to_int(part('Transform')), ('true' if '[*]' in parts[-1] else 'false') if self.focus_column else '',
            self.name_line[1]))
        self.name_line = None


# ---------------------------------------------------------------------------------------------
# registration with the shared reader
# ---------------------------------------------------------------------------------------------
READERS = [LocationReader, TimeZoneReader, SensorReader, CameraReader, AudioReader, AudioFlingerReader, MediaSessionReader,
           MediaMetricsReader, AccessibilityReader, InputMethodReader, DisplayReader, WindowReader, SurfaceFlingerReader]
READ_BY = {
    ('service', 'location'): 'Location Providers; Location Last Known; Location Requests; Location Events; Location Usage',
    ('service', 'location_time_zone_manager'): 'Time Zone Detection State',
    ('service', 'sensorservice'): 'Sensors; Sensor Connections; Sensor Registrations; Sensor Events',
    ('service', 'media.camera'): 'Camera Service Events; Camera Devices',
    ('service', 'audio'): 'Audio Events',
    ('service', 'media.audio_flinger'): 'Audio Clients',
    ('service', 'media_session'): 'Media Sessions; Audio Playback Order',
    ('service', 'media.metrics'): 'Media Metrics',
    ('service', 'accessibility'): 'Accessibility Services',
    ('service', 'input_method'): 'Input Methods; Input Start History; Soft Input History',
    ('service', 'display'): 'Display States; Brightness Events',
    ('service', 'window'): 'Window Focus; Windows',
    ('service', 'SurfaceFlinger'): 'SurfaceFlinger Layers',
}


def register():
    """Add the readers and the section index entries to the pass of ``dumpstate_reader`` (once, in any import order)."""
    for reader_class in READERS:
        if reader_class not in base.READERS:
            base.READERS.append(reader_class)
    for key, value in READ_BY.items():
        base.READ_BY.setdefault(key, value)


register()
