__artifacts_v2__ = {
    "google_find_my_device_devices": {
        "name": "Google Find My Device - Devices",
        "description": "Devices the Google Find My Device app keeps in its devices list for a "
                       "Google account: name, device type and category, manufacturer, model, "
                       "IMEI and activation time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Google Find My Device",
        "notes": "Read from "
                 "com.google.android.apps.adm/files/datastore/com.google:<account>_devices_store.pb, "
                 "a DataStore file the app registers as devices_store. It holds one protobuf "
                 "message: a repeated device record (field 1), a timestamp (field 2, present on the "
                 "tested file, meaning not established, not reported) and a second list (field 3, "
                 "absent on the tested file). It is decoded with the vendored blackboxprotobuf and "
                 "field types from the app's own message classes. Field meanings come from the "
                 "decompiled app (Find My Device versionName 3.1.763-04, versionCode 20014429, "
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
                 "'_devices_store.pb'. The message classes also have fields that look like location "
                 "data (on the device record, on the tracker record and in a separate list). None "
                 "was present in the tested file, so they are not read. Several other fields (a "
                 "second timestamp on the device record, an integer the app compares with 28 and 30, "
                 "a string it clears when the location response says location is off) had no reader "
                 "found in the app that names them, and they are not reported. The tested records "
                 "also carry fields 2, 6 and 11 of the device record, which are not read. The app "
                 "keeps this list locally and merges incoming records into the stored ones, so a "
                 "record can mix values from more than one update. A row does not establish that the "
                 "device was ever near this phone. Tested on one image (dragna_pixel9a_a16): 3 "
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
_TYPEDEF = {'1': {'type': 'message', 'name': '', 'message_typedef': _DEVICE}}

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


@artifact_processor
def google_find_my_device_devices(context):
    data_headers = (('Activated', 'datetime'), 'Device Name', 'Device Type', 'Device Category',
                    'Manufacturer', 'Model', 'IMEI', 'Account')
    data_list, sources = [], []
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
            logfunc(f'Google Find My Device - Devices: could not decode {os.path.basename(path)}: '
                    f'{type(error).__name__}')
            continue
        account = _account(path)
        for device in _as_list(message.get('1')):
            if not isinstance(device, dict):
                continue
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
                activated, manufacturer, model = _tracker_values(
                    _as_dict(device.get('10')).get('11'))
            device_type = _as_dict(device.get('1')).get('2', 0)
            data_list.append((
                activated, _text(device.get('5')), _enum_name(_DEVICE_TYPES, device_type),
                _enum_name(_CATEGORIES, device.get('8', 0)), manufacturer, model, imei, account,
            ))
    return data_headers, data_list, '\n'.join(sources)
