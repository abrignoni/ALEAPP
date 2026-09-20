__artifacts_v2__ = {
    "cloudflare_warp_registration": {
        "name": "Cloudflare 1.1.1.1 WARP Registration and State",
        "description": "The WARP registration this device holds and the VPN state the app recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Cloudflare WARP",
        "sample_data": {
            "emu_a15_oss_v16": "1.1.1.1 WARP 6.38.9 | 12 rows",
        },
        "notes": "One row per value read from "
                 "com.cloudflare.onedotonedotonedotone/shared_prefs/"
                 "com.cloudflare.onedotonedotonedotone_preferences.xml, ; no database of the "
                 "app's own was found in its container on the tested image. Registration Id, "
                 "Account Id and Account Type are reported as stored; Account Type read 'free' "
                 "on the tested image. Terms Accepted and Registration Executed are ISO 8601 "
                 "strings that carry their own UTC offset, so they are reported exactly as "
                 "stored and need no conversion; on the tested device both ended in -04:00. VPN "
                 "Profile Installed, Service Running, Auto Connect and Tunnel Protocol are the "
                 "app's own flags, reported as stored. Tunnel Protocol read 'masque'. Installed "
                 "By is the installer package name the app recorded, as stored. **The private "
                 "key is deliberately not reported.** The preferences file also holds "
                 "warp_private_key, and a private key has no place in a forensic artifact; its "
                 "presence is noted here so an examiner knows it exists in the file, and its "
                 "value is left there. The public key and the tunnel peer configuration are not "
                 "reported either, being long key material of no evidential use on their own. "
                 "What a row supports is bounded: these values are the registration and tunnel "
                 "settings the preferences file held at acquisition. They are "
                 "current state, not history, so they do not say when the tunnel went up or "
                 "down. "
                 "**The app does write timestamped logs, and they are not parsed here.** Under "
                 "cache/logs it keeps a console log and a native tunnel log; on the tested "
                 "device those were 8.9 MB and 3.1 MB, the console log spanning about eight "
                 "hours with ISO 8601 timestamps that carry their own offset, and holding "
                 "13,301 NetworkChangeReceiver entries alongside WarpTunnel, registration and "
                 "autostart lines. An examiner chasing when the device was on which network, or "
                 "when the tunnel restarted, should read those files; this artifact does not, "
                 "and saying so is the point, because their being in cache makes them easy to "
                 "overlook.",
        "paths": ('*/com.cloudflare.onedotonedotonedotone/shared_prefs/'
                  'com.cloudflare.onedotonedotonedotone_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "shield",
    },
}

import json
import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

PREFS_SUFFIX = ('com.cloudflare.onedotonedotonedotone/shared_prefs/'
                'com.cloudflare.onedotonedotonedotone_preferences.xml')
# Reported directly. Key material is deliberately absent from this map.
SIMPLE = {
    'warp_registration_id': 'Registration Id',
    'terms_acceptance_date': 'Terms Accepted',
    'registration_data_exec_timestamp': 'Registration Executed',
    'selected_tunnel_protocol': 'Tunnel Protocol',
    'vpn_profile_installed': 'VPN Profile Installed',
    'is_service_running': 'Service Running',
    'auto_connect': 'Auto Connect',
    'installer_package_name': 'Installed By',
    'onboardingstatus': 'Onboarding Complete',
}


def _prefs_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(PREFS_SUFFIX)]


def _values(path):
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'Cloudflare WARP: could not read {os.path.basename(path)}: {error}')
        return {}
    out = {}
    for node in root:
        name = node.get('name')
        if not name:
            continue
        out[name] = node.get('value') if node.get('value') is not None else (node.text or '')
    return out


def _account(raw):
    """(account id, account type) from the warp_account JSON, blanks when it will not read."""
    try:
        parsed = json.loads(raw or '')
    except (TypeError, ValueError):
        return '', ''
    if not isinstance(parsed, dict):
        return '', ''
    return str(parsed.get('id') or ''), str(parsed.get('account_type') or '')


@artifact_processor
def cloudflare_warp_registration(context):
    data_list = []
    sources = []
    for path in _prefs_files(context):
        values = _values(path)
        if not values:
            continue
        rows = []
        for key, label in SIMPLE.items():
            if values.get(key) not in (None, ''):
                rows.append((label, values[key].strip('"')))
        account_id, account_type = _account(values.get('warp_account'))
        if account_id:
            rows.append(('Account Id', account_id))
        if account_type:
            rows.append(('Account Type', account_type))
        if values.get('warp_private_key'):
            rows.append(('Private Key', 'present in the preferences file, not reported here'))
        for label, value in rows:
            data_list.append((label, value, context.get_relative_path(path)))
        if rows and path not in sources:
            sources.append(path)

    data_headers = ('Item', 'Value (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
