# pylint: disable=E1121,W0718
__artifacts_v2__ = {
    "speedtest_tests": {
        "name": "Speedtest Test Results",
        "description": "Rows of the UnivSpeedTestResult table of AmplifyDatastore.db: date, "
                       "connection type, SSID, latitude, longitude, external and internal IP "
                       "address, and download and upload speed in Kbps as stored.",
        "author": "its5Q",
        "creation_date": "2025-07-28",
        "last_update_date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "Only the first matched path is opened, and the path pattern also matches the "
                 "-wal and -shm sidecar files. Timestamp is the date column read as a Unix time "
                 "and shown as UTC; the conversion picks the unit from the size of the value, and "
                 "the unit the app stores is not sourced here. The other columns are reported as "
                 "stored. No registered test image is listed for this artifact.",
        "paths": ('*/org.zwanoo.android.speedtest/databases/AmplifyDatastore.db*',),
        "output_types": "all",
        "artifact_icon": "loader"
    },

    "speedtest_reports_location": {
        "name": "Speedtest Reports - Location",
        "description": "Latitude, longitude, altitude and accuracy from the start.location object "
                       "of each JSON record in the REPORT table of the speedtest database, with "
                       "the record's start.timestamp.",
        "author": "its5Q",
        "creation_date": "2025-07-28",
        "last_update_date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "A record with no start.location gives no row. For a record with no "
                 "start.timestamp the code substitutes the text 1970-01-01T00:00:00Z, so on Python "
                 "3.11 and later the row shows 1970-01-01 00:00:00 UTC; Python 3.10 cannot parse "
                 "that text and the record gives no row. The accuracy column is headed in meters; "
                 "that unit is not sourced here. What event writes a record is not established "
                 "here. No registered test image is listed for this artifact.",
        "paths": ('*/org.zwanoo.android.speedtest/databases/speedtest',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    },

    "speedtest_reports_wifi": {
        "name": "Speedtest Reports - Wi-Fi data",
        "description": "BSSID, SSID and signal level of each entry in "
                       "start.extended.wifi.scanResults of the JSON records in the REPORT table of "
                       "the speedtest database, with a computed time.",
        "author": "its5Q",
        "creation_date": "2025-07-28",
        "last_update_date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "Timestamp is computed, not stored: the record's start.time.timestamp minus its "
                 "elapsedRealtimeNanos, plus the scan entry's timestamp read as microseconds since "
                 "boot. It is blank when the record holds no start.time.timestamp or no "
                 "elapsedRealtimeNanos. AOSP documents ScanResult.timestamp as microseconds since "
                 "boot when the result was last seen; that the stored entry carries that field is "
                 "taken from its field names and was not measured here. No registered test image "
                 "is listed for this artifact. Reference: AOSP, ScanResult.java at tag "
                 "android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/tags/android-14.0.0_r1/framework/java/android/net/wifi/ScanResult.java#621",
        "paths": ('*/org.zwanoo.android.speedtest/databases/speedtest',),
        "output_types": "all",
        "artifact_icon": "wifi"
    },
}

from datetime import datetime, timezone, timedelta
from scripts.ilapfuncs import open_sqlite_db_readonly, logfunc, artifact_processor, convert_unix_ts_to_utc
import json

@artifact_processor
def speedtest_tests(context):
    files_found = context.get_files_found()
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'Connection type', 'SSID', 'Latitude', 'Longitude', 'External IP', 'Internal IP', 'Download speed (Kbps)', 'Upload speed (Kbps)']

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT date, connectionType, ssid, userLatitude, userLongitude, externalIp, internalIp, downloadKbps, uploadKbps FROM UnivSpeedTestResult')
        result = cur.fetchall()
    except Exception as ex:
        logfunc(f'Error retrieving Speedtest test results: {ex}')

    timestamped_result = []
    for row in result:
        row = list(row)
        try:
            row[0] = convert_unix_ts_to_utc(row[0])
        except Exception as ex:
            logfunc(f'Error converting timestamp for Speedtest test result: {ex}')
        timestamped_result.append(row)

    return headers, timestamped_result, file_path

@artifact_processor
def speedtest_reports_location(context):
    files_found = context.get_files_found()
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude', 'Accuracy (meters)']

    reports = []

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT DATA FROM REPORT')
        result = cur.fetchall()
    except Exception as ex:
        logfunc(f'Error retrieving Speedtest reports: {ex}')

    if result:
        for row in result:
            try:
                j = json.loads(row[0])
                location_data = j.get('start', {}).get('location', {})
                report_timestamp = datetime.fromisoformat(j.get('start', {}).get('timestamp', '1970-01-01T00:00:00Z')).astimezone(timezone.utc)
                if location_data:
                    latitude = location_data.get('latitude', None)
                    longitude = location_data.get('longitude', None)
                    altitude = location_data.get('altitude', None)
                    accuracy = location_data.get('accuracy', None)

                    reports.append((report_timestamp, latitude, longitude, altitude, accuracy))
            except Exception as ex:
                logfunc(f'Error retrieving Speedtest reports: {ex}')

    return headers, reports, file_path

@artifact_processor
def speedtest_reports_wifi(context):
    files_found = context.get_files_found()
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'BSSID', 'SSID', 'Signal Strength']
    results = []

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT DATA FROM REPORT')
        result = cur.fetchall()
    except Exception as ex:
        logfunc(f'Error retrieving Speedtest reports: {ex}')

    if result:
        for row in result:
            try:
                j = json.loads(row[0])
                wifi_scan_data = j.get('start', {}).get('extended', {}).get('wifi', {}).get('scanResults', [])
                
                elapsedRealtimeNanos = j.get('start', {}).get('time', {}).get('elapsedRealtimeNanos', 0)
                timestamp = j.get('start', {}).get('time', {}).get('timestamp', 0)
                boot_time = datetime.fromisoformat(timestamp).astimezone(timezone.utc) - timedelta(microseconds=elapsedRealtimeNanos/1000) if timestamp and elapsedRealtimeNanos else None

                for scan_result in wifi_scan_data:
                    try:
                        timestamp = boot_time + timedelta(microseconds=scan_result.get('timestamp', 0)) if boot_time else None
                        bssid = scan_result.get('BSSID')
                        ssid = scan_result.get('SSID')
                        level = scan_result.get('level')
                    except Exception as ex:
                        logfunc(f'Error retrieving Speedtest Wi-Fi scan data: {ex}')

                    results.append((timestamp, bssid, ssid, level))

            except Exception as ex:
                logfunc(f'Error retrieving Speedtest reports: {ex}')

    return headers, results, file_path
