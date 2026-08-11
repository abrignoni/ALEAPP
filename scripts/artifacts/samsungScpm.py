__artifacts_v2__ = {
    "samsungScpmDevices": {
        "name": "Samsung Cloud Platform Devices",
        "description": "Devices recorded by the Samsung Cloud Platform Manager (scpmv2.db, "
                       "devices table): device alias, model, OS version, country and SIM "
                       "codes, with the registration and last access times.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/com.samsung.android.scpm/databases/scpmv2.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.scpm | 1 row",
            "samsunga53_a14": "Android 14 | com.samsung.android.scpm | 2 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.scpm | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.scpm | 1 row",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, does_table_exist_in_db


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -wal/-shm sidecars and without the
    duplicates extractions carry for the same file (data_mirror, and /data/data next
    to /data/user/0).'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        if 'data_mirror' in file_found:
            continue
        normalized = file_found.replace('\\', '/').replace('/data/data/', '/data/user/0/')
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


@artifact_processor
def samsungScpmDevices(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'scpmv2.db'):
        # some One UI builds (seen on an SM-G991B image) ship scpmv2.db without a
        # devices table; skip those rather than raising "no such table: devices"
        if not does_table_exist_in_db(file_found, 'devices'):
            continue
        db_records = get_sqlite_db_records(file_found, '''
            SELECT registration_time, last_access_time, alias, type, model_name,
                   model_code, os_type, os_version, platform_version, country_code,
                   sim_mcc, sim_mnc, csc, id
            FROM devices
            ORDER BY registration_time DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                row[12],
                row[13],
            ))

    data_headers = (
        ('Registration Time', 'datetime'),
        ('Last Access Time', 'datetime'),
        'Alias',
        'Type',
        'Model Name',
        'Model Code',
        'OS Type',
        'OS Version',
        'Platform Version',
        'Country Code',
        'SIM MCC',
        'SIM MNC',
        'CSC',
        'Device ID',
    )
    return data_headers, data_list, source_path
