__artifacts_v2__ = {
    "samsungWifiConfigStoreDb": {
        "name": "Samsung WiFi Config Store DB",
        "description": "Saved Wi-Fi networks recorded in the Samsung WifiConfigStore.db "
                       "(configs table): SSID with security type and, where present, the "
                       "creation time.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "The CREATION_TIME column does not exist in every schema observed and is "
                 "reported empty there; where it exists, entries holding 0 are also "
                 "reported empty.",
        "paths": ('*/system/WifiConfigStore.db*',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "anne_a15": "Android 15 | 24 rows",
            "samsunga53_a14": "Android 14 | 4 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 29 rows",
        },
    },
    "samsungWifiGeofence": {
        "name": "Samsung WiFi Geofence",
        "description": "Wi-Fi networks with the geographic coordinates recorded for them in "
                       "the Samsung wifigeofence.db (geofence_wifi table). The latitude and "
                       "longitude come from the base columns when set and from the "
                       "*_major columns otherwise; the Coordinate Source column names which "
                       "pair supplied them.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Coordinates of 1000.0 (the declared column default) or -1.0 (observed for "
                 "unset entries in test data) are reported empty.",
        "paths": ('*/system/wifigeofence.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | 11 rows",
            "galaxys10_a10": "Android 10 | 4 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 14 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, does_column_exist_in_db

# unset coordinates observed in the data / declared as the column default
COORD_SENTINELS = (-1.0, 1000.0)


def _db_files(context, name_suffix):
    '''Database files matching the suffix, without -wal/-shm sidecars.'''
    return [str(x) for x in context.get_files_found() if str(x).endswith(name_suffix)]


def _ts(value):
    '''CREATION_TIME is a TEXT column; unset values are '', '0' or 0.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return convert_unix_ts_to_utc(value)


def _coord(value):
    if value is None or value in COORD_SENTINELS:
        return ''
    return value


@artifact_processor
def samsungWifiConfigStoreDb(context):
    data_list = []
    source_path = ''

    for file_found in _db_files(context, 'WifiConfigStore.db'):
        # older One UI versions do not have the CREATION_TIME column
        creation_column = 'CREATION_TIME' if does_column_exist_in_db(
            file_found, 'configs', 'CREATION_TIME') else "''"
        db_records = get_sqlite_db_records(file_found, f'''
            SELECT {creation_column}, CONFIG_KEY, NETWORK_SCORE, CAPTIVE_PORTAL, LOCK_DOWN,
                   NO_INTERNET_ACCESS_EXPECTED, NETWORK_DISABLE_REASON
            FROM configs
            ORDER BY _ID
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                _ts(row[0]),
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
            ))

    data_headers = (
        ('Creation Time', 'datetime'),
        'Config Key',
        'Network Score',
        'Captive Portal',
        'Lock Down',
        'No Internet Access Expected',
        'Network Disable Reason',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungWifiGeofence(context):
    data_list = []
    source_path = ''

    for file_found in _db_files(context, 'wifigeofence.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT time, time_major, config_key, bssid, latitude, longitude,
                   latitude_major, longitude_major, location_id, network_id
            FROM geofence_wifi
            ORDER BY _id
        ''')

        for row in db_records:
            source_path = file_found
            latitude, longitude = _coord(row[4]), _coord(row[5])
            coord_source = 'latitude/longitude'
            if latitude == '' or longitude == '':
                latitude, longitude = _coord(row[6]), _coord(row[7])
                coord_source = 'latitude_major/longitude_major' if latitude != '' else ''
            data_list.append((
                _ts(row[0]),
                _ts(row[1]),
                row[2],
                row[3],
                latitude,
                longitude,
                coord_source,
                _coord(row[6]),
                _coord(row[7]),
                row[8],
                row[9],
            ))

    data_headers = (
        ('Time', 'datetime'),
        ('Time Major', 'datetime'),
        'Config Key',
        'BSSID',
        'Latitude',
        'Longitude',
        'Coordinate Source',
        'Latitude Major',
        'Longitude Major',
        'Location ID',
        'Network ID',
    )
    return data_headers, data_list, source_path
