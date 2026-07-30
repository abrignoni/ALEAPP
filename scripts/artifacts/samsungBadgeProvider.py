__artifacts_v2__ = {
    "samsungBadgeApps": {
        "name": "Samsung Badge Provider",
        "description": "App icon badge counts recorded by the Samsung badge provider "
                       "(badge.db, apps table): the package and activity each badge belongs "
                       "to, its count and whether it is hidden.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Badge Provider",
        "notes": "More info: https://blog.digital-forensics.it/2025/11/beyond-known-call-to-forensic-research.html",
        "paths": ('*/com.sec.android.provider.badge/databases/badge.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.provider.badge | 18 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.provider.badge | 11 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.provider.badge | 20 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.provider.badge | 19 rows",
            "sharon_a14": "Android 14 | com.sec.android.provider.badge | 24 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


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
def samsungBadgeApps(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'badge.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT package, class, badgecount, hidden, extraData
            FROM apps
            ORDER BY package
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((row[0], row[1], row[2], row[3], row[4]))

    data_headers = (
        'Package',
        'Class',
        'Badge Count',
        'Hidden',
        'Extra Data',
    )
    return data_headers, data_list, source_path
