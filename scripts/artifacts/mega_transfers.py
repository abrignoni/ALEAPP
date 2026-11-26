__artifacts_v2__ = {
    "get_mega_transfers": {
        "name": "mega_transfers",
        "description": "Parses MEGA transfer records (timestamp, folder, filename, size, direction and state) from the completedtransfers table of the MEGA megapreferences database.",
        "author": "@kibaffo33",
        "creation_date": "2022-06-04",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Cloud & Files",
        "notes": ""
                 "Each cell is AES decrypted with a fixed key written in this module. Direction "
                 "and State are labelled from the MEGA SDK's MegaTransfer constants "
                 "(https://github.com/meganz/sdk/blob/74326bb0aa09b13f0a1ec8eab9611e4c0de98cc6/include/megaapi.h#L6902-L6917): "
                 "type 0 is shown as Download, 1 as Upload and 2, the SDK's "
                 "TYPE_LOCAL_TCP_DOWNLOAD, as Local TCP Download, and State follows STATE_NONE 0 to "
                 "STATE_FAILED 8. Any other value is shown as decrypted. A row that does not "
                 "decrypt is logged and not reported. Timestamp is read as Unix milliseconds. "
                 "The three images named below returned 0 rows, so the decoding is code present "
                 "and unexercised on them. On hc_pixel8pro_a16, hc_pixel8pro_a17 and "
                 "pixel7a_a14 megapreferences does not start with the SQLite header, so it is "
                 "logged and not read. What format the file is in on those images is not "
                 "established.",
        "paths": ('*/mega.privacy.android.app/databases/megapreferences',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | mega.privacy.android.app vc 261630858 | 0 rows",
            "pixel7a_a14": "Android 14 | mega.privacy.android.app vc 241780257 | 0 rows",
        },
    }
}

import base64
import binascii
import datetime
import sqlite3

from Crypto.Cipher import AES

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc
from scripts.artifacts.storagePathViews import unique_files

SQLITE_HEADER = b'SQLite format 3\x00'

DIRECTION = {"0": "Download", "1": "Upload", "2": "Local TCP Download"}
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
def get_mega_transfers(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('megapreferences'):
            continue
        source_path = file_found
        shown = context.get_relative_path(file_found)
        try:
            with open(file_found, 'rb') as handle:
                header = handle.read(len(SQLITE_HEADER))
        except OSError as exc:
            logfunc(f'Mega transfers: could not open {shown}: {type(exc).__name__}')
            continue
        if header != SQLITE_HEADER:
            # Not SQLite at all, so there is nothing for a SQLite reader to report. Logged
            # in plain words, not as a database error, because no read was attempted.
            logfunc(f'Mega transfers: {shown} does not start with the SQLite header, so it was not read')
            continue
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
            # A file with the SQLite header that still fails to read is a real read error,
            # so it is logged with SQLite's own message.
            logfunc(f'Mega transfers: could not read {shown}: {exc}')
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
