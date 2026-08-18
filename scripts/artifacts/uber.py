__artifacts_v2__ = {
    "uber_account": {
        "name": "Uber - Account",
        "description": "Parses the rider account record cached by the Uber Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Read from the app's base key value store. Values are stored as JSON preceded by a "
                 "single byte, which held 0x2d on every file in the tested sample; the parser reads from "
                 "the first JSON token. The two timestamps are the lastModifiedTimeMs and originTimeMs "
                 "members of the record's own meta object, in Unix milliseconds. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/com.ubercab/files/base-key-value-store/realtime-demo_KEY_RIDER',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "uber_locations": {
        "name": "Uber - Locations",
        "description": "Parses cached location records from the Uber Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Three record types are reported and the Record Type column says which store each row "
                 "came from. CACHED_UBER_LOCATION is a protobuf carrying no schema; field 2>1 and field "
                 "2>2 are reported as latitude and longitude because they differ by less than 0.0001 "
                 "degree from the coordinates stored as named JSON members in "
                 "KEY_TARGET_LOCATION_SYNCED, and field 1>1 is reported as a Unix millisecond timestamp "
                 "because it falls within one second of the lastModifiedTimeMs recorded by other stores "
                 "in the same sample. No source was found for the record's remaining fields, so they are "
                 "reported as stored under their field numbers. KEY_TARGET_LOCATION_SYNCED carries "
                 "coordinates with no timestamp. The home screen layout record carries the coordinates "
                 "its request was made from together with its own creation and expiration times. Field "
                 "mapping was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/com.ubercab/files/simplestore/*/CACHED_UBER_LOCATION',
            '*/com.ubercab/files/base-key-value-store/realtime-demo_KEY_TARGET_LOCATION_SYNCED',
            '*/com.ubercab/files/simplestore/home_screen_simple_store_scope/home_screen_layout_simple_store_key',
        ),
        "output_types": "all",
        "artifact_icon": "map-pin"
    },
    "uber_shortcuts": {
        "name": "Uber - Suggested Destinations",
        "description": "Parses the shortcuts cache, which holds destinations offered to the rider.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "The cache is keyed by a cell identifier that is reported as stored. Each entry carries "
                 "a timestamp in Unix milliseconds, the coordinates the entry was triggered from, and a "
                 "list of destinations. Latitude and Longitude are the destination coordinates. Presence "
                 "of a destination in this cache does not establish that the rider selected or travelled "
                 "to it. Field mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.ubercab/files/base-key-value-store/ShortcutsCache_CACHED_SHORTCUTS_MAP_KEY',),
        "output_types": "all",
        "artifact_icon": "navigation"
    },
    "uber_payment_profiles": {
        "name": "Uber - Payment Profiles",
        "description": "Parses the payment profiles cached by the Uber Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Status, token type, use case and authentication type are reported as stored. The "
                 "supportedUseCases member is a list of opaque identifiers and is reported as a count "
                 "only. Field mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.ubercab/files/base-key-value-store/payments_KEY_PROFILES',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "credit-card"
    },
    "uber_city": {
        "name": "Uber - City",
        "description": "Parses the city record cached by the Uber Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "The record describes the service area the app last loaded products for. Vehicle views "
                 "are reported as a count and a comma separated list of the identifiers the record "
                 "orders them by. Field mapping was done against a private sample provided by Mattia; no "
                 "sample data is recorded for it.",
        "paths": ('*/com.ubercab/files/base-key-value-store/realtime-demo_KEY_CITY',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    "uber_sessions": {
        "name": "Uber - Sessions",
        "description": "Parses session identifiers and token expiry times from the Uber Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Token and session values held in the shared preferences are reported by presence and "
                 "expiry time; the token strings themselves are not written to the report. "
                 "session_LAST_SESSION stores sessionStartTimeMs in Unix milliseconds. Its "
                 "sessionBackgroundedTimeNanos member is reported as stored and not converted: in the "
                 "tested sample it was exactly sessionStartTimeMs multiplied by one million, which one "
                 "sample is not enough to establish as a wall clock value rather than an uptime value. "
                 "Field mapping was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/com.ubercab/files/base-key-value-store/session_LAST_SESSION',
            '*/com.ubercab/files/base-key-value-store/realtime-demo_KEY_CLIENT_STATUS',
            '*/com.ubercab/shared_prefs/oauth_tokens.xml',
            '*/com.ubercab/shared_prefs/unified_session_swap_store.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock"
    },
    "uber_telemetry": {
        "name": "Uber - Telemetry Messages",
        "description": "Parses queued telemetry messages from the Uber Android message database.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Rows are messages the app had queued for upload. Each content payload carries a "
                 "contextual_data.prod_meta block describing the app, device, carrier, network, city and "
                 "session at the time the message was sealed. createdAt and createdAtNtp are the table's "
                 "own columns in Unix milliseconds; createdAtNtp was empty on every row of the tested "
                 "sample. The message_type value is reported as stored. Field mapping was done against a "
                 "private sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/com.ubercab/databases/ur_message.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "activity"
    },
    "uber_cached_images": {
        "name": "Uber - Cached Images",
        "description": "Recovers images from the Uber Android app image cache.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Each cache entry is a pair of files sharing a base name: a .0 metadata file whose "
                 "first two lines are Unix millisecond timestamps and which also carries the stored HTTP "
                 "response headers, and a .1 file holding the bytes. The entry base name is a 64 "
                 "character hex string reported as stored; it did not reproduce as MD5, SHA-1 or SHA-256 "
                 "of the one image URL recoverable from the tested sample, and the cache carries no "
                 "journal mapping entries to URLs, so no source URL is reported. Media type is taken "
                 "from the bytes rather than from the stored content-type header. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded for it.",
        "paths": ('*/com.ubercab/cache/image_cache/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image"
    },
    "uber_settings": {
        "name": "Uber - App Settings",
        "description": "Parses assorted settings and consent records from the Uber Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Uber",
        "notes": "Values are reported as stored. Absence of a key is not evidence a feature was unused "
                 "or a setting was never changed. Field mapping was done against a private sample "
                 "provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.ubercab/files/base-key-value-store/location_sharing_PERMISSION',
            '*/com.ubercab/files/base-key-value-store/mode_activation_ACTIVATED_MODES',
            '*/com.ubercab/files/base-key-value-store/consent-and-copy_USER_CONSENT',
            '*/com.ubercab/files/base-key-value-store/push_registration_KEY_REGISTRATION_ID',
            '*/com.ubercab/files/base-key-value-store/push_registration_KEY_REGISTERED_APP_VERSION',
            '*/com.ubercab/files/base-key-value-store/last-selected-prod_pkg_KEY_LAST_SELECTED_VEHICLE_HASH',
            '*/com.ubercab/files/simplestore/*/language_detected_store_key',
            '*/com.ubercab/files/simplestore/*/user_uuid',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
}

import json
import os
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)

_JSON_STARTS = (0x7b, 0x5b, 0x22)  # '{', '[', '"'


def _load_kv_json(file_found):
    """JSON from a base key value store file, skipping the leading prefix byte(s)."""
    try:
        with open(file_found, 'rb') as handle:
            raw = handle.read()
    except OSError as ex:
        logfunc(f'Could not read {file_found}: {ex}')
        return None

    start = next((i for i, b in enumerate(raw[:8]) if b in _JSON_STARTS), None)
    if start is None:
        return None
    try:
        return json.loads(raw[start:].decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as ex:
        logfunc(f'Could not decode JSON from {file_found}: {ex}')
        return None


def _load_simplestore_json(file_found):
    """JSON from a simple store file. Text in these files is UTF-16 big endian."""
    try:
        with open(file_found, 'rb') as handle:
            raw = handle.read()
    except OSError as ex:
        logfunc(f'Could not read {file_found}: {ex}')
        return None

    for encoding in ('utf-16-be', 'utf-8'):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        text = text.lstrip('\x00').strip()
        if not text:
            continue
        start = next((i for i, c in enumerate(text[:8]) if c in '{["'), None)
        if start is None:
            # Not every value is JSON. Bare strings are stored unquoted.
            return text
        try:
            return json.loads(text[start:])
        except json.JSONDecodeError:
            return text
    return None


def _ms(value):
    """A Unix millisecond value as a UTC datetime, or '' when it is absent or zero."""
    try:
        value = int(float(value))
    except (TypeError, ValueError):
        return ''
    return convert_unix_ts_to_utc(value) if value else ''


def _iso(value):
    """An ISO 8601 timestamp string as a UTC datetime, or the value unchanged."""
    if not value or not isinstance(value, str):
        return ''
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_varint(buffer, index):
    result = shift = 0
    while index < len(buffer):
        byte = buffer[index]
        index += 1
        result |= (byte & 0x7f) << shift
        if not byte & 0x80:
            return result, index
        shift += 7
    raise ValueError('truncated varint')


def _parse_protobuf(buffer):
    """{field number: value} for one protobuf message. Length delimited fields stay raw."""
    fields = {}
    index = 0
    while index < len(buffer):
        try:
            key, index = _read_varint(buffer, index)
        except ValueError:
            break
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, index = _read_varint(buffer, index)
        elif wire == 5:
            value = struct.unpack('<f', buffer[index:index + 4])[0]
            index += 4
        elif wire == 1:
            value = struct.unpack('<Q', buffer[index:index + 8])[0]
            index += 8
        elif wire == 2:
            length, index = _read_varint(buffer, index)
            value = buffer[index:index + length]
            index += length
        else:
            break
        fields[number] = value
    return fields


def _as_stored(fields, skip):
    """The fields not read by name, rendered as 'f<number>=<value>' for reporting."""
    parts = []
    for number in sorted(fields):
        if number in skip:
            continue
        value = fields[number]
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8')
            except UnicodeDecodeError:
                value = value.hex()
        elif isinstance(value, float):
            value = round(value, 6)
        parts.append(f'f{number}={value}')
    return '; '.join(parts)


@artifact_processor
def uber_account(context):
    data_list = []
    source_path = ''

    for file_found in unique_files(context):
        record = _load_kv_json(file_found)
        if not isinstance(record, dict) or 'uuid' not in record:
            continue
        source_path = file_found
        meta = record.get('meta') or {}
        data_list.append((
            _ms(meta.get('lastModifiedTimeMs')),
            _ms(meta.get('originTimeMs')),
            record.get('uuid', ''),
            record.get('firstName', ''),
            record.get('lastName', ''),
            record.get('email', ''),
            record.get('mobileCountryIso2', ''),
            record.get('mobileDigits', ''),
            record.get('hasConfirmedMobileStatus', ''),
            record.get('isAdmin', ''),
            record.get('hasNoPassword', ''),
            record.get('pictureUrl', ''),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Last Modified', 'datetime'),
        ('Origin Time', 'datetime'),
        'Rider UUID',
        'First Name',
        'Last Name',
        'Email',
        'Mobile Country ISO2',
        ('Mobile Digits', 'phonenumber'),
        'Has Confirmed Mobile (as stored)',
        'Is Admin (as stored)',
        'Has No Password (as stored)',
        'Picture URL',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def uber_locations(context):
    data_list = []
    sources = []

    for file_found in unique_files(context):
        name = os.path.basename(file_found)

        if name == 'CACHED_UBER_LOCATION':
            try:
                with open(file_found, 'rb') as handle:
                    fields = _parse_protobuf(handle.read())
            except OSError as ex:
                logfunc(f'Could not read {file_found}: {ex}')
                continue
            timestamp = ''
            if isinstance(fields.get(1), bytes):
                timestamp = _ms(_parse_protobuf(fields[1]).get(1))
            coordinates = _parse_protobuf(fields[2]) if isinstance(fields.get(2), bytes) else {}
            latitude = coordinates.get(1, '')
            longitude = coordinates.get(2, '')
            data_list.append((
                timestamp,
                round(latitude, 7) if isinstance(latitude, float) else '',
                round(longitude, 7) if isinstance(longitude, float) else '',
                'CACHED_UBER_LOCATION',
                '',
                _as_stored(fields, skip={1, 2}),
                context.get_relative_path(file_found),
            ))
            sources.append(file_found)

        elif name == 'realtime-demo_KEY_TARGET_LOCATION_SYNCED':
            record = _load_kv_json(file_found)
            if not isinstance(record, dict):
                continue
            data_list.append((
                '',
                record.get('latitude', ''),
                record.get('longitude', ''),
                'KEY_TARGET_LOCATION_SYNCED',
                '',
                '',
                context.get_relative_path(file_found),
            ))
            sources.append(file_found)

        elif name == 'home_screen_layout_simple_store_key':
            record = _load_simplestore_json(file_found)
            if not isinstance(record, dict):
                continue
            meta = record.get('metadata') or {}
            location = meta.get('requestLocation') or {}
            if not location:
                continue
            data_list.append((
                _iso(meta.get('creationTime')),
                location.get('latitude', ''),
                location.get('longitude', ''),
                'Home screen layout request location',
                meta.get('cityID', ''),
                f"expirationTime={meta.get('expirationTime', '')}",
                context.get_relative_path(file_found),
            ))
            sources.append(file_found)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Record Type',
        'City ID',
        'Additional Fields (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def uber_shortcuts(context):
    data_list = []
    source_path = ''

    for file_found in unique_files(context):
        record = _load_kv_json(file_found)
        if not isinstance(record, dict):
            continue
        source_path = file_found
        relative_path = context.get_relative_path(file_found)

        for cell_key, entry in record.items():
            if not isinstance(entry, dict):
                continue
            trigger = entry.get('triggerLocation') or {}
            for shortcut in entry.get('shortcuts') or []:
                if not isinstance(shortcut, dict):
                    continue
                destination = shortcut.get('destination') or {}
                coordinate = destination.get('coordinate') or {}
                categories = destination.get('categories') or []
                data_list.append((
                    _ms(entry.get('timestamp')),
                    coordinate.get('latitude', ''),
                    coordinate.get('longitude', ''),
                    shortcut.get('title', ''),
                    shortcut.get('subtitle', ''),
                    destination.get('addressLine1', ''),
                    destination.get('addressLine2', ''),
                    destination.get('fullAddress', ''),
                    ', '.join(str(c) for c in categories),
                    shortcut.get('acceleratorType', ''),
                    destination.get('provider', ''),
                    destination.get('locale', ''),
                    shortcut.get('uuid', ''),
                    destination.get('id', ''),
                    len(destination.get('accessPoints') or []),
                    trigger.get('latitude', ''),
                    trigger.get('longitude', ''),
                    cell_key,
                    relative_path,
                ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Title',
        'Subtitle',
        'Address Line 1',
        'Address Line 2',
        'Full Address',
        'Categories',
        'Accelerator Type (as stored)',
        'Provider (as stored)',
        'Locale',
        'Shortcut UUID',
        'Destination ID',
        'Access Point Count',
        'Trigger Latitude',
        'Trigger Longitude',
        'Cell Key (as stored)',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def uber_payment_profiles(context):
    data_list = []
    source_path = ''

    for file_found in unique_files(context):
        record = _load_kv_json(file_found)
        if not isinstance(record, list):
            continue
        source_path = file_found
        relative_path = context.get_relative_path(file_found)

        for profile in record:
            if not isinstance(profile, dict):
                continue
            data_list.append((
                _iso(profile.get('updatedAt')),
                profile.get('uuid', ''),
                profile.get('accountName', ''),
                profile.get('tokenDisplayName', ''),
                profile.get('status', ''),
                profile.get('tokenType', ''),
                profile.get('useCase', ''),
                profile.get('authenticationType', ''),
                profile.get('hasBalance', ''),
                ', '.join(str(c) for c in profile.get('supportedCapabilities') or []),
                len(profile.get('supportedUseCases') or []),
                profile.get('clientUuid', ''),
                relative_path,
            ))

    data_headers = (
        ('Updated At', 'datetime'),
        'Profile UUID',
        'Account Name',
        'Token Display Name',
        'Status (as stored)',
        'Token Type (as stored)',
        'Use Case (as stored)',
        'Authentication Type (as stored)',
        'Has Balance',
        'Supported Capabilities (as stored)',
        'Supported Use Case Count',
        'Client UUID',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def uber_city(context):
    data_list = []
    source_path = ''

    for file_found in unique_files(context):
        record = _load_kv_json(file_found)
        if not isinstance(record, dict) or 'cityId' not in record:
            continue
        source_path = file_found
        meta = record.get('meta') or {}
        views_order = record.get('vehicleViewsOrder') or []
        data_list.append((
            _ms(meta.get('lastModifiedTimeMs')),
            _ms(meta.get('originTimeMs')),
            record.get('cityId', ''),
            record.get('cityName', ''),
            record.get('countryIso2', ''),
            record.get('currencyCode', ''),
            record.get('timezone', ''),
            record.get('defaultVehicleViewId', ''),
            record.get('isEmergencyLocationSharingAvailable', ''),
            len(record.get('vehicleViews') or {}),
            ', '.join(str(v) for v in views_order),
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Last Modified', 'datetime'),
        ('Origin Time', 'datetime'),
        'City ID',
        'City Name (as stored)',
        'Country ISO2',
        'Currency Code',
        'Timezone',
        'Default Vehicle View ID',
        'Emergency Location Sharing Available',
        'Vehicle View Count',
        'Vehicle Views Order (as stored)',
        'Source File',
    )
    return data_headers, data_list, source_path


@artifact_processor
def uber_sessions(context):
    data_list = []
    sources = []

    for file_found in unique_files(context):
        name = os.path.basename(file_found)
        relative_path = context.get_relative_path(file_found)

        if name == 'session_LAST_SESSION':
            record = _load_kv_json(file_found)
            if not isinstance(record, dict):
                continue
            data_list.append((
                _ms(record.get('sessionStartTimeMs')),
                '',
                'session_LAST_SESSION',
                record.get('sessionId', ''),
                '',
                'sessionBackgroundedTimeNanos='
                f"{record.get('sessionBackgroundedTimeNanos', '')}",
                relative_path,
            ))
            sources.append(file_found)

        elif name == 'realtime-demo_KEY_CLIENT_STATUS':
            record = _load_kv_json(file_found)
            if not isinstance(record, dict):
                continue
            meta = record.get('meta') or {}
            data_list.append((
                _ms(meta.get('lastModifiedTimeMs')),
                _ms(meta.get('originTimeMs')),
                'KEY_CLIENT_STATUS',
                record.get('lastRequestJobUUID', ''),
                '',
                f"status={record.get('status', '')}; "
                f"statusDescription={record.get('statusDescription', '')}",
                relative_path,
            ))
            sources.append(file_found)

        elif name == 'oauth_tokens.xml':
            values = _read_shared_prefs(file_found)
            if not values:
                continue
            present = [key for key in ('access_token', 'refresh_token') if values.get(key)]
            data_list.append((
                _ms(values.get('expire_time_ms')),
                _ms(values.get('rt_expire_time_ms')),
                'oauth_tokens.xml',
                values.get('session_id', ''),
                values.get('user_uuid', ''),
                f"tokens present: {', '.join(present) if present else 'none'}",
                relative_path,
            ))
            sources.append(file_found)

        elif name == 'unified_session_swap_store.xml':
            values = _read_shared_prefs(file_found)
            for key, value in (values or {}).items():
                try:
                    session = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    continue
                if not isinstance(session, dict):
                    continue
                data_list.append((
                    '',
                    '',
                    key,
                    session.get('sessionId', ''),
                    '',
                    f"deviceId={session.get('deviceId', '')}",
                    relative_path,
                ))
            if values:
                sources.append(file_found)

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Second Timestamp', 'datetime'),
        'Record Type',
        'Session or Job UUID',
        'User UUID',
        'Additional Fields (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


def _read_shared_prefs(file_found):
    """{name: text} for the entries of an Android shared preferences XML file."""
    try:
        root = ET.parse(file_found).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {file_found}: {ex}')
        return {}
    values = {}
    for element in root:
        name = element.get('name')
        if not name:
            continue
        values[name] = element.get('value') if element.get('value') is not None else element.text
    return values


@artifact_processor
def uber_telemetry(context):
    data_list = []
    source_path = ''

    query = '''
        SELECT createdAt, createdAtNtp, message_type, message_uuid, group_uuid,
               cold_launch_uuid, status, content
        FROM message
        ORDER BY createdAt
    '''

    for file_found in unique_files(context):
        if not file_found.endswith('ur_message.db'):
            continue
        records = get_sqlite_db_records(file_found, query)
        if not records:
            continue
        source_path = file_found
        relative_path = context.get_relative_path(file_found)

        for record in records:
            try:
                payload = json.loads(record[7]) if record[7] else {}
            except (json.JSONDecodeError, TypeError):
                payload = {}
            meta = (payload.get('contextual_data') or {}).get('prod_meta') or {}
            app = meta.get('app') or {}
            device = meta.get('device') or {}
            carrier = meta.get('carrier') or {}
            network = meta.get('network') or {}
            session = meta.get('session') or {}
            location = meta.get('location') or {}
            data_list.append((
                _ms(record[0]),
                _ms(record[1]),
                record[2],
                record[3],
                app.get('version', ''),
                app.get('type', ''),
                app.get('installation_source', ''),
                device.get('manufacturer', ''),
                device.get('model', ''),
                device.get('os_version', ''),
                device.get('os_version_build', ''),
                device.get('locale', ''),
                device.get('device_id', ''),
                device.get('installation_id', ''),
                session.get('user_uuid', ''),
                session.get('session_id', ''),
                record[5] or session.get('cold_launch_id', ''),
                location.get('city', ''),
                location.get('city_id', ''),
                f"mcc={carrier.get('mcc', '')}; mnc={carrier.get('mnc', '')}",
                network.get('type', ''),
                record[6],
                relative_path,
            ))

    data_headers = (
        ('Created At', 'datetime'),
        ('Created At NTP', 'datetime'),
        'Message Type (as stored)',
        'Message UUID',
        'App Version',
        'App Type',
        'Installation Source',
        'Device Manufacturer',
        'Device Model',
        'OS Version',
        'OS Build',
        'Locale',
        'Device ID',
        'Installation ID',
        'User UUID',
        'Session ID',
        'Cold Launch ID',
        'City (as stored)',
        'City ID',
        'Carrier (as stored)',
        'Network Type (as stored)',
        'Status (as stored)',
        'Source File',
    )
    return data_headers, data_list, source_path


_MAGIC = (
    (b'RIFF', 4, b'WEBP', 'image/webp', 'webp'),
    (b'\x89PNG\r\n\x1a\n', 0, b'', 'image/png', 'png'),
    (b'\xff\xd8\xff', 0, b'', 'image/jpeg', 'jpg'),
    (b'GIF8', 0, b'', 'image/gif', 'gif'),
)


def _sniff_image(head):
    """(mime, extension) from the leading bytes, or (None, None) when unrecognised."""
    for magic, offset, secondary, mime, extension in _MAGIC:
        if head.startswith(magic) and (not secondary or head[offset + 4:offset + 8] == secondary):
            return mime, extension
    return None, None


@artifact_processor
def uber_cached_images(context):
    data_list = []
    sources = []

    entries = {}
    for file_found in unique_files(context):
        base, _, suffix = os.path.basename(file_found).rpartition('.')
        if suffix not in ('0', '1') or not base:
            continue
        entries.setdefault(base, {})[suffix] = file_found

    for base, pair in sorted(entries.items()):
        body = pair.get('1')
        if not body:
            continue
        try:
            with open(body, 'rb') as handle:
                head = handle.read(16)
            size = os.path.getsize(body)
        except OSError as ex:
            logfunc(f'Could not read {body}: {ex}')
            continue

        mime, extension = _sniff_image(head)
        if not mime:
            continue

        fetched = received = ''
        headers = {}
        metadata = pair.get('0')
        if metadata:
            try:
                with open(metadata, 'r', encoding='utf-8', errors='replace') as handle:
                    lines = handle.read().splitlines()
            except OSError:
                lines = []
            if len(lines) >= 2:
                fetched, received = _ms(lines[0]), _ms(lines[1])
            for line in lines:
                key, separator, value = line.partition(': ')
                if separator:
                    headers.setdefault(key.strip().lower(), value.strip())

        media_ref = check_in_media(body, name=base, force_type=mime, force_extension=extension)
        data_list.append((
            fetched,
            received,
            media_ref,
            mime,
            size,
            headers.get('content-type', ''),
            headers.get('date', ''),
            headers.get('etag', ''),
            base,
            context.get_relative_path(body),
        ))
        sources.append(body)

    data_headers = (
        ('Cached At', 'datetime'),
        ('Response Stored At', 'datetime'),
        ('Image', 'media'),
        'Detected Media Type',
        'Size (bytes)',
        'Stored Content-Type Header',
        'Stored Date Header',
        'Stored ETag Header',
        'Cache Entry Name (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def uber_settings(context):
    data_list = []
    sources = []

    for file_found in unique_files(context):
        name = os.path.basename(file_found)
        relative_path = context.get_relative_path(file_found)

        if name.endswith('_store_key') or name == 'user_uuid':
            value = _load_simplestore_json(file_found)
        else:
            value = _load_kv_json(file_found)
        if value is None:
            continue

        if name == 'consent-and-copy_USER_CONSENT' and isinstance(value, dict):
            for consent_uuid, consent in value.items():
                if not isinstance(consent, dict):
                    continue
                data_list.append((
                    _iso((consent.get('timestamp') or '').replace(' UTC', '').replace(' +0000', '+00:00')),
                    'User consent',
                    f"compliance={consent.get('compliance', '')}; "
                    f"disclosureUuid={consent.get('disclosureUuid', '')}; "
                    f"consentUuid={consent_uuid}",
                    relative_path,
                ))
            sources.append(file_found)
            continue

        data_list.append((
            '',
            name,
            json.dumps(value) if isinstance(value, (dict, list)) else str(value),
            relative_path,
        ))
        sources.append(file_found)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Setting',
        'Value (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
