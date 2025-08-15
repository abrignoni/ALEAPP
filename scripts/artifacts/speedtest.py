__artifacts_v2__ = {
    "speedtest_tests": {
        "name": "Speedtest Test Results",
        "description": "Extracts Speedtest Test metadata and other interaction artifacts",
        "author": "its5Q",
        "version": "0.1",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "",
        "paths": ('*/org.zwanoo.android.speedtest/databases/AmplifyDatastore.db',),
        "artifact_icon": "loader"
    },

    "speedtest_reports_location": {
        "name": "Speedtest Reports - Location",
        "description": "Extracts location data from Speedtest usage reports",
        "author": "its5Q",
        "version": "0.1",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "",
        "paths": ('*/org.zwanoo.android.speedtest/databases/speedtest',),
        "artifact_icon": "map-pin"
    },

    "speedtest_reports_wifi": {
        "name": "Speedtest Reports - Wi-Fi data",
        "description": "Extracts Wi-Fi scan data from Speedtest usage reports",
        "author": "its5Q",
        "version": "0.1",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "",
        "paths": ('*/org.zwanoo.android.speedtest/databases/speedtest',),
        "artifact_icon": "wifi"
    },
}

from datetime import datetime, timezone, timedelta
from scripts.ilapfuncs import open_sqlite_db_readonly, logfunc, artifact_processor, convert_unix_ts_to_utc
import json

@artifact_processor
def speedtest_tests(files_found, report_folder, seeker, wrap_text):
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'Connection type', 'SSID', 'Latitude', 'Longitude', 'External IP', 'Internal IP', 'Download speed (Kbps)', 'Upload speed (Kbps)']

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT date, connectionType, ssid, userLatitude, userLongitude, externalIp, internalIp, downloadKbps, uploadKbps FROM UnivSpeedTestResult')
        result = cur.fetchall()
    except Exception as ex:
        logfunc('Error retrieving Speedtest test results: ', ex)

    timestamped_result = []
    for row in result:
        row = list(row)
        try:
            row[0] = convert_unix_ts_to_utc(row[0])
        except Exception:
            logfunc('Error converting timestamp for Speedtest test result: ', ex)
        timestamped_result.append(row)

    return headers, timestamped_result, file_path

@artifact_processor
def speedtest_reports_location(files_found, report_folder, seeker, wrap_text):
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude', 'Accuracy (meters)']

    reports = []

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT DATA FROM REPORT')
        result = cur.fetchall()
    except Exception as ex:
        logfunc('Error retrieving Speedtest reports: ', ex)

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
                logfunc('Error retrieving Speedtest reports: ', ex)

    return headers, reports, file_path

@artifact_processor
def speedtest_reports_wifi(files_found, report_folder, seeker, wrap_text):
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'BSSID', 'SSID', 'Signal Strength']
    results = []

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT DATA FROM REPORT')
        result = cur.fetchall()
    except Exception as ex:
        logfunc('Error retrieving Speedtest reports: ', ex)

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
                        logfunc('Error retrieving Speedtest Wi-Fi scan data: ', ex)

                    results.append((timestamp, bssid, ssid, level))

            except Exception as ex:
                logfunc('Error retrieving Speedtest reports: ', ex)

    return headers, results, file_path