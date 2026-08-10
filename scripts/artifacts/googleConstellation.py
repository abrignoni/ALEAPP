__artifacts_v2__ = {
    "constellationSimVerifications": {
        "name": "Constellation SIM Verifications",
        "description": "Phone numbers of SIM cards verified on the device by Google Play "
                       "services (constellation.db, sim_verifications table), with the IMSI "
                       "and verification time and method.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "The sim_slot column does not exist on older Play services versions and "
                 "is reported empty there. The state column is stored as a raw integer "
                 "and is reported as-is.",
        "paths": ('*/com.google.android.gms/databases/constellation.db*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 1 row",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 2 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 2 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 2 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 1 row",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 2 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, does_column_exist_in_db


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -journal/-wal/-shm sidecars and
    without the duplicates extractions carry for the same file (data_mirror, and
    /data/data next to /data/user/0).'''
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
def constellationSimVerifications(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'constellation.db'):
        # older Play services versions do not have the sim_slot column
        slot_column = 'sim_slot' if does_column_exist_in_db(
            file_found, 'sim_verifications', 'sim_slot') else "''"
        db_records = get_sqlite_db_records(file_found, f'''
            SELECT verification_time, phone_number, imsi, sim_readable_number, state,
                   verification_method, {slot_column}
            FROM sim_verifications
            ORDER BY verification_time DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
            ))

    data_headers = (
        ('Verification Time', 'datetime'),
        ('Phone Number', 'phonenumber'),
        'IMSI',
        ('SIM Readable Number', 'phonenumber'),
        'State',
        'Verification Method',
        'SIM Slot',
    )
    return data_headers, data_list, source_path
