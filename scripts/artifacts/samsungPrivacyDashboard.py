__artifacts_v2__ = {
    "samsungPrivacyDashboardAccess": {
        "name": "Samsung Privacy Dashboard Permission Access",
        "description": "Permission accesses logged by the Samsung Privacy Dashboard "
                       "(permission_db, permissionAccessInformations table): the accessing "
                       "package, permission group, access time and whether the access "
                       "happened in the background. The operation code is stored as a raw "
                       "integer and is reported as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Permissions",
        "notes": "More info: https://blog.digital-forensics.it/2025/11/beyond-known-call-to-forensic-research.html. "
                 "The UID column does not exist on older One UI versions and is reported "
                 "empty there.",
        "paths": ('*/com.samsung.android.privacydashboard/databases/permission_db*',),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.privacydashboard | 3758 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.privacydashboard | 652 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.privacydashboard | 239 rows",
            "sharon_a14": "Android 14 | com.samsung.android.privacydashboard | 2232 rows",
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
def samsungPrivacyDashboardAccess(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'permission_db'):
        # older One UI versions do not have the UID column
        uid_column = 'UID' if does_column_exist_in_db(
            file_found, 'permissionAccessInformations', 'UID') else "''"
        db_records = get_sqlite_db_records(file_found, f'''
            SELECT ACCESS_TIME, PACKAGE_NAME, PERMISSION_GROUP_ID, OPERATION_CODE,
                   BACKGROUND, PROXY_NAME, PROXY_ATTRIBUTION_TAG, {uid_column}
            FROM permissionAccessInformations
            ORDER BY ACCESS_TIME DESC
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
                row[7],
            ))

    data_headers = (
        ('Access Time', 'datetime'),
        'Package Name',
        'Permission Group',
        'Operation Code',
        'Background',
        'Proxy Name',
        'Proxy Attribution Tag',
        'UID',
    )
    return data_headers, data_list, source_path
