__artifacts_v2__ = {
    "get_installedappsVending": {
        "name": "InstalledappsVending",
        "description": "Parses installed applications (package, title, first download and last updated times, install reason and account) from the Play Store localappstate.db.",
        "author": "",
        "creation_date": "2020-03-01",
        "last_update_date": "2020-03-01",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.android.vending/databases/localappstate.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.vending vc 84801930 | 93 rows",
            "galaxys10_a10": "Android 10 | com.android.vending vc 82481710 | 56 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.vending vc 85180930 | 147 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.vending vc 84812830 | 97 rows",
            "pixel7a_a14": "Android 14 | com.android.vending vc 84191730 | 155 rows",
            "samsunga53_a14": "Android 14 | com.android.vending vc 84913330 | 204 rows",
            "samsungs20_a13": "Android 13 | com.android.vending vc 84962330 | 150 rows",
            "sharon_a14": "Android 14 | com.android.vending vc 84222730 | 122 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.vending vc 83631220 | 204 rows",
            "userb2_a13": "Android 13 | com.android.vending vc 84371930 | 214 rows",
        },
    }
}

import datetime
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_column_exist_in_db


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_installedappsVending(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('localappstate.db'):
            continue

        user = Path(file_found).parts[-4]
        if user == 'data':
            user = '0'

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        if does_column_exist_in_db(file_found, 'appstate', 'install_reason'):
            install_reason_query = 'install_reason'
        else:
            install_reason_query = "'' as install_reason"

        cursor.execute(f'''
            SELECT first_download_ms, package_name, title, {install_reason_query},
                   last_update_timestamp_ms,
                   CASE auto_update WHEN '0' THEN '' WHEN '1' THEN 'Yes' END AS 'Auto_Updated',
                   account
            FROM appstate
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((user, _ms_to_utc(row[0]), row[1], row[2], row[3], _ms_to_utc(row[4]), row[5], row[6]))

    data_headers = ('User', ('First Download', 'datetime'), 'Package Name', 'Title', 'Install Reason', ('Last Updated', 'datetime'), 'Auto Update?', 'Account')
    return data_headers, data_list, source_path
