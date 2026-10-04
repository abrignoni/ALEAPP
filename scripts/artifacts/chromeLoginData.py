__artifacts_v2__ = {
    "get_chromeLoginData": {
        "name": "Login Data",
        "description": "Rows of the logins table of the Login Data database of Chromium based browsers, with the stored password value decrypted where it carries the v10 prefix and the result passes a padding and text check.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2020-03-20",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Chromium",
        "notes": (
            "Created Time is date_created read as microseconds since 1601-01-01 UTC, shown to the "
            "second. Chromium binds the column that way: "
            "https://github.com/chromium/chromium/blob/f944233df11d0ed7beaef976919b6df3bf95e23d/components/password_manager/core/browser/password_store/login_database.cc#L240 "
            "and https://github.com/chromium/chromium/blob/f944233df11d0ed7beaef976919b6df3bf95e23d/sql/statement.cc#L43 . "
            "A stored 0 is shown blank. The same file converts a database of schema version 8 or lower "
            "from seconds since 1970 (lines 823 to 833); this artifact does not handle such a database, "
            "and the tested databases were versions 29, 34 and 41. "
            "Password: at Chromium tag 120.0.6099.230 the build for Android uses os_crypt_posix.cc, which "
            "encrypts with AES-128-CBC under a key derived from a fixed text (PBKDF2, one iteration), "
            "an initialization vector of 16 spaces, and the prefix v10: "
            "https://github.com/chromium/chromium/blob/cd2ca78927de15f20169009a0799d02aa5120b4c/components/os_crypt/sync/os_crypt_posix.cc#L39-L55 "
            "and https://github.com/chromium/chromium/blob/cd2ca78927de15f20169009a0799d02aa5120b4c/components/os_crypt/sync/BUILD.gn#L40-L41 . "
            "Other Chromium versions and other browsers were not read. A v10 value is decrypted with that "
            "key and shown only when the PKCS#7 padding is valid and the result is UTF-8 text; a wrong key "
            "passes the padding test about once in 256 values, so the check lowers that risk and does not "
            "remove it. Password Status says what was done with each stored value: blank when "
            "password_value is empty, otherwise decrypted, not decrypted with the reason, or no v10 "
            "prefix with the number of stored bytes. A value without the v10 prefix is not shown; "
            "os_crypt_posix.cc reads such a value as clear text (lines 115 to 124). "
            "On the tested images 5 rows were reported (galaxys10_a10 1, pixel7a_a14 3, "
            "russell_pixel6a_a13 1): password_value was empty on 4 and a v10 value on 1, which passed "
            "both checks; date_created was 0 on 3 and a 1601 microsecond value on 2. The not decrypted "
            "and no prefix outcomes were exercised with constructed values only."
        ),
        "paths": ('*/app_chrome/Default/Login Data*', '*/app_sbrowser/Default/Login Data*', '*/app_opera/Login Data*', '*/app_webview/Default/Login Data*'),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 0 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "samsungs20_a13": "Android 13 | com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 0 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 1 row",
        },
    }
}

import datetime
import os
import sqlite3

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, artifact_processor
from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files


_EPOCH_1601 = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)


def decrypt(ciphertxt, key=b"peanuts"):
    '''Returns (password text, status) for a stored password_value.

    Only a value carrying the v10 prefix is decrypted, with the fixed key
    Chromium's os_crypt_posix.cc uses. The text is returned only when the
    PKCS#7 padding is valid and the result is UTF-8.'''
    if not ciphertxt:
        return '', ''
    if isinstance(ciphertxt, str):
        ciphertxt = ciphertxt.encode('utf-8', 'surrogateescape')
    if not ciphertxt.startswith(b'v10'):
        return '', f'No v10 prefix, not decrypted ({len(ciphertxt)} bytes stored)'
    ciphertxt = ciphertxt[3:]
    if len(ciphertxt) == 0 or len(ciphertxt) % 16 != 0:
        return '', 'Not decrypted: length is not a multiple of the AES block size'
    salt = b"saltysalt"
    derived_key = PBKDF2(key, salt, 0x10, 1)
    iv = b" "*0x10
    cipher = AES.new(derived_key, AES.MODE_CBC, IV=iv)
    plaintxt_pad = cipher.decrypt(ciphertxt)
    pad = plaintxt_pad[-1]
    if pad < 1 or pad > 16 or plaintxt_pad[-pad:] != bytes([pad]) * pad:
        return '', 'Not decrypted: padding not valid with the fixed key'
    try:
        plaintxt = plaintxt_pad[:-pad].decode('utf-8')
    except UnicodeDecodeError:
        return '', 'Not decrypted: result is not UTF-8 text'
    return plaintxt, 'Decrypted (v10, fixed key)'


def created_time(date_created):
    '''date_created as microseconds since 1601-01-01 UTC, to the second.'''
    if not isinstance(date_created, int) or date_created <= 0:
        return ''
    try:
        return _EPOCH_1601 + datetime.timedelta(seconds=date_created // 1000000)
    except OverflowError:
        return ''


@artifact_processor
def get_chromeLoginData(context):
    files_found = unique_files(context)
    all_data = []

    data_headers = ['Created Time', 'Username', 'Password', 'Password Status', 'Origin URL', 'Blacklisted by User']
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
        if db is None:
            continue

        # One unreadable database must not end the artifact: a Login Data file
        # left with a non-empty rollback journal cannot be read through a
        # read-only handle, because SQLite has to write to replay and clear it.
        try:
            cursor = db.cursor()
            cursor.execute('''
        SELECT
        username_value,
        password_value,
        date_created,
        origin_url,
        blacklisted_by_user
        FROM logins
        ''')
            all_rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} login data in {file_found}: {ex}')
            continue
        finally:
            db.close()

        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

            data_list = []
            for row in all_rows:
                password, password_status = decrypt(row[1])
                data_list.append((created_time(row[2]), row[0], password, password_status, row[3], row[4]))

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Login Data available')

    return all_data_headers, all_data, report_file
