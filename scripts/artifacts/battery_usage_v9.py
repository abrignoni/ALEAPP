__artifacts_v2__ = {
    "get_battery_usage_v9": {
        "name": "Settings Services - Battery Usage - Battery States",
        "description": "Battery usage states from the Settings battery-usage-db-v<number> "
                       "databases; v9, v10 and v11 were tested (seen on Android 14 to 17 "
                       "images).",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-05-12",
        "last_update_date": "2026-11-17",
        "requirements": "blackboxprotobuf",
        "category": "Device Information",
        "notes": "First based on the Android 14 post "
                 "https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html."
                 " The databases are read by file name battery-usage-db-v<number> with their "
                 "write-ahead log; the BatteryState and AppUsageEventEntity columns read are "
                 "the same in v9, v10 and v11 on the tested images. When more than one such "
                 "database is found, a Source File column names the database of each row. "
                 "Field names come from the Settings proto BatteryInformation "
                 "(fuelgauge_usage_state.proto at android-14.0.0_r1 and android-16.0.0_r1; "
                 "the only difference is field 20). Battery Status is labelled on the reading"
                 " that the stored code, which the proto names battery_status (int32), holds "
                 "the AOSP BatteryManager status constants (1 Unknown, 2 Charging, 3 "
                 "Discharging, 4 Not Charging, 5 Fully charged); any other code is reported "
                 "as the raw number. No source for its value set is cited here. Battery "
                 "Health is labelled with this module's map 1 Unknown, 2 Good, 3 Overheat, 4 "
                 "Dead, 5 Over Voltage, 6 Unspecified Failure and 7 Cold, with unmapped "
                 "present codes marked Unmapped and absent codes left blank. Raw decoded "
                 "status and health values are kept in their own columns; the proto names the"
                 " fields battery_status and battery_health, and the value labels are this "
                 "module's reading. Proto field 20 is retained raw beside the existing "
                 "numeric /1000 result; the Android 16 source defines it as "
                 "foreground_service_usage_time_in_ms, android-14.0.0_r1 does not define it "
                 "and android-14.0.0_r50 and later do; russell_a14 carries it on every row "
                 "and pixel7a_a14 on none. Total Power and Consumed Power are proto fields 10"
                 " and 11 (total_power and consume_power, doubles), read as doubles, and fall"
                 " back to the batteryInformationDebug text, then NOVALUE, when a record "
                 "lacks them; the debug-text fallback supplied no value on any tested image. "
                 "batteryInformationDebug was NULL on every row of the six phone images. On "
                 "the two Android 15 emulator images the records carry neither field and "
                 "their debug text has no total_power or consume_power line, so those columns"
                 " read NOVALUE there. Proto 1.3 (stored health) held 2 on every row of "
                 "russell_a14 and dragna_pixel9a_a16. Boot Timestamp retains its existing "
                 "numeric /1000 conversion. A row whose batteryInformation value does not "
                 "decode is not reported. Reference: AOSP, 'BatteryManager status constants',"
                 " https://developer.android.com/reference/android/os/BatteryManager",
        "paths": ('*/user_de/*/com.android.settings/databases/battery-usage-db-v*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.android.settings | 19163 rows",
            "emu_a15_oss2_v3": "Android 15 | com.android.settings | 229 rows",
            "emu_a15_oss_v17": "Android 15 | com.android.settings | 344 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.settings | 9944 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.settings | 29899 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.settings | 24918 rows",
            "pixel7a_a14": "Android 14 | com.android.settings | 26561 rows",
            "russell_a14": "Android 14 | com.android.settings | 32018 rows",
        },
    },
    "get_app_usage_events": {
        "name": "Settings Services - Battery Usage - App Usage Events",
        "description": "App usage events from the AppUsageEventEntity table of the Settings "
                       "battery-usage-db-v<number> databases; v9, v10 and v11 were tested "
                       "(seen on Android 14 to 17 images).",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Claude",
        "creation_date": "2024-05-12",
        "last_update_date": "2026-11-17",
        "requirements": "blackboxprotobuf",
        "category": "Device Information",
        "notes": "Getting App Battery Usage Event from Settings Services - Based on "
                 "https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html."
                 " App Usage Event Type decodes the AppUsageEventEntity.appUsageEventType "
                 "values defined by the Settings app usage event proto, 0 Unknown, 1 Activity"
                 " Resumed, 2 Activity Stopped and 3 Device Shutdown; any other code is "
                 "reported as the raw number. Codes 4 and 5 occur on dragna_pixel9a_a16, "
                 "hc_pixel8pro_a16 and hc_pixel8pro_a17; the AOSP proto does not define them "
                 "at android-16.0.0_r1, and they are reported as stored. The proto is the "
                 "same at android-16.0.0_r1. The databases are read by file name "
                 "battery-usage-db-v<number> with their write-ahead log; on "
                 "dragna_pixel9a_a16 the v11 file without its log held 775 of the 791 events."
                 " When more than one such database is found, a Source File column names the "
                 "database of each row. Reference: AOSP Settings, 'app_usage_event.proto', "
                 "https://android.googlesource.com/platform/packages/apps/Settings/+/refs/tags/android-14.0.0_r1/src/com/android/settings/fuelgauge/protos/app_usage_event.proto#7",
        "paths": ('*/user_de/*/com.android.settings/databases/battery-usage-db-v*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.android.settings | 791 rows",
            "emu_a15_oss2_v3": "Android 15 | com.android.settings | 1075 rows",
            "emu_a15_oss_v17": "Android 15 | com.android.settings | 3411 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.settings | 1069 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.settings | 420 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.settings | 1431 rows",
            "pixel7a_a14": "Android 14 | com.android.settings | 3196 rows",
            "russell_a14": "Android 14 | com.android.settings | 629 rows",
        },
    }
}

import base64
import datetime
import os
import re
import sqlite3
import struct

from scripts.artifacts.storagePathViews import unique_files

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_STATUS = {1: 'Unknown', 2: 'Charging', 3: 'Discharging', 4: 'Not Charging', 5: 'Fully charged'}
_HEALTH = {1: 'Unknown', 2: 'Good', 3: 'Overheat', 4: 'Dead', 5: 'Over Voltage',
           6: 'Unspecified Failure', 7: 'Cold'}


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _as_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _status(value):
    '''Battery status name from the BatteryManager set; the raw code when unrecognized.'''
    code = _as_int(value)
    if code is None:
        return ''
    return _STATUS.get(code, code)


def _txt(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return value if value is not None else ''


def _ms_field(proto, key):
    '''Optional numeric proto field divided by 1000; '' when the field is absent.'''
    value = proto.get(key)
    return value / 1000 if isinstance(value, (int, float)) else ''


def _double(proto, key, fallback):
    '''A proto double field the schema-less decoder returned as a 64-bit integer, or fallback.'''
    value = proto.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        return fallback
    return struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]


def _parse_debug(text):
    out = {}
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    for line in (text or '').split('\n'):
        parts = line.split(':', 1)
        if len(parts) == 2:
            out[parts[0].strip()] = parts[1].strip().replace('"', '')
    return out


_DB_NAME = re.compile(r'battery-usage-db-v\d+$')


def _dbs(context):
    """Every battery-usage-db-v<number> found, one copy per file (storage views merged)."""
    return [str(f) for f in unique_files(context)
            if _DB_NAME.match(os.path.basename(str(f)))]


def _per_db(context, rows_of):
    """rows_of(db) for each database, with a Source File column when there are several."""
    dbs = _dbs(context)
    data_list = []
    for db in dbs:
        rows = rows_of(db)
        if len(dbs) > 1:
            relative = context.get_relative_path(db)
            rows = [tuple(row) + (relative,) for row in rows]
        data_list.extend(rows)
    return dbs, data_list


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_battery_usage_v9(context):
    dbs, data_list = _per_db(context, _battery_rows)
    data_headers = (('Timestamp', 'datetime'), 'Boot Timestamp', 'Application', 'Package Name',
                    'Hidden', 'Timezone', 'Total Power', 'Consumed Power',
                    'Foreground Usage (Seconds)', 'Proto Field 20 (as decoded)',
                    'Proto Field 20 / 1000 (derived)', 'Background Usage (Seconds)',
                    'Battery Level (%)', 'Proto 1.2 (stored status)',
                    'Battery Status (existing interpretation)', 'Proto 1.3 (stored health)',
                    'Battery Health (existing interpretation)', 'Drain Type')
    if len(dbs) > 1:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(dbs)


def _battery_rows(source_path):
    data_list = []
    rows = _run(source_path, '''
        SELECT uid, packageName, timestamp, consumerType, isFullChargeCycleStart,
        batteryInformation, batteryInformationDebug
        FROM BatteryState
    ''')
    for row in rows:
        try:
            proto, _ = decode_protobuf(base64.b64decode(row[5]))
        except Exception:  # pylint: disable=W0718
            continue
        if not isinstance(proto, dict):
            continue
        info = proto.get('1') if isinstance(proto.get('1'), dict) else {}
        debug = _parse_debug(row[6])
        data_list.append((
            _ms_to_utc(row[2]),
            _ms_field(proto, '3'),                             # Existing Boot Timestamp
            _txt(proto.get('7')),                              # Application label
            row[1],                                            # Package Name
            _txt(proto.get('2')),                              # Hidden
            _txt(proto.get('4')),                              # Timezone
            _double(proto, '10', debug.get('total_power', 'NOVALUE')),
            _double(proto, '11', debug.get('consume_power', 'NOVALUE')),
            _ms_field(proto, '14'),                            # Foreground
            proto.get('20'),                                  # Raw decoded field
            _ms_field(proto, '20'),                            # Existing arithmetic only
            _ms_field(proto, '15'),                            # Background
            info.get('1', ''),                                 # Battery Level
            info.get('2'),
            _status(info.get('2')),                            # Battery Status
            info.get('3'),
            _HEALTH.get(_as_int(info.get('3')), 'Unmapped') if info.get('3') is not None else '',       # Battery Health
            _txt(proto.get('13'))))                            # Drain Type
    return data_list


@artifact_processor
def get_app_usage_events(context):
    dbs, data_list = _per_db(context, _app_usage_rows)
    data_headers = (('Timestamp', 'datetime'), 'App Usage Event Type', 'Package Name',
                    'Root Package Name', 'uid', 'userId', 'Instance Id')
    if len(dbs) > 1:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(dbs)


def _app_usage_rows(source_path):
    rows = _run(source_path, '''
        SELECT uid, userId, timestamp,
        CASE appUsageEventType WHEN 0 THEN 'Unknown' WHEN 1 THEN 'Activity Resumed'
                               WHEN 2 THEN 'Activity Stopped' WHEN 3 THEN 'Device Shutdown'
                               ELSE appUsageEventType END,
        packageName, taskRootPackageName, instanceId
        FROM AppUsageEventEntity
    ''')
    return [(_ms_to_utc(r[2]), r[3], r[4], r[5], r[0], r[1], r[6]) for r in rows]
