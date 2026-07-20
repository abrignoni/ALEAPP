__artifacts_v2__ = {
    'Life360_CircleSettings': {
        'name': 'Life360 CircleSettings',
        'description': 'Parses Life360 Circle Settings',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-11',
        'last_update_date': '2026-06-12',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/L360LocalStoreRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'circle',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 1 row',
            'pixel7a_a14': 'Android 14 | com.life360.android.safetymapd vc 294540 | 0 rows',
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    logfunc
)

@artifact_processor
def Life360_CircleSettings(context):

    data_list = []

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'L360LocalStoreRoomDatabase')

    query = '''
    SELECT
        je.key AS "Circle ID",
        json_extract(je.value, '$.featureSetId') AS "App Features",
        json_extract(je.value, '$.featureSetRefId') AS "App Features ID",
        json_extract(je.value, '$.features.collision_alerts_push') AS "Collision Alerts Push",
        json_extract(je.value, '$.features.collision_alerts_sms') AS "Collision Alerts SMS",
        json_extract(je.value, '$.features.customer_support') AS "Customer Support",
        json_extract(je.value, '$.features.data_breach_detection') AS "Data Breach Detection",
        json_extract(je.value, '$.features.driver_reports') AS "Driver Reports",
        json_extract(je.value, '$.features.location_history') AS "Location History",
        json_extract(je.value, '$.features.place_alerts') AS "Place Alerts",
        json_extract(je.value, '$.features.plan') AS "Plan",
        json_extract(je.value, '$.features.sos_alerts_push') AS "SOS Alerts Push",
        json_extract(je.value, '$.features.sos_alerts_sms') AS "SOS Alerts SMS",
        json_extract(je.value, '$.features.tilegps_activation') AS "TileGPS Activation",
        json_extract(je.value, '$.features.uber_one') AS "Uber One"
    FROM Premium p
    CROSS JOIN json_each(p.circleFeatureSetInfo) je;
    '''

    try:
        db_records = get_sqlite_db_records(source_path, query)

        logfunc(f'Life360_CircleSettings: Records found = {len(db_records)}')

        for record in db_records:

            data_list.append((record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], record[12], record[13], record[14]))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Error processing Life360 CircleSettings: {e}')

    data_headers = ('Circle ID', 'App Features', 'App Features ID', 'Collision Alerts Push', 'Collision Alerts SMS', 'Customer Support', 'Data Breach Detection', 'Driver Reports', 'Location History', 'Place Alerts', 'Plan', 'SOS Alerts Push', 'SOS Alerts SMS', 'TileGPS Activation', 'Uber One')

    return data_headers, data_list, source_path