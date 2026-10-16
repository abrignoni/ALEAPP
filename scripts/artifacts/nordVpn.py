__artifacts_v2__ = {
    "nordvpn_app_events": {
        "name": "NordVPN - App Events",
        "description": "Parses the event records in the queue_elements table of the "
                       "NordVPN Android app's Moose.db, with the local time each records "
                       "and the ISP and network type values each carries, as stored.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "NordVPN",
        "notes": "One row per event record in the queue_elements table. Timestamp is the event's "
                 "own Unix second value "
                 "rendered in UTC, and Local Time is the value the event separately records "
                 "with the device's UTC offset, kept as stored so the offset stays readable. "
                 "What the app does with a row after it is written was not established, so the "
                 "set present is not shown to be a complete history of app use. Event "
                 "names, network type and interface are the app's own labels, as stored. ISP "
                 "and ISP ASN are the values each event carries, reported as stored; whether "
                 "they describe the device's own network was not established. On VPN is the flag "
                 "each event carries; on the tested devices every "
                 "event that carried it recorded false, and no event carried a server "
                 "address, city or country, so these samples hold no record of a VPN connection, "
                 "which is not evidence that none took place. "
                 "Field mapping was done against two private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": (
            '*/com.nordvpn.android/databases/Moose.db*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity"
    },
    "nordvpn_settings": {
        "name": "NordVPN - Settings and State",
        "description": "Parses the NordVPN Android app's connection settings, the last "
                       "recorded connection state and the device and account identifiers "
                       "the app stores.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "NordVPN",
        "notes": "One row per app data directory. Values come from the app's Settings "
                 "database, from the shared context its reporting library keeps, and from "
                 "its own preference files, all read from the same directory. Server "
                 "Catalogue Updated is the ServerUpdateTime value of the LastUpdateEntity table "
                 "in Main.db, read as Unix milliseconds; what the app updates it for was not "
                 "established. The server catalogue itself is a server supplied list of "
                 "servers, "
                 "tens of thousands of rows on the tested devices, and is "
                 "not reported because it records what the service offers rather than "
                 "anything the device did. Last Cache Date and Token Renew are Unix seconds. "
                 "Connection fields are reported as stored. On VPN is the shared context value "
                 "and, when that is empty, vpn_connected from last_known_state.xml. Threat "
                 "Protection is the shared context's user_preferences value and, when that is "
                 "empty, its current_state value. Meshnet is meshnet_enabled from "
                 "last_meshnet_state.xml and, when that is empty, the shared context value. "
                 "On VPN Read From, Threat Protection Read From and Meshnet Read From name the "
                 "stored field each of those three values was read from and are blank when "
                 "neither field held a value; Source Files lists a preference file when it "
                 "supplied one of those values. Those three columns were added after the "
                 "tested devices were examined and were not exercised on them. The "
                 "connection fields were empty on both tested "
                 "devices, where the app recorded that it was not connected and not signed "
                 "in. SIM Country is the plaintext value the app stores beside its location "
                 "record. The location record's own country, latitude, longitude and update "
                 "time are stored in a form this module does not read; the key could not be "
                 "recovered, because the extraction carries no app binary and no derivation "
                 "from the seed the app stores reproduced it, so the cipher and the plaintext "
                 "were not established and those four values are not reported. "
                 "Field mapping was done against two private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": (
            '*/com.nordvpn.android/databases/Settings.db*',
            '*/com.nordvpn.android/databases/Moose.db*',
            '*/com.nordvpn.android/databases/Main.db*',
            '*/com.nordvpn.android/shared_prefs/com.nordvpn.android.*.xml',
            '*/com.nordvpn.android/shared_prefs/com.nordvpn.android[a-z]*.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield"
    },
    "nordvpn_domains": {
        "name": "NordVPN - Stored Domains",
        "description": "Parses the domain names held in the NordVPN Android app's PDP "
                       "database.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "NordVPN",
        "notes": "One row per stored domain. The rows are reported as stored: the database "
                 "records only an identifier and a domain, the extraction carries no app "
                 "binary, and nothing in the extraction states what the app does with them, "
                 "so no purpose is asserted here. On the tested device the list held one "
                 "name on the vendor's own domain and ten others, and the same database "
                 "carried no timestamp, so the rows cannot be placed in time. They are "
                 "reported because they are network names an examiner can look for "
                 "elsewhere. Field mapping was done against a private sample provided by "
                 "Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.nordvpn.android/databases/PDP.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
}

import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.nordvpn.android'
_CONTEXT_PREFIX = 'application.nordvpnapp.config.'
_TYPE_SUFFIX = re.compile(r'\.(value|meta)?\.?_[a-z_]+$')


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context):
    '''{container key: [path]} for the files this artifact matched.

    Every caller iterates the containers rather than taking the first database that
    opens, so a second app data directory contributes its own rows instead of being
    dropped.
    '''
    grouped = {}
    for file_found in unique_files(context):
        grouped.setdefault(_container(context, file_found), []).append(str(file_found))
    return grouped


def _named(paths, name):
    '''The matched paths whose file name is name.'''
    return [path for path in paths if os.path.basename(path) == name]


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


def _prefs(source_path):
    '''{name: text} for an Android shared preferences file.'''
    values = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'NordVPN: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _first_stored(candidates):
    '''(value, origin, path) for the first candidate holding a value, or blanks.

    Each candidate is (value, origin label, source path or None). A blank value is
    passed over, which is the order the columns have always been filled in; the label
    says which stored field the reported value was read from.
    '''
    for value, origin, path in candidates:
        if value not in (None, ''):
            return value, origin, path
    return '', '', None


def _all_prefs(paths):
    '''{file name: {name: text}} for every preference file in one container.'''
    return {os.path.basename(path): _prefs(path)
            for path in paths if path.endswith('.xml')}


def _open(paths, name):
    '''The named database in one container, opened read only, or None.'''
    for path in _named(paths, name):
        try:
            return path, open_sqlite_db_readonly(get_sqlite_db_path(path))
        except sqlite3.Error as ex:
            logfunc(f'NordVPN: could not open {name}: {ex}')
    return None, None


def _rows(database, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    if database is None:
        return []
    try:
        cursor = database.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'NordVPN: could not read from the database: {ex}')
        return []


def _stored(value):
    '''A shared context value rendered as text, with a stored null read as absent.'''
    if value is None:
        return ''
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return str(value)
    if parsed is None:
        return ''
    if isinstance(parsed, bool):
        return str(parsed)
    return str(parsed)


def _context_values(database):
    '''{short key: text} for the reporting library's shared context.

    The stored keys carry a fixed prefix and a type suffix that names the value's type
    rather than the value itself, so both are stripped and the remaining name is what the
    columns are read from. A meta entry keeps its own name, because it holds different
    information from the value beside it.
    '''
    values = {}
    for key, value in _rows(database, 'SELECT key, val FROM shared_context'):
        name = str(key)
        if name.startswith(_CONTEXT_PREFIX):
            name = name[len(_CONTEXT_PREFIX):]
        is_meta = '.meta.' in name or name.endswith('.meta')
        name = _TYPE_SUFFIX.sub('', name)
        if is_meta and not name.endswith('.meta'):
            name = name + '.meta'
        values[name] = _stored(value)
    return values


def _flatten(document, prefix=''):
    '''{dotted key: value} for a nested document, lists kept as stored.'''
    flat = {}
    if isinstance(document, dict):
        for key, value in document.items():
            flat.update(_flatten(value, f'{prefix}.{key}' if prefix else str(key)))
    elif isinstance(document, list):
        flat[prefix] = json.dumps(document)
    else:
        flat[prefix] = document
    return flat


@artifact_processor
def nordvpn_app_events(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        source_path, database = _open(paths, 'Moose.db')
        if database is None:
            continue
        relative = context.get_relative_path(source_path)
        for (stored,) in _rows(database, 'SELECT obj FROM queue_elements'):
            try:
                document = json.loads(stored)
            except (TypeError, ValueError):
                logfunc('NordVPN: a queued event did not parse and was reported as stored')
                document = None
            if not isinstance(document, dict):
                source_files.append(relative)
                data_list.append(('', '', '', '', '', '', '', '', '', '', '', '',
                                  str(stored or ''), relative))
                continue
            flat = _flatten(document)
            event = document.get('event') or {}
            source_files.append(relative)
            data_list.append((
                _seconds(event.get('timestamp')),
                str(event.get('datetime_local') or ''),
                str(event.get('category') or ''),
                str(event.get('group') or ''),
                str(event.get('name') or ''),
                str(flat.get('event.session.count', '')),
                str(flat.get('context.application.nordvpnapp.config.current_state.isp.value', '')),
                str(flat.get('context.application.nordvpnapp.config.current_state.isp_asn.value', '')),
                str(flat.get('context.application.nordvpnapp.config.current_state.is_on_vpn.value', '')),
                str(flat.get('context.device.location.country', '')),
                str(flat.get('context.application.nordvpnapp.config.current_state.mobile_network_type.value', '')),
                str(flat.get('context.device.fp', '')),
                json.dumps(document.get('body')) if document.get('body') is not None else '',
                relative,
            ))
        database.close()

    # Most recent first, with the stored local time breaking ties so the order is the same
    # on every run rather than depending on the order the rows were read.
    data_list.sort(key=lambda row: (str(row[0]), str(row[1])), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Local Time (as stored)',
        'Event Category',
        'Event Group',
        'Event Name',
        'Session Count',
        'ISP',
        'ISP ASN',
        'On VPN (as stored)',
        'Device Country (as stored)',
        'Mobile Network Type (as stored)',
        'Device Fingerprint',
        'Event Body (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def nordvpn_settings(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        settings_path, settings = _open(paths, 'Settings.db')
        moose_path, moose = _open(paths, 'Moose.db')
        main_path, main = _open(paths, 'Main.db')
        preferences = _all_prefs(paths)
        if settings is None and moose is None and not preferences:
            continue

        state = _context_values(moose) if moose is not None else {}

        auto_connect = (_rows(settings, 'SELECT wifiEnabled, mobileEnabled, ethernetEnabled, '
                                        'isAutoConnectEnabled, exceptions FROM AutoConnectEntity')
                        or [(None, None, None, None, None)])[0]
        technology = (_rows(settings, 'SELECT name, technologyId, protocolIds, apiProtocolIds '
                                      'FROM PreferredTechnologyEntity')
                      or [(None, None, None, None)])[0]
        mfa = (_rows(settings, 'SELECT mfaStatus FROM MultiFactorAuthStatusEntity')
               or [(None,)])[0]
        dns = (_rows(settings, 'SELECT customDnsAddresses FROM DnsConfigurationEntity')
               or [(None,)])[0]
        location_preference = (_rows(settings, 'SELECT preferenceType, categoryId, countryId, '
                                               'regionId, serverId FROM ConnectionLocationEntity')
                               or [(None, None, None, None, None)])[0]
        catalogue = (_rows(main, "SELECT value FROM LastUpdateEntity WHERE key = 'ServerUpdateTime'")
                     or [(None,)])[0]

        identifier = preferences.get('com.nordvpn.android.device_unique_identifier.xml', {})
        flavor = preferences.get('com.nordvpn.android.flavor_persistence.xml', {})
        last_known = preferences.get('com.nordvpn.android.last_known_state.xml', {})
        meshnet = preferences.get('com.nordvpn.android.last_meshnet_state.xml', {})
        device_location = preferences.get('com.nordvpn.androiddevice-location.xml', {})
        user_identifier = preferences.get('com.nordvpn.android.userIdentifier.xml', {})
        snooze = preferences.get('com.nordvpn.androidsnooze.xml', {})
        onboarding = preferences.get('com.nordvpn.android.onboarding.xml', {})
        switches = preferences.get('com.nordvpn.android.feature_switch_control.xml', {})

        account = ''
        for name, value in user_identifier.items():
            if name.startswith('userId'):
                account = f'{name}={value}'
                break

        def _pref_path(name, held=tuple(paths)):
            return next((path for path in held if os.path.basename(path) == name), None)

        on_vpn, on_vpn_from, on_vpn_path = _first_stored((
            (state.get('current_state.is_on_vpn', ''),
             'Moose.db shared_context current_state.is_on_vpn', None),
            (last_known.get('vpn_connected', ''),
             'last_known_state.xml vpn_connected',
             _pref_path('com.nordvpn.android.last_known_state.xml')),
        ))
        threat, threat_from, _ = _first_stored((
            (state.get('user_preferences.threat_protection_lite_enabled', ''),
             'Moose.db shared_context user_preferences.threat_protection_lite_enabled', None),
            (state.get('current_state.threat_protection_lite_enabled', ''),
             'Moose.db shared_context current_state.threat_protection_lite_enabled', None),
        ))
        mesh, mesh_from, mesh_path = _first_stored((
            (meshnet.get('meshnet_enabled', ''),
             'last_meshnet_state.xml meshnet_enabled',
             _pref_path('com.nordvpn.android.last_meshnet_state.xml')),
            (state.get('user_preferences.meshnet_enabled', ''),
             'Moose.db shared_context user_preferences.meshnet_enabled', None),
        ))

        relative_paths = [context.get_relative_path(path)
                          for path in (settings_path, moose_path, main_path,
                                       on_vpn_path, mesh_path) if path]
        source_files.extend(relative_paths)
        data_list.append((
            _ms(catalogue[0]),
            _seconds(state.get('current_state.last_cache_date')),
            _seconds(state.get('current_state.token_renew_date')),
            state.get('current_state.is_logged_in', ''),
            on_vpn,
            on_vpn_from,
            state.get('current_state.server_city', ''),
            state.get('current_state.server_country', ''),
            state.get('current_state.server_domain', ''),
            state.get('current_state.server_ip', ''),
            state.get('current_state.server_group', ''),
            state.get('current_state.protocol', ''),
            state.get('current_state.technology', ''),
            state.get('current_state.isp', ''),
            state.get('current_state.isp_asn', ''),
            state.get('current_state.mobile_network_type', ''),
            state.get('current_state.mobile_network_type.meta', ''),
            state.get('current_state.active_network_interface', ''),
            str(technology[0] or ''),
            str(technology[2] or ''),
            str(auto_connect[3] if auto_connect[3] is not None else ''),
            str(auto_connect[0] if auto_connect[0] is not None else ''),
            str(auto_connect[1] if auto_connect[1] is not None else ''),
            str(auto_connect[2] if auto_connect[2] is not None else ''),
            str(auto_connect[4] or ''),
            str(location_preference[0] or ''),
            str(location_preference[1] if location_preference[1] is not None else ''),
            str(mfa[0] or ''),
            str(dns[0] or ''),
            state.get('user_preferences.kill_switch_enabled', ''),
            state.get('user_preferences.connection_preference', ''),
            state.get('user_preferences.consent_level', ''),
            threat,
            threat_from,
            state.get('user_preferences.dark_web_monitor_enabled', ''),
            state.get('user_preferences.post_quantum_enabled', ''),
            mesh,
            mesh_from,
            str(switches.get('scam_call_protection', '')),
            str(device_location.get('sim_countryCode', '')),
            str(device_location.get('source', '')),
            str(identifier.get('IdentifierId_v2', '')),
            account,
            str(flavor.get('flavor', '')),
            str(onboarding.get('onboarding_shown', '')),
            str(snooze.get('snooze_active', '')),
            '; '.join(relative_paths),
        ))
        for database in (settings, moose, main):
            if database is not None:
                database.close()

    data_headers = (
        ('Server Catalogue Updated', 'datetime'),
        ('Last Cache Date', 'datetime'),
        ('Token Renew', 'datetime'),
        'Logged In (as stored)',
        'On VPN (as stored)',
        'On VPN Read From',
        'Server City',
        'Server Country',
        'Server Domain',
        'Server IP',
        'Server Group',
        'Protocol (as stored)',
        'Technology (as stored)',
        'ISP',
        'ISP ASN',
        'Mobile Network Type (as stored)',
        'Mobile Network Detail (as stored)',
        'Active Network Interface (as stored)',
        'Preferred Technology (as stored)',
        'Preferred Protocol IDs (as stored)',
        'Auto Connect Enabled',
        'Auto Connect On Wifi',
        'Auto Connect On Mobile',
        'Auto Connect On Ethernet',
        'Auto Connect Exceptions',
        'Connection Preference Type (as stored)',
        'Connection Category ID (as stored)',
        'Multi Factor Auth Status (as stored)',
        'Custom DNS Addresses',
        'Kill Switch (as stored)',
        'Connection Preference (as stored)',
        'Consent Level (as stored)',
        'Threat Protection (as stored)',
        'Threat Protection Read From',
        'Dark Web Monitor (as stored)',
        'Post Quantum (as stored)',
        'Meshnet (as stored)',
        'Meshnet Read From',
        'Scam Call Protection (as stored)',
        'SIM Country',
        'Location Source (as stored)',
        'Device Identifier',
        'Account Identifier',
        'Install Flavor',
        'Onboarding Shown',
        'Snooze Active',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def nordvpn_domains(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        source_path, database = _open(paths, 'PDP.db')
        if database is None:
            continue
        relative = context.get_relative_path(source_path)
        for identifier, domain in _rows(database, 'SELECT id, domain FROM domains'):
            source_files.append(relative)
            data_list.append((
                str(identifier if identifier is not None else ''),
                str(domain or ''),
                relative,
            ))
        database.close()

    data_headers = (
        'ID',
        'Domain',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
