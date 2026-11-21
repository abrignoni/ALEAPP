"""Section readers for accounts, sync, backup, users, battery, power, process and memory parts of an Android bug report text.

These readers are registered with ``scripts.dumpstate_reader`` (see the READERS block at the end of that file), which
reads the report text once, in one pass, and hands each line of a section to the readers of that section. A reader
here keeps bounded rows in tables that live on the :class:`~scripts.dumpstate_reader.Report` (``report.ap``); the
artifacts in ``scripts/artifacts/bugreportAccountsPower.py`` present them. Nothing is written and nothing is judged.

The module does not import ``scripts.dumpstate_reader`` at load time (that module imports this one while it is loading):
the readers need only the small helpers below, and the row limit is looked up when the first row is added.
"""
import collections
import re

# ---------------------------------------------------------------------------------------------
# small helpers (the same meaning as the ones in scripts.dumpstate_reader)
# ---------------------------------------------------------------------------------------------
_CONTROL = re.compile('[\x00-\x08\x0b-\x1f\x7f]')
VALUE_CHARS = 2000
LINE_CHARS = 600


def tidy(value):
    """A text value with control characters shown as a space."""
    if value is None:
        return ''
    return _CONTROL.sub(' ', str(value))


def is_digits(text):
    """True for a non-empty text of ASCII digits."""
    return text.isascii() and text.isdigit()


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


def to_float(text, default=None):
    """Float value of a printed number, or ``default`` (nan and inf are not numbers here)."""
    try:
        value = float(str(text).strip().rstrip(','))
    except ValueError:
        return default
    return value if value == value and value not in (float('inf'), float('-inf')) else default


def dash_time(text):
    """``YYYY-MM-DD HH:MM:SS[.mmm]`` from the ``YYYY-MM-DD-HH-MM-SS[-mmm]`` form some dumps print, or ''."""
    found = re.match(r'^(\d{4})-(\d\d)-(\d\d)-(\d\d)-(\d\d)-(\d\d)(?:-(\d{3}))?$', str(text).strip())
    if not found:
        return ''
    year, month, day, hour, minute, second, milli = found.groups()
    return '%s-%s-%s %s:%s:%s%s' % (year, month, day, hour, minute, second, '.' + milli if milli else '')


_DURATION_PART = re.compile(r'(\d+)(d|h|ms|m|s)')
_DURATION_MS = {'d': 86400000, 'h': 3600000, 'm': 60000, 's': 1000, 'ms': 1}


def duration_ms(text):
    """Milliseconds of a printed ``+1d04h32m55s844ms`` (sign and spaces ignored), or None when no part is found."""
    parts = _DURATION_PART.findall(str(text))
    if not parts:
        return None
    return sum(int(number) * _DURATION_MS[unit] for number, unit in parts)


# ---------------------------------------------------------------------------------------------
# tables on the report
# ---------------------------------------------------------------------------------------------
class Tables:
    """The rows of one report, by table name, and the names of the tables that reached the row limit."""

    def __init__(self):
        self.rows = collections.defaultdict(list)
        self.truncated = set()
        self.uid_packages = collections.defaultdict(list)      # batterystats: uid label -> packages of its Apk lines
        self.counts = {}                                       # small counters (lines seen but not listed)


def tables(report):
    """The :class:`Tables` of a report, made on first use."""
    found = report.__dict__.get('ap')
    if found is None:
        found = report.__dict__['ap'] = Tables()
    return found


def rows(report, table):
    """The rows of ``table`` (an empty list when the report has none)."""
    found = report.__dict__.get('ap')
    return found.rows.get(table, []) if found is not None else []


def add(report, table, row):
    """Append to a table unless it holds the row limit of the reader module."""
    from scripts import dumpstate_reader        # pylint: disable=import-outside-toplevel
    state = tables(report)
    held = state.rows[table]
    if len(held) >= dumpstate_reader.MAX_ROWS:
        if table not in state.truncated:
            state.truncated.add(table)
            report.warn('%s: more than %d rows, the rest were not kept' % (table, dumpstate_reader.MAX_ROWS))
        return
    held.append(row)


def bump(report, name, amount=1):
    """Count lines that were seen and not turned into rows."""
    counts = tables(report).counts
    counts[name] = counts.get(name, 0) + amount


class Reader:
    """Base of the readers here: the same interface as ``SectionReader``."""
    kind = ''
    name = ''

    def __init__(self, report, section):
        self.report = report
        self.section = section

    def feed(self, line_no, text):
        """One line of the section body (the header line is not included)."""

    def finish(self):
        """The section ended."""


def _indent(text):
    return len(text) - len(text.lstrip(' '))


def _fact(name, value, line_no):
    return Fact(tidy(name.strip())[:200], tidy(value.strip())[:VALUE_CHARS], line_no)


Fact = collections.namedtuple('Fact', 'name value line')

# ---------------------------------------------------------------------------------------------
# account
# ---------------------------------------------------------------------------------------------
Account = collections.namedtuple('Account', 'user user_name user_flags name account_type line')
AccountEvent = collections.namedtuple('AccountEvent', 'user account_id action time_text uid table key line')
Authenticator = collections.namedtuple('Authenticator', 'user account_type component uid updated line')
AccountVisibility = collections.namedtuple('AccountVisibility', 'user account package value line')


class AccountReader(Reader):
    """``dumpsys account``: the accounts, the account history table, the registered authenticators and the visibility lists."""
    kind = 'service'
    name = 'account'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.user = None
        self.user_name = ''
        self.user_flags = ''
        self.declared = None
        self.listed = 0
        self.mode = ''
        self.account = ''

    def _end_user(self):
        if self.user is not None and self.declared is not None and self.declared != self.listed:
            self.report.warn('account: user %s lists %d accounts and the header says %d' % (self.user, self.listed, self.declared))
        self.declared = None
        self.listed = 0

    def _start_user(self, body):
        self._end_user()
        inner = body[len('User UserInfo{'):-2]
        user, _colon, rest = inner.partition(':')
        name, _colon, flags = rest.rpartition(':')
        self.user = to_int(user, tidy(user))
        self.user_name = tidy(name)[:200]
        self.user_flags = tidy(flags)[:40]
        self.mode = ''
        self.account = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = _indent(text)
        if indent == 0:
            if body.startswith('User UserInfo{') and body.endswith('}:'):
                self._start_user(body)
            elif body.startswith('Account event dump'):
                self._end_user()
                self.user = None
            return
        if self.user is None:
            return
        if indent == 2:
            if body.startswith('Accounts:'):
                self.declared = to_int(body.partition(':')[2])
                self.mode = 'accounts'
            elif body == 'Accounts History':
                self.mode = 'history'
            elif body.startswith('AccountId, Action_Type'):
                pass
            elif body.startswith('RegisteredServicesCache:'):
                self.mode = 'services'
            elif body.startswith('Account visibility'):
                self.mode = 'visibility'
                self.account = ''
            elif body.startswith('Active Sessions'):
                self.mode = ''
            elif self.mode == 'history':
                self._history(line_no, body)
            else:
                self.mode = ''
            return
        if indent == 4:
            if self.mode == 'accounts' and body.startswith('Account {') and body.endswith('}'):
                inner = body[len('Account {'):-1]
                head, _sep, kind = inner.rpartition(', type=')
                name = head[len('name='):] if head.startswith('name=') else head
                self.listed += 1
                add(self.report, 'accounts', Account(self.user, self.user_name, self.user_flags, tidy(name)[:300],
                                                     tidy(kind)[:200], line_no))
            elif self.mode == 'services' and body.startswith('ServiceInfo:'):
                self._service(line_no, body)
            elif self.mode == 'visibility':
                self.account = tidy(body)[:300]
        elif indent >= 6 and self.mode == 'visibility' and self.account:
            package, _sep, value = body.rpartition(', ')
            add(self.report, 'account_visibility', AccountVisibility(self.user, self.account, tidy(package)[:300],
                                                                      tidy(value)[:40], line_no))

    def finish(self):
        self._end_user()

    def _history(self, line_no, body):
        parts = body.split(',')
        if len(parts) >= 6 and parts[1].startswith('action_'):
            add(self.report, 'account_history', AccountEvent(
                self.user, to_int(parts[0], tidy(parts[0])), tidy(parts[1]), tidy(parts[2]), to_int(parts[3], tidy(parts[3])),
                tidy(parts[4]), to_int(parts[5], tidy(parts[5])), line_no))
        else:
            bump(self.report, 'account_history_unread')

    def _service(self, line_no, body):
        kind = body.partition('{type=')[2].partition('}')[0]
        component = body.partition('ComponentInfo{')[2].partition('}')[0]
        uid = body.partition(', uid ')[2].partition(',')[0].strip()
        updated = body.partition('lastUpdateTime ')[2].strip()
        add(self.report, 'authenticators', Authenticator(self.user, tidy(kind)[:200], tidy(component)[:400],
                                                         to_int(uid, tidy(uid)), tidy(updated)[:40], line_no))


# ---------------------------------------------------------------------------------------------
# content (sync manager)
# ---------------------------------------------------------------------------------------------
SyncJob = collections.namedtuple('SyncJob', 'kind job_id account account_type user authority source details line')
SyncStatusRow = collections.namedtuple(
    'SyncStatusRow', 'user account account_type account_state authority syncable enabled loc poll per feed user_req othr total fail cancel '
                     'time success_source success_time failure_source failure_time failure_message backoff line')
SyncHistoryRow = collections.namedtuple(
    'SyncHistoryRow', 'index time_text source duration extra account account_type user authority reason message extras text line')
SyncLastRow = collections.namedtuple(
    'SyncLastRow', 'user account account_type authority time_text result source elapsed reason exemption extras line')

_JOB_A = re.compile(r'^(?P<account>.*?)/(?P<type>\S*) u(?P<user>\d+) \[(?P<authority>[^\]]*)\] (?P<rest>.*)$')
_JOB_B = re.compile(r'^(?P<account>.*?)/ ?u(?P<user>\d+) \((?P<type>\S+) u\d+ \[(?P<authority>[^\]]*)\] (?P<rest>.*)$')
_ACCOUNT_HEAD = re.compile(r'^Account (?P<name>.*) u(?P<user>\d+) (?P<type>\S+)(?: \((?P<state>[^)]*)\))?$')
_ADAPTER_HEAD = re.compile(r'^(?P<account>.*)/(?P<type>\S+) u(?P<user>\d+) \[(?P<authority>.*)\]$')
_RECENT = re.compile(r'^\s*#(\d+)\s*:\s+(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s+(\S+)\s+([\d.]+)s(.*)$')
_NAME_TYPE_USER = re.compile(r'^(?P<name>.*)/(?P<type>\S+) u(?P<user>\d+)$')
_LAST_SYNC = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (\S+) Source=(\S+) Elapsed=(\S+) Reason=(.*?)'
                        r'(?: Exemption=(\S+))? Extras=(.*)$')
HEAD_SKIP = ('Service host process PID', 'Threads in use', 'Client PIDs')
CONTENT_SKIP_HEADS = ('SyncManager Config', 'Sync adapters for', 'Detailed Sync History', 'Observer tree', 'Observer leaking',
                      'Cached content', 'Detailed Statistics')


def split_account(text):
    """``(name, type, user)`` of a ``name/type uN`` text; the whole text as the name when it has another shape."""
    found = _NAME_TYPE_USER.match(text.strip())
    if found:
        return found.group('name'), found.group('type'), to_int(found.group('user'))
    return text.strip(), '', None


class ContentReader(Reader):
    """``dumpsys content``: the sync manager state, its jobs, the adapter status table, the recent history and the per adapter history."""
    kind = 'service'
    name = 'content'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.mode = 'head'
        self.job_kind = ''
        self.block = None           # the account of the status table that is being read
        self.columns = None         # [(name, start)] of the status table header
        self.current = None         # the authority row that is being read
        self.recent = []            # SyncHistoryRow fields as lists, so that mesg= and the extras can be added
        self.extras = {}
        self.adapter = None
        self.in_last = False

    # -- status table --------------------------------------------------------------------------
    def _cells(self, text):
        starts = self.columns
        found = {}
        for number, (name, start) in enumerate(starts):
            stop = starts[number + 1][1] if number + 1 < len(starts) else len(text)
            found[name] = text[start:stop].strip() if start < len(text) else ''
        return found

    def _close_row(self):
        row = self.current
        self.current = None
        if row is None:
            return
        success = failure = ('', '')
        message = ''
        cells = row['syncs']
        number = 0
        while number < len(cells):
            cell = cells[number]
            if cell.endswith(' SUCCESS') and not row['seen_success']:
                row['seen_success'] = True
                success = (cell[:-len(' SUCCESS')], cells[number + 1] if number + 1 < len(cells) else '')
                number += 2
            elif cell.endswith(' FAILURE') and not row['seen_failure']:
                row['seen_failure'] = True
                failure = (cell[:-len(' FAILURE')], cells[number + 1] if number + 1 < len(cells) else '')
                message = cells[number + 2] if number + 2 < len(cells) else ''
                number += 3
            else:
                number += 1
        total = row['total']

        def count(name):
            value = total.get(name, '')
            return to_int(value, tidy(value))
        account = self.block
        add(self.report, 'sync_status', SyncStatusRow(
            account[2], account[0], account[1], account[3], tidy(total.get('Authority', ''))[:200], count('Syncable'),
            tidy(total.get('Enabled', ''))[:20], count('Loc'), count('Poll'), count('Per'), count('Feed'), count('User'),
            count('Othr'), count('Tot'), count('Fail'), count('Can'), tidy(total.get('Time', ''))[:40],
            tidy(success[0])[:40], tidy(success[1])[:40], tidy(failure[0])[:40], tidy(failure[1])[:40], tidy(message)[:200],
            tidy(total.get('Backoff', ''))[:80], row['line']))

    def _status_line(self, line_no, text, body):
        if not text.startswith(' ') and body.startswith('Account '):
            found = _ACCOUNT_HEAD.match(body)
            self._close_row()
            if found:
                self.block = (tidy(found.group('name'))[:300], tidy(found.group('type'))[:200], to_int(found.group('user')),
                              tidy(found.group('state') or '')[:40])
            else:
                self.block = (tidy(body[len('Account '):])[:300], '', None, '')
                bump(self.report, 'sync_account_heading_unread')
            self.columns = None
            return True
        if body.startswith('====='):
            return True
        if body.startswith('Authority'):
            self.columns = [(m.group(0), m.start()) for m in re.finditer(r'\S+(?: \S+)*', text)]
            return True
        if set(body) == {'-'}:
            return True
        if self.columns is None or self.block is None:
            return False
        cells = self._cells(text)
        if cells.get('Authority'):
            self._close_row()
            self.current = {'total': cells, 'syncs': [], 'line': line_no, 'seen_success': False, 'seen_failure': False}
            if cells.get('Last Sync'):
                self.current['syncs'].append(cells['Last Sync'])
        elif self.current is not None and cells.get('Last Sync'):
            self.current['syncs'].append(cells['Last Sync'])
        return True

    # -- recent history ------------------------------------------------------------------------
    def _recent_line(self, line_no, text, body):
        if body.startswith('mesg=') and self.recent:
            self.recent[-1]['message'] = tidy(body[len('mesg='):])[:300]
            return
        found = _RECENT.match(text)
        if not found:
            return
        rest = found.group(5)
        head = rest[:12]
        if len(head) == 12 and head.endswith('  ') and not rest[12:13].isspace():
            extra, tail = head.strip(), rest[12:]
        else:
            extra, tail = '', rest.strip()
        parts = re.match(r'^(?P<account>.*?)\s+(?P<authority>\S+)\s+(?P<reason>\S+)\s*$', tail.strip())
        account, authority, reason = (parts.group('account'), parts.group('authority'), parts.group('reason')) if parts else (tail.strip(), '', '')
        name, kind, user = split_account(account)
        self.recent.append({'index': to_int(found.group(1)), 'time': found.group(2), 'source': found.group(3),
                            'duration': found.group(4), 'extra': extra, 'account': name, 'type': kind, 'user': user,
                            'authority': authority, 'reason': reason, 'message': '', 'text': text.strip()[:LINE_CHARS],
                            'line': line_no})

    def _extras_line(self, text):
        found = re.match(r'^\s*#(\d+)\s*:', text)
        if found:
            at = text.find('Bundle[')
            self.extras[to_int(found.group(1))] = tidy(text[at:] if at >= 0 else '')[:VALUE_CHARS]

    # -- the dump ------------------------------------------------------------------------------
    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        top = not text.startswith(' ')
        if top:
            if body.startswith(HEAD_SKIP):
                return
            if body.startswith(('Active Syncs:', 'Pending Syncs:', 'Periodic Syncs:')):
                self.mode = 'jobs'
                self.job_kind = body.split(' ', 1)[0]
                add(self.report, 'sync_facts', Fact(tidy(body.partition(':')[0]), tidy(body.partition(':')[2].strip()), line_no))
                return
            heading = {'Sync Status': 'status', 'Recent Sync History': 'recent', 'Recent Sync History Extras': 'extras',
                       'Sync Statistics': 'stats', 'Per Adapter History': 'adapters'}.get(body)
            if heading is not None or body.startswith(CONTENT_SKIP_HEADS):
                if self.mode == 'status':
                    self._close_row()
                self.mode = heading or 'skip'
                self.in_last = False
                return
        mode = self.mode
        if mode == 'status':
            self._status_line(line_no, text, body)
        elif mode == 'recent':
            self._recent_line(line_no, text, body)
        elif mode == 'extras':
            self._extras_line(text)
        elif mode == 'jobs' and body.startswith('JobId='):
            self._job(line_no, body)
        elif mode == 'stats':
            name, _sep, value = body.partition(':')
            if _sep:
                add(self.report, 'sync_facts', Fact('Sync Statistics: ' + tidy(name), tidy(value.strip())[:VALUE_CHARS], line_no))
        elif mode == 'adapters':
            self._adapter_line(line_no, text, body)
        elif mode == 'head' and top and ': ' in body:
            name, _sep, value = body.partition(': ')
            add(self.report, 'sync_facts', Fact(tidy(name)[:200], tidy(value.strip())[:VALUE_CHARS], line_no))

    def _job(self, line_no, body):
        job_id, _sep, rest = body[len('JobId='):].partition(' ')
        found = _JOB_A.match(rest) or _JOB_B.match(rest)
        if not found:
            add(self.report, 'sync_jobs', SyncJob(self.job_kind, to_int(job_id), '', '', None, '', '', tidy(rest)[:VALUE_CHARS], line_no))
            return
        detail = found.group('rest')
        source, _sep, details = detail.partition(' ')
        add(self.report, 'sync_jobs', SyncJob(self.job_kind, to_int(job_id), tidy(found.group('account'))[:300],
                                              tidy(found.group('type'))[:200], to_int(found.group('user')),
                                              tidy(found.group('authority'))[:200], tidy(source)[:40],
                                              tidy(details)[:VALUE_CHARS], line_no))

    def _adapter_line(self, line_no, text, body):
        indent = _indent(text)
        if indent == 2:
            found = _ADAPTER_HEAD.match(body)
            self.adapter = (tidy(found.group('account'))[:300], tidy(found.group('type'))[:200], to_int(found.group('user')),
                            tidy(found.group('authority'))[:200]) if found else None
            self.in_last = False
        elif indent == 4:
            self.in_last = body == 'Last syncs:'
        elif indent >= 6 and self.in_last and self.adapter is not None:
            found = _LAST_SYNC.match(body)
            if found:
                account, kind, user, authority = self.adapter
                time_text, result, source, elapsed, reason, exemption, extras = found.groups()
                add(self.report, 'sync_last', SyncLastRow(user, account, kind, authority, time_text, tidy(result)[:40],
                                                          tidy(source)[:40], tidy(elapsed)[:40], tidy(reason)[:200],
                                                          tidy(exemption or '')[:40], tidy(extras)[:VALUE_CHARS], line_no))
            elif body != 'N/A':
                bump(self.report, 'sync_last_unread')

    def finish(self):
        if self.mode == 'status':
            self._close_row()
        for item in self.recent:
            add(self.report, 'sync_history', SyncHistoryRow(
                item['index'], item['time'], tidy(item['source'])[:40], tidy(item['duration'])[:20], tidy(item['extra'])[:40],
                tidy(item['account'])[:300], tidy(item['type'])[:200], item['user'], tidy(item['authority'])[:200],
                tidy(item['reason'])[:200], item['message'], self.extras.get(item['index'], ''), tidy(item['text']), item['line']))


# ---------------------------------------------------------------------------------------------
# backup
# ---------------------------------------------------------------------------------------------
BackupTransport = collections.namedtuple('BackupTransport', 'kind name current destination intent line')
BackupPackageState = collections.namedtuple('BackupPackageState', 'transport package state_bytes line')
BackupParticipant = collections.namedtuple('BackupParticipant', 'uid package line')
BackupQueueRow = collections.namedtuple('BackupQueueRow', 'queue package value line')
BackupFact = collections.namedtuple('BackupFact', 'name value line')
BACKUP_LISTS = {'Transport whitelist:': 'whitelist', 'Available transports:': 'transports', 'Participants:': 'participants'}


class BackupReader(Reader):
    """``dumpsys backup``: the manager state, the transports, the participants and the two queues."""
    kind = 'service'
    name = 'backup'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.mode = ''
        self.uid = None
        self.transport = None       # the transport row that is being read: a dict
        self.queue = ''

    def _close_transport(self):
        item = self.transport
        self.transport = None
        if item is not None:
            add(self.report, 'backup_transports', BackupTransport(
                'Available', item['name'], item['current'], item['destination'], item['intent'], item['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = _indent(text)
        if indent == 0:
            self._close_transport()
            self.queue = ''
            if body in BACKUP_LISTS:
                self.mode = BACKUP_LISTS[body]
                return
            name, separator, value = body.partition(':')
            if body.startswith(('Pending key/value backup', 'Full backup queue')):
                self.mode = 'queue'
                self.queue = tidy(name)
                add(self.report, 'backup_facts', BackupFact(tidy(name), tidy(value.strip()), line_no))
                return
            self.mode = ''
            if body.startswith(HEAD_SKIP):
                return
            if name == 'Last backup pass started' and separator:
                started, _sep, now = value.partition('(now =')
                add(self.report, 'backup_facts', BackupFact('Last backup pass started', tidy(started.strip()), line_no))
                if now:
                    add(self.report, 'backup_facts', BackupFact('now (in the Last backup pass started line)', tidy(now.rstrip(') ').strip()), line_no))
            elif separator:
                add(self.report, 'backup_facts', BackupFact(tidy(name)[:200], tidy(value.strip())[:VALUE_CHARS], line_no))
            else:
                add(self.report, 'backup_facts', BackupFact('Statement', tidy(body)[:VALUE_CHARS], line_no))
            return
        if indent == 2 and body.startswith('next scheduled:'):
            add(self.report, 'backup_facts', BackupFact('next scheduled', tidy(body.partition(':')[2].strip()), line_no))
            return
        mode = self.mode
        if mode == 'whitelist':
            add(self.report, 'backup_transports', BackupTransport('Whitelist', tidy(body)[:300], False, '', '', line_no))
        elif mode == 'transports':
            self._transport_line(line_no, body, indent)
        elif mode == 'participants':
            if indent == 2 and body.startswith('uid:'):
                self.uid = to_int(body[4:], tidy(body[4:].strip()))
            elif indent >= 4 and self.uid is not None:
                add(self.report, 'backup_participants', BackupParticipant(self.uid, tidy(body)[:300], line_no))
        elif mode == 'queue':
            if body.startswith('BackupRequest{pkg=') and body.endswith('}'):
                add(self.report, 'backup_queues', BackupQueueRow(self.queue, tidy(body[len('BackupRequest{pkg='):-1])[:300], '', line_no))
            elif ' : ' in body:
                value, _sep, package = body.partition(' : ')
                add(self.report, 'backup_queues', BackupQueueRow(self.queue, tidy(package.strip())[:300], tidy(value.strip())[:40], line_no))
            else:
                bump(self.report, 'backup_queue_unread')

    def _transport_line(self, line_no, body, indent):
        if indent <= 4:
            self._close_transport()
            current = body.startswith('* ')
            self.transport = {'name': tidy(body[2:] if current else body)[:300], 'current': current, 'destination': '',
                              'intent': '', 'line': line_no}
        elif self.transport is not None:
            if body.startswith('destination:'):
                self.transport['destination'] = tidy(body[len('destination:'):].strip())[:300]
            elif body.startswith('intent:'):
                self.transport['intent'] = tidy(body[len('intent:'):].strip())[:400]
            elif body.endswith(' state bytes') and ' - ' in body:
                package, _sep, size = body[:-len(' state bytes')].rpartition(' - ')
                add(self.report, 'backup_package_state', BackupPackageState(
                    self.transport['name'], tidy(package)[:300], to_int(size, tidy(size)), line_no))

    def finish(self):
        self._close_transport()


# ---------------------------------------------------------------------------------------------
# user
# ---------------------------------------------------------------------------------------------
UserRow = collections.namedtuple(
    'UserRow', 'user_id name flags_hex serial primary parent user_type flags state created last_logged_in start_time '
               'unlock_time last_foreground profile_owner restrictions effective_restrictions line')
USER_RESTRICTION_HEADS = {'Restrictions:': 'restrictions', 'Effective restrictions:': 'effective',
                          'Device policy restrictions:': 'device', 'Device policy global restrictions:': 'device',
                          'Device policy local restrictions:': 'device'}


class UserReader(Reader):
    """``dumpsys user``: one record per ``UserInfo`` and the facts the dump prints about the user manager."""
    kind = 'service'
    name = 'user'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.user = None
        self.sub = ''
        self.facts_list = ''

    def _close_user(self):
        user = self.user
        self.user = None
        if user is None:
            return
        attrs = user['attrs']
        add(self.report, 'users', UserRow(
            user['id'], user['name'], user['flags_hex'], user['serial'], user['primary'], user['parent'],
            attrs.get('Type', ''), attrs.get('Flags', ''), attrs.get('State', ''), attrs.get('Created', ''),
            attrs.get('Last logged in', ''), attrs.get('Start time', ''), attrs.get('Unlock time', ''),
            attrs.get('Last entered foreground', ''), attrs.get('Has profile owner', ''),
            ', '.join(user['lists'].get('restrictions', [])), ', '.join(user['lists'].get('effective', [])), user['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(HEAD_SKIP):
            return
        indent = _indent(text)
        if body.startswith('UserInfo{') and indent == 2:
            self._close_user()
            inner, _sep, tail = body[len('UserInfo{'):].partition('}')
            user_id, _colon, rest = inner.partition(':')
            name, _colon, flags = rest.rpartition(':')
            values = {}
            for token in tail.split():
                key, equals, value = token.partition('=')
                if equals:
                    values[key] = value
            self.user = {'id': to_int(user_id, tidy(user_id)), 'name': tidy(name)[:200], 'flags_hex': tidy(flags)[:40],
                         'serial': to_int(values.get('serialNo')), 'primary': tidy(values.get('isPrimary', ''))[:10],
                         'parent': to_int(values.get('parentId')), 'attrs': {}, 'lists': {}, 'line': line_no}
            self.sub = ''
            self.facts_list = ''
            return
        if indent <= 2 and not body.startswith('Users:'):
            self._close_user()
            self.facts_list = ''
            name, separator, value = body.partition(':')
            if separator and value.strip():
                add(self.report, 'user_facts', Fact(tidy(name)[:200], tidy(value.strip())[:VALUE_CHARS], line_no))
            elif separator:
                self.facts_list = tidy(name)[:200]
                add(self.report, 'user_facts', Fact(self.facts_list, '', line_no))
            return
        if self.user is None:
            if indent >= 4 and self.facts_list:
                last = tables(self.report).rows['user_facts']
                if last and last[-1].name == self.facts_list:
                    last[-1] = last[-1]._replace(value=(last[-1].value + ', ' + tidy(body)).strip(', ')[:VALUE_CHARS])
            return
        if indent == 4:
            name, separator, value = body.partition(':')
            self.sub = USER_RESTRICTION_HEADS.get(body, '')
            if separator and not self.sub:
                self.user['attrs'][tidy(name)] = tidy(value.strip())[:VALUE_CHARS]
            elif not separator:
                self.sub = ''
        elif indent >= 6 and self.sub in ('restrictions', 'effective'):
            self.user['lists'].setdefault(self.sub, []).append(tidy(body)[:100])

    def finish(self):
        self._close_user()


# ---------------------------------------------------------------------------------------------
# battery service, thermal service
# ---------------------------------------------------------------------------------------------
class BatteryServiceReader(Reader):
    """``dumpsys battery``: the ``name: value`` lines of the Battery Service state."""
    kind = 'service'
    name = 'battery'

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(HEAD_SKIP) or ': ' not in body:
            return
        name, _sep, value = body.partition(': ')
        add(self.report, 'battery_facts', _fact(name, value, line_no))


ThermalRow = collections.namedtuple('ThermalRow', 'group kind name item_type value status detail line')
_THERMAL_ITEM = re.compile(r'^(Temperature|CoolingDevice|TemperatureThreshold)\{(.*)\}$')


class ThermalReader(Reader):
    """``dumpsys thermalservice``: status lines, the temperatures, cooling devices and thresholds the dump prints."""
    kind = 'service'
    name = 'thermalservice'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.group = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(HEAD_SKIP):
            return
        found = _THERMAL_ITEM.match(body)
        if found:
            kind = {'Temperature': 'Temperature', 'CoolingDevice': 'Cooling Device',
                    'TemperatureThreshold': 'Threshold'}[found.group(1)]
            inner = found.group(2)
            if kind == 'Threshold':
                name = inner.partition('mName=')[2].partition(',')[0]
                item_type = inner.partition('mType=')[2].partition(',')[0]
                detail = inner.partition('mName=')[2].partition(',')[2].strip()
                add(self.report, 'thermal', ThermalRow(self.group, kind, tidy(name), tidy(item_type), '', '', tidy(detail)[:VALUE_CHARS], line_no))
            else:
                values = {}
                for part in inner.split(', '):
                    key, equals, value = part.partition('=')
                    if equals:
                        values[key] = value
                add(self.report, 'thermal', ThermalRow(self.group, kind, tidy(values.get('mName', '')), tidy(values.get('mType', '')),
                                                       tidy(values.get('mValue', '')), tidy(values.get('mStatus', '')), '', line_no))
            return
        if body.startswith('['):
            add(self.report, 'thermal', ThermalRow(self.group, 'Status', 'Values', '', tidy(body)[:200], '', '', line_no))
        elif not text.startswith((' ', '\t')):
            name, separator, value = body.partition(':')
            if separator and value.strip():
                self.group = ''
                add(self.report, 'thermal', ThermalRow('', 'Status', tidy(name)[:200], '', tidy(value.strip())[:200], '', '', line_no))
            else:
                self.group = tidy(name)[:200]
        elif ':' in body and not body.endswith(':'):
            name, _sep, value = body.partition(':')
            add(self.report, 'thermal', ThermalRow(self.group, 'Status', tidy(name)[:200], '', tidy(value.strip())[:200], '', '', line_no))
        else:
            bump(self.report, 'thermal_unread')


# ---------------------------------------------------------------------------------------------
# power
# ---------------------------------------------------------------------------------------------
PowerFact = collections.namedtuple('PowerFact', 'block name value line')
PowerWakeLock = collections.namedtuple('PowerWakeLock', 'level tag flags held uid pid details line')
PowerEvent = collections.namedtuple('PowerEvent', 'kind index time_text uid display state reason foreground caller held level tag details line')
_WAKE_LOCK = re.compile(r"^(?:mLock:\d+ )?(?P<level>[A-Z][A-Z_]*)\s+'(?P<tag>.*)'\s*(?P<flags>[A-Z_ ]*?)\s*ACQ=(?P<held>\S+)\s*(?P<more>.*)$")
_RELEASE = re.compile(r"^\[(?P<index>\d+)\]\s+(?P<time>\d\d-\d\d \d\d:\d\d:\d\d\.\d{3})\s+(?P<held>\S+)\s+(?P<level>[A-Z][A-Z_]*)\s+"
                      r"'(?P<tag>.*)'\s*(?P<more>.*)$")
_WAKE_UP = re.compile(r'^\[(?P<index>\d+)\]\s+(?P<time>\d\d-\d\d \d\d:\d\d:\d\d\.\d{3})\s+(?P<rest>.*)$')
POWER_BLOCKS = {'Power Manager State:': 'Power Manager State', 'Settings and Configuration:': 'Settings and Configuration'}


class PowerReader(Reader):
    """``dumpsys power``: the state and settings lines, the wake locks held when the dump ran and the wake up and release histories."""
    kind = 'service'
    name = 'power'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.mode = ''
        self.block = ''
        self.prefix = ''
        self.history = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(HEAD_SKIP):
            return
        indent = _indent(text)
        if indent == 0:
            self.prefix = ''
            if body in POWER_BLOCKS:
                self.mode, self.block = 'facts', POWER_BLOCKS[body]
            elif body.startswith('Wake Locks:'):
                self.mode = 'wakelocks'
            elif body == 'PowerHistorian:':
                self.mode, self.history = 'history', ''
            else:
                self.mode = ''
                found = re.match(r'^([A-Z][A-Za-z ]+): (-?\d+ ms)$', body)
                if found:
                    add(self.report, 'power_facts', PowerFact('Timeouts', tidy(found.group(1)), tidy(found.group(2)), line_no))
            return
        if self.mode == 'facts':
            self._fact(line_no, body, indent)
        elif self.mode == 'wakelocks' and indent == 2:
            self._wake_lock(line_no, body)
        elif self.mode == 'history':
            self._history(line_no, body, indent)

    def _fact(self, line_no, body, indent):
        if body.endswith(':') and indent == 2:
            self.prefix = body[:-1] + '.'
            return
        if indent == 2:
            self.prefix = ''
        at_equals, at_colon = body.find('='), body.find(': ')
        if at_equals >= 0 and (at_colon < 0 or at_equals < at_colon):
            name, value = body[:at_equals], body[at_equals + 1:]
        elif at_colon >= 0:
            name, value = body[:at_colon], body[at_colon + 2:]
        else:
            return
        add(self.report, 'power_facts', PowerFact(self.block, tidy(self.prefix + name.strip())[:200], tidy(value.strip())[:VALUE_CHARS], line_no))

    def _wake_lock(self, line_no, body):
        found = _WAKE_LOCK.match(body)
        if not found:
            bump(self.report, 'power_wake_lock_unread')
            return
        more = found.group('more')
        uid = re.search(r'\buid=(\d+)', more)
        pid = re.search(r'\bpid=(\d+)', more)
        flags = ' '.join(part for part in (found.group('flags').strip(), more.partition('(')[0].strip()) if part)
        add(self.report, 'power_wake_locks', PowerWakeLock(
            found.group('level'), tidy(found.group('tag'))[:400], tidy(flags)[:100], tidy(found.group('held'))[:40],
            to_int(uid.group(1)) if uid else None, to_int(pid.group(1)) if pid else None, tidy(more)[:VALUE_CHARS], line_no))

    def _history(self, line_no, body, indent):
        if indent == 2 and body.endswith(':'):
            self.history = body[:-1]
            return
        if self.history == 'WakeLock Release History':
            found = _RELEASE.match(body)
            if found:
                more = found.group('more')
                uid = re.search(r'\buid=(\d+)', more)
                add(self.report, 'power_events', PowerEvent(
                    'WakeLock Release', to_int(found.group('index')), found.group('time'), to_int(uid.group(1)) if uid else None,
                    '', '', '', '', '', tidy(found.group('held'))[:40], tidy(found.group('level'))[:60],
                    tidy(found.group('tag'))[:400], tidy(more)[:VALUE_CHARS], line_no))
            elif body:
                bump(self.report, 'power_event_unread')
        elif self.history == 'WakeUp History':
            if body.startswith('No '):
                return
            found = _WAKE_UP.match(body)
            if found:
                tokens = found.group('rest').split()
                if len(tokens) >= 4:
                    add(self.report, 'power_events', PowerEvent(
                        'WakeUp', to_int(found.group('index')), found.group('time'), to_int(tokens[0], tidy(tokens[0])), tidy(tokens[1])[:20],
                        tidy(tokens[2])[:20], tidy(tokens[3])[:100], tidy(tokens[4])[:200] if len(tokens) > 4 else '',
                        tidy(' '.join(tokens[5:]))[:200], '', '', '', '', line_no))
                    return
            bump(self.report, 'power_event_unread')


# ---------------------------------------------------------------------------------------------
# device idle
# ---------------------------------------------------------------------------------------------
IdleFact = collections.namedtuple('IdleFact', 'block name value line')
IdleHistoryRow = collections.namedtuple('IdleHistoryRow', 'position state ago reason line')
_IDLE_PAIR_SPLIT = re.compile(r'\s+(?=m[A-Z][A-Za-z0-9_.]*=)')


class DeviceIdleReader(Reader):
    """``dumpsys deviceidle``: the settings, the idling history and the state lines."""
    kind = 'service'
    name = 'deviceidle'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.mode = ''
        self.position = 0

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(HEAD_SKIP):
            return
        indent = _indent(text)
        if indent == 2 and body.endswith(':') and '=' not in body:
            self.mode = {'Settings:': 'settings', 'Idling history:': 'history'}.get(body, 'list')
            self.position = 0
            return
        if indent == 2:
            self.mode = 'state'
            for pair in _IDLE_PAIR_SPLIT.split(body):
                name, equals, value = pair.partition('=')
                if equals:
                    add(self.report, 'idle_facts', IdleFact('State', tidy(name)[:200], tidy(value.strip())[:VALUE_CHARS], line_no))
            return
        if self.mode == 'settings' and indent == 4 and '=' in body:
            name, _sep, value = body.partition('=')
            add(self.report, 'idle_facts', IdleFact('Settings', tidy(name)[:200], tidy(value.strip())[:VALUE_CHARS], line_no))
        elif self.mode == 'history' and indent >= 4:
            state, separator, rest = body.partition(':')
            if separator:
                ago, _sep, reason = rest.strip().partition(' ')
                add(self.report, 'idle_history', IdleHistoryRow(self.position, tidy(state.strip())[:40], tidy(ago)[:40],
                                                                tidy(reason.strip().strip('()'))[:100], line_no))
                self.position += 1


# ---------------------------------------------------------------------------------------------
# procstats
# ---------------------------------------------------------------------------------------------
ProcStat = collections.namedtuple('ProcStat', 'period period_start process uid version state share measures line')
_PROC_HEAD = re.compile(r'^\* (?P<process>.*) / (?P<uid>\S+) / v(?P<version>\S*):$')
_PROC_STATE = re.compile(r'^(?P<state>[^:]+?):\s+(?P<share>[\d.]+%)(?:\s+\((?P<measures>.*)\))?\s*$')


class ProcStatsReader(Reader):
    """``dumpsys procstats``: the process lines of the committed periods and of the Process summary of the other periods."""
    kind = 'service'
    name = 'procstats'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.period = ''
        self.start = ''
        self.mode = ''
        self.process = None

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(HEAD_SKIP):
            return
        if not text.startswith(' '):
            self.process = None
            if body.startswith('COMMITTED STATS FROM '):
                self.period = tidy(body.rstrip(':'))[:100]
                self.start = body[len('COMMITTED STATS FROM '):].rstrip(':').strip()
                self.mode = 'proc'
            elif body.startswith(('CURRENT STATS', 'AGGREGATED OVER')):
                self.period = tidy(body.rstrip(':'))[:100]
                self.start = ''
                self.mode = ''
            elif body == 'Process summary:':
                self.mode = 'proc'
            else:
                self.mode = ''
            return
        if self.mode != 'proc':
            return
        found = _PROC_HEAD.match(body) if _indent(text) == 2 else None
        if found:
            self.process = (tidy(found.group('process'))[:400], tidy(found.group('uid'))[:40], tidy(found.group('version'))[:40])
            return
        if self.process is not None and _indent(text) >= 4:
            state = _PROC_STATE.match(body)
            if state:
                add(self.report, 'procstats', ProcStat(self.period, self.start, self.process[0], self.process[1], self.process[2],
                                                       tidy(state.group('state'))[:60], state.group('share'),
                                                       tidy(state.group('measures') or '')[:200], line_no))
            else:
                bump(self.report, 'procstats_unread')


# ---------------------------------------------------------------------------------------------
# ps
# ---------------------------------------------------------------------------------------------
PsRow = collections.namedtuple('PsRow', 'label user pid tid ppid vsz rss wchan addr state pri nice rtprio sched policy cpu_time command line')
PS_COLUMNS = {'LABEL': 'label', 'USER': 'user', 'PID': 'pid', 'TID': 'tid', 'PPID': 'ppid', 'VSZ': 'vsz', 'RSS': 'rss',
              'WCHAN': 'wchan', 'ADDR': 'addr', 'S': 'state', 'PRI': 'pri', 'NI': 'nice', 'RTPRIO': 'rtprio', 'SCH': 'sched',
              'PCY': 'policy', 'TIME': 'cpu_time', 'CMD': 'command'}
PS_NUMBERS = ('pid', 'tid', 'ppid', 'vsz', 'rss', 'pri', 'nice')


class PsReader(Reader):
    """``ps -A -T -Z``: one record per thread."""
    kind = 'command'
    name = 'PROCESSES AND THREADS'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.header = None

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        if self.header is None:
            names = body.split()
            if 'PID' in names and 'CMD' in names:
                self.header = [PS_COLUMNS.get(name, '') for name in names]
            else:
                self.report.warn('PROCESSES AND THREADS: the header line was not recognised, no rows were read')
                self.header = []
            return
        if not self.header:
            return
        tokens = body.split(None, len(self.header) - 1)
        if len(tokens) < len(self.header) - 1:
            bump(self.report, 'ps_unread')
            return
        values = dict.fromkeys(PsRow._fields[:-1], '')
        for name, token in zip(self.header, tokens):
            if name:
                values[name] = token
        for name in PS_NUMBERS:
            values[name] = to_int(values[name], tidy(values[name]))
        add(self.report, 'ps', PsRow(*(values[name] if name in PS_NUMBERS else tidy(values[name])[:400] for name in PsRow._fields[:-1]), line_no))


# ---------------------------------------------------------------------------------------------
# meminfo
# ---------------------------------------------------------------------------------------------
MemoryEntry = collections.namedtuple('MemoryEntry', 'basis kilobytes process pid note user swap_kilobytes line')
MemoryProcess = collections.namedtuple(
    'MemoryProcess', 'pid process pss_total private_dirty shared_dirty swap_pss rss_total heap_size heap_alloc heap_free '
                     'native_heap_pss dalvik_heap_pss java_heap native_heap code stack graphics private_other system views '
                     'activities line')
MemoryFact = collections.namedtuple('MemoryFact', 'name value line')
_MEM_ENTRY = re.compile(r'^([\d,]+)K: (.*?) \(pid (\d+)(?: / ([^)]*))?\)\s*(?:\(user (\d+)\))?\s*(?:\(\s*([\d,]+)K in swap\))?$')
_MEM_HEADER = re.compile(r'^\*\* MEMINFO in pid (\d+) \[(.*)\] \*\*$')
_MEM_ROW = re.compile(r'^\s*(?P<label>.*?)\s+(?P<numbers>-?\d+(?:\s+-?\d+)*)\s*$')
MEM_FACT_NAMES = ('Total RAM', 'Free RAM', 'Used RAM', 'Lost RAM', 'ZRAM', 'Tuning', 'DMA-BUF', 'DMA-BUF Heaps', 'DMA-BUF Heaps pool',
                  'GPU', 'Kernel CMA')
MEM_SUMMARY_FIELDS = {'Java Heap': 'java_heap', 'Native Heap': 'native_heap', 'Code': 'code', 'Stack': 'stack',
                      'Graphics': 'graphics', 'Private Other': 'private_other', 'System': 'system'}


class MeminfoReader(Reader):
    """``dumpsys meminfo``: the process lists, the per process blocks and the memory totals the dump prints."""
    kind = 'service'
    name = 'meminfo'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.mode = ''
        self.basis = ''
        self.block = None
        self.header = []
        self.names = []

    def _close_block(self):
        block = self.block
        self.block = None
        if block is None:
            return
        total = block['heap'].get('TOTAL', {})
        if not total and not block['summary']:
            bump(self.report, 'meminfo_blocks_unread')
            return
        summary = block['summary']
        add(self.report, 'memory_processes', MemoryProcess(
            block['pid'], block['process'], total.get('Pss Total'), total.get('Private Dirty'), total.get('Shared Dirty'),
            total.get('SwapPss Dirty'), total.get('Rss Total'), total.get('Heap Size'), total.get('Heap Alloc'),
            total.get('Heap Free'), block['heap'].get('Native Heap', {}).get('Pss Total'),
            block['heap'].get('Dalvik Heap', {}).get('Pss Total'), summary.get('java_heap'), summary.get('native_heap'),
            summary.get('code'), summary.get('stack'), summary.get('graphics'), summary.get('private_other'),
            summary.get('system'), block['objects'].get('Views'), block['objects'].get('Activities'), block['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            if self.mode == 'list':
                self.mode = ''
            return
        header = _MEM_HEADER.match(body)
        if header:
            self._close_block()
            self.block = {'pid': to_int(header.group(1)), 'process': tidy(header.group(2))[:400], 'heap': {}, 'summary': {},
                          'objects': {}, 'line': line_no}
            self.mode, self.header, self.names = 'heap', [], []
            return
        if body.startswith('Total ') and ' by ' in body and body.endswith(':'):
            self._close_block()
            self.basis = body.split(' ')[1] if body.startswith(('Total PSS by process', 'Total RSS by process')) else ''
            self.mode = 'list' if self.basis else ''
            return
        if self.mode == 'list':
            found = _MEM_ENTRY.match(body)
            if found:
                add(self.report, 'memory_entries', MemoryEntry(self.basis, to_int(found.group(1).replace(',', '')), tidy(found.group(2))[:400],
                                                               to_int(found.group(3)), tidy(found.group(4) or '')[:100],
                                                               to_int(found.group(5)), to_int((found.group(6) or '').replace(',', '')), line_no))
            else:
                bump(self.report, 'memory_entry_unread')
            return
        uptime = re.match(r'^Uptime: (\d+) Realtime: (\d+)$', body)
        if uptime:
            add(self.report, 'memory_facts', MemoryFact('Uptime', uptime.group(1), line_no))
            add(self.report, 'memory_facts', MemoryFact('Realtime', uptime.group(2), line_no))
            return
        for name in MEM_FACT_NAMES:
            if body.startswith(name + ':'):
                add(self.report, 'memory_facts', MemoryFact(name, tidy(body[len(name) + 1:].strip())[:VALUE_CHARS], line_no))
                return
        if self.block is not None:
            self._block_line(text, body)

    def _block_line(self, text, body):
        block = self.block
        if body in ('Dalvik Details', 'App Summary', 'Objects', 'SQL', 'DATABASES', 'Asset Allocations', 'Unreachable memory'):
            self.mode = {'App Summary': 'summary', 'Objects': 'objects'}.get(body, '')
            return
        if self.mode == 'heap':
            tokens = body.split()
            if tokens[0] == 'Pss' and 'Heap' in tokens:
                self.header = tokens
                return
            if self.header and tokens[0] == 'Total' and not self.names:
                self.names = [' '.join(pair) for pair in zip(self.header, tokens)]
                return
            found = _MEM_ROW.match(text)
            if found and self.names and not body.startswith('---'):
                label = found.group('label').strip()
                if label in ('Native Heap', 'Dalvik Heap', 'TOTAL'):
                    block['heap'][label] = dict(zip(self.names, [int(number) for number in found.group('numbers').split()]))
        elif self.mode == 'summary':
            found = re.match(r'^([A-Za-z ]+?):\s+(\d+)(?:\s+(\d+))?\s*$', body)
            if found and found.group(1) in MEM_SUMMARY_FIELDS:
                block['summary'][MEM_SUMMARY_FIELDS[found.group(1)]] = int(found.group(2))
        elif self.mode == 'objects':
            for name, number in re.findall(r'([A-Za-z]+(?: [A-Za-z]+)*):\s+(\d+)', body):
                if name in ('Views', 'Activities'):
                    block['objects'][name] = int(number)

    def finish(self):
        self._close_block()


# ---------------------------------------------------------------------------------------------
# batterystats
# ---------------------------------------------------------------------------------------------
BatteryEvent = collections.namedtuple('BatteryEvent', 'form time_text anchor delta_ms level state marker changes line')
DailyPeriod = collections.namedtuple('DailyPeriod', 'kind start end discharge_steps charge_steps totals package_changes line')
PackageChange = collections.namedtuple('PackageChange', 'period_start period_end change package version line')
PowerUse = collections.namedtuple('PowerUse', 'kind name context total detail line')
WakeLockUse = collections.namedtuple('WakeLockUse', 'kind uid name usage line')
_HISTORY_F2 = re.compile(r'^  (\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}) (.*)$')
_HISTORY_F1 = re.compile(r'^\s+(0|\+[0-9a-z]+) \((\d+)\) (.*)$')
_HISTORY_STATE = re.compile(r'^(\d{3}) ([0-9a-fA-F]+)(?: (.*))?$')
_UID_HEAD = re.compile(r'^(?:u\d+[ais]\d+|\d+):$')
_UID_POWER = re.compile(r'^(?:UID|Uid) (?P<name>\S+): (?P<total>-?[\d.]+)(?P<rest>.*)$')
_ITEM_POWER = re.compile(r'^(?P<name>[A-Za-z][A-Za-z_ ]*?): (?P<total>-?[\d.]+)(?P<rest>.*)$')
_WAKE = re.compile(r'^(?P<name>.*?): (?P<usage>\d+[a-z]+ .*)$')
_STEP = re.compile(r'^#\d+:')
BATTERY_HEADS = ('Per-PID Stats:', 'Discharge step durations:', 'Charge step durations:', 'Daily stats:', 'Statistics since last charge',
                 'Per process state tracking', 'Battery History')
MARKERS = (('RESET:', 'Reset'), ('TIME:', 'Clock'), ('SHUTDOWN', 'Shutdown'), ('START', 'Start'), ('*OVERFLOW*', 'Overflow'))


class BatteryStatsReader(Reader):
    """``dumpsys batterystats``: the history, the daily periods, the estimated power use and the wake locks."""
    kind = 'service'
    name = 'batterystats'

    def __init__(self, report, section):
        Reader.__init__(self, report, section)
        self.mode = ''
        self.form = ''
        self.anchor = None          # (wall text, offset ms) of the last clock record
        self.period = None
        self.sub = ''
        self.current_start = ''
        self.stats = ''
        self.uid = ''
        self.last_power = None
        self.context = ''

    # -- history -------------------------------------------------------------------------------
    def _history(self, line_no, text):
        if self.form == 'F2':
            found = _HISTORY_F2.match(text)
            if not found:
                return
            time_text, rest = found.group(1), found.group(2)
            anchor, delta = '', None
        else:
            found = _HISTORY_F1.match(text)
            if not found:
                return
            time_text, rest = found.group(1), found.group(3)
            offset = 0 if time_text == '0' else duration_ms(time_text)
            marker_time = ''
            if rest.startswith(('RESET:TIME: ', 'TIME: ')):
                marker_time = dash_time(rest.rpartition(' ')[2])
            if marker_time and offset is not None:
                self.anchor = (marker_time, offset)
            anchor, delta = (self.anchor[0], offset - self.anchor[1]) if self.anchor and offset is not None else ('', None)
        state_found = _HISTORY_STATE.match(rest)
        if state_found:
            level, state, changes = int(state_found.group(1)), state_found.group(2).lower(), state_found.group(3) or ''
        else:
            level, state, changes = None, '', rest        # a clock, reset, shutdown or start record carries no level and no state
        marker = ''
        for prefix, label in MARKERS:
            if changes.startswith(prefix):
                marker = label
                break
        add(self.report, 'battery_history', BatteryEvent(self.form, time_text, anchor, delta, level, state, marker,
                                                         tidy(changes)[:VALUE_CHARS], line_no))

    # -- daily ---------------------------------------------------------------------------------
    def _close_period(self):
        period = self.period
        self.period = None
        if period is not None:
            add(self.report, 'battery_daily', DailyPeriod(
                period['kind'], period['start'], period['end'], period['discharge'], period['charge'],
                ' | '.join(period['totals'])[:VALUE_CHARS], period['changes'], period['line']))

    def _daily(self, line_no, text, body):
        indent = _indent(text)
        if indent == 2:
            if body.startswith('Current start time:'):
                self.current_start = body.partition(':')[2].strip()
            elif body.startswith('Current daily '):
                if self.period is None or self.period['kind'] != 'Current':
                    self._close_period()
                    self.period = {'kind': 'Current', 'start': self.current_start, 'end': '', 'discharge': 0, 'charge': 0,
                                   'totals': [], 'changes': 0, 'line': line_no}
                self.sub = 'discharge' if 'discharge' in body else 'charge'
            elif body.startswith('Daily from ') and body.endswith(':'):
                self._close_period()
                start, _sep, end = body[len('Daily from '):-1].partition(' to ')
                self.period = {'kind': 'Daily', 'start': start.strip(), 'end': end.strip(), 'discharge': 0, 'charge': 0,
                               'totals': [], 'changes': 0, 'line': line_no}
                self.sub = ''
            return
        period = self.period
        if period is None:
            return
        if body.endswith('step durations:'):
            self.sub = 'discharge' if body.startswith('Discharge') else 'charge'
        elif body == 'Package changes:':
            self.sub = 'package'
        elif self.sub == 'package':
            kind, _sep, rest = body.partition(' ')
            package, _sep, version = rest.partition(' vers=')
            period['changes'] += 1
            add(self.report, 'battery_packages', PackageChange(period['start'], period['end'], tidy(kind)[:40], tidy(package)[:300],
                                                               to_int(version, tidy(version)) if version else None, line_no))
        elif _STEP.match(body):
            period['discharge' if self.sub == 'discharge' else 'charge'] += 1
        elif body.startswith(('Discharge ', 'Charge ')) and ' time:' in body:
            period['totals'].append(tidy(body))

    # -- statistics since last charge ----------------------------------------------------------
    def _stats(self, line_no, text, body):
        indent = _indent(text)
        if self.stats == 'power':
            ends = indent <= 2 and not _UID_POWER.match(body)
            if not ends:
                self._power_line(line_no, body, indent)
                return
            self._flush_power()
            self.stats = ''
        if self.stats == 'kernel' and indent == 2 and body.startswith('Kernel Wake lock '):
            self._wake_lock('Kernel', '', body[len('Kernel Wake lock '):], line_no)
            return
        if indent == 2:
            if body.startswith('Estimated power use (mAh):'):
                self.stats, self.last_power, self.context = 'power', None, ''
            elif body == 'All kernel wake locks:':
                self.stats = 'kernel'
            elif _UID_HEAD.match(body):
                self.stats, self.uid = 'uid', body[:-1]
            else:
                self.stats = ''
            return
        if self.stats == 'uid' and indent == 4:
            if body.startswith('Wake lock '):
                self._wake_lock('UID', self.uid, body[len('Wake lock '):], line_no)
            elif body.startswith('Apk ') and body.endswith(':'):
                package = tidy(body[4:-1])[:300]
                if package not in tables(self.report).uid_packages[self.uid]:
                    tables(self.report).uid_packages[self.uid].append(package)

    def _wake_lock(self, kind, uid, rest, line_no):
        found = _WAKE.match(rest)
        if found:
            name, usage = found.group('name'), found.group('usage')
        else:
            name, usage = (rest[:-len(' realtime')] if rest.endswith(' realtime') else rest), ''
        add(self.report, 'battery_wake_locks', WakeLockUse(kind, uid, tidy(name)[:400], tidy(usage)[:VALUE_CHARS], line_no))

    def _power_line(self, line_no, body, indent):
        if body.startswith('('):
            if body.endswith(')') and '=' not in body:
                self.context = body        # a heading on a line of its own: the items that follow belong to it
            elif self.last_power is not None:
                self.last_power['detail'] = (self.last_power['detail'] + ' | ' + body)[:VALUE_CHARS]
            return
        uid = _UID_POWER.match(body)
        if uid:
            self._flush_power()
            self.context = ''
            self.last_power = {'kind': 'UID', 'name': uid.group('name'), 'context': '', 'total': to_float(uid.group('total')),
                               'detail': uid.group('rest').strip(), 'line': line_no}
            return
        if body == 'Global':
            self._flush_power()
            self.context = ''
            return
        if self.last_power is not None and self.last_power['kind'] == 'UID' and indent >= 6 and '=' in body:
            self.last_power['detail'] = (self.last_power['detail'] + ' | ' + body).strip(' |')[:VALUE_CHARS]
            return
        item = _ITEM_POWER.match(body)
        if item and indent >= 4:
            self._flush_power()
            self.last_power = {'kind': 'Item', 'name': item.group('name'), 'context': self.context if indent >= 6 else '',
                               'total': to_float(item.group('total')), 'detail': item.group('rest').lstrip(', ').strip(),
                               'line': line_no}
        elif indent >= 4 and self.last_power is not None:
            self.last_power['detail'] = (self.last_power['detail'] + ' | ' + body)[:VALUE_CHARS]

    def _flush_power(self):
        item = self.last_power
        self.last_power = None
        if item is not None:
            add(self.report, 'battery_power', PowerUse(item['kind'], tidy(item['name'])[:200], tidy(item['context'])[:100], item['total'], tidy(item['detail']), item['line']))

    # -- the dump ------------------------------------------------------------------------------
    def feed(self, line_no, text):
        if not text.strip():
            return
        if not text.startswith(' '):
            body = text.strip()
            if self.mode == 'history' and not body.startswith(BATTERY_HEADS):
                return          # a wrapped line of a record's details starts at column 0
            if self.mode == 'daily':
                self._close_period()
            if self.mode == 'stats':
                self._flush_power()
            if body.startswith('Battery History'):
                self.mode = 'history'
                self.form = 'F2' if '[Format: 2]' in body else 'F1'
                self.anchor = None
            elif body == 'Daily stats:':
                self.mode = 'daily'
                self.period, self.sub = None, ''
            elif body.startswith('Statistics since last charge'):
                self.mode, self.stats = 'stats', ''
            else:
                self.mode = ''
            return
        body = text.strip()
        if self.mode == 'history':
            self._history(line_no, text)
        elif self.mode == 'daily':
            self._daily(line_no, text, body)
        elif self.mode == 'stats':
            self._stats(line_no, text, body)

    def finish(self):
        if self.mode == 'daily':
            self._close_period()
        if self.mode == 'stats':
            self._flush_power()


READERS = [AccountReader, ContentReader, BackupReader, UserReader, BatteryServiceReader, ThermalReader, PowerReader,
           DeviceIdleReader, ProcStatsReader, PsReader, MeminfoReader, BatteryStatsReader]
READ_BY = {
    ('service', 'account'): 'Accounts; Account History; Account Authenticators; Account Visibility',
    ('service', 'content'): 'Sync Adapter Status; Sync Recent History; Sync Adapter Last Syncs; Sync Jobs; Sync State',
    ('service', 'backup'): 'Backup State; Backup Transports; Backup Package State; Backup Participants; Backup Queues',
    ('service', 'user'): 'Users; User Manager Facts',
    ('service', 'battery'): 'Battery Service State',
    ('service', 'thermalservice'): 'Thermal Service State',
    ('service', 'power'): 'Power Manager State; Power Wake Locks; Power Events',
    ('service', 'deviceidle'): 'Device Idle State; Device Idle History',
    ('service', 'procstats'): 'Process Stats',
    ('command', 'PROCESSES AND THREADS'): 'Process Threads',
    ('service', 'meminfo'): 'Memory By Process; Memory Process Detail; Memory Summary',
    ('service', 'batterystats'): 'Battery History; Battery Daily Summary; Battery Package Changes; Battery Power Use; Battery Wake Locks',
}
