__artifacts_v2__ = {
    "extract_android_auto": {
        "name": "Android Auto - Connected Cars",
        "description": "Android Auto connected cars",
        "author": "its5Q",
        "creation_date": "2025-07-28",
        "last_update_date": "2026-05-28",
        "requirements": "none",
        "category": "Android Auto",
        "notes": "",
        "paths": ('*/com.google.android.projection.gearhead/databases/carservicedata.db*'),
        "output_types": "standard",
        "artifact_icon": "truck",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.projection.gearhead vc 151653424 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.projection.gearhead vc 152653624 | 3 rows",
            "pixel7a_a14": "Android 14 | com.google.android.projection.gearhead vc 123642624 | 1 row",
            "samsunga53_a14": "Android 14 | com.google.android.projection.gearhead vc 156654484 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.projection.gearhead vc 124642854 | 0 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_unix_ts_to_utc

@artifact_processor
def extract_android_auto(context):
    data_list = []
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "carservicedata.db") 

    query = '''
    SELECT
    connectiontime,
    manufacturer,
    model,
    modelyear,
    bluetoothaddress,
    wifissid,
    wifibssid,
    wifipassword,
    headUnitMake,
    headUnitModel,
    headUnitSoftwareVersion,
    vehicleidclient
    FROM allowedcars;
    '''

    data_headers = (('Connection Time', 'datetime'), 'Manufacturer', 'Model', 'Year', 'Bluetooth MAC', 'Wi-Fi SSID', 'Wi-Fi BSSID', 'Wi-Fi Password', 'Head Unit Make', 'Head Unit Model', 'Head Unit Software Version', 'Vehicle Client ID')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        connectiontime = convert_unix_ts_to_utc(record[0])

        data_list.append((connectiontime, record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11]))

    return data_headers, data_list, source_path