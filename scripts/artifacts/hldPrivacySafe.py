__artifacts_v2__ = {
    "hld_privacy_safe_files": {
        "name": "HLD Vault - Hidden Files",
        "description": "Rows from the FILE_INFO table of the vault's encrypted index, each "
                       "naming a file taken into the vault, the path it was taken from, the "
                       "name it was stored under and the times recorded for it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "sqlcipher3",
        "category": "Encrypting Media Apps",
        "notes": "The vault's index, .privacy_safe/db/privacy_safe.db, is a SQLCipher database "
                 "opened by the application through greenDAO. Its passphrase is the same fixed "
                 "string that decrypts the preferences and the stored media, the ASCII "
                 "Rny48Ni8aPjYCnUI. The SQLCipher parameter set differs by application version "
                 "and cannot be read from the file, so this artifact tries the version 4 "
                 "defaults first and then falls back to the version 3 set (page size 1024, "
                 "64000 KDF iterations, HMAC_SHA1, PBKDF2_HMAC_SHA1); on the corpora below two "
                 "images needed the version 3 set and one the version 4 defaults, and a "
                 "database opened with the wrong set fails outright rather than returning "
                 "wrong rows. Original Name and Original Path are where the file was taken "
                 "from, and Encrypted Name and Encrypted Path are what the application wrote "
                 "in its place; File Length matched the byte size of the stored file on every "
                 "row below. The stored file itself is not decrypted here, because the "
                 "existing App Locker artifact already decrypts .privacy_safe/picture and "
                 "video with this same key. Media is the THUMBNAIL column, a WebP image the "
                 "index stores unencrypted, so a preview is available from the index even "
                 "where the stored file is absent. Added To Vault and Original Created are "
                 "TEXT written in the device's local time with no zone recorded, so they are "
                 "reported exactly as stored and are not converted; on one image the value in "
                 "Original Created was five hours behind the UTC time embedded in the camera "
                 "file name of the same row, which is how the local reading was established. "
                 "Because they carry no zone this artifact emits no datetime column and its "
                 "rows do not reach the timeline. In Decoy Space is the IS_MOCK_SPACE column, "
                 "which the application sets for items held in the separate space its "
                 "MockSpace screens manage; it was 0 on every row below. Account held the "
                 "same short numeric value that the preferences store under number_password. "
                 "Type, Encrypt Type and Delete Time are reported as stored, no source for "
                 "their code lists having been located. The index holds eight further tables "
                 "which were present and empty on all three corpora below and so have no "
                 "artifact here: NOTE, BOOKMARK, HIDE_APP, LOCK_APP, INTRUDER_SHOOT, IMEI, "
                 "PAY_ORDER and SAMPLE. From Folder is the FROM_FOLDER_NAME column and was empty on "
                 "every row of all three corpora below; it is kept because the "
                 "application writes it when an item is moved between albums, which "
                 "none of the tested items had been.",
        "paths": ('*/.privacy_safe/db/privacy_safe.db*',),
        "output_types": "standard",
        "artifact_icon": "eye-off",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.hld.anzenbokusucal | 1 row",
            "pixel3_a12": "Android 12 | com.hld.anzenbokusucal | 1 row",
            "cookbook_a11": "Android 11 | com.hld.anzenbokusucal | 1 row",
        },
    },
    "hld_privacy_safe_albums": {
        "name": "HLD Vault - Albums",
        "description": "Rows from the SAFE_BOX table of the vault's encrypted index, one per "
                       "album the vault presents, with the number of items it holds and its "
                       "cover",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "sqlcipher3",
        "category": "Encrypting Media Apps",
        "notes": "SAFE_BOX is the album listing behind the vault's own screens, read from the "
                 "same SQLCipher index and with the same key and fallback as the Hidden Files "
                 "artifact. Four rows were present on each corpus below, named recycler_bin, "
                 "Pictures, Videos and Files, which are the albums the application creates "
                 "rather than folders on disk: a row's File Count is the application's own "
                 "tally and an item's album is not necessarily the directory its stored file "
                 "sits in. Cover is the THUMBNAIL column, a WebP image stored unencrypted in "
                 "the index, and Cover File Name names the item it was taken from. Sort Type, "
                 "Sort Index, Span Count, Cover Type and Rotate are reported as stored, no "
                 "source for their code lists having been located. In Decoy Space is the "
                 "IS_MOCK_SPACE column and was 0 on every row below. Account (as stored) held the "
                 "same value on all four rows of each corpus, being the account the "
                 "albums belong to rather than a per-album value, and Cover Always First "
                 "was likewise uniform at 1; both are kept because they are what "
                 "separates albums on a device carrying more than one account or "
                 "setting.",
        "paths": ('*/.privacy_safe/db/privacy_safe.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.hld.anzenbokusucal | 4 rows",
            "pixel3_a12": "Android 12 | com.hld.anzenbokusucal | 4 rows",
            "cookbook_a11": "Android 11 | com.hld.anzenbokusucal | 4 rows",
        },
    },
    "hld_privacy_safe_preferences": {
        "name": "HLD Vault - Preferences",
        "description": "Entries from the share_privacy_safe.xml preferences file of "
                       "com.hld.anzenbokusucal, with the name and the value of each entry "
                       "decrypted",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "com.hld.anzenbokusucal presents a working calculator and opens a storage area "
                 "when a stored value is entered. Its preferences file stores both halves of "
                 "every entry as hexadecimal ciphertext: the entry name and, for string entries, "
                 "the value. Both decrypt with AES in CBC mode using the key and initialisation "
                 "vector 526e7934384e693861506a59436e5549, which is the ASCII string "
                 "Rny48Ni8aPjYCnUI used as both the key and the initialisation vector. That "
                 "value is fixed rather than derived per device: the same key opens both "
                 "corpora below and is the one this repository's App Locker Pat artifact "
                 "has carried for the sibling package com.hld.anzenbokusufake since 2021. "
                 "It is not present as a literal string in base.vdex from the same "
                 "extraction, in ASCII or in either hex case, so the application assembles "
                 "it at run time or holds it in native code; where it comes from was not "
                 "established. Every name decrypted on both corpora below, 20 of 20 "
                 "13 of 13 and 19 of 19, each to a printable lower case identifier matching the type "
                 "of the value stored under it, which is what a correct key produces and a wrong "
                 "one does not. The names recovered include number_password, holding a short "
                 "numeric value; recovery_email, holding an email address; security_question, "
                 "holding a JSON object with a question and an answer; app_start_time and "
                 "app_used_times; and error_count, mock_space, init_safe_box and unlock. Those "
                 "are the application's own names for its entries, read out of the file; what "
                 "the app does with each one was not tested, and no claim is made here about "
                 "the effect of entering any stored value into the application. The same key "
                 "decrypts the name the App Locker Pat artifact matches on the sibling package "
                 "to gesture_password. Preference (as stored) and Value (as stored) carry the "
                 "hexadecimal forms so the decryption can be checked. Boolean, integer and long "
                 "entries store their values unencrypted, so Value repeats the stored value for "
                 "those and only the name is decrypted. Two long entries held values consistent "
                 "with Unix epoch milliseconds; which event each records is not established, so "
                 "no date conversion is applied. The vault's stored items are kept outside the "
                 "package directory, in a .privacy_safe folder on external storage. Items under "
                 "its picture and video folders are not read here, being decrypted by the "
                 "existing App Locker artifact using this same key, and the index under its db "
                 "folder is read by the Hidden Files and Albums artifacts in this module. "
                 "The package's other "
                 "shared_prefs files were read and are not parsed: on the corpora below they "
                 "belong to bundled advertising and analytics libraries (AppLovin, MoPub, "
                 "Vungle, Unity, Smaato, InMobi, ironSource, HyBid) and to Firebase, and "
                 "share_privacy_safe.xml was the only one holding values written by the app's "
                 "own storage feature.",
        "paths": ('*/com.hld.anzenbokusucal/shared_prefs/share_privacy_safe.xml',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.hld.anzenbokusucal | 19 rows",
            "pixel3_a12": "Android 12 | com.hld.anzenbokusucal | 20 rows",
            "cookbook_a11": "Android 11 | com.hld.anzenbokusucal | 13 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    get_sqlite_db_path,
    logfunc,
)

try:
    from sqlcipher3 import dbapi2 as sqlcipher
    _SQLCIPHER_AVAILABLE = True
except ImportError as _sqlcipher_import_error:
    # Guarded so a missing sqlcipher3 install disables only these two artifacts
    # rather than aborting the import of every ALEAPP artifact, the same pattern
    # threema.py already uses in this project.
    _SQLCIPHER_AVAILABLE = False
    logfunc(f'HLD Vault: sqlcipher3 not available, encrypted-index artifacts '
            f'disabled: {_sqlcipher_import_error}')

# Fixed key and initialisation vector, both the same value. Already used by this
# repository's appLockerfishingnetpat.py for the sibling package
# com.hld.anzenbokusufake, and confirmed here by every entry name and every string
# value on both tested corpora decrypting to correctly padded printable text.
VAULT_KEY = bytes.fromhex('526e7934384e693861506a59436e5549')

PREFERENCE_HEADERS = (
    'Preference',
    'Value',
    'Preference (as stored)',
    'Value (as stored)',
    'Stored Type',
)


def _decrypt(value):
    """Decrypt one hexadecimal preference name or value.

    Returns the decoded text, or '' when the value is not hexadecimal, is not a
    whole number of AES blocks, does not decrypt, or does not decode as text.
    Every one of those cases is logged rather than passed over silently, so a
    value the key does not open is visible in the run log instead of the column
    simply being short.
    """
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        logfunc('HLD Vault: preference field is not hexadecimal, reported as stored')
        return ''
    if not raw or len(raw) % AES.block_size:
        logfunc('HLD Vault: preference field is not a whole number of AES blocks, '
                'reported as stored')
        return ''
    try:
        plain = unpad(AES.new(VAULT_KEY, AES.MODE_CBC, VAULT_KEY).decrypt(raw), AES.block_size)
    except ValueError as error:
        logfunc(f'HLD Vault: preference field did not decrypt with the known key: {error}')
        return ''
    try:
        return plain.decode('utf-8')
    except UnicodeDecodeError:
        logfunc('HLD Vault: decrypted preference field did not decode as UTF-8')
        return ''


@artifact_processor
def hld_privacy_safe_preferences(context):
    data_list = []
    source_paths = []

    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        try:
            root = ET.parse(file_found).getroot()
        except (OSError, ET.ParseError) as error:
            logfunc(f'HLD Vault: could not parse {file_found}: {error}')
            continue

        source_paths.append(context.get_relative_path(file_found))
        for entry in root:
            stored_name = entry.get('name', '')
            name = _decrypt(stored_name) if stored_name else ''
            if entry.tag == 'string':
                stored_value = entry.text or ''
                # Only string entries are stored encrypted; the rest are in the clear.
                value = _decrypt(stored_value) if stored_value else ''
            else:
                stored_value = entry.get('value', '')
                value = stored_value
            data_list.append((name, value, stored_name, stored_value, entry.tag))

    data_list.sort(key=lambda row: row[0])
    return PREFERENCE_HEADERS, data_list, '\n'.join(source_paths)


# The application's SQLCipher parameters differ by version and cannot be read from
# the file, so each set is tried in turn. Version 4 defaults need no pragmas beyond
# the key; the version 3 set is the one older builds wrote. The key must be set
# before these, because SQLCipher defers deriving it until the first page is read.
_CIPHER_PARAMETER_SETS = (
    ('SQLCipher 4 defaults', ()),
    ('SQLCipher 3 parameters', (
        'PRAGMA cipher_page_size = 1024;',
        'PRAGMA kdf_iter = 64000;',
        'PRAGMA cipher_hmac_algorithm = HMAC_SHA1;',
        'PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;',
    )),
)

FILE_HEADERS = (
    'Added To Vault (as stored, device local)',
    'Original Created (as stored, device local)',
    ('Media', 'media'),
    'Original Name',
    'Original Path',
    'Album',
    'Encrypted Name',
    'Encrypted Path',
    'Size (as stored)',
    'File Length',
    'Image Size',
    'Suffix',
    'In Decoy Space',
    'Account (as stored)',
    'Type (as stored)',
    'Encrypt Type (as stored)',
    'Delete Time (as stored)',
    'From Folder',
)

ALBUM_HEADERS = (
    ('Cover', 'media'),
    'Album',
    'File Count',
    'Cover File Name',
    'Cover Suffix',
    'In Decoy Space',
    'Account (as stored)',
    'Cover Always First',
    'Span Count',
    'Sort Type (as stored)',
    'Sort Index (as stored)',
    'Cover Type (as stored)',
    'Rotate (as stored)',
)


def _open_index(db_path):
    """Open the vault index, trying each known SQLCipher parameter set.

    A wrong parameter set fails outright rather than returning wrong rows, because
    SQLCipher checks the HMAC of every page it decrypts, so trying them in turn
    cannot silently pick the wrong one.
    """
    for label, pragmas in _CIPHER_PARAMETER_SETS:
        connection = None
        try:
            connection = sqlcipher.connect(  # pylint: disable=no-member
                f'file:{get_sqlite_db_path(db_path)}?mode=ro', uri=True)
            cursor = connection.cursor()
            cursor.execute(f"PRAGMA key = '{VAULT_KEY.decode()}';")
            for pragma in pragmas:
                cursor.execute(pragma)
            cursor.execute('SELECT count(*) FROM sqlite_master;').fetchone()
            return connection
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'HLD Vault: {os.path.basename(db_path)} did not open with '
                    f'{label}: {error}')
            if connection is not None:
                try:
                    connection.close()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
    return None


def _index_files(context):
    """The privacy_safe.db files, storage views collapsed and sidecars dropped.

    unique_files collapses the duplicate app data directory spellings, but the
    vault index lives on external storage, which it does not cover: an extraction
    can carry the same file under both a media path and a pass-through mount path,
    and reading both reports every row twice. Those are collapsed here on the path
    from .privacy_safe onward, which is the same location reached by two names. A
    pair whose sizes disagree is kept rather than silently reduced to one.
    """
    found = []
    seen = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if os.path.basename(file_found) != 'privacy_safe.db':
            continue
        relative = context.get_relative_path(file_found).replace('\\', '/')
        marker = relative.split('.privacy_safe/', 1)
        key = marker[1] if len(marker) == 2 else relative
        try:
            size = os.path.getsize(file_found)
        except OSError as error:
            logfunc(f'HLD Vault: could not size {file_found}: {error}')
            continue
        if seen.get(key) == size:
            logfunc(f'HLD Vault: skipping a duplicate external storage spelling of '
                    f'.privacy_safe/{key}')
            continue
        seen.setdefault(key, size)
        found.append(file_found)
    return found


def _rows(context, query):
    """(rows, source paths) from every vault index the seeker returned."""
    data_rows, source_paths = [], []
    if not _SQLCIPHER_AVAILABLE:
        return data_rows, source_paths
    for db_path in _index_files(context):
        connection = _open_index(db_path)
        if connection is None:
            continue
        try:
            rows = connection.cursor().execute(query).fetchall()
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'HLD Vault: query failed on {db_path}: {error}')
            rows = []
        finally:
            connection.close()
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            data_rows.append((row, db_path))
    return data_rows, source_paths


@artifact_processor
def hld_privacy_safe_files(context):
    data_list = []
    rows, source_paths = _rows(context, """
        SELECT ADD_TIME, CREATE_TIME, THUMBNAIL, ORIGIN_NAME, ORIGIN_PATH, FOLDER_NAME,
               ENCRYPT_NAME, ENCRYPT_PATH, SIZE, FILE_LENGTH, IMAGE_SIZE, SUFFIX,
               IS_MOCK_SPACE, ACCOUNT, TYPE, ENCRYPT_TYPE, DELETE_TIME, FROM_FOLDER_NAME
        FROM FILE_INFO ORDER BY ADD_TIME
    """)
    for row, db_path in rows:
        (added, created, thumbnail, origin_name, origin_path, album, encrypt_name,
         encrypt_path, size, length, image_size, suffix, mock, account, kind,
         encrypt_type, delete_time, from_folder) = row
        media = ''
        if thumbnail:
            media = check_in_embedded_media(
                db_path, bytes(thumbnail), f'{origin_name or encrypt_name} thumbnail',
                force_type='image/webp', force_extension='webp')
        data_list.append((
            added or '', created or '', media, origin_name or '', origin_path or '',
            album or '', encrypt_name or '', encrypt_path or '', size or '',
            length if length is not None else '', image_size or '', suffix or '',
            mock if mock is not None else '', account or '',
            kind if kind is not None else '',
            encrypt_type if encrypt_type is not None else '',
            delete_time if delete_time is not None else '', from_folder or '',
        ))
    return FILE_HEADERS, data_list, '\n'.join(source_paths)


@artifact_processor
def hld_privacy_safe_albums(context):
    data_list = []
    rows, source_paths = _rows(context, """
        SELECT THUMBNAIL, FOLDER_NAME, FILE_COUNT, COVER_FILE_NAME, COVER_SUFFIX,
               IS_MOCK_SPACE, ACCOUNT, IS_COVER_ALWAYS_FIRST, SPAN_COUNT, SORT_TYPE,
               SORT_INDEX, COVER_TYPE, ROTATE
        FROM SAFE_BOX ORDER BY SORT_INDEX
    """)
    for row, db_path in rows:
        (thumbnail, album, count, cover_name, cover_suffix, mock, account,
         cover_first, span, sort_type, sort_index, cover_type, rotate) = row
        media = ''
        if thumbnail:
            media = check_in_embedded_media(
                db_path, bytes(thumbnail), f'{album or "album"} cover',
                force_type='image/webp', force_extension='webp')
        data_list.append((
            media, album or '', count if count is not None else '', cover_name or '',
            cover_suffix or '', mock if mock is not None else '', account or '',
            cover_first if cover_first is not None else '',
            span if span is not None else '',
            sort_type if sort_type is not None else '',
            sort_index if sort_index is not None else '',
            cover_type if cover_type is not None else '',
            rotate if rotate is not None else '',
        ))
    return ALBUM_HEADERS, data_list, '\n'.join(source_paths)
