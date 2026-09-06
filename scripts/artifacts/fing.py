__artifacts_v2__ = {
    "fing_app_state": {
        "name": "Fing App State and Last Network",
        "description": "What the Fing app recorded about itself and the network it last scanned",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Fing",
        "sample_data": {
            "emu_a15_oss_v16": "Fing 12.13.3 | 10 rows",
        },
        "notes": "One row per value read from the app's own preference files and from "
                 "files/network.last. This artifact is deliberately narrow, and the reason is "
                 "worth stating plainly: **on the tested device Fing wrote no list of the devices "
                 "it discovered**. A scan found four and displayed them, and nothing about "
                 "those four exists anywhere in the container afterwards. No account was signed "
                 "in, and whether signing in changes that was not tested, so the absence is "
                 "reported for the anonymous case only. The app's databases directory holds only Firebase "
                 "stores, and the two large files in its cache, AndroidDeviceDB and EthVendorDB, "
                 "are vendor and device catalogues the app downloads, which are server data and "
                 "are not reported here as anything the device did. "
                 "What does survive is this: Last Scan is uiprefs last_scan_date and Discovery "
                 "Count is its discovery_count, both written by the app itself. First Used, Last "
                 "Used and App Version come from marketprefs. Privacy Agreed is that file's "
                 "privacy.agreed key, which records when the policy was accepted on this device. "
                 "All four times are Unix milliseconds and are reported as UTC. "
                 "BSSID and Network Id come from files/network.last, a Java properties file the "
                 "app writes for the network it last worked with; the BSSID identifies that "
                 "wireless network, and Current Wifi is the flag stored beside it. The colons in "
                 "the stored BSSID are backslash escaped by the properties writer and are "
                 "unescaped here. "
                 "Values are reported as stored, one per row, so nothing is inferred from them. "
                 "A row dates app activity, not a person's presence on that network.",
        "paths": ('*/com.overlook.android.fing/shared_prefs/uiprefs.xml',
                  '*/com.overlook.android.fing/shared_prefs/marketprefs.xml',
                  '*/com.overlook.android.fing/files/network.last'),
        "output_types": "standard",
        "artifact_icon": "wifi",
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

# key in the app's file -> (label, is it a Unix millisecond time)
UI_KEYS = {'last_scan_date': ('Last Scan', True), 'discovery_count': ('Discovery Count', False)}
MARKET_KEYS = {
    'app.firstused': ('First Used', True),
    'app.lastused': ('Last Used', True),
    'app.versionlastused': ('App Version', False),
    'rate.numberofruns': ('Number Of Runs', False),
}
NETWORK_KEYS = {'bssid': 'BSSID', 'networkid': 'Network Id', 'currentwifi': 'Current Wifi'}


def _files(context, tail):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(tail)]


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value // 1000)
    except (OverflowError, OSError, ValueError):
        return ''


def _pref_values(path):
    """{name: text} for every simple value in an Android preferences XML."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'Fing: could not read {os.path.basename(path)}: {error}')
        return {}
    out = {}
    for node in root:
        name = node.get('name')
        if not name:
            continue
        out[name] = node.get('value') if node.get('value') is not None else (node.text or '')
    return out


def _properties(path):
    """{key: value} for a Java properties file, with the writer's escaping undone."""
    out = {}
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, value = line.partition('=')
                out[key.strip()] = value.strip().replace('\\:', ':').replace('\\=', '=')
    except OSError as error:
        logfunc(f'Fing: could not read {os.path.basename(path)}: {error}')
    return out


@artifact_processor
def fing_app_state(context):
    data_list = []
    sources = []

    def add(label, value, path, when=''):
        if value in (None, ''):
            return
        data_list.append((label, value, when, context.get_relative_path(path)))
        if path not in sources:
            sources.append(path)

    for path in _files(context, 'shared_prefs/uiprefs.xml'):
        values = _pref_values(path)
        for key, (label, is_time) in UI_KEYS.items():
            if key in values:
                add(label, values[key], path, _ms(values[key]) if is_time else '')
    for path in _files(context, 'shared_prefs/marketprefs.xml'):
        values = _pref_values(path)
        for key, (label, is_time) in MARKET_KEYS.items():
            if key in values:
                add(label, values[key], path, _ms(values[key]) if is_time else '')
        for key, value in values.items():
            if key.startswith('privacy.agreed'):
                add('Privacy Agreed', value, path, _ms(value))
    for path in _files(context, 'files/network.last'):
        values = _properties(path)
        for key, label in NETWORK_KEYS.items():
            if key in values:
                add(label, values[key], path)

    data_headers = ('Item', 'Value (as stored)', ('Time', 'datetime'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)
