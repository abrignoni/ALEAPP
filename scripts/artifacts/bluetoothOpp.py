__artifacts_v2__ = {
    "get_bluetooth_opp": {
        "name": "Bluetooth File Transfers",
        "description": "Rows of the btopp table in the Android Bluetooth app's btopp.db: transfer records with the stored remote address, device name, file name, MIME type, direction, status and byte counts",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "One row per row of the btopp table of each btopp.db found (the Bluetooth app's database in "
                 "device encrypted storage, one per Android user, storage views of one copy collapsed; Source "
                 "File names the database). The columns are reported as stored. Direction, Visibility, Confirm, "
                 "Status and Scanned are integers reported as stored: no row was available to read, so no value "
                 "was checked against what the device did and none is translated. Destination is the "
                 "destination column and Device Name the device_name column. File Path is the _data column and "
                 "URI the uri column; whether the file still exists on the device is not checked. Timestamp is "
                 "the timestamp column read as Unix time with the core's second or millisecond detection; no "
                 "row with a timestamp was available, so which unit the column holds is not verified, and what "
                 "event the time marks is not established. "
                 "A row is a record in the Bluetooth app's table and is not by itself proof that a file "
                 "reached the other device; the table being empty is not evidence that no file was ever "
                 "transferred over Bluetooth. Transfers made through other mechanisms (Quick Share, Nearby "
                 "Share, messaging apps) are not in this table. "
                 "Validation boundary: the schema (table btopp with _id, uri, hint, _data, mimetype, direction, "
                 "destination, visibility, confirm, status, total_bytes, current_bytes, timestamp, scanned, "
                 "device_name, reserved; user_version 2) was read from four real Android 16 databases under "
                 "data/user_de/0/com.android.bluetooth/databases, all with no rows, so row values have not been "
                 "decoded from real data and the row handling was exercised on a constructed database only. "
                 "The com.google.android.bluetooth path (the Bluetooth module on some builds) is included from "
                 "the module's naming and was not seen in an extraction.",
        "paths": ('*/com.android.bluetooth/databases/btopp.db*',
                  '*/com.google.android.bluetooth/databases/btopp.db*'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.android.bluetooth | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.android.bluetooth | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.android.bluetooth | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.android.bluetooth | 0 rows",
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
