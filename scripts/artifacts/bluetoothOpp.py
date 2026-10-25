__artifacts_v2__ = {
    "get_bluetooth_opp": {
        "name": "Bluetooth File Transfers",
        "description": "Rows of the btopp table in the Android Bluetooth app's btopp.db: transfer records with the destination Bluetooth device address, the device name where the schema has that column, file name, MIME type, direction, status and byte counts",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "One row per row of the btopp table of each btopp.db found (the Bluetooth app's database in "
                 "device encrypted storage, one per Android user, storage views of one copy collapsed; Source "
                 "File names the database). A copy found under data/misc_de/<user>/rollback/<id>/<package>/ "
                 "is read as its own database, and its rows, if any, carry its own Source File. Columns other than "
                 "Timestamp are reported as stored. Destination is the destination column and Device Name the device_name "
                 "column. File Path is the _data column and URI the uri column; whether the file still exists on "
                 "the device is not checked. "
                 "Direction, Visibility, Confirm, Status and Scanned are integers reported as stored, not "
                 "translated. In the AOSP Bluetooth source, direction 0 is outbound and 1 inbound; visibility 0 "
                 "is visible and 1 hidden; confirm 0 is pending, 1 confirmed, 2 auto-confirmed, 3 denied, 4 timed "
                 "out and 5 handover-confirmed; status 190 is pending, 192 running and 200 success, and codes 400 "
                 "to 599 are errors (BluetoothShare.java). The provider fills timestamp with "
                 "System.currentTimeMillis() when the inserting code gives none (BluetoothOppProvider.java, insert). "
                 "Reference: https://android.googlesource.com/platform/packages/modules/Bluetooth/+/"
                 "745ee92b87ed62b5a8a1bac47d5df8cad623bf59/android/app/src/com/android/bluetooth/opp/. Whether "
                 "a device maker's build uses the same codes was not examined. Timestamp is the timestamp column "
                 "read as Unix time with the core's magnitude-based unit detection (seconds, milliseconds, "
                 "microseconds or nanoseconds). AOSP describes the column as the time the transfer was "
                 "initialized (BluetoothShare.java, TIMESTAMP); whether a device maker's build updates it later "
                 "was not examined. "
                 "A row is a record in the Bluetooth app's table and is not by itself proof that a file "
                 "reached the other device; the table being empty is not evidence that no file was ever "
                 "transferred over Bluetooth. Only the Bluetooth app's OPP provider writes this table (BluetoothOppProvider.java). Transfers "
                 "made through other mechanisms, such as Quick Share, Nearby Share or messaging apps, were not "
                 "examined and are not expected here. "
                 "Validation boundary: btopp.db was found in 40 corpus images (100 copies counting storage views, "
                 "second users and one rollback copy), under com.android.bluetooth in 14 and "
                 "com.google.android.bluetooth in 26, with three schemas: 14 columns (_id, uri, hint, _data, "
                 "mimetype, direction, destination, visibility, confirm, status, total_bytes, current_bytes, "
                 "timestamp, scanned; user_version 1) in 29 images, the same plus device_name and reserved "
                 "(user_version 2) in 10 images, and the 14 plus carrier_name (user_version 2, no device_name) in "
                 "1 image. Device Name is blank where the column is absent, and carrier_name is not read. Two "
                 "copies held rows, one row each (see sample_data), both in the 16-column schema: each had "
                 "direction 1, status 200, confirm 1, scanned 1 and a 13-digit timestamp, read here as "
                 "milliseconds. No row was seen in the 14- or 15-column schema, or in a second Android user's or "
                 "rollback copy. Second-user row handling was exercised on a constructed database (test case "
                 "casesynthetic_btopp_users); rows in the 14- or 15-column schema and in a rollback copy were not "
                 "exercised, and go through the same query with Device Name reported empty where the column is absent. The four "
                 "Android 16 databases the artifact was first written against held the 16-column schema "
                 "(user_version 2) and no rows.",
        "paths": ('*/com.android.bluetooth/databases/btopp.db*',
                  '*/com.google.android.bluetooth/databases/btopp.db*'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.android.bluetooth | 1 row",
            "cookbook_a11": "Android 11 | com.android.bluetooth | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.bluetooth | 0 rows",
            "russell_a14": "Android 14 | com.google.android.bluetooth | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.bluetooth | 0 rows",
        },
    }
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, null_absent_columns


@artifact_processor
def get_bluetooth_opp(context):
    data_headers = (('Timestamp', 'datetime'), 'ID', 'Direction (as stored)', 'Destination', 'Device Name',
                    'File Path', 'Hint', 'URI', 'MIME Type', 'Status (as stored)', 'Total Bytes',
                    'Current Bytes', 'Visibility (as stored)', 'Confirm (as stored)', 'Scanned (as stored)',
                    'Source File')
    data_list = []
    sources = []
    query = '''
    SELECT
    timestamp,
    _id,
    direction,
    destination,
    device_name,
    _data,
    hint,
    uri,
    mimetype,
    status,
    total_bytes,
    current_bytes,
    visibility,
    confirm,
    scanned
    FROM btopp
    ORDER BY _id;
    '''
    for file_found in unique_files(context):
        if os.path.basename(file_found) != 'btopp.db':
            continue
        sources.append(file_found)
        relative = context.get_relative_path(file_found)
        for record in get_sqlite_db_records(file_found, null_absent_columns(file_found, query)):
            data_list.append((convert_unix_ts_to_utc(record[0]),) + tuple(record[1:]) + (relative,))

    return data_headers, data_list, '\n'.join(sources)
