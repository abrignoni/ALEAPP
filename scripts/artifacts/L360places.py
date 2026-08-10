# pylint: disable=W0613
__artifacts_v2__ = {
    'Life360_Places': {
        'name': 'Life360 Places',
        'description': 'Parses Life360 Places',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-11',
        'last_update_date': '2026-06-30',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360LocalStoreRoomDatabase*',),
        'output_types': ['html', 'tsv', 'lava', 'kml'],
        'artifact_icon': 'home',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 6 rows',
            'pixel7a_a14': 'Android 14 | com.life360.android.safetymapd vc 294540 | 0 rows',
        }
    },
    'Life360_PlaceAlerts': {
        'name': 'Life360 Place Alerts',
        'description': 'Parses Life360 Place Alerts',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-11',
        'last_update_date': '2026-06-30',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360LocalStoreRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'home',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 12 rows',
            'pixel7a_a14': 'Android 14 | com.life360.android.safetymapd vc 294540 | 0 rows',
        }
    },

}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _bool(value):
    if value is None:
        return ''
    return 'Yes' if int(value) == 1 else 'No'


def _find(context, suffix):
    for file_found in context.get_files_found():
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


@artifact_processor
def Life360_Places(context):
    source = _find(context, 'L360LocalStoreRoomDatabase')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                place_id,
                circle_id,
                name,
                latitude,
                longitude,
                radius,
                source,
                source_id,
                owner_id,
                has_alerts,
                website,
                types,
                category
            FROM places
            ORDER BY name
        '''):
            data_list.append((
                row[0], row[1], row[2],
                row[3], row[4], row[5],
                row[6], row[7], row[8],
                _bool(row[9]),
                row[10], row[11], row[12]
            ))
        db.close()

    data_headers = (
        'Place ID', 'Circle ID', 'Name',
        'Latitude', 'Longitude', 'Radius',
        'Source', 'Source ID', 'Owner ID',
        'Has Alerts', 'Website', 'Types', 'Category'
    )
    return data_headers, data_list, source


@artifact_processor
def Life360_PlaceAlerts(context):
    source = _find(context, 'L360LocalStoreRoomDatabase')
    data_list = []

    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()

        for row in _q(cursor, '''
            SELECT
                place_alerts.place_id,
                place_alerts.circle_id,
                place_alerts.member_id,
                place_alerts.name,
                place_alerts.arrive,
                place_alerts.leave,
                places.latitude,
                places.longitude
            FROM place_alerts
            LEFT JOIN places ON places.place_id = place_alerts.place_id
            ORDER BY place_alerts.name
        '''):
            data_list.append((
                row[0], row[1], row[2],
                row[3],
                _bool(row[4]), _bool(row[5]),
                row[6], row[7]
            ))
        db.close()

    data_headers = (
        'Place ID', 'Circle ID', 'Member ID',
        'Place Name',
        'Arrive Alert', 'Leave Alert',
        'Latitude', 'Longitude'
    )
    return data_headers, data_list, source