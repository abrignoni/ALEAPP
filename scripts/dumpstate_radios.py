"""Section readers for the radios of an Android bug report: Bluetooth, NFC, USB and telephony state.

These readers plug into the one-pass reader in ``dumpstate_reader.py``: that module opens each
section of the bug report text and feeds its lines to the classes listed in ``READERS`` below.
Nothing here opens a file or makes a second pass, and nothing judges what it reads.

This module does not import ``dumpstate_reader`` (that module imports this one to register the
readers, and an import in both directions would depend on which of the two is imported first).
The few helpers it needs are small and are written out here; the tables are lists of named tuples
that ``Report.add`` fills, so the row limit (MAX_ROWS) and its warning are the shared ones.

Values are shown as the report prints them. The telephony sections print SIM and phone
identifiers (ICCID, IMSI, phone numbers) and the Bluetooth section prints the adapter's own
address; they are read like any other value, and nothing is masked, replaced or left out. The
tool is run on the examiner's own evidence.
"""
import collections
import re

# Longest text kept for one value, and for one free-text line.
MAX_VALUE = 400
MAX_TEXT = 1000
# Rows of one kind that a single section can add; a damaged text cannot grow a table past this.
MAX_SECTION_ROWS = 200000
# Deepest nesting of the usb service dump that is followed; a deeper level is matched with its closing and not kept.
MAX_DEPTH = 64

_CONTROL = re.compile('[\x00-\x08\x0b-\x1f\x7f]')
_MAC = r'[0-9A-Fa-fXx*]{2}(?::[0-9A-Fa-fXx*]{2}){5}'
_MAC_ONLY = re.compile(r'^' + _MAC + r'$')
_MONTH_DAY_TIME = r'\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?'
_STATE_RECORD = re.compile(r'^\s*rec\[(\d+)\]:\s*time=(' + _MONTH_DAY_TIME + r')\s+processed=(\S*)\s+org=(\S*)\s+dest=(\S*)'
                           r'\s+what=(.*)$')


def tidy(value):
    """A text value with control characters (NUL, lone carriage returns, form feeds) shown as a space."""
    if value is None:
        return ''
    return _CONTROL.sub(' ', str(value))


def to_int(text, default=None):
    """Integer value of a printed decimal number, or ``default``."""
    try:
        value = str(text).strip()
        return int(value) if value.isascii() and value.lstrip('-').isdigit() else default
    except ValueError:
        return default


def split_key_value(text):
    """``(key, value)`` of a ``key: value`` line, split at the first colon that is outside brackets; ``('', '')`` without one."""
    depth = 0
    for index, char in enumerate(text):
        if char in '({[':
            depth += 1
        elif char in ')}]':
            depth = max(depth - 1, 0)
        elif char == ':' and depth == 0 and (index + 1 == len(text) or text[index + 1] == ' '):
            return text[:index].strip(), text[index + 1:].strip()
    return '', ''


def indent_of(text):
    return len(text) - len(text.lstrip(' \t'))


BtStatus = collections.namedtuple('BtStatus', 'item value line')
BtDevice = collections.namedtuple('BtDevice', 'list_name address address_type device_type device_class name profiles packages connection line')
BtEvent = collections.namedtuple('BtEvent', 'source time_text event address detail line')
BtLinkKey = collections.namedtuple('BtLinkKey', 'address br_key le_key line')
NfcState = collections.namedtuple('NfcState', 'group item value line')
NfcService = collections.namedtuple('NfcService', 'service_list component package description uid host aid_group category aid '
                                                  'settings_activity requires_unlock requires_screen_on line')
NfcEvent = collections.namedtuple('NfcEvent', 'time_text event detail line')
NfcDriverLine = collections.namedtuple('NfcDriverLine', 'kernel_time wall_text message line')
UsbState = collections.namedtuple('UsbState', 'path value time_text line')
UsbLogLine = collections.namedtuple('UsbLogLine', 'block kernel_time wall_text event vendor_id product_id message line')
TelState = collections.namedtuple('TelState', 'service phone item value line')
SimSub = collections.namedtuple('SimSub', 'list_name sub_id slot_index carrier_id display_name carrier_name mcc mnc country_iso '
                                          'data_roaming sub_type embedded iccid imsi phone_number card_string number_from_carrier line')
CarrierValue = collections.namedtuple('CarrierValue', 'phone source key value line')
TelLog = collections.namedtuple('TelLog', 'service heading time_text message line')
StateRecord = collections.namedtuple('StateRecord', 'service machine position time_text processed origin destination what line')
TelAccount = collections.namedtuple('TelAccount', 'enabled component package account_id user capabilities audio_routes schemes '
                                                  'extras restrictions line')
RadioLine = collections.namedtuple('RadioLine', 'time_text uid pid tid level tag message line')


class RadioReader:
    """Base of the readers here: gives them the report, the section and the row tables."""
    kind = 'service'
    name = ''
    tables = ()           # the tables of the report that the reader fills; they are created when the reader starts

    def __init__(self, report, section):
        self.report = report
        self.section = section
        self.section_rows = collections.Counter()
        for table in self.tables:
            if not hasattr(report, table):
                setattr(report, table, [])

    def feed(self, line_no, text):
        """One line of the section body (the header line is not included)."""

    def finish(self):
        """The section ended."""

    def add(self, table, row):
        if self.section_rows[table] >= MAX_SECTION_ROWS:
            if self.section_rows[table] == MAX_SECTION_ROWS:
                self.section_rows[table] += 1
                self.report.warn('%s: more than %d rows in the %s section, the rest were not kept' % (
                    table, MAX_SECTION_ROWS, self.name))
            return
        self.section_rows[table] += 1
        # Every text field is tidied here, so a field taken as printed (a word matched by a pattern, a key, a mark)
        # shows its control characters as spaces like the fields that clean() cuts.
        self.report.add(table, type(row)(*[tidy(value) if isinstance(value, str) else value for value in row]))

    def clean(self, value, limit=MAX_VALUE):
        """Control characters shown as spaces, cut to ``limit`` characters. The text is otherwise as printed."""
        return tidy(str(value)[:limit])


# ---------------------------------------------------------------------------------------------
# Bluetooth
# ---------------------------------------------------------------------------------------------
_BT_BONDED = re.compile(
    r'^(?P<addr>' + _MAC + r')(?P<atype>\([^)]*\))?(?:\s*=>\s*' + _MAC + r'(?:\([^)]*\))?)?\s*'
    r'\[\s*(?P<ttype>[^\]]*?)\s*\](?:\s*\[\s*(?P<cls>0x[0-9a-fA-F]+)\s*\])?(?P<acl>\s*\[ACL[^\]]*\])?'
    r'(?:\s*\[\s*Encryption[^\]]*\])?\s*(?P<rest>.*)$')
_BT_CLASS_INLINE = re.compile(r'^\[\s*(0x[0-9a-fA-F]+)\s*\]\s*(.*)$')
_BT_ENABLE_PLAIN = re.compile(r'^(Enabled|Disabled|Enable|Disable)\s+(.*)$')
_BT_ENABLE_PACKAGE = re.compile(r'requested to \[([^\]]+)\]')
_BT_TIME = re.compile(r'^(' + _MONTH_DAY_TIME + r')\s+(.*)$')
_BT_CONN = re.compile(r'^(\S+)\s+(' + _MAC + r')\s*(.*)$')
_BT_LIST = re.compile(r'^(Bonded|Other) devices:(?:\s*(\d+))?\s*$')
_BT_APPS = re.compile(r'^(?:Number of Ble app registered:\s*(\d+)|(\d+) BLE apps? ?registered)\s*$')
_BT_PROPERTIES = ('ConnectionState', 'State', 'ScanMode', 'MaxConnectedAudioDevices', 'A2dpOffloadEnabled', 'Discovering',
                  'DiscoveryEndMs', 'SarType', 'SarStatus')


class BluetoothReader(RadioReader):
    """The bluetooth_manager service dump: adapter status, the bonded and other device lists, events and link key types."""
    name = 'bluetooth_manager'
    tables = ('bt_status', 'bt_devices', 'bt_events', 'bt_link_keys')

    def __init__(self, report, section):
        RadioReader.__init__(self, report, section)
        self.list_name = ''
        self.block = ''           # heading of the list that is being read
        self.block_indent = 0
        self.in_status = False
        self.device = None
        self.link_key = None
        self.properties_seen = set()

    def _flush_device(self):
        device = self.device
        self.device = None
        if device is not None:
            self.add('bt_devices', BtDevice(
                device['list'], device['addr'], device['atype'], device['ttype'], device['cls'], device['name'], device['profiles'],
                device['packages'], device['acl'], device['line']))

    def _flush_key(self):
        key = self.link_key
        self.link_key = None
        if key is not None:
            self.add('bt_link_keys', BtLinkKey(key['addr'], key['br'], key['le'], key['line']))

    def _event(self, source, time_text, event, address, detail, line_no):
        self.add('bt_events', BtEvent(source, tidy(time_text), self.clean(event, 80), self.clean(address, 40),
                                      self.clean(' '.join(detail.split()), MAX_VALUE), line_no))

    def _set_block(self, name, indent):
        self._flush_device()
        self._flush_key()
        self.block, self.block_indent = name, indent

    def _bonded_entry(self, line_no, body):
        found = _BT_BONDED.match(body)
        if found is None:
            return False
        rest = found.group('rest').strip()
        profiles = ''
        if found.group('cls') is None:
            inline = _BT_CLASS_INLINE.match(rest)
            if inline:
                rest = inline.group(2)
                class_text = inline.group(1)
            else:
                class_text = ''
        else:
            class_text = found.group('cls')
        if rest.endswith(')') and ' (' in rest:
            head, _, tail = rest.rpartition(' (')
            if ',' in tail or tail.rstrip(')') in ('SPP', 'AudioSink', 'Avrcp', 'Handsfree', 'PANU', 'MNS'):
                rest, profiles = head, tail[:-1]
        self.device = {'addr': tidy(found.group('addr')), 'atype': tidy((found.group('atype') or '').strip('() ')),
                       'ttype': tidy(found.group('ttype')), 'cls': class_text, 'name': self.clean(rest, 200),
                       'profiles': self.clean(profiles), 'packages': '', 'acl': tidy((found.group('acl') or '').strip(' []')),
                       'line': line_no, 'list': self.list_name}
        return True

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            self._flush_device()
            self._flush_key()
            if self.block in ('bonded', 'link keys', 'enable log', 'connection events', 'scan mode changes'):
                self.block = ''
            return
        indent = indent_of(text)
        if indent == 0:
            self._set_block('', 0)
            self.in_status = body == 'Bluetooth Status'
            if body.startswith('Enable log:'):
                self._set_block('enable log', 0)
            elif body.startswith('Connection Events:'):
                self._set_block('connection events', 0)
            elif body.startswith('Bond Events:'):
                self._set_block('bond events', 0)
            elif body.startswith('Link Key Types:'):
                self._set_block('link keys', 0)
            elif body.startswith('AdapterState:') or body.endswith('BluetoothAdapterState:'):
                self._set_block('adapter state', 0)
            elif body.startswith('Scan Mode Changes:'):
                self._set_block('scan mode changes', 0)
            elif body.startswith('Bluetooth crashed '):
                number = body.split()[2]
                self.add('bt_status', BtStatus('Bluetooth crashed (times)', number, line_no))
            else:
                apps = _BT_APPS.match(body)
                if apps:
                    self.add('bt_status', BtStatus('BLE apps registered', apps.group(1) or apps.group(2), line_no))
                elif body.startswith('ScanMode:'):
                    self.add('bt_status', BtStatus('ScanMode', self.clean(body.split(':', 1)[1].strip()), line_no))
            return
        # ---- indented lines
        if self.in_status:
            key, _, value = body.partition(':')
            if key in ('enabled', 'state', 'address', 'name', 'time since enabled'):
                self.add('bt_status', BtStatus(key, self.clean(value.strip(), 200), line_no))
            return
        if body.startswith('Scan Mode Changes:'):
            self._set_block('scan mode changes', indent)
            return
        device_list = _BT_LIST.match(body)
        if device_list:
            self._set_block('bonded', indent)
            self.list_name = device_list.group(1) + ' devices'
            return
        if body.startswith('Link Key Types:'):
            self._set_block('link keys', indent)
            return
        key, separator, value = body.partition(':')
        if separator and key in _BT_PROPERTIES and indent <= 4 and key not in self.properties_seen and not self.block:
            self.properties_seen.add(key)
            self.add('bt_status', BtStatus(key, self.clean(value.strip(), 200), line_no))
            return
        block = self.block
        if block == 'bonded':
            if indent <= self.block_indent:
                self._flush_device()
                self.block = ''
            elif _MAC_ONLY.match(body.split()[0].split('(')[0]) and self._bonded_flush_and_open(line_no, body):
                return
            elif self.device is not None:
                key, _, value = body.partition(']:')
                if body.startswith('[') and ']:' in body:
                    label = key.strip('[ ')
                    if label.startswith('Packages'):
                        self.device['packages'] = self.clean(value.strip().strip('[]'))
                    elif label.endswith('UUIDs') and not self.device['profiles']:
                        self.device['profiles'] = self.clean(value.strip())
            return
        if block == 'link keys':
            if _MAC_ONLY.match(body):
                self._flush_key()
                self.link_key = {'addr': tidy(body), 'br': '', 'le': '', 'line': line_no}
            elif self.link_key is not None and body.startswith(('BR:', 'LE:')):
                self.link_key['br' if body.startswith('BR:') else 'le'] = self.clean(body[3:].strip(), 120)
            return
        if block == 'enable log':
            found = _BT_TIME.match(body)
            if found:
                detail = found.group(2).strip()
                plain = _BT_ENABLE_PLAIN.match(detail)
                if plain:
                    self._event('Enable log', found.group(1), plain.group(1), '', plain.group(2), line_no)
                else:
                    action = _BT_ENABLE_PACKAGE.search(detail)
                    self._event('Enable log', found.group(1), action.group(1) if action else '', '', detail, line_no)
            return
        if block == 'connection events':
            found = _BT_TIME.match(body)
            if found:
                parts = _BT_CONN.match(found.group(2))
                if parts:
                    self._event('Connection events', found.group(1), parts.group(1), parts.group(2), parts.group(3), line_no)
                else:
                    self._event('Connection events', found.group(1), '', '', found.group(2), line_no)
            return
        if block == 'bond events':
            found = _BT_TIME.match(body)
            if found:
                self._event('Bond events', found.group(1), '', '', found.group(2), line_no)
            return
        if block == 'scan mode changes':
            found = _BT_TIME.match(body)
            if found:
                self._event('Scan mode changes', found.group(1), '', '', found.group(2), line_no)
            return
        if block == 'adapter state':
            record = _STATE_RECORD.match(text)
            if record:
                what = record.group(6).strip()
                event = what.split(' ', 1)[1] if ' ' in what else what
                self._event('Adapter state', record.group(2), event, '',
                            'processed=%s org=%s dest=%s' % (record.group(3), record.group(4), record.group(5)), line_no)

    def _bonded_flush_and_open(self, line_no, body):
        self._flush_device()
        return self._bonded_entry(line_no, body)

    def finish(self):
        self._flush_device()
        self._flush_key()


# ---------------------------------------------------------------------------------------------
# NFC
# ---------------------------------------------------------------------------------------------
_NFC_COMPONENT = re.compile(r'^ComponentInfo\{([^}]*)\}?\s*(?:\(Description:\s*(.*?)\))?\s*(?:\(UID:\s*(-?\d+)\))?\s*$')
_NFC_COMPONENT_LOOSE = re.compile(r'^ComponentInfo\{([^}\s]*)')
_NFC_CATEGORY = re.compile(r'^Category:\s*(.*?)(?:\(enabled:\s*(\w+)\))?\s*$')
_NFC_EVENT = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?):\s+(\S+)\s*(.*)$')
_NFC_STATE_LINE = re.compile(r'^(m?[A-Za-z][A-Za-z0-9_.]*)\s*[=:]\s*(.*)$')
_SERVICE_WRAPPER_KEYS = frozenset({'Service host process PID', 'Threads in use', 'Client PIDs'})


class NfcReader(RadioReader):
    """The nfc service dump: adapter state lines, card emulation services with their AIDs, preferred services, event log."""
    name = 'nfc'
    tables = ('nfc_state', 'nfc_services', 'nfc_events')

    def __init__(self, report, section):
        RadioReader.__init__(self, report, section)
        self.mode = 'state'          # state, services, preferred, routing, other
        self.list_name = ''
        self.service = None
        self.group = ''
        self.category = ''

    def _flush_service(self):
        service = self.service
        self.service = None
        if service is None:
            return
        rows = service['aids'] or [('', '', '')]
        for group, category, aid in rows:
            self.add('nfc_services', NfcService(
                self.list_name, service['component'], service['package'], service['description'], service['uid'],
                service['host'], group, category, aid, service['settings'], service['unlock'], service['screen'],
                service['line']))

    def _new_service(self, line_no, body):
        found = _NFC_COMPONENT.match(body)
        if found:
            component, description, uid = found.group(1), found.group(2) or '', found.group(3) or ''
        else:
            loose = _NFC_COMPONENT_LOOSE.match(body)
            component, description, uid = (loose.group(1) if loose else body), '', ''
        package = component.split('/', 1)[0]
        self._flush_service()
        self.service = {'component': self.clean(component, 300), 'package': self.clean(package, 200),
                        'description': self.clean(description, 200), 'uid': uid, 'host': '', 'aids': [], 'settings': '',
                        'unlock': '', 'screen': '', 'line': line_no}
        self.group = ''
        self.category = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        event = _NFC_EVENT.match(body)
        if event:
            self.add('nfc_events', NfcEvent(event.group(1), self.clean(event.group(2), 120), self.clean(event.group(3)),
                                            line_no))
            return
        if indent == 0:
            if body.startswith('Registered ') and ' services for current user' in body:
                self._flush_service()
                self.mode = 'services'
                self.list_name = body.split(' for current user')[0][len('Registered '):]
                return
            self._flush_service()
            if body.startswith('Preferred services'):
                self.mode = 'preferred'
                return
            if body.startswith('Routing table'):
                self.mode = 'routing'
                return
            if body.startswith(('T3T Identifier', 'HCE-F routing', 'Bound HCE', 'mNfcee', 'mOverride', '---', '=====')):
                self.mode = 'other'
                return
            if self.mode == 'state':
                found = _NFC_STATE_LINE.match(body)
                if found and found.group(1) not in _SERVICE_WRAPPER_KEYS:
                    self.add('nfc_state', NfcState('Adapter state', self.clean(found.group(1), 80),
                                                   self.clean(found.group(2)), line_no))
            return
        if self.mode == 'services':
            if body.startswith('ComponentInfo{'):
                self._new_service(line_no, body)
            elif self.service is not None:
                self._service_line(body)
        elif self.mode == 'preferred':
            key, value = split_key_value(body.lstrip('* '))
            if key and not body.startswith(('"', '*DEFAULT*', 'ComponentInfo')) and 'AID cache' not in body:
                self.add('nfc_state', NfcState('Preferred services', self.clean(key, 120), self.clean(value), line_no))
        elif self.mode == 'routing':
            if body.startswith('Default route:'):
                self.add('nfc_state', NfcState('Routing table', 'Default route', self.clean(body.split(':', 1)[1].strip()),
                                               line_no))

    def _service_line(self, body):
        service = self.service
        if body in ('On Host Service', 'Off-host Service', 'Off Host Service'):
            service['host'] = body
        elif body.startswith('Static AID groups'):
            self.group, self.category = 'static', ''
        elif body.startswith('Dynamic AID groups'):
            self.group, self.category = 'dynamic', ''
        elif body.startswith('Category:'):
            found = _NFC_CATEGORY.match(body)
            self.category = self.clean(found.group(1).strip() if found else body[9:].strip(), 80)
            if found and found.group(2):
                self.category += ' (enabled: %s)' % found.group(2)
        elif body.startswith('AID:'):
            service['aids'].append((self.group, self.category, self.clean(body[4:].strip(), 80)))
        elif body.startswith('Settings Activity:'):
            service['settings'] = self.clean(body.split(':', 1)[1].strip(), 200)
        elif body.startswith('Requires Device Unlock:'):
            service['unlock'] = self.clean(body.split(':', 1)[1].strip(), 20)
        elif body.startswith('Requires Device ScreenOn:'):
            service['screen'] = self.clean(body.split(':', 1)[1].strip(), 20)

    def finish(self):
        self._flush_service()


_NFC_DRIVER = re.compile(r'^\[\s*([^\]]*?)\s*\]\s*(?:\[(\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?)\]\s*)?(.*)$')


class NfcDriverLogReader(RadioReader):
    """The NFC SYSTEM LOG command section (the NFC kernel driver log some builds print)."""
    kind = 'command'
    name = 'NFC SYSTEM LOG'
    tables = ('nfc_driver_log',)

    def feed(self, line_no, text):
        if not text.strip():
            return
        found = _NFC_DRIVER.match(text)
        if found:
            self.add('nfc_driver_log', NfcDriverLine(tidy(found.group(1)), tidy(found.group(2) or ''),
                                                     self.clean(found.group(3).strip(), MAX_VALUE), line_no))
        else:
            self.add('nfc_driver_log', NfcDriverLine('', '', self.clean(text.strip(), MAX_VALUE), line_no))


# ---------------------------------------------------------------------------------------------
# USB
# ---------------------------------------------------------------------------------------------
_USB_EVENT = re.compile(r'^(\d\d-\d\d \d\d:\d\d:\d\d:\d+)\s+(.*)$')
_USB_STATE_ROOTS = frozenset({'device_manager', 'host_manager', 'port_manager', 'alsa_manager'})


class UsbStateReader(RadioReader):
    """The usb service dump: the device, host, port and ALSA manager state as path = value, and the USB event list."""
    name = 'usb'
    tables = ('usb_state',)

    def __init__(self, report, section):
        RadioReader.__init__(self, report, section)
        self.stack = []             # [name, child counter, opening character]
        self.overflow = 0           # openings beyond MAX_DEPTH, which are matched with their closings and not kept
        self.events = False

    def _path(self):
        return '.'.join(item[0] for item in self.stack if item[0])

    def _push(self, item):
        if len(self.stack) >= MAX_DEPTH:
            self.overflow += 1
        else:
            self.stack.append(item)

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(('USB MANAGER STATE', 'Service host process', 'Threads in use', 'Client PIDs')):
            return
        if body in ('{', '['):
            name = ''
            if self.stack:
                parent = self.stack[-1]
                name = '[%d]' % parent[1] if parent[2] == '[' else ''
                parent[1] += 1
            self._push([name, 0, body])
            return
        if body in ('}', ']', '},', '],'):
            if self.overflow:
                self.overflow -= 1
            elif self.stack:
                self.stack.pop()
            self.events = False
            return
        if body.endswith(('={', '=[')):
            key = body[:-2]
            if self.stack:
                self.stack[-1][1] += 1
            self._push([key, 0, body[-1]])
            self.events = key == 'USB Event' and body.endswith('=[') and not self.overflow
            return
        names = [item[0] for item in self.stack if item[0]]
        if self.overflow or not names or names[0] not in _USB_STATE_ROOTS:
            return
        if self.events:
            found = _USB_EVENT.match(body)
            if found:
                self.add('usb_state', UsbState(self._path(), self.clean(found.group(2), MAX_TEXT), found.group(1), line_no))
            return
        key, separator, value = body.partition('=')
        if separator:
            path = self._path()
            self.add('usb_state', UsbState((path + '.' if path else '') + key, self.clean(value), '', line_no))


_USB_LOG_LINE = re.compile(r'^\[(?:(\d\d-\d\d \d\d:\d\d:\d\d)\]\s*\[)?\s*(\d+\.\d+)\]\s*(.*)$')
_USB_SYNC = re.compile(r'^time sync:\s*\[(\d\d-\d\d \d\d:\d\d:\d\d)\]\s*\[\s*(\d+\.\d+)\]')
_USB_VID_PID = re.compile(r'VID:(0x[0-9a-fA-F]+)\s+PID:(0x[0-9a-fA-F]+)')
_USB_PORT = re.compile(r'^(port (?:connect|disconnect))\b')


class UsbLogReader(RadioReader):
    """The USB LOG command section (the /proc/usblog ring buffers some Samsung builds print)."""
    kind = 'command'
    name = 'USB LOG'
    tables = ('usb_log',)

    def __init__(self, report, section):
        RadioReader.__init__(self, report, section)
        self.block = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        sync = _USB_SYNC.match(body)
        if sync:
            self.add('usb_log', UsbLogLine('time sync', sync.group(2), sync.group(1), '', '', '', 'time sync', line_no))
            return
        if body.startswith('usblog '):
            self.block = self.clean(body[7:].split(':', 1)[0], 60)
            self.add('usb_log', UsbLogLine(self.block, '', '', '', '', '', self.clean(body, MAX_VALUE), line_no))
            return
        found = _USB_LOG_LINE.match(body)
        if found:
            message = found.group(3).strip()
            ids = _USB_VID_PID.search(message)
            port = _USB_PORT.match(message)
            self.add('usb_log', UsbLogLine(self.block, found.group(2), found.group(1) or '', port.group(1) if port else '',
                                           ids.group(1) if ids else '', ids.group(2) if ids else '',
                                           self.clean(message, MAX_VALUE), line_no))
        else:
            self.add('usb_log', UsbLogLine(self.block, '', '', '', '', '', self.clean(body, MAX_VALUE), line_no))


# ---------------------------------------------------------------------------------------------
# Telephony
# ---------------------------------------------------------------------------------------------
_TEL_LOG = re.compile(r'^\s*(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?)\s+-\s+(.*)$')
_TEL_ITEM = re.compile(r'^(m?[A-Za-z][A-Za-z0-9_]*(?:\[\d+\])?)=(.*)$')
_TEL_PHONE_ID = re.compile(r'^Phone Id\s*=\s*(\d+)\s*$')
# Items that are lists of public or very long text: not listed.
_SKIP_ITEMS = frozenset({'mEmergencyNumberList'})


class TelephonyReader(RadioReader):
    """Base of the telephony service readers: timestamped log lines and state machine records are read the same way."""
    tables = ('telephony_state', 'telephony_logs', 'state_records', 'carrier_values', 'sim_subscriptions',
              'telecom_accounts')

    def __init__(self, report, section):
        RadioReader.__init__(self, report, section)
        self.heading = ''
        self.candidate = ''
        self.machine = ''

    def state(self, phone, item, value, line_no):
        if item in _SKIP_ITEMS:
            return
        self.add('telephony_state', TelState(self.name, phone, self.clean(item, 80), self.clean(value.strip()), line_no))

    def log_line(self, line_no, text):
        """True when the line was a timestamped log line or a state machine record (it has been kept)."""
        log = _TEL_LOG.match(text)
        if log:
            self.add('telephony_logs', TelLog(self.name, self.clean(self.heading, 100), log.group(1),
                                              self.clean(log.group(2), MAX_TEXT), line_no))
            return True
        record = _STATE_RECORD.match(text)
        if record:
            self.add('state_records', StateRecord(self.name, self.clean(self.machine, 100), int(record.group(1)), record.group(2),
                                                  self.clean(record.group(3), 100), self.clean(record.group(4), 100),
                                                  self.clean(record.group(5), 100), self.clean(record.group(6).strip(), 200),
                                                  line_no))
            return True
        body = text.strip()
        if body.startswith('total records='):
            self.machine = self.candidate
        elif body and not body.startswith('curState=') and body.strip('+-=*') != '':
            self.heading = body[:100]
            if body.endswith(':'):
                self.candidate = body[:-1].strip()
        return False


class TelephonyRegistryReader(TelephonyReader):
    """The telephony.registry service dump: the last known state of each phone and the local and listen logs."""
    name = 'telephony.registry'

    def __init__(self, report, section):
        TelephonyReader.__init__(self, report, section)
        self.mode = ''
        self.phone = ''

    def feed(self, line_no, text):
        if self.log_line(line_no, text):
            return
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if indent == 0:
            self.mode = 'state' if body.startswith('last known state') else (
                'logs' if body.startswith(('local logs', 'listen logs')) else (
                    'registrations' if body.startswith('registrations') else self.mode))
            return
        if self.mode != 'state':
            return
        found = _TEL_PHONE_ID.match(body) if indent <= 2 else None
        if found:
            self.phone = found.group(1)
            return
        item = _TEL_ITEM.match(body)
        if item and indent <= 4:
            self.state('' if indent <= 2 else self.phone, item.group(1), item.group(2), line_no)


class PhoneReader(TelephonyReader):
    """The phone service dump: the PhoneGlobals values and the timestamped logs."""
    name = 'phone'

    def __init__(self, report, section):
        TelephonyReader.__init__(self, report, section)
        self.in_globals = False

    def feed(self, line_no, text):
        if self.log_line(line_no, text):
            return
        body = text.strip()
        if body == '------- PhoneGlobals -------':
            self.in_globals = True
        elif body == '------- End PhoneGlobals -------':
            self.in_globals = False
        elif self.in_globals and indent_of(text) == 2:
            item = _TEL_ITEM.match(body)
            if item:
                self.state('', item.group(1), item.group(2), line_no)


_SUB_ID = re.compile(r'\bid=(-?\d+)')
_SUB_SLOT = re.compile(r'\bsimSlotIndex=(-?\d+)')
_SUB_CARRIER_ID = re.compile(r'\bcarrierId=(\S+)')
_SUB_DISPLAY = re.compile(r'\bdisplayName=(.*?)\s+carrierName=')
_SUB_CARRIER = re.compile(r'\bcarrierName=(.*?)\s+(?:nameSource|isOpportunistic|displayNameSource)=')
_SUB_MCC = re.compile(r'\bmcc[= ]\s*([0-9*]+)')
_SUB_MNC = re.compile(r'\bmnc[= ]\s*([0-9*]+)')
_SUB_COUNTRY = re.compile(r'[cC]ountryIso=(\S*)')
_SUB_ROAMING = re.compile(r'\bdataRoaming=(-?\d+)')
_SUB_TYPE = re.compile(r'\b(?:subscriptionType|type)=(\S+)')
_SUB_EMBEDDED = re.compile(r'\bisEmbedded[= ]\s*(\w+)')
_SUB_ICCID = re.compile(r'\biccId=(\S*)')
_SUB_IMSI = re.compile(r'\bimsi=(\S*)')
_SUB_NUMBER = re.compile(r'\b(?:mNumber|number)=(\S*)')
_SUB_CARD = re.compile(r'\bcardString=(\S*)')
_SUB_FROM_CARRIER = re.compile(r'\bnumberFromCarrier=(\S*)')
_SIM_ITEM = re.compile(r'^(Active modem count|Logical SIM slot \d+|default\w*|activeDataSubId|areAllSubscriptionsLoaded|'
                       r'mSimState\[\d+\]|sSlotIndexToSubId\[\d+\])\s*[=:]\s*(.*)$')


def _first(pattern, text):
    found = pattern.search(text)
    return found.group(1).strip() if found else ''


def _last_value(pattern, text):
    """Like ``_first``, but a closing bracket of the record that follows the value directly is not part of it."""
    found = pattern.search(text)
    if not found:
        return ''
    value = found.group(1).strip()
    if found.end() == len(text.rstrip()) and value[-1:] in (']', '}'):
        value = value[:-1]
    return value


class SubscriptionReader(TelephonyReader):
    """The isub service dump: the SIM slots, the default subscriptions and the subscription list.

    The ICCID, IMSI, phone number and card string printed on each subscription are read as printed.
    """
    name = 'isub'

    def __init__(self, report, section):
        TelephonyReader.__init__(self, report, section)
        self.list_name = ''

    def feed(self, line_no, text):
        if self.log_line(line_no, text):
            return
        body = text.strip()
        if body in ('Active subscriptions:', 'ActiveSubInfoList:'):
            self.list_name = 'active'
            return
        if body in ('All subscriptions:', 'AllSubInfoList:'):
            self.list_name = 'all'
            return
        if body.startswith(('[SubscriptionInfoInternal:', '{id=')) and self.list_name:
            self.add('sim_subscriptions', SimSub(
                self.list_name, to_int(_first(_SUB_ID, body)), to_int(_first(_SUB_SLOT, body)), self.clean(_first(_SUB_CARRIER_ID, body), 20),
                self.clean(_first(_SUB_DISPLAY, body), 100), self.clean(_first(_SUB_CARRIER, body), 100),
                self.clean(_first(_SUB_MCC, body), 10), self.clean(_first(_SUB_MNC, body), 10),
                self.clean(_first(_SUB_COUNTRY, body), 10), self.clean(_first(_SUB_ROAMING, body), 10),
                self.clean(_first(_SUB_TYPE, body), 30), self.clean(_first(_SUB_EMBEDDED, body), 10),
                self.clean(_last_value(_SUB_ICCID, body), 60), self.clean(_last_value(_SUB_IMSI, body), 60),
                self.clean(_last_value(_SUB_NUMBER, body), 60), self.clean(_last_value(_SUB_CARD, body), 60),
                self.clean(_last_value(_SUB_FROM_CARRIER, body), 60), line_no))
            return
        if body.startswith('++++'):
            return
        item = _SIM_ITEM.match(body)
        if item:
            self.state('', item.group(1), item.group(2), line_no)


class SmsServiceReader(TelephonyReader):
    """The isms service dump: the timestamped logs and the state machine records of the SMS and cell broadcast handlers.

    The records say that a handler changed state at a time; they hold no message text.
    """
    name = 'isms'

    def feed(self, line_no, text):
        self.log_line(line_no, text)


_CARRIER_SOURCE = re.compile(r'^(m[A-Za-z]+)\s*:\s*(null)?\s*$')
_CARRIER_KEY = re.compile(r'^(\S+)\s+=\s+(.*)$')
_CARRIER_CACHE = re.compile(r'^(\S+?),\s*modified time=(.*)$')


class CarrierConfigReader(TelephonyReader):
    """The carrier_config service dump: the values the carrier configuration app set for each phone, the cached files, the log.

    The block of default values that the platform prints before them is counted and not listed.
    """
    name = 'carrier_config'

    def __init__(self, report, section):
        TelephonyReader.__init__(self, report, section)
        self.phone = ''
        self.source = ''
        self.cache = False
        self.defaults = collections.Counter()

    def feed(self, line_no, text):
        if self.log_line(line_no, text):
            return
        body = text.strip()
        if not body:
            return
        phone = _TEL_PHONE_ID.match(body)
        if phone:
            self.phone, self.source, self.cache = phone.group(1), '', False
            return
        if body.startswith('Default Values from CarrierConfigManager'):
            self.source, self.cache = 'defaults', False
            return
        source = _CARRIER_SOURCE.match(body)
        if source and indent_of(text) <= 4:
            self.source, self.cache = source.group(1), False
            return
        if body.startswith('Cached config files'):
            self.source, self.cache = '', True
            return
        if self.cache:
            cached = _CARRIER_CACHE.match(body)
            if cached:
                self.add('carrier_values', CarrierValue('', 'Cached config files', self.clean(cached.group(1), 200),
                                                        self.clean('modified time=' + cached.group(2).strip(), 100), line_no))
            return
        if self.source == 'defaults':
            if _CARRIER_KEY.match(body):
                self.defaults[self.phone] += 1
            return
        if indent_of(text) == 0:
            item = _TEL_ITEM.match(body)
            if item:
                self.state('', item.group(1), item.group(2), line_no)
            return
        pair = _CARRIER_KEY.match(body)
        if pair and self.source:
            self.add('carrier_values', CarrierValue(self.phone, self.source, self.clean(pair.group(1), 150),
                                                    self.clean(pair.group(2).strip()), line_no))

    def finish(self):
        if self.defaults:
            counts = getattr(self.report, 'carrier_default_counts', None)
            if counts is None:
                counts = self.report.carrier_default_counts = collections.Counter()
            counts.update(self.defaults)


_ACCOUNT = re.compile(r'^\[\[(.)\]\s*PhoneAccount:\s*ComponentInfo\{([^}]*)\},\s*(.*?),\s*UserHandle\{(\d+)\}\s*(.*)$')
_ACCOUNT_FIELDS = ('Capabilities:', 'Audio Routes:', 'Schemes:', 'Extras:', 'GroupId:', 'SC Restrictions:')


def split_account_fields(tail):
    """``{field: text}`` of the fields of a PhoneAccount line, in the order the platform prints them."""
    found = []
    for field in _ACCOUNT_FIELDS:
        index = tail.find(field)
        if index >= 0:
            found.append((index, field))
    found.sort()
    values = {}
    for number, (index, field) in enumerate(found):
        stop = found[number + 1][0] if number + 1 < len(found) else len(tail)
        values[field] = tail[index + len(field):stop].strip()
    return values


class TelecomReader(TelephonyReader):
    """The telecom service dump: the registered phone accounts and the timestamped logs. Calls are not read."""
    name = 'telecom'

    def feed(self, line_no, text):
        if self.log_line(line_no, text):
            return
        body = text.strip()
        found = _ACCOUNT.match(body)
        if found:
            fields = split_account_fields(found.group(5)[:-1] if found.group(5).endswith(']') else found.group(5))
            component = found.group(2)
            self.add('telecom_accounts', TelAccount(
                found.group(1), self.clean(component, 300), self.clean(component.split('/', 1)[0], 200),
                self.clean(found.group(3), 60), found.group(4), self.clean(fields.get('Capabilities:', ''), 200),
                self.clean(fields.get('Audio Routes:', ''), 60), self.clean(fields.get('Schemes:', ''), 100),
                self.clean(fields.get('Extras:', '')), self.clean(fields.get('SC Restrictions:', ''), 100), line_no))


# The tags of the radio log lines that are read. They are the tags of the platform's service, network, data and
# subscription state trackers; the lines of every other tag (the modem request and response traces, the AT command
# trace, the SIM phone book and SMS handling) are not read.
RADIO_STATE_TAGS = ('SST', 'ServiceStateTracker', 'SSCtr', 'NetworkTypeController', 'DNC-', 'DN-', 'DefaultPhoneNotifier',
                    'LocaleTracker', 'NitzStateMachineImpl', 'PhoneSwitcher', 'SubscriptionController',
                    'SubscriptionManagerService', 'TelephonyRegistry', 'TelephonyNetworkFactory', 'DIC-',
                    'TelephonyCountryDetector', 'CellularNetworkService', 'NRM-', 'ImsPhone')
_RADIO_LINE = re.compile(r'^(\d\d-\d\d \d\d:\d\d:\d\d\.\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+([VDIWEFA])\s+(.*?)\s*:\s?(.*)$')


class RadioLogReader(RadioReader):
    """The RADIO LOG command section (logcat -b radio): only the lines of the state tracker tags above are kept."""
    kind = 'command'
    name = 'RADIO LOG'
    tables = ('radio_log',)

    def __init__(self, report, section):
        RadioReader.__init__(self, report, section)
        self.seen = 0
        self.kept = 0

    def feed(self, line_no, text):
        found = _RADIO_LINE.match(text)
        if not found:
            return
        self.seen += 1
        tag = found.group(6).strip()
        if not tag.startswith(RADIO_STATE_TAGS):
            return
        self.kept += 1
        self.add('radio_log', RadioLine(found.group(1), tidy(found.group(2)), found.group(3), found.group(4), found.group(5),
                                        self.clean(tag, 60), self.clean(found.group(7), MAX_TEXT), line_no))

    def finish(self):
        counts = getattr(self.report, 'radio_log_counts', None)
        if counts is None:
            counts = self.report.radio_log_counts = [0, 0]
        counts[0] += self.seen
        counts[1] += self.kept


READERS = [BluetoothReader, NfcReader, NfcDriverLogReader, UsbStateReader, UsbLogReader, TelephonyRegistryReader,
           PhoneReader, SubscriptionReader, SmsServiceReader, CarrierConfigReader, TelecomReader, RadioLogReader]
# Which artifacts present each section, for the section index.
READ_BY = {
    ('service', 'bluetooth_manager'): 'Bluetooth Adapter Status; Bluetooth Devices; Bluetooth Events; '
                                      'Bluetooth Link Key Types',
    ('service', 'nfc'): 'NFC State; NFC Card Emulation Services; NFC Events',
    ('command', 'NFC SYSTEM LOG'): 'NFC Driver Log',
    ('service', 'usb'): 'USB Manager State',
    ('command', 'USB LOG'): 'USB Log',
    ('service', 'telephony.registry'): 'Telephony State; Telephony Service Logs',
    ('service', 'phone'): 'Telephony State; Telephony Service Logs',
    ('service', 'isub'): 'SIM Subscriptions; Telephony State; Telephony Service Logs',
    ('service', 'isms'): 'Telephony State Machine Records; Telephony Service Logs',
    ('service', 'carrier_config'): 'Carrier Config Values; Telephony State; Telephony Service Logs',
    ('service', 'telecom'): 'Telecom Phone Accounts; Telephony Service Logs',
    ('command', 'RADIO LOG'): 'Radio Log State Lines',
}
