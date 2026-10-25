__artifacts_v2__ = {
    "extract_android_auto": {
        "name": "Android Auto - Allowed Cars",
        "description": "Rows of the allowedcars table in Android Auto's carservicedata.db: car and head unit details with the stored connectiontime value",
        "author": "its5Q, @AlexisBrignoni, Codex",
        "creation_date": "2025-07-28",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Android Auto",
        "notes": "One row per row of the allowedcars table. The same database also has a rejectedcars table with "
                 "the same columns, which the Android Auto - Rejected Cars artifact reads. Android Auto is closed source and what places "
                 "a car in allowedcars, or what event the connectiontime column marks, is not established; a row is "
                 "not by itself shown to be a completed connection. The connectiontime column is declared INTEGER and "
                 "held a 13-digit value on all 7 rows of the tested images, read here as Unix milliseconds and shown "
                 "in UTC to the second. Every copy of carservicedata.db found is read, one per Android user with the storage views of one copy collapsed, and Source File names the copy a row came from.",
        "paths": ('*/com.google.android.projection.gearhead/databases/carservicedata.db*'),
        "output_types": "standard",
        "artifact_icon": "truck",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.projection.gearhead vc 151653424 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.projection.gearhead vc 152653624 | 3 rows",
            "pixel7a_a14": "Android 14 | com.google.android.projection.gearhead vc 123642624 | 1 row",
            "samsunga53_a14": "Android 14 | com.google.android.projection.gearhead vc 156654484 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.projection.gearhead vc 124642854 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.projection.gearhead vc 97632214 | 2 rows",
            "userb2_a13": "Android 13 | com.google.android.projection.gearhead vc 132644464 | 0 rows",
        },
    },
    "extract_android_auto_rejected": {
        "name": "Android Auto - Rejected Cars",
        "description": "Rows of the rejectedcars table in Android Auto's carservicedata.db: car and head unit details with the stored connectiontime value",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Android Auto",
        "notes": "One row per row of the rejectedcars table, which has the same columns as allowedcars and is read "
                 "with the same code as Android Auto - Allowed Cars, whose notes describe the columns. Android Auto "
                 "is closed source and what places a car in rejectedcars, or what event the connectiontime column "
                 "marks, is not established; the table name is the only thing the database says about why a row is "
                 "there. Validation boundary: in the one real database examined the rejectedcars table was present "
                 "with the same 24 columns as allowedcars and held no rows, so the stored values of a rejectedcars "
                 "row (including whether connectiontime and the Wi-Fi columns are filled the way allowedcars rows "
                 "are) have not been decoded from real data, and the row handling was exercised on a constructed "
                 "database only. An empty table is not evidence that no car was ever rejected. Every copy of carservicedata.db found is read, one per Android user with the storage views of one copy collapsed, and Source File names the copy a row came from.",
        "paths": ('*/com.google.android.projection.gearhead/databases/carservicedata.db*',),
        "output_types": "standard",
        "artifact_icon": "truck",
        "sample_data": {},
    }
}

import os

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, null_absent_columns, convert_unix_ts_to_utc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files

_CARS_QUERY = '''
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
    FROM {table};
    '''


def _has_table(source_path, table):
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return False
    try:
        return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is not None
    finally:
        db.close()


def _car_rows(context, table):
    """(rows, source paths) of one table in every carservicedata.db found.

    table is one of two fixed names below, never a value from the evidence. A database
    without the table (an older one) contributes no rows.
    """
    query = _CARS_QUERY.format(table=table)
    data_list = []
    sources = []
    for source_path in unique_files(context):
        if os.path.basename(source_path) != 'carservicedata.db':
            continue
        sources.append(source_path)
        if not _has_table(source_path, table):
            continue
        relative = context.get_relative_path(source_path)
        for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
            connectiontime = convert_unix_ts_to_utc(record[0])
            data_list.append((connectiontime, record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], relative))
    return data_list, '\n'.join(sources)


@artifact_processor
def extract_android_auto(context):
    data_headers = (('connectiontime', 'datetime'), 'Manufacturer', 'Model', 'Year', 'Bluetooth MAC', 'Wi-Fi SSID', 'Wi-Fi BSSID', 'Wi-Fi Password', 'Head Unit Make', 'Head Unit Model', 'Head Unit Software Version', 'Vehicle Client ID', 'Source File')
    data_list, source_path = _car_rows(context, 'allowedcars')

    return data_headers, data_list, source_path


@artifact_processor
def extract_android_auto_rejected(context):
    data_headers = (('connectiontime', 'datetime'), 'Manufacturer', 'Model', 'Year', 'Bluetooth MAC', 'Wi-Fi SSID', 'Wi-Fi BSSID', 'Wi-Fi Password', 'Head Unit Make', 'Head Unit Model', 'Head Unit Software Version', 'Vehicle Client ID', 'Source File')
    data_list, source_path = _car_rows(context, 'rejectedcars')

    return data_headers, data_list, source_path
