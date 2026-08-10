__artifacts_v2__ = {
    "get_samsungSmartThings": {
        "name": "samsungSmartThings",
        "description": "Samsung SmartThings",
        "author": "Kevin Pagano (@KevinPagno3)",
        "creation_date": "2022-06-13",
        "last_update_date": "2022-06-13",
        "requirements": "none",
        "category": "Samsung SmartThings",
        "notes": "",
        "paths": ('*/com.samsung.android.oneconnect/databases/QcDB.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

# Samsung SmartThings
# Author: Kevin Pagano (@KevinPagno3)
# Date: 2022-06-13
# Artifact version: 0.0.1
# Requirements: none

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_samsungSmartThings(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('QcDB.db'):
            continue  # Skip all other files

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timeStamp/1000,'unixepoch'),
        deviceName,
        deviceType,
        netType,
        wifiP2pMac,
        btMac,
        bleMac
        from devices
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6]))
        db.close()

    data_headers = (
        ('Connection Timestamp', 'datetime'),
        'Device Name',
        'Device Type',
        'Net Type',
        'Wifi P2P MAC',
        'Bluetooth MAC',
        'Bluetooth (LE) MAC',
    )
    return data_headers, data_list, source_path
