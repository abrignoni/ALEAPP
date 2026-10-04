__artifacts_v2__ = {
    "get_airGuard": {
        "name": "AirGuard AirTag Tracker",
        "description": "Parses the beacon rows of the AirGuard attd_db database with the matching device record",
        "author": "@AlexisBrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-01-08",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "AirTags",
        "notes": "One row per beacon row. Timestamp is the matching device record's lastSeen, so "
                 "it repeats on every beacon of one device and is not the time of that beacon; "
                 "Received Time is the beacon's receivedAt, Device First Discovery is the device "
                 "record's firstDiscovery and Last Notification Sent is its lastNotificationSent. "
                 "The app's source stores these times as java.time.LocalDateTime text with no time "
                 "zone (seemoo-lab/AirGuard, "
                 "https://github.com/seemoo-lab/AirGuard/blob/"
                 "d515c534be7aac370de33e7bae0136a7b995e0cf/app/src/main/java/de/seemoo/"
                 "at_tracking_detection/util/converter/DateTimeConverter.kt#L12-L15). The source "
                 "was read at that commit, not at the version on the tested image. The four time "
                 "columns are reported as the text the database stores, with no conversion and no "
                 "time zone asserted. Their offset from UTC is not recorded in the database and was "
                 "not measured, and the rows are not written to the timeline for that reason. On "
                 "russell_pixel6a_a13 (1,960 rows) no stored lastSeen, receivedAt or firstDiscovery "
                 "value carried a zone or offset, and Last Notification Sent was empty on 1,910 "
                 "rows and zone-less on the other 50. What the app does when it sets "
                 "lastNotificationSent was not examined.",
        "paths": ('*/de.seemoo.at_tracking_detection.release/databases/attd_db*',),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "shield",
        "sample_data": {
            "russell_pixel6a_a13": "Android 13 | de.seemoo.at_tracking_detection.release vc 37 | 1960 rows",
        },
    },
    "get_airGuard_scans": {
        "name": "AirGuard AirTag Scans",
        "description": "Parses the rows of the scan table in the AirGuard attd_db database",
        "author": "@AlexisBrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-01-08",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "AirTags",
        "notes": "The app's source (seemoo-lab/AirGuard at commit d515c53, Scan.kt and "
                 "DateTimeConverter.kt) stores startDate and endDate as LocalDateTime strings with "
                 "no time zone. Both are reported as the text the database stores, with no "
                 "conversion and no time zone asserted; their offset from UTC is not recorded in "
                 "the database and was not measured, and the rows are not written to the timeline "
                 "for that reason. On russell_pixel6a_a13 none of the 805 startDate and 695 "
                 "endDate values carried a zone or offset. Duration is reported as stored. A "
                 "comment in Scan.kt at "
                 "that commit calls the column the duration in seconds of the scan; the source was "
                 "read at that commit, not at the version on the tested image. On "
                 "russell_pixel6a_a13 (805 rows) the end time and duration were empty on 110 rows. "
                 "Of the other 695, duration held 15 on 693 and 8 on 2, and the end time minus the "
                 "start time was within 1 second of it on 84 rows, so the stored times do not "
                 "confirm the unit.",
        "paths": ('*/de.seemoo.at_tracking_detection.release/databases/attd_db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search",
        "sample_data": {
            "russell_pixel6a_a13": "Android 13 | de.seemoo.at_tracking_detection.release vc 37 | 805 rows",
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db, logfunc


def _as_stored(value):
    # The app writes java.time.LocalDateTime text, which records no time zone, so the
    # stored text is reported unchanged and no instant is asserted.
    if value is None:
        return ''
    return str(value)


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
    if db is None:
        logfunc(f'airGuard: {source_path} could not be opened read-only; artifact skipped')
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'airGuard: query error on {source_path}: {ex}')
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
        if source_path:
            logfunc('airGuard: no location table in attd_db; reading latitude/longitude from the beacon table')
    rows = _run(source_path, f'''
        SELECT device.lastSeen, beacon.receivedAt, beacon.deviceAddress, {coords}, beacon.rssi,
        device.deviceType, device.firstDiscovery, device.lastNotificationSent
        FROM beacon
        LEFT JOIN device ON device.address = beacon.deviceAddress
        {coord_join}
    ''')
    data_list = [(_as_stored(r[0]), _as_stored(r[1]), r[2], r[3], r[4], r[5], r[6],
                  _as_stored(r[7]), _as_stored(r[8])) for r in rows]
    data_headers = ('Timestamp', 'Received Time', 'Device MAC Address',
                    'Latitude', 'Longitude', 'Signal Strength (RSSI)', 'Device Type',
                    'Device First Discovery', 'Last Notification Sent')
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
    data_list = [(_as_stored(r[0]), _as_stored(r[1]), r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = ('Start Scan Timestamp', 'End Scan Timestamp',
                    'Duration (Seconds)', 'Devices Found', 'Manual Scan?', 'Scan Mode')
    return data_headers, data_list, source_path
