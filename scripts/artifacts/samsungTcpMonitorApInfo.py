__artifacts_v2__ = {
    "samsungTcpMonitorApInfo": {
        "name": "Samsung Wi-Fi - Networks and Foreground Apps",
        "description": "Records of Samsung's Wi-Fi TCP monitor in misc/wifi/TcpMonitorApInfo.json: one "
                       "record per Wi-Fi network name (SSID) with its stored connection figures, and the "
                       "packages the monitor listed under that network.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-10-27",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "Reads misc/wifi/TcpMonitorApInfo.json, written by the TCP monitor in Samsung's Wi-Fi "
                 "service. One row per package listed under a network; a network with no package list "
                 "gives one row with the package cells blank. The meanings below come from three Samsung "
                 "builds decompiled with jadx 1.5.6: G973FXXS9DTK9 (Android 10, wifi-service.jar, SHA-256 "
                 "43016271367f078ea1f605f954c9dbe95430da77b26efff913c3576e88d35705, classes "
                 "com.android.server.wifi.tcp.Wifi*), G991BXXS5DWA4 (Android 13, semwifi-service.jar, "
                 "SHA-256 18da235b0f69d3b746239522f0c403cd865f86df176226e679c7b2e82f43f065) and "
                 "G991BXXU9FWK3 (Android 14, semwifi-service.jar, SHA-256 "
                 "b1213a303cc048b0d781b2692e8251723e41d11fad23e14f1303796928278c55), the last two in "
                 "com.samsung.android.server.wifi.tcp.SemWifi*. Other builds were not decompiled. The "
                 "store is keyed by the SSID string the service read for the connected network, so two "
                 "networks with the same name are one record; SSID is shown as stored, with the double "
                 "quotes the file holds. The connection figures are changed in the service's Wi-Fi "
                 "network callback (SwitchForIndividualAppsService): when a Wi-Fi network becomes "
                 "available the record's count is increased by 1, and when it is lost the whole minutes "
                 "since it became available are added to its time. On the Android 13 and 14 builds the "
                 "record is first copied with a constructor that sets the count from the stored time "
                 "(SemWifiApInfo(SemWifiApInfo)); on the tested images every network on those versions "
                 "with a count above 1 (7 of 7) stored a count exactly 1 more than its time. On Android "
                 "10 the stored record is used without a copy, and none of the 4 networks showed that "
                 "relation. On Android 13 and 14 Accumulated Connection Count is therefore not a number "
                 "of connections. The file is written only when an active monitoring session stops "
                 "(saveTcpMonitorFiles, called from stopTCPMonitoring), so it can lag what the service "
                 "held in memory. The exact sequence that leaves the count 1 above the time was not "
                 "established, and neither connection column should be read as a total of connections or "
                 "of time. Monitoring runs only while the poor-network detection state reported by "
                 "SemWifiConnectivityMonitor is on, the Wi-Fi network is validated, the screen is on and "
                 "the network is in a switchable quality mode (isMonitoringEnabled). That state combines "
                 "a switch with SIM, user and IMS conditions and was not resolved to one user setting, so "
                 "an absent or short file is not evidence that the device did not use Wi-Fi. A package is "
                 "added to a network's list when, with monitoring active, the top activity of the focused "
                 "task changes away from it after a whole minute or more, or monitoring stops while it is "
                 "on top (updateSwitchedPackageInfo). Package Normal Operation Time holds the whole "
                 "minutes counted for it then, added to on later such changes under the conditions in "
                 "updateNormalOperationTime, and set to 0 on one path where the monitor flags the app. It "
                 "is time counted only while monitoring was active, not total use of the app. Package "
                 "Detected Count, Package Last Detected Time and Switch For Individual Apps Detection "
                 "Count change when the monitor flags the foreground app's connection while switching is "
                 "enabled (addSwitchForIndivdiaulAppsDetectionCount); the time is written as device local "
                 "time with no zone ('yyyy-MM-dd HH:mm:ss '). On the tested images Package Detected Count "
                 "held 0 on every row, Package Last Detected Time was empty on every row and Switch For "
                 "Individual Apps Detection Count held 0 on every row, so that path was not exercised. A "
                 "package's entry is removed from every network's list when the service drops it from its "
                 "list of switch-enabled apps (MSG_AP_RESET_DETECTION_HISTORY), and not when the package "
                 "is uninstalled, so a listed package need not still be installed. Both writers omit "
                 "DetectedPackageList when the list is empty; the Android 10 file had none, so on "
                 "galaxys10_a10 Package Name, Package Normal Operation Time and Package Detected Count "
                 "are blank on every row. On the four tested images every SSID in this file was also a "
                 "network saved in WifiConfigStore.xml; whether a forgotten network stays in this file "
                 "was not tested. sharon_a13 and sharon_a14 are extractions of the same device, and three "
                 "of their network records are identical. Not reported: "
                 "misc/wifi/TcpMonitorPackageInfo.json, a per-UID record of installed packages with a "
                 "category and flags, whose counters (DetectedCount, DataUsage, UsagePattern) held 0 on "
                 "all ten images that had it and whose entries the service removes when a package is "
                 "uninstalled; and misc/wifi/TcpMonitorSwitchEnabledUID.xml, which no tested image held. "
                 "TcpMonitorApInfo.json was on galaxys10_a10, samsungs20_a13, sharon_a13 and sharon_a14. "
                 "adams_ss135dl_a13, anne_a15, cookbook_a11, falken_a326u_a13, s20fe_a13 and "
                 "samsunga53_a14 held TcpMonitorPackageInfo.json but not this file.",
        "paths": ('*/misc/wifi/TcpMonitorApInfo.json',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 16 rows",
            "sharon_a13": "Android 13 | 25 rows",
            "sharon_a14": "Android 14 | 47 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import hashlib
import json
import re

from scripts.ilapfuncs import artifact_processor, logfunc

_PACKAGE = re.compile(r'^[A-Za-z]\w*(\.[A-Za-z_]\w*)+$')


def _in_app_folder(parts):
    """True when the path runs through an app's data folder: data/<package>/ or
    user[_de]/<n>/<package>/."""
    for i, part in enumerate(parts):
        if not _PACKAGE.match(part):
            continue
        if i >= 1 and parts[i - 1] == 'data':
            return True
        if i >= 2 and parts[i - 1].isdigit() and parts[i - 2] in ('user', 'user_de'):
            return True
    return False


def _is_store(path):
    """True for <root>/misc/wifi/TcpMonitorApInfo.json outside any app's data folder."""
    parts = path.replace('\\', '/').split('/')
    return (len(parts) >= 4 and parts[-1] == 'TcpMonitorApInfo.json' and parts[-2] == 'wifi'
            and parts[-3] == 'misc' and not _in_app_folder(parts[:-3]))


def _as_stored(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return value


@artifact_processor
def samsungTcpMonitorApInfo(context):
    data_list = []
    sources = []
    seen = set()
    for path in context.get_files_found():
        path = str(path)
        if not _is_store(path):
            continue
        try:
            with open(path, 'rb') as fh:
                raw = fh.read()
            digest = hashlib.sha256(raw).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            records = json.loads(raw.decode('utf-8'))['Data']
        except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as ex:
            logfunc(f'Samsung TcpMonitorApInfo: could not read {context.get_relative_path(path)}: {ex}')
            continue
        sources.append(path)
        for record in records:
            if not isinstance(record, dict):
                logfunc(f'Samsung TcpMonitorApInfo: skipped a non-object record in '
                        f'{context.get_relative_path(path)}')
                continue
            network = (_as_stored(record.get('SSID')),
                       _as_stored(record.get('AccumulatedConnectionTime')),
                       _as_stored(record.get('AccumulatedConnectionCount')),
                       _as_stored(record.get('SwitchForIndividualAppsDetectionCount')))
            packages = [p for p in record.get('DetectedPackageList') or [] if isinstance(p, dict)]
            if not packages:
                data_list.append(('',) + network + ('', '', ''))
                continue
            for package in sorted(packages, key=lambda p: str(p.get('PackageName', ''))):
                data_list.append((_as_stored(package.get('PackageLastDetectedTime')),) + network +
                                 (_as_stored(package.get('PackageName')),
                                  _as_stored(package.get('PackageNormalOperationTime')),
                                  _as_stored(package.get('PackageDetectedCount'))))

    data_headers = ('Package Last Detected Time (as stored, device local)', 'SSID (as stored)',
                    'Accumulated Connection Time (as stored)',
                    'Accumulated Connection Count (as stored)',
                    'Switch For Individual Apps Detection Count', 'Package Name',
                    'Package Normal Operation Time (as stored)', 'Package Detected Count')
    return data_headers, data_list, '\n'.join(sources)
