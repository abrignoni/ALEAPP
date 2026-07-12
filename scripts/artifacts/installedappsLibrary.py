# pylint: disable=W0613
__artifacts_v2__ = {
    "get_installedappsLibrary": {
        "name": "InstalledappsLibrary",
        "description": "Parses app purchase and ownership records (purchase time, account and doc ID) from the Play Store library.db.",
        "author": "",
        "creation_date": "2020-03-01",
        "last_update_date": "2020-03-01",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.android.vending/databases/library.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.vending vc 84801930 | 73 rows",
            "galaxys10_a10": "Android 10 | com.android.vending vc 82481710 | 62 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.vending vc 85180930 | 116 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.vending vc 84812830 | 69 rows",
            "pixel7a_a14": "Android 14 | com.android.vending vc 84191730 | 145 rows",
            "samsunga53_a14": "Android 14 | com.android.vending vc 84913330 | 384 rows",
            "samsungs20_a13": "Android 13 | com.android.vending vc 84962330 | 162 rows",
            "sharon_a14": "Android 14 | com.android.vending vc 84222730 | 99 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.vending vc 83631220 | 160 rows",
            "userb2_a13": "Android 13 | com.android.vending vc 84371930 | 178 rows",
        },
    }
}

import datetime
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_installedappsLibrary(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('library.db'):
            continue

        user = Path(file_found).parts[-4]
        if user == 'data':
            user = '0'

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT purchase_time, account, doc_id
            FROM ownership
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            purchase_time = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((user, purchase_time, row[1], row[2]))

    data_headers = ('User', ('Purchase Time', 'datetime'), 'Account', 'Doc ID')
    return data_headers, data_list, source_path
