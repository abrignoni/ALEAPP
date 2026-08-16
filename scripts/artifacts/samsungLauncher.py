__artifacts_v2__ = {
    "samsungLauncherItems": {
        "name": "Samsung Launcher Items",
        "description": "Home screen and app screen layout of the Samsung One UI launcher "
                       "(OneUI.db, item table): each item's title, component, position, "
                       "container and hidden flag. Type and container codes are stored as "
                       "raw values and are reported as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.sec.android.app.launcher/databases/OneUI.db*',),
        "output_types": "standard",
        "artifact_icon": "grid",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.launcher | 90 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.launcher | 118 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.launcher | 111 rows",
        },
    },
    "samsungLauncherIcons": {
        "name": "Samsung Launcher Icons",
        "description": "App icon cache of the Samsung One UI launcher (Icon.db, icon "
                       "table): the component name, displayed label, Android user profile "
                       "and when the entry was last updated.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.sec.android.app.launcher/databases/Icon.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.launcher | 62 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.launcher | 92 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.launcher | 90 rows",
        },
    },
}

import re

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -wal/-shm sidecars and without the
    duplicates extractions carry for the same file (data_mirror, and /data/data next
    to /data/user/0).

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
def samsungLauncherItems(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'OneUI.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT title, component, type, item_position, position_x, position_y, rank,
                   container_type, container_id, hidden, profile_id, restored,
                   reference_package_name
            FROM item
            ORDER BY container_type, container_id, rank
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append(tuple(row))

    data_headers = (
        'Title',
        'Component',
        'Type',
        'Item Position',
        'Position X',
        'Position Y',
        'Rank',
        'Container Type',
        'Container ID',
        'Hidden',
        'Profile ID',
        'Restored',
        'Reference Package',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungLauncherIcons(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'Icon.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT last_updated, label, component_name, profile_id, version
            FROM icon
            ORDER BY last_updated DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                row[1],
                row[2],
                row[3],
                row[4],
            ))

    data_headers = (
        ('Last Updated', 'datetime'),
        'Label',
        'Component Name',
        'Profile ID',
        'Version',
    )
    return data_headers, data_list, source_path
