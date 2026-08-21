__artifacts_v2__ = {
    "galleryvault_vault_files": {
        "name": "GalleryVault - Vault Files",
        "description": "Recovers files hidden by GalleryVault from the encrypted objects stored "
                       "under the vault folder on external storage, together with the original "
                       "file name and creation time held in each object's own trailer",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "Each vault object is a 2803-byte decoy PNG, followed by the tail of the original "
                 "file, followed by a trailer bounded by the markers >>tyfs>> and <<tyfs<<. The "
                 "trailer holds the relocated first 2803 bytes of the original, the original size, "
                 "a DES-ECB wrapped XOR key and a DES-ECB wrapped JSON block naming the file. Both "
                 "DES blocks use the hard-coded key 'tianxiaw' documented by S-RM in 'Cracking the "
                 "Vault: Exposing the weaknesses of encrypted apps'; the relocated block is "
                 "recovered with keystream[i] = xor_key[i % 4] XOR (i AND 0xFF), which was derived "
                 "and confirmed against the corpora below. Recovery is reported per object and a "
                 "row is produced even when an object cannot be rebuilt.",
        "paths": ('*/.galleryvault_*/files/*/*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 27 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 2 rows",
        },
    },
    "galleryvault_hidden_files": {
        "name": "GalleryVault - Hidden Files (database)",
        "description": "Files hidden in GalleryVault as recorded in the file_v1 table, including "
                       "the path each file was taken from",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "The file_v1 table can be empty while encrypted objects remain on external "
                 "storage; compare against the GalleryVault - Vault Files artifact.",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "eye-off",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 2 rows",
        },
    },
    "galleryvault_folders": {
        "name": "GalleryVault - Folders",
        "description": "GalleryVault folders, their child counts and creation times",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "The folder type labels come from the names the app gives its own default "
                 "folders in this table; a type of 0 is used by folders the user creates.",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 15 rows",
        },
    },
    "galleryvault_break_in_reports": {
        "name": "GalleryVault - Break-in Reports",
        "description": "Failed unlock attempts recorded by GalleryVault, with the code that was "
                       "entered and the photo captured at the time",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "user-x",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 0 rows",
        },
    },
    "galleryvault_break_in_images": {
        "name": "GalleryVault - Break-in Report Images",
        "description": "Images written to the BreakInReports folder on external storage, with the "
                       "capture time taken from the file name",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "File names follow PS_YYYYMMDD_HHMMSS. The app writes these files in device local "
                 "time, so the reported value is labelled as local rather than UTC. These images "
                 "survive on external storage after the database rows are gone.",
        "paths": ('*/.galleryvault_*/BreakInReports/*',),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 4 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | no vault folder present",
        },
    },
    "galleryvault_locked_apps": {
        "name": "GalleryVault - Locked Apps",
        "description": "Applications locked by the GalleryVault AppLock feature",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "",
        "paths": ('*/com.thinkyeah.galleryvault/databases/AppLock.db*',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | AppLock.db not present",
        },
    },
    "galleryvault_applock_break_ins": {
        "name": "GalleryVault - AppLock Break-in Reports",
        "description": "Failed unlock attempts recorded against individual locked applications",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "",
        "paths": ('*/com.thinkyeah.galleryvault/databases/AppLock.db*',),
        "output_types": "standard",
        "artifact_icon": "user-x",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | AppLock.db not present",
        },
    },
    "galleryvault_browser_history": {
        "name": "GalleryVault - Browser History",
        "description": "Entries in the browser_history table of the browser built into "
                       "GalleryVault, with the URL, host, title and last visit time the app "
                       "recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 0 rows",
        },
    },
    "galleryvault_browser_urls": {
        "name": "GalleryVault - Browser Start Pages",
        "description": "Entries in the web_url table used by the built-in browser start page",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "The app ships with preset entries; a visit count of zero and empty timestamps "
                 "indicate a preset that was not opened on the device.",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 8 rows",
        },
    },
    "galleryvault_downloads": {
        "name": "GalleryVault - Downloads",
        "description": "Download tasks created by the browser built into GalleryVault",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 0 rows",
        },
    },
    "galleryvault_unhide_history": {
        "name": "GalleryVault - Unhide and Export History",
        "description": "Records of files taken back out of the vault, including the path they were "
                       "written to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "The export_unhidden_history table is absent from older schema versions.",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "upload",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | table absent",
        },
    },
    "galleryvault_recycle_bin": {
        "name": "GalleryVault - Recycle Bin",
        "description": "Vault files sitting in the GalleryVault recycle bin and when they were "
                       "deleted",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "",
        "paths": ('*/com.thinkyeah.galleryvault/databases/galleryvault.db*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 0 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 0 rows",
        },
    },
    "galleryvault_file_actions": {
        "name": "GalleryVault - File Action Log",
        "description": "Action log kept next to the vault on external storage, recording vault "
                       "file paths and the time each action was carried out",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "This log lives outside the app sandbox and can outlive the application database.",
        "paths": ('*/.galleryvault_*/backup/file_action_log.db*',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.thinkyeah.galleryvault vc 406018 | 3 rows",
            "pixel7a_a14": "Android 14 | com.thinkyeah.galleryvault vc 40309 | 2 rows",
        },
    },
    "galleryvault_preferences": {
        "name": "GalleryVault - Preferences",
        "description": (
            "Parses GalleryVault account, vault storage and lock-related "
            "preferences from Kidd.xml."
        ),
        "author": "@segumarc",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": (
            "Every row reports the interpreted preference label together with the "
            "original shared_prefs key so the value can be verified directly against "
            "Kidd.xml. LockPin components are presented as SHA1 and MD5. "
            "GalleryVault supports launcher icon disguise, including a calculator "
            "disguise. Last Android ID is the value used elsewhere in this parser "
            "to derive the DES key for AccountProfile.xml. Cloud Storage Type should "
            "be cross-referenced against galleryvault_cloud_account when cloud_cache.db "
            "is present."
        ),
        "paths": (
            '*/com.thinkyeah.galleryvault/shared_prefs/Kidd.xml*',
        ),
        "output_types": "standard",
        "artifact_icon": "key",
    },
    "galleryvault_account_profile": {
        "name": "GalleryVault - Account Profile",
        "description": (
            "Decrypts GalleryVault account profile information stored in "
            "AccountProfile.xml using the Android ID recorded in Kidd.xml."
        ),
        "author": "@segumarc",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-13",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": (
            "GalleryVault encrypts account profile values using DES. "
            "The account profile is decrypted using key material derived "
            "from the Android ID recorded in Kidd.xml. The decrypted "
            "AccountInfo structure may contain an account authentication token."
        ),
        "paths": (
            '*/com.thinkyeah.galleryvault/shared_prefs/AccountProfile.xml*',
            '*/com.thinkyeah.galleryvault/shared_prefs/Kidd.xml*',
        ),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "galleryvault_cloud_account": {
        "name": "GalleryVault - Cloud Account",
        "description": (
            "Cloud backup account bound to the vault, including provider, account "
            "identifier, drive status and monthly usage/quota."
        ),
        "author": "@segumarc",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": (
            "drive_account_id is the cloud account (e.g. a Google account email) that "
            "GalleryVault is syncing hidden vault content to, independent of the device "
            "owner's own accounts. This ties hidden content to an off-device destination."
        ),
        "paths": ('*/com.thinkyeah.galleryvault/databases/cloud_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
    },
    "galleryvault_cloud_folders": {
        "name": "GalleryVault - Cloud Folders",
        "description": "Folder tree of the cloud backup copy of the vault, with resolved parent paths",
        "author": "@segumarc",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": "Mirrors the local vault folder structure as it exists in the cloud copy.",
        "paths": ('*/com.thinkyeah.galleryvault/databases/cloud_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
    },
    "galleryvault_cloud_files": {
        "name": "GalleryVault - Cloud Files",
        "description": (
            "Files present in the cloud backup copy of the vault, with resolved folder "
            "path, size, mime type and the per-file encryption key held in the cache"
        ),
        "author": "@segumarc",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": (
            "file_encryption_key is the key GalleryVault used to encrypt this file's "
            "content before upload; it is not the DES key used elsewhere in this parser. "
            "It is presented here so it is available if the corresponding cloud object "
            "is later obtained through legal process against the cloud provider."
        ),
        "paths": ('*/com.thinkyeah.galleryvault/databases/cloud_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
    },
    "galleryvault_cloud_change_history": {
        "name": "GalleryVault - Cloud Change History",
        "description": (
            "Change history of cloud entries, resolved back to file or folder names "
            "where the entry still exists"
        ),
        "author": "@segumarc",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": (
            "Change Action Value is presented as the raw numeric code recorded by the "
            "app; the mapping to add/modify/delete has not been confirmed against a "
            "large enough corpus to label with confidence. This log can outlive the "
            "file or folder row it refers to, so Entry Name may be blank for entries "
            "later removed from cloud_files/cloud_folders."
        ),
        "paths": ('*/com.thinkyeah.galleryvault/databases/cloud_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "list",
    },
    "galleryvault_cloud_upload_tasks": {
        "name": "GalleryVault - Cloud Upload Tasks",
        "description": (
            "Sync tasks queued to upload vault files to the cloud, including partial "
            "and failed transfers, joined to their raw-file/thumbnail parts"
        ),
        "author": "@segumarc",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "GalleryVault",
        "notes": (
            "A row here shows a sync was attempted even when it never completed "
            "(Task State/Task Error Code non-zero and bytes uploaded less than bytes "
            "total), which is evidence distinct from a finished upload in "
            "galleryvault_cloud_files."
        ),
        "paths": ('*/com.thinkyeah.galleryvault/databases/cloud_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "upload-cloud",
    },
}

import json
import mimetypes
import os
import re
import struct
import xml.etree.ElementTree as ET

from Crypto.Cipher import DES

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    check_in_media,
    convert_unix_ts_to_utc,
    get_file_path,
    get_sqlite_db_records,
    logfunc,
)

# Hard-coded DES key used by GalleryVault, documented by S-RM in "Cracking the Vault:
# Exposing the weaknesses of encrypted apps".
DES_KEY = b'tianxiaw'
START_MARKER = b'>>tyfs>>'
END_MARKER = b'<<tyfs<<'

# Labels taken from the names the app gives its own default folders in folder_v1.
FOLDER_TYPES = {
    -1: 'Recycle Bin',
    0: 'User created',
    1: 'From Share',
    2: 'From Download',
    3: 'From Camera',
    4: 'From Restore',
}

BREAK_IN_NAME = re.compile(r'PS_(\d{8})_(\d{6})')

# entry_type values in entry_change_history, confirmed against cloud_folders/cloud_files uuids.
CLOUD_ENTRY_TYPES = {
    1: 'Folder',
    2: 'File',
}


def _unpad(data):
    """Strip PKCS#5 padding when the trailing byte describes a valid pad length."""
    if data and 1 <= data[-1] <= 8 and data[-data[-1]:] == bytes([data[-1]]) * data[-1]:
        return data[:-data[-1]]
    return data


def _des_decrypt(data):
    if not data or len(data) % 8:
        return b''
    return DES.new(DES_KEY, DES.MODE_ECB).decrypt(data)


def _parse_vault_object(raw):
    """Split a GalleryVault object into its trailer fields.

    Layout confirmed against the corpora listed in sample_data:
        [decoy PNG of block_len bytes][original[block_len:]]
        >>tyfs>>
        [relocated first bytes, XOR encrypted]
        [8 bytes big endian: block_len][8 bytes big endian: original size]
        [1 byte: check][wrapped XOR key][8 bytes big endian: wrapped key length]
        [wrapped JSON metadata][8 bytes big endian: JSON length][2 bytes: version]
        <<tyfs<<
    """
    start = raw.find(START_MARKER)
    end = raw.rfind(END_MARKER)
    if start < 0 or end < 0 or end < start:
        return None

    tail = raw[start + len(START_MARKER):end]
    if len(tail) < 10:
        return None
    json_len = struct.unpack('>Q', raw[end - 10:end - 2])[0]
    version = raw[end - 2:end]
    fields_end = len(tail) - (json_len + 10)
    if fields_end < 25:
        return None

    key_len = struct.unpack('>Q', tail[fields_end - 8:fields_end])[0]
    block_start = fields_end - 25 - key_len
    if block_start < 0 or key_len > len(tail):
        return None

    wrapped_key = tail[fields_end - 8 - key_len:fields_end - 8]
    check_byte = tail[fields_end - 9 - key_len]
    original_size = struct.unpack('>Q', tail[fields_end - 17 - key_len:fields_end - 9 - key_len])[0]
    block_len = struct.unpack('>Q', tail[fields_end - 25 - key_len:fields_end - 17 - key_len])[0]

    metadata = {}
    decrypted = _unpad(_des_decrypt(tail[-(json_len + 10):-10]))
    if decrypted:
        try:
            metadata = json.loads(decrypted.decode('utf-8', 'replace'))
        except ValueError:
            metadata = {}

    return {
        'marker_offset': start,
        'encrypted_block': tail[:block_start],
        'wrapped_key': wrapped_key,
        'check_byte': check_byte,
        'original_size': original_size,
        'block_len': block_len,
        'version': version.hex(),
        'metadata': metadata,
    }


def _recover_vault_file(raw, parsed):
    """Rebuild the original bytes of a vault object, or return None."""
    xor_key = _unpad(_des_decrypt(parsed['wrapped_key']))
    if not xor_key:
        return None
    block = parsed['encrypted_block']
    head = bytes(block[i] ^ xor_key[i % len(xor_key)] ^ (i & 0xFF) for i in range(len(block)))
    recovered = head + raw[parsed['block_len']:parsed['marker_offset']]
    return recovered[:parsed['original_size']]


def _sniff(data, name=''):
    """Return (label, mime, extension) for recovered bytes, falling back to the file name."""
    if data[:3] == b'\xff\xd8\xff':
        return 'JPEG', 'image/jpeg', 'jpg'
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'PNG', 'image/png', 'png'
    if data[:4] in (b'GIF8',) or data[:6] in (b'GIF87a', b'GIF89a'):
        return 'GIF', 'image/gif', 'gif'
    if data[4:8] == b'ftyp':
        return 'MP4', 'video/mp4', 'mp4'
    if data[:4] == b'RIFF':
        return 'RIFF', 'video/x-msvideo', 'avi'
    if data[:4] == b'%PDF':
        return 'PDF', 'application/pdf', 'pdf'
    guessed_type, _ = mimetypes.guess_type(name) if name else (None, None)
    if guessed_type:
        return 'By file name', guessed_type, os.path.splitext(name)[1].lstrip('.') or None
    return 'Unknown', None, None


def _table_exists(db_path, table):
    # get_sqlite_db_records returns a cursor, so the rows have to be pulled out of it.
    rows = list(get_sqlite_db_records(
        db_path, f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
    return len(rows) > 0


def _columns(db_path, table):
    return {row[0] for row in get_sqlite_db_records(
        db_path, f"SELECT name FROM pragma_table_info('{table}')")}


def _query(db_path, table, query):
    """Run a query only when its table is present, so older schemas stay quiet."""
    if not db_path or not _table_exists(db_path, table):
        return []
    return get_sqlite_db_records(db_path, query)


def _ms(value):
    """GalleryVault stores epoch milliseconds; empty and zero values stay blank."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return convert_unix_ts_to_utc(value)


def _galleryvault_db(files_found):
    return get_file_path(files_found, 'galleryvault.db')


def _cloud_cache_db(files_found):
    return get_file_path(files_found, 'cloud_cache.db')


def _cloud_folder_map(db_path):
    """Return {entry_id: (name, parent_folder_id)} for every row in cloud_folders."""
    folder_map = {}
    for record in _query(
            db_path, 'cloud_folders',
            'SELECT entry_id, name, parent_folder_id FROM cloud_folders'):
        folder_map[record[0]] = (record[1] or '', record[2])
    return folder_map


def _cloud_folder_path(folder_id, folder_map, path_cache):
    """Resolve a cloud_folders entry_id to a '/'-joined path below the drive root.

    parent_folder_id 0 marks the drive root itself, which is not included in the
    returned path, so a top-level folder's path is just its own name.
    """
    if folder_id in path_cache:
        return path_cache[folder_id]
    if folder_id not in folder_map or not folder_map[folder_id][1]:
        path_cache[folder_id] = ''
        return ''

    name, parent_id = folder_map[folder_id]
    parent_path = _cloud_folder_path(parent_id, folder_map, path_cache)
    path = f'{parent_path}/{name}' if parent_path else name
    path_cache[folder_id] = path
    return path


def _get_xml_value(root, name):
    for elem in root:
        if elem.attrib.get('name') != name:
            continue

        if elem.tag == 'string':
            return elem.text or ''

        return elem.attrib.get('value', '')

    return ''


def _galleryvault_des_decrypt(value, key):
    if not value or not key:
        return ''

    try:
        encrypted = bytes.fromhex(value)

        if len(encrypted) % 8:
            return ''

        decrypted = DES.new(
            key.encode('utf-8'),
            DES.MODE_ECB,
        ).decrypt(encrypted)

        return _unpad(decrypted).decode('utf-8', 'replace')

    except (ValueError, UnicodeDecodeError) as error:
        logfunc(
            f'GalleryVault: could not decrypt account value: {error}'
        )
        return ''

@artifact_processor
def galleryvault_vault_files(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        source_path = os.path.dirname(file_found)
        try:
            with open(file_found, 'rb') as vault_object:
                raw = vault_object.read()
        except OSError as error:
            logfunc(f'GalleryVault: could not read {file_found}: {error}')
            continue

        parsed = _parse_vault_object(raw)
        uuid = os.path.basename(file_found)
        is_thumbnail = uuid.endswith('_t')
        if parsed is None:
            data_list.append(('', '', '', 'Not a GalleryVault object', '', '', '', '',
                              uuid, context.get_relative_path(file_found), ''))
            continue

        metadata = parsed['metadata']
        recovered = _recover_vault_file(raw, parsed)
        media = ''
        kind = ''
        status = 'Not recovered'
        if recovered:
            kind, mime, extension = _sniff(recovered, metadata.get('name', ''))
            if len(recovered) == parsed['original_size']:
                status = 'Recovered'
            else:
                status = f'Recovered {len(recovered)} of {parsed["original_size"]} bytes'
            name = metadata.get('name') or f'{uuid}.{extension or "bin"}'
            if mime:
                media = check_in_embedded_media(file_found, recovered, name,
                                                force_type=mime, force_extension=extension) or ''

        data_list.append((
            _ms(metadata.get('create_time_utc')),
            metadata.get('name', ''),
            media,
            status,
            kind,
            'Thumbnail' if is_thumbnail else 'File',
            parsed['original_size'],
            metadata.get('email', ''),
            metadata.get('uuid', ''),
            context.get_relative_path(file_found),
            parsed['version'],
        ))

    data_headers = (
        ('Create Time', 'datetime'),
        'Original File Name',
        ('Recovered File', 'media'),
        'Recovery Status',
        'Recovered Format',
        'Object Role',
        'Original Size (bytes)',
        'Account Email',
        'UUID',
        'Vault Object Path',
        'Trailer Version',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_hidden_files(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    columns = _columns(source_path, 'file_v1')
    delete_state = 'file_v1.delete_state' if 'delete_state' in columns else "''"

    query = f'''
    SELECT file_v1.added_time_utc, file_v1.file_last_modified_time_utc, file_v1.name,
           folder_v1.name, file_v1.original_path, file_v1.mime_type, file_v1.file_size,
           file_v1.image_width, file_v1.image_height, file_v1.video_duration,
           file_v1.file_type, file_v1.encrypt_state, file_v1.storage_type,
           file_v1.complete_state, {delete_state}, file_v1.uuid, file_v1.source
    FROM file_v1
    LEFT JOIN folder_v1 ON file_v1.folder_id = folder_v1._id
    ORDER BY file_v1.added_time_utc
    '''
    for record in _query(source_path, 'file_v1', query):
        dimensions = f'{record[7]} x {record[8]}' if record[7] or record[8] else ''
        data_list.append((
            _ms(record[0]), _ms(record[1]), record[2], record[3], record[4], record[5],
            record[6], dimensions, record[9], record[10], record[11], record[12],
            record[13], record[14], record[15], record[16],
        ))

    data_headers = (
        ('Added Time', 'datetime'),
        ('File Last Modified Time', 'datetime'),
        'File Name',
        'Folder',
        'Original Path',
        'MIME Type',
        'File Size',
        'Dimensions',
        'Video Duration',
        'File Type Value',
        'Encrypt State',
        'Storage Type',
        'Complete State',
        'Delete State',
        'UUID',
        'Source',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_folders(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT create_time_utc, name, folder_type, child_file_count, child_folder_count,
           parent_folder_id, password_hash, uuid, _id
    FROM folder_v1
    ORDER BY create_time_utc
    '''
    for record in _query(source_path, 'folder_v1', query):
        data_list.append((
            _ms(record[0]), record[1], FOLDER_TYPES.get(record[2], record[2]), record[3],
            record[4], record[5], 'Yes' if record[6] else 'No', record[7], record[8],
        ))

    data_headers = (
        ('Create Time', 'datetime'),
        'Folder Name',
        'Folder Type',
        'Child File Count',
        'Child Folder Count',
        'Parent Folder ID',
        'Folder Password Set',
        'UUID',
        'Folder ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_break_in_reports(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT timestamp, wrongly_attempt_code, locking_type, photo_path, location_latitude,
           location_longitude, address, is_new
    FROM break_in_report
    ORDER BY timestamp
    '''
    for record in _query(source_path, 'break_in_report', query):
        media = check_in_media(record[3], os.path.basename(record[3] or '')) or '' if record[3] else ''
        data_list.append((
            _ms(record[0]), record[1], record[2], media, record[3], record[4], record[5],
            record[6], record[7],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Code Entered',
        'Locking Type',
        ('Photo', 'media'),
        'Photo Path',
        'Latitude',
        'Longitude',
        'Address',
        'Unread',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_break_in_images(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        source_path = os.path.dirname(file_found)
        name = os.path.basename(file_found)
        match = BREAK_IN_NAME.search(name)
        captured = ''
        if match:
            day, clock = match.groups()
            captured = f'{day[0:4]}-{day[4:6]}-{day[6:8]} {clock[0:2]}:{clock[2:4]}:{clock[4:6]}'
        media = check_in_media(file_found, name) or ''
        data_list.append((captured, media, name, os.path.getsize(file_found),
                          context.get_relative_path(file_found)))

    data_headers = (
        'Capture Time (device local)',
        ('Image', 'media'),
        'File Name',
        'File Size',
        'Path',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_locked_apps(context):
    source_path = get_file_path(context.get_files_found(), 'AppLock.db')
    data_list = []
    for record in _query(
            source_path, 'locked_app',
            'SELECT package_name, disguise_lock, _id FROM locked_app ORDER BY package_name'):
        data_list.append((record[0], 'Yes' if record[1] else 'No', record[2]))

    data_headers = ('Package Name', 'Disguise Lock', 'Row ID')
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_applock_break_ins(context):
    source_path = get_file_path(context.get_files_found(), 'AppLock.db')
    data_list = []
    query = '''
    SELECT timestamp, package_name, wrongly_attempt_code, locking_type, photo_path, is_new
    FROM break_in_report_in_applock
    ORDER BY timestamp
    '''
    for record in _query(source_path, 'break_in_report_in_applock', query):
        media = check_in_media(record[4], os.path.basename(record[4] or '')) or '' if record[4] else ''
        data_list.append((_ms(record[0]), record[1], record[2], record[3], media, record[4], record[5]))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Package Name',
        'Code Entered',
        'Locking Type',
        ('Photo', 'media'),
        'Photo Path',
        'Unread',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_browser_history(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = 'SELECT last_visit_time_utc, title, url, host FROM browser_history ORDER BY last_visit_time_utc'
    for record in _query(source_path, 'browser_history', query):
        data_list.append((_ms(record[0]), record[1], record[2], record[3]))

    data_headers = (
        ('Last Visit Time', 'datetime'),
        'Title',
        'URL',
        'Host',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_browser_urls(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT last_visit_time_utc, create_time_utc, title, url, visit_count, fav_icon_url
    FROM web_url
    ORDER BY _id
    '''
    for record in _query(source_path, 'web_url', query):
        data_list.append((_ms(record[0]), _ms(record[1]), record[2], record[3], record[4], record[5]))

    data_headers = (
        ('Last Visit Time', 'datetime'),
        ('Create Time', 'datetime'),
        'Title',
        'URL',
        'Visit Count',
        'Favicon URL',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_downloads(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT begin_time, end_time, name, url, web_url, local_path, mime_type, total_size,
           downloaded_size, download_percentage, state, error_code, thumbnail_url
    FROM download_task
    ORDER BY begin_time
    '''
    for record in _query(source_path, 'download_task', query):
        data_list.append((
            _ms(record[0]), _ms(record[1]), record[2], record[3], record[4], record[5],
            record[6], record[7], record[8], record[9], record[10], record[11], record[12],
        ))

    data_headers = (
        ('Begin Time', 'datetime'),
        ('End Time', 'datetime'),
        'Name',
        'Download URL',
        'Page URL',
        'Local Path',
        'MIME Type',
        'Total Size',
        'Downloaded Size',
        'Percentage',
        'State',
        'Error Code',
        'Thumbnail URL',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_unhide_history(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = '''
        SELECT action_time, create_time, name, action_type, file_type, target_path,
               original_path, mime_type, size, duration, uuid, file_id
        FROM export_unhidden_history
        ORDER BY action_time
        '''
    for record in _query(source_path, 'export_unhidden_history', query):
        data_list.append((
            _ms(record[0]), _ms(record[1]), record[2], record[3], record[4], record[5],
            record[6], record[7], record[8], record[9], record[10], record[11],
        ))

    data_headers = (
        ('Action Time', 'datetime'),
        ('Create Time', 'datetime'),
        'File Name',
        'Action Type Value',
        'File Type Value',
        'Target Path',
        'Original Path',
        'MIME Type',
        'Size',
        'Duration',
        'UUID',
        'File ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_recycle_bin(context):
    source_path = _galleryvault_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT recycle_bin_v1.delete_time, file_v1.name, file_v1.original_path, file_v1.mime_type,
           file_v1.file_size, file_v1.uuid, recycle_bin_v1.file_id
    FROM recycle_bin_v1
    LEFT JOIN file_v1 ON recycle_bin_v1.file_id = file_v1._id
    ORDER BY recycle_bin_v1.delete_time
    '''
    for record in _query(source_path, 'recycle_bin_v1', query):
        data_list.append((_ms(record[0]), record[1], record[2], record[3], record[4],
                          record[5], record[6]))

    data_headers = (
        ('Delete Time', 'datetime'),
        'File Name',
        'Original Path',
        'MIME Type',
        'File Size',
        'UUID',
        'File ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_file_actions(context):
    source_path = get_file_path(context.get_files_found(), 'file_action_log.db')
    data_list = []
    query = 'SELECT action_time, action_type, file_path, _id FROM file_action ORDER BY action_time'
    for record in _query(source_path, 'file_action', query):
        data_list.append((_ms(record[0]), record[1], record[2], record[3]))

    data_headers = (
        ('Action Time', 'datetime'),
        'Action Type Value',
        'Vault File Path',
        'Row ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_preferences(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''

    # (friendly label, raw shared_prefs key, is a millisecond timestamp)
    preference_fields = (
        ('Authentication Email', 'AuthenticationEmail', False),
        ('Gallery Vault Folder', 'gallery_vault_folder', False),
        ('First Open Time', 'first_open_time', True),
        ('Last Recycle Bin Cleanup Time', 'last_clear_expire_recycle_bin_file_time', True),
        ('Cloud Storage Type', 'use_cloud_storage_type', False),
        ('Icon Disguise Enabled', 'icon_disguise_enabled', False),
        ('Calculator Disguise Shortcut ID', 'calculator_short_cut_id', False),
        ('Icon Disguise Enabled Time', 'last_enable_icon_disguise_time', True),
        ('Install Referrer Package', 'app_fresh_installer', False),
        ('Install Signature (App Instance UUID)', 'signature', False),
        ('Currently Unlocked', 'is_unlocked', False),
        ('Last Active Time', 'ActiveTimeMS', True),
        ('App Version Code', 'VersionCode', False),
        ('Fresh Install Version Code', 'FreshInstallVersionCode', False),
        ('Launch Count', 'launch_times', False),
        ('Add File Count', 'add_file_times', False),
        ('Last Unlocked Profile ID', 'unlock_successfully_profile_id', False),
        ('Last Android ID (DES key source)', 'last_android_id', False),
    )

    for file_found in files_found:
        file_found = str(file_found)

        if os.path.basename(file_found) != 'Kidd.xml':
            continue

        source_path = file_found

        try:
            root = ET.parse(file_found).getroot()
        except (ET.ParseError, OSError) as error:
            logfunc(
                f'GalleryVault: could not parse Kidd.xml '
                f'{file_found}: {error}'
            )
            continue

        for label, raw_key, is_timestamp in preference_fields:
            value = _get_xml_value(root, raw_key)

            if is_timestamp:
                value = _ms(value)

            data_list.append((
                label,
                value,
                raw_key,
            ))

        lock_pin = _get_xml_value(root, 'LockPin')
        lock_pin_part_1 = ''
        lock_pin_part_2 = ''

        if (
            lock_pin
            and len(lock_pin) == 72
            and all(c in '0123456789abcdefABCDEF' for c in lock_pin)
        ):
            lock_pin_part_1 = lock_pin[:40]
            lock_pin_part_2 = lock_pin[40:]

        data_list.extend([
            (
                'LockPin',
                lock_pin,
                'LockPin',
            ),
            (
                'LockPin Part 1 SHA1 (40 hex)',
                lock_pin_part_1,
                'LockPin',
            ),
            (
                'LockPin Part 2 MD5 (32 hex)',
                lock_pin_part_2,
                'LockPin',
            ),
        ])

    data_headers = (
        'Preference',
        'Value',
        'Original Key',
    )

    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_account_profile(context):
    files_found = context.get_files_found()

    account_profile_path = ''
    kidd_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        basename = os.path.basename(file_found)

        if basename == 'AccountProfile.xml':
            account_profile_path = file_found

        elif basename == 'Kidd.xml':
            kidd_path = file_found

    if not account_profile_path or not kidd_path:
        return (
            ('Name', 'Value'),
            [],
            account_profile_path or kidd_path,
        )

    try:
        kidd_root = ET.parse(kidd_path).getroot()
        profile_root = ET.parse(account_profile_path).getroot()

    except (ET.ParseError, OSError) as error:
        logfunc(
            f'GalleryVault: could not parse account preferences: {error}'
        )

        return (
            ('Name', 'Value'),
            [],
            account_profile_path,
        )

    android_id = _get_xml_value(
        kidd_root,
        'last_android_id'
    ).strip()

    if len(android_id) < 8:
        logfunc(
            'GalleryVault: last_android_id not found or invalid'
        )
        return ('Name', 'Value'), [], account_profile_path


    # GalleryVault's DES helper uses an 8-byte DES key.
    des_key = android_id[:8]

    encrypted_email = _get_xml_value(
        profile_root,
        'AccountEmail'
    )

    encrypted_id = _get_xml_value(
        profile_root,
        'AccountId'
    )

    encrypted_info = _get_xml_value(
        profile_root,
        'AccountInfo'
    )

    account_email = _galleryvault_des_decrypt(
        encrypted_email,
        des_key
    )

    account_id = _galleryvault_des_decrypt(
        encrypted_id,
        des_key
    )

    account_info_raw = _galleryvault_des_decrypt(
        encrypted_info,
        des_key
    )

    account_info = {}

    if account_info_raw:
        try:
            account_info = json.loads(account_info_raw)
        except ValueError:
            logfunc(
                'GalleryVault: decrypted AccountInfo is not valid JSON'
            )

    data_list = [
        ('Account Email', account_email),
        ('Account ID', account_id),
        ('Account Name', account_info.get('name', '')),
        (
            'Account Active',
            str(account_info.get('active', ''))
        ),
        (
            'OAuth Login',
            str(account_info.get('is_oauth_login', ''))
        ),
        (
            'OAuth Provider',
            account_info.get('oauth_provider', '')
        ),
        (
            'OAuth User Email',
            account_info.get('oauth_user_email', '')
        ),
        (
            'Account Token',
            account_info.get('token', '')
        ),
    ]

    data_headers = (
        'Name',
        'Value',
    )

    return (
        data_headers,
        data_list,
        account_profile_path,
    )

@artifact_processor
def galleryvault_cloud_account(context):
    files_found = context.get_files_found()
    source_path = _cloud_cache_db(files_found)
    data_list = []

    drive_query = '''
    SELECT drive_provider, drive_account_id, drive_id, drive_identity_id, is_primary,
           status, space_used, drive_storage_size, root_folder_internal_id
    FROM user_cloud_drive
    ORDER BY is_primary DESC
    '''
    for record in _query(source_path, 'user_cloud_drive', drive_query):
        data_list.extend([
            ('Cloud Provider', record[0]),
            ('Cloud Account', record[1]),
            ('Drive ID', record[2]),
            ('Drive Identity ID', record[3]),
            ('Primary Drive', 'Yes' if record[4] else 'No'),
            ('Drive Status', record[5]),
            ('Space Used (bytes)', record[6]),
            ('Drive Storage Size (bytes)', record[7]),
            ('Root Folder Internal ID', record[8]),
        ])

    for record in _query(
            source_path, 'user_cloud_storage_property',
            'SELECT storage_level_type, status FROM user_cloud_storage_property'):
        data_list.extend([
            ('Storage Level Type', record[0]),
            ('Storage Property Status', record[1]),
        ])

    for record in _query(
            source_path, 'user_cloud_monthly_usage',
            'SELECT added_file_count, add_file_quota, is_upload_exceed_max '
            'FROM user_cloud_monthly_usage'):
        data_list.extend([
            ('Files Added This Month', record[0]),
            ('Monthly File Quota', record[1]),
            ('Quota Exceeded', 'Yes' if record[2] else 'No'),
        ])

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_cloud_folders(context):
    files_found = context.get_files_found()
    source_path = _cloud_cache_db(files_found)
    folder_map = _cloud_folder_map(source_path)
    path_cache = {}
    data_list = []

    query = '''
    SELECT create_date_utc, name, folder_uuid, files_count, revision_id,
           parent_folder_id, entry_id, cloud_drive_id
    FROM cloud_folders
    ORDER BY create_date_utc
    '''
    for record in _query(source_path, 'cloud_folders', query):
        parent_path = _cloud_folder_path(record[5], folder_map, path_cache)
        data_list.append((
            _ms(record[0]), record[1], parent_path or '/', record[2], record[3],
            record[4], record[6], record[7],
        ))

    data_headers = (
        ('Create Time', 'datetime'),
        'Folder Name',
        'Parent Path',
        'Folder UUID',
        'Files Count',
        'Revision ID',
        'Entry ID',
        'Cloud Drive ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_cloud_files(context):
    files_found = context.get_files_found()
    source_path = _cloud_cache_db(files_found)
    folder_map = _cloud_folder_map(source_path)
    path_cache = {}
    data_list = []

    query = '''
    SELECT file_add_time_utc, file_org_create_time_utc, name, file_uuid, mime_type,
           size, image_width, image_height, parent_folder_id, is_complete, has_thumb,
           cloud_file_storage_key, file_encryption_key, move_to_recycle_bin_time_utc,
           file_content_hash, cloud_drive_id
    FROM cloud_files
    ORDER BY file_add_time_utc
    '''
    for record in _query(source_path, 'cloud_files', query):
        folder_path = _cloud_folder_path(record[8], folder_map, path_cache) or '/'
        dimensions = f'{record[6]} x {record[7]}' if record[6] or record[7] else ''
        encryption_key = record[12].hex() if record[12] else ''
        data_list.append((
            _ms(record[0]), _ms(record[1]), record[2], folder_path, record[3],
            record[4], record[5], dimensions, 'Yes' if record[9] else 'No',
            'Yes' if record[10] else 'No', _ms(record[13]), record[11],
            encryption_key, record[14], record[15],
        ))

    data_headers = (
        ('Cloud Add Time', 'datetime'),
        ('Original Create Time', 'datetime'),
        'File Name',
        'Cloud Folder Path',
        'File UUID',
        'MIME Type',
        'Size (bytes)',
        'Dimensions',
        'Upload Complete',
        'Has Thumbnail',
        ('Moved to Recycle Bin', 'datetime'),
        'Cloud Storage Key',
        'File Encryption Key (hex)',
        'File Content Hash',
        'Cloud Drive ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_cloud_change_history(context):
    files_found = context.get_files_found()
    source_path = _cloud_cache_db(files_found)
    data_list = []

    name_by_uuid = {}
    for record in _query(
            source_path, 'cloud_folders', 'SELECT folder_uuid, name FROM cloud_folders'):
        if record[0]:
            name_by_uuid[record[0]] = record[1]
    for record in _query(
            source_path, 'cloud_files', 'SELECT file_uuid, name FROM cloud_files'):
        if record[0]:
            name_by_uuid[record[0]] = record[1]

    query = '''
    SELECT modify_date_utc, entry_type, entry_uuid, change_action, revision_id,
           entry_id, cloud_drive_id
    FROM entry_change_history
    ORDER BY modify_date_utc
    '''
    for record in _query(source_path, 'entry_change_history', query):
        data_list.append((
            _ms(record[0]), CLOUD_ENTRY_TYPES.get(record[1], record[1]),
            name_by_uuid.get(record[2], ''), record[2], record[3], record[4],
            record[5], record[6],
        ))

    data_headers = (
        ('Modify Time', 'datetime'),
        'Entry Type',
        'Entry Name',
        'Entry UUID',
        'Change Action Value',
        'Revision ID',
        'Entry ID',
        'Cloud Drive ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def galleryvault_cloud_upload_tasks(context):
    files_found = context.get_files_found()
    source_path = _cloud_cache_db(files_found)
    data_list = []

    query = '''
    SELECT cloud_file_upload_tasks.begin_time, cloud_files.name,
           cloud_file_upload_tasks.bytes_current, cloud_file_upload_tasks.bytes_total,
           cloud_file_upload_tasks.state, cloud_file_upload_tasks.error_code,
           cloud_upload_part_tasks.type, cloud_upload_part_tasks.bytes_current,
           cloud_upload_part_tasks.bytes_total, cloud_upload_part_tasks.error_code,
           cloud_file_upload_tasks.cloud_file_storage_key,
           cloud_file_upload_tasks.cloud_file_encryption_key,
           cloud_file_upload_tasks._id
    FROM cloud_file_upload_tasks
    LEFT JOIN cloud_files ON cloud_file_upload_tasks.cloud_file_id = cloud_files.entry_id
    LEFT JOIN cloud_upload_part_tasks
           ON cloud_upload_part_tasks.cloud_file_transfer_task_id = cloud_file_upload_tasks._id
    ORDER BY cloud_file_upload_tasks.begin_time
    '''
    for record in _query(source_path, 'cloud_file_upload_tasks', query):
        percent = ''
        if record[8]:
            percent = f'{(record[7] or 0) / record[8] * 100:.1f}%'
        encryption_key = record[11].hex() if record[11] else ''
        data_list.append((
            _ms(record[0]), record[1], record[2], record[3], record[4], record[5],
            record[6], record[7], record[8], percent, record[9], record[10],
            encryption_key, record[12],
        ))

    data_headers = (
        ('Begin Time', 'datetime'),
        'File Name',
        'File Bytes Uploaded',
        'File Bytes Total',
        'Task State',
        'Task Error Code',
        'Part Type',
        'Part Bytes Uploaded',
        'Part Bytes Total',
        'Part Percent Complete',
        'Part Error Code',
        'Cloud Storage Key',
        'File Encryption Key (hex)',
        'Task ID',
    )
    return data_headers, data_list, source_path
