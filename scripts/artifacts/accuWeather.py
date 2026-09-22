__artifacts_v2__ = {
    "accuweather_location": {
        "name": "AccuWeather Location",
        "description": "The position AccuWeather stored for the device and the location it was set to use",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "AccuWeather",
        "sample_data": {
            "emu_a15_oss_v16": "AccuWeather 21.1.16-4-rc | 1 row",
        },
        "notes": "One row per location record in the DataStore preferences file "
                 "com.accuweather.android/files/datastore/SETTINGS_LOCATION_PREFERENCES."
                 "preferences_pb. The app's own SQLite database holds only home screen widget "
                 "tables and was empty on the tested image, so this file is where the position "
                 "lives. "
                 "Latitude, Longitude and Fix Time are read from the GPS_LOCATION_COORDINATES "
                 "value, which the app stores as a JSON object with latitude, longitude and "
                 "lastKnownLocationFix members. Fix Time is Unix milliseconds and is reported as "
                 "UTC. "
                 "**The stored coordinates are rounded to three decimal places**, which is "
                 "roughly 110 metres, so they are not the fix the platform handed the app. "
                 "Measured by moving the device position and reading the file back three "
                 "times: 38.897683 was stored as 38.898, 64.146600 as 64.147 and 51.507350 as "
                 "51.507. An examiner should treat the value as a neighbourhood, not a point. "
                 "Location Key is the app's own numeric key for the place it was showing, and "
                 "**it can lag the coordinates**: across those same three moves it changed once "
                 "and then stayed on the previous place's key while the coordinates moved on, "
                 "so the key can name somewhere the device has already left. Why it lags was not "
                 "established here. Default Location is which source the app was set to use, "
                 "'gps_location' on the tested image. **The coordinates on the tested image are "
                 "the Android emulator's default fix**, 38.898, -77.037, which is not a place "
                 "anyone travelled to; they are reported because the field is the artifact, and "
                 "an examiner reading a real device gets a real position in the same field. A "
                 "row records the position the app last held, not a track. That the file keeps "
                 "one coordinate pair and overwrites it was measured rather than assumed: moving "
                 "the device twice replaced the pair both times and the file shrank from 285 to "
                 "284 to 283 bytes, never growing, so no previous position is retained and there "
                 "is no way to tell how long the device was anywhere. Two neighbouring DataStore "
                 "files are not parsed. SETTINGS_SHARED_PREFERENCES holds display, unit and "
                 "notification settings, which say nothing about where the device was. "
                 "one_app_native_settings_datastore holds a catalogue of national weather alert "
                 "providers, which is not device position data and is not reported.",
        "paths": ('*/com.accuweather.android/files/datastore/SETTINGS_LOCATION_PREFERENCES.preferences_pb',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
}

import json
import os

import scripts.blackboxprotobuf as blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

STORE_SUFFIX = 'SETTINGS_LOCATION_PREFERENCES.preferences_pb'
# DataStore preferences wire layout: entries(1){ key(1), value(2){ string(5) } }
_ENTRIES, _KEY, _VALUE, _STRING = '1', '1', '2', '5'


def _store_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(STORE_SUFFIX)]


def _as_text(value):
    return value.decode('utf-8', 'replace') if isinstance(value, bytes) else (value or '')


def _preferences(path):
    """{key: string value} for a DataStore preferences file, or {} when unreadable."""
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        logfunc(f'AccuWeather: could not read {os.path.basename(path)}: {error}')
        return {}
    try:
        message, _ = blackboxprotobuf.decode_message(raw)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'AccuWeather: {os.path.basename(path)} did not decode as protobuf: {error}')
        return {}
    entries = message.get(_ENTRIES)
    if entries is None:
        return {}
    if not isinstance(entries, list):
        entries = [entries]
    out = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = _as_text(entry.get(_KEY))
        value = entry.get(_VALUE)
        if key and isinstance(value, dict) and _STRING in value:
            out[key] = _as_text(value[_STRING])
    return out


@artifact_processor
def accuweather_location(context):
    data_list = []
    sources = []
    for path in _store_files(context):
        values = _preferences(path)
        if not values:
            continue
        latitude = longitude = fix = ''
        try:
            coordinates = json.loads(values.get('GPS_LOCATION_COORDINATES') or '')
        except (TypeError, ValueError):
            coordinates = None
        if isinstance(coordinates, dict):
            latitude = coordinates.get('latitude', '')
            longitude = coordinates.get('longitude', '')
            stamp = coordinates.get('lastKnownLocationFix')
            if isinstance(stamp, int) and stamp > 0:
                try:
                    fix = convert_unix_ts_to_utc(stamp // 1000)
                except (OverflowError, OSError, ValueError):
                    fix = ''
        if latitude == '' and longitude == '' and not values.get('CURRENT_LOCATION_KEY'):
            continue
        data_list.append((
            fix, latitude, longitude,
            values.get('CURRENT_LOCATION_KEY', ''),
            values.get('DEFAULT_LOCATION_KEY_SETTING_SHARED_KEY', ''),
            values.get('DEFAULT_LOCATION_NAME_SETTING_SHARED_KEY', ''),
            context.get_relative_path(path)))
        if path not in sources:
            sources.append(path)

    data_headers = (
        ('Fix Time', 'datetime'), 'Latitude', 'Longitude', 'Location Key',
        'Default Location', 'Default Location Name', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
