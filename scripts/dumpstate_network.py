"""Readers for the network sections of an Android bug report text (dumpstate).

These readers plug into the single pass of ``scripts/dumpstate_reader.py``: they receive the lines
of one section at a time, keep bounded tables on the report object and judge nothing. The sections
are the Wi-Fi services (wifi, wifiscanner, wifip2p), the network statistics (the netstats service
and the CHECKIN NETSTATS command), the network policy, the connectivity service, the interface
commands, the DNS resolver, the socket commands and the tethering service.

The module has no import from ``dumpstate_reader`` on purpose: that module imports this one to
register the readers, and a reader only needs the ``report`` object it is given. A reader class has
``kind``, ``name``, ``feed`` and ``finish``, which is all the pass asks of it.

Tables are lists of named tuples on the report, named ``net_<table>``. Times stay as printed; the
artifacts convert them with the report's own clock.
"""
import collections
import re

MAX_TEXT = 1500
MAX_UID_TEXT = 400
MAX_ID_TEXT = 600

_CONTROL = re.compile('[\x00-\x08\x0b-\x1f\x7f]')
_ISO_LINE = re.compile(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?) - (.*)$')
_POLICY_TIME = re.compile(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d):(\d+) - (.*)$')
_REC_LINE = re.compile(r'^\s*rec\[(\d+)\]: time=(\d\d-\d\d \d\d?:\d\d?:\d\d?(?:\.\d+)?) (.*)$')


def tidy(value):
    """A text with control characters (NUL, lone carriage returns, form feeds) shown as a space."""
    if value is None:
        return ''
    return _CONTROL.sub(' ', str(value))


def cut(value, limit=MAX_TEXT):
    return tidy(value)[:limit]


def to_int(text, default=None):
    value = str(text).strip().rstrip(',') if text is not None else ''
    try:
        return int(value)
    except ValueError:
        return default


def is_digits(text):
    return text.isascii() and text.isdigit()


def indent_of(text):
    return len(text) - len(text.lstrip(' '))


def put(report, table, row):
    """Append a row to the report's ``net_<table>`` list (created on first use); the cap is the report's own.

    Every text field of the row is tidied here, so a field that a reader takes as printed (a word matched by a pattern,
    a heading) shows its control characters as spaces like the fields the reader cuts.
    """
    name = 'net_' + table
    if name not in report.__dict__:
        setattr(report, name, [])
    report.add(name, type(row)(*[tidy(value) if isinstance(value, str) else value for value in row]))


def braced(text, key):
    """The text inside ``key{...}`` (braces counted), or '' when the key is not in the text."""
    found = re.search(r'(?<![A-Za-z0-9_])' + re.escape(key) + r'\{', text)
    if not found:
        return ''
    pos = found.end()
    depth = 1
    end = pos
    while end < len(text) and depth:
        char = text[end]
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        end += 1
    return text[pos:end - 1] if depth == 0 else text[pos:end]


def name_value(text):
    """``(name, value)`` for a ``name: value`` line whose name is plain words; ``('', text)`` otherwise."""
    head, separator, tail = text.partition(': ')
    if separator and re.match(r'^[A-Za-z][\w .()\-/]{0,70}$', head):
        return head, tail
    return '', text


class NetReader:
    """Base of the readers in this module (the pass needs ``kind``, ``name``, ``feed`` and ``finish``)."""
    kind = ''
    name = ''

    def __init__(self, report, section):
        self.report = report
        self.section = section

    def feed(self, line_no, text):
        """One line of the section body (the header line is not included)."""

    def finish(self):
        """The section ended."""


# ---------------------------------------------------------------------------------------------
# Wi-Fi: saved networks
# ---------------------------------------------------------------------------------------------
WifiNetwork = collections.namedtuple(
    'WifiNetwork', 'prefix network_id ssid bssid fqdn provider hidden pmf carrier_id subscription_id currently_connected '
                   'user_selected auto_join selection_status disable_reason has_ever_connected associations creation update '
                   'key_mgmt protocols mac_setting random_mac creator_uid creator_name update_uid update_name connect_uid '
                   'recent_failure reboots most_recent connect_choice line')

_HEADER_KEYS = ('PROVIDER-NAME', 'BSSID', 'FQDN', 'HOME-PROVIDER-NETWORK', 'PRIO', 'HIDDEN', 'PMF', 'CarrierId',
                'SubscriptionId', 'SubscriptionGroup', 'Currently Connected', 'User Selected', 'autoJoin', 'autoJoinMenu',
                'canModify', 'canForget', 'REMOVABLE', 'CARRIERPRELOAD')
_HEADER_PAIR = re.compile('(?:^| )(' + '|'.join(re.escape(key) for key in sorted(_HEADER_KEYS, key=len, reverse=True)) + r'): (\S*)')
_NETWORK_HEAD = re.compile(r'^((?:\* |- [A-Z]+ )?)ID: (-?\d+) SSID: (.*)$')
_KEY_MGMT = re.compile(r'^KeyMgmt: (.*?) Protocols: (.*)$')
_CONNECT_CHOICE = re.compile(r'connect choice: (.*?)(?: connect choice rssi: (-?\d+))?(?: hasEverConnected: |$)')


def token_pairs(text):
    """``{key: value}`` for the ``key=value`` words of a text (the first value of a repeated key)."""
    found = {}
    for word in text.split():
        key, separator, value = word.partition('=')
        if separator and key and key not in found:
            found[key] = value
    return found


class WifiNetworksReader(NetReader):
    """The ``Configured networks`` entries of the WifiConfigManager part of the wifi service dump."""
    kind = 'service'
    name = 'wifi'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.active = False
        self.entry = None

    def _flush(self):
        entry = self.entry
        self.entry = None
        if entry is None:
            return
        put(self.report, 'wifi_networks', WifiNetwork(*[entry.get(field, '') for field in WifiNetwork._fields]))

    def feed(self, line_no, text):
        if text.startswith('WifiConfigManager - Configured networks'):
            self._flush()
            self.active = 'Begin' in text
            return
        if not self.active:
            return
        head = _NETWORK_HEAD.match(text)
        if head:
            self._flush()
            ssid, _separator, rest = head.group(3).partition(' PROVIDER-NAME: ')
            pairs = {}
            for key, value in _HEADER_PAIR.findall('PROVIDER-NAME: ' + rest):
                pairs.setdefault(key, value)
            self.entry = {
                'prefix': head.group(1).strip(), 'network_id': to_int(head.group(2)), 'ssid': cut(ssid, 200),
                'bssid': pairs.get('BSSID', ''), 'fqdn': pairs.get('FQDN', ''), 'provider': pairs.get('PROVIDER-NAME', ''),
                'hidden': pairs.get('HIDDEN', ''), 'pmf': pairs.get('PMF', ''), 'carrier_id': pairs.get('CarrierId', ''),
                'subscription_id': pairs.get('SubscriptionId', ''),
                'currently_connected': pairs.get('Currently Connected', ''), 'user_selected': pairs.get('User Selected', ''),
                'auto_join': pairs.get('autoJoin', ''), 'line': line_no}
            return
        entry = self.entry
        if entry is None:
            return
        body = text.strip()
        if body.startswith('NetworkSelectionStatus '):
            entry['selection_status'] = cut(body.split(' ', 1)[1], 120)
        elif body.startswith('mNetworkSelectionDisableReason '):
            entry['disable_reason'] = cut(body.split(' ', 1)[1], 120)
        elif 'hasEverConnected: ' in body:
            entry['has_ever_connected'] = body.split('hasEverConnected: ', 1)[1].split(' ', 1)[0]
            choice = _CONNECT_CHOICE.search(body) if body.startswith('connect choice') else None
            if choice:
                entry['connect_choice'] = cut(choice.group(1), 200)
        elif body.startswith('numAssociation '):
            entry['associations'] = to_int(body.split(' ', 1)[1])
        elif body.startswith('creation time='):
            entry['creation'] = cut(body[len('creation time='):], 40)
        elif body.startswith('update time='):
            entry['update'] = cut(body[len('update time='):], 40)
        elif body.startswith('macRandomizationSetting: '):
            entry['mac_setting'] = body.split(': ', 1)[1]
        elif body.startswith('mRandomizedMacAddress: '):
            entry['random_mac'] = body.split(': ', 1)[1]
        elif body.startswith('KeyMgmt: ') and 'key_mgmt' not in entry:
            both = _KEY_MGMT.match(body)
            if both:
                entry['key_mgmt'], entry['protocols'] = cut(both.group(1), 80), cut(both.group(2), 80)
        elif body.startswith('numRebootsSinceLastUse: '):
            entry['reboots'] = to_int(body.split(': ', 1)[1])
        elif body.startswith('recentFailure: '):
            entry['recent_failure'] = cut(body.split(': ', 1)[1], 200)
        elif body.startswith('cuid='):
            pairs = token_pairs(body)
            entry['creator_uid'], entry['creator_name'] = pairs.get('cuid', ''), cut(pairs.get('cname', ''), 120)
            entry['update_uid'], entry['update_name'] = pairs.get('luid', ''), cut(pairs.get('lname', ''), 120)
            entry['connect_uid'] = pairs.get('lcuid', '')
            entry['most_recent'] = pairs.get('mostRecentlyConnected', '')
            if not entry.get('auto_join'):
                entry['auto_join'] = pairs.get('allowAutojoin', '')

    def finish(self):
        self._flush()
        self.active = False


# ---------------------------------------------------------------------------------------------
# Wi-Fi: current state and connection events
# ---------------------------------------------------------------------------------------------
WifiState = collections.namedtuple(
    'WifiState', 'power mode ssid bssid mac ip security supplicant standard rssi link_speed tx_speed rx_speed frequency '
                 'net_id metered last_bssid link_properties other line')
WifiConnection = collections.namedtuple(
    'WifiConnection', 'start ssid bssid duration roam result l2_failure connectivity_failure rssi wifi_state screen_on '
                      'channel network_type nominator creator other line')

_INFO_SPLIT = re.compile(r', (?=[A-Za-z][A-Za-z0-9\- ]*: )')
_EVENT_SPLIT = re.compile(r', (?=[A-Za-z][A-Za-z0-9_]*=)')
_INFO_KEYS = {'SSID': 'ssid', 'BSSID': 'bssid', 'MAC': 'mac', 'IP': 'ip', 'Security type': 'security',
              'Supplicant state': 'supplicant', 'Wi-Fi standard': 'standard', 'RSSI': 'rssi', 'Link speed': 'link_speed',
              'Tx Link speed': 'tx_speed', 'Rx Link speed': 'rx_speed', 'Frequency': 'frequency', 'Net ID': 'net_id',
              'Metered hint': 'metered'}
_EVENT_KEYS = {'durationMillis': 'duration', 'roamType': 'roam', 'connectionResult': 'result',
               'level2FailureCode': 'l2_failure', 'connectivityLevelFailureCode': 'connectivity_failure',
               'signalStrength': 'rssi', 'wifiState': 'wifi_state', 'screenOn': 'screen_on', 'mChannelInfo': 'channel',
               'networkType': 'network_type', 'connectionNominator': 'nominator', 'networkCreator': 'creator'}


def parse_wifi_info(text):
    """The fields of an ``mWifiInfo`` line as a dict (named keys, and the remaining ``other`` text)."""
    fields = {}
    other = []
    for piece in _INFO_SPLIT.split(text):
        key, separator, value = piece.partition(': ')
        if separator and key in _INFO_KEYS:
            fields.setdefault(_INFO_KEYS[key], cut(value, 300))
        else:
            other.append(piece)
    fields['other'] = cut(', '.join(other), 600)
    return fields


def parse_connection_event(text):
    """The fields of a ``startTime=...`` connection event line as a dict, or None when it is not one."""
    body = text[len('startTime='):]
    start, separator, rest = body.partition(', SSID=')
    if not separator:
        return None
    ssid, separator, rest = rest.partition(', BSSID=')
    if not separator:
        return None
    pieces = _EVENT_SPLIT.split(rest)
    fields = {'start': cut(start, 40), 'ssid': cut(ssid, 200), 'bssid': cut(pieces[0], 80)}
    other = []
    for piece in pieces[1:]:
        key, _separator, value = piece.partition('=')
        if key in _EVENT_KEYS:
            fields.setdefault(_EVENT_KEYS[key], cut(value, 120))
        else:
            other.append(piece)
    fields['other'] = cut(', '.join(other), MAX_TEXT)
    return fields


class WifiStateReader(NetReader):
    """The Wi-Fi power and mode lines, the ``mWifiInfo`` snapshots and the ``mConnectionEvents`` lines of the wifi dump."""
    kind = 'service'
    name = 'wifi'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.power = ''
        self.mode = ''
        self.mode_line = 0
        self.infos = []
        self.link = ''

    def feed(self, line_no, text):
        if text.startswith('startTime='):
            fields = parse_connection_event(text)
            if fields is not None:
                fields['line'] = line_no
                put(self.report, 'wifi_connections', WifiConnection(*[fields.get(field, '') for field in WifiConnection._fields]))
        elif text.startswith('Wi-Fi is '):
            self.power = cut(text, 80)
            self.mode_line = self.mode_line or line_no
        elif text.startswith('Current wifi mode: '):
            self.mode = cut(text[len('Current wifi mode: '):], 80)
            self.mode_line = self.mode_line or line_no
        elif text.startswith('mLinkProperties '):
            self.link = cut(text[len('mLinkProperties '):], 1000)      # printed just before the mWifiInfo line of its client
        elif text.startswith('mWifiInfo '):
            fields = parse_wifi_info(text[len('mWifiInfo '):])
            fields['line'] = line_no
            fields['link_properties'] = self.link
            self.link = ''
            self.infos.append(fields)
        elif self.infos and text.startswith('mLastBssid '):
            self.infos[-1]['last_bssid'] = cut(text[len('mLastBssid '):], 80)

    def finish(self):
        if not self.infos and not (self.power or self.mode):
            return
        for fields in self.infos or [{'line': self.mode_line}]:
            fields = dict(fields, power=self.power, mode=self.mode)
            put(self.report, 'wifi_state', WifiState(*[fields.get(field, '') for field in WifiState._fields]))


# ---------------------------------------------------------------------------------------------
# Wi-Fi: state machine records and log blocks
# ---------------------------------------------------------------------------------------------
WifiRecord = collections.namedtuple('WifiRecord', 'service machine number time_text processed origin destination what line')
WifiLog = collections.namedtuple('WifiLog', 'service log_name time_text message line')


class WifiRecordsReader(NetReader):
    """The ``rec[N]: time=`` lines of the state machines and the time-stamped lines of the ``- Log Begin`` blocks."""
    kind = 'service'
    name = ''

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.machine = ''
        self.log_name = ''

    def feed(self, line_no, text):
        if not text:
            return
        if text[0] != ' ' and text.endswith(' ----'):
            if ' - Log Begin ' in text:
                self.log_name = text.split(' - Log Begin ', 1)[0].strip()
            elif ' - Log End ' in text:
                self.log_name = ''
            return
        if self.log_name:
            match = _ISO_LINE.match(text)
            if match:
                put(self.report, 'wifi_log', WifiLog(self.name, self.log_name, match.group(1), cut(match.group(2), 1000), line_no))
                return
        if text[0] != ' ' and text.rstrip().endswith(':'):
            self.machine = tidy(text.strip())[:-1][:120]
            return
        if text.startswith(' ') and 'rec[' in text:
            match = _REC_LINE.match(text)
            if match:
                rest = match.group(3)
                what = rest.partition(' what=')[2] if ' what=' in rest else ''
                pairs = token_pairs(rest.partition(' what=')[0])
                put(self.report, 'wifi_records', WifiRecord(
                    self.name, self.machine, to_int(match.group(1)), match.group(2), cut(pairs.get('processed', ''), 120),
                    cut(pairs.get('org', ''), 120), cut(pairs.get('dest', ''), 120), cut(what, 500), line_no))


class WifiServiceRecordsReader(WifiRecordsReader):
    name = 'wifi'


class WifiScannerRecordsReader(WifiRecordsReader):
    name = 'wifiscanner'


class WifiP2pRecordsReader(WifiRecordsReader):
    name = 'wifip2p'


# ---------------------------------------------------------------------------------------------
# Wi-Fi: scan results of the scanner service
# ---------------------------------------------------------------------------------------------
WifiScanResult = collections.namedtuple('WifiScanResult', 'table bssid frequency rssi rssi_detail age ssid flags line')
_SCAN_ROW = re.compile(r'^\s+(\S+)\s+(\d{3,5})\s+(-?\d+)(\([^)]*\))?\s+(\S+)\s*(.*)$')
_SCAN_TAIL = re.compile(r'^(.*?)\s*((?:\[[^\]]*\])*)\s*$')


class WifiScanResultsReader(NetReader):
    """The ``Latest scan results`` tables of the wifiscanner service dump."""
    kind = 'service'
    name = 'wifiscanner'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.table = ''

    def feed(self, line_no, text):
        if not text.strip():
            self.table = ''
            return
        if text[0] != ' ':
            title = text.strip()
            self.table = title[:-1] if title.endswith(':') and title.startswith('Latest') and not title.endswith('IEs:') else ''
            return
        if not self.table or 'BSSID' in text and 'Frequency' in text:
            return
        match = _SCAN_ROW.match(text)
        if not match:
            return
        tail = _SCAN_TAIL.match(match.group(6))
        put(self.report, 'wifi_scan_results', WifiScanResult(
            self.table, cut(match.group(1), 40), to_int(match.group(2)), to_int(match.group(3)), cut(match.group(4) or '', 60),
            cut(match.group(5), 30), cut(tail.group(1), 100), cut(tail.group(2), 300), line_no))


# ---------------------------------------------------------------------------------------------
# Network statistics: usage buckets
# ---------------------------------------------------------------------------------------------
UsageBucket = collections.namedtuple(
    'UsageBucket', 'origin table identity uid net_set tag bucket_seconds start rx_bytes rx_packets tx_bytes tx_packets '
                   'operations extra line')
_IDENT = re.compile(r'^\s*ident=\[(.*)\]\s+uid=(-?\d+)\s+set=(\w+)(?:\s+tag=(\S+))?\s*$')
_BUCKET_DURATION = re.compile(r'NetworkStatsHistory: bucketDuration=(\d+)')
_HISTORY_ROW = re.compile(r'^\s+st=(\d+)\s+rb=(\d+)\s+rp=(\d+)\s+tb=(\d+)\s+tp=(\d+)\s+op=(\d+)(.*)$')
_STATS_TABLES = {'Dev stats:': 'Dev stats', 'Xt stats:': 'Xt stats', 'UID stats:': 'UID stats', 'UID tag stats:': 'UID tag stats'}


class NetStatsReader(NetReader):
    """The statistics histories of the netstats service dump and of the CHECKIN NETSTATS command (both layouts)."""
    origin = ''

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.table = ''
        self.ident = None
        self.seconds = None
        self.checkin = None       # (group, label, uid, set, tag) of a checkin ``c,`` line

    def feed(self, line_no, text):
        if not text:
            return
        if text[0] != ' ':
            title = text.rstrip()
            if title in _STATS_TABLES:
                self.table, self.ident, self.seconds = _STATS_TABLES[title], None, None
            elif title.endswith(':'):
                self.table, self.ident, self.seconds = '', None, None
            elif text.startswith(('c,', 'd,', 'b,', 'v1,')) or text.isalpha():
                self._checkin(text, line_no)
            return
        if not self.table:
            return
        body = text.lstrip()
        if body.startswith('st='):
            row = _HISTORY_ROW.match(text)
            if row and self.ident is not None:
                put(self.report, 'usage_buckets', UsageBucket(
                    self.origin, self.table, self.ident[0], self.ident[1], self.ident[2], self.ident[3], self.seconds,
                    int(row.group(1)), int(row.group(2)), int(row.group(3)), int(row.group(4)), int(row.group(5)),
                    int(row.group(6)), cut(row.group(7).strip(), 120), line_no))
        elif body.startswith('ident='):
            match = _IDENT.match(text)
            if match:
                self.ident = (cut(match.group(1), MAX_ID_TEXT), to_int(match.group(2)), match.group(3), match.group(4) or '')
                self.seconds = None
        elif self.ident is not None and 'bucketDuration=' in text:
            found = _BUCKET_DURATION.search(text)
            self.seconds = to_int(found.group(1)) if found else None

    def _checkin(self, text, line_no):
        parts = text.rstrip().split(',')
        if text.startswith('c,') and len(parts) >= 5:
            group = self.checkin[0] if self.checkin else ''
            self.checkin = (group, cut(parts[1], 60), to_int(parts[2]), cut(parts[3], 20), cut(parts[4], 20))
            self.ident, self.seconds, self.table = None, None, ''
        elif text.startswith('d,') and len(parts) >= 2:
            self.seconds = to_int(parts[1])
        elif text.startswith('b,') and len(parts) >= 7 and self.checkin is not None and all(is_digits(p) for p in parts[1:7]):
            group, label, uid, net_set, tag = self.checkin
            put(self.report, 'usage_buckets', UsageBucket(
                self.origin, 'checkin ' + group, label, uid, net_set, tag, self.seconds, int(parts[1]), int(parts[2]),
                int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6]), '', line_no))
        elif text.isalpha():
            self.checkin = (text.strip(), '', None, '', '')


class NetStatsServiceReader(NetStatsReader):
    kind = 'service'
    name = 'netstats'
    origin = 'DUMP OF SERVICE netstats'


class NetStatsCheckinReader(NetStatsReader):
    kind = 'command'
    name = 'CHECKIN NETSTATS'
    origin = 'CHECKIN NETSTATS'


# ---------------------------------------------------------------------------------------------
# Network policy
# ---------------------------------------------------------------------------------------------
PolicyUid = collections.namedtuple('PolicyUid', 'group uid value line')
PolicySetting = collections.namedtuple('PolicySetting', 'group name value line')
PolicyEvent = collections.namedtuple('PolicyEvent', 'log time_text message line')
_UID_LINE = re.compile(r'^  UID=(-?\d+)(.*)$')
_SKIP_PREFIXES = ('Service host process PID', 'Threads in use', 'Client PIDs')


class NetPolicyReader(NetReader):
    """The network policy service dump: UID lists and rules, the state and policy lines, and the event logs."""
    kind = 'service'
    name = 'netpolicy'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.group = ''

    def feed(self, line_no, text):
        if not text.strip() or text.startswith(_SKIP_PREFIXES):
            return
        if text[0] != ' ':
            if text.rstrip().endswith(':'):
                self.group = tidy(text.strip())[:-1]
                return
            self.group = ''
            name, value = name_value(text.strip())
            put(self.report, 'policy_settings', PolicySetting('', name, cut(value), line_no))
            return
        if indent_of(text) != 2:
            return
        if 'Logs' in self.group:
            match = _POLICY_TIME.match(text.strip())
            if match:
                put(self.report, 'policy_events', PolicyEvent(
                    self.group.split(' ')[0], match.group(1) + ':' + match.group(2), cut(match.group(3), 600), line_no))
            return
        uid = _UID_LINE.match(text)
        if uid:
            value = uid.group(2).lstrip(':, ').strip()
            put(self.report, 'policy_uids', PolicyUid(self.group, int(uid.group(1)), cut(value, MAX_UID_TEXT), line_no))
            return
        name, value = name_value(text.strip())
        put(self.report, 'policy_settings', PolicySetting(self.group, name, cut(value), line_no))


# ---------------------------------------------------------------------------------------------
# Connectivity service: networks
# ---------------------------------------------------------------------------------------------
ConnectedNetwork = collections.namedtuple(
    'ConnectedNetwork', 'network_id default info created interface addresses dns domains routes transports capabilities '
                        'signal ssid score line')
_LP_INTERFACE = re.compile(r'InterfaceName: (\S+)')
_LP_ADDRESSES = re.compile(r'LinkAddresses: \[(.*?)\]')
_LP_DNS = re.compile(r'DnsAddresses: \[(.*?)\]')
_LP_DOMAINS = re.compile(r'Domains: (\S+)')
_LP_ROUTES = re.compile(r'Routes: \[(.*?)\]\s*\}?')
_NC_TRANSPORTS = re.compile(r'Transports: ([A-Z_|]+)')
_NC_CAPABILITIES = re.compile(r'Capabilities: (\S+)')
_NC_SIGNAL = re.compile(r'SignalStrength: (-?\d+)')
_NC_SSID = re.compile(r'(?<![A-Za-z])SSID: ("[^"]*"|[^\s\]]+)')
_SCORE = re.compile(r'Score[({]([^)}]*)[)}]')
_CREATED = re.compile(r'created=(\S+)')


def first_group(pattern, text):
    match = pattern.search(text)
    return match.group(1) if match else ''


class ConnectivityReader(NetReader):
    """The ``Current Networks`` list of the connectivity service dump."""
    kind = 'service'
    name = 'connectivity'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.default = None
        self.in_networks = False

    def feed(self, line_no, text):
        if not text:
            return
        if text[0] != ' ':
            self.in_networks = text.rstrip() == 'Current Networks:'
            if text.startswith('Active default network: '):
                self.default = to_int(text[len('Active default network: '):])
            return
        if not self.in_networks or not text.startswith('  NetworkAgentInfo{'):
            return
        network_text = braced(text, 'network')
        network_id = to_int(network_text)
        link = braced(text, 'lp')
        caps = braced(text, 'nc')
        put(self.report, 'connectivity_networks', ConnectedNetwork(
            network_id, 'true' if network_id is not None and network_id == self.default else 'false',
            cut(braced(text, 'ni'), 300), first_group(_CREATED, text), first_group(_LP_INTERFACE, link),
            cut(first_group(_LP_ADDRESSES, link), 400), cut(first_group(_LP_DNS, link), 400), first_group(_LP_DOMAINS, link),
            cut(first_group(_LP_ROUTES, link), 600), first_group(_NC_TRANSPORTS, caps), cut(first_group(_NC_CAPABILITIES, caps), 600),
            first_group(_NC_SIGNAL, caps), cut(first_group(_NC_SSID, caps), 200), cut(first_group(_SCORE, text), 300), line_no))


# ---------------------------------------------------------------------------------------------
# Interface commands
# ---------------------------------------------------------------------------------------------
NetInterface = collections.namedtuple(
    'NetInterface', 'index name linked flags mtu qdisc state mode group qlen link_type link_address broadcast extra '
                    'rx_bytes rx_packets rx_errors rx_dropped rx_overrun rx_mcast tx_bytes tx_packets tx_errors tx_dropped '
                    'tx_carrier tx_collisions line')
InterfaceCounters = collections.namedtuple(
    'InterfaceCounters', 'name rx_bytes rx_packets rx_errs rx_drop rx_fifo rx_frame rx_compressed rx_multicast tx_bytes '
                         'tx_packets tx_errs tx_drop tx_fifo tx_colls tx_carrier tx_compressed line')
_LINK_HEAD = re.compile(r'^(\d+): ([^:\s]+?)(?:@([^:\s]*))?: <([^>]*)> mtu (\d+)(.*)$')
_LINK_LINE = re.compile(r'^\s+link/(\S+)\s*(\S*)(?:\s+brd\s+(\S+))?(.*)$')
_LINK_KEYS = ('qdisc', 'state', 'mode', 'group', 'qlen')


class InterfacesReader(NetReader):
    """The interface list (``ip link`` or ``ip -s link``) of the NETWORK INTERFACES command."""
    kind = 'command'
    name = 'NETWORK INTERFACES'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.entry = None
        self.expect = ''

    def _flush(self):
        entry = self.entry
        self.entry = None
        if entry is not None:
            put(self.report, 'interfaces', NetInterface(*[entry.get(field, '') for field in NetInterface._fields]))

    def feed(self, line_no, text):
        head = _LINK_HEAD.match(text)
        if head:
            self._flush()
            tokens = head.group(6).split()
            values = {}
            other = []
            position = 0
            while position < len(tokens):
                if tokens[position] in _LINK_KEYS and position + 1 < len(tokens):
                    values.setdefault(tokens[position], tokens[position + 1])
                    position += 2
                else:
                    other.append(tokens[position])
                    position += 1
            self.entry = {'index': to_int(head.group(1)), 'name': cut(head.group(2), 60), 'linked': cut(head.group(3) or '', 60),
                          'flags': cut(head.group(4), 200), 'mtu': to_int(head.group(5)), 'qdisc': values.get('qdisc', ''),
                          'state': values.get('state', ''), 'mode': values.get('mode', ''), 'group': values.get('group', ''),
                          'qlen': values.get('qlen', ''), 'extra': cut(' '.join(other), 200), 'line': line_no}
            self.expect = ''
            return
        entry = self.entry
        if entry is None:
            return
        link = _LINK_LINE.match(text)
        if link:
            entry['link_type'], entry['link_address'] = link.group(1), cut(link.group(2), 60)
            entry['broadcast'] = cut(link.group(3) or '', 60)
            return
        body = text.strip()
        if body.startswith('RX:'):
            self.expect = 'rx'
        elif body.startswith('TX:'):
            self.expect = 'tx'
        elif self.expect:
            numbers = body.split()
            if len(numbers) >= 6 and all(is_digits(item) for item in numbers[:6]):
                names = (('rx_bytes', 'rx_packets', 'rx_errors', 'rx_dropped', 'rx_overrun', 'rx_mcast') if self.expect == 'rx'
                         else ('tx_bytes', 'tx_packets', 'tx_errors', 'tx_dropped', 'tx_carrier', 'tx_collisions'))
                for key, number in zip(names, numbers):
                    entry[key] = int(number)
            self.expect = ''

    def finish(self):
        self._flush()


class InterfaceCountersReader(NetReader):
    """The per-interface counters of the NETWORK DEV INFO command (``/proc/net/dev``)."""
    kind = 'command'
    name = 'NETWORK DEV INFO'

    def feed(self, line_no, text):
        name, separator, rest = text.partition(':')
        if not separator or '|' in text:
            return
        numbers = rest.split()
        if len(numbers) == 16 and all(is_digits(item) for item in numbers):
            put(self.report, 'interface_counters', InterfaceCounters(cut(name.strip(), 60), *[int(item) for item in numbers], line_no))


# ---------------------------------------------------------------------------------------------
# DNS resolver
# ---------------------------------------------------------------------------------------------
DnsServer = collections.namedtuple(
    'DnsServer', 'net_id server total successes errors timeouts internal_errors rtt_ms last_sample interfaces search_domains '
                 'private_mode transport metered line')
PrivateDnsEntry = collections.namedtuple('PrivateDnsEntry', 'time_text net_id server state line')
_DNS_SERVER = re.compile(r'^\s+(\S+) \((\d+), (\d+), (\d+), (\d+), (\d+), (-?\d+)ms, (-?\d+)s\)\s*$')
_PRIVATE_DNS = re.compile(r'^\s+(\d\d:\d\d:\d\d\.\d+) - netId=(\d+) PrivateDns=\{(.*?)\} state=(\S+)\s*$')


class DnsReader(NetReader):
    """The per-network DNS servers and the private DNS log of the dnsresolver service dump."""
    kind = 'service'
    name = 'dnsresolver'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.block = None
        self.in_servers = False
        self.in_log = False

    def _flush(self):
        block = self.block
        self.block = None
        if block is None:
            return
        for server in block['servers']:
            put(self.report, 'dns_servers', DnsServer(
                block['net_id'], *server[:8], block.get('interfaces', ''), block.get('search', ''), block.get('private_mode', ''),
                block.get('transport', ''), block.get('metered', ''), server[8]))

    def feed(self, line_no, text):
        if not text.strip():
            return
        if text[0] != ' ':
            if text.startswith('NetId: '):
                self._flush()
                self.block = {'net_id': to_int(text[len('NetId: '):]), 'servers': []}
                self.in_log = False
            elif text.startswith('PrivateDnsLog'):
                self._flush()
                self.in_log = True
            else:
                self._flush()
                self.in_log = False
            return
        if self.in_log:
            match = _PRIVATE_DNS.match(text)
            if match:
                put(self.report, 'private_dns', PrivateDnsEntry(match.group(1), to_int(match.group(2)), cut(match.group(3), 200),
                                                               match.group(4), line_no))
            return
        block = self.block
        if block is None:
            return
        body = text.strip()
        if body.startswith('DNS servers:'):
            self.in_servers = True
            return
        match = _DNS_SERVER.match(text) if self.in_servers else None
        if match:
            block['servers'].append((cut(match.group(1), 100), int(match.group(2)), int(match.group(3)), int(match.group(4)),
                                     int(match.group(5)), int(match.group(6)), int(match.group(7)), int(match.group(8)), line_no))
            return
        if indent_of(text) <= 2:
            self.in_servers = False
        if body.startswith('Interface names: '):
            block['interfaces'] = cut(body[len('Interface names: '):], 200)
        elif body.startswith('No search domains'):
            block['search'] = 'none defined'
        elif body.startswith('Search domains'):
            block['search'] = cut(body.partition(':')[2].strip(), 300)
        elif body.startswith('Private DNS mode: '):
            block['private_mode'] = cut(body[len('Private DNS mode: '):], 60)
        elif body.startswith('TransportType: '):
            block['transport'] = cut(body[len('TransportType: '):], 60)
        elif body.startswith('Metered: '):
            block['metered'] = cut(body[len('Metered: '):], 20)

    def finish(self):
        self._flush()


# ---------------------------------------------------------------------------------------------
# Sockets
# ---------------------------------------------------------------------------------------------
InetSocket = collections.namedtuple('InetSocket', 'protocol recv_q send_q local foreign state uid inode program line')
UnixSocket = collections.namedtuple('UnixSocket', 'protocol ref_count flags socket_type state inode program path line')
SocketState = collections.namedtuple('SocketState', 'netid state recv_q send_q local peer uid inode socket timer users other info line')
_TCP_STATE = re.compile(r'^[A-Z][A-Z0-9_]+$')
_UNIX_ROW = re.compile(r'^(\S+)\s+(\d+)\s+(\[[^\]]*\])\s+(\S+)\s+(?:([A-Z]+)\s+)?(\d+)\s*(.*)$')


class NetstatReader(NetReader):
    """The Internet and UNIX domain socket tables of the NETSTAT command."""
    kind = 'command'
    name = 'NETSTAT'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.mode = ''
        self.has_user = False
        self.has_program = False

    def feed(self, line_no, text):
        if text.startswith('Active Internet connections'):
            self.mode = 'internet'
            return
        if text.startswith('Active UNIX domain sockets'):
            self.mode = 'unix'
            return
        if text.startswith('Proto '):
            words = text.split()
            self.has_user = 'User' in words and 'Inode' in words
            self.has_program = 'PID/Program' in words
            return
        if self.mode == 'internet':
            tokens = text.split()
            if len(tokens) < 5 or not is_digits(tokens[1]) or not is_digits(tokens[2]):
                return
            rest = tokens[5:]
            state = ''
            if rest and (not self.has_user or _TCP_STATE.match(rest[0]) or (len(rest) > 2 and all(is_digits(item) for item in rest[:3]))):
                state, rest = rest[0], rest[1:]      # a raw socket prints a number where tcp prints its state word
            user = inode = program = ''
            if self.has_user and rest:
                user = rest[0]
                inode = rest[1] if len(rest) > 1 else ''
                program = ' '.join(rest[2:])
            put(self.report, 'inet_sockets', InetSocket(
                cut(tokens[0], 20), int(tokens[1]), int(tokens[2]), cut(tokens[3], 120), cut(tokens[4], 120), state,
                to_int(user), to_int(inode), cut(program, 120), line_no))
        elif self.mode == 'unix':
            match = _UNIX_ROW.match(text)
            if not match:
                return
            rest = match.group(7).strip()
            program = ''
            if self.has_program and rest:
                program, _separator, rest = rest.partition(' ')
            put(self.report, 'unix_sockets', UnixSocket(
                cut(match.group(1), 20), int(match.group(2)), cut(match.group(3), 40), cut(match.group(4), 40),
                match.group(5) or '', int(match.group(6)), cut(program, 120), cut(rest.strip(), 400), line_no))


class SocketStateReader(NetReader):
    """The ``ss`` socket table of the DETAILED SOCKET STATE command, with the continuation line of a TCP socket."""
    kind = 'command'
    name = 'DETAILED SOCKET STATE'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.pending = None

    def _flush(self):
        pending = self.pending
        self.pending = None
        if pending is not None:
            put(self.report, 'socket_state', SocketState(*pending))

    def feed(self, line_no, text):
        if not text.strip() or text.startswith('Netid'):
            return
        if text[0] in ' 	':
            if self.pending is not None:
                self.pending[12] = cut(' '.join((self.pending[12] + ' ' + text.strip()).split()), 800)
            return
        tokens = text.split(None, 6)
        if len(tokens) < 6 or not is_digits(tokens[2]) or not is_digits(tokens[3]):
            return
        self._flush()
        rest = tokens[6] if len(tokens) > 6 else ''
        pairs = {}
        for word in rest.split():
            key, separator, value = word.partition(':')
            if separator and key in ('uid', 'ino', 'sk') and key not in pairs:
                pairs[key] = value
        timer = re.search(r'timer:\([^)]*\)', rest)
        users = re.search(r'users:\(\(.*\)\)', rest)
        self.pending = [cut(tokens[0], 20), cut(tokens[1], 20), int(tokens[2]), int(tokens[3]), cut(tokens[4], 120),
                        cut(tokens[5], 120), to_int(pairs.get('uid')), to_int(pairs.get('ino')), cut(pairs.get('sk', ''), 40),
                        cut(timer.group(0) if timer else '', 120), cut(users.group(0) if users else '', 200), cut(rest, 400),
                        '', line_no]

    def finish(self):
        self._flush()


# ---------------------------------------------------------------------------------------------
# Tethering
# ---------------------------------------------------------------------------------------------
TetheringLog = collections.namedtuple('TetheringLog', 'time_text message line')
TetheringState = collections.namedtuple('TetheringState', 'group name value line')


class TetheringReader(NetReader):
    """The state lines and the time-stamped log lines of the tethering service dump."""
    kind = 'service'
    name = 'tethering'

    def __init__(self, report, section):
        NetReader.__init__(self, report, section)
        self.group = ''
        self.in_log = False

    def feed(self, line_no, text):
        if not text.strip() or text.startswith(_SKIP_PREFIXES):
            return
        body = text.strip()
        indent = indent_of(text)
        if indent <= 2 and body.endswith(':'):
            self.group = tidy(body)[:-1]
            self.in_log = self.group == 'Log'
            return
        if self.in_log:
            match = _ISO_LINE.match(body)
            if match:
                put(self.report, 'tethering_log', TetheringLog(match.group(1), cut(match.group(2), 1000), line_no))
            return
        if indent >= 2:
            name, value = name_value(body)
            put(self.report, 'tethering_state', TetheringState(self.group, name, cut(value), line_no))


READERS = [WifiNetworksReader, WifiStateReader, WifiServiceRecordsReader, WifiScannerRecordsReader, WifiP2pRecordsReader,
           WifiScanResultsReader, NetStatsServiceReader, NetStatsCheckinReader, NetPolicyReader, ConnectivityReader,
           InterfacesReader, InterfaceCountersReader, DnsReader, NetstatReader, SocketStateReader, TetheringReader]
READ_BY = {
    ('service', 'wifi'): 'Wi-Fi Saved Networks; Wi-Fi Connection Events; Wi-Fi Current State; Wi-Fi State Machine Records; Wi-Fi Service Log',
    ('service', 'wifiscanner'): 'Wi-Fi Scan Results; Wi-Fi State Machine Records; Wi-Fi Service Log',
    ('service', 'wifip2p'): 'Wi-Fi State Machine Records',
    ('service', 'netstats'): 'Network Usage Buckets',
    ('command', 'CHECKIN NETSTATS'): 'Network Usage Buckets',
    ('service', 'netpolicy'): 'Network Policy UID Entries; Network Policy Settings; Network Policy Events',
    ('service', 'connectivity'): 'Connected Networks',
    ('command', 'NETWORK INTERFACES'): 'Network Interfaces',
    ('command', 'NETWORK DEV INFO'): 'Network Interface Counters',
    ('service', 'dnsresolver'): 'DNS Servers; Private DNS Log',
    ('command', 'NETSTAT'): 'Open Sockets; Unix Domain Sockets',
    ('command', 'DETAILED SOCKET STATE'): 'Socket Details',
    ('service', 'tethering'): 'Tethering Log; Tethering State',
}
