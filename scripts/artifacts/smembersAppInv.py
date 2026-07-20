__artifacts_v2__ = {
    "get_smembersAppInv": {
        "name": "smembersAppInv",
        "description": "Parses the Samsung Members app inventory (last used, display and package name, system-app flag, hashes and classification) from the com_pocketgeek_sdk_app_inventory database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/com.samsung.oh/databases/com_pocketgeek_sdk_app_inventory.db',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_smembersAppInv(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        select last_used, display_name, package_name, system_app, confidence_hash, sha1, classification
        from android_app
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        last_used = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
        data_list.append((last_used, row[1], row[2], row[3], row[4], row[5], row[6]))

    data_headers = (('Timestamp', 'datetime'), 'Display Name', 'Package Name', 'System App?', 'Confidence Hash', 'SHA1', 'Classification')
    return data_headers, data_list, source_path
