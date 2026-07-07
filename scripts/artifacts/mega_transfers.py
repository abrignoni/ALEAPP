# pylint: disable=W0613
__artifacts_v2__ = {
    "get_mega_transfers": {
        "name": "mega_transfers",
        "description": "",
        "author": "",
        "creation_date": "2022-06-04",
        "last_update_date": "2022-06-04",
        "requirements": "none",
        "category": "Mega",
        "notes": "",
        "paths": ('*/mega.privacy.android.app/databases/megapreferences',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import base64
import binascii
import datetime
import sqlite3

from Crypto.Cipher import AES

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc

DIRECTION = {"0": "Download", "1": "Upload", "2": "Download"}
STATE = {
    "0": "None", "1": "Queued", "2": "Active", "3": "Paused", "4": "Retrying",
    "5": "Completing", "6": "Completed", "7": "Cancelled", "8": "Failed",
}


def _ms_to_utc(value):
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError):
        return ''


def decrypt(cell):
    cipher_text = base64.b64decode(cell)
    secret_key = "android_idfkvn8 w4y*(NC$G*(G($*GR*(#)*huio4h389$G"[0:32].encode('utf-8')
    algorithm = AES.new(secret_key, AES.MODE_ECB)
    plain_text = algorithm.decrypt(cipher_text).decode('utf-8')
    last_char = plain_text[-1]
    first_of_the_last_chars = plain_text.index(last_char)
    return plain_text[:first_of_the_last_chars]


@artifact_processor
def get_mega_transfers(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('megapreferences'):
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        try:
            cursor = db.cursor()
            cursor.execute('''
                SELECT transfertimestamp, transferpath, transferfilename, transfersize,
                       transfertype, transferstate, transferoriginalpath
                FROM completedtransfers
            ''')
            results = cursor.fetchall()
        except sqlite3.Error as exc:
            # megapreferences isn't always a valid sqlite db (encrypted/other format) --
            # skip it instead of aborting the whole artifact ("file is not a database")
            logfunc(f'Mega transfers: could not read {file_found}: {exc}')
            results = []
        finally:
            db.close()

        for r in results:
            try:
                decrypted = [decrypt(x) for x in r]
            except (binascii.Error, ValueError, TypeError, IndexError, UnicodeDecodeError) as exc:
                logfunc(f'Mega transfers: could not decrypt a row: {exc}')
                continue
            decrypted[0] = _ms_to_utc(decrypted[0])
            decrypted[4] = DIRECTION.get(decrypted[4], decrypted[4])
            decrypted[5] = STATE.get(decrypted[5], decrypted[5])
            data_list.append(decrypted)

    data_headers = (('Timestamp', 'datetime'), 'Mega Folder', 'Filename', 'Size', 'Direction', 'State', 'Transfer Path')
    return data_headers, data_list, source_path
