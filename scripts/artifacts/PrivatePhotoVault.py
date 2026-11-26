__artifacts_v2__ = {
    "private_photo_vault_account": {
        "name": "Private Photo Vault - Account Usage",
        "description": "Install date and the key event count and last key event date the Private Photo Vault app keeps "
                       "in its main preferences file, with the two dates converted from Unix "
                       "milliseconds to UTC and the counts as stored.",
        "author": "@Gear-I & Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "On pixel7a_a14 this preferences file holds 15 entries and none is named as an "
                 "email, password or PIN field. On pixel3_a12 the file holds 11 entries, and four "
                 "are named aesEncryptedEmail, rsaEncryptedEmailKey, aesEncryptedPasscode and "
                 "rsaEncryptedPasscodeKey. This module does not read those four entries. "
                 "The module reads six named entries and does not "
                 "search the file for others. The six values are two dates, three numbers and "
                 "one flag. None is a user identity field. 'Key Event Count' and 'Last Key Event' come "
                 "from two preferences the app names keyEventCount and lastKeyEventDate. No "
                 "source for their meaning was found, so this module does not say what triggers "
                 "them. The count is reported as stored and the date is converted from Unix "
                 "milliseconds to UTC. On pixel7a_a14 (1 row), the one recorded event's timestamp "
                 "is within a second before the stored creation date of each of the three media "
                 "rows, which does not establish what the event is. 'Uses Encrypted Preferences' "
                 "is the app's own usesEncryptedPreferencesV2 flag, reported as stored; what the "
                 "app does when it is set is not established here. This module does not look for "
                 "a PIN.",
        "paths": ('*/com.enchantedcloud.photovault/shared_prefs/APP_PREFERENCES.xml',),
        "output_types": ["standard"],
        "artifact_icon": "info-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.enchantedcloud.photovault | 1 row",
        },
    },
    "private_photo_vault_albums": {
        "name": "Private Photo Vault - Albums",
        "description": "Albums recorded in Private Photo Vault's local database, each with its bucket identifier and creation time.",
        "author": "@Gear-I & Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Read from the app's own ppv.db, opened read-only alongside its write-ahead log (ppv.db-wal) so that any transaction committed to the log but not yet checkpointed into the main file is still included. On pixel7a_a14, two albums exist: one with bucket_id 'albums', which all three media rows (MIME type image/jpeg) point to, and one with bucket_id 'albums_decoy', whose creation_date is 7 milliseconds later, that no media row points to. This module reports the bucket_id exactly as stored rather than asserting what feature it belongs to. Creation Date (As Stored) is the creation_date text. Created is that text converted to UTC, and is filled only when the text carries a Z or a UTC offset; a value with neither is left blank in Created because no zone is recorded for it. Both stored values on pixel7a_a14 carry a UTC offset. A row whose creation_date is the schema's default, 2021-01-01T01:00:00.000Z, which both tables declare for the column, has a blank Created and the default in Creation Date (As Stored). No row on pixel7a_a14 holds it.",
        "paths": ('*/com.enchantedcloud.photovault/databases/ppv.db*',),
        "output_types": ["standard"],
        "artifact_icon": "album",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.enchantedcloud.photovault | 2 rows",
        },
    },
    "private_photo_vault_media": {
        "name": "Private Photo Vault - Media",
        "description": "Media file records in Private Photo Vault's local database (MediaFile table), with each row's stored creation date, image width and height, the view count as stored, Favourite and Deleted shown as Yes when the stored flag is non-zero, and the stored deletion, trash, favourite and upload dates.",
        "author": "@Gear-I & Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Read the same way as Private Photo Vault - Albums, including the write-ahead log. From ppv.db this module reads the Album and MediaFile tables, and the LoginRecord table in Private Photo Vault - Login Records. The Download, CircularLog and CachedPartAuthorization tables are not read. On pixel3_a12 (schema version 10) the database has only the first two. All four are empty on pixel7a_a14. On cookbook_a11 CircularLog holds 1 row, which this module does not report. The media content behind each row is not recovered by this module. On pixel7a_a14 the files at File Path and Thumbnail Path were not examined by this module. The database does store a per-file 'Encryption Key' and IV for each row. That stored value decodes from base64 to 48 bytes, which is not the length of a bare 32-byte AES key. This module does not look for a key that decrypts the files. The encryption_key and local_iv values are reported exactly as stored. How the 48 byte value relates to the key that encrypts the file is not established, and this module makes no attempt to decrypt the media itself. 'View Count' is reported as stored. 'Favourite' and 'Deleted' show Yes when the stored flag is non-zero and are blank otherwise. What updates them is not established. Creation Date (As Stored) is the creation_date text. Created is that text converted to UTC, and is filled only when the text carries a Z or a UTC offset; a value with neither is left blank in Created because no zone is recorded for it. All three stored values on pixel7a_a14 carry a UTC offset, two of them with a two digit fraction of a second. A row whose creation_date is the schema's default, 2021-01-01T01:00:00.000Z, which both tables declare for the column, has a blank Created and the default in Creation Date (As Stored). No row on pixel7a_a14 holds it. Image Width, Image Height and View Count are read where the MediaFile table has those columns and are blank where it does not. On pixel3_a12 (database schema version 10) the table has none of the three, and its 2 rows are reported with those columns blank. Deleted Time (as stored), Trashed Date (as stored), Favourite Date (as stored) and Uploaded Date (as stored) are the deleted_time, trashed_date, favourite_date and uploaded_date text columns, shown unchanged. Their format and what sets them are not established, and they are blank where the table has no such column. They held no value on any media row of pixel7a_a14, cookbook_a11 or pixel3_a12, so they are not exercised on real data.",
        "paths": ('*/com.enchantedcloud.photovault/databases/ppv.db*',),
        "output_types": ["standard", "timeline"],
        "artifact_icon": "photo",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.enchantedcloud.photovault | 3 rows",
        },
    },
    "private_photo_vault_login_records": {
        "name": "Private Photo Vault - Login Records",
        "description": "Rows of the LoginRecord table in Private Photo Vault's local database: each row's stored date, type, latitude, longitude and original file path.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Read from the LoginRecord table of ppv.db the same way as Private Photo Vault - Albums, including the write-ahead log. The table is declared with uid, orig_file_path, date, type, latitude and longitude columns. Date (as stored) is the date text. Date is that text converted to UTC, filled only when the text carries a Z or a UTC offset, as for the Created column of the other Private Photo Vault artifacts. Type (as stored), Original File Path (as stored), Latitude and Longitude are the stored values, unchanged. The app's source was not read, so what a row records, what the type values mean, what the file at the original path is and how the position was obtained are not established. A column the table lacks is blank. The table is present and empty on pixel7a_a14, cookbook_a11 and pixel3_a12, so this artifact is not exercised on real data.",
        "paths": ('*/com.enchantedcloud.photovault/databases/ppv.db*',),
        "output_types": ["standard", "timeline", "kml"],
        "artifact_icon": "lock",
    },
}

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, does_column_exist_in_db, does_table_exist_in_db, get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files


def _find_all(files_found, suffix):
    """Every file ending in suffix, sorted: an extraction can carry a copy per
    Android user, and each user's vault is separate evidence. ppv.db's
    write-ahead log/shared-memory sidecars are matched by the same glob (so
    ALEAPP extracts them alongside the main file, which SQLite needs in order
    to fold their content in), but the exact-suffix test never returns one."""
    return sorted(str(f) for f in files_found if str(f).endswith(suffix))


def _xml_pref(root, name):
    node = root.find(f".//*[@name='{name}']")
    if node is None:
        return None
    return node.get('value')


def _epoch_ms_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


_ISO_FRACTION = re.compile(r'\.(\d+)')


# Both tables declare creation_date TEXT NOT NULL DEFAULT this value. It is not shown as a Created time.
# When the app leaves the default in place is not established.
_SCHEMA_DEFAULT_DATE = '2021-01-01T01:00:00.000Z'


def _iso_to_utc(value):
    """The stored ISO 8601 text as a UTC datetime, or None when the text
    carries no Z or UTC offset (no instant can be stated for it) or cannot be
    parsed. The fraction is padded to six digits first: before Python 3.11,
    fromisoformat accepts only three or six."""
    if not value or not isinstance(value, str) or value.strip() == _SCHEMA_DEFAULT_DATE:
        return None
    text = _ISO_FRACTION.sub(
        lambda m: '.' + m.group(1)[:6].ljust(6, '0'), value.strip(), count=1)
    if text.endswith(('Z', 'z')):
        text = text[:-1] + '+00:00'
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


@artifact_processor
def private_photo_vault_account(context):
    data_headers = (
        ("Install Date", "datetime"), "Imported Media Count",
        "Minutes Spent In App", "Key Event Count",
        ("Last Key Event", "datetime"), "Uses Encrypted Preferences",
    )

    files_found = unique_files(context)
    prefs_paths = _find_all(files_found, 'APP_PREFERENCES.xml')
    if not prefs_paths:
        return data_headers, [], ""

    data_list = []
    for prefs_path in prefs_paths:
        try:
            root = ET.parse(prefs_path).getroot()
        except ET.ParseError as ex:
            logfunc(f"Private Photo Vault: could not parse {prefs_path}: {ex}")
            continue

        install_date = _epoch_ms_to_utc(_xml_pref(root, 'installDate'))
        imported_media = _xml_pref(root, 'importedMedia') or ''
        minutes_spent = _xml_pref(root, 'minutesSpentInApp') or ''
        key_event_count = _xml_pref(root, 'keyEventCount') or ''
        last_key_event = _epoch_ms_to_utc(_xml_pref(root, 'lastKeyEventDate'))
        uses_encrypted_prefs = _xml_pref(root, 'usesEncryptedPreferencesV2') or ''

        data_list.append((
            install_date, imported_media, minutes_spent, key_event_count,
            last_key_event, uses_encrypted_prefs,
        ))

    logfunc("Private Photo Vault Account: usage counters recovered.")
    return data_headers, data_list, '\n'.join(prefs_paths)


@artifact_processor
def private_photo_vault_albums(context):
    data_headers = (
        ("Created", "datetime"), "Creation Date (As Stored)",
        "Album Name", "Bucket ID", "Order Number", "Deleted",
    )

    files_found = unique_files(context)
    source_paths = _find_all(files_found, 'ppv.db')
    if not source_paths:
        return data_headers, [], ""

    data_list = []
    for name, bucket_id, created, order_number, is_deleted in (
            record for source_path in source_paths
            for record in get_sqlite_db_records(
                source_path,
                "SELECT name, bucket_id, creation_date, order_number, is_deleted "
                "FROM Album;")):
        data_list.append((
            _iso_to_utc(created),
            created,
            name,
            bucket_id,
            order_number,
            "Yes" if is_deleted else "",
        ))

    logfunc(f"Private Photo Vault Albums: {len(data_list)} album(s) recovered.")
    return data_headers, data_list, '\n'.join(source_paths)


_MEDIA_COLUMNS = ('creation_date', 'bucket_id', 'file_path', 'thumbnail_path', 'mime_type', 'image_width',
                  'image_height', 'is_favourite', 'is_deleted', 'view_count', 'encryption_key', 'local_iv',
                  'deleted_time', 'trashed_date', 'favourite_date', 'uploaded_date')


def _media_query(source_path):
    """The MediaFile query, with NULL in place of a column this schema version does not have, so its
    rows are still reported. An older schema has no image_width, image_height or view_count."""
    columns = ', '.join(c if does_column_exist_in_db(source_path, 'MediaFile', c) else f'NULL AS {c}'
                        for c in _MEDIA_COLUMNS)
    return f'SELECT {columns} FROM MediaFile ORDER BY creation_date;'


@artifact_processor
def private_photo_vault_media(context):
    data_headers = (
        ("Created", "datetime"), "Creation Date (As Stored)",
        "Album Bucket ID", "File Path",
        "Thumbnail Path", "MIME Type", "Image Width", "Image Height",
        "Favourite", "Deleted", "View Count", "Encryption Key", "IV",
        "Deleted Time (as stored)", "Trashed Date (as stored)", "Favourite Date (as stored)",
        "Uploaded Date (as stored)",
    )

    files_found = unique_files(context)
    source_paths = _find_all(files_found, 'ppv.db')
    if not source_paths:
        return data_headers, [], ""

    data_list = []
    for (created, bucket_id, file_path, thumbnail_path, mime_type, width,
         height, is_favourite, is_deleted, view_count, encryption_key,
         local_iv, deleted_time, trashed_date, favourite_date, uploaded_date) in (
            record for source_path in source_paths
            for record in get_sqlite_db_records(source_path, _media_query(source_path))):
        data_list.append((
            _iso_to_utc(created),
            created,
            bucket_id,
            file_path,
            thumbnail_path,
            mime_type,
            width,
            height,
            "Yes" if is_favourite else "",
            "Yes" if is_deleted else "",
            view_count,
            encryption_key,
            local_iv,
            deleted_time,
            trashed_date,
            favourite_date,
            uploaded_date,
        ))

    logfunc(f"Private Photo Vault Media: {len(data_list)} media record(s) "
            f"recovered.")
    return data_headers, data_list, '\n'.join(source_paths)


_LOGIN_COLUMNS = ('date', 'type', 'latitude', 'longitude', 'orig_file_path', 'uid')


@artifact_processor
def private_photo_vault_login_records(context):
    data_headers = (
        ("Date", "datetime"), "Date (as stored)", "Type (as stored)", ("Latitude", "latitude"),
        ("Longitude", "longitude"), "Original File Path (as stored)", "UID",
    )

    source_paths = _find_all(unique_files(context), 'ppv.db')
    data_list = []
    read_paths = []
    for source_path in source_paths:
        if not does_table_exist_in_db(source_path, 'LoginRecord'):
            continue
        read_paths.append(source_path)
        columns = ', '.join(c if does_column_exist_in_db(source_path, 'LoginRecord', c) else f'NULL AS {c}'
                            for c in _LOGIN_COLUMNS)
        for date, kind, latitude, longitude, orig_file_path, uid in get_sqlite_db_records(
                source_path, f'SELECT {columns} FROM LoginRecord ORDER BY date;'):
            data_list.append((_iso_to_utc(date), date, kind, latitude, longitude, orig_file_path, uid))

    logfunc(f"Private Photo Vault Login Records: {len(data_list)} record(s) recovered.")
    return data_headers, data_list, '\n'.join(read_paths)
