__artifacts_v2__ = {
    'Life360_Locations': {
        'name': 'Life360 Locations',
        'description': 'Parses Life360 Location Events',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-30',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360EventStore_service.db*',),
        'output_types': ['html', 'tsv', 'lava', 'kml'],
        'artifact_icon': 'map-pin'
    },
    'Life360_Waypoints': {
        'name': 'Life360 Waypoints',
        'description': 'Parses Life360 Waypoints',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-30',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360EventStore_service.db*',),
        'output_types': ['html', 'tsv', 'lava', 'kml'],
        'artifact_icon': 'map-pin'
    },
    'Life360_BatteryLevel': {
        'name': 'Life360 Battery Level',
        'description': 'Parses Life360 Battery Level Events',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-30',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360EventStore_service.db*',),
        'output_types': 'standard',
        'artifact_icon': 'battery-charging'
    },
    'Life360_Drive_Events': {
        'name': 'Life360 Drive Events (EventStore)',
        'description': 'Parses Life360 Drive Events (EventStore)',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-30',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360EventStore_service.db*',),
        'output_types': ['html', 'tsv', 'lava', 'kml'],
        'artifact_icon': 'truck'
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(context, suffix):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(suffix):
            return file_found
    return ''


def _q(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


@artifact_processor
def Life360_Locations(context):
    source = _find(context, 'L360EventStore_service.db')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                json_extract(event.data, '$.locationData.time') AS timestamp,
                json_extract(event.data, '$.locationData.latitude') AS latitude,
                json_extract(event.data, '$.locationData.longitude') AS longitude,
                json_extract(event.data, '$.locationData.horizontalAccuracy') AS horizontal_accuracy,
                json_extract(event.data, '$.locationData.speed') AS speed_mps,
                json_extract(event.data, '$.locationData.speed') * 2.23694 AS speed_mph,
                json_extract(event.data, '$.locationData.speedAccuracy') AS speed_accuracy
            FROM event
            WHERE eventVersion = 6
            ORDER BY timestamp
        '''):
            data_list.append((
                _ms_to_utc(row[0]),
                row[1], row[2], row[3],
                row[4], row[5], row[6]
            ))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude',
        'Horizontal Accuracy', 'Speed MPS', 'Speed MPH', 'Speed Accuracy'
    )
    return data_headers, data_list, source


@artifact_processor
def Life360_Waypoints(context):
    source = _find(context, 'L360EventStore_service.db')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                json_extract(event.data, '$.tripId') AS trip_id,
                json_extract(json_each.value, '$.timestamp') AS timestamp,
                json_extract(json_each.value, '$.latitude') AS latitude,
                json_extract(json_each.value, '$.longitude') AS longitude,
                json_extract(json_each.value, '$.accuracy') AS accuracy,
                json_extract(json_each.value, '$.speed') AS speed_mps,
                json_extract(json_each.value, '$.speed') * 2.23694 AS speed_mph
            FROM event,
                json_each(event.data, '$.type.waypoints')
            WHERE event.eventVersion IN (1, 3, 4, 5)
            ORDER BY timestamp
        '''):
            data_list.append((
                row[0],
                _ms_to_utc(row[1]),
                row[2], row[3], row[4],
                row[5], row[6]
            ))
        db.close()

    data_headers = (
        'Trip ID', ('Timestamp', 'datetime'),
        'Latitude', 'Longitude', 'Accuracy',
        'Speed MPS', 'Speed MPH'
    )
    return data_headers, data_list, source


@artifact_processor
def Life360_BatteryLevel(context):
    source = _find(context, 'L360EventStore_service.db')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT DISTINCT
                timestamp,
                CASE
                    WHEN eventVersion IN (1, 2)
                    THEN json_extract(event.data, '$.batteryLevel')
                    WHEN eventVersion = 6
                    THEN json_extract(event.data, '$.metaData.battery')
                END AS battery_level,
                CASE
                    WHEN eventVersion IN (1, 2) THEN
                        CASE
                            WHEN json_extract(event.data, '$.chargingState') = 1 THEN 'True'
                            WHEN json_extract(event.data, '$.chargingState') = 0 THEN 'False'
                            ELSE NULL
                        END
                    WHEN eventVersion = 6 THEN
                        CASE
                            WHEN json_extract(event.data, '$.metaData.chargingState') = 1 THEN 'True'
                            WHEN json_extract(event.data, '$.metaData.chargingState') = 0 THEN 'False'
                            ELSE NULL
                        END
                END AS charging_state,
                CASE
                    WHEN eventVersion = 2
                    THEN json_extract(event.data, '$.powerMode')
                    ELSE NULL
                END AS power_mode
            FROM event
            WHERE eventVersion IN (1, 2, 6)
              AND (data LIKE '%batteryLevel%' OR data LIKE '%metaData%')
            ORDER BY timestamp
        '''):
            data_list.append((
                _ms_to_utc(row[0]),
                row[1], row[2], row[3]
            ))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Battery Level', 'Charging State', 'Power Mode'
    )
    return data_headers, data_list, source


@artifact_processor
def Life360_Drive_Events(context):
    source = _find(context, 'L360EventStore_service.db')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                json_extract(event.data, '$.tripId') AS trip_id,
                json_extract(json_each.value, '$.timestamp') AS timestamp,
                json_extract(json_each.value, '$.latitude') AS latitude,
                json_extract(json_each.value, '$.longitude') AS longitude,
                json_extract(json_each.value, '$.type') AS type
            FROM event,
                json_each(event.data, '$.type.driveEvents')
            WHERE event.eventVersion IN (3, 4, 5)
            ORDER BY timestamp
        '''):
            data_list.append((
                row[0],
                _ms_to_utc(row[1]),
                row[2], row[3], row[4]
            ))
        db.close()

    data_headers = (
        'Trip ID', ('Timestamp', 'datetime'),
        'Latitude', 'Longitude', 'Type'
    )
    return data_headers, data_list, source
