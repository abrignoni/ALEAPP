# pylint: disable=W0613
__artifacts_v2__ = {
    "get_chromeLoginData": {
        "name": "Login Data",
        "description": "Parses saved Login Data from Chromium Based Browsers",
        "author": "",
        "creation_date": "2020-03-20",
        "last_update_date": "2020-03-20",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Login Data*', '*/app_sbrowser/Default/Login Data*', '*/app_opera/Login Data*', '*/app_webview/Default/Login Data*'),
        "output_types": "standard",
        "artifact_icon": "key",
    }
}

import datetime
import os
import re

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, get_next_unused_name, open_sqlite_db_readonly, lava_process_artifact, lava_insert_sqlite_data, artifact_processor
from scripts.artifacts.chrome import get_browser_name


def decrypt(ciphertxt, key=b"peanuts"):
    if re.match(rb"^v1[01]",ciphertxt):
        ciphertxt = ciphertxt[3:]
    salt = b"saltysalt"
    derived_key = PBKDF2(key, salt, 0x10, 1)
    iv = b" "*0x10
    cipher = AES.new(derived_key, AES.MODE_CBC, IV=iv)
    try:
        plaintxt_pad = cipher.decrypt(ciphertxt)
        plaintxt = plaintxt_pad[:-ord(plaintxt_pad[len(plaintxt_pad)-1:])]
    except ValueError as ex:
        logfunc('Exception while decrypting data: ' + str(ex))
        plaintxt = b''
    return plaintxt


def get_valid_date(d1, d2):
    '''Returns a valid date based on closest year to now'''
    # Since the dates in question will be hundreds of years apart, this should be easy
    if d1 == '': return d2
    if d2 == '': return d1

    year1 = int(d1[0:4])
    year2 = int(d2[0:4])

    today = datetime.datetime.today()
    diff1 = abs(today.year - year1)
    diff2 = abs(today.year - year2)

    if diff1 < diff2:
        return d1
    else:
        return d2


@artifact_processor
def get_chromeLoginData(files_found, report_folder, seeker, wrap_text):
    all_data = []

    data_headers = ['Created Time', 'Username', 'Password', 'Origin URL', 'Blacklisted by User']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']

    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Login Data':  # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        username_value,
        password_value,
        CASE date_created
            WHEN "0" THEN ""
            ELSE datetime(date_created / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "date_created_win_epoch",
        CASE date_created WHEN "0" THEN ""
            ELSE datetime(date_created / 1000000 + (strftime('%s', '1970-01-01')), "unixepoch")
            END AS "date_created_unix_epoch",
        origin_url,
        blacklisted_by_user
        FROM logins
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

            data_list = []
            for row in all_rows:
                password = ''
                password_enc = row[1]
                if password_enc:
                    password = decrypt(password_enc).decode("utf-8", 'replace')
                valid_date = get_valid_date(row[2], row[3])
                data_list.append((valid_date, row[0], password, row[4], row[5]))

            report_name = f'{browser_name} - Login Data'
            report = ArtifactHtmlReport(report_name)
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            category = "Chromium"
            module_name = "get_chromeLoginData"
            table_name, object_columns, column_map = lava_process_artifact(
                category, module_name, report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Login Data available')

        db.close()

    return all_data_headers, all_data, report_file
