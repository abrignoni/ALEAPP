# pylint: disable=W0613
__artifacts_v2__ = {
    'Life360_Drives': {
        'name': 'Life360 Drives',
        'description': 'Parses Life360 Drives',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-10',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/DriveBladeDB*',),
        'output_types': 'standard',
        'artifact_icon': 'map-pin'
    },
    'Life360_DriveEvents': {
        'name': 'Life360 Drive Events (DriveBladeDB)',
        'description': 'Parses Life360 Drive Events (DriveBladeDB)',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-10',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/DriveBladeDB*',),
        'output_types': ['html', 'tsv', 'lava', 'kml'],
        'artifact_icon': 'map-pin'
    },
    'Life360_DriveWaypoints': {
        'name': 'Life360 Drive Waypoints',
        'description': 'Parses Life360 Drive Waypoints',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-10',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/DriveBladeDB*',),
        'output_types': ['html', 'tsv', 'lava', 'kml'],
        'artifact_icon': 'map-pin'
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
def Life360_Drives(context):
    source = _find(context, 'DriveBladeDB')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                driveId,
                userId,
                startTime,
                endTime,
                topSpeed,
                topSpeed * 2.23694,
                averageSpeed,
                averageSpeed * 2.23694,
                distance,
                duration,
                speedingCount,
                hardBrakingCount,
                rapidAccelerationCount,
                distractedCount,
                crashCount,
                score,
                updatedAt
            FROM Drives
            ORDER BY startTime
        '''):
            data_list.append((
                row[0], row[1],
                _ms_to_utc(row[2]), _ms_to_utc(row[3]),
                row[4], row[5], row[6], row[7],
                row[8], row[9],
                row[10], row[11], row[12], row[13], row[14],
                row[15], _ms_to_utc(row[16])
            ))
        db.close()

    data_headers = (
        'Drive ID', 'User ID',
        ('Start Time', 'datetime'), ('End Time', 'datetime'),
        'Top Speed MPS', 'Top Speed MPH',
        'Average Speed MPS', 'Average Speed MPH',
        'Distance', 'Duration',
        'Speeding Events', 'Hard Braking Events',
        'Rapid Acceleration Events', 'Distracted Events', 'Crash Events',
        'Score', ('Updated At', 'datetime')
    )
    return data_headers, data_list, source


@artifact_processor
def Life360_DriveEvents(context):
    source = _find(context, 'DriveBladeDB')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                DriveEvents.eventId,
                DriveEvents.driveId,
                Drives.userId,
                DriveEvents.eventTime,
                DriveEvents.eventType,
                DriveEvents.lat,
                DriveEvents.lon,
                DriveEvents.speed,
                DriveEvents.speed * 2.23694,
                DriveEvents.accuracy
            FROM DriveEvents
            LEFT JOIN Drives ON Drives.driveId = DriveEvents.driveId
            ORDER BY DriveEvents.eventTime
        '''):
            data_list.append((
                row[0], row[1], row[2],
                _ms_to_utc(row[3]),
                row[4], row[5], row[6],
                row[7], row[8], row[9]
            ))
        db.close()

    data_headers = (
        'Event ID', 'Drive ID', 'User ID',
        ('Event Time', 'datetime'),
        'Event Type', 'Latitude', 'Longitude',
        'Speed MPS', 'Speed MPH', 'Accuracy'
    )
    return data_headers, data_list, source


@artifact_processor
def Life360_DriveWaypoints(context):
    source = _find(context, 'DriveBladeDB')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                DriveWaypoints.driveId,
                Drives.userId,
                DriveWaypoints.timestamp,
                DriveWaypoints.lat,
                DriveWaypoints.lon,
                DriveWaypoints.speed,
                DriveWaypoints.speed * 2.23694,
                DriveWaypoints.accuracy
            FROM DriveWaypoints
            LEFT JOIN Drives ON Drives.driveId = DriveWaypoints.driveId
            ORDER BY DriveWaypoints.timestamp
        '''):
            data_list.append((
                row[0], row[1],
                _ms_to_utc(row[2]),
                row[3], row[4],
                row[5], row[6], row[7]
            ))
        db.close()

    data_headers = (
        'Drive ID', 'User ID',
        ('Timestamp', 'datetime'),
        'Latitude', 'Longitude',
        'Speed MPS', 'Speed MPH', 'Accuracy'
    )
    return data_headers, data_list, source
