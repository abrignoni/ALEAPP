"""Samsung Continuity Service context engine (context_engine_database).

Reports columns stored in plain form. The database file opened as plain SQLite on the three
samples. In mcfds 1.3.08.9 and 4.6.12.16 the app encrypts the coordinate fields with its own key
and writes -9999 to the plain latitude and longitude columns. Earlier versions were not examined.
Three artifacts report the plain pair only when latitude is between -90 and 90, longitude is
between -180 and 180, and the pair is not 0, 0.

Left out on purpose:
- BehaviorSleepEntity: on anne_a15 its 5 start and end pairs equal the sleep_time rows
  reported by Samsung Sleep Detection Sleep Times.
- FrequentlyVisitedPlaceEntity and VisitedAreaEntity: one row per place or area (3 and 2 on
  anne_a15). The coordinates are encrypted. The other columns held one value per table on
  anne_a15, except timestamp and radius and the row ids and encrypted fields.
- PedometerDataEntity: one row on anne_a15, with no period for its distance.
- function_log_database: a separate log database of the service. Not parsed.

Not parsed, and empty on anne_a15 (16 tables): ActivityDriveDataEntity and the other drive,
exercise, sleep, park, Bluetooth, contact, channel, connected Wi-Fi, exemplar, owner, travel and
Wi-Fi data tables. No sample has shown their rows.
"""

__artifacts_v2__ = {
    "samsungContextActivity": {
        "name": "Samsung Context Engine Detected Activity",
        "description": "Activity types recorded by the Samsung Continuity Service context "
                       "engine (context_engine_database, ActivityMoveDataEntity). Type is "
                       "the stored label, such as STATIONARY, WALKING or VEHICLE. It does "
                       "not show who carried the phone.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "The store also holds a detectingDevice code and a deviceUuid. Both held "
                 "one value on all 66 rows of anne_a15 and are not reported. Which device "
                 "made the classification is not established. The store's confidence column "
                 "is not reported because its meaning is not established. User is the user "
                 "number in the database path, and a path with no user folder, such as "
                 "/data/data, is reported as 0. On anne_a15 the database was under "
                 "/data/data, so User is 0 on all 66 rows.",
        "paths": ('*/com.samsung.android.mcfds/databases/context_engine_database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds 1.3.08.9 | 66 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.mcfds | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.mcfds 4.6.12.16 | 0 rows",
        },
    },
    "samsungContextMoveSessions": {
        "name": "Samsung Context Engine Move Sessions",
        "description": "Movement periods the Samsung Continuity Service context engine "
                       "built from its detected activity (context_engine_database, "
                       "BehaviorMoveEntity), with start, end and activity.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "Activity decodes the stored state with the order of the activity list in "
                 "mcfds 1.3.08.9 (0 UNKNOWN, 1 STATIONARY, 2 WALKING, 3 RUNNING, 4 VEHICLE, "
                 "5 CYCLE, 6 AIRPLANE). Only 2 and 4 occur on anne_a15, and the mapping was "
                 "not exercised on another version. A code outside the list is shown as "
                 "stored. A session can contain detections of another type between its "
                 "start and end (6 of 7 sessions on anne_a15), so compare it with Samsung "
                 "Context Engine Detected Activity. User is the user number in the database "
                 "path, and a path with no user folder, such as /data/data, is reported as "
                 "0. On anne_a15 the database was under /data/data, so User is 0 on all 7 "
                 "rows.",
        "paths": ('*/com.samsung.android.mcfds/databases/context_engine_database*',),
        "output_types": "standard",
        "artifact_icon": "navigation",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds 1.3.08.9 | 7 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.mcfds | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.mcfds 4.6.12.16 | 0 rows",
        },
    },
    "samsungContextVisits": {
        "name": "Samsung Context Engine Visits",
        "description": "Entry and exit times of places and areas recorded by the Samsung "
                       "Continuity Service context engine (context_engine_database, "
                       "VisitedPlaceEntity and VisitedAreaRecordEntity), with the plain "
                       "latitude and longitude when both are in range.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "Entered and Exited follow the column names ingressTime and egressTime. "
                 "Visit ID is fvpId for a place and varId for an area, as stored. Latitude "
                 "and Longitude are the plain columns. Both are filled only when latitude "
                 "is between -90 and 90, longitude is between -180 and 180, and the pair is "
                 "not 0, 0. Otherwise both are blank. The app reads a plain value between "
                 "-360 and 360 as the coordinate (mcfds 1.3.08.9 and 4.6.12.16), so a value "
                 "between those ranges is left blank here. Latitude and Longitude have no "
                 "value on any of the 5 rows of anne_a15, where the plain columns held a "
                 "placeholder outside the valid range and the alpha and bravo columns were "
                 "filled. In mcfds 1.3.08.9 those hold the encrypted pair, which is not "
                 "decoded. None of the three samples listed held a filled value, and no "
                 "writer of an in-range plain value was found in mcfds 1.3.08.9 or "
                 "4.6.12.16. In mcfds 1.3.08.9 the pair is copied from the place or area "
                 "record and is not a fix taken at entry. The poi and address columns held "
                 "one 3-character value on every row of anne_a15 and are not reported. User "
                 "is the user number in the database path, and a path with no user folder, "
                 "such as /data/data, is reported as 0. On anne_a15 the database was under "
                 "/data/data, so User is 0 on all 5 rows.",
        "paths": ('*/com.samsung.android.mcfds/databases/context_engine_database*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds 1.3.08.9 | 5 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.mcfds | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.mcfds 4.6.12.16 | 0 rows",
        },
    },
    "samsungContextWifiScans": {
        "name": "Samsung Context Engine Wi-Fi Scan Sets",
        "description": "Access points in the merged Wi-Fi scan sets saved by the Samsung "
                       "Continuity Service context engine (context_engine_database, "
                       "ScanEntity). In mcfds 1.3.08.9 each set is built from several scans "
                       "and keeps only access points the engine already tracks. A row shows "
                       "the access point was in at least one of the scans merged into that "
                       "set. An access point missing from a set is not shown to be out of "
                       "range, and a row does not show the phone connected to it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "Set Time is the time of the saved set. Level is the stored value. In "
                 "mcfds 1.3.08.9 it is calculated from the scans merged into the set, so it "
                 "is not one measured reading. Latitude and Longitude are the plain "
                 "columns. Both are filled only when latitude is between -90 and 90, "
                 "longitude is between -180 and 180, and the pair is not 0, 0. Otherwise "
                 "both are blank. The app reads a plain value between -360 and 360 as the "
                 "coordinate (mcfds 1.3.08.9 and 4.6.12.16), so a value between those "
                 "ranges is left blank here. Latitude and Longitude have no value on any of "
                 "the 487 rows of anne_a15, where the plain columns held a placeholder "
                 "outside the valid range and the alpha and bravo columns were filled. In "
                 "mcfds 1.3.08.9 those hold the encrypted pair, which is not decoded. None "
                 "of the three samples listed held a filled value, and no writer of an "
                 "in-range plain value was found in mcfds 1.3.08.9 or 4.6.12.16. In mcfds "
                 "1.3.08.9 the pair is the position held when the set was saved, the same "
                 "for every access point in the set. It is not a position of the access "
                 "point. User is the user number in the database path, and a path with no "
                 "user folder, such as /data/data, is reported as 0. On anne_a15 the "
                 "database was under /data/data, so User is 0 on all 487 rows.",
        "paths": ('*/com.samsung.android.mcfds/databases/context_engine_database*',),
        "output_types": "all",
        "artifact_icon": "wifi",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds 1.3.08.9 | 487 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.mcfds | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.mcfds 4.6.12.16 | 0 rows",
        },
    },
    "samsungContextTelephony": {
        "name": "Samsung Context Engine Telephony Events",
        "description": "Network operator, SIM operator, network country code and roaming "
                       "flag recorded by the Samsung Continuity Service context engine when "
                       "a trigger fired (context_engine_database, TelephonyDataEntity), "
                       "such as a country code or SIM state change.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "Trigger, operators, country code and Roaming are as stored. On anne_a15 "
                 "Network Operator, SIM Operator, Country Code and Roaming each held one "
                 "value on all 33 rows. User is the user number in the database path, and a "
                 "path with no user folder, such as /data/data, is reported as 0. On "
                 "anne_a15 the database was under /data/data, so User is 0 on all 33 rows.",
        "paths": ('*/com.samsung.android.mcfds/databases/context_engine_database*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds 1.3.08.9 | 33 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.mcfds | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.mcfds 4.6.12.16 | 0 rows",
        },
    },
    "samsungContextLocationFixes": {
        "name": "Samsung Context Engine Location Fix Times",
        "description": "Times of the location fixes the Samsung Continuity Service context "
                       "engine stored, with provider, accuracy value, and the plain "
                       "latitude and longitude when both are in range "
                       "(context_engine_database, GpsDataEntity).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "Latitude and Longitude are the plain columns. Both are filled only when "
                 "latitude is between -90 and 90, longitude is between -180 and 180, and "
                 "the pair is not 0, 0. Otherwise both are blank. The app reads a plain "
                 "value between -360 and 360 as the coordinate (mcfds 1.3.08.9 and "
                 "4.6.12.16), so a value between those ranges is left blank here. Latitude "
                 "and Longitude have no value on any of the 710 rows of anne_a15, where the "
                 "plain columns held a placeholder outside the valid range and the alpha "
                 "and bravo columns were filled. In mcfds 1.3.08.9 those hold the encrypted "
                 "pair, which is not decoded. None of the three samples listed held a "
                 "filled value, and no writer of an in-range plain value was found in mcfds "
                 "1.3.08.9 or 4.6.12.16. Accuracy is the stored value. User is the user "
                 "number in the database path, and a path with no user folder, such as "
                 "/data/data, is reported as 0. On anne_a15 the database was under "
                 "/data/data, so User is 0 on all 710 rows.",
        "paths": ('*/com.samsung.android.mcfds/databases/context_engine_database*',),
        "output_types": "all",
        "artifact_icon": "crosshair",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds 1.3.08.9 | 710 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.mcfds | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.mcfds 4.6.12.16 | 0 rows",
        },
    },
}

import os
import re

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc

DB_NAME = 'context_engine_database'
PACKAGE = 'com.samsung.android.mcfds'
MOVE_STATES = {
    0: 'UNKNOWN',
    1: 'STATIONARY',
    2: 'WALKING',
    3: 'RUNNING',
    4: 'VEHICLE',
    5: 'CYCLE',
    6: 'AIRPLANE',
}


def _android_user(relative):
    '''The Android user folder in an evidence-relative path. /data/data is user 0.'''
    match = re.search(rf'(?:^|/)user(?:_de)?/(\d+)/{re.escape(PACKAGE)}/', relative)
    return int(match.group(1)) if match else 0


def _databases(context):
    '''(path, user) for each database, without sidecars or duplicate storage views.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != DB_NAME:
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if f'/{PACKAGE}/' not in f'/{relative}' or 'data_mirror' in relative:
            continue
        user = _android_user(relative)
        if user in seen:
            continue
        seen.add(user)
        result.append((file_found, user))
    return result


def _coordinates(latitude, longitude):
    '''The plain pair when both values are in range and not 0, 0, otherwise blanks.'''
    if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)) \
            and -90 <= latitude <= 90 and -180 <= longitude <= 180 \
            and (latitude, longitude) != (0, 0):
        return latitude, longitude
    return '', ''


def _rows(context, query):
    '''Yield (user, row) and collect the databases that returned rows.'''
    sources = []
    rows = []
    for file_found, user in _databases(context):
        records = list(get_sqlite_db_records(file_found, query))
        if records:
            sources.append(file_found)
        rows.extend((user, record) for record in records)
    return rows, '\n'.join(sources)


@artifact_processor
def samsungContextActivity(context):
    rows, source_path = _rows(context, '''
        SELECT timestamp, type FROM ActivityMoveDataEntity ORDER BY timestamp DESC
    ''')
    data_list = [(convert_unix_ts_to_utc(r[0]), r[1], user) for user, r in rows]
    data_headers = (('Time', 'datetime'), 'Type', 'User')
    return data_headers, data_list, source_path


@artifact_processor
def samsungContextMoveSessions(context):
    rows, source_path = _rows(context, '''
        SELECT startTime, endTime, state FROM BehaviorMoveEntity ORDER BY startTime DESC
    ''')
    data_list = [(convert_unix_ts_to_utc(r[0]), convert_unix_ts_to_utc(r[1]),
                  MOVE_STATES.get(r[2], r[2]), user) for user, r in rows]
    data_headers = (('Start', 'datetime'), ('End', 'datetime'), 'Activity', 'User')
    return data_headers, data_list, source_path


@artifact_processor
def samsungContextVisits(context):
    rows, source_path = _rows(context, '''
        SELECT ingressTime, egressTime, 'Place', fvpId, latitude, longitude
        FROM VisitedPlaceEntity
        UNION ALL
        SELECT ingressTime, egressTime, 'Area', varId, latitude, longitude
        FROM VisitedAreaRecordEntity
        ORDER BY 1 DESC
    ''')
    data_list = [(convert_unix_ts_to_utc(r[0]), convert_unix_ts_to_utc(r[1]),
                  *_coordinates(r[4], r[5]), r[2], r[3], user) for user, r in rows]
    data_headers = (('Entered', 'datetime'), ('Exited', 'datetime'),
                    ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Visit Type',
                    'Visit ID', 'User')
    return data_headers, data_list, source_path


@artifact_processor
def samsungContextWifiScans(context):
    rows, source_path = _rows(context, '''
        SELECT timestamp, bssid, level, latitude, longitude
        FROM ScanEntity ORDER BY timestamp DESC, level DESC
    ''')
    data_list = [(convert_unix_ts_to_utc(r[0]), *_coordinates(r[3], r[4]), r[1], r[2], user)
                 for user, r in rows]
    data_headers = (('Set Time', 'datetime'), ('Latitude', 'latitude'),
                    ('Longitude', 'longitude'), 'BSSID', 'Level', 'User')
    return data_headers, data_list, source_path


@artifact_processor
def samsungContextTelephony(context):
    rows, source_path = _rows(context, '''
        SELECT timestamp, triggerType, networkOperator, simOperator, countryCode, isRoaming
        FROM TelephonyDataEntity ORDER BY timestamp DESC
    ''')
    data_list = [(convert_unix_ts_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], user)
                 for user, r in rows]
    data_headers = (('Time', 'datetime'), 'Trigger', 'Network Operator', 'SIM Operator',
                    'Country Code', 'Roaming', 'User')
    return data_headers, data_list, source_path


@artifact_processor
def samsungContextLocationFixes(context):
    rows, source_path = _rows(context, '''
        SELECT timestamp, provider, accuracy, latitude, longitude
        FROM GpsDataEntity ORDER BY timestamp DESC
    ''')
    data_list = [(convert_unix_ts_to_utc(r[0]), *_coordinates(r[3], r[4]), r[1], r[2], user)
                 for user, r in rows]
    data_headers = (('Time', 'datetime'), ('Latitude', 'latitude'), ('Longitude', 'longitude'),
                    'Provider', 'Accuracy', 'User')
    return data_headers, data_list, source_path
