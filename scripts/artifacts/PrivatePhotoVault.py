__artifacts_v2__ = {
    "private_photo_vault_account": {
        "name": "Private Photo Vault - Account Usage",
        "description": "Install date and the key event count and last key event date the Private Photo Vault app keeps "
                       "in its main preferences file, reported as stored.",
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Private Photo Vault",
        "notes": "Private Photo Vault has no email/password account; these are "
                 "app-level counters the app itself maintains, not a user "
                 "identity. 'Key Event Count' and 'Last Key Event' come from a "
                 "preference the app calls lastKeyEventDate/keyEventCount; its "
                 "exact meaning is not documented publicly, so this module "
                 "reports the raw value rather than asserting what triggers it. "
                 "On the device this was validated against, its one recorded "
                 "event's timestamp lands within a second of every imported "
                 "media file's own creation timestamp, consistent with (but not "
                 "proof of) the single PIN-setup/import session documented for "
                 "this app on this device. 'Uses Encrypted Preferences' reflects "
                 "the app's own usesEncryptedPreferencesV2 flag; when true, it "
                 "confirms the app is using Android's Keystore-backed "
                 "EncryptedSharedPreferences for its sensitive settings, which "
                 "explains why a PIN, if one was set, is not recoverable from "
                 "this file even though the file itself is plaintext XML - the "
                 "values inside it are encrypted with a hardware-backed key "
                 "that does not leave the device.",
        "paths": ('*/com.enchantedcloud.photovault/shared_prefs/APP_PREFERENCES.xml',),
        "output_types": ["standard"],
        "artifact_icon": "info-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.enchantedcloud.photovault | 1 row",
        },
    },
    "private_photo_vault_albums": {
        "name": "Private Photo Vault - Albums",
        "description": "Albums recorded in Private Photo Vault's local database, "
                       "each with its own bucket identifier and creation time.",
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Private Photo Vault",
        "notes": "Read from the app's own ppv.db, opened read-only alongside "
                 "its write-ahead log (ppv.db-wal) so that any transaction "
                 "committed to the log but not yet checkpointed into the main "
                 "file is still included. On the device this was validated "
                 "against, two albums exist: one with bucket_id 'albums' "
                 "holding the device's three imported pictures, and one, "
                 "created one millisecond later at the same PIN-setup moment, "
                 "with bucket_id 'albums_decoy' and no media in it. This "
                 "module reports the bucket_id exactly as stored rather than "
                 "asserting what feature it belongs to, but the literal string "
                 "'decoy' in an otherwise-empty, simultaneously-created second "
                 "album is worth an examiner's attention.",
        "paths": ('*/com.enchantedcloud.photovault/databases/ppv.db*',),
        "output_types": ["standard"],
        "artifact_icon": "album",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.enchantedcloud.photovault | 2 rows",
        },
    },
    "private_photo_vault_media": {
        "name": "Private Photo Vault - Media",
        "description": "Imported media files recorded in Private Photo Vault's "
                       "local database, with each file's original dimensions, "
                       "import time, and favourite/deleted/view-count state.",
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Private Photo Vault",
        "notes": "Read the same way as Private Photo Vault - Albums, including "
                 "the write-ahead log. The image/video content behind each row "
                 "is not recoverable from this extraction: the app encrypts "
                 "every imported file on disk (confirmed - the files at File "
                 "Path and Thumbnail Path do not begin with any recognizable "
                 "image file signature), and while the database does store a "
                 "per-file 'Encryption Key' and IV for each row, that stored "
                 "key is itself an encrypted value (48 bytes once "
                 "base64-decoded, not a bare 32-byte AES key) - consistent with "
                 "Private Photo Vault - Account Usage's finding that this app "
                 "uses Android Keystore-backed encrypted storage, whose "
                 "unwrapping key is hardware-bound and does not leave the "
                 "device. The wrapped key and IV are still reported here "
                 "exactly as stored, in case a future extraction method "
                 "recovers the missing unwrapping key, but this module makes "
                 "no attempt to decrypt the media itself. 'View Count' and "
                 "'Favourite'/'Deleted' reflect the app's own tracked state "
                 "for each file, not necessarily anything documented in an "
                 "action sheet.",
        "paths": ('*/com.enchantedcloud.photovault/databases/ppv.db*',),
        "output_types": ["standard", "timeline"],
        "artifact_icon": "photo",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.enchantedcloud.photovault | 3 rows",
        },
    },
}

import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc
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


def _iso_to_utc(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


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
        "Album Name", "Bucket ID", ("Created", "datetime"), "Order Number",
        "Deleted",
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
            name,
            bucket_id,
            _iso_to_utc(created),
            order_number,
            "Yes" if is_deleted else "",
        ))

    logfunc(f"Private Photo Vault Albums: {len(data_list)} album(s) recovered.")
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def private_photo_vault_media(context):
    data_headers = (
        ("Created", "datetime"), "Album Bucket ID", "File Path",
        "Thumbnail Path", "MIME Type", "Image Width", "Image Height",
        "Favourite", "Deleted", "View Count", "Encryption Key (Wrapped)", "IV",
    )

    files_found = unique_files(context)
    source_paths = _find_all(files_found, 'ppv.db')
    if not source_paths:
        return data_headers, [], ""

    data_list = []
    for (created, bucket_id, file_path, thumbnail_path, mime_type, width,
         height, is_favourite, is_deleted, view_count, encryption_key,
         local_iv) in (
            record for source_path in source_paths
            for record in get_sqlite_db_records(
                source_path,
                "SELECT creation_date, bucket_id, file_path, thumbnail_path, "
                "mime_type, image_width, image_height, is_favourite, is_deleted, "
                "view_count, encryption_key, local_iv FROM MediaFile "
                "ORDER BY creation_date;")):
        data_list.append((
            _iso_to_utc(created),
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
        ))

    logfunc(f"Private Photo Vault Media: {len(data_list)} media record(s) "
            f"recovered.")
    return data_headers, data_list, '\n'.join(source_paths)