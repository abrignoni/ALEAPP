__artifacts_v2__ = {
    "gmsAccountHistory": {
        "name": "Google Account History",
        "description": "History of Google accounts on the device recorded by Google Play "
                       "services (google_account_history.db, AccountHistory table). The "
                       "change type is stored as a raw integer and is reported as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Accounts",
        "notes": "More info: https://blog.digital-forensics.it/2024/01/a-first-look-at-android-14-forensics.html",
        "paths": ('*/com.google.android.gms/databases/google_account_history.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 1 row",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 2 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 2 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 2 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 1 row",
            "userb2_a13": "Android 13 | com.google.android.gms | 1 row",
        },
    },
}

import re

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -journal/-wal/-shm sidecars and
    without the duplicates extractions carry for the same file (data_mirror, and
    /data/data next to /data/user/0).

    The dedupe key is the evidence-relative path, not the extracted path: the report's own
    data folder ends in /data, so a raw-path replace can rewrite the harness boundary
    instead of the evidence path on archives whose members start with data/.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


@artifact_processor
def gmsAccountHistory(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'google_account_history.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT account_name, change_type, event_index, change_data
            FROM AccountHistory
            ORDER BY id
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((row[0], row[1], row[2], row[3]))

    data_headers = (
        'Account Name',
        'Change Type',
        'Event Index',
        'Change Data',
    )
    return data_headers, data_list, source_path
