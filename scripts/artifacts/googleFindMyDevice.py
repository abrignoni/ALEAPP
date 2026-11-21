__artifacts_v2__ = {
    "google_find_my_device_devices": {
        "name": "Google Find My Device - Devices",
        "description": "Devices the Google Find My Device app (labelled Find Hub in the tested "
                       "version) keeps in its devices list for a Google account: name, device type and category, manufacturer, model, "
                       "IMEI and activation time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Google Find My Device",
        "notes": "Read from "
                 "com.google.android.apps.adm/files/datastore/com.google:<account>_devices_store.pb, "
                 "a DataStore file the app registers as devices_store. It holds one protobuf "
                 "message: a repeated device record (field 1), a timestamp (field 2, present on the "
                 "tested files, meaning not established, not reported) and a per-device location "
                 "list (field 3), which Google Find My Device - Device Locations reports. It is decoded with the vendored blackboxprotobuf and "
                 "field types from the app's own message classes, except that the identifier's "
                 "sub-fields are read as raw bytes. Field meanings come from the "
                 "decompiled app (com.google.android.apps.adm, labelled Find Hub, versionName 3.1.763-04, versionCode 20014429, "
                 "decompiled with jadx; the code is obfuscated). The app builds a DeviceModel from "
                 "each record for its listDevices app function: deviceName, deviceType, "
                 "deviceCategory, manufacturer and model. Device Type uses the app's own enum names "
                 "(such as ANDROID_DEVICE, SPOT_DEVICE and FASTPAIR_DEVICE) and Device Category the "
                 "names the app gives the stored value (such as PHONE, BEACON and EARBUDS). The same "
                 "model also carries a device id, a current-device flag, a ringable flag and a "
                 "tracker type, which are not reported. For an Android device record, Manufacturer "
                 "and Model are the ones DeviceModel carries. IMEI and Activated are the values the "
                 "app shows under its strings 'IMEI: ...' and 'Activated: ...'. Activated is a time "
                 "kept in seconds, which the app shows as a date only. For a tracker (SPOT_DEVICE) "
                 "and a Fast Pair (FASTPAIR_DEVICE) device the app reads a nested device record. Its "
                 "own accessors return the tracker's record, or for Fast Pair the record in field "
                 "11 of the device record's field 10. From that record the app's device details code takes the model (field "
                 "34, falling back to the manufacturer and model strings joined) and the time it "
                 "shows under 'Activated: ...' (field 33). Manufacturer is that record's field 20, "
                 "which DeviceModel carries for trackers. For Fast Pair, DeviceModel leaves "
                 "manufacturer and model empty, so for that record they are the device details "
                 "values, not DeviceModel's. IMEI is reported only for Android device records. "
                 "Account is the part of the file name between 'com.google:' and "
                 "'_devices_store.pb'. The message classes also have location fields on the device "
                 "record (field 36 of its Android part, field 2 of the tracker part, field 10 of the "
                 "Fast Pair part). None was present in the tested files (one corpus image, one lab "
                 "capture), and they are not read. Several other fields (a "
                 "second timestamp on the device record, an integer the app compares with 28 and 30, "
                 "a string it clears when the location response says location is off) had no reader "
                 "found in the app that names them, and they are not reported. The tested records "
                 "also carry fields 2, 6 and 11 of the device record, which are not read. The app "
                 "keeps this list locally and merges incoming records into the stored ones, so a "
                 "record can mix values from more than one update. A row does not establish that the "
                 "device was ever near this phone. Rows came from one corpus image (dragna_pixel9a_a16): 3 "
                 "records, one each of ANDROID_DEVICE, SPOT_DEVICE and FASTPAIR_DEVICE. Account held "
                 "one value on all 3 rows. IMEI is filled on 1 of 3 rows, the Android one. On the "
                 "other 11 tested images no file matched this artifact's path pattern.",
        "paths": ('*/com.google.android.apps.adm/files/datastore/*_devices_store.pb',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.apps.adm versionCode 20014429 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
        },
    },
    "google_find_my_device_locations": {
        "name": "Google Find My Device - Device Locations",
        "description": "The location the Google Find My Device app (labelled Find Hub in the tested "
                       "version) cached for an Android device, when the file holds one: time, "
                       "coordinates and accuracy.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Google Find My Device",
        "notes": "Read from the location list (field 3) of "
                 "com.google.android.apps.adm/files/datastore/com.google:<account>_devices_store.pb, "
                 "the same file as Google Find My Device - Devices. Field meanings come from the "
                 "decompiled app (com.google.android.apps.adm, labelled Find Hub, versionName "
                 "3.1.763-04, versionCode 20014429, decompiled with jadx; the code is obfuscated). "
                 "The app's code writes an entry when it processes a location for an Android device "
                 "and an app flag is on. The flag's default is not established. Its log calls this a "
                 "cleartext location cache. Latitude, Longitude, Accuracy (m) and Location Time are "
                 "read from the stored fields the app loads into its DeviceLocationModel as "
                 "latitude, longitude, accuracyMeters and locationTimestampMillis. Accuracy is "
                 "rounded to 3 decimals. Location Saved is the app's reading of the phone's clock "
                 "when it wrote the entry. Location Type (as stored) is an integer kept with the "
                 "entry, and its meaning is not established. An entry is matched to a device on the "
                 "whole identifier in field 1 of both records. When no device record matches, Device "
                 "Name, Manufacturer and Model are empty and Device Type comes from the entry's own "
                 "identifier. No tested file had such an entry. The app updates a "
                 "device's entry in place and has a cleanup that clears a stored location older than "
                 "a cutoff it is given. The cutoff's length is not established. So a row holds at "
                 "most the last stored location, and no row for a device does not establish that it "
                 "was never located. A row is a location stored for the named device, which need not "
                 "be the phone holding this file. The code also caches tracker locations in field 7 of an entry. "
                 "That field was not present in the tested files and is not read. Exercised on one "
                 "lab test account capture that is not in the corpus: after an Android phone was "
                 "selected in the app, the file held one location entry for it, and the stored "
                 "coordinates were within 0.1 km of that phone's own last location fix. The "
                 "dragna_pixel9a_a16 file has no location list. On the other 11 images in "
                 "sample_data no file matched this artifact's path pattern.",
        "paths": ('*/com.google.android.apps.adm/files/datastore/*_devices_store.pb',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.apps.adm versionCode 20014429 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ilapfuncs import artifact_processor, logfunc

_TIMESTAMP = {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}
# ssq: the tracker record (manufacturer 20, model parts 21 and 34, activation time 33)
_TRACKER_RECORD = {
    '20': {'type': 'bytes', 'name': ''},
    '33': {'type': 'message', 'name': '', 'message_typedef': _TIMESTAMP},
    '21': {'type': 'bytes', 'name': ''},
    '34': {'type': 'bytes', 'name': ''},
}
_TRACKER = {'1': {'type': 'message', 'name': '', 'message_typedef': _TRACKER_RECORD}}
# uep, one device record; field numbers from the app's message classes (see the notes)
_DEVICE = {
    '1': {'type': 'message', 'name': '',
          'message_typedef': {'2': {'type': 'int', 'name': ''}}},
    '3': {'type': 'message', 'name': '', 'message_typedef': {
        '2': {'type': 'message', 'name': '', 'message_typedef': _TIMESTAMP},
        '3': {'type': 'bytes', 'name': ''},
        '4': {'type': 'bytes', 'name': ''},
        '7': {'type': 'bytes', 'name': ''},
    }},
    '4': {'type': 'message', 'name': '', 'message_typedef': _TRACKER},
    '5': {'type': 'bytes', 'name': ''},
    '8': {'type': 'int', 'name': ''},
    '10': {'type': 'message', 'name': '', 'message_typedef': {
        '11': {'type': 'message', 'name': '', 'message_typedef': _TRACKER}}},
}
# ueq, a device identifier: a oneof over fields 1, 3 and 5, and the device type in field 2
_IDENTIFIER = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'int', 'name': ''},
    '3': {'type': 'bytes', 'name': ''},
    '5': {'type': 'bytes', 'name': ''},
}
_DEVICE['1'] = {'type': 'message', 'name': '', 'message_typedef': _IDENTIFIER}
# gli, the location entry for one device: identifier (field 1) and glg (field 6)
_LOCATION_ENTRY = {
    '1': {'type': 'message', 'name': '', 'message_typedef': _IDENTIFIER},
    '6': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'message', 'name': '', 'message_typedef': {
            '1': {'type': 'message', 'name': '', 'message_typedef': {
                '1': {'type': 'double', 'name': ''},
                '2': {'type': 'double', 'name': ''},
            }},
            '2': {'type': 'float', 'name': ''},
        }},
        '2': {'type': 'message', 'name': '', 'message_typedef': _TIMESTAMP},
        '3': {'type': 'int', 'name': ''},
        '4': {'type': 'message', 'name': '', 'message_typedef': _TIMESTAMP},
    }},
}
_TYPEDEF = {
    '1': {'type': 'message', 'name': '', 'message_typedef': _DEVICE},
    '3': {'type': 'message', 'name': '', 'message_typedef': _LOCATION_ENTRY},
}

# enum ues, names kept in the app
_DEVICE_TYPES = {
    0: 'UNKNOWN_DEVICE_TYPE', 1: 'ANDROID_DEVICE', 2: 'SPOT_DEVICE', 3: 'TEST_DEVICE_TYPE',
    4: 'AUTO_DEVICE', 5: 'FASTPAIR_DEVICE', 6: 'SUPERVISED_ANDROID_DEVICE',
}
# the app names stored value n with entry n + 2 of its category switch
_CATEGORIES = (
    'UNKNOWN_DEVICE_CATEGORY', 'PHONE', 'TABLET', 'TV', 'WEAR', 'CHROMEBOOK', 'AUTO',
    'BEACON', 'HEADPHONES', 'WATCH', 'STYLUS', 'EARBUDS',
)
_DECODE_ERRORS = (ValueError, KeyError, TypeError, IndexError, EOFError)
_PREFIX = 'com.google:'
_SUFFIX = '_devices_store.pb'


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _as_dict(value):
    if isinstance(value, list):
        value = value[0] if value else {}
    return value if isinstance(value, dict) else {}


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return value if isinstance(value, str) else ''


def _enum_name(names, value):
    if not isinstance(value, int):
        return ''
    if isinstance(names, dict):
        name = names.get(value)
    else:
        name = names[value] if 0 <= value < len(names) else None
    return name if name else f'Unknown ({value})'


def _seconds_utc(timestamp):
    seconds = _as_dict(timestamp).get('1')
    if not isinstance(seconds, int) or seconds <= 0:
        return ''
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _tracker_values(tracker):
    """(activated, manufacturer, model) from a tracker or Fast Pair device's nested record."""
    record = _as_dict(_as_dict(tracker).get('1'))
    manufacturer = _text(record.get('20'))
    model = _text(record.get('34')) or f"{manufacturer} {_text(record.get('21'))}".strip()
    return _seconds_utc(record.get('33')), manufacturer, model


def _account(path):
    """The account part of the file name. The zip and tar seekers stage a ':' as '_'."""
    name = os.path.basename(path)
    for prefix in (_PREFIX, _PREFIX.replace(':', '_')):
        if name.startswith(prefix) and name.endswith(_SUFFIX):
            return name[len(prefix):-len(_SUFFIX)]
    return ''


def _time_utc(timestamp):
    """A seconds and nanoseconds message as a UTC datetime, to the microsecond."""
    stamp = _as_dict(timestamp)
    seconds = stamp.get('1')
    if not isinstance(seconds, int) or seconds <= 0:
        return ''
    nanos = stamp.get('2', 0)
    micros = nanos // 1000 if isinstance(nanos, int) and 0 <= nanos < 1_000_000_000 else 0
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc).replace(microsecond=micros)
    except (OverflowError, OSError, ValueError):
        return ''


def _device_key(identifier):
    """The whole identifier, so tracker and Fast Pair ids compare as well as Android ones."""
    identifier = _as_dict(identifier)
    return tuple(identifier.get(field) for field in ('1', '2', '3', '5'))


def _device_values(device):
    """(activated, name, type, category, manufacturer, model, IMEI) for one device record."""
    activated, manufacturer, model, imei = '', '', '', ''
    android = device.get('3')
    if android is not None:
        android = _as_dict(android)
        activated = _seconds_utc(android.get('2'))
        manufacturer = _text(android.get('4'))
        model = _text(android.get('3'))
        imei = _text(android.get('7'))
    elif device.get('4') is not None:
        activated, manufacturer, model = _tracker_values(device.get('4'))
    elif device.get('10') is not None:
        activated, manufacturer, model = _tracker_values(_as_dict(device.get('10')).get('11'))
    device_type = _as_dict(device.get('1')).get('2', 0)
    return (activated, _text(device.get('5')), _enum_name(_DEVICE_TYPES, device_type),
            _enum_name(_CATEGORIES, device.get('8', 0)), manufacturer, model, imei)


def _stores(context, artifact_name, sources):
    """(account, message) for each readable store; adds each store's path to sources."""
    for file_found in unique_files(context):
        path = str(file_found)
        if not path.endswith(_SUFFIX):
            continue
        sources.append(path)
        with open(path, 'rb') as handle:
            data = handle.read()
        if not data:
            continue
        try:
            message, _ = decode_message(data, _TYPEDEF)
        except _DECODE_ERRORS as error:
            logfunc(f'{artifact_name}: could not decode {os.path.basename(path)}: '
                    f'{type(error).__name__}')
            continue
        yield _account(path), message


@artifact_processor
def google_find_my_device_devices(context):
    data_headers = (('Activated', 'datetime'), 'Device Name', 'Device Type', 'Device Category',
                    'Manufacturer', 'Model', 'IMEI', 'Account')
    data_list, sources = [], []
    for account, message in _stores(context, 'Google Find My Device - Devices', sources):
        for device in _as_list(message.get('1')):
            if isinstance(device, dict):
                data_list.append((*_device_values(device), account))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def google_find_my_device_locations(context):
    data_headers = (('Location Time', 'datetime'), ('Location Saved', 'datetime'),
                    ('Latitude', 'latitude'), ('Longitude', 'longitude'),
                    ('Accuracy (m)', 'number'), 'Location Type (as stored)', 'Device Name',
                    'Device Type', 'Manufacturer', 'Model', 'Account')
    data_list, sources = [], []
    for account, message in _stores(context, 'Google Find My Device - Device Locations', sources):
        devices = {_device_key(device.get('1')): device
                   for device in _as_list(message.get('1')) if isinstance(device, dict)}
        for entry in _as_list(message.get('3')):
            if not isinstance(entry, dict) or entry.get('6') is None:
                continue
            cached = _as_dict(entry.get('6'))
            fix = _as_dict(cached.get('1'))
            point = _as_dict(fix.get('1'))
            latitude, longitude = point.get('1'), point.get('2')
            if not isinstance(latitude, float) or not isinstance(longitude, float):
                latitude, longitude = '', ''
            accuracy = fix.get('2')
            location_type = cached.get('3')
            identifier = _as_dict(entry.get('1'))
            device = devices.get(_device_key(identifier))
            if device is not None:
                _, name, device_type, _, manufacturer, model, _ = _device_values(device)
            else:
                name, manufacturer, model = '', '', ''
                device_type = _enum_name(_DEVICE_TYPES, identifier.get('2', 0))
            data_list.append((
                _time_utc(cached.get('2')), _time_utc(cached.get('4')), latitude, longitude,
                round(accuracy, 3) if isinstance(accuracy, float) else '',
                location_type if isinstance(location_type, int) else '',
                name, device_type, manufacturer, model, account,
            ))
    return data_headers, data_list, '\n'.join(sources)
