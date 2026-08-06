__artifacts_v2__ = {
    "galleryvault_vault_files": {
        "name": "GalleryVault - Vault Files",
        "description": "Recovers files hidden by GalleryVault from the encrypted objects stored "
                       "under the vault folder on external storage, together with the original "
                       "file name and creation time held in each object's own trailer",
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
        "author": "",
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
}

import json
import mimetypes
import os
import re
import struct

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
        ('URL', 'url'),
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
        ('URL', 'url'),
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
        ('Download URL', 'url'),
        ('Page URL', 'url'),
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
