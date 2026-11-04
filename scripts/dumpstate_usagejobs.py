"""Section readers for the usage statistics, job scheduler, alarm and notification dumps of an Android bug report.

They plug into the single pass of ``scripts/dumpstate_reader.py``: each reader is a ``SectionReader`` that
receives the lines of one section while that pass runs, keeps bounded rows in tables it adds to the report
(``uj_*`` attributes, created on first use) and never judges what it reads. Nothing here reads the file a
second time.

Sections read:

* ``DUMP OF SERVICE usagestats`` and ``CHECKIN USAGESTATS``: the interval statistics (daily, weekly, monthly,
  yearly) per package, their event aggregations and the app standby states;
* ``DUMP OF SERVICE jobscheduler``: the registered jobs and, where printed, the recently completed jobs;
* ``DUMP OF SERVICE alarm``: the pending alarms, the next alarm clock and the alarm histories;
* ``DUMP OF SERVICE notification``: the notification list, the archive, the listeners and the channels.

The module registers its readers in ``dumpstate_reader.READERS`` when it is imported (the reader module imports
it once, at its end), so it works whichever of the two modules is imported first.
"""
import collections
import re

from scripts import dumpstate_reader as dr

MAX_TEXT = 400
MAX_TAG = 300
MAX_FIELDS = 64          # key=value pairs kept for one alarm
MAX_PENDING = 20000     # characters held while the lines of one entry are joined
STANDBY_HEADING = re.compile(r'^User (\d+) App Standby States:$')

# ---------------------------------------------------------------------------------------------
# Rows
# ---------------------------------------------------------------------------------------------
IntervalRow = collections.namedtuple(
    'IntervalRow', 'section user interval range_text begin end package total_used last_used total_visible last_visible '
                   'last_component total_fs last_fs launches line')
IntervalEvent = collections.namedtuple(
    'IntervalEvent', 'section user interval range_text begin end event count total tail line')
StandbyRow = collections.namedtuple(
    'StandbyRow', 'section user package bucket reason used used_by_user used_scr last_pred expiry last_job '
                  'last_informed next_launch idle other line')
JobRow = collections.namedtuple(
    'JobRow', 'listing namespace uid_label user package job_id label service tag job_type persisted priority requires '
              'network min_latency max_delay extras required satisfied unsatisfied bucket enqueue run_earliest '
              'run_latest last_success last_failure restricted ready completed line')
AlarmRow = collections.namedtuple(
    'AlarmRow', 'listing batch index alarm_type package tag when max_when orig_when window repeat count flags '
                'exact_reason operation listener anchor_ms clock_ms clock_text line')
AlarmHistoryRow = collections.namedtuple(
    'AlarmHistoryRow', 'history uid_label package user alarm_type tag reason rtc_text offset detail anchor_ms line')
NotificationRow = collections.namedtuple(
    'NotificationRow', 'listing package user uid notification_id tag key channel importance importance_note flags '
                       'category group_key ticker seen created updated interrupted visible_since line')
ListenerRow = collections.namedtuple('ListenerRow', 'role listing component package user detail line')
ChannelRow = collections.namedtuple(
    'ChannelRow', 'package uid app_settings channel_id name importance bypass_dnd lockscreen sound lights badge '
                  'vibration deleted deleted_ms group locked_fields line')


def ensure(report):
    """Create the ``uj_*`` tables and counters on a report the first time a reader of this module runs."""
    if not hasattr(report, 'uj_intervals'):
        for name in ('uj_intervals', 'uj_interval_events', 'uj_standby', 'uj_jobs', 'uj_alarms', 'uj_alarm_history',
                      'uj_notifications', 'uj_listeners', 'uj_channels'):
            setattr(report, name, [])
        report.uj_counts = collections.OrderedDict()      # (what, section) -> number, for the log and the notes
        report.uj_anchor = None                           # (nowRTC milliseconds, wall text) of the alarm dump


def counts(report):
    """The counters of a report (``{(what, key): number}``); empty for a report in which no reader of this module ran."""
    return getattr(report, 'uj_counts', {})


def anchor(report):
    """``(nowRTC milliseconds, wall text)`` printed in the alarm dump, or None."""
    return getattr(report, 'uj_anchor', None)


def table(report, name):
    """The rows of one ``uj_*`` table; an empty list for a report in which no reader of this module ran."""
    return getattr(report, name, [])


def count(report, what, key, step=1):
    report.uj_counts[(what, key)] = report.uj_counts.get((what, key), 0) + step


# ---------------------------------------------------------------------------------------------
# Small parsers
# ---------------------------------------------------------------------------------------------
_DURATION = re.compile(r'^([+-]?)(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m(?!s))?(?:(\d+)s)?(?:(\d+)ms)?$')


def duration_ms(text):
    """Milliseconds of a printed duration such as ``-1h7m31s759ms`` or ``+22m30s0ms``; None when it is not one."""
    value = str(text).strip()
    if value in ('0', '+0', '-0'):
        return 0
    match = _DURATION.match(value)
    if not match or not any(match.groups()[1:]):
        return None
    sign, days, hours, minutes, seconds, millis = match.groups()
    total = ((((int(days or 0) * 24 + int(hours or 0)) * 60 + int(minutes or 0)) * 60 + int(seconds or 0)) * 1000
             + int(millis or 0))
    return -total if sign == '-' else total


def clock_text_ms(text):
    """Milliseconds of ``MM:SS`` or ``H:MM:SS`` (the formatted clock the service form prints), or None."""
    parts = str(text).strip().split(':')
    if len(parts) not in (2, 3) or not all(dr.is_digits(part) for part in parts):
        return None
    numbers = [int(part) for part in parts]
    seconds = numbers[-1] + numbers[-2] * 60 + (numbers[0] * 3600 if len(numbers) == 3 else 0)
    return seconds * 1000


def time_amount_ms(text):
    """Milliseconds of a printed amount of time: digits (milliseconds, checkin form) or a clock text (service form)."""
    value = str(text).strip()
    if dr.is_digits(value):
        return int(value)
    return clock_text_ms(value)


def uid_user(label):
    """The Android user of a printed uid (``u11a283`` is user 11, a plain number is its uid divided by 100000), or None."""
    match = re.match(r'^u(\d+)a\d+$', str(label))
    if match:
        return int(match.group(1))
    return int(label) // 100000 if dr.is_digits(str(label)) else None


def _clip(text, size=MAX_TEXT):
    return dr.tidy(text)[:size]


def _indent(text):
    return len(text) - len(text.lstrip(' '))


# ---------------------------------------------------------------------------------------------
# usagestats: interval statistics and app standby states
# ---------------------------------------------------------------------------------------------
_EVENT_AGGREGATION = re.compile(r'^([\w.-]+): (\d+)x for (?:"([^"]*)"|(\S+))(.*)$')
_UNSET_TIMES = frozenset({'0', '', '1970-01-01 00:00:00', '1969-12-31 23:59:59'})
_STANDBY_KNOWN = ('package', 'u', 'bucket', 'reason', 'used', 'usedByUser', 'usedScr', 'lastPred', 'expiryTimes', 'lastJob',
                  'lastInformedBucket', 'nextEstimatedLaunchTime', 'idle')


class UsageIntervalReader(dr.SectionReader):
    """In-memory daily, weekly, monthly and yearly stats per package, event aggregations and App Standby States."""
    label = ''

    def __init__(self, report, section):
        dr.SectionReader.__init__(self, report, section)
        ensure(report)
        self.user = None
        self.mode = ''            # '' | 'interval' | 'standby'
        self.interval = ''
        self.sub = ''             # inside an interval: packages | chooser | config | events
        self.range_text = ''
        self.begin = ''
        self.end = ''
        self.skipped = 0

    def _interval_line(self, line_no, body):
        values = dr.key_values(body)
        total = [values.get(key, '') for key in ('totalTimeUsed', 'totalTimeVisible', 'totalTimeFS')]
        lasts = [values.get(key, '') for key in ('lastTimeUsed', 'lastTimeVisible', 'lastTimeComponentUsed', 'lastTimeFS')]
        launches = dr.to_int(values.get('appLaunchCount'))
        if all((time_amount_ms(value) or 0) == 0 for value in total) and all(value in _UNSET_TIMES for value in lasts) \
                and not launches:
            self.skipped += 1       # nothing but zeros and unset times: counted, not listed
            return
        self.report.add('uj_intervals', IntervalRow(
            self.label, self.user, self.interval, self.range_text, self.begin, self.end, dr.tidy(values.get('package', '')),
            dr.tidy(total[0]), dr.tidy(lasts[0]), dr.tidy(total[1]), dr.tidy(lasts[1]), dr.tidy(lasts[2]),
            dr.tidy(total[2]), dr.tidy(lasts[3]), launches, line_no))

    def _event_line(self, line_no, body):
        match = _EVENT_AGGREGATION.match(body)
        if not match:
            return
        name, number, quoted, bare, tail = match.groups()
        self.report.add('uj_interval_events', IntervalEvent(
            self.label, self.user, self.interval, self.range_text, self.begin, self.end, dr.tidy(name), int(number),
            dr.tidy(quoted if quoted is not None else bare), _clip(tail.strip(), 120), line_no))

    def _standby_line(self, line_no, body):
        values = dr.key_values(body)
        other = ' '.join('%s=%s' % (key, value) for key, value in values.items() if key not in _STANDBY_KNOWN)
        user = dr.to_int(values.get('u'))
        self.report.add('uj_standby', StandbyRow(
            self.label, self.user if user is None else user, dr.tidy(values.get('package', '')),
            dr.tidy(values.get('bucket', '')), dr.tidy(values.get('reason', '')), dr.tidy(values.get('used', '')),
            dr.tidy(values.get('usedByUser', '')), dr.tidy(values.get('usedScr', '')), dr.tidy(values.get('lastPred', '')),
            dr.tidy(values.get('expiryTimes', '')), dr.tidy(values.get('lastJob', '')),
            dr.tidy(values.get('lastInformedBucket', '')), dr.tidy(values.get('nextEstimatedLaunchTime', '')),
            dr.tidy(values.get('idle', '')), _clip(other, 200), line_no))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        if body.startswith('*** SERVICE') and 'DUMP TIMEOUT' in body and self.section.kind == 'command':
            count(self.report, 'cut', self.label)
            return
        indent = _indent(text)
        if indent == 0:
            if body.startswith('user=') and dr.is_digits(body.split()[0][5:]):
                self.user, self.mode, self.interval, self.sub = int(body.split()[0][5:]), '', '', ''
                return
            heading = STANDBY_HEADING.match(body)
            self.mode, self.interval, self.sub = ('standby' if heading else ''), '', ''
            if heading:
                self.user = int(heading.group(1))
            return
        if self.mode == 'standby':
            if body.startswith('package=') and indent in (2, 4):
                self._standby_line(line_no, body)
                return
            if indent == 2 and body.startswith(('totalElapsedTime=', 'totalScreenOnTime=')):
                return
            if indent == 2 and not body.startswith('package='):
                self.mode = ''          # another heading of the user block ends the list
            else:
                return
        if indent == 2:
            if body.startswith('In-memory ') and body.endswith(' stats'):
                self.mode, self.interval, self.sub = 'interval', body.split()[1], ''
                self.range_text = self.begin = self.end = ''
            elif body == 'App Standby States:':
                self.mode, self.interval, self.sub = 'standby', '', ''
            elif self.mode == 'interval' and not self.range_text and not self.begin and body.startswith('timeRange='):
                self.range_text = ' '.join(dr.tidy(body[len('timeRange='):]).strip().strip('"').split())
            elif self.mode == 'interval' and not self.range_text and not self.begin and body.startswith('beginTime='):
                values = dr.key_values(body)
                self.begin, self.end = dr.tidy(values.get('beginTime', '')), dr.tidy(values.get('endTime', ''))
            else:
                self.mode, self.interval, self.sub = '', '', ''
            return
        if self.mode != 'interval':
            return
        if indent == 4:
            self.sub = {'packages': 'packages', 'ChooserCounts': 'chooser', 'configurations': 'config',
                        'event aggregations': 'events'}.get(body, self.sub)
        elif indent == 6:
            if self.sub == 'packages' and body.startswith('package='):
                self._interval_line(line_no, body)
            elif self.sub == 'events':
                self._event_line(line_no, body)

    def finish(self):
        if self.skipped:
            count(self.report, 'interval_skipped', self.label, self.skipped)


class UsageIntervalServiceReader(UsageIntervalReader):
    kind = 'service'
    name = 'usagestats'
    label = 'DUMP OF SERVICE usagestats'


class UsageIntervalCheckinReader(UsageIntervalReader):
    kind = 'command'
    name = 'CHECKIN USAGESTATS'
    label = 'CHECKIN USAGESTATS'


# ---------------------------------------------------------------------------------------------
# jobscheduler
# ---------------------------------------------------------------------------------------------
_JOB_REGISTERED = re.compile(r'^JOB (?:#|(?P<ns>.+?):)(?P<uid>[^/:\s]+)/(?P<id>-?\d+): (?P<hash>\S+) ?(?P<rest>.*)$')
_JOB_COMPLETED = re.compile(r'^(?P<hash>[0-9a-f]+) (?:\{(?P<ns>[^}]*)\} )?#(?P<uid>[^/\s]+)/(?P<id>-?\d+) ?(?P<rest>.*)$')
_RUN_TIME = re.compile(r'earliest=([^,]+), latest=([^,]+)')
_CONSTRAINTS = re.compile(r'^(.*?)(?: \[0x[0-9a-f]+\])?$')


class JobReader(dr.SectionReader):
    """Registered jobs and recently completed jobs of the jobscheduler dump."""
    kind = 'service'
    name = 'jobscheduler'

    def __init__(self, report, section):
        dr.SectionReader.__init__(self, report, section)
        ensure(report)
        self.listing = ''
        self.job = None
        self.attr = 0             # indent of the attribute lines of the job being read
        self.in_info = False
        self.completed = ''
        self.registered_seen = 0
        self.expected = None

    def _flush(self):
        job = self.job
        self.job = None
        if job is None:
            return
        info = job['info']
        kept = [job['listing'], job['namespace'], job['uid_label'], job['user'], job['package'], job['job_id'], job['label'],
                info.get('service', ''), job['tag'], info.get('type', ''), info.get('persisted', ''), info.get('priority', ''),
                info.get('requires', ''), info.get('network', ''), info.get('min_latency', ''), info.get('max_delay', ''),
                info.get('extras', ''), job.get('required', ''), job.get('satisfied', ''), job.get('unsatisfied', ''),
                job.get('bucket', ''), job.get('enqueue', ''), job.get('run_earliest', ''), job.get('run_latest', ''),
                job.get('last_success', ''), job.get('last_failure', ''), job.get('restricted', ''), job.get('ready', ''),
                job['completed'], job['line']]
        self.report.add('uj_jobs', JobRow(*kept))
        if job['listing'] == 'Registered':
            self.registered_seen += 1

    def _start(self, match, listing, line_no, completed=''):
        self._flush()
        self.attr = 4 if listing == 'Registered' else 6
        self.in_info = False
        self.job = {'listing': listing, 'namespace': dr.tidy(match.group('ns') or ''), 'uid_label': dr.tidy(match.group('uid')),
                    'user': None, 'package': '', 'job_id': dr.to_int(match.group('id')), 'label': _clip(match.group('rest'), MAX_TAG),
                    'tag': '', 'info': {}, 'completed': completed, 'line': line_no}

    def _info_line(self, body):
        info = self.job['info']
        if body.startswith('Service:'):
            info['service'] = _clip(body[len('Service:'):].strip(), MAX_TAG)
        elif body.startswith('PERIODIC'):
            info['type'] = _clip(body, 160)
        elif body == 'PERSISTED':
            info['persisted'] = 'yes'
        elif body.startswith('Priority:'):
            info['priority'] = _clip(body[len('Priority:'):].strip(), 60)
        elif body.startswith('Requires:'):
            info['requires'] = _clip(body[len('Requires:'):].strip(), 120)
        elif body.startswith('Network type:'):
            info['network'] = _clip(body[len('Network type:'):].strip(), MAX_TEXT)
        elif body.startswith('Minimum latency:'):
            info['min_latency'] = _clip(body[len('Minimum latency:'):].strip(), 60)
        elif body.startswith('Max execution delay:'):
            info['max_delay'] = _clip(body[len('Max execution delay:'):].strip(), 60)
        elif body.startswith('Extras:'):
            info['extras'] = _clip(body[len('Extras:'):].strip(), MAX_TEXT)

    def _attribute(self, body):
        job = self.job
        if 'tag=' in body and not job['tag'] and body.split(' ', 1)[-1].startswith('tag='):
            job['tag'] = _clip(body.split('tag=', 1)[1], MAX_TAG)
        elif body.startswith('Source:'):
            values = dr.key_values(body[len('Source:'):])
            job['user'], job['package'] = dr.to_int(values.get('user')), dr.tidy(values.get('pkg', ''))
        elif body.startswith('JobInfo:'):
            self.in_info = True
            return
        elif body.startswith(('Required constraints:', 'Satisfied constraints:', 'Unsatisfied constraints:')):
            head, _, rest = body.partition(':')
            key = {'Required constraints': 'required', 'Satisfied constraints': 'satisfied',
                   'Unsatisfied constraints': 'unsatisfied'}[head]
            job[key] = _clip(_CONSTRAINTS.match(rest.strip()).group(1), 300)
        elif body.startswith('Standby bucket:'):
            job['bucket'] = _clip(body[len('Standby bucket:'):].strip(), 40)
        elif body.startswith('Enqueue time:'):
            job['enqueue'] = _clip(body[len('Enqueue time:'):].strip(), 60)
        elif body.startswith('Run time:'):
            match = _RUN_TIME.search(body)
            if match:
                job['run_earliest'], job['run_latest'] = dr.tidy(match.group(1)), dr.tidy(match.group(2))
        elif body.startswith('Last successful run:'):
            job['last_success'] = _clip(body[len('Last successful run:'):].strip(), 40)
        elif body.startswith('Last failed run:'):
            job['last_failure'] = _clip(body[len('Last failed run:'):].strip(), 40)
        elif body.startswith('Restricted due to:'):
            job['restricted'] = _clip(body[len('Restricted due to:'):].strip(), 80)
        elif body.startswith('Ready:'):
            job['ready'] = _clip(body[len('Ready:'):].strip(), 200)
        self.in_info = False

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = _indent(text)
        if indent == 0:
            self._flush()
            if body.startswith('Registered ') and body.endswith(' jobs:'):
                self.listing = 'Registered'
                self.expected = dr.to_int(body.split()[1])
            elif body == 'Recently completed jobs:':
                self.listing = 'Recently completed'
            else:
                self.listing = ''
            self.completed = ''
            return
        if not self.listing:
            return
        if self.listing == 'Registered':
            if indent == 2:
                match = _JOB_REGISTERED.match(body) if body.startswith('JOB ') else None
                if match:
                    self._start(match, 'Registered', line_no)
                else:
                    self._flush()
                return
        elif indent == 2:
            self._flush()
            self.completed = dr.tidy(body) if duration_ms(body) is not None else ''
            return
        elif indent == 6:
            match = _JOB_COMPLETED.match(body)
            if match:
                self._start(match, 'Recently completed', line_no, self.completed)
                return
        if self.job is None:
            return
        if indent == self.attr:
            self._attribute(body)
        elif indent == self.attr + 2 and self.in_info:
            self._info_line(body)

    def finish(self):
        self._flush()
        if self.expected is not None and self.expected != self.registered_seen:
            self.report.warn('jobscheduler: the dump says %d registered jobs, %d were read' % (self.expected, self.registered_seen))


# ---------------------------------------------------------------------------------------------
# alarm
# ---------------------------------------------------------------------------------------------
_ALARM_HEAD = re.compile(r'^(?P<kind>[A-Z_]+) #(?P<index>\d+): Alarm\{(?P<hash>[0-9a-f]+) type (?P<type>-?\d+) (?:origType \S+ )?'
                         r'(?:origWhen (?P<orig>\S+) whenElapsed (?P<elapsed>\S+)|when (?P<when>\S+)) ?(?P<rest>.*)\}$')
_NOW_RTC = re.compile(r'^nowRTC=(\d+)=(\S+ \S+) nowELAPSED=(\d+)')
_ALARM_CLOCK = re.compile(r'^user:(\d+) pendingSend:(\w+) time:(\d+) = (.*?) = (\S+)$')
_RTC_WALL = re.compile(r'rtc=(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)')
_HISTORY_HEADINGS = {
    'Removal history:': 'Removal', 'Addition history:': 'Addition', 'Delivery history:': 'Delivery',
    'Wakeup Alarm history(screen off):': 'Wakeup (screen off)', 'App Alarm history:': 'App alarm history',
    'Allow while idle history:': 'Allow while idle', 'Allow while idle compat history:': 'Allow while idle (compat)',
}
_ORIG_WHEN = re.compile(r'origWhen=(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?|\S+)')
_ELAPSED_OFFSET = re.compile(r'elapsed=(\S+)(?: ([+-]\d\S*))?')
_HISTORY_TAG = re.compile(r'tag=(.*?)(?= (?:T|F|AC|H|OW|WL|origWhen|elapsed|rtc)=|$)')
_PACKAGE_OFFSETS = re.compile(r'^(?P<package>\S+), u(?P<user>\d+): ?(?P<offsets>.*)$')


class AlarmReader(dr.SectionReader):
    """Pending alarms, the next alarm clock and the history lists of the alarm dump."""
    kind = 'service'
    name = 'alarm'

    def __init__(self, report, section):
        dr.SectionReader.__init__(self, report, section)
        ensure(report)
        self.anchor_ms = None
        self.mode = ''            # pending | batches | history | ''
        self.history = ''
        self.sub = ''             # the uid heading inside a history
        self.batch = ''
        self.alarm = None
        self.removal = None
        self.clock_pending = False

    # -- pending alarms --------------------------------------------------------------------
    def _flush_alarm(self):
        alarm = self.alarm
        self.alarm = None
        if alarm is None:
            return
        values = alarm['values']
        self.report.add('uj_alarms', AlarmRow(
            'Pending alarms', self.batch, alarm['index'], alarm['kind'], alarm['package'], alarm['tag'],
            dr.tidy(values.get('whenElapsed') or values.get('expectedWhenElapsed') or alarm['when']),
            dr.tidy(values.get('maxWhenElapsed') or values.get('expectedMaxWhenElapsed') or ''),
            dr.tidy(values.get('origWhen') or ''), dr.tidy(values.get('window', '')), dr.tidy(values.get('repeatInterval', '')),
            dr.to_int(values.get('count')), dr.tidy(values.get('flags', '')), dr.tidy(values.get('exactAllowReason', '')),
            alarm['operation'], alarm['listener'], self.anchor_ms, None, '', alarm['line']))

    def _alarm_line(self, body):
        alarm = self.alarm
        if body.startswith('tag='):
            alarm['tag'] = _clip(body[4:].rstrip(), MAX_TAG)
        elif body.startswith('operation='):
            alarm['operation'] = _clip(body[len('operation='):], 200)
        elif body.startswith('listener='):
            alarm['listener'] = _clip(body[len('listener='):], 200)
        elif body.startswith(('policyWhenElapsed:', 'idleUntil=')):
            return
        else:
            match = _ORIG_WHEN.search(body)
            if match:
                alarm['values'].setdefault('origWhen', match.group(1))
            for key, value in dr.key_values(body).items():
                if len(alarm['values']) < MAX_FIELDS:
                    alarm['values'].setdefault(key, value)

    def _start_alarm(self, match, line_no):
        self._flush_alarm()
        self.alarm = {'kind': match.group('kind'), 'index': dr.to_int(match.group('index')), 'tag': '', 'operation': '',
                      'listener': '', 'values': {}, 'line': line_no, 'when': match.group('when') or match.group('elapsed') or '',
                      'package': _clip(match.group('rest'), 300)}

    # -- histories -------------------------------------------------------------------------
    def _history_row(self, history, uid_label, package, user, alarm_type, tag, reason, rtc_text, offset, detail, line_no):
        self.report.add('uj_alarm_history', AlarmHistoryRow(
            history, dr.tidy(uid_label), dr.tidy(package), user, dr.tidy(alarm_type), _clip(tag, MAX_TAG), dr.tidy(reason),
            dr.tidy(rtc_text), dr.tidy(offset), _clip(detail, 240), self.anchor_ms, line_no))

    def _flush_removal(self):
        entry = self.removal
        self.removal = None
        if entry is not None:
            self._history_row('Removal', self.sub.rstrip(':'), '', uid_user(self.sub.rstrip(':')), entry.get('type', ''), entry.get('tag', ''),
                              entry.get('reason', ''), entry.get('rtc', ''), entry.get('offset', ''), entry.get('detail', ''),
                              entry['line'])

    def _history_line(self, line_no, body, indent):
        history = self.history
        if history in ('Removal', 'Addition', 'Delivery'):
            if indent == 4 and body.endswith(':') and not body.startswith(('[', '#')):
                self._flush_removal()
                self.sub = body
                return
            if history == 'Removal':
                if indent == 6 and body.startswith('#'):
                    self._flush_removal()
                    fields = body.split(': ', 1)[1] if ': ' in body else ''
                    values = dr.key_values(fields)
                    rtc = _RTC_WALL.search(fields)
                    offset = ''
                    printed = _ELAPSED_OFFSET.search(fields)
                    if printed:
                        raw, extra = printed.groups()
                        if extra and duration_ms(extra) is not None:
                            offset = extra
                        elif not dr.is_digits(raw) and duration_ms(raw) is not None:
                            offset = raw
                    self.removal = {'reason': values.get('Reason', ''), 'offset': offset, 'rtc': rtc.group(1) if rtc else '',
                                    'line': line_no, 'detail': ''}
                elif self.removal is not None and indent >= 8:
                    if body.startswith('type='):
                        values = dr.key_values(body.split(' tag=', 1)[0])
                        self.removal['type'] = values.get('type', '')
                        self.removal['tag'] = body.split(' tag=', 1)[1] if ' tag=' in body else ''
                return
            if indent == 6 and body.startswith('['):
                inner = body.strip('[]')
                tag = _HISTORY_TAG.search(inner)
                rtc = _RTC_WALL.search(inner)
                detail = _HISTORY_TAG.sub('', inner).replace(rtc.group(0), '') if rtc else _HISTORY_TAG.sub('', inner)
                self._history_row(history, self.sub.rstrip(':'), '', uid_user(self.sub.rstrip(':')), '',
                                  tag.group(1) if tag else '', '', rtc.group(1) if rtc else '', '', ' '.join(detail.split()),
                                  line_no)
            return
        if history == 'Wakeup (screen off)':
            if indent == 4 and body.startswith('rtc='):
                rtc = _RTC_WALL.search(body)
                values = dr.key_values(body.split(' tag=', 1)[0])
                self._history_row(history, values.get('uid', ''), '', uid_user(values.get('uid', '')), '', body.split(' tag=', 1)[1] if ' tag=' in body else '',
                                  '', rtc.group(1) if rtc else '', '', '', line_no)
            return
        if indent == 4:
            match = _PACKAGE_OFFSETS.match(body)
            if not match:
                return
            offsets = [part.strip() for part in match.group('offsets').split(',') if part.strip()]
            for offset in offsets:
                self._history_row(history, '', match.group('package'), int(match.group('user')), '', '', '', '', offset, '',
                                  line_no)

    # -- lines -----------------------------------------------------------------------------
    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = _indent(text)
        if indent == 0:
            if body.startswith('Batch{') and self.mode in ('batches', 'pending'):
                self._flush_alarm()
                self.batch = dr.tidy(body.split('{', 1)[1].split(' ', 1)[0])
                self.mode = 'batches'
                return
            self._flush_alarm()
            self._flush_removal()
            self.mode = self.history = ''
            return
        if indent == 2:
            self._flush_alarm()
            self._flush_removal()
            match = _NOW_RTC.match(body)
            if match:
                self.anchor_ms = int(match.group(1))
                self.report.uj_anchor = (self.anchor_ms, match.group(2))
            self.clock_pending = body.startswith('Next alarm clock information:')
            self.mode = ''
            self.history = ''
            self.sub = ''
            if body.endswith(' pending alarms:') or body.startswith('Pending alarm batches:'):
                self.mode = 'pending' if body.endswith(' pending alarms:') else 'batches'
                self.batch = ''
            elif body in _HISTORY_HEADINGS:
                self.mode, self.history = 'history', _HISTORY_HEADINGS[body]
            return
        if self.clock_pending and indent == 4:
            match = _ALARM_CLOCK.match(body)
            if match:
                self.report.add('uj_alarms', AlarmRow(
                    'Next alarm clock', '', None, 'user %s' % match.group(1), '', '', dr.tidy(match.group(3)), '', '', '', '',
                    None, '', '', '', '', self.anchor_ms, int(match.group(3)), dr.tidy(match.group(4)), line_no))
            return
        if self.mode in ('pending', 'batches'):
            if indent == 4:
                match = _ALARM_HEAD.match(body)
                if match:
                    self._start_alarm(match, line_no)
                    return
            if self.alarm is not None and indent >= 6:
                self._alarm_line(body)
        elif self.mode == 'history':
            self._history_line(line_no, body, indent)

    def finish(self):
        self._flush_alarm()
        self._flush_removal()


# ---------------------------------------------------------------------------------------------
# notification
# ---------------------------------------------------------------------------------------------
_RECORD_HEAD = re.compile(r'^NotificationRecord\(0x[0-9a-f]+: pkg=(?P<pkg>\S+) user=UserHandle\{(?P<user>-?\d+)\} '
                          r'id=(?P<id>-?\d+) tag=(?P<tag>.*?) importance=(?P<importance>-?\d+) key=')
_SBN = re.compile(r'^StatusBarNotification\(pkg=(?P<pkg>\S+) user=UserHandle\{(?P<user>-?\d+)\} id=(?P<id>-?\d+) '
                  r'tag=(?P<tag>.*?) key=(?P<key>.*?): Notification\(channel=(?P<channel>\S*)(?P<tail>.*)\)\)$')
_CHANNEL_FIELD = re.compile(r', (?=m[A-Z])')
_ARCHIVE_COUNT = re.compile(r'^mArchive=Archive \((\d+) notifications?\)')
_COMPONENT = re.compile(r'^ComponentInfo\{([^}]*)\}(.*)$')
_ALLOWED_TAIL = re.compile(r'^(.*?) \(user: (-?\d+)(.*)\)$')
_LIVE_TAIL = re.compile(r'^\(user (-?\d+)\):? ?(.*)$')
_SETTINGS = re.compile(r'^AppSettings: (?P<pkg>\S+) \((?P<uid>\d+)\)(?P<rest>.*)$')
_LISTENER_HEADINGS = (
    ('Allowed notification ', 'Allowed'), ('All notification ', 'Enabled for current profiles'),
    ('Live notification ', 'Live'), ('Snoozed notification ', 'Snoozed'))
_NOTIFICATION_TIMES = ('mCreationTimeMs', 'mUpdateTimeMs', 'mInterruptionTimeMs', 'mVisibleSinceMs')


def _package_of(component):
    return component.split('/', 1)[0] if '/' in component else component


def channel_fields(text):
    """The fields of a ``NotificationChannel{...}`` text: only the ones the artifact lists."""
    inner = text[len('NotificationChannel{'):]
    if inner.endswith('}'):
        inner = inner[:-1]
    found = {}
    channel_id = inner.find("mId='")
    if channel_id >= 0:
        end = inner.find("', mName=", channel_id)
        found['mId'] = inner[channel_id + 5:end if end >= 0 else len(inner)]
    name_at = inner.find(', mName=')
    if name_at >= 0:
        end = inner.find(', mDescription=', name_at)
        found['mName'] = inner[name_at + len(', mName='):end if end >= 0 else len(inner)]
    for key in ('mImportance', 'mBypassDnd', 'mLockscreenVisibility', 'mLights', 'mShowBadge', 'mVibrationEnabled', 'mDeleted',
                'mDeletedTimeMs', 'mUserLockedFields'):
        match = re.search(r'(?:^|, )%s=([^,}]*)' % key, inner)
        if match:
            found[key] = match.group(1)
    sound = re.search(r', mSound=([^,]*)', inner)
    if sound:
        found['mSound'] = sound.group(1)
    group = re.search(r", mGroup='(.*?)'(?:, |$)", inner)
    if group:
        found['mGroup'] = group.group(1)
    return found


class NotificationReader(dr.SectionReader):
    """Notification list, archive, listeners, assistants and the per-package channels of the notification dump."""
    kind = 'service'
    name = 'notification'

    def __init__(self, report, section):
        dr.SectionReader.__init__(self, report, section)
        ensure(report)
        self.mode = ''            # records | archive | listeners | prefs | ''
        self.role = ''
        self.listing = ''
        self.record = None
        self.pending_archive = None
        self.pending_record = None
        self.user_heading = None
        self.app = None
        self.listed = 0

    # -- notification list -----------------------------------------------------------------
    def _flush_record(self):
        record = self.record
        self.record = None
        if record is None:
            return
        values = record['values']
        times = []
        for key in _NOTIFICATION_TIMES:
            times.append(dr.tidy(values.get(key, '')))
        note = dr.tidy(values.get('mImportanceExplanation', ''))
        self.report.add('uj_notifications', NotificationRow(
            'Notification list', record['package'], record['user'], dr.to_int(values.get('uid')), record['id'], record['tag'],
            dr.tidy(values.get('key', '')), self._channel_of(record), record['importance'], note,
            dr.tidy(values.get('flags', '')), record['category'], dr.tidy(values.get('groupKey', '')),
            _clip(values.get('tickerText', ''), 120), dr.tidy(values.get('seen', '')), times[0], times[1], times[2], times[3],
            record['line']))

    def _resolve_record(self):
        pending = self.pending_record
        self.pending_record = None
        if pending is None:
            return
        text, line_no = pending
        match = _RECORD_HEAD.match(text)
        if match:
            self._start_record(match, text, line_no)
        else:
            self.report.warn('notification: unreadable record header at line %d' % line_no)

    @staticmethod
    def _channel_of(record):
        values = record['values']
        effective = values.get('effectiveNotificationChannel', '')
        if "mId='" in effective:
            return dr.tidy(effective.split("mId='", 1)[1].split("'", 1)[0])
        return record['channel']

    def _record_line(self, body):
        record = self.record
        key, separator, value = body.partition('=')
        if separator and key in ('uid', 'flags', 'key', 'seen', 'groupKey', 'tickerText', 'mImportanceExplanation',
                                 'effectiveNotificationChannel') + _NOTIFICATION_TIMES:
            record['values'].setdefault(key, value.split(' ', 1)[0] if key == 'uid' else value)

    def _start_record(self, match, body, line_no):
        self._flush_record()
        channel = body.split('Notification(channel=', 1)[1].split(' ', 1)[0].rstrip(')') if 'Notification(channel=' in body else ''
        category = body.split(' category=', 1)[1].split(' ', 1)[0] if ' category=' in body else ''
        self.record = {'package': dr.tidy(match.group('pkg')), 'user': int(match.group('user')), 'id': dr.to_int(match.group('id')),
                       'tag': _clip(match.group('tag'), MAX_TAG), 'importance': dr.to_int(match.group('importance')),
                       'channel': dr.tidy(channel), 'category': dr.tidy(category), 'values': {}, 'line': line_no}

    # -- archive ---------------------------------------------------------------------------
    def _flush_archive(self):
        pending = self.pending_archive
        self.pending_archive = None
        if pending is None:
            return
        text, line_no = pending
        match = _SBN.match(' '.join(text.split('\n')))
        if not match:
            self.report.warn('notification: unreadable archive entry at line %d' % line_no)
            return
        tail = match.group('tail')
        flags = tail.split(' flags=', 1)[1].split(' ', 1)[0] if ' flags=' in tail else ''
        category = tail.split(' category=', 1)[1].split(' ', 1)[0] if ' category=' in tail else ''
        group_key = tail.split(' groupKey=', 1)[1].split(' ', 1)[0] if ' groupKey=' in tail else ''
        self.report.add('uj_notifications', NotificationRow(
            'Archive', dr.tidy(match.group('pkg')), int(match.group('user')), None, dr.to_int(match.group('id')),
            _clip(match.group('tag'), MAX_TAG), _clip(match.group('key'), MAX_TAG), dr.tidy(match.group('channel')), None, '',
            dr.tidy(flags), dr.tidy(category), dr.tidy(group_key), '', '', '', '', '', '', line_no))
        self.listed += 1

    # -- listeners -------------------------------------------------------------------------
    def _listener(self, component, user, detail, line_no):
        component = component.strip()
        if not component:
            return
        self.report.add('uj_listeners', ListenerRow(
            self.role, self.listing, dr.tidy(component), dr.tidy(_package_of(component)), user, _clip(detail, 200), line_no))

    def _listener_line(self, line_no, body, indent):
        if indent == 4:
            self.listing = ''
            self.user_heading = None
            for prefix, listing in _LISTENER_HEADINGS:
                if body.startswith(prefix) and body.endswith(':') and (' listeners' in body or ' assistants' in body):
                    self.listing = listing
                    break
            return
        if not self.listing or indent < 6:
            return
        if self.listing == 'Allowed':
            match = _ALLOWED_TAIL.match(body)
            detail, user = (match.group(3).strip(), int(match.group(2))) if match else ('', None)
            for component in (match.group(1) if match else body).split(':'):
                self._listener(component, user, detail, line_no)
        elif self.listing == 'Enabled for current profiles':
            match = _COMPONENT.match(body)
            self._listener(match.group(1) if match else body, None, match.group(2).strip() if match else '', line_no)
        elif self.listing == 'Live':
            match = _COMPONENT.match(body)
            if match:
                tail = _LIVE_TAIL.match(match.group(2).strip())
                user = int(tail.group(1)) if tail else None
                rest = tail.group(2) if tail else match.group(2).strip()
                self._listener(match.group(1), user, re.sub(r'^\S*@[0-9a-f]+ ?', '', rest), line_no)
        elif self.listing == 'Snoozed':
            if body.startswith('User:'):
                self.user_heading = dr.to_int(body.split(':', 1)[1])
            else:
                component, _, rest = body.partition(' (')
                self._listener(component, self.user_heading, ('(' + rest) if rest else '', line_no)

    # -- channels --------------------------------------------------------------------------
    def _app_line(self, match):
        self.app = {'package': dr.tidy(match.group('pkg')), 'uid': int(match.group('uid')),
                    'settings': _clip(match.group('rest').strip(), 160), 'channels': 0, 'line': 0}

    def _close_app(self):
        app = self.app
        self.app = None
        if app is not None and app['settings'] and not app['channels']:
            self.report.add('uj_channels', ChannelRow(app['package'], app['uid'], app['settings'], '', '', '', '', '', '', '',
                                                      '', '', '', '', '', '', app['line']))

    def _channel_line(self, line_no, body):
        app = self.app
        if app is None:
            return
        fields = channel_fields(body)
        app['channels'] += 1
        deleted_ms = fields.get('mDeletedTimeMs', '')
        self.report.add('uj_channels', ChannelRow(
            app['package'], app['uid'], app['settings'], _clip(fields.get('mId', ''), MAX_TAG), _clip(fields.get('mName', ''), 80),
            dr.tidy(fields.get('mImportance', '')), dr.tidy(fields.get('mBypassDnd', '')),
            dr.tidy(fields.get('mLockscreenVisibility', '')), _clip(fields.get('mSound', ''), 160), dr.tidy(fields.get('mLights', '')),
            dr.tidy(fields.get('mShowBadge', '')), dr.tidy(fields.get('mVibrationEnabled', '')),
            dr.tidy(fields.get('mDeleted', '')), dr.tidy(deleted_ms), _clip(fields.get('mGroup', ''), 120),
            dr.tidy(fields.get('mUserLockedFields', '')), line_no))

    # -- lines -----------------------------------------------------------------------------
    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = _indent(text)
        if body.startswith('AppSettings: ') and indent >= 4:
            self._close_app()
            match = _SETTINGS.match(body)
            if match:
                self._app_line(match)
                self.app['line'] = line_no
            return
        if self.pending_record is not None:
            if indent <= 1 and len(self.pending_record[0]) < MAX_PENDING:
                # a tag with a line break in it continues the header on the next lines of the dump
                self.pending_record = (self.pending_record[0] + ' ' + body, self.pending_record[1])
                return
            self._resolve_record()
        if body.startswith('NotificationChannel{') and indent >= 6:
            self._channel_line(line_no, body)
            return
        if self.pending_archive is not None:
            starts_entry = indent == 4 and body.startswith(('StatusBarNotification(', '...'))
            is_heading = indent == 2 and body.endswith(':')
            if self.pending_archive[0].rstrip().endswith('))') or starts_entry or is_heading                     or len(self.pending_archive[0]) >= MAX_PENDING:
                self._flush_archive()
            else:
                # a tag with a line break in it continues on the next lines of the dump
                self.pending_archive = (self.pending_archive[0] + '\n' + body, self.pending_archive[1])
                return
        if indent == 0:
            if body == 'PackagePreferences:':
                self.mode = 'prefs'
            elif body.startswith('Restored without uid'):
                self._close_app()
                self.mode = ''
            return
        if indent <= 2:
            self._flush_record()
            if indent == 2 or body.startswith('Notification Preferences'):
                self.mode = ''
            match = _ARCHIVE_COUNT.match(body)
            if match and indent == 2:
                self.mode = 'archive'
                count(self.report, 'archive_total', self.section.line, int(match.group(1)))
            elif body == 'Notification List:':
                self.mode = 'records'
            elif body in ('Notification listeners:', 'Notification assistant services:'):
                self.mode = 'listeners'
                self.role = 'Listener' if 'listeners' in body else 'Assistant'
                self.listing = ''
            return
        if self.mode == 'records':
            if indent == 4 and body.startswith('NotificationRecord('):
                self._flush_record()
                self.pending_record = (body, line_no)
            elif self.record is not None and indent >= 6:
                self._record_line(body)
        elif self.mode == 'archive':
            if indent == 4 and body.startswith('StatusBarNotification('):
                self.pending_archive = (body, line_no)
            elif indent == 4 and body == '...':
                count(self.report, 'archive_cut', self.section.line)
        elif self.mode == 'listeners':
            self._listener_line(line_no, body, indent)

    def finish(self):
        self._resolve_record()
        self._flush_record()
        self._flush_archive()
        self._close_app()
        archive_total = self.report.uj_counts.get(('archive_total', self.section.line))
        if archive_total is not None:
            count(self.report, 'archive_listed', self.section.line, self.listed)


READERS = [UsageIntervalServiceReader, UsageIntervalCheckinReader, JobReader, AlarmReader, NotificationReader]
# Which artifacts present each section, for the section index of the Device artifacts.
READ_BY = {
    ('service', 'jobscheduler'): 'Scheduled Jobs',
    ('service', 'alarm'): 'Pending Alarms; Alarm History',
    ('service', 'notification'): 'Notification Records; Notification Listeners; Notification Channels',
}


def register():
    """Add the readers to the pass of ``dumpstate_reader`` once."""
    for reader in READERS:
        if reader not in dr.READERS:
            dr.READERS.append(reader)
    for key, value in READ_BY.items():
        dr.READ_BY.setdefault(key, value)


register()
