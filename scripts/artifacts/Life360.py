# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Life360_chat_messages": {
        "name": "Life360 - Chat Messages",
        "description": "Parses Life360 chat messages (messaging.db)",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-17",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.android.safetymapd/databases/messaging.db*',),
        "output_types": "all",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Sent",
                "directionSentValue": "Yes",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name"
            }
        },
    },
    "get_Life360_places": {
        "name": "Life360 - Places",
        "description": "Parses Life360 saved places (L360LocalStoreRoomDatabase)",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-17",
        "last_update_date": "2024-01-17",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.android.safetymapd/databases/L360LocalStoreRoomDatabase*',),
        "output_types": ['html', 'tsv', 'lava', 'kml'],
        "artifact_icon": "map-pin",
    },
    "get_Life360_locations": {
        "name": "Life360 - Locations",
        "description": "Parses Life360 device geolocation events (L360EventStore.db)",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-17",
        "last_update_date": "2024-01-17",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.android.safetymapd/databases/L360EventStore.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "get_Life360_device_battery": {
        "name": "Life360 - Device Battery",
        "description": "Parses Life360 device battery events (L360EventStore.db)",
        "author": "@KevinPagano3",
        "creation_date": "2024-01-17",
        "last_update_date": "2024-01-17",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.android.safetymapd/databases/L360EventStore.db*',),
        "output_types": "standard",
        "artifact_icon": "battery",
    }
}

import datetime
import json
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(files_found, suffix):
    for file_found in files_found:
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


def _ble_events(file_found):
    """Parse the BLE geolocation/battery events from L360EventStore.db into dicts."""
    rows = []
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    # Filter to BLE events in Python (json_extract in SQL errors on any malformed-JSON row).
    for data, ev_id in _q(cursor, 'SELECT data, id FROM event WHERE eventVersion = 5'):
        try:
            j = json.loads(data)
        except (ValueError, TypeError):
            continue
        if j.get('tag') != 'BLE':
            continue
        loc = j.get('locationData') or {}
        meta = j.get('metaData') or {}
        wifi = (meta.get('wifiData') or {}).get('connectedAccessPoint') or {}
        rows.append({
            'time': _ms_to_utc(loc.get('time')),
            'lat': loc.get('latitude', ''), 'lon': loc.get('longitude', ''),
            'alt': loc.get('altitude', ''), 'speed': loc.get('speed', ''),
            'course': loc.get('course', ''), 'bearing': loc.get('bearing', ''),
            'vert': loc.get('verticalAccuracy', ''), 'hor': loc.get('horizontalAccuracy', ''),
            'lmode': meta.get('lmode', ''), 'battery': meta.get('battery', ''),
            'charging': meta.get('chargingState', ''),
            'bssid': wifi.get('bssid', ''),
            'ssid': (wifi.get('ssid', '') or '').replace('"', ''),
            'id': ev_id,
        })
    db.close()
    return rows


@artifact_processor
def get_Life360_chat_messages(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'messaging.db')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            message.created_at,
            message.thread_id,
            message.sender_id,
            thread_participant.participant_name,
            message.content,
            CASE message.sent WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.read WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.dismissed WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.deleted WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.has_location WHEN 1 THEN 'Yes' ELSE '' END,
            message.location_latitude,
            message.location_longitude,
            message.location_name,
            message.location_timestamp
        FROM message
        LEFT JOIN thread_participant ON message.sender_id = thread_participant.participant_id
        ''')
        for row in rows:
            data_list.append((_sec_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              row[7], row[8], row[9], row[10], row[11], row[12], _sec_to_utc(row[13]),
                              source))
        db.close()

    data_headers = (('Timestamp', 'datetime'), 'Thread ID', 'Sender ID', 'Sender Name', 'Message',
                    'Message Sent', 'Message Read', 'Message Dismissed', 'Message Deleted',
                    'Has Location', 'Latitude', 'Longitude', 'Location Name',
                    ('Location Timestamp', 'datetime'), 'Source File')
    return data_headers, data_list, source


@artifact_processor
def get_Life360_places(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'L360LocalStoreRoomDatabase')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        for row in _q(cursor, '''SELECT name, latitude, longitude, radius, source, source_id, owner_id
                FROM places'''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], source))
        db.close()

    data_headers = ('Place Name', 'Latitude', 'Longitude', 'Radius (m)', 'Places Source', 'Source ID',
                    'Owner ID', 'Source File')
    return data_headers, data_list, source


@artifact_processor
def get_Life360_locations(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'L360EventStore.db')
    data_list = []
    if source:
        for e in _ble_events(source):
            data_list.append((e['time'], e['lat'], e['lon'], e['alt'], e['speed'], e['course'],
                              e['bearing'], e['vert'], e['hor'], e['lmode'], e['bssid'], e['ssid'],
                              e['id'], source))

    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude', 'Speed (mps)',
                    'Course', 'Bearing', 'Vertical Accuracy (+/- m)', 'Horizontal Accuracy (+/- m)',
                    'Location Mode', 'Connected Access Point BSSID', 'Connected Access Point SSID',
                    'ID', 'Source File')
    return data_headers, data_list, source


@artifact_processor
def get_Life360_device_battery(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'L360EventStore.db')
    data_list = []
    if source:
        for e in _ble_events(source):
            data_list.append((e['time'], e['battery'], e['charging'], source))

    data_headers = (('Timestamp', 'datetime'), 'Device Battery (%)', 'Charging', 'Source File')
    return data_headers, data_list, source
