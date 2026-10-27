"""Builds the synthetic Android bug report texts used by the Android Bug Report network test cases.

Every value is invented: SSIDs are Example names, addresses are in the documentation ranges (192.0.2.0/24,
198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32), hardware addresses start with 02:00:5e, package names are under
example.*, uids and times are fixed. Only the structure is taken from real bug reports: the banner, the header
lines, the command sections (NETWORK DEV INFO, NETWORK INTERFACES, NETSTAT, DETAILED SOCKET STATE, CHECKIN NETSTATS)
and the dumpsys service sections (wifi, wifiscanner, wifip2p, netstats, netpolicy, connectivity, dnsresolver,
tethering) with the section trailers the platform prints. Two layouts are built:

* ``a16``: the layout of Android 15 and 16 (extended Wi-Fi entries, the full netstats dump with a UID table, link
  properties, ``created=`` times, counters in ``ip -s link``, user and inode columns in netstat, a tethering service,
  a private DNS log);
* ``a10``: the layout of Android 10 (creation and update times on the Wi-Fi entries, the compact ``--checkin`` netstats
  form, no link properties, ``ip link`` without counters, netstat without user and inode, no tethering service).

Usage (from the repository root): python -m admin.test.scripts.bugreport_network_fixture <output folder>
Writes one zip per test case into the folder, each holding a synthetic extraction, and prints their names and sizes.
"""
import io
import os
import sys

from admin.test.scripts import bugreport_fixture as base

REPORT = '2026-11-02 10:15:30'
ZONE = 'Europe/Paris'


def epoch_s(text):
    return base.epoch_s(text)


# ------------------------------------------------------------------------------------------
# wifi
# ------------------------------------------------------------------------------------------
def wifi_networks(layout):
    lines = ['WifiConfigManager - Configured networks Begin ----']
    if layout == 'a16':
        entries = [
            ('* ', 0, '"Example-Home"', 'true', 'true', None, 'NETWORK_SELECTION_ENABLED', None, 3, '02:00:5e:10:00:01',
             'WPA_PSK', 1000, 'android.uid.system:1000', 10100, 'com.example.settings', 10100, 'true', 0, None, None, None),
            ('- DSBLE ', 1, '"Example Guest"', 'false', 'false', None, 'NETWORK_SELECTION_PERMANENTLY_DISABLED',
             'NETWORK_SELECTION_DISABLED_BY_WRONG_PASSWORD', 3, '02:00:5e:10:00:02', 'WPA_PSK', 1000,
             'android.uid.system:1000', 1000, 'android.uid.system:1000', 1000, 'false', 41, None, None, None),
            ('', 2, '"Example Cafe, Terrace"', 'false', 'false', None, 'NETWORK_SELECTION_ENABLED', None, 3,
             '02:00:5e:10:00:03', 'SAE', 1000, 'android.uid.system:1000', 1000, 'android.uid.system:1000', 10200, 'false', 7,
             None, None, None),
        ]
        for (mark, number, ssid, current, selected, _x, status, reason, mac_setting, mac, key_mgmt, cuid, cname, luid, lname,
             lcuid, recent, reboots, _y, _z, _w) in entries:
            lines.append('%sID: %d SSID: %s PROVIDER-NAME: null BSSID: null FQDN: null HOME-PROVIDER-NETWORK: false PRIO: 0 '
                         'HIDDEN: false PMF: false CarrierId: -1 SubscriptionId: -1 SubscriptionGroup: null '
                         'Currently Connected: %s User Selected: %s' % (mark, number, ssid, current, selected))
            lines.append(' NetworkSelectionStatus %s' % status)
            if reason:
                lines.append(' mNetworkSelectionDisableReason %s' % reason)
                lines.append('%s counter:1' % reason)
            lines += [' hasEverConnected: true', ' hasNeverDetectedCaptivePortal: true',
                      ' macRandomizationSetting: %d' % mac_setting, ' mRandomizedMacAddress: %s' % mac,
                      ' KeyMgmt: %s Protocols: WPA RSN' % key_mgmt, ' AuthAlgorithms:', ' PairwiseCiphers: TKIP CCMP',
                      'SecurityParams List:', 'Security Parameters:', ' Type: 2', ' Enabled: true', ' KeyMgmt: SAE',
                      ' Protocols: RSN', '',
                      ' cuid=%d cname=%s luid=%d lname=%s lcuid=%d allowAutojoin=true noInternetAccessExpected=false '
                      'mostRecentlyConnected=%s ' % (cuid, cname, luid, lname, lcuid, recent),
                      'numRebootsSinceLastUse: %d' % reboots,
                      'recentFailure: Association Rejection code: 0, last update time: 0', 'bssidAllowlist unset', '']
    else:
        entries = [
            (0, '"Example-Home"', 627, 'creation time=08-27 15:07:06.108', 'update time=10-30 06:39:02.605', None),
            (1, '"Example Office"', 3, 'creation time=09-08 21:14:58.080', None, '"Example Home"WPA_PSK connect choice rssi: -81'),
            (2, 'ExampleHex0A', 0, 'creation time=03-27 02:30:00.000', None, None),
        ]
        for number, ssid, associations, creation, update, choice in entries:
            lines.append('ID: %d SSID: %s PROVIDER-NAME: null BSSID: null FQDN: null autoJoin: true autoJoinMenu: false '
                         'canModify: true canForget: true PRIO: 0 HIDDEN: false REMOVABLE: true CARRIERPRELOAD: false PMF: %s'
                         % (number, ssid, 'true' if number == 1 else 'false'))
            lines.append(' NetworkSelectionStatus NETWORK_SELECTION_ENABLED')
            if choice:
                lines.append(' connect choice: %s hasEverConnected: true' % choice)
            else:
                lines.append(' hasEverConnected: true')
            lines.append(' numAssociation %d' % associations)
            lines.append(' ' + creation)
            if update:
                lines.append(' ' + update)
            lines += [' validatedInternetAccess trusted', ' macRandomizationSetting: 1', ' mRandomizedMacAddress: 02:00:5e:20:00:0%d' % number,
                      ' KeyMgmt: WPA_PSK Protocols: WPA RSN', ' AuthAlgorithms: OPEN', '', '', 'IP config:',
                      'IP assignment: DHCP', 'Proxy settings: NONE',
                      ' cuid=1000 cname=android.uid.system:1000 luid=1000 lname=android.uid.system:1000 lcuid=1000 '
                      'userApproved=USER_UNSPECIFIED noInternetAccessExpected=false ',
                      'recentFailure: Association Rejection code: 0', '']
    lines.append('WifiConfigManager - Configured networks End ----')
    lines.append('WifiConfigManager - ConfigurationMap Begin ----')       # the same networks again: must not be read
    lines.append('ID: 9 SSID: "Example Duplicate" PROVIDER-NAME: null BSSID: null FQDN: null PRIO: 0 HIDDEN: false PMF: false')
    lines.append('WifiConfigManager - ConfigurationMap End ----')
    return lines


def wifi_service(layout):
    lines = ['DUMP OF SERVICE wifi:', 'Service host process PID: 2682', 'Threads in use: 2/32', 'Client PIDs: 4901, 2096',
             'Wi-Fi is enabled' if layout == 'a10' else 'Wi-Fi is enabled', 'Current wifi mode: %s'
             % ('ClientModeActiveState' if layout == 'a10' else 'EnabledState'),
             'ID: 7 SSID: "Example Outside The Block" PROVIDER-NAME: null BSSID: null FQDN: null PRIO: 0 HIDDEN: false PMF: false',
             'WifiController:',
             '  rec[0]: time=11-01 21:05:10.120 processed=DefaultState org=EnabledState dest=<null> what=CMD_UPDATE_AP_CAPABILITY 1 0',
             '  rec[1]: time=11-01 21:06:40.007 processed=EnabledState org=EnabledState dest=<null> what=160006(0x27106)',
             'WifiClientModeImpl:']
    if layout == 'a16':
        lines += ['mLinkProperties {InterfaceName: wlan0 LinkAddresses: [ fe80::ff:fe00:1/64,192.0.2.15/24 ] DnsAddresses: [ /192.0.2.1 ] '
                  'Domains: null MTU: 0 ServerAddress: /192.0.2.1 Routes: [ 0.0.0.0/0 -> 192.0.2.1 wlan0 mtu 0 ]}',
                  'mWifiInfo SSID: "Example-Home", BSSID: 02:00:5e:30:00:01, MAC: 02:00:5e:10:00:01, IP: /192.0.2.15, '
                  'Security type: 2, Supplicant state: COMPLETED, Wi-Fi standard: 11n, RSSI: -61, Link speed: 65Mbps, '
                  'Tx Link speed: 65Mbps, Max Supported Tx Link speed: 150Mbps, Rx Link speed: -1Mbps, Frequency: 2437MHz, '
                  'Net ID: 0, Metered hint: false, score: 60, isUsable: true',
                  'mLastBssid 02:00:5e:30:00:01',
                  'mWifiInfo SSID: <unknown ssid>, BSSID: <none>, MAC: 02:00:00:00:00:00, IP: null, Security type: -1, '
                  'Supplicant state: DISCONNECTED, RSSI: -127, Link speed: -1Mbps, Frequency: -1MHz, Net ID: -1, Metered hint: false',
                  'mLastBssid null']
    else:
        lines += ['mLinkProperties {InterfaceName: wlan0 DnsAddresses: [ /198.51.100.1 ] Domains: null MTU: 0}',
                  'mWifiInfo SSID: Example Hotspot, Supplicant state: COMPLETED, RSSI: -41, Link speed: 144Mbps, '
                  'Tx Link speed: 144Mbps, Rx Link speed: 144Mbps, Frequency: 2437MHz, Net ID: 10, Metered hint: true, score: 60',
                  'mLastBssid 02:00:**:**:b4:9d']
    lines += ['WifiMetrics:', 'mConnectionEvents:']
    lines.append('startTime=11-01 6:5:39.713, SSID="Example-Home", BSSID=02:00:5e:30:00:01, durationMillis=1623, '
                 'roamType=ROAM_UNRELATED, connectionResult=1, level2FailureCode=NONE, connectivityLevelFailureCode=NONE, '
                 'signalStrength=-73, wifiState=WIFI_DISCONNECTED, screenOn=true, mRouterFingerprint=mConnectionEvent.roamType=0, '
                 'mChannelInfo=2412, mDtim=0, mAuthentication=2, mHidden=false, networkType=TYPE_WPA2, '
                 'connectionNominator=NOMINATOR_SAVED, networkCreator=CREATOR_USER, interfaceName=wlan0 interfaceRole=ROLE_CLIENT_PRIMARY, uid=1010')
    lines.append('startTime=11-01 21:5:48.45, SSID="Example Cafe, Terrace", BSSID=02:00:5e:30:00:03, durationMillis=488, '
                 'roamType=ROAM_UNRELATED, connectionResult=3, level2FailureCode=ASSOCIATION_REJECTION, '
                 'connectivityLevelFailureCode=NONE, signalStrength=-80, wifiState=WIFI_DISCONNECTED, screenOn=false, mChannelInfo=5180')
    lines += ['mWifiLogProto.numSavedNetworks=3', 'mGroupEvents:']
    lines += wifi_networks(layout)
    lines += ['WifiDeviceStateChangeManager - Log Begin ----',
              '2026-11-01T21:05:09.500000 - mLastScreenOn: true:',
              'mLastActiveScreenStateQuery: not a time-stamped line',
              '2026-11-01T21:05:12.250000 - screen off',
              'WifiDeviceStateChangeManager - Log End ----',
              'WifiConnectivityManager - Log Begin ----',
              '2026-11-01T21:06:00.001 - setWifiEnabled: uid=1000',
              '1970-01-01T00:00:00.000 - an unset time',
              'WifiConnectivityManager - Log End ----',
              '2026-11-01T22:00:00.000 - a time-stamped line outside any block']
    return '\n'.join(lines) + '\n--------- 0.200s was the duration of dumpsys wifi, ending at: 2026-11-02 10:15:12\n\n'


def wifiscanner_service(layout):
    lines = ['DUMP OF SERVICE wifiscanner:', 'WifiScanningService - Log Begin ----',
             '2026-11-01T21:05:10.100000 - registerScanListener: ClientInfo[uid=1000, package=android]',
             '2026-11-01T21:05:11.000000 - singleScanResults: ClientInfo[uid=1000, package=android],results=2',
             'WifiScanningService - Log End ----', '', 'clients:', 'WifiPnoScanStateMachine:', ' total records=2',
             ' rec[0]: time=11-01 21:05:10.527 processed=DefaultState org=DefaultState dest=StartedState what=WifiScanner.CMD_ENABLE  0 0',
             ' rec[1]: time=11-01 21:05:30.711 processed=StartedState org=StartedState dest=<null> what=160006(0x27106)',
             'curState=StartedState', '', 'WifiSingleScanStateMachine:', ' total records=1',
             ' rec[0]: time=11-01 21:05:11.000 processed=ScanningState org=ScanningState dest=IdleState what=CMD_SCAN_RESULTS_AVAILABLE  0 0',
             'curState=IdleState', '', 'Latest scan results:',
             '    BSSID              Frequency      RSSI           Age(sec)     SSID                                 Flags']
    if layout == 'a16':
        lines += ['  02:00:5e:30:00:01       2437        -58(0:-61/1:-62)   226.141    Example-Home                      [WPA2-PSK-CCMP-128][RSN-PSK-CCMP-128][ESS]',
                  '  02:00:5e:30:00:02       5180        -86            >1000.0    Example Neighbor 5G               [RSN-SAE-CCMP-128][ESS][WPS]',
                  '  02:00:5e:30:00:03       2412        -90            12.5                                         ']
    else:
        lines += ['  02:00:**:**:b4:9d       2437        -40             53.452    ExHot11D8E522                     [WPA2-PSK-CCMP][RSN-PSK-CCMP][ESS]']
    lines += ['', 'Latest native scan results:',
              '    BSSID              Frequency      RSSI           Age(sec)     SSID                                 Flags',
              '  02:00:5e:30:00:01       2437        -57            226.150    Example-Home                      [WPA2-PSK-CCMP-128][ESS]',
              'Latest native pno scan results:', 'Latest native scan results IEs:',
              '000f4578616d706c652d486f6d65010882848b960c1218240301']
    return '\n'.join(lines) + '\n--------- 0.034s was the duration of dumpsys wifiscanner, ending at: 2026-11-02 10:15:13\n\n'


def wifip2p_service():
    lines = ['DUMP OF SERVICE wifip2p:', 'WifiP2pService:', ' total records=2',
             ' rec[0]: time=11-01 21:05:34.808 processed=DefaultState org=P2pDisabledState dest=<null> what=WifiP2pManager.UPDATE_CHANNEL_INFO sender=com.example.share(10120)',
             ' rec[1]: time=11-01 21:05:35.757 processed=DefaultState org=P2pDisabledState dest=<null> what=AsyncChannel.CMD_CHANNEL_FULL_CONNECTION sender=android(1000)',
             'curState=P2pDisabledState', 'WifiP2pMetrics:', 'mConnectionEvents:', 'mGroupEvents:']
    return '\n'.join(lines) + '\n--------- 0.010s was the duration of dumpsys wifip2p, ending at: 2026-11-02 10:15:13\n\n'


# ------------------------------------------------------------------------------------------
# netstats
# ------------------------------------------------------------------------------------------
WIFI_IDENT_A16 = ('{type=1, ratType=COMBINED, wifiNetworkKey="Example-Home"wpa2-psk, metered=false, defaultNetwork=true, '
                  'oemManaged=OEM_NONE, subId=-1, transports={1}}')
CELL_IDENT_A16 = ('{type=0, ratType=13, subscriberId=999990..., metered=true, defaultNetwork=false, oemManaged=OEM_NONE, '
                  'subId=2, transports={0}}')
WIFI_IDENT_A10 = '{type=WIFI, subType=0, networkId="Example Hotspot", metered=true, defaultNetwork=true}'


def history(bucket, rows, form):
    """History lines: ``rows`` are (start, rb, rp, tb, tp, op)."""
    out = ['    NetworkStatsHistory: bucketDuration=%d' % bucket] if form == 'a16' else \
        ['   proc=', '   actUid=-1NetworkStatsHistory: bucketDuration=%d' % bucket]
    for start, rb, rp, tb, tp, op in rows:
        extra = '' if form == 'a16' else ' rb=0 rp=0 tb=0 tp=0'
        out.append('      st=%d rb=%d rp=%d tb=%d tp=%d op=%d%s' % (start, rb, rp, tb, tp, op, extra))
    return out


def netstats_tables(layout, with_uid):
    base_start = epoch_s('2026-11-01 20:00:00')
    lines = []
    if layout == 'a16':
        lines += ['Dev stats:', '  Pending bytes: 0', 'Xt stats:', '  Pending bytes: 507749', '  Complete history:',
                  '  ident=[%s] uid=-1 set=ALL tag=0x0' % WIFI_IDENT_A16]
        lines += history(3600, [(base_start, 3200614, 15100, 9886381, 13967, 0), (base_start + 3600, 2923206, 14613, 86325178, 14240, 0),
                                (1000, 5, 1, 5, 1, 0)], 'a16')
        lines += ['  ident=[%s] uid=-1 set=ALL tag=0x0' % CELL_IDENT_A16]
        lines += history(3600, [(base_start, 371791, 296, 1484, 26, 0)], 'a16')
        if with_uid:
            lines += ['UID stats:', '  Pending bytes: 0', '  Complete history:']
            for uid, net_set, rows in ((10300, 'DEFAULT', [(base_start, 1200, 10, 3400, 12, 0), (base_start + 7200, 50, 1, 60, 1, 0)]),
                                       (10300, 'FOREGROUND', [(base_start, 700, 5, 800, 6, 1)]),
                                       (1010300, 'DEFAULT', [(base_start, 15, 1, 25, 1, 0)])):
                lines.append('  ident=[%s] uid=%d set=%s tag=0x0' % (WIFI_IDENT_A16, uid, net_set))
                lines += history(7200, rows, 'a16')
            lines += ['UID tag stats:', '  Pending bytes: 0', '  Complete history:']
        lines += ['InterfaceMapHelper:', '  Nothing to see']
    else:
        lines += ['Dev stats:', '  Pending bytes: 0', '  History since boot:', '  ident=[%s] uid=-1 set=ALL tag=0x0' % WIFI_IDENT_A10]
        lines += history(3600, [(base_start, 81970169, 13886, 1420640, 5060, 0)], 'a10')
        lines += ['Xt stats:', '  Pending bytes: 0', '  History since boot:', '  ident=[%s] uid=-1 set=ALL tag=0x0' % WIFI_IDENT_A10]
        lines += history(3600, [(base_start, 81970169, 13886, 1420640, 5060, 0)], 'a10')
    return lines


def netstats_service(layout):
    lines = ['DUMP OF SERVICE netstats:', 'Active interfaces:',
             '  iface=wlan0 ident=[%s] ' % (WIFI_IDENT_A16 if layout == 'a16' else WIFI_IDENT_A10),
             'Top openSession callers:', '  {uid=1000,package=android}=271', '']
    lines += netstats_tables(layout, with_uid=False)
    return '\n'.join(lines) + '\n--------- 0.044s was the duration of dumpsys netstats, ending at: 2026-11-02 10:15:14\n\n'


def checkin_netstats(layout):
    if layout == 'a16':
        text = '------ CHECKIN NETSTATS (/system/bin/dumpsys -T 30000 netstats --full --uid) ------\nDirectory:\n  /data/misc/example\nConfigs:\n  a=b\n'
        text += '\n'.join(netstats_tables('a16', with_uid=True)) + '\n'
    else:
        start = epoch_s('2026-11-01 20:00:00')
        text = ('------ CHECKIN NETSTATS (/system/bin/dumpsys -T 30000 netstats --checkin) ------\n'
                'v1,%d,%d\nxt\nc,cell,-1,all,0\nd,3600\nb,%d,5103817,5709,1546414,4346,0\nb,%d,83868088,17466,1962777,7866,0\n'
                'c,wifi,-1,all,0\nd,3600\nb,%d,3850766,4899,1038873,5502,0\n' % (start, start + 86400, start, start + 3600, start))
    return text + "------ 0.300s was the duration of 'CHECKIN NETSTATS' ------\n\n"


# ------------------------------------------------------------------------------------------
# netpolicy
# ------------------------------------------------------------------------------------------
def netpolicy_service(layout, cut=False):
    lines = ['DUMP OF SERVICE netpolicy:', 'Service host process PID: 2682', 'Threads in use: 1/32', 'Client PIDs: 2554, 2542',
             'System ready: true', 'Restrict background: false', 'Restrict power: true', 'Device idle: false', '', 'Flags:',
             'com.example.net.use_metered_firewall_chains: true', 'mRestrictBackgroundLowPowerMode: false', '',
             'Network policies:',
             '  NetworkPolicy{template=NetworkTemplate: matchRule=CARRIER, matchSubscriberIds=[999990...], metered=YES warningBytes=2000000000 limitBytes=-1}',
             '', 'Active subscriptions:', '  1=999990...', '', 'Policy for UIDs:',
             '  UID=1000 policy=4 (ALLOW_METERED_BACKGROUND)', '  UID=10300 policy=4 (ALLOW_METERED_BACKGROUND)',
             'Power save whitelist (except idle) app ids:', '  UID=1000: true', '  UID=10120: true',
             'Default restrict background %s uids:' % ('allowlist' if layout == 'a16' else 'whitelist'), '  UID=10300',
             'Uids transitioning to background:', '  UID=10300, +3s400ms']
    if layout == 'a16':
        lines += ['Status for all known UIDs:', '  UID=-1 state=null blocked_state={blocked=NONE,allowed=NONE,effective=NONE} ',
                  '    callback_info=null ',
                  '  UID=10300 state={procState=TOP ,seq=55,cap=LCMNFUAT} blocked_state={blocked=NONE,allowed=RESTRICTED_MODE_PERMISSIONS,effective=NONE} ']
    else:
        lines += ['Status for all known UIDs:', '  UID=10300 state=2 (fg) rules=0 (NONE)', 'Status for just UIDs with rules:',
                  '  UID=10120 rules=1 (REJECT_ALL)']
    lines += ['Network to interfaces:', '  101: {wlan0}', '', 'Stats:',
              '  updateNetworkEnabledNL(): count=74, total=17.6ms, avg=0.238ms, max calls/s=4', '',
              'mEventLogs (most recent first):', '  2026-11-01T21:06:17:657 - Firewall rule changed: 10246-powersave-allow',
              '  2026-11-01T21:05:17:165 - Firewall rule changed: 20065-background-allow', '  1970-01-01T00:00:00:000 - null',
              'mNetworkBlockedLogs (most recent first):',
              '  2026-11-01T21:06:18:679 - 86664-{blocked=BATTERY_SAVER|APP_BACKGROUND,allowed=NOT_IN_BACKGROUND,effective=BATTERY_SAVER}',
              'mUidStateChangeLogs (most recent first):', '  2026-11-01T21:02:53:415 - 86098:LAST:--------:46474',
              'MultipathPolicyTracker:', '  Network 101: quota 0, budget 0']
    text = '\n'.join(lines) + '\n'
    if cut:
        return text + "*** SERVICE 'netpolicy' DUMP TIMEOUT (10000ms) EXPIRED ***\n\n"
    return text + '--------- 0.080s was the duration of dumpsys netpolicy, ending at: 2026-11-02 10:15:17\n\n'


# ------------------------------------------------------------------------------------------
# connectivity and dns
# ------------------------------------------------------------------------------------------
def connectivity_service(layout):
    lines = ['DUMP OF SERVICE connectivity:', 'NetworkProviders for:', '  1: EthernetNetworkFactory',
             'Active default network: %d' % (101 if layout == 'a16' else 100),
             '', 'Current Networks:']
    if layout == 'a16':
        lines.append('  NetworkAgentInfo{network{101}  handle{758161092145}  ni{WIFI CONNECTED extra: } created=2026-11-01T20:40:10.404Z '
                     'Score(Policies : TRANSPORT_PRIMARY&IS_UNMETERED ; KeepConnected : 0)  created 290474441  '
                     'lp{{InterfaceName: wlan0 LinkAddresses: [ fe80::ff:fe00:1/64,192.0.2.15/24 ] DnsAddresses: [ /192.0.2.1 ] '
                     'Domains: null MTU: 0 ServerAddress: /192.0.2.1 Routes: [ fe80::/64 -> :: wlan0 mtu 0,0.0.0.0/0 -> 192.0.2.1 wlan0 mtu 0 ]}}  '
                     'nc{[ Transports: WIFI Capabilities: NOT_METERED&INTERNET&VALIDATED&NOT_ROAMING LinkUpBandwidth>=12000Kbps '
                     'Specifier: <WifiNetworkAgentSpecifier [WifiConfiguration=, SSID="Example-Home", BSSID=02:00:5e:30:00:01]> '
                     'SignalStrength: -64 OwnerUid: 1000 SSID: "Example-Home" UnderlyingNetworks: Null]}  factorySerialNumber=6}')
        lines.append('    Nat464Xlat:')
        lines.append('  NetworkAgentInfo{network{102}  handle{437197393999}  ni{MOBILE CONNECTED extra: internet} created=2026-11-01T20:41:00.000Z '
                     'Score(Policies : IS_VALIDATED ; KeepConnected : 0)  '
                     'lp{{InterfaceName: rmnet0 LinkAddresses: [ 198.51.100.7/30 ] DnsAddresses: [ /198.51.100.1,/198.51.100.2 ] Domains: example.test MTU: 1500 Routes: [  ]}}  '
                     'nc{[ Transports: CELLULAR Capabilities: INTERNET&VALIDATED SignalStrength: -95]}  factorySerialNumber=7}')
    else:
        lines.append('  NetworkAgentInfo{ ni{[type: WIFI[], state: CONNECTED/CONNECTED, reason: (unspecified), extra: (none), failover: false, '
                     'available: true, roaming: false]}  network{100}  nethandle{753596381247}  nc{[ Transports: WIFI Capabilities: '
                     'INTERNET&NOT_RESTRICTED&TRUSTED&NOT_VPN&VALIDATED SignalStrength: -36 SSID: *****]}  Score{60}  everValidated{true}  '
                     'clat{mBaseIface: null, mIface: null, mState: IDLE} }')
    lines += ['    Requests: REQUEST:1', '      NetworkRequest [ REQUEST id=1, [ Capabilities: INTERNET ] ]', 'Status for known UIDs:']
    return '\n'.join(lines) + '\n--------- 0.100s was the duration of dumpsys connectivity, ending at: 2026-11-02 10:15:18\n\n'


def dnsresolver_service(layout):
    lines = ['DUMP OF SERVICE dnsresolver:', 'NetId: 101', '  DNS servers: # IP (total, successes, errors, timeouts, internal errors, RTT avg, last sample)',
             '    192.0.2.1 (64, 62, 0, 2, 0, 53ms, 43s)', '    2001:db8::53%wlan0 (6, 1, 0, 5, 0, -1ms, 257s)']
    if layout == 'a16':
        lines += ['  Interface names: [wlan0]', '  No search domains defined', '  DNS parameters: sample validity = 1800s',
                  '  Private DNS mode: OPPORTUNISTIC', '  Server statistics: (total, RTT avg, {rcode:counts}, last update)',
                  '    over UDP', '      192.0.2.1:53 (104, 50ms, [NOERROR:104 ], 42s) score{99.5}', '  TransportType: WIFI',
                  '  Metered: false', '', 'NetId: 102', '  DNS servers: # IP (total, successes, errors, timeouts, internal errors, RTT avg, last sample)',
                  '    198.51.100.1 (3, 0, 0, 3, 0, -1ms, 286s)', '  Interface names: [rmnet0]', '  Search domains: example.test',
                  '  Private DNS mode: OFF', '  TransportType: CELLULAR', '  Metered: true', '', 'PrivateDnsLog:',
                  '  03:06:25.779 - netId=100 PrivateDns={192.0.2.1:853/} state=in_process',
                  '  03:06:26.365 - netId=101 PrivateDns={192.0.2.1:853/} state=fail', '', 'Experiments list: ', '  retry_count: 2']
    else:
        lines += ['  No search domains defined', '  DNS parameters: sample validity = 1800s', '  Private DNS mode: OPPORTUNISTIC',
                  '  Private DNS configuration (1 entries)', '    192.0.2.1 name{} status{fail}', '  Concurrent DNS query timeout: 0', '']
    return '\n'.join(lines) + '\n--------- 0.010s was the duration of dumpsys dnsresolver, ending at: 2026-11-02 10:15:19\n\n'


def tethering_service():
    lines = ['DUMP OF SERVICE HIGH tethering:', 'Service host process PID: 2481', 'Tethering:', '  Callbacks registered: 24',
             '  Configuration:', '    activeDataSubId: 2', '    tetherableUsbRegexs: [rndis\\d]', '  Entitlement:',
             '    isCellularUpstreamPermitted: true', '  Tether state:', '    Upstream wanted: false',
             '    Current upstream interface(s): null', '  Hardware offload:', '    Offload HALs not started', '    ForwardedStats:',
             '      <empty>', '  Log:',
             '    2026-11-01T21:05:34.472718 - MARK Tethering.constructed',
             '    2026-11-01T21:05:36.767088 - OBSERVED configuration changed',
             '    2026-11-01T21:05:38.044112 - USB bcast connected:false configured:false rndis:false ncm:false']
    return '\n'.join(lines) + '\n--------- 0.020s was the duration of dumpsys tethering, ending at: 2026-11-02 10:15:20\n\n'


# ------------------------------------------------------------------------------------------
# commands
# ------------------------------------------------------------------------------------------
def command(title, text, duration=True):
    out = '------ %s ------\n%s' % (title, text)
    if duration:
        out += "------ 0.002s was the duration of '%s' ------\n\n" % title.split(' (')[0]
    return out


def dev_info():
    rows = ['    lo:  183416    7401    0    0    0     0          0         0   183416    7401    0    0    0     0       0          0',
            ' wlan0: 84368415   14685    0    0    0     0          0         0  1641480    5516    0    3    0     0       0          0',
            'rmnet0:       0       0    0    0    0     0          0         0      280       2    0    0    0     0       0          0']
    return command('NETWORK DEV INFO (/proc/net/dev)',
                   'Inter-|   Receive                                                |  Transmit\n'
                   ' face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed\n'
                   + '\n'.join(rows) + '\n')


def interfaces(layout):
    stats = layout == 'a16'
    lines = ['1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000',
             '    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00']
    if stats:
        lines += ['    RX: bytes  packets  errors  dropped overrun mcast   ', '    183416     7401     0       0       0       0       ',
                  '    TX: bytes  packets  errors  dropped carrier collsns ', '    183416     7401     0       0       0       0       ']
    lines += ['2: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DORMANT group default qlen 3000',
              '    link/ether 02:00:5e:10:00:01 brd ff:ff:ff:ff:ff:ff']
    if stats:
        lines += ['    RX: bytes  packets  errors  dropped overrun mcast   ', '    84368415   14685    0       0       0       12      ',
                  '    TX: bytes  packets  errors  dropped carrier collsns ', '    1641480    5516     0       3       0       0       ']
    lines += ['3: ip_vti0@NONE: <NOARP> mtu 1480 qdisc noop state DOWN mode DEFAULT group default qlen 1000',
              '    link/ipip 0.0.0.0 brd 0.0.0.0']
    if stats:
        lines += ['    RX: bytes  packets  errors  dropped overrun mcast   ', '    0          0        0       0       0       0       ',
                  '    TX: bytes  packets  errors  dropped carrier collsns ', '    0          0        0       0       0       0       ']
    return command('NETWORK INTERFACES (%s)' % ('ip -s link' if stats else 'ip link'), '\n'.join(lines) + '\n')


def netstat(layout):
    if layout == 'a16':
        text = ('Active Internet connections (servers and established)\n'
                'Proto Recv-Q Send-Q Local Address                                       Foreign Address                                     State       User       Inode       PID/Program\n'
                'tcp        0      0 192.0.2.15:42676                                    203.0.113.4:443                                     ESTABLISHED 86664      67153498    -\n'
                'tcp      130      0 192.0.2.15:36384                                    203.0.113.9:443                                     CLOSE_WAIT  10246      67823827    -\n'
                'tcp        0      1 192.0.2.15:40346                                    203.0.113.11:443                                    FIN_WAIT1   0          0           -\n'
                'udp     4352      0 192.0.2.15:68                                       192.0.2.1:67                                        ESTABLISHED 1073       67804605    -\n'
                'udp        0      0 192.0.2.15:47000                                    203.0.113.4:443                                                 86664      67198007    -\n'
                'tcp6       0      0 [2001:db8::1]:41000                                 [2001:db8::2]:443                                   ESTABLISHED 86664      77880000    -\n'
                'raw6       0      0 [::]:58                                             [::]:*                                              7           1000       67224811    -\n'
                'Active UNIX domain sockets (servers and established)\n'
                'Proto RefCnt Flags       Type       State         I-Node   PID/Program Name     Path\n'
                'unix  2      [ ]         DGRAM      CONNECTED     67485743 -                   \n'
                'unix  2      [ ACC ]     STREAM     LISTENING     67293694 -                    /dev/socket/example\n'
                'unix  3      [ ]         SEQPACKET  CONNECTED     67222009 1234/example_daemon  /dev/socket/example name\n')
    else:
        text = ('Active Internet connections (w/o servers)\r\n'
                'Proto Recv-Q Send-Q Local Address                                       Foreign Address                                     State      \r\n'
                'tcp      130      0 198.51.100.20:39726                                 203.0.113.9:443                                     CLOSE_WAIT \r\n'
                'tcp6       0      0 [2001:db8::1]:41000                                 [2001:db8::2]:443                                   ESTABLISHED\r\n'
                'udp        0      0 198.51.100.20:68                                    198.51.100.1:67                                     ESTABLISHED\r\n'
                'raw6       0      0 [::]:58                                             [::]:*                                              7\r\n'
                'Active UNIX domain sockets (w/o servers)\r\n'
                'Proto RefCnt Flags\t Type\t    State\t    I-Node Path\r\n'
                'unix  76     [ ]         DGRAM                       23594 /dev/socket/example\r\n'
                'unix  2      [ ]         STREAM     CONNECTED       674368 /dev/socket/example2\r\n')
    return command('NETSTAT (%s)' % ('netstat -npWae' if layout == 'a16' else 'netstat -nW'), text)


def socket_state():
    text = ('Netid  State      Recv-Q Send-Q Local Address:Port               Peer Address:Port              \n'
            'udp    ESTAB      4352   0      192.0.2.15%wlan0:68                    192.0.2.1:67                  uid:1073 ino:67804605 sk:81aeed <->\n'
            'tcp    ESTAB      0      0      192.0.2.15:42676              203.0.113.4:443                 timer:(keepalive,7.2sec,0) uid:86664 ino:67153498 sk:836409 <->\n'
            '\t ts sack cubic wscale:9,10 rto:280 rtt:79.908/34.454 ato:40 mss:1348\n'
            '\t bytes_acked:582 bytes_received:4173 segs_out:17 segs_in:7\n'
            'tcp    LISTEN     0      4      *:8080                        *:*                       users:(("example",pid=1234,fd=7)) uid:0 ino:1 sk:1\n'
            'tcp    ESTAB      0      0      192.0.2.15:1                  203.0.113.5:2\n')
    return command('DETAILED SOCKET STATE (ss -eionptu)', text)


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='a16', zone=ZONE, report=REPORT, cut=False, newline='\n', with_banner=True):
    text = (base.BANNER.format(report=report) if with_banner else '') + '\n' + base.HEADER[layout] + '\n'
    text += base.properties(layout, zone, 'reboot,userrequested,%d' % epoch_s('2026-10-30 07:00:00'))
    text += dev_info() + interfaces(layout) + netstat(layout) + socket_state() + checkin_netstats(layout)
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    text += wifi_service(layout) + wifiscanner_service(layout) + wifip2p_service() + netstats_service(layout)
    text += netpolicy_service(layout, cut=cut) + connectivity_service(layout) + dnsresolver_service(layout)
    if layout == 'a16':
        text += tethering_service()
    text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"
    text += '== dumpstate: done (id 1)\n'
    return text.replace('\n', newline)


def bug_report_zip(layout, **kwargs):
    """The zip a device keeps: main_entry.txt naming the main text, the text, a side log and a version file."""
    main_text = 'bugreport-example-%s-2026-11-02-10-15-30.txt' % ('EXAMPLE' if layout == 'a16' else 'EXOLD')
    buffer = io.BytesIO()
    base.write_zip(buffer, [('main_entry.txt', main_text.encode()), (main_text, build_report(layout, **kwargs).encode('utf-8')),
                            ('dumpstate_log.txt', b'dumpstate log of an invented device\n'), ('version.txt', b'2.0')])
    return buffer.getvalue()


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16').encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt', build_report('a10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_zip_on_device'] = [
        ('Dump/data/user_de/0/com.android.shell/files/bugreports/bugreport-example-2026-11-02-10-15-30.zip',
         bug_report_zip('a16', zone='Asia/Kolkata', report='2026-11-02 15:45:30'))]
    out['synthetic_two_reports'] = [('Dump1/dumpstate.txt', build_report('a16', zone='Asia/Kolkata').encode('utf-8')),
                                    ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                                     build_report('a10', zone='America/Sao_Paulo').encode('utf-8'))]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report=REPORT) + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\nDUMP OF SERVICE wifi:\nID: 0 SSID: "x"\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    odd = build_report('a16', zone='').encode('utf-8')
    odd = b'\xef\xbb\xbf' + odd.replace(b'Example-Home"wpa2-psk', b'Example-\xe9Home"wpa2-psk', 1).replace(
        b'Example Guest', b'Example\x00 Guest', 1).replace(b'Bootloader: EXAMPLEBL1', b'Bootloader: EX\rAMPLE\x0cBL1', 1)
    out['synthetic_odd_bytes'] = [('Dump/dumpstate.txt', odd)]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_network_fixture_out')
