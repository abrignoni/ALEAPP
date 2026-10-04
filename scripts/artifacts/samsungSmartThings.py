__artifacts_v2__ = {
    "get_samsungSmartThings": {
        "name": "samsungSmartThings",
        "description": "Rows of the devices table in the Samsung SmartThings QcDB.db: timeStamp (as UTC), device name, type, network type and MAC addresses as stored. What event timeStamp marks is not established.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2022-06-13",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Samsung SmartThings",
        "notes": "The first column is the devices table's timeStamp column, read as Unix milliseconds and shown as UTC. What event that value marks is not established, and the column carries the stored field's name for that reason. No registered corpus holds this database (20 zip listings and 24 tar indexes checked on 2026-10-04), so the millisecond reading is the module's existing conversion and was not measured.",
        "paths": ('*/com.samsung.android.oneconnect/databases/QcDB.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

# Samsung SmartThings
# Author: Kevin Pagano (@stark4n6)
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
        ('timeStamp', 'datetime'),
        'Device Name',
        'Device Type',
        'Net Type',
        'Wifi P2P MAC',
        'Bluetooth MAC',
        'Bluetooth (LE) MAC',
    )
    return data_headers, data_list, source_path
