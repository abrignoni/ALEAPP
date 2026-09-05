"""Life360 Android local Room stores: the device's own location samples and geofences
(L360LocationLocalStoreRoomDatabase) and the circle's devices with their last known locations
(MembersEngineRoomDatabase). Rows of both stores live partly or wholly in the write-ahead log,
so the -wal and -shm sidecars are part of every path pattern."""

__artifacts_v2__ = {
    "life360DeviceLocationStore": {
        "name": "Life360 Device Location Store",
        "description": "Location samples the Life360 app recorded on this device, from the location table of L360LocationLocalStoreRoomDatabase, with the sample type, location mode and device state as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the location table of "
                 "com.life360.android.safetymapd/databases/L360LocationLocalStoreRoomDatabase, Life360's own store "
                 "of the fixes it took on this device; the -wal and -shm sidecars are read with it because 12 and "
                 "11 of the rows on two tested images existed only in the write-ahead log. Timestamp is the time "
                 "column, a millisecond Unix epoch, converted to UTC. Sample Type (as stored) is the row's type "
                 "(RAW 109, FILTERED 94 and SENT 55 of the 258 rows on the 3 tested images that held the store), "
                 "Location Mode (as stored) is the lmode value (int, move, prox, geo, gh or heartbeat, blank on 62 "
                 "rows), and Provider (as stored) was fused on every row as User Activity (as stored) was unknown "
                 "on every row; both are kept as the values the app wrote. Bearing (as stored) was 0 on 198 of the "
                 "258 rows and Speed (as stored) 0 on 76, and Battery Charging (as stored) and Wi-Fi Connected (as "
                 "stored) are the 0 or 1 flags stored with the fix, each one value across an image whose fixes all "
                 "shared it. Each image's rows spanned under three hours, so this store is a short recent buffer "
                 "and not a location history; the longer records are in the Life360 API cache and event store "
                 "artifacts. Of the 7 extractions run, 3 held the store (a public Pixel 7a and two Pixel 8 Pro "
                 "training images); a file listing scan of all 23 zip-form Android corpora found it on no other, "
                 "and the tar-form emulator snapshots hold only the lab's open-source apps and were not scanned. "
                 "The store's smart_realtime_execution_data table, one row of a start time and duration, is "
                 "service telemetry and is not reported.",
        "paths": ('*/com.life360.android.safetymapd/databases/L360LocationLocalStoreRoomDatabase*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 107 rows",
            "hc_pixel8pro_a17": "Android 17 | 84 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no Life360 local stores | 0 rows",
            "pixel3_a12": "Android 12 | no Life360 local stores | 0 rows",
            "pixel7a_a14": "Android 14 | 67 rows",
            "samsungs20_a13": "Android 13 | no Life360 local stores | 0 rows",
            "sharon_a14": "Android 14 | no Life360 local stores | 0 rows",
        },
    },
    "life360ActivityTransitions": {
        "name": "Life360 Activity Transitions",
        "description": "Activity transition records from the activity_transition table of L360LocationLocalStoreRoomDatabase, with the activity type and transition codes as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the activity_transition table of the same L360LocationLocalStoreRoomDatabase, with the "
                 "same write-ahead log handling and millisecond time conversion. Activity Type (as stored) and "
                 "Transition (as stored) are the table's integer type and transition columns, reported as stored; "
                 "Life360 is closed source, so no mapping is applied. The column names match the fields of "
                 "Google's ActivityTransitionEvent, whose documented vocabulary is DetectedActivity IN_VEHICLE 0, "
                 "ON_BICYCLE 1, ON_FOOT 2, STILL 3, UNKNOWN 4, TILTING 5, WALKING 7 and RUNNING 8 with "
                 "ActivityTransition ENTER 0 and EXIT 1 (developers.google.com reference pages for "
                 "com.google.android.gms.location, read 2026-09-05). Every one of the 19 rows on the 3 tested "
                 "images held a type of 0, 3 or 7 with a transition of 0 or 1, and each exit shared its instant "
                 "with an enter. That match is an inference from the names and the value set, not a statement from "
                 "the app's code.",
        "paths": ('*/com.life360.android.safetymapd/databases/L360LocationLocalStoreRoomDatabase*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 11 rows",
            "hc_pixel8pro_a17": "Android 17 | 4 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no Life360 local stores | 0 rows",
            "pixel3_a12": "Android 12 | no Life360 local stores | 0 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "samsungs20_a13": "Android 13 | no Life360 local stores | 0 rows",
            "sharon_a14": "Android 14 | no Life360 local stores | 0 rows",
        },
    },
    "life360Geofences": {
        "name": "Life360 Geofences",
        "description": "Geofences the Life360 app holds in the geofence table of L360LocationLocalStoreRoomDatabase, each with its place id, radius and centre coordinates as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the geofence table of the same L360LocationLocalStoreRoomDatabase, with the same "
                 "write-ahead log handling. Geofence ID and Place ID are as stored (on every tested row the "
                 "geofence id is the place id with a _LOCAL suffix), Latitude and Longitude are placeLatitude and "
                 "placeLongitude, and Radius (as stored), Place Radius (as stored), Type (as stored) and End Time "
                 "(as stored) are kept as the values the app wrote: on all 10 rows of the 3 tested images Type was "
                 "LOCAL, End Time was 0, and Radius equalled Place Radius at 152.4. The place each fence belongs "
                 "to is reported by the Life360 Places artifact from L360LocalStoreRoomDatabase; this table lists "
                 "the fences the app held.",
        "paths": ('*/com.life360.android.safetymapd/databases/L360LocationLocalStoreRoomDatabase*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | 4 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no Life360 local stores | 0 rows",
            "pixel3_a12": "Android 12 | no Life360 local stores | 0 rows",
            "pixel7a_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | no Life360 local stores | 0 rows",
            "sharon_a14": "Android 14 | no Life360 local stores | 0 rows",
        },
    },
    "life360MemberDeviceLocations": {
        "name": "Life360 Member Device Locations",
        "description": "Last known location the Life360 app held for devices in the user's circles, from the device_locations table of MembersEngineRoomDatabase joined to the devices and members tables for the device name and owner.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the device_locations table of "
                 "com.life360.android.safetymapd/databases/MembersEngineRoomDatabase, joined to devices on "
                 "device_id for Device Name and Device OS (as stored) and to members on default_member_id and "
                 "circle_id for Owner Member; both joins resolved on all 6 rows of the 3 tested images. On one "
                 "tested image every row of this database sat only in the write-ahead log, so the -wal and -shm "
                 "sidecars are read with it. Last Observed and First Observed are the ISO 8601 UTC text the app "
                 "stored, converted, and Last Updated is a millisecond epoch. One row per device, the last "
                 "position the app held for it, not a history. Two app builds were seen: the newer one renames "
                 "battery_level and battery_charging to state_power_battery_level and "
                 "state_power_battery_charging, and the artifact reads whichever pair the store has (Battery Level "
                 "filled on all 6 rows); it also adds an app_version column, so App Version (as stored) is filled "
                 "only on the one image with that build (2 rows) and blank on the others. The newer build also "
                 "adds state_ columns for the device's connected Wi-Fi access point (SSID, BSSID, IPv4, RSSI), a "
                 "named place with a start time, online, nearby and tethering state and an activity type; every "
                 "one of them was empty on all rows of both images that have them, apart from "
                 "state_deviceUIFeature holding the text null, so they are not reported here and are the first "
                 "thing to check on an image where they are filled. In Transit (as stored) was 1 on 2 of the 6 "
                 "rows, User Activity (as stored) unknown on 5 and vehicle on 1, and Location Source (as stored) "
                 "was http and Wi-Fi Connected (as stored) 1 on all 6.",
        "paths": ('*/com.life360.android.safetymapd/databases/MembersEngineRoomDatabase*',),
        "output_types": "all",
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no Life360 local stores | 0 rows",
            "pixel3_a12": "Android 12 | no Life360 local stores | 0 rows",
            "pixel7a_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | no Life360 local stores | 0 rows",
            "sharon_a14": "Android 14 | no Life360 local stores | 0 rows",
        },
    },
    "life360CircleDevices": {
        "name": "Life360 Circle Devices",
        "description": "Devices recorded in the user's Life360 circles, from the devices table of MembersEngineRoomDatabase, with name, platform, OS version and owner ids as stored, and the hardware model where the schema carries it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "Read from the devices table of the same MembersEngineRoomDatabase, with Circle IDs from "
                 "device_circle_cross_ref and Owner IDs the userId values of the owners JSON list (filled on all "
                 "11 rows). Modified is the ISO 8601 UTC text the app stored and Last Updated a millisecond epoch "
                 "that held one value per image, the last refresh of the table. Device Type (as stored) was PHONE "
                 "and Provider (as stored) LIFE360 on all 11 rows of the 3 tested images, and Circle IDs held one "
                 "circle per image. Hardware Model (as stored) comes from type_hardware_model, present in the "
                 "older app build (3 rows on one image) and absent from the newer build's schema, so it is blank "
                 "on the other two images. Columns the schema carries but no tested row filled are not reported: "
                 "type_iccid, type_manufacturer, type_firmware_version, type_hardware_revision, type_lfid, "
                 "type_device_id, type_auth_key, the group id, name and avatar, category, activation_state and the "
                 "lost, dead and hidden state flags, plus the newer build's type_product_code and state_battery. "
                 "Members and circles are reported by the Life360 Members and Circles artifact; the device_issues "
                 "table (4 rows of type UNKNOWN with the values authorized and denied_modal) and the newer build's "
                 "members role column are not reported.",
        "paths": ('*/com.life360.android.safetymapd/databases/MembersEngineRoomDatabase*',),
        "output_types": "standard",
        "artifact_icon": "devices",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | 4 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no Life360 local stores | 0 rows",
            "pixel3_a12": "Android 12 | no Life360 local stores | 0 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "samsungs20_a13": "Android 13 | no Life360 local stores | 0 rows",
            "sharon_a14": "Android 14 | no Life360 local stores | 0 rows",
        },
    },
}

import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _sources(context, suffix):
    """Every distinct copy of the store named by suffix, one per app container."""
    return [f for f in unique_files(context)
            if str(f).endswith(suffix) and not str(f).endswith(('-wal', '-shm', '-journal'))
            and not os.path.isdir(f)]


def _ms(value):
    """A millisecond Unix epoch value as a UTC datetime; blank when not a positive number."""
    if isinstance(value, (int, float)) and value > 0:
        return _EPOCH + timedelta(milliseconds=value)
    return ''


def _iso(value):
    """An ISO 8601 text timestamp as a UTC datetime; blank when it does not parse."""
    if not value:
        return ''
    text = str(value).strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    m = re.match(r'^(.*\d{2}:\d{2}:\d{2})(\.\d+)?(.*)$', text)
    if m and m.group(2):
        text = m.group(1) + (m.group(2) + '000000')[:7] + m.group(3)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return ''
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _owner_ids(value):
    """User ids from the JSON owners list, joined; the raw text when it is not that shape."""
    try:
        items = json.loads(value) if value else []
    except ValueError:
        return value or ''
    if not isinstance(items, list):
        return value or ''
    ids = []
    for item in items:
        if isinstance(item, dict):
            ids.append(str(item.get('userId', item.get('id', ''))))
        else:
            ids.append(str(item))
    return ', '.join(i for i in ids if i)


def _columns(cursor, table):
    """The column names a table has in this copy of the store."""
    try:
        return {row[1] for row in cursor.execute(f'PRAGMA table_info("{table}")')}
    except sqlite3.Error:
        return set()


def _pick(have, alias, *names):
    """A SELECT expression for the first of names the table has, else NULL, under alias.

    Life360 renamed the device_locations battery fields under a state_power_ prefix and
    dropped type_hardware_model from devices between the tested app builds."""
    for name in names:
        if name in have:
            return f'"{name}" AS {alias}'
    return f'NULL AS {alias}'


def _query(cursor, sql):
    try:
        return cursor.execute(sql).fetchall()
    except sqlite3.Error as exc:
        logfunc(f'life360LocalStores: query failed: {exc}')
        return []


@artifact_processor
def life360DeviceLocationStore(context):
    data_list = []
    sources = []
    for source in _sources(context, 'L360LocationLocalStoreRoomDatabase'):
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        sources.append(source)
        rel = context.get_relative_path(source)
        for row in _query(db.cursor(), '''
            SELECT time, type, latitude, longitude, accuracy, speed, altitude, bearing, provider,
                   lmode, userActivity, batteryLevel, batteryCharging, wifiConnected, elapsedRealtimeNanos
            FROM location ORDER BY time'''):
            data_list.append((_ms(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9] if row[9] is not None else '', row[10], row[11],
                              row[12], row[13], row[14], rel))
        db.close()
    data_headers = (('Timestamp', 'datetime'), 'Sample Type (as stored)', 'Latitude', 'Longitude',
                    'Accuracy (as stored)', 'Speed (as stored)', 'Altitude (as stored)',
                    'Bearing (as stored)', 'Provider (as stored)', 'Location Mode (as stored)',
                    'User Activity (as stored)', 'Battery Level (as stored)',
                    'Battery Charging (as stored)', 'Wi-Fi Connected (as stored)',
                    'Elapsed Realtime Nanos (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def life360ActivityTransitions(context):
    data_list = []
    sources = []
    for source in _sources(context, 'L360LocationLocalStoreRoomDatabase'):
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        sources.append(source)
        rel = context.get_relative_path(source)
        for row in _query(db.cursor(), 'SELECT time, type, transition FROM activity_transition ORDER BY time, id'):
            data_list.append((_ms(row[0]), row[1], row[2], rel))
        db.close()
    data_headers = (('Timestamp', 'datetime'), 'Activity Type (as stored)',
                    'Transition (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def life360Geofences(context):
    data_list = []
    sources = []
    for source in _sources(context, 'L360LocationLocalStoreRoomDatabase'):
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        sources.append(source)
        rel = context.get_relative_path(source)
        for row in _query(db.cursor(), '''
            SELECT id, placeId, type, radius, placeRadius, placeLatitude, placeLongitude, endTime
            FROM geofence'''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], rel))
        db.close()
    data_headers = ('Geofence ID', 'Place ID', 'Type (as stored)', 'Radius (as stored)',
                    'Place Radius (as stored)', 'Latitude', 'Longitude', 'End Time (as stored)',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def life360MemberDeviceLocations(context):
    data_list = []
    sources = []
    for source in _sources(context, 'MembersEngineRoomDatabase'):
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        sources.append(source)
        rel = context.get_relative_path(source)
        cursor = db.cursor()
        have = _columns(cursor, 'device_locations')
        sub = ', '.join((
            _pick(have, 'battery_level', 'battery_level', 'state_power_battery_level'),
            _pick(have, 'battery_charging', 'battery_charging', 'state_power_battery_charging'),
            _pick(have, 'app_version', 'app_version')))
        for row in _query(cursor, f'''
            SELECT dl.last_observed, dl.first_observed, dl.last_updated, d.name, d.type_os,
                   TRIM(COALESCE(m.first_name, '') || ' ' || COALESCE(m.last_name, '')),
                   dl.default_member_id, dl.device_id, dl.circle_id, dl.latitude, dl.longitude,
                   dl.accuracy, dl.speed, dl.in_transit, dl.battery_level, dl.battery_charging,
                   dl.wifi_connected, dl.user_activity, dl.location_source, dl.app_version
            FROM (SELECT *, {sub} FROM device_locations) dl
            LEFT JOIN devices d ON d.device_id = dl.device_id
            LEFT JOIN members m ON m.id = dl.default_member_id AND m.circle_id = dl.circle_id
            ORDER BY dl.last_observed'''):
            data_list.append((_iso(row[0]), _iso(row[1]), _ms(row[2]), row[3] or '', row[4] or '',
                              row[5] or '', row[6], row[7], row[8], row[9], row[10], row[11],
                              row[12], row[13], row[14], row[15], row[16], row[17] or '',
                              row[18] or '', row[19] or '', rel))
        db.close()
    data_headers = (('Last Observed', 'datetime'), ('First Observed', 'datetime'),
                    ('Last Updated', 'datetime'), 'Device Name', 'Device OS (as stored)',
                    'Owner Member', 'Member ID', 'Device ID', 'Circle ID', 'Latitude', 'Longitude',
                    'Accuracy (as stored)', 'Speed (as stored)', 'In Transit (as stored)',
                    'Battery Level (as stored)', 'Battery Charging (as stored)',
                    'Wi-Fi Connected (as stored)', 'User Activity (as stored)',
                    'Location Source (as stored)', 'App Version (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def life360CircleDevices(context):
    data_list = []
    sources = []
    for source in _sources(context, 'MembersEngineRoomDatabase'):
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        sources.append(source)
        rel = context.get_relative_path(source)
        cursor = db.cursor()
        have = _columns(cursor, 'devices')
        hw = _pick(have, 'type_hardware_model', 'type_hardware_model')
        for row in _query(cursor, f'''
            SELECT d.modified, d.last_updated, d.device_id, d.name, d.type, d.provider, d.type_os,
                   d.type_os_version, d.type_hardware_model, d.owners, d.avatar,
                   (SELECT GROUP_CONCAT(x.circle_id, ', ') FROM device_circle_cross_ref x
                     WHERE x.device_id = d.device_id)
            FROM (SELECT *, {hw} FROM devices) d ORDER BY d.modified'''):
            data_list.append((_iso(row[0]), _ms(row[1]), row[2], row[3] or '', row[4] or '',
                              row[5] or '', row[6] or '', row[7] or '', row[8] or '',
                              _owner_ids(row[9]), row[10] or '', row[11] or '', rel))
        db.close()
    data_headers = (('Modified', 'datetime'), ('Last Updated', 'datetime'), 'Device ID',
                    'Device Name', 'Device Type (as stored)', 'Provider (as stored)',
                    'OS (as stored)', 'OS Version (as stored)', 'Hardware Model (as stored)',
                    'Owner IDs', 'Avatar URL', 'Circle IDs', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
