"""Android bug report text: Bluetooth, NFC, USB, telephony state and the radio log."""
# pylint: disable=protected-access,no-member
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as base
from admin.test.scripts import bugreport_radios_fixture as fixture
from scripts import dumpstate_radios as radios
from scripts import dumpstate_reader as reader
from scripts.artifacts import bugreportRadios as artifacts


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


def scan_text(text):
    report = reader.Report(reader.Source('memory', ''))
    data = text.encode('utf-8') if isinstance(text, str) else text
    reader.scan_lines(reader.iter_lines(io.BytesIO(data)), report)
    report.finish()
    return report


def section_text(*parts):
    return base.BANNER.format(report=fixture.REPORT) + '\n------ DUMPSYS (/system/bin/dumpsys) ------\n' + ''.join(parts)


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


def rows_of(report, table):
    return getattr(report, table, [])


class BluetoothTests(unittest.TestCase):
    def test_bonded_devices_in_the_three_layouts(self):
        a16 = rows_of(scan_text(fixture.build_report('a16')), 'bt_devices')
        self.assertEqual([(d.address, d.device_type, d.device_class, d.name) for d in a16],
                         [('XX:XX:XX:XX:BB:11', 'BR/EDR', '0x340408', 'Example Car Kit'),
                          ('XX:XX:XX:XX:BB:22', 'DUAL', '0x360408', 'Example Speaker')])
        self.assertEqual(a16[0].profiles, '00000000-aaaa-bbbb-cccc-000000000001,SPP,AudioSink,Avrcp')
        a15 = rows_of(scan_text(fixture.build_report('a15')), 'bt_devices')
        self.assertEqual([(d.address, d.device_type, d.name) for d in a15],
                         [('02:00:00:00:CC:11', '????', 'Example Watch'), ('02:00:00:00:CC:22', '????', 'Example Buds')])
        a10 = rows_of(scan_text(fixture.build_report('a10')), 'bt_devices')
        self.assertEqual([(d.address, d.device_type, d.name) for d in a10],
                         [('02:11:**:**:**:95', 'BR/EDR', 'Example Car'), ('02:12:**:**:**:96', 'LE', 'Example Tag')])

    def test_remote_device_layout_with_uuids_and_packages(self):
        text = section_text(service('bluetooth_manager', '''BluetoothRemoteDevices
  Bonded devices: 2
    XX:XX:XX:XX:Ec:Fe(Public ) => XX:XX:XX:XX:Ec:Fe(Public ) [ DUAL ] [0x280704] [ACL BR/EDR:N LE:N] [ Encryption status(BR/EDR): null LE: null] Example Watch
        [BR/EDR UUIDs]: SPP AudioSource Hid 00000000-1111-2222-3333-000000000002
    XX:XX:XX:XX:dc:8c(Public ) => XX:XX:XX:XX:dc:8c(Public ) [  LE  ] [0x001F00] [ACL BR/EDR:N LE:N] [ Encryption status(BR/EDR): null LE: null] Example Pen
        [Packages    ]: [com.example.pen]

  Other devices: 1
    XX:XX:XX:XX:31:F3(Public ) => XX:XX:XX:XX:XX:XX(Unknown) [ DUAL ] [0x001F00] [ACL BR/EDR:N LE:N] [ Encryption status(BR/EDR): null LE: null] [TV] Example Display (65)

  Devices in DB:
    XX:XX:XX:XX:Ec:Fe | Example Watch | 2 | 3
''', ))
        devices = rows_of(scan_text(text), 'bt_devices')
        self.assertEqual([(d.list_name, d.address, d.address_type, d.device_type, d.device_class, d.name, d.connection)
                          for d in devices],
                         [('Bonded devices', 'XX:XX:XX:XX:Ec:Fe', 'Public', 'DUAL', '0x280704', 'Example Watch', 'ACL BR/EDR:N LE:N'),
                          ('Bonded devices', 'XX:XX:XX:XX:dc:8c', 'Public', 'LE', '0x001F00', 'Example Pen', 'ACL BR/EDR:N LE:N'),
                          ('Other devices', 'XX:XX:XX:XX:31:F3', 'Public', 'DUAL', '0x001F00', '[TV] Example Display (65)',
                           'ACL BR/EDR:N LE:N')])
        self.assertEqual(devices[0].profiles, 'SPP AudioSource Hid 00000000-1111-2222-3333-000000000002')
        self.assertEqual(devices[1].packages, 'com.example.pen')

    def test_events_status_and_link_keys(self):
        report = scan_text(fixture.build_report('a15'))
        events = rows_of(report, 'bt_events')
        self.assertEqual([(e.source, e.event) for e in events],
                         [('Enable log', 'Enabled'), ('Enable log', 'Disabled'), ('Adapter state', 'BLE_TURN_ON'),
                          ('Connection events', 'DISCONNECTED'), ('Connection events', 'CONNECTED')])
        self.assertEqual(events[3].address, 'xx:xx:xx:xx:cc:11')
        self.assertEqual(events[3].detail, 'reason=22')
        self.assertEqual(events[0].detail, 'due to APPLICATION_REQUEST by android')
        keys = rows_of(report, 'bt_link_keys')
        self.assertEqual([(k.address, k.br_key, k.le_key) for k in keys], [('xx:xx:xx:xx:cc:11', 'UNAUTH_COMB', 'LE_KEY_PENC LE_KEY_LID')])
        status = {s.item: s.value for s in rows_of(report, 'bt_status')}
        self.assertEqual((status['enabled'], status['state'], status['BLE apps registered']), ('false', 'BLE_ON', '1'))
        self.assertEqual(status['address'], '02:00:00:00:AA:02')   # the adapter's own address is shown as printed

    def test_enable_log_in_the_package_layout_and_scan_mode_changes(self):
        events = rows_of(scan_text(fixture.build_report('a16')), 'bt_events')
        self.assertEqual(events[0].event, 'Enable')
        self.assertIn('Reason is SYSTEM_BOOT', events[0].detail)
        self.assertIn(('Scan mode changes', '11-02 07:17:34.872'), [(e.source, e.time_text) for e in events])

    def test_bond_events_and_an_empty_list(self):
        text = section_text(service('bluetooth_manager', '''Bond Events:
  Total Number of events: 1
  11-02 07:00:00.100 Bond state changed to BONDING
Connection Events:
  None
'''))
        events = rows_of(scan_text(text), 'bt_events')
        self.assertEqual([(e.source, e.time_text) for e in events], [('Bond events', '11-02 07:00:00.100')])

    def test_a_dump_that_was_never_enabled_has_no_devices(self):
        text = section_text(service('bluetooth_manager', '''Bluetooth Status
  enabled: false
  state: OFF
  address: 02:00:00:00:00:01
  name: Example

Bluetooth never enabled!
'''))
        report = scan_text(text)
        self.assertEqual(rows_of(report, 'bt_devices'), [])
        self.assertEqual([s.item for s in rows_of(report, 'bt_status')], ['enabled', 'state', 'address', 'name'])


def service(name, body):
    return fixture.service(name, body)


class NfcTests(unittest.TestCase):
    def test_state_services_aids_and_events(self):
        report = scan_text(fixture.build_report('a16'))
        state = {(s.group, s.item): s.value for s in rows_of(report, 'nfc_state')}
        self.assertEqual(state[('Adapter state', 'mState')], 'on')
        self.assertEqual(state[('Adapter state', 'pollTech')], '0x2f')
        self.assertEqual(state[('Routing table', 'Default route')], 'host')
        self.assertEqual(state[('Preferred services', 'Default for foreground app (UID: 0)')], 'null')
        self.assertNotIn(('Adapter state', 'Threads in use'), state)
        services = rows_of(report, 'nfc_services')
        self.assertEqual(len(services), 5)                         # a service with no AID is one row
        pay = [s for s in services if s.package == 'com.example.pay']
        self.assertEqual([(s.aid_group, s.category, s.aid) for s in pay],
                         [('static', 'payment (enabled: true)', 'A0000000FFFF0000'),
                          ('dynamic', 'payment (enabled: true)', 'A0000000FFFF0001'),
                          ('dynamic', 'payment (enabled: true)', 'A0000000FFFF0002')])
        self.assertEqual((pay[0].description, pay[0].uid, pay[0].host, pay[0].settings_activity),
                         ('Example Pay', '10501', 'On Host Service', 'com.example.pay.Settings'))
        transit = services[-1]
        self.assertEqual((transit.host, transit.aid, transit.description), ('Off-host Service', '', 'null'))
        events = rows_of(report, 'nfc_events')
        self.assertEqual([e.event for e in events], ['reader_mode_change', 'reader_mode_change', 'bootup_state', 'aid_registration'])
        self.assertEqual(events[0].time_text, '2026-11-01 11:57:17.101')

    def test_driver_log_lines_with_and_without_wall_time(self):
        lines = rows_of(scan_text(fixture.build_report('a16')), 'nfc_driver_log')
        self.assertEqual(len(lines), 9)
        self.assertEqual((lines[0].kernel_time, lines[0].wall_text, lines[0].message), ('B   1.670555', '', 'sec_nfc_init'))
        self.assertEqual((lines[4].wall_text, lines[4].message), ('11-01 16:33:33.757', 'en(0) firm(1) pvdd(1) irq(0) mode(2) clk_state(0)'))
        self.assertEqual((lines[6].kernel_time, lines[6].wall_text), ('687861.569311', '11-02 05:54:38.685'))
        self.assertEqual((lines[8].kernel_time, lines[8].message), ('', '32.684900] clk'))      # a damaged line is kept as printed

    def test_no_nfc_section_gives_no_rows(self):
        report = scan_text(fixture.build_report('a10'))
        self.assertEqual(rows_of(report, 'nfc_events'), [])
        self.assertEqual(rows_of(report, 'nfc_driver_log'), [])
        self.assertEqual(len(rows_of(report, 'nfc_services')), 5)


class UsbTests(unittest.TestCase):
    def test_state_paths_and_events(self):
        rows = rows_of(scan_text(fixture.build_report('a15')), 'usb_state')
        paths = {row.path: row.value for row in rows if not row.time_text}
        self.assertEqual(paths['device_manager.handler.kernel_state'], 'DISCONNECTED')
        self.assertEqual(paths['port_manager.usb_ports.status.role_combinations.power_role'], 'no-power')
        self.assertEqual(paths['port_manager.usb_hal_version'], '13')
        self.assertFalse([path for path in paths if 'activity' in path or path.startswith('settings_manager')])
        events = [row for row in rows if row.time_text]
        self.assertEqual([row.time_text for row in events], ['11-02 06:05:38:034', '11-02 06:05:38:039'])
        self.assertEqual(events[0].path, 'device_manager.USB Event')
        self.assertTrue(events[0].value.startswith('USB intent: Intent'))

    def test_arrays_of_ports_are_numbered(self):
        text = section_text(service('usb', '''USB MANAGER STATE (dumpsys usb):
{
  port_manager={
    usb_ports=[
      {
        port={
          id=port0
        }
      }
      {
        port={
          id=port1
        }
      }
    ]
  }
}'''))
        rows = rows_of(scan_text(text), 'usb_state')
        self.assertEqual([(r.path, r.value) for r in rows],
                         [('port_manager.usb_ports.[0].port.id', 'port0'), ('port_manager.usb_ports.[1].port.id', 'port1')])

    def test_log_lines_and_vendor_product_numbers(self):
        lines = rows_of(scan_text(fixture.build_report('a16')), 'usb_log')
        sync = [line for line in lines if line.block == 'time sync']
        self.assertEqual((sync[0].kernel_time, sync[0].wall_text), ('688349.963811', '11-02 06:02:46'))
        connect = [line for line in lines if line.event == 'port connect']
        self.assertEqual((connect[0].vendor_id, connect[0].product_id, connect[0].kernel_time), ('0x1234', '0x5678', '509596.560543'))
        self.assertEqual([line.event for line in lines if line.event], ['port connect', 'port disconnect'])
        dual = [line for line in lines if line.kernel_time == '1866.503644'][0]
        self.assertEqual(dual.wall_text, '11-01 20:38:23')
        glued = [line for line in lines if line.kernel_time == '1867.029714'][0]
        self.assertEqual(glued.wall_text, '11-01 20:38:24')       # the stamps printed with no space between them
        self.assertEqual({line.block for line in lines if line.kernel_time}, {'time sync', 'CCIC EVENT', 'EXTRA'})


class TelephonyTests(unittest.TestCase):
    def test_registry_state_by_phone(self):
        state = rows_of(scan_text(fixture.build_report('a15')), 'telephony_state')
        registry = {(s.phone, s.item): s.value for s in state if s.service == 'telephony.registry'}
        self.assertEqual(registry[('0', 'mCallState')], '0')
        self.assertTrue(registry[('0', 'mServiceState')].startswith('{mVoiceRegState=0(IN_SERVICE)'))
        self.assertEqual(registry[('1', 'mCellIdentity')], 'null')
        self.assertEqual(registry[('', 'mActiveDataSubId')], '1')
        self.assertNotIn(('', 'mEmergencyNumberList'), registry)
        phone = {s.item: s.value for s in state if s.service == 'phone'}
        self.assertEqual((phone['mDefaultDataSubId'], phone['isSmsCapable']), ('1', 'true'))
        self.assertNotIn('exampleFlag', phone)

    def test_identifiers_are_shown_as_printed(self):
        report = scan_text(fixture.build_report('a15'))
        every_value = []
        for table in ('telephony_state', 'telephony_logs', 'sim_subscriptions', 'carrier_values', 'state_records', 'radio_log'):
            for row in rows_of(report, table):
                every_value.extend(str(value) for value in row)
        text = '\n'.join(every_value)
        for printed in ('+15550100', '+15550101', '89990000000000000011', '001010000000001', '-1234567890123456789'):
            self.assertIn(printed, text, printed)
        self.assertNotIn('withheld', text.replace('carrierconfig-com.example.carrier-withheld', ''))
        incoming = [s for s in rows_of(report, 'telephony_state') if s.item == 'mCallIncomingNumber']
        self.assertEqual([s.value for s in incoming], ['+15550100'])
        self.assertFalse(hasattr(report, 'radios_withheld'))

    def test_clean_changes_only_control_characters_and_length(self):
        reader_ = radios.RadioReader(reader.Report(reader.Source('memory', '')), reader.Section('service', 'x', 1))
        clean = reader_.clean
        for printed in ('iccid=89990000000000000011 slot=1', 'imsi: 001010000000001 x', 'call from +1 555 0100 ended',
                        'number=15550100', 'ptr=0000000000000000', 'A000000809434343444B467631', 'iccid=null'):
            self.assertEqual(clean(printed), printed)

    def test_subscriptions_in_both_layouts_with_identifiers_as_printed(self):
        new = rows_of(scan_text(fixture.build_report('a16')), 'sim_subscriptions')
        self.assertEqual([(s.list_name, s.sub_id, s.slot_index, s.carrier_id, s.display_name, s.carrier_name, s.mcc, s.mnc,
                           s.country_iso, s.data_roaming, s.sub_type, s.embedded) for s in new],
                         [('active', 1, 0, '9001', 'Example Cell', 'Example Cell', '001', '01', 'xx', '0', 'LOCAL_SIM', '0'),
                          ('all', 1, 0, '9001', 'Example Cell', 'Example Cell', '001', '01', 'xx', '0', 'LOCAL_SIM', '0'),
                          ('all', 2, -1, '9002', 'Other Cell', 'No service', '001', '02', 'xx', '1', 'LOCAL_SIM', '0')])
        old = rows_of(scan_text(fixture.build_report('a10')), 'sim_subscriptions')
        self.assertEqual([(s.list_name, s.sub_id, s.slot_index, s.display_name, s.mcc, s.mnc, s.country_iso, s.embedded)
                          for s in old],
                         [('active', 1, 0, 'Example Cell', '001', '01', 'xx', 'false'),
                          ('all', 1, 0, 'Example Cell', '001', '01', 'xx', 'false'),
                          ('all', 2, -1, 'Other Cell', '001', '02', 'xx', 'false')])
        state = {s.item: s.value for s in rows_of(scan_text(fixture.build_report('a16')), 'telephony_state') if s.service == 'isub'}
        self.assertEqual((state['mSimState[0]'], state['mSimState[1]'], state['Logical SIM slot 0']), ('LOADED', 'NOT_READY', 'subId=1'))
        self.assertNotIn('slot 0', state)
        self.assertEqual([(s.iccid, s.imsi, s.phone_number, s.card_string, s.number_from_carrier) for s in new],
                         [('89990000000000000011[****]', '001010000000001[****]', '[****]', '89990000000000000011[****]', ''),
                          ('89990000000000000011[****]', '001010000000001[****]', '[****]', '89990000000000000011[****]', ''),
                          ('89990000000000000022[****]', '001020000000002[****]', '', '89990000000000000022[****]', '')])
        self.assertEqual([(s.iccid, s.imsi, s.phone_number, s.card_string) for s in old],
                         [('89990000000000000011', '', '+15550101', '89990000000000000011'),
                          ('89990000000000000011', '', '+15550101', '89990000000000000011'),
                          ('89990000000000000022', '', '', '89990000000000000022')])

    def test_carrier_config_values_and_default_block(self):
        report = scan_text(fixture.build_report('a16'))
        values = rows_of(report, 'carrier_values')
        applied = [(v.phone, v.source, v.key, v.value) for v in values if v.source == 'mConfigFromDefaultApp']
        self.assertEqual(applied, [('0', 'mConfigFromDefaultApp', 'carrier_name_string', 'Example Cell'),
                                   ('0', 'mConfigFromDefaultApp', 'carrier_volte_available_bool', 'true'),
                                   ('0', 'mConfigFromDefaultApp', 'example_array_int_array', '[-110, -90]'),
                                   ('0', 'mConfigFromDefaultApp', 'example_number_string', '+15550102')])
        self.assertEqual([(v.phone, v.key) for v in values if v.source == 'mNoSimConfig'], [('1', 'example_nosim_bool')])
        self.assertFalse([v for v in values if v.key.startswith('example_default_key')])
        self.assertEqual(dict(report.carrier_default_counts), {'0': 6, '1': 6})
        cached = [v for v in values if v.source == 'Cached config files']
        self.assertEqual([v.key for v in cached], ['carrierconfig-com.example.carrier-nosim.xml',
                                                   'carrierconfig-com.example.carrier-89990000000000000011-9001-00101-FF.xml'])
        self.assertEqual(cached[0].value, 'modified time=2026-09-02 19:10:46')

    def test_logs_records_and_headings(self):
        report = scan_text(fixture.build_report('a15'))
        logs = rows_of(report, 'telephony_logs')
        self.assertEqual({log.service for log in logs}, {'phone', 'telephony.registry', 'telecom', 'carrier_config', 'isms'})
        registry = [log for log in logs if log.service == 'telephony.registry']
        self.assertEqual([log.heading for log in registry], ['local logs:'] * 3 + ['listen logs:'])
        self.assertEqual(registry[0].time_text, '2026-11-02T06:05:40.308756')
        records = rows_of(report, 'state_records')
        self.assertEqual([(r.machine, r.position, r.processed, r.destination, r.what) for r in records[:3]],
                         [('GsmInboundSmsHandler', 0, 'StartupState', 'IdleState', 'EVENT_START_ACCEPTING_SMS'),
                          ('GsmInboundSmsHandler', 1, 'IdleState', 'DeliveringState', 'EVENT_NEW_SMS'),
                          ('GsmInboundSmsHandler', 2, 'DeliveringState', 'IdleState', 'EVENT_RETURN_TO_IDLE')])
        self.assertEqual(records[3].machine, 'CellBroadcastHandler')

    def test_phone_accounts(self):
        accounts = rows_of(scan_text(fixture.build_report('a15')), 'telecom_accounts')
        self.assertEqual([(a.enabled, a.package, a.account_id, a.user, a.schemes, a.restrictions) for a in accounts],
                         [('X', 'com.example.phone', '1', '0', 'tel voicemail', '[NONE]'),
                          (' ', 'com.example.chat', '***', '11', 'tel', '')])
        self.assertEqual(accounts[0].capabilities, 'CallProvider MultiUser PlaceEmerg SimSub')
        self.assertEqual(accounts[0].audio_routes, 'BESW')
        self.assertNotIn('GroupId', accounts[0].extras)
        self.assertEqual(rows_of(scan_text(fixture.build_report('a16')), 'telecom_accounts'), [])      # calls are not read

    def test_radio_log_keeps_only_the_state_tags(self):
        report = scan_text(fixture.build_report('a16'))
        lines = rows_of(report, 'radio_log')
        self.assertEqual([line.tag for line in lines], ['NetworkTypeController', 'DNC-0', 'SST', 'DefaultPhoneNotifier', 'SST'])
        self.assertEqual(report.radio_log_counts, [9, 5])
        self.assertEqual(lines[0].time_text, '11-02 06:05:47.082')
        self.assertEqual((lines[0].uid, lines[0].pid, lines[0].tid, lines[0].level), ('radio', '2529', '2529', 'D'))
        self.assertIn('imsi=001010000000001 number=+15550101 iccid=89990000000000000011', lines[4].message)
        self.assertFalse([line for line in lines if 'SEND_SMS' in line.message or 'AT+' in line.message])


class BoundTests(unittest.TestCase):
    def test_a_table_is_bounded_and_says_so(self):
        body = ''.join('2026-11-02 11:57:%02d.000:  reader_mode_change { x }\n' % number for number in range(10))
        text = section_text(service('nfc', 'mState=on\n' + body))
        with mock.patch.object(radios, 'MAX_SECTION_ROWS', 4):
            report = scan_text(text)
        self.assertEqual(len(rows_of(report, 'nfc_events')), 4)
        self.assertTrue([w for w in report.warnings if 'nfc_events' in w and 'not kept' in w])

    def test_deep_nesting_is_bounded(self):
        levels = radios.MAX_DEPTH + 40
        lines = ['USB MANAGER STATE (dumpsys usb):', '{', '  device_manager={', '    handler={', '      kernel_state=ok']
        lines += ['  x%d={' % number for number in range(levels)] + ['  deep=1'] + ['  }'] * levels
        lines += ['      after=x', '    }', '  }', '}']
        rows = rows_of(scan_text(section_text(service('usb', chr(10).join(lines)))), 'usb_state')
        self.assertEqual([(row.path, row.value) for row in rows],
                         [('device_manager.handler.kernel_state', 'ok'), ('device_manager.handler.after', 'x')])

    def test_long_lines_are_cut(self):
        text = section_text(service('nfc', 'mState=on\n2026-11-02 11:57:00.000:  big ' + 'x' * 50000 + '\n'))
        event = rows_of(scan_text(text), 'nfc_events')[0]
        self.assertLessEqual(len(event.detail), radios.MAX_VALUE)

    def test_damaged_lines_do_not_stop_the_pass(self):
        damaged = fixture.build_report('a16').replace('mState=on', 'mState=on\x00\x0c\r').replace(
            'XX:XX:XX:XX:BB:11', 'XX:XX:XX\xff\xfe').encode('utf-8').replace(b'Example Pay', b'Example \xff Pay')
        report = scan_text(damaged)
        self.assertTrue(rows_of(report, 'nfc_services'))
        self.assertEqual([d.name for d in rows_of(report, 'bt_devices')], ['Example Speaker'])


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def stage(self, name, text):
        path = Path(self.work) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode('utf-8') if isinstance(text, str) else text)
        return path

    def run_artifact(self, function, *paths):
        return function.__wrapped__(Context(self.work, paths))

    FUNCTIONS = tuple(getattr(artifacts, name) for name in dir(artifacts) if name.startswith('bugreport_'))

    def test_there_are_seventeen_artifacts_and_the_info_block_names_them(self):
        self.assertEqual(len(self.FUNCTIONS), 17)
        self.assertEqual(sorted(artifacts.__artifacts_v2__), sorted(function.__name__ for function in self.FUNCTIONS))
        for info in artifacts.__artifacts_v2__.values():
            self.assertTrue(info['category'].startswith('Android Bug Report - '))
            self.assertEqual(info['paths'], ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'))

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a15'))
        path16 = self.stage('Dump16/dumpstate.txt', fixture.build_report('a16'))
        for function in self.FUNCTIONS:
            headers, rows, source_path = self.run_artifact(function, path, path16)
            self.assertTrue(rows, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
            self.assertEqual(set(source_path.split('\n')), {str(path), str(path16)})

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        empty = self.stage('Dump2/dumpstate.txt', base.BANNER.format(report=fixture.REPORT))
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path, empty)
            self.assertEqual(rows, [], function.__name__)
            self.assertTrue(headers)

    def test_a_missing_section_is_said_once(self):
        empty = self.stage('Dump/dumpstate.txt', base.BANNER.format(report=fixture.REPORT))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_nfc_events, empty)
            self.run_artifact(artifacts.bugreport_nfc_state, empty)
        self.assertEqual(len([m for m in messages if 'no nfc section in this report' in m]), 1)

    def test_times_are_converted_with_the_report_zone(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a15', zone='Asia/Kolkata'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_nfc_events, path)
        self.assertEqual(rows[0][0], utc(2026, 10, 1, 8, 4, 58, 998000))
        self.assertEqual(rows[0][1], '2026-10-01 13:34:58.998')
        _h, rows, _s = self.run_artifact(artifacts.bugreport_bluetooth_events, path)
        first = rows[0]
        self.assertEqual((first[0], first[1], first[2]), (utc(2026, 11, 2, 0, 35, 38, 7000), '11-02 06:05:38.007', 'Enable log'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_telephony_logs, path)
        registry = [row for row in rows if row[2] == 'telephony.registry']
        self.assertEqual(registry[0][0], utc(2026, 11, 2, 0, 35, 40, 308756))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_usb_state, path)
        event = [row for row in rows if row[2]][0]
        self.assertEqual((event[2], event[3]), ('11-02 06:05:38:034', utc(2026, 11, 2, 0, 35, 38, 34000)))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_telephony_state_records, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 2, 0, 35, 37, 133000))

    def test_no_zone_gives_no_utc_and_says_why(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a15', zone=''))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_nfc_events, path)
        self.assertIsNone(rows[0][0])
        self.assertEqual(rows[0][4], reader.NOTE_NO_ZONE)
        _h, rows, _s = self.run_artifact(artifacts.bugreport_usb_log, self.stage('Dump2/dumpstate.txt', fixture.build_report('a16', zone='')))
        stamped = [row for row in rows if row[2]]
        self.assertTrue(all(row[3] is None and row[8] for row in stamped))

    def test_a_kernel_log_time_before_the_device_start_gets_no_utc(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='UTC'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_usb_log, path)
        by_kernel = {row[1]: row for row in rows}
        early = by_kernel['4.796833']                      # stamped 03-03: months before the device start (1 day 2 hours before the report)
        self.assertEqual((early[2], early[3]), ('03-03 00:34:20', None))
        self.assertEqual(early[8], artifacts.NOTE_CLOCK_NOT_SET)
        later = by_kernel['1866.503644']                   # 11-01 20:38:23, after the start (2026-11-01 08:12:30)
        self.assertEqual((later[3], later[8]), (utc(2026, 11, 1, 20, 38, 23), ''))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_nfc_driver_log, path)
        self.assertEqual([row[4] for row in rows if row[2]], ['', ''])
        self.assertEqual(artifacts._boot_wall(scan_text(fixture.build_report('a16'))), datetime(2026, 11, 1, 8, 12, 30))
        self.assertIsNone(artifacts._boot_wall(scan_text(section_text())))

    def test_hce_f_entries_are_read_like_the_others(self):
        text = section_text(service('nfc', '''mState=on
Registered HCE services for current user:

Registered HCE-F services for current user:
    ComponentInfo{com.example.fservice/com.example.fservice.F} (Description: Example F) (UID: 10500)
    Off-host Service
    Static AID groups:
    Dynamic AID groups:
    Settings Activity: null
'''))
        services = rows_of(scan_text(text), 'nfc_services')
        self.assertEqual([(s.service_list, s.package, s.uid, s.host, s.aid) for s in services],
                         [('HCE-F services', 'com.example.fservice', '10500', 'Off-host Service', '')])

    def test_a_year_less_time_needs_the_report_time(self):
        text = fixture.build_report('a15').replace('== dumpstate: ' + fixture.REPORT, '== dumpstate: garbage')
        path = self.stage('Dump/dumpstate.txt', text)
        _h, rows, _s = self.run_artifact(artifacts.bugreport_bluetooth_events, path)
        self.assertTrue(rows)
        self.assertTrue(all(row[0] is None and 'no report time' in row[6] for row in rows))

    def test_a_cut_dump_is_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_bluetooth_devices, path)
            self.run_artifact(artifacts.bugreport_bluetooth_events, path)
            self.run_artifact(artifacts.bugreport_nfc_services, path)
            self.run_artifact(artifacts.bugreport_usb_log, path)
        text = '\n'.join(messages)
        self.assertEqual(len([m for m in messages if 'bluetooth_manager service dump was cut by a 500 ms timeout' in m]), 1)
        self.assertEqual(len([m for m in messages if 'nfc service dump was cut by a 10000 ms timeout' in m]), 1)
        self.assertIn('USB LOG section has no duration line', text)

    def test_nothing_is_withheld_and_the_log_does_not_say_so(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a15'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_telephony_state, path)
        self.assertFalse([m for m in messages if 'withheld' in m])

    def test_radio_log_count_is_logged(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_radio_state_log, path)
        self.assertTrue([m for m in messages if '5 of 9 lines of the RADIO LOG section are listed' in m])

    def test_the_carrier_default_block_is_logged(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_carrier_config, path)
        self.assertEqual(len([m for m in messages if 'default values block of the carrier_config dump' in m]), 2)

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10'))
        alone = len(self.run_artifact(artifacts.bugreport_bluetooth_devices, first)[1])
        both = self.run_artifact(artifacts.bugreport_bluetooth_devices, first, second)[1]
        self.assertEqual(len(both), alone + 2)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})

    def test_the_section_index_names_the_new_artifacts(self):
        report = scan_text(fixture.build_report('a15'))
        names = {section.name: reader.READ_BY.get((section.kind, section.name), 'not read') for section in report.sections}
        self.assertIn('Bluetooth Devices', names['bluetooth_manager'])
        self.assertIn('USB Manager State', names['usb'])
        self.assertIn('Telephony State Machine Records', names['isms'])
        self.assertEqual(names['RADIO LOG'], 'Radio Log State Lines')
        self.assertEqual(names['SYSTEM PROPERTIES'], 'Device Facts; Device Identifiers; Boot Reasons')       # the shared entries are kept


if __name__ == '__main__':
    unittest.main()
