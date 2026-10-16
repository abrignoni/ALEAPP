# pylint: disable=E1121,W0718
__artifacts_v2__ = {
    "speedtest_tests": {
        "name": "Speedtest Test Results",
        "description": "Rows selected from UnivSpeedTestResult in each matched AmplifyDatastore.db main: timestamp, connection type, SSID, coordinates, IP values and the stored downloadKbps and uploadKbps values.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2025-07-28",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "Original parser contribution credited to its5Q. Exact AmplifyDatastore.db main filenames are processed in matched input encounter order; standalone WAL/SHM/journal paths are excluded and each main is opened with its own available sidecars. Repeated input occurrences, including repeated aliases, are retained without byte-hash or canonical-path deduplication. Equal stored result rows are retained. Timestamp is the date column read as a Unix time and shown as UTC; the conversion picks the unit from the size of the value, and the unit the app stores is not sourced here. The other eight values and the existing Kbps headers are unchanged; their units and meanings are not independently established by this selection correction. A Source File column is appended only when more than one distinct matched main path contributes rows, using the existing extraction-relative path helper. The artifact source indicator lists distinct contributing paths in encounter order; when no rows are found it lists successfully queried empty mains instead. Unreadable mains or failed queries are logged and skipped; this does not establish a complete result history. A matched path is a source indicator, not an account, user or device ownership assertion. No registered positive test image was previously listed for this artifact; the historical 44-image absence statements belong to the unchanged REPORT siblings and are not revalidated here.",
        "paths": ('*/org.zwanoo.android.speedtest/databases/AmplifyDatastore.db*',),
        "output_types": "all",
        "artifact_icon": "loader"
    },

    "speedtest_reports_location": {
        "name": "Speedtest Reports - Location",
        "description": "Latitude, longitude, altitude and accuracy from the start.location object "
                       "of each JSON record in the REPORT table of the speedtest database, with "
                       "the record's start.timestamp.",
        "author": "its5Q, @AlexisBrignoni, Codex",
        "creation_date": "2025-07-28",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "A record with no start.location gives no row. Start Timestamp (as stored) is "
                 "the record's start.timestamp text, unchanged. Timestamp is that text converted "
                 "to UTC, and only when the text is an ISO 8601 time that carries its own offset "
                 "or a Z suffix; it is blank when the record holds no start.timestamp, when the "
                 "text names no offset, or when the text cannot be read. Accuracy is the stored "
                 "accuracy value; its unit is not sourced here. What event writes a record is not "
                 "established here. None of the 44 registered Android test images holds this "
                 "app, so the columns were checked on constructed records only.",
        "paths": ('*/org.zwanoo.android.speedtest/databases/speedtest',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    },

    "speedtest_reports_wifi": {
        "name": "Speedtest Reports - Wi-Fi data",
        "description": "BSSID, SSID and signal level of each entry in "
                       "start.extended.wifi.scanResults of the JSON records in the REPORT table of "
                       "the speedtest database, with the stored time fields and a computed time.",
        "author": "its5Q, @AlexisBrignoni, Codex",
        "creation_date": "2025-07-28",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Speedtest",
        "notes": "Computed Time is computed, not stored: the record's start.time.timestamp "
                 "minus its elapsedRealtimeNanos, plus the scan entry's timestamp read as "
                 "microseconds since boot. It is blank when the record holds no "
                 "start.time.timestamp or no elapsedRealtimeNanos, when start.time.timestamp "
                 "names no offset, or when a value cannot be read. Record Time (as stored), "
                 "Elapsed Realtime Nanos (as stored) and Scan Timestamp (as stored) are the three "
                 "stored values the computation uses, unchanged. AOSP documents "
                 "ScanResult.timestamp as microseconds since boot when the result was last seen; "
                 "that the stored entry carries that field is taken from its field names and was "
                 "not measured here. None of the 44 registered Android test images holds this "
                 "app, so the columns were checked on constructed records only. Reference: AOSP, "
                 "ScanResult.java at tag "
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
import re
import os
import sqlite3


def _iso_to_utc(text):
    """An ISO 8601 text that carries its own offset (or Z), as an aware UTC datetime.

    Returns '' for a missing value, for a text that names no offset (reading it as UTC or
    as this machine's zone would assert an instant the record does not state), and for a
    text that cannot be read. A trailing Z and a fraction that is not 3 or 6 digits are
    normalised first, because datetime.fromisoformat accepts neither before Python 3.11.
    """
    if not isinstance(text, str) or not text.strip():
        return ''
    value = text.strip()
    if value[-1] in 'Zz':
        value = value[:-1] + '+00:00'
    value = re.sub(r'\.(\d+)', lambda m: '.' + m.group(1)[:6].ljust(6, '0'), value, count=1)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return ''
    if parsed.tzinfo is None:
        return ''
    return parsed.astimezone(timezone.utc)


def _speedtest_error(context, file_path, error):
    source = ascii(context.get_relative_path(file_path))[:256]
    detail = ascii(str(error))[:256]
    logfunc(f'Error retrieving Speedtest test results from {source}: {type(error).__name__}: {detail}')


@artifact_processor
def speedtest_tests(context):
    files_found = context.get_files_found()
    headers = [('Timestamp', 'datetime'), 'Connection type', 'SSID', 'Latitude', 'Longitude', 'External IP', 'Internal IP', 'Download speed (Kbps)', 'Upload speed (Kbps)']
    timestamped_result = []
    row_sources = []
    contributors = []
    queried_sources = []
    for file_found in files_found:
        file_path = str(file_found)
        if os.path.basename(file_path) != 'AmplifyDatastore.db':
            continue
        db = None
        result = []
        try:
            db = open_sqlite_db_readonly(file_path)
            if db is None:
                _speedtest_error(context, file_path, OSError('read-only database open returned no connection'))
                continue
            cur = db.cursor()
            cur.execute('SELECT date, connectionType, ssid, userLatitude, userLongitude, externalIp, internalIp, downloadKbps, uploadKbps FROM UnivSpeedTestResult')
            result = cur.fetchall()
            if file_path not in queried_sources:
                queried_sources.append(file_path)
        except (sqlite3.Error, OSError) as ex:
            _speedtest_error(context, file_path, ex)
            continue
        finally:
            if db is not None:
                try:
                    db.close()
                except sqlite3.Error as ex:
                    _speedtest_error(context, file_path, ex)
        if result and file_path not in contributors:
            contributors.append(file_path)
        for row in result:
            row = list(row)
            try:
                row[0] = convert_unix_ts_to_utc(row[0])
            except Exception as ex:
                logfunc(f'Error converting timestamp for Speedtest test result: {ex}')
            timestamped_result.append(row)
            row_sources.append(file_path)
    if len(contributors) > 1:
        headers = headers + ['Source File']
        timestamped_result = [row + [context.get_relative_path(path)] for row, path in zip(timestamped_result, row_sources)]
    source_path = '\n'.join(contributors or queried_sources)
    return headers, timestamped_result, source_path

@artifact_processor
def speedtest_reports_location(context):
    files_found = context.get_files_found()
    file_path = files_found[0]
    headers = [('Timestamp', 'datetime'), 'Start Timestamp (as stored)', 'Latitude', 'Longitude', 'Altitude', 'Accuracy']

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
                stored_timestamp = j.get('start', {}).get('timestamp')
                report_timestamp = _iso_to_utc(stored_timestamp)
                if location_data:
                    latitude = location_data.get('latitude', None)
                    longitude = location_data.get('longitude', None)
                    altitude = location_data.get('altitude', None)
                    accuracy = location_data.get('accuracy', None)

                    reports.append((report_timestamp, stored_timestamp, latitude, longitude, altitude, accuracy))
            except Exception as ex:
                logfunc(f'Error retrieving Speedtest reports: {ex}')

    return headers, reports, file_path

@artifact_processor
def speedtest_reports_wifi(context):
    files_found = context.get_files_found()
    file_path = files_found[0]
    headers = [('Computed Time', 'datetime'), 'Record Time (as stored)', 'Elapsed Realtime Nanos (as stored)', 'Scan Timestamp (as stored)', 'BSSID', 'SSID', 'Signal Strength']
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
                
                elapsedRealtimeNanos = j.get('start', {}).get('time', {}).get('elapsedRealtimeNanos')
                record_time = j.get('start', {}).get('time', {}).get('timestamp')
                record_time_utc = _iso_to_utc(record_time)
                boot_time = None
                if record_time_utc and elapsedRealtimeNanos:
                    try:
                        boot_time = record_time_utc - timedelta(microseconds=elapsedRealtimeNanos/1000)
                    except (TypeError, OverflowError):
                        boot_time = None

                for scan_result in wifi_scan_data:
                    try:
                        scan_timestamp = scan_result.get('timestamp')
                        computed_time = ''
                        if boot_time and scan_timestamp is not None:
                            try:
                                computed_time = boot_time + timedelta(microseconds=scan_timestamp)
                            except (TypeError, OverflowError):
                                computed_time = ''
                        bssid = scan_result.get('BSSID')
                        ssid = scan_result.get('SSID')
                        level = scan_result.get('level')
                    except Exception as ex:
                        logfunc(f'Error retrieving Speedtest Wi-Fi scan data: {ex}')
                        continue

                    results.append((computed_time, record_time, elapsedRealtimeNanos, scan_timestamp, bssid, ssid, level))

            except Exception as ex:
                logfunc(f'Error retrieving Speedtest reports: {ex}')

    return headers, results, file_path
