__artifacts_v2__ = {
    "syncAccountsXml": {
        "name": "Account Sync Authorities",
        "description": "Per-account sync authorities from /data/system/sync/accounts.xml: "
                       "which data types each account on the device syncs, whether syncing "
                       "is enabled and the syncable state.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
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
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if 'data_mirror' in file_found:
            continue

        root = parse_settings_root(file_found, 'syncAccounts')
        if root is None:
            continue

        source_path = file_found
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
    return data_headers, data_list, source_path
