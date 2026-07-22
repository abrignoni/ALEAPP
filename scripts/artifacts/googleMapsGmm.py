# pylint: disable=W0718
__artifacts_v2__ = {
    "get_googleMapsGmm": {
        "name": "Google Search History Maps",
        "description": "Parse Google Maps GMM directions (gmm_storage.db)",
        "author": "@AlexisBrignoni",
        "creation_date": "2022-12-30",
        "last_update_date": "2022-12-30",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Updated 2023-12-12 by @segumarc",
        "paths": ('*/com.google.android.apps.maps/databases/gmm_storage.db',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 13 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.maps vc 1064201040 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.maps vc 1068624404 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.maps vc 1067620099 | 4 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.maps vc 1068326445 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.maps vc 1068347331 | 1 row",
            "sharon_a14": "Android 14 | com.google.android.apps.maps vc 1067648704 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.maps vc 1067057900 | 6 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.maps vc 1067804533 | 6 rows",
        },
    },
    "get_googleMapsGmm_places": {
        "name": "Google Maps Label Places",
        "description": "Parse Google Maps GMM labeled places (gmm_myplaces.db)",
        "author": "@AlexisBrignoni",
        "creation_date": "2022-12-30",
        "last_update_date": "2022-12-30",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Updated 2023-12-12 by @segumarc",
        "paths": ('*/com.google.android.apps.maps/databases/gmm_myplaces.db',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 1 row",
            "galaxys10_a10": "Android 10 | com.google.android.apps.maps vc 1064201040 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.maps vc 1068624404 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.maps vc 1067620099 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.maps vc 1068347331 | 1 row",
            "sharon_a14": "Android 14 | com.google.android.apps.maps vc 1067648704 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.maps vc 1067057900 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.maps vc 1067804533 | 0 rows",
        },
    }
}

import datetime
import sqlite3
import struct

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
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
def get_googleMapsGmm(context):
    files_found = context.get_files_found()
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('gmm_storage.db'):
            continue
        source_path = file_found
        for row in _run(file_found, 'SELECT rowid, _data, _key_pri FROM gmm_storage_table'):
            try:
                rowid, data, keypri = row[0], row[1], row[2]
                idx = data.find(b'/dir/')
                if idx == -1:
                    continue
                length = struct.unpack('<B', data[idx - 2:idx - 1])[0]
                directions = data[idx:idx + length]
                try:
                    directions = directions.decode()
                except Exception:
                    directions = str(directions)
                fromlat = directions.split('/dir/')[1].split(',')[0]
                fromlon = directions.split(',')[1].split('/')[0]
                tolat = ''
                tolon = ''
                dd = directions[directions.rfind('!1d'):]
                if len(dd.split('!1d')) > 1 and len(dd.split('!2d')) > 1:
                    tolon = dd.split('!1d')[1].split('!')[0]
                    tolat = dd.split('!2d')[1].split('!')[0]
                if directions.startswith("b'"):
                    directions = directions.replace("b'", '', 1)[:-1]
                directions = 'https://google.com/maps' + directions
                data_list.append((directions, fromlat, fromlon, tolat, tolon, rowid, keypri))
            except (struct.error, IndexError, TypeError, AttributeError):
                continue

    data_headers = ('Directions URL', 'Latitude', 'Longitude', 'To Latitude', 'To Longitude',
                    'Row ID', 'Type')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleMapsGmm_places(context):
    files_found = context.get_files_found()
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('gmm_myplaces.db'):
            continue
        source_path = file_found
        rows = _run(file_found, '''
            SELECT rowid, key_string, round(latitude*.000001, 6), round(longitude*.000001, 6),
            sync_item, timestamp
            FROM sync_item
        ''')
        for row in rows:
            try:
                pb = decode_protobuf(row[4], 'None')
                if row[1] == '0:0':
                    label = 'Home'
                elif row[1] == '1:0':
                    label = 'Work'
                else:
                    label = pb[0].get('6', {}).get('7', b'').decode('utf-8')
                address = pb[0].get('6', {}).get('2', b'').decode('utf-8')
                url = pb[0].get('6', {}).get('6', b'').decode('utf-8')
            except Exception:
                continue
            data_list.append((_ms_to_utc(row[5]), label, row[2], row[3], address, url))

    data_headers = (('Timestamp', 'datetime'), 'Label', 'Latitude', 'Longitude', 'Address', 'URL')
    return data_headers, data_list, source_path
