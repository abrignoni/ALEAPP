__artifacts_v2__ = {
    "get_airGuard": {
        "name": "AirGuard AirTag Tracker",
        "description": "Parses tracker detections from the AirGuard AirTag app",
        "author": "@AlexisBrignoni",
        "creation_date": "2022-01-08",
        "last_update_date": "2022-01-08",
        "requirements": "none",
        "category": "AirTags",
        "notes": "",
        "paths": ('*/de.seemoo.at_tracking_detection.release/databases/attd_db*',),
        "output_types": "all",
        "artifact_icon": "shield",
        "sample_data": {
            "russell_pixel6a_a13": "Android 13 | de.seemoo.at_tracking_detection.release vc 37 | 1960 rows",
        },
    },
    "get_airGuard_scans": {
        "name": "AirGuard AirTag Scans",
        "description": "Parses scan history from the AirGuard AirTag app",
        "author": "@AlexisBrignoni",
        "creation_date": "2022-01-08",
        "last_update_date": "2022-01-08",
        "requirements": "none",
        "category": "AirTags",
        "notes": "",
        "paths": ('*/de.seemoo.at_tracking_detection.release/databases/attd_db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "russell_pixel6a_a13": "Android 13 | de.seemoo.at_tracking_detection.release vc 37 | 805 rows",
        },
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db


def _iso_to_utc(value):
    if value is None:
        return ''
    text = str(value)
    if not text or text == 'None':
        return ''
    try:
        parsed = datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return ''
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _attd_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('attd_db'):
            return file_found
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
def get_airGuard(context):
    files_found = context.get_files_found()
    source_path = _attd_db(files_found)
    # Older databases keep latitude/longitude on the beacon table; newer ones use a location table
    if source_path and does_table_exist_in_db(source_path, 'location'):
        coords = 'location.latitude, location.longitude'
        coord_join = 'LEFT JOIN location ON location.locationId = beacon.locationId'
    else:
        coords = 'beacon.latitude, beacon.longitude'
        coord_join = ''
    rows = _run(source_path, f'''
        SELECT device.lastSeen, beacon.receivedAt, beacon.deviceAddress, {coords}, beacon.rssi,
        device.deviceType, device.firstDiscovery, device.lastNotificationSent
        FROM beacon
        LEFT JOIN device ON device.address = beacon.deviceAddress
        {coord_join}
    ''')
    data_list = [(_iso_to_utc(r[0]), _iso_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6],
                  _iso_to_utc(r[7]), _iso_to_utc(r[8])) for r in rows]
    data_headers = (('Timestamp', 'datetime'), ('Received Time', 'datetime'), 'Device MAC Address',
                    'Latitude', 'Longitude', 'Signal Strength (RSSI)', 'Device Type',
                    ('First Time Device Seen', 'datetime'), ('Last Time User Notified', 'datetime'))
    return data_headers, data_list, source_path


@artifact_processor
def get_airGuard_scans(context):
    files_found = context.get_files_found()
    source_path = _attd_db(files_found)
    rows = _run(source_path, '''
        SELECT startDate, endDate, duration, noDevicesFound,
        CASE isManual WHEN 0 THEN 'No' WHEN 1 THEN 'Yes' END, scanMode
        FROM scan
    ''')
    data_list = [(_iso_to_utc(r[0]), _iso_to_utc(r[1]), r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Start Scan Timestamp', 'datetime'), ('End Scan Timestamp', 'datetime'),
                    'Duration (Seconds)', 'Devices Found', 'Manual Scan?', 'Scan Mode')
    return data_headers, data_list, source_path
