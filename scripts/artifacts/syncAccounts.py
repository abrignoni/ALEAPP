__artifacts_v2__ = {
    "syncAccountsXml": {
        "name": "Account Sync Authorities",
        "description": "Per-account sync authorities from /data/system/sync/accounts.xml: one row "
                       "per authority element, with the account, account type, authority, and the "
                       "enabled and syncable attributes as stored.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Accounts",
        "notes": "A row is an authority element of accounts.xml. Its presence does not show that "
                 "the account synced that data, and no source for the values of enabled and "
                 "syncable is given here. A copy of the file whose path in the extraction has a "
                 "data_mirror folder is skipped. Every file read is named as the source.",
        "paths": ('*/system/sync/accounts.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "refresh-cw",
        "sample_data": {
            "anne_a15": "Android 15 | 33 rows",
            "galaxys10_a10": "Android 10 | 31 rows",
            "hc_pixel8pro_a16": "Android 16 | 24 rows",
            "kevin_pocox7_a15": "Android 15 | 36 rows",
            "pixel7a_a14": "Android 14 | 41 rows",
            "russell_pixel6a_a13": "Android 13 | 53 rows",
            "samsunga53_a14": "Android 14 | 44 rows",
            "samsungs20_a13": "Android 13 | 44 rows",
            "sharon_a14": "Android 14 | 39 rows",
            "userb2_a13": "Android 13 | 21 rows",
        },
    },
}

from scripts.artifacts.settingsSecure import parse_settings_root
from scripts.ilapfuncs import artifact_processor


@artifact_processor
def syncAccountsXml(context):
    data_list = []
    source_paths = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        relative = context.get_relative_path(file_found).replace('\\', '/')
        if 'data_mirror' in relative.split('/'):
            continue
        if file_found in source_paths:
            continue

        root = parse_settings_root(file_found, 'syncAccounts')
        if root is None:
            continue

        source_paths.append(file_found)
        for authority in root.iter('authority'):
            data_list.append((
                authority.get('user'),
                authority.get('account'),
                authority.get('type'),
                authority.get('authority'),
                authority.get('enabled'),
                authority.get('syncable'),
                authority.get('id'),
            ))

    data_headers = (
        'User',
        'Account',
        'Account Type',
        'Authority',
        'Enabled',
        'Syncable',
        'ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
