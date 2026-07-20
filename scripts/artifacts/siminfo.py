__artifacts_v2__ = {
    "get_siminfo": {
        "name": "siminfo",
        "description": "SIM card details (number, IMSI, ICCID, carrier) from the telephony provider database",
        "author": "",
        "creation_date": "2020-03-02",
        "last_update_date": "2020-03-02",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/user_de/*/com.android.providers.telephony/databases/telephony.db',),
        "output_types": "standard",
        "artifact_icon": "info-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.telephony | 1 row",
            "galaxys10_a10": "Android 10 | com.android.providers.telephony | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.telephony | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.telephony | 3 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.telephony | 1 row",
            "samsunga53_a14": "Android 14 | com.android.providers.telephony | 2 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.telephony | 2 rows",
            "sharon_a14": "Android 14 | com.android.providers.telephony | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.telephony | 2 rows",
            "userb2_a13": "Android 13 | com.android.providers.telephony | 1 row",
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, logdevinfo, open_sqlite_db_readonly

PRIMARY_SQL = '''
    SELECT number, imsi, display_name, carrier_name, iso_country_code, carrier_id, icc_id
    FROM siminfo
'''

FALLBACK_SQL = '''
    SELECT number, card_id, display_name, carrier_name, carrier_name, carrier_name, icc_id
    FROM siminfo
'''


@artifact_processor
def get_siminfo(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        # Skip mirrored copies (e.g. magisk mirror) which duplicate the data
        if '/mirror/' in file_found:
            continue
        # Path layout: .../user_de/<uid>/com.android.providers.telephony/databases/telephony.db
        parts = file_found.split('/')
        try:
            uid = parts[-4]
            int(uid)  # uid must be numeric
        except (IndexError, ValueError):
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute(PRIMARY_SQL)
        except sqlite3.Error:
            cursor.execute(FALLBACK_SQL)
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            # When the fallback schema is used, carrier_name fills the iso/carrier_id
            # slots (row[3] == row[4]); blank those out so they aren't shown as data.
            if row[3] == row[4]:
                imsi, iso_code, carrier_id = '', '', ''
            else:
                imsi, iso_code, carrier_id = row[1], row[4], row[5]
            data_list.append((uid, row[0], imsi, row[2], row[3], iso_code, carrier_id, row[6]))
            logdevinfo(f"<b>SIM Number & IMSI: </b>{row[0]} - {imsi}")
            logdevinfo(f"<b>SIM Display Name: </b>{row[2]}")
        source_paths.append(file_found)

    data_headers = (
        'User ID', ('Number', 'phonenumber'), 'IMSI', 'Display Name',
        'Carrier Name', 'ISO Code', 'Carrier ID', 'ICC ID')
    return data_headers, data_list, ', '.join(source_paths)
