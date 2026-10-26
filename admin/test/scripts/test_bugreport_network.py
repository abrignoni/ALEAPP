"""Android bug report text: Wi-Fi, network usage, network policy, connectivity, DNS, interfaces, sockets and tethering."""
# pylint: disable=protected-access,unbalanced-tuple-unpacking
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_fixture as base
from admin.test.scripts import bugreport_network_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts import dumpstate_network as network
from scripts.artifacts import bugreportNetwork as artifacts


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


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


def table(report, name):
    return getattr(report, 'net_' + name, [])


A16 = fixture.build_report('a16')
A10 = fixture.build_report('a10')


class RegistrationTests(unittest.TestCase):
    def test_readers_are_registered_once_for_their_sections(self):
        by_section = reader.readers_by_section()
        for cls in network.READERS:
            self.assertIn(cls, by_section[(cls.kind, cls.name)])
        self.assertEqual(len(network.READERS), len(set(network.READERS)))
        self.assertEqual(set(network.READ_BY), {(cls.kind, cls.name) for cls in network.READERS})
        for key in network.READ_BY:
            self.assertEqual(reader.READ_BY[key], network.READ_BY[key])

    def test_the_other_readers_are_still_there(self):
        self.assertIn(reader.SettingsReader, reader.READERS)


class WifiNetworkTests(unittest.TestCase):
    def test_android_16_entries(self):
        report = scan_text(A16)
        networks = table(report, 'wifi_networks')
        self.assertEqual([n.network_id for n in networks], [0, 1, 2])         # the ConfigurationMap copy and the stray ID: line are not read
        home, guest, cafe = networks
        self.assertEqual((home.prefix, home.ssid, home.currently_connected, home.user_selected, home.most_recent),
                         ('*', '"Example-Home"', 'true', 'true', 'true'))
        self.assertEqual((home.key_mgmt, home.protocols), ('WPA_PSK', 'WPA RSN'))        # the entry level line, not the security parameter sets
        self.assertEqual((home.creator_uid, home.creator_name, home.update_uid, home.update_name, home.connect_uid),
                         ('1000', 'android.uid.system:1000', '10100', 'com.example.settings', '10100'))
        self.assertEqual((home.mac_setting, home.random_mac, home.reboots), ('3', '02:00:5e:10:00:01', 0))
        self.assertEqual((guest.prefix, guest.selection_status, guest.disable_reason),
                         ('- DSBLE', 'NETWORK_SELECTION_PERMANENTLY_DISABLED', 'NETWORK_SELECTION_DISABLED_BY_WRONG_PASSWORD'))
        self.assertEqual(guest.reboots, 41)
        self.assertEqual((cafe.ssid, cafe.key_mgmt, cafe.prefix), ('"Example Cafe, Terrace"', 'SAE', ''))
        self.assertEqual(home.recent_failure, 'Association Rejection code: 0, last update time: 0')
        self.assertEqual((home.creation, home.update, home.associations), ('', '', ''))

    def test_android_10_entries_carry_times_and_a_connect_choice(self):
        report = scan_text(A10)
        home, office, hexed = table(report, 'wifi_networks')
        self.assertEqual((home.creation, home.update, home.associations), ('08-27 15:07:06.108', '10-30 06:39:02.605', 627))
        self.assertEqual((office.creation, office.update, office.pmf), ('09-08 21:14:58.080', '', 'true'))
        self.assertEqual(office.connect_choice, '"Example Home"WPA_PSK')
        self.assertEqual(hexed.ssid, 'ExampleHex0A')
        self.assertEqual((home.auto_join, home.currently_connected, home.reboots), ('true', '', ''))     # printed by other builds only

    def test_no_block_no_rows(self):
        text = fixture.build_report('a16').replace('Configured networks Begin', 'Configured networks Begun')
        self.assertEqual(table(scan_text(text), 'wifi_networks'), [])

    def test_an_entry_without_the_closing_line_is_kept(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE wifi:\n'
                'WifiConfigManager - Configured networks Begin ----\nID: 3 SSID: "x" PROVIDER-NAME: null BSSID: null FQDN: null PRIO: 0\n'
                ' numAssociation 4\n')
        networks = table(scan_text(text), 'wifi_networks')
        self.assertEqual([(n.network_id, n.associations) for n in networks], [(3, 4)])


class WifiStateTests(unittest.TestCase):
    def test_connection_events(self):
        report = scan_text(A16)
        first, second = table(report, 'wifi_connections')
        self.assertEqual((first.start, first.ssid, first.bssid, first.duration, first.result, first.rssi),
                         ('11-01 6:5:39.713', '"Example-Home"', '02:00:5e:30:00:01', '1623', '1', '-73'))
        self.assertEqual((first.network_type, first.nominator, first.creator, first.channel),
                         ('TYPE_WPA2', 'NOMINATOR_SAVED', 'CREATOR_USER', '2412'))
        self.assertIn('mRouterFingerprint=mConnectionEvent.roamType=0', first.other)
        self.assertIn('uid=1010', first.other)
        self.assertEqual((second.ssid, second.start, second.l2_failure, second.result), ('"Example Cafe, Terrace"', '11-01 21:5:48.45',
                                                                                         'ASSOCIATION_REJECTION', '3'))
        self.assertEqual(second.network_type, '')

    def test_current_state_one_row_for_each_wifi_info_line(self):
        report = scan_text(A16)
        connected, idle = table(report, 'wifi_state')
        self.assertEqual((connected.power, connected.mode, connected.ssid, connected.rssi, connected.frequency),
                         ('Wi-Fi is enabled', 'EnabledState', '"Example-Home"', '-61', '2437MHz'))
        self.assertEqual(connected.last_bssid, '02:00:5e:30:00:01')
        self.assertIn('InterfaceName: wlan0', connected.link_properties)       # printed before its mWifiInfo line
        self.assertEqual((idle.ssid, idle.supplicant, idle.last_bssid, idle.link_properties), ('<unknown ssid>', 'DISCONNECTED', 'null', ''))
        self.assertIn('Max Supported Tx Link speed: 150Mbps', connected.other)

    def test_current_state_without_a_wifi_info_line(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE wifi:\n'
                'Wi-Fi is disabled\nCurrent wifi mode: EnabledState\n')
        rows = table(scan_text(text), 'wifi_state')
        self.assertEqual([(r.power, r.mode, r.ssid) for r in rows], [('Wi-Fi is disabled', 'EnabledState', '')])
        self.assertEqual(table(scan_text(text.replace('Wi-Fi is disabled\nCurrent wifi mode: EnabledState\n', 'nothing\n')), 'wifi_state'), [])

    def test_state_machine_records_and_logs(self):
        report = scan_text(A16)
        records = table(report, 'wifi_records')
        self.assertEqual([r.service for r in records], ['wifi', 'wifi', 'wifiscanner', 'wifiscanner', 'wifiscanner', 'wifip2p', 'wifip2p'])
        self.assertEqual((records[0].machine, records[0].number, records[0].time_text, records[0].processed, records[0].origin,
                          records[0].destination), ('WifiController', 0, '11-01 21:05:10.120', 'DefaultState', 'EnabledState', '<null>'))
        self.assertIn('CMD_UPDATE_AP_CAPABILITY', records[0].what)
        self.assertEqual(records[2].machine, 'WifiPnoScanStateMachine')
        self.assertEqual(records[4].machine, 'WifiSingleScanStateMachine')
        self.assertIn('sender=com.example.share(10120)', records[5].what)
        logs = table(report, 'wifi_log')
        self.assertEqual([(l.service, l.log_name) for l in logs],
                         [('wifi', 'WifiDeviceStateChangeManager'), ('wifi', 'WifiDeviceStateChangeManager'),
                          ('wifi', 'WifiConnectivityManager'), ('wifi', 'WifiConnectivityManager'),
                          ('wifiscanner', 'WifiScanningService'), ('wifiscanner', 'WifiScanningService')])
        self.assertEqual(logs[0].message, 'mLastScreenOn: true:')              # a message that ends with a colon is a log line, not a heading
        self.assertNotIn('not a time-stamped line', ' '.join(l.message for l in logs))
        self.assertNotIn('outside any block', ' '.join(l.message for l in logs))

    def test_scan_results(self):
        report = scan_text(A16)
        rows = table(report, 'wifi_scan_results')
        self.assertEqual([r.table for r in rows], ['Latest scan results'] * 3 + ['Latest native scan results'])
        first, neighbor, empty, native = rows
        self.assertEqual((first.bssid, first.frequency, first.rssi, first.rssi_detail, first.age, first.ssid),
                         ('02:00:5e:30:00:01', 2437, -58, '(0:-61/1:-62)', '226.141', 'Example-Home'))
        self.assertEqual((neighbor.ssid, neighbor.age, neighbor.flags), ('Example Neighbor 5G', '>1000.0', '[RSN-SAE-CCMP-128][ESS][WPS]'))
        self.assertEqual((empty.ssid, empty.flags), ('', ''))
        self.assertEqual(native.rssi, -57)
        masked = table(scan_text(A10), 'wifi_scan_results')[0]
        self.assertEqual((masked.bssid, masked.ssid), ('02:00:**:**:b4:9d', 'ExHot11D8E522'))


class UsageTests(unittest.TestCase):
    def test_android_16_service_and_checkin_tables(self):
        report = scan_text(A16)
        buckets = table(report, 'usage_buckets')
        origins = [(b.origin, b.table) for b in buckets]
        self.assertEqual(origins.count(('DUMP OF SERVICE netstats', 'Xt stats')), 4)
        self.assertEqual(origins.count(('CHECKIN NETSTATS', 'Xt stats')), 4)
        self.assertEqual(origins.count(('CHECKIN NETSTATS', 'UID stats')), 4)
        uid = [b for b in buckets if b.table == 'UID stats']
        self.assertEqual([(b.uid, b.net_set, b.bucket_seconds) for b in uid],
                         [(10300, 'DEFAULT', 7200), (10300, 'DEFAULT', 7200), (10300, 'FOREGROUND', 7200), (1010300, 'DEFAULT', 7200)])
        first = [b for b in buckets if b.table == 'Xt stats'][0]
        self.assertEqual((first.rx_bytes, first.rx_packets, first.tx_bytes, first.tx_packets, first.operations, first.tag),
                         (3200614, 15100, 9886381, 13967, 0, '0x0'))
        self.assertIn('wifiNetworkKey="Example-Home"wpa2-psk', first.identity)
        self.assertEqual(first.start, base.epoch_s('2026-11-01 20:00:00'))
        self.assertEqual([b.uid for b in buckets if b.table == 'Xt stats'], [-1] * 8)

    def test_android_10_checkin_form_and_second_counter_set(self):
        report = scan_text(A10)
        buckets = table(report, 'usage_buckets')
        checkin = [b for b in buckets if b.origin == 'CHECKIN NETSTATS']
        self.assertEqual([(b.table, b.identity, b.net_set, b.tag, b.bucket_seconds) for b in checkin],
                         [('checkin xt', 'cell', 'all', '0', 3600)] * 2 + [('checkin xt', 'wifi', 'all', '0', 3600)])
        self.assertEqual((checkin[0].rx_bytes, checkin[0].rx_packets, checkin[0].tx_bytes, checkin[0].tx_packets, checkin[0].operations),
                         (5103817, 5709, 1546414, 4346, 0))
        service = [b for b in buckets if b.origin.startswith('DUMP')]
        self.assertEqual([b.table for b in service], ['Dev stats', 'Xt stats'])
        self.assertEqual(service[0].extra, 'rb=0 rp=0 tb=0 tp=0')              # the second set is kept as printed
        self.assertEqual(service[0].bucket_seconds, 3600)                       # on the line after proc= and actUid=

    def test_a_checkin_line_before_any_group_is_ignored(self):
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ CHECKIN NETSTATS (/system/bin/dumpsys netstats --checkin) ------\n'
                'b,1790000000,1,2,3,4,5\nv1,1,2\nxt\nc,cell,-1,all,0\nb,1790000000,1,2,3,4,5\nb,1790003600,1,2,3,4\nb,x,1,2,3,4,5\n')
        buckets = table(scan_text(text), 'usage_buckets')
        self.assertEqual(len(buckets), 1)
        self.assertEqual((buckets[0].start, buckets[0].bucket_seconds), (1790000000, None))


class PolicyTests(unittest.TestCase):
    def test_uid_entries(self):
        report = scan_text(A16)
        entries = [(e.group, e.uid, e.value) for e in table(report, 'policy_uids')]
        self.assertEqual(entries[0], ('Policy for UIDs', 1000, 'policy=4 (ALLOW_METERED_BACKGROUND)'))
        self.assertIn(('Default restrict background allowlist uids', 10300, ''), entries)
        self.assertIn(('Uids transitioning to background', 10300, '+3s400ms'), entries)
        status = [e for e in entries if e[0] == 'Status for all known UIDs']
        self.assertEqual([e[1] for e in status], [-1, 10300])                     # the callback_info continuation line is not a row
        self.assertIn('procState=TOP', status[1][2])

    def test_android_10_uid_entries(self):
        entries = [(e.group, e.uid, e.value) for e in table(scan_text(A10), 'policy_uids')]
        self.assertIn(('Status for all known UIDs', 10300, 'state=2 (fg) rules=0 (NONE)'), entries)
        self.assertIn(('Status for just UIDs with rules', 10120, 'rules=1 (REJECT_ALL)'), entries)
        self.assertIn(('Default restrict background whitelist uids', 10300, ''), entries)

    def test_settings_lines(self):
        settings = [(s.group, s.name, s.value) for s in table(scan_text(A16), 'policy_settings')]
        self.assertIn(('', 'System ready', 'true'), settings)
        self.assertIn(('', 'mRestrictBackgroundLowPowerMode', 'false'), settings)
        self.assertIn(('', 'com.example.net.use_metered_firewall_chains', 'true'), settings)
        self.assertIn(('Active subscriptions', '', '1=999990...'), settings)
        self.assertIn(('Network to interfaces', '', '101: {wlan0}'), settings)
        self.assertTrue(any(group == 'Network policies' and 'matchRule=CARRIER' in value for group, _name, value in settings))
        self.assertFalse([s for s in settings if 'Client PIDs' in s[1] or 'Service host' in s[1]])
        self.assertFalse([s for s in settings if s[2].startswith('UID=')])

    def test_event_logs_keep_the_printed_time(self):
        events = table(scan_text(A16), 'policy_events')
        self.assertEqual([(e.log, e.time_text) for e in events],
                         [('mEventLogs', '2026-11-01T21:06:17:657'), ('mEventLogs', '2026-11-01T21:05:17:165'),
                          ('mEventLogs', '1970-01-01T00:00:00:000'), ('mNetworkBlockedLogs', '2026-11-01T21:06:18:679'),
                          ('mUidStateChangeLogs', '2026-11-01T21:02:53:415')])
        self.assertEqual(events[0].message, 'Firewall rule changed: 10246-powersave-allow')


class ConnectivityTests(unittest.TestCase):
    def test_android_16_networks(self):
        wifi, cell = table(scan_text(A16), 'connectivity_networks')
        self.assertEqual((wifi.network_id, wifi.default, wifi.info, wifi.created, wifi.interface),
                         (101, 'true', 'WIFI CONNECTED extra: ', '2026-11-01T20:40:10.404Z', 'wlan0'))
        self.assertEqual((wifi.addresses.strip(), wifi.dns.strip(), wifi.domains, wifi.transports, wifi.signal, wifi.ssid),
                         ('fe80::ff:fe00:1/64,192.0.2.15/24', '/192.0.2.1', 'null', 'WIFI', '-64', '"Example-Home"'))
        self.assertIn('0.0.0.0/0 -> 192.0.2.1 wlan0 mtu 0', wifi.routes)
        self.assertIn('NOT_METERED&INTERNET', wifi.capabilities)
        self.assertIn('TRANSPORT_PRIMARY', wifi.score)
        self.assertEqual((cell.default, cell.transports, cell.domains, cell.interface), ('false', 'CELLULAR', 'example.test', 'rmnet0'))

    def test_android_10_network_has_no_link_properties(self):
        network_row, = table(scan_text(A10), 'connectivity_networks')
        self.assertEqual((network_row.network_id, network_row.default, network_row.interface, network_row.created, network_row.ssid,
                          network_row.score), (100, 'true', '', '', '*****', '60'))
        self.assertTrue(network_row.info.startswith('[type: WIFI[]'))

    def test_requests_are_not_networks(self):
        self.assertEqual(len(table(scan_text(A16), 'connectivity_networks')), 2)


class InterfaceTests(unittest.TestCase):
    def test_ip_s_link(self):
        rows = table(scan_text(A16), 'interfaces')
        self.assertEqual([r.name for r in rows], ['lo', 'wlan0', 'ip_vti0'])
        wlan = rows[1]
        self.assertEqual((wlan.index, wlan.flags, wlan.mtu, wlan.qdisc, wlan.state, wlan.mode, wlan.qlen, wlan.link_type, wlan.link_address),
                         (2, 'BROADCAST,MULTICAST,UP,LOWER_UP', 1500, 'mq', 'UP', 'DORMANT', '3000', 'ether', '02:00:5e:10:00:01'))
        self.assertEqual((wlan.rx_bytes, wlan.rx_packets, wlan.rx_mcast, wlan.tx_bytes, wlan.tx_dropped), (84368415, 14685, 12, 1641480, 3))
        self.assertEqual(rows[2].linked, 'NONE')
        self.assertEqual((rows[2].link_type, rows[2].link_address, rows[2].rx_bytes), ('ipip', '0.0.0.0', 0))

    def test_plain_ip_link_has_no_counters(self):
        rows = table(scan_text(A10), 'interfaces')
        self.assertEqual([r.rx_bytes for r in rows], ['', '', ''])
        self.assertEqual(rows[1].state, 'UP')

    def test_dev_counters(self):
        rows = table(scan_text(A16), 'interface_counters')
        self.assertEqual([r.name for r in rows], ['lo', 'wlan0', 'rmnet0'])
        self.assertEqual((rows[1].rx_bytes, rows[1].rx_packets, rows[1].tx_bytes, rows[1].tx_packets, rows[1].tx_drop),
                         (84368415, 14685, 1641480, 5516, 3))
        self.assertEqual(rows[2].tx_bytes, 280)

    def test_a_damaged_counter_line_is_skipped(self):
        text = A16.replace(' wlan0: 84368415   14685', ' wlan0: 84368415   x')
        self.assertEqual([r.name for r in table(scan_text(text), 'interface_counters')], ['lo', 'rmnet0'])


class DnsTests(unittest.TestCase):
    def test_servers_and_private_dns_log(self):
        report = scan_text(A16)
        servers = table(report, 'dns_servers')
        self.assertEqual([(s.net_id, s.server) for s in servers], [(101, '192.0.2.1'), (101, '2001:db8::53%wlan0'), (102, '198.51.100.1')])
        first = servers[0]
        self.assertEqual((first.total, first.successes, first.errors, first.timeouts, first.internal_errors, first.rtt_ms, first.last_sample),
                         (64, 62, 0, 2, 0, 53, 43))
        self.assertEqual((first.interfaces, first.search_domains, first.private_mode, first.transport, first.metered),
                         ('[wlan0]', 'none defined', 'OPPORTUNISTIC', 'WIFI', 'false'))
        self.assertEqual(servers[1].rtt_ms, -1)
        self.assertEqual((servers[2].search_domains, servers[2].private_mode, servers[2].transport, servers[2].metered),
                         ('example.test', 'OFF', 'CELLULAR', 'true'))
        log = table(report, 'private_dns')
        self.assertEqual([(l.time_text, l.net_id, l.server, l.state) for l in log],
                         [('03:06:25.779', 100, '192.0.2.1:853/', 'in_process'), ('03:06:26.365', 101, '192.0.2.1:853/', 'fail')])

    def test_android_10_has_no_log_and_no_transport(self):
        report = scan_text(A10)
        self.assertEqual(table(report, 'private_dns'), [])
        servers = table(report, 'dns_servers')
        self.assertEqual(len(servers), 2)
        self.assertEqual((servers[0].transport, servers[0].interfaces), ('', ''))


class SocketTests(unittest.TestCase):
    def test_android_16_internet_table(self):
        rows = table(scan_text(A16), 'inet_sockets')
        self.assertEqual([r.protocol for r in rows], ['tcp', 'tcp', 'tcp', 'udp', 'udp', 'tcp6', 'raw6'])
        first, closing, half, udp, udp_plain, tcp6, raw = rows
        self.assertEqual((first.local, first.foreign, first.state, first.uid, first.inode, first.program),
                         ('192.0.2.15:42676', '203.0.113.4:443', 'ESTABLISHED', 86664, 67153498, '-'))
        self.assertEqual((closing.recv_q, closing.state), (130, 'CLOSE_WAIT'))
        self.assertEqual((half.send_q, half.uid, half.inode), (1, 0, 0))
        self.assertEqual((udp.recv_q, udp.uid), (4352, 1073))
        self.assertEqual((udp_plain.state, udp_plain.uid, udp_plain.inode), ('', 86664, 67198007))     # a udp line prints no state
        self.assertEqual(tcp6.local, '[2001:db8::1]:41000')
        self.assertEqual((raw.state, raw.uid, raw.inode), ('7', 1000, 67224811))                      # a raw socket prints a number there

    def test_android_10_table_has_no_user_columns(self):
        rows = table(scan_text(A10), 'inet_sockets')
        self.assertEqual([(r.protocol, r.state, r.uid, r.inode, r.program) for r in rows],
                         [('tcp', 'CLOSE_WAIT', None, None, ''), ('tcp6', 'ESTABLISHED', None, None, ''),
                          ('udp', 'ESTABLISHED', None, None, ''), ('raw6', '7', None, None, '')])

    def test_unix_table(self):
        rows = table(scan_text(A16), 'unix_sockets')
        self.assertEqual([(r.ref_count, r.flags, r.socket_type, r.state, r.inode, r.program, r.path) for r in rows],
                         [(2, '[ ]', 'DGRAM', 'CONNECTED', 67485743, '-', ''),
                          (2, '[ ACC ]', 'STREAM', 'LISTENING', 67293694, '-', '/dev/socket/example'),
                          (3, '[ ]', 'SEQPACKET', 'CONNECTED', 67222009, '1234/example_daemon', '/dev/socket/example name')])
        old = table(scan_text(A10), 'unix_sockets')
        self.assertEqual([(r.ref_count, r.state, r.program, r.path) for r in old],
                         [(76, '', '', '/dev/socket/example'), (2, 'CONNECTED', '', '/dev/socket/example2')])

    def test_socket_state_table(self):
        rows = table(scan_text(A16), 'socket_state')
        self.assertEqual([(r.netid, r.state) for r in rows], [('udp', 'ESTAB'), ('tcp', 'ESTAB'), ('tcp', 'LISTEN'), ('tcp', 'ESTAB')])
        udp, tcp, listen, bare = rows
        self.assertEqual((udp.local, udp.peer, udp.uid, udp.inode, udp.socket), ('192.0.2.15%wlan0:68', '192.0.2.1:67', 1073, 67804605, '81aeed'))
        self.assertEqual((tcp.timer, tcp.uid), ('timer:(keepalive,7.2sec,0)', 86664))
        self.assertIn('rtt:79.908/34.454', tcp.info)                                  # both continuation lines are joined
        self.assertIn('segs_out:17', tcp.info)
        self.assertEqual((listen.users, listen.send_q, listen.local), ('users:(("example",pid=1234,fd=7))', 4, '*:8080'))
        self.assertEqual((bare.uid, bare.inode, bare.info), (None, None, ''))


class TetheringTests(unittest.TestCase):
    def test_log_and_state(self):
        report = scan_text(A16)
        log = table(report, 'tethering_log')
        self.assertEqual([(l.time_text, l.message) for l in log],
                         [('2026-11-01T21:05:34.472718', 'MARK Tethering.constructed'),
                          ('2026-11-01T21:05:36.767088', 'OBSERVED configuration changed'),
                          ('2026-11-01T21:05:38.044112', 'USB bcast connected:false configured:false rndis:false ncm:false')])
        state = [(s.group, s.name, s.value) for s in table(report, 'tethering_state')]
        self.assertIn(('Tethering', 'Callbacks registered', '24'), state)
        self.assertIn(('Configuration', 'activeDataSubId', '2'), state)
        self.assertIn(('Tether state', 'Current upstream interface(s)', 'null'), state)
        self.assertIn(('Hardware offload', '', '<empty>'), state)
        self.assertFalse([s for s in state if 'Tethering.constructed' in s[2]])        # the log lines are not state lines

    def test_android_10_has_no_tethering(self):
        report = scan_text(A10)
        self.assertEqual((table(report, 'tethering_log'), table(report, 'tethering_state')), ([], []))


class BoundTests(unittest.TestCase):
    def test_long_values_are_cut(self):
        text = A16.replace('"Example-Home"wpa2-psk', 'x' * 5000, 1).replace('Example Neighbor 5G', 'n' * 900, 1)
        report = scan_text(text)
        self.assertLessEqual(len(table(report, 'usage_buckets')[0].identity), network.MAX_ID_TEXT)
        self.assertLessEqual(max(len(r.ssid) for r in table(report, 'wifi_scan_results')), 100)

    def test_row_cap_is_reported(self):
        with mock.patch.object(reader, 'MAX_ROWS', 2):
            report = scan_text(A16)
        self.assertEqual(len(table(report, 'wifi_networks')), 2)
        self.assertTrue([w for w in report.warnings if 'net_wifi_networks' in w])

    def test_control_characters_are_shown_as_spaces(self):
        text = A16.replace('Example Guest', 'Example\x00\x0c\rGuest', 1)
        ssids = [n.ssid for n in table(scan_text(text), 'wifi_networks')]
        self.assertIn('"Example   Guest"', ssids)


class TimeTests(unittest.TestCase):
    def setUp(self):
        self.report = scan_text(fixture.build_report('a16', zone='Europe/Paris'))

    def test_month_day_without_a_year(self):
        moment, note = artifacts._month_day(self.report, '10-30 06:39:02.605')
        self.assertEqual((moment, note), (utc(2026, 10, 30, 5, 39, 2, 605000), ''))
        self.assertEqual(artifacts._month_day(self.report, '12-31 23:00:00.000')[0], utc(2025, 12, 31, 22, 0))     # after the report: last year
        self.assertEqual(artifacts._month_day(self.report, '11-03 10:00:00.000')[0], utc(2026, 11, 3, 9, 0))     # within a day after it

    def test_unpadded_times_are_given_to_the_whole_second(self):
        moment, _note = artifacts._month_day(self.report, '11-01 6:5:48.45', whole_seconds=True)
        self.assertEqual(moment, utc(2026, 11, 1, 5, 5, 48))
        moment, _note = artifacts._month_day(self.report, '11-01 6:5:48.45')
        self.assertEqual(moment, utc(2026, 11, 1, 5, 5, 48))                        # a fraction that is not three digits is not used
        self.assertEqual(artifacts._month_day(self.report, '11-01 06:05:48.450')[0], utc(2026, 11, 1, 5, 5, 48, 450000))

    def test_month_day_edge_cases(self):
        self.assertEqual(artifacts._month_day(self.report, ''), (None, ''))
        self.assertEqual(artifacts._month_day(self.report, 'garbage')[0], None)
        self.assertEqual(artifacts._month_day(self.report, '02-29 12:00:00.000')[0], None)
        bare = scan_text(fixture.build_report('a16', with_banner=False))
        self.assertEqual(artifacts._month_day(bare, '10-30 06:39:02.605'), (None, artifacts.NOTE_NO_YEAR))
        nozone = scan_text(fixture.build_report('a16', zone=''))
        self.assertEqual(artifacts._month_day(nozone, '10-30 06:39:02.605'), (None, reader.NOTE_NO_ZONE))

    def test_iso_wall_times(self):
        self.assertEqual(artifacts._wall(self.report, '2026-11-01T21:05:09.500000'), (utc(2026, 11, 1, 20, 5, 9, 500000), ''))
        self.assertEqual(artifacts._wall(self.report, '1970-01-01T00:00:00.000'), (None, reader.NOTE_UNSET))
        self.assertEqual(artifacts._wall(self.report, '2008-12-31T23:59:59'), (None, artifacts.NOTE_BEFORE_2009))
        self.assertEqual(artifacts._wall(self.report, 'x'), (None, reader.NOTE_NOT_A_TIME))
        self.assertEqual(artifacts._wall(scan_text(fixture.build_report('a16', zone='')), '2026-11-01T21:05:09'),
                         (None, reader.NOTE_NO_ZONE))
        self.assertEqual(artifacts._wall(self.report, '2026-03-29T02:30:00'), (None, reader.NOTE_NONEXISTENT))   # clocks set forward in Paris

    def test_policy_times_have_a_colon_before_the_milliseconds(self):
        self.assertEqual(artifacts._policy_wall(self.report, '2026-11-01T21:06:17:657'), (utc(2026, 11, 1, 20, 6, 17, 657000), ''))
        self.assertEqual(artifacts._policy_wall(self.report, '1970-01-01T00:00:00:000'), (None, reader.NOTE_UNSET))

    def test_epoch_and_created_times(self):
        self.assertEqual(artifacts._epoch(base.epoch_s('2026-11-01 20:00:00')), utc(2026, 11, 1, 20, 0))
        self.assertIsNone(artifacts._epoch(1000))
        self.assertIsNone(artifacts._epoch(None))
        self.assertEqual(artifacts._printed_utc('2026-11-01T20:40:10.404Z'), utc(2026, 11, 1, 20, 40, 10, 404000))
        self.assertIsNone(artifacts._printed_utc('2026-11-01T20:40:10.404'))
        self.assertIsNone(artifacts._printed_utc(''))


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

    FUNCTIONS = tuple(getattr(artifacts, key) for key in artifacts.__artifacts_v2__)

    def test_every_artifact_has_a_function(self):
        self.assertEqual(len(self.FUNCTIONS), 20)
        self.assertEqual(len({function.__name__ for function in self.FUNCTIONS}), 20)

    def test_row_width_matches_the_headers(self):
        for layout in ('a16', 'a10'):
            path = self.stage('Dump/dumpstate-%s.txt' % layout, fixture.build_report(layout))
            for function in self.FUNCTIONS:
                headers, rows, source_path = self.run_artifact(function, path)
                self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
                self.assertEqual(source_path, str(path))
                if layout == 'a16' or function.__name__ not in ('bugreport_tethering_log', 'bugreport_tethering_state',
                                                                'bugreport_private_dns_log'):
                    self.assertTrue(rows, '%s %s' % (layout, function.__name__))
                self.assertEqual(headers[-1], 'Source File')

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)

    def test_a_text_without_these_sections_gives_no_rows(self):
        path = self.stage('Dump/dumpstate.txt', base.BANNER.format(report='2026-11-02 10:15:30'))
        for function in self.FUNCTIONS:
            self.assertEqual(self.run_artifact(function, path)[1], [])

    def test_saved_network_rows(self):
        path = self.stage('Dump/bugreport-a.txt', fixture.build_report('a10', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_saved_networks, path)

        def by_header(row, name):
            return row[headers_index(headers, name)]
        first = rows[0]
        self.assertEqual(by_header(first, 'Creation Time (UTC)'), utc(2026, 8, 27, 13, 7, 6, 108000))
        self.assertEqual(by_header(first, 'Creation Time As Printed'), '08-27 15:07:06.108')
        self.assertEqual(by_header(first, 'Update Time (UTC)'), utc(2026, 10, 30, 5, 39, 2, 605000))
        self.assertEqual(by_header(first, 'SSID (as printed)'), '"Example-Home"')
        self.assertEqual(by_header(first, 'Associations'), 627)
        self.assertIsNone(by_header(rows[1], 'Update Time (UTC)'))
        self.assertEqual(by_header(rows[1], 'Connect Choice'), '"Example Home"WPA_PSK')

    def test_connection_event_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_connection_events, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 5, 5, 39))
        self.assertEqual(rows[0][1], '11-01 6:5:39.713')
        self.assertEqual(rows[1][0], utc(2026, 11, 1, 20, 5, 48))
        self.assertEqual(len(headers), len(rows[0]))

    def test_usage_bucket_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_network_usage_buckets, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 20, 0))
        self.assertEqual(rows[0][1], base.epoch_s('2026-11-01 20:00:00'))
        odd = [row for row in rows if row[1] == 1000]
        self.assertEqual(len(odd), 2)                                               # an epoch outside 2009 to 2100 has no UTC
        self.assertTrue(all(row[0] is None for row in odd))
        self.assertEqual({row[14] for row in rows}, {'DUMP OF SERVICE netstats', 'CHECKIN NETSTATS'})

    def test_policy_event_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_netpolicy_events, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 20, 6, 17, 657000))
        self.assertEqual(rows[0][1], '2026-11-01T21:06:17:657')
        self.assertEqual((rows[2][0], rows[2][2]), (None, reader.NOTE_UNSET))

    def test_connected_network_rows(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_connected_networks, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 20, 40, 10, 404000))
        self.assertEqual(rows[0][1], '2026-11-01T20:40:10.404Z')

    def test_log_rows_in_the_report_zone(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Asia/Kolkata'))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_tethering_log, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 15, 35, 34, 472718))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_service_log, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 15, 35, 9, 500000))
        self.assertIsNone([row for row in rows if row[1].startswith('1970')][0][0])
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_state_records, path)
        self.assertEqual(rows[0][0], utc(2026, 11, 1, 15, 35, 10, 120000))

    def test_odd_bytes_do_not_stop_the_pass(self):
        path = self.stage('Dump/dumpstate.txt', fixture.cases()['synthetic_odd_bytes'][0][1])
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path)
            self.assertTrue(all(len(row) == len(headers) for row in rows))
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_saved_networks, path)
        self.assertIn('"Example  Guest"', [row[headers_index(_headers, 'SSID (as printed)')] for row in rows])
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_service_log, path)
        self.assertTrue(rows and all(row[0] is None for row in rows))               # no zone property in this text

    def test_a_dump_cut_by_the_platform_is_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            for function in (artifacts.bugreport_netpolicy_uid_entries, artifacts.bugreport_netpolicy_settings,
                             artifacts.bugreport_netpolicy_events):
                rows = self.run_artifact(function, path)[1]
                self.assertTrue(rows)
        cut = [message for message in messages if 'netpolicy service dump was cut by a 10000 ms timeout' in message]
        self.assertEqual(len(cut), 1)

    def test_a_complete_dump_is_not_reported_as_cut(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            for function in self.FUNCTIONS:
                self.run_artifact(function, path)
        self.assertFalse([message for message in messages if 'was cut' in message])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example.txt', fixture.build_report('a10'))
        alone = len(self.run_artifact(artifacts.bugreport_unix_sockets, first)[1])
        both = self.run_artifact(artifacts.bugreport_unix_sockets, first, second)[1]
        self.assertEqual(len(both), alone + 2)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example.txt'})

    def test_a_zip_on_the_device_is_read(self):
        data = fixture.cases()['synthetic_zip_on_device'][0]
        path = self.stage(data[0], data[1])
        _headers, rows, _source = self.run_artifact(artifacts.bugreport_wifi_saved_networks, path)
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[0][-1].endswith('.zip!/bugreport-example-EXAMPLE-2026-11-02-10-15-30.txt'))

    def test_the_section_index_names_these_artifacts(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        from scripts.artifacts import bugreportDevice          # pylint: disable=import-outside-toplevel
        _headers, rows, _source = self.run_artifact(bugreportDevice.bugreport_sections, path)
        text = ' | '.join(str(row) for row in rows)
        self.assertIn('Wi-Fi Saved Networks', text)
        self.assertIn('Open Sockets', text)


def headers_index(headers, name):
    return [h[0] if isinstance(h, tuple) else h for h in headers].index(name)


if __name__ == '__main__':
    unittest.main()
