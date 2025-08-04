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
        "function": "extract_speedtest_test_results"
    },

    "speedtest_reports": {
        "name": "Speedtest Reports",
        "description": "Extracts Speedtest logging reports which contain more information, like Wi-Fi scan data",
        "author": "its5Q",
        "version": "0.1",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "",
        "paths": ('*/org.zwanoo.android.speedtest/databases/speedtest',),
        "function": "extract_speedtest_reports"
    },
}

from datetime import datetime, timezone, timedelta
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import open_sqlite_db_readonly, does_column_exist_in_db, tsv, timeline, logfunc
import json

def extract_speedtest_test_results(files_found, report_folder, seeker, wrap_text):
    file_path = files_found[0]
    headers = ['Timestamp', 'Connection type', 'SSID', 'User Latitude', 'User Longitude', 'External IP', 'Internal IP', 'Download speed (Kbps)', 'Upload speed (Kbps)']

    db = open_sqlite_db_readonly(file_path)
    cur = db.cursor()

    try:
        cur.execute('SELECT datetime(date, \'unixepoch\'), connectionType, ssid, userLatitude, userLongitude, externalIp, internalIp, downloadKbps, uploadKbps FROM UnivSpeedTestResult')
        result = cur.fetchall()
    except Exception as ex:
        logfunc('Error retrieving Speedtest test results: ', ex)

    if result:
        report = ArtifactHtmlReport("Speedtest Test Results")
        report_name = "Speedtest Test Results"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        report.write_artifact_data_table(headers, result, file_path)
        report.end_artifact_report()

        tsv(report_folder, headers, result, report_name, file_path)

        timeline(report_folder, report_name, result, headers)


def extract_speedtest_reports(files_found, report_folder, seeker, wrap_text):
    file_path = files_found[0]
    headers = ['Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Accuracy (meters)']
    wifi_scan_headers = ['Timestamp', 'BSSID', 'SSID', 'Signal Strength']

    reports = []
    wifi_scan_results = []

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
                wifi_scan_data = j.get('start', {}).get('extended', {}).get('wifi', {}).get('scanResults', [])
                report_timestamp = datetime.fromisoformat(j.get('start', {}).get('timestamp', '1970-01-01T00:00:00Z'))
                if location_data:
                    latitude = location_data.get('latitude', None)
                    longitude = location_data.get('longitude', None)
                    altitude = location_data.get('altitude', None)
                    accuracy = location_data.get('accuracy', None)

                    reports.append((report_timestamp, latitude, longitude, altitude, accuracy))
                
                elapsedRealtimeNanos = j.get('start', {}).get('time', {}).get('elapsedRealtimeNanos', 0)
                timestamp = j.get('start', {}).get('time', {}).get('timestamp', 0)
                boot_time = datetime.fromisoformat(timestamp) - timedelta(microseconds=elapsedRealtimeNanos/1000) if timestamp and elapsedRealtimeNanos else None

                for scan_result in wifi_scan_data:
                    try:
                        timestamp = boot_time + timedelta(microseconds=scan_result.get('timestamp', 0)) if boot_time else None
                        bssid = scan_result.get('BSSID')
                        ssid = scan_result.get('SSID')
                        level = scan_result.get('level')
                    except Exception as ex:
                        logfunc('Error retrieving Speedtest Wi-Fi scan data: ', ex)

                    wifi_scan_results.append((timestamp, bssid, ssid, level))

            except Exception as ex:
                logfunc('Error retrieving Speedtest reports: ', ex)

    report = ArtifactHtmlReport("Speedtest Extended Reports")
    report_name = "Speedtest Extended Reports"
    report.start_artifact_report(report_folder, report_name)
    report.add_script()
    report.write_artifact_data_table(headers, reports, file_path)
    report.write_artifact_data_table(wifi_scan_headers, wifi_scan_results, file_path)
    report.end_artifact_report()

    tsv(report_folder, headers, reports, "Speedtest Extended Reports (Location Data)", file_path)
    tsv(report_folder, wifi_scan_headers, wifi_scan_results, "Speedtest Extended Reports (Wi-Fi Data)", file_path)

    timeline(report_folder, "Speedtest Extended Reports (Location Data)", reports, headers)
    timeline(report_folder, "Speedtest Extended Reports (Wi-Fi Data)", wifi_scan_results, wifi_scan_headers)