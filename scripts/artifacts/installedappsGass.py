# pylint: disable=W0613
__artifacts_v2__ = {
    "get_installedappsGass": {
        "name": "installedappsGass",
        "description": "Parses installed applications (bundle ID, version code and SHA-256 hash) from the Google Play services gass.db.",
        "author": "",
        "creation_date": "2020-03-01",
        "last_update_date": "2020-03-01",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.google.android.gms/databases/gass.db*', '*/user/*/com.google.android.gms/databases/gass.db*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
    }
}

from scripts.ilapfuncs import artifact_processor, is_platform_windows, open_sqlite_db_readonly


@artifact_processor
def get_installedappsGass(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue

        source_path = file_found
        if 'user' in file_found:
            usernum = str(file_found.split(slash)[-4])
        else:
            usernum = '0'

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT distinct(package_name), version_code, digest_sha256
            FROM app_info
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((usernum, row[0], row[1], row[2]))

    data_headers = ('User', 'Bundle ID', 'Version Code', 'SHA-256 Hash')
    return data_headers, data_list, source_path
