# snapchatMEO: Brute-force SnapChat My Eyes Only PIN Code
# Author: David Mann {Twitter: @Sector7Reactor}
# Date: 17/06/2022
# Artifact version: 1.0.0
# Android version tested: 12
# Requirements: None

import bcrypt
import sqlite3
import itertools
import string

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, media_to_html, open_sqlite_db_readonly


def bruteforceMEO(encrypted_password):

    for numbers in itertools.product(string.digits, repeat=4):

        pin = ''.join(numbers)
        check_hash_match = bcrypt.checkpw(pin.encode('utf-8'), encrypted_password.encode('utf-8'))

        if check_hash_match == True:
            logfunc(f'PIN code match found: {pin}')

            return encrypted_password, pin
    else:
        return None

def get_snapchatMEO(files_found, report_folder, seeker, wrap_text):

    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        connection = open_sqlite_db_readonly(file_found)

        pointer = connection.cursor()
        try:
            pointer.execute("SELECT hashed_passcode FROM memories_meo_confidential")
            encrypted_password = pointer.fetchone()[0]
        except:
            continue

        if encrypted_password != '':
            logfunc(f'Encrypted PIN Found: {encrypted_password}')

            try:
                data_list.append((bruteforceMEO(encrypted_password)))
            except:
                continue

            if data_list != [None]:
                report = ArtifactHtmlReport('SnapChat My Eyes Only PIN')
                report.start_artifact_report(report_folder, 'SnapChat My Eyes Only PIN')
                report.add_script()
                data_headers = ('Encrypted PIN', 'Decrypted PIN')

                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media'])
                report.end_artifact_report()

                tsvname = f'SnapChat My Eyes Only PIN'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc('No PIN code found.')
        else:
            logfunc('No encrypted PIN hash found in Database.')