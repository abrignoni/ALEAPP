__artifacts_v2__ = {
    "get_battery_usage_v9": {
        "name": "Settings Services - Battery Usages v9 - Battery States",
        "description": "Getting Battery Usage data out of the database battery-usage-db-v9. Introduced with Android 14",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-05-12",
        "last_update_date": "2024-05-12",
        "requirements": "blackboxprotobuf",
        "category": "Settings Services - Battery Usage v9 - Battery States",
        "notes": "Getting battery usage data from Settings Services - Android 14 - Based on post https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html",
        "paths": ('*/user_de/*/com.android.settings/databases/battery-usage-db-v9',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.android.settings | 26561 rows",
        },
    },
    "get_app_usage_events": {
        "name": "Settings Services - App Battery Usages v9 - App Battery Usage Events",
        "description": "Getting Battery Usage data out of the database battery-usage-db-v9. Introduced with Android 14",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-05-12",
        "last_update_date": "2024-05-12",
        "requirements": "blackboxprotobuf",
        "category": "Settings Services - Battery Usage v9 - App Battery Usage Events",
        "notes": "Getting App Battery Usage Event from Settings Services - Based on https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html",
        "paths": ('*/user_de/*/com.android.settings/databases/battery-usage-db-v9',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.android.settings | 3196 rows",
        },
    }
}

import base64
import datetime
import sqlite3

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly
from scripts.context import Context

_STATUS = {2: 'Charging', 3: 'Discharging', 5: 'Fully charged'}
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


def _txt(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return value if value is not None else ''


def _ms_field(proto, key):
    '''Optional numeric proto field divided by 1000; '' when the field is absent.'''
    value = proto.get(key)
    return value / 1000 if isinstance(value, (int, float)) else ''


def _parse_debug(text):
    out = {}
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    for line in (text or '').split('\n'):
        parts = line.split(':', 1)
        if len(parts) == 2:
            out[parts[0].strip()] = parts[1].strip().replace('"', '')
    return out


def _db(files_found):
    for file_found in files_found:
        if str(file_found).endswith('battery-usage-db-v9'):
            return str(file_found)
    return ''


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
    files_found = context.get_files_found()
    source_path = _db(files_found)
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
            _txt(proto.get('7')),                              # Application label
            row[1],                                            # Package Name
            _txt(proto.get('2')),                              # Hidden
            _ms_field(proto, '3'),                             # Boot Timestamp
            _txt(proto.get('4')),                              # Timezone
            debug.get('total_power', 'NOVALUE'),
            debug.get('consume_power', 'NOVALUE'),
            _ms_field(proto, '14'),                            # Foreground
            _ms_field(proto, '20'),                            # Foreground Service (optional - was KeyError)
            _ms_field(proto, '15'),                            # Background
            info.get('1', ''),                                 # Battery Level
            _STATUS.get(_as_int(info.get('2')), 'Unknown'),    # Battery Status
            _HEALTH.get(_as_int(info.get('3')), 'None'),       # Battery Health
            _txt(proto.get('13')),                             # Drain Type
            Context.get_relative_path(source_path)))

    data_headers = (('Timestamp', 'datetime'), 'Application', 'Package Name', 'Hidden',
                    'Boot Timestamp', 'Timezone', 'Total Power', 'Consumed Power',
                    'Foreground Usage (Seconds)', 'Foreground Service Usage (seconds)',
                    'Background Usage (Seconds)', 'Battery Level (%)', 'Battery Status',
                    'Battery Health', 'Drain Type', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_app_usage_events(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT uid, userId, timestamp,
        CASE appUsageEventType WHEN 1 THEN 'Paused' WHEN 2 THEN 'Resumed' END,
        packageName, taskRootPackageName, instanceId
        FROM AppUsageEventEntity
    ''')
    data_list = [(r[0], r[1], _ms_to_utc(r[2]), r[3], r[4], r[5], r[6], Context.get_relative_path(source_path)) for r in rows]
    data_headers = ('uid', 'userId', ('Timestamp', 'datetime'), 'App Usage Event Type',
                    'Package Name', 'Root Package Name', 'Instance Id', 'Source File')
    return data_headers, data_list, source_path
