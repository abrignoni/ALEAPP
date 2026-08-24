__artifacts_v2__ = {
    "outlook_accounts": {
        "name": "Outlook - Accounts",
        "description": "Parses the signed in account recorded by the OneAuth component of "
                       "the Microsoft Outlook Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Outlook",
        "notes": "Each entry in the OneAuth accounts preferences file holds a JSON value "
                 "carrying the account identifiers and, on some entries, an "
                 "additional_properties member holding the claims of a token the component "
                 "had cached. Issued At, Not Before and Expires come from the iat, nbf and "
                 "exp claims and are Unix seconds: the values are ten digits and resolve "
                 "inside the range covered by the app's own logs, where a millisecond "
                 "reading would place them in 1970. On the sample carrying claims, Issued "
                 "At falls five minutes before the officeConfigLastFetchedTime value "
                 "reported by the settings artifact, which was read independently. The aio "
                 "claim is opaque token material and is not written to the report. Account "
                 "type, age group, sovereignty and association status are reported as "
                 "stored. Reading a claim here is not evidence the token was accepted by "
                 "any service. This file records the credential broker's view of the "
                 "signed in account and is separate from the Outlook account store in "
                 "acompliAcct.db. Field mapping was done against private samples provided "
                 "by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.microsoft.office.outlook/shared_prefs/com.microsoft.oneauth.accounts.xml',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "user"
    },
    "outlook_app_versions": {
        "name": "Outlook - App Version History",
        "description": "Parses the version and storage boot lines the Microsoft Outlook "
                       "Android app writes to its appUpdates log.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Outlook",
        "notes": "The appUpdates log is tab delimited and carries a level, an ISO 8601 "
                 "timestamp with a UTC offset, a correlation identifier, a thread, a "
                 "component and a message. Three message forms were seen across the tested "
                 "samples: one naming the app version and version code the app was "
                 "initialising, one reporting the storage boot and whether storage "
                 "migrated, and one marking a migration start. The version and version code "
                 "are taken from the first form and the migration flag from the second; "
                 "other message forms are reported with their text as stored and no version "
                 "parsed. The correlation identifier matched the pref_install_id value in "
                 "the app's own preferences on each tested sample, so it is reported as the "
                 "install identifier. Timestamps are converted from the offset the line "
                 "carries. A line here records what the app logged when it initialised, not "
                 "an interaction. Field mapping was done against private samples provided "
                 "by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.microsoft.office.outlook/app_logs/appUpdates.log*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "package"
    },
    "outlook_installation": {
        "name": "Outlook - Installation",
        "description": "Parses the install identifier and the version names and codes the "
                       "Microsoft Outlook Android app records in its preferences.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Outlook",
        "notes": "The versions preferences file holds an initial, a previous and a last run "
                 "version name and version code. The install identifier comes from the "
                 "pref_install_id value in the acompli preferences file and matched the "
                 "correlation identifier carried by the app's own log lines on each tested "
                 "sample. Neither file carries a timestamp, so the row is reported without "
                 "one; the version history artifact carries the timestamped lines. Values "
                 "are reported as stored. Field mapping was done against private samples "
                 "provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.microsoft.office.outlook/shared_prefs/versions.xml',
            '*/com.microsoft.office.outlook/shared_prefs/acompli_prefs.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smartphone"
    },
    "outlook_settings": {
        "name": "Outlook - Settings",
        "description": "Parses the settings the Microsoft Outlook Android app records in "
                       "its own preferences file.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Outlook",
        "notes": "Each preference is reported as a row carrying its key, the type the file "
                 "declares for it and its value as stored. The tested samples ranged from "
                 "7 to 85 keys and the sets differ between them, so no key is required to "
                 "be present. Two keys hold epoch values and they do not share a unit: "
                 "officeConfigLastFetchedTime is thirteen digits and is Unix milliseconds, "
                 "and wearUpsellLastCheck is ten digits and is Unix seconds. Both were "
                 "established from the values themselves, each resolving inside the range "
                 "covered by the app's own logs on the sample carrying it while the other "
                 "unit did not, and the milliseconds reading agrees to within five minutes "
                 "with a token claim read independently by the accounts artifact. A "
                 "Resolved Timestamp is emitted for those two keys only; any other key is "
                 "reported with its value as stored and no conversion. Keys under the "
                 "NetworkOverrides and DynamicConfigSettings branches are configuration "
                 "the app received rather than choices made on the device. Field mapping "
                 "was done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.microsoft.office.outlook/shared_prefs/com.microsoft.office.outlook_preferences.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
}

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

_ACCOUNTS_PREFS = 'com.microsoft.oneauth.accounts.xml'
_VERSIONS_PREFS = 'versions.xml'
_ACOMPLI_PREFS = 'acompli_prefs.xml'
_SETTINGS_PREFS = 'com.microsoft.office.outlook_preferences.xml'

# The two settings keys whose epoch unit was established from the sample values. Anything
# not named here is reported as stored rather than guessed at, since the two keys already
# in this file disagree on unit.
_SETTING_EPOCH_UNITS = {
    'officeConfigLastFetchedTime': 1000,
    'wearUpsellLastCheck': 1,
}

# The claims read out of a OneAuth entry's additional_properties member. aio is deliberately
# absent: it is opaque token material and does not belong in a report.
_CLAIM_FIELDS = ('oid', 'tid', 'sub', 'preferred_username', 'iss', 'aud', 'graph_url',
                 'ver', 'tr_flow_status')


def _files_named(context, name):
    '''The matched files whose basename is name, one per storage view.'''
    return [path for path in unique_files(context)
            if os.path.basename(path) == name]


def _files_starting(context, prefix):
    '''The matched files whose basename starts with prefix, one per storage view.

    The app rotates its logs to <name>.log.1 and upward, so the glob has to accept a
    suffix and the basename test cannot be an equality.
    '''
    return [path for path in unique_files(context)
            if os.path.basename(path).startswith(prefix)]


def _epoch(value, divisor):
    '''An epoch value as a UTC datetime, or '' when absent or unparsable.

    Built by adding a timedelta to the epoch rather than through convert_unix_ts_to_utc,
    which sizes its input with math.log10 and so raises on a negative, and rather than
    through datetime.fromtimestamp, which raises on Windows for any value before 1970.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    try:
        return _EPOCH + timedelta(seconds=value / divisor)
    except (OverflowError, OSError, ValueError):
        return ''


def _prefs_entries(source_path):
    '''(name, type, value) for each entry of an Android shared preferences file.

    A scalar carries its value in a value attribute and a string carries it as text, so
    both are read. Returns an empty list when the file does not parse.
    '''
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
        return []
    entries = []
    for element in root:
        value = element.get('value')
        if value is None:
            value = element.text or ''
        entries.append((element.get('name') or '', element.tag, value))
    return entries


def _prefs_map(source_path):
    '''The entries of a shared preferences file as a name to value mapping.'''
    return {name: value for name, _, value in _prefs_entries(source_path)}


def _log_lines(source_path):
    '''(level, timestamp, correlation id, thread, component, message) per log line.

    The app writes these logs tab delimited with six fields. Lines that do not carry six
    fields are skipped, and a continuation line of a wrapped message is one of those.
    '''
    try:
        with open(source_path, 'r', encoding='utf-8', errors='replace') as handle:
            raw = handle.read()
    except OSError as ex:
        logfunc(f'Could not read {os.path.basename(source_path)}: {ex}')
        return
    for line in raw.splitlines():
        fields = line.split('\t')
        if len(fields) < 6:
            continue
        yield tuple(field.strip() for field in fields[:6])


def _log_timestamp(value):
    '''A log line's ISO 8601 timestamp as a UTC datetime, or '' when it does not parse.

    The app writes the offset as +0000 rather than +00:00, which fromisoformat does not
    accept before Python 3.11, so the colon is inserted before parsing.
    '''
    text = (value or '').strip()
    if len(text) > 5 and (text[-5] in '+-') and text[-5:].replace('+', '').replace('-', '').isdigit():
        text = f'{text[:-2]}:{text[-2:]}'
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return ''
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _claims(entry):
    '''The additional_properties member of a OneAuth entry as a mapping.'''
    raw = entry.get('additional_properties')
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


@artifact_processor
def outlook_accounts(context):
    data_list = []
    sources = []

    for source_path in _files_named(context, _ACCOUNTS_PREFS):
        relative_path = context.get_relative_path(source_path)
        rows = 0
        for name, _, value in _prefs_entries(source_path):
            try:
                entry = json.loads(value)
            except (TypeError, ValueError):
                logfunc(f'OneAuth entry {name} in {os.path.basename(source_path)} was not JSON')
                continue
            if not isinstance(entry, dict):
                continue
            claims = _claims(entry)
            data_list.append((
                _epoch(claims.get('iat'), 1),
                _epoch(claims.get('nbf'), 1),
                _epoch(claims.get('exp'), 1),
                entry.get('email', ''),
                entry.get('login_name', ''),
                claims.get('preferred_username', ''),
                entry.get('display_name', ''),
                entry.get('first_name', ''),
                entry.get('last_name', ''),
                entry.get('phone_number', ''),
                entry.get('birthday', ''),
                entry.get('age_group', ''),
                entry.get('location', ''),
                entry.get('account_type', ''),
                entry.get('home_account_id', ''),
                entry.get('id', ''),
                entry.get('provider_id', ''),
                claims.get('oid', ''),
                claims.get('tid', ''),
                claims.get('sub', ''),
                entry.get('realm', ''),
                entry.get('realm_name', ''),
                entry.get('authority', ''),
                claims.get('iss', ''),
                claims.get('aud', ''),
                claims.get('graph_url', ''),
                entry.get('sovereignty', ''),
                entry.get('telemetry_region', ''),
                entry.get('association_status', ''),
                entry.get('onprem_sid', ''),
                entry.get('password_change_url', ''),
                claims.get('ver', ''),
                claims.get('tr_flow_status', ''),
                name,
                relative_path,
            ))
            rows += 1
        if rows:
            sources.append(source_path)

    data_headers = (
        ('Token Issued At', 'datetime'),
        ('Token Not Before', 'datetime'),
        ('Token Expires', 'datetime'),
        'Email',
        'Login Name',
        'Preferred Username',
        'Display Name',
        'First Name',
        'Last Name',
        'Phone Number',
        'Birthday (as stored)',
        'Age Group (as stored)',
        'Location (as stored)',
        'Account Type (as stored)',
        'Home Account ID',
        'Account ID',
        'Provider ID',
        'Object ID',
        'Tenant ID',
        'Subject',
        'Realm',
        'Realm Name',
        'Authority',
        'Issuer',
        'Audience',
        'Graph URL',
        'Sovereignty (as stored)',
        'Telemetry Region (as stored)',
        'Association Status (as stored)',
        'On Premises SID',
        'Password Change URL',
        'Claims Version (as stored)',
        'Token Flow Status (as stored)',
        'Preference Key',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def outlook_app_versions(context):
    data_list = []
    sources = []

    for source_path in _files_starting(context, 'appUpdates.log'):
        relative_path = context.get_relative_path(source_path)
        rows = 0
        for level, raw_time, correlation, thread, component, message in _log_lines(source_path):
            version = ''
            version_code = ''
            migrated = ''
            event = message
            if message.startswith('Initiate hx for '):
                event = 'Initiate hx'
                remainder = message[len('Initiate hx for '):]
                parts = [part.strip() for part in remainder.split(',')]
                version = parts[0] if parts else ''
                version_code = parts[1] if len(parts) > 1 else ''
            elif message.startswith('Store boot complete'):
                event = 'Store boot complete'
                marker = 'didStorageMigrate='
                if marker in message:
                    migrated = message.split(marker, 1)[1].rstrip(')').strip()
            data_list.append((
                _log_timestamp(raw_time),
                event,
                version,
                version_code,
                migrated,
                level,
                thread,
                component,
                correlation.strip('[]').replace('ci=', ''),
                message,
                relative_path,
            ))
            rows += 1
        if rows:
            sources.append(source_path)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Event',
        'App Version',
        'App Version Code',
        'Storage Migrated (as stored)',
        'Log Level (as stored)',
        'Thread',
        'Component',
        'Install ID',
        'Message',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def outlook_installation(context):
    data_list = []
    sources = []

    # The install identifier and the version names live in two preferences files that sit
    # beside each other, so they are paired on the directory holding them.
    install_ids = {}
    for source_path in _files_named(context, _ACOMPLI_PREFS):
        value = _prefs_map(source_path).get('pref_install_id', '')
        if value:
            install_ids[os.path.dirname(source_path)] = (value, source_path)

    for source_path in _files_named(context, _VERSIONS_PREFS):
        values = _prefs_map(source_path)
        if not values:
            continue
        install_id, install_source = install_ids.get(os.path.dirname(source_path), ('', None))
        data_list.append((
            install_id,
            values.get('initialVersionName', ''),
            values.get('initialVersionCode', ''),
            values.get('previousVersionName', ''),
            values.get('previousVersionCode', ''),
            values.get('lastRunVersionName', ''),
            values.get('lastRunVersionCode', ''),
            context.get_relative_path(source_path),
        ))
        sources.append(source_path)
        if install_source:
            sources.append(install_source)

    data_headers = (
        'Install ID',
        'Initial Version Name',
        'Initial Version Code',
        'Previous Version Name',
        'Previous Version Code',
        'Last Run Version Name',
        'Last Run Version Code',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def outlook_settings(context):
    data_list = []
    sources = []

    for source_path in _files_named(context, _SETTINGS_PREFS):
        relative_path = context.get_relative_path(source_path)
        rows = 0
        for name, value_type, value in _prefs_entries(source_path):
            divisor = _SETTING_EPOCH_UNITS.get(name)
            data_list.append((
                _epoch(value, divisor) if divisor else '',
                name,
                value_type,
                value,
                relative_path,
            ))
            rows += 1
        if rows:
            sources.append(source_path)

    data_headers = (
        ('Resolved Timestamp', 'datetime'),
        'Setting',
        'Type',
        'Value (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
