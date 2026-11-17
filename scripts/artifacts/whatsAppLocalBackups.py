__artifacts_v2__ = {
    "whatsapp_local_backups": {
        "name": "WhatsApp - Local Backups",
        "description": "The encrypted local backup files of WhatsApp and WhatsApp Business in shared storage, with the "
                       "format, key type, app version and other fields of each file's unencrypted header, and the key "
                       "file in the extraction whose salts match it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per backup file whose name ends in .crypt and a number, in a WhatsApp/Databases or WhatsApp/Backups folder (WhatsApp Business/ for WhatsApp Business). The same path below the storage root, for one Android user and with identical bytes, seen under several spellings of shared storage (data/media/<N>, mnt/pass_through/.../emulated/<N>, mnt/user/.../emulated/<N>, storage/emulated/<N>) is one row. Copies counts the spellings and Source File is the shortest one. Storage User is the <N> of that root, and is empty where the path names none, as in a pull of /sdcard. Backup Of is the file name without its .crypt extension, as stored.\nFormat is read from the file's first bytes, not from its name, with the layouts of ElDavoo/wa-crypt-tools at commit b6f67453d19e443f53f57da0361f3ef5e8b6821d (proto/backup_prefix.proto, proto/C14_cipher.proto, proto/C15_IV.proto, proto/backup_expiry.proto and src/wa_crypt_tools/lib/db/db12.py). crypt14 and crypt15 files start with a varint size and a BackupPrefix protobuf message, which carries an encryption IV in field 2 (crypt14) or field 3 (crypt15); a crypt12 file starts with a 67-byte header with no protobuf, whose first two bytes are the cipher version 00 01. A file that fits none of these shows not recognised and the run log names it. The contents of a backup are encrypted. They are not decrypted or parsed; the whole file is hashed only to recognise identical copies.\nKey Type (as stored) is the key_type_new field of the header, or key_type_deprecated where key_type_new is absent, with the name wa-crypt-tools gives the value (proto/key_type.proto, which says the names are WhatsApp's own); crypt12 headers carry no key type. The wa-crypt-tools README says a crypt14 backup is opened with the key file named key, found on the device at /data/data/com.whatsapp/files/key, and an end-to-end (crypt15) backup with encrypted_backup.key or the user's 64-digit key. WhatsApp Version, JID Suffix (as stored), Backup Version (as stored) and Cleaned DB (as stored) are fields 1, 3, 4 and 39 of the header's backup metadata, shown as stored and empty where absent; wa-crypt-tools describes jid_suffix as the last two digits of the user's JID (phone number).\nMatching Key File is the WhatsApp key file in the extraction (com.whatsapp/files/key or com.whatsapp.w4b/files/key) whose server salt (32 bytes) and Google ID salt (16 bytes) equal those in the backup's header. wa-crypt-tools checks these two values against the key file when it reads a crypt12 header (src/wa_crypt_tools/lib/db/db12.py) and copies them from the key file when it writes a crypt14 header (src/wa_crypt_tools/lib/db/db14.py); the match here is a comparison of the stored bytes, and nothing is decrypted. A key file is read as a serialized Java byte[] (src/wa_crypt_tools/lib/key/key14.py) and used only when its cipher version is 00 01 and its stored hash equals the SHA-256 of its Google ID salt; a key file that fails these checks is named in the run log. The same key under data/data, data/user/<N> and data_mirror is counted once. An empty value means none of the key files read here (the two paths above) carries the header's salts. It does not say why, and it does not rule out a copy of the key elsewhere in the extraction. The crypt15 key data wa-crypt-tools describes (proto/C15_IV.proto) holds only an IV, and encrypted_backup.key is not read, so a crypt15 row is expected to show no match; this was not exercised on a real file.\nModified (UTC) is the modification time the extraction recorded for the file. Where the input is a zip that records only the time in its directory entry, that time is shown in Modified (zip entry, as stored) and not converted, because a zip directory entry has no time zone. Not reported: the device model, export file size, migration flags, hash salt and hash, LID and display suffix and passkey fields of the header (the device model and export file size were absent on all 262 crypt14 headers examined), and the Stickers and Wallpapers folders under Backups.\nEvidence tiers. Data-proven on six real profile runs: moto_g_play_2026_a16_logical_known_20261116 (a logical collection, 9 rows, no key file in it), russell_pixel6a_a13 (13 rows from 39 files, three spellings each, none matching the key file in that extraction), pixel3_a11 (11 crypt12 rows, 9 named .crypt12 and 2 named .crypt1 with the crypt12 layout, all matching its key), samsungs20_a13 (23 rows, all matching), pixel7a_a14 (12 rows; 8 match, and the 4 that do not are the dated msgstore backups whose header gives an earlier WhatsApp version) and anne_a15 (19 rows, all matching). The header reader read all 273 backup files (262 crypt14, 11 crypt12) of the 15 registered Android extractions found to hold any, and their key matches were counted again on four of them by a second reader (a raw protobuf walk and a search of the key file's bytes), with the same result. Every crypt14 header examined (262) carried 0 in key_type_deprecated, and 87 also carried 0 in key_type_new; the split is by file, not by image. So Key Type (as stored) held one value, WA_PROVIDED (0), on all rows of the five crypt14 runs, and Format one value on all rows of every run (crypt14, or crypt12 on pixel3_a11). App held one value, WhatsApp, on all rows of all six runs. Storage User held one value on all rows of each run (0, or empty on the moto pull of /sdcard). JID Suffix (as stored) held one value on all rows of each crypt14 run and is empty on crypt12 rows. Copies held one value on all rows of each run (3 on russell_pixel6a_a13, 1 on the others). WhatsApp Version held one value on all 9 rows of the moto run. Matching Key File had no value on any row of the moto and russell_pixel6a_a13 runs and held one path on all rows of pixel3_a11. On the moto known data, WhatsApp Version equals the WhatsApp version installed on the phone (2.26.44.90, from its package dump). Source-verified, not exercised on a real file: crypt15 and the end-to-end key types. Code-present, tested only on constructed files: WhatsApp Business (its folder and package names are not from a cited source), a second Android user's own backups and key, and the mnt/user and storage/emulated spellings, which were not in any image examined.",
        "paths": ('*/WhatsApp/Databases/*.crypt*', '*/WhatsApp/Backups/*.crypt*',
                  '*/WhatsApp Business/Databases/*.crypt*', '*/WhatsApp Business/Backups/*.crypt*',
                  '*/com.whatsapp/files/key', '*/com.whatsapp.w4b/files/key'),
        "output_types": "standard",
        "artifact_icon": "archive",
        "sample_data": {
            "moto_g_play_2026_a16_logical_known_20261116": "Android 16 | logical collection (known data) | 9 rows",
            "russell_pixel6a_a13": "Android 13 | 39 files under three spellings | 13 rows",
            "pixel3_a11": "Android 11 | crypt12 | 11 rows",
            "samsungs20_a13": "Android 13 | 23 rows",
            "pixel7a_a14": "Android 14 | 12 rows",
            "anne_a15": "Android 15 | 19 rows",
        },
    },
}

import datetime
import hashlib
import os
import re

from scripts.blackboxprotobuf import decode_message
from scripts.artifacts.storagePathViews import canonical_path
from scripts.ilapfuncs import artifact_processor, logfunc

# How much of a file is read: the header is a varint size and a protobuf message (crypt14 and crypt15),
# or 67 fixed bytes (crypt12). A header claiming more than this is not read.
HEADER_LIMIT = 4096

# KeyType of the BackupPrefix header (wa-crypt-tools proto/key_type.proto, names WhatsApp's own).
KEY_TYPES = {0: 'WA_PROVIDED', 1: 'E2EE_DEPRECATED', 2: 'E2EE_PASSWORD', 3: 'E2EE_ENCRYPTION_KEY', 4: 'E2EE_PASSKEY'}

# BackupPrefix (wa-crypt-tools proto/backup_prefix.proto) with the fields read here typed, so that no
# bytes field is guessed as a message. Field 4 is BackupExpiry, the backup metadata.
_TYPEDEF = {
    '1': {'type': 'int'},
    '2': {'type': 'message', 'message_typedef': {
        '1': {'type': 'bytes'}, '2': {'type': 'bytes'}, '3': {'type': 'bytes'}, '4': {'type': 'bytes'},
        '5': {'type': 'bytes'}}},
    '3': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes'}}},
    '4': {'type': 'message', 'message_typedef': {
        '1': {'type': 'bytes'}, '2': {'type': 'bytes'}, '3': {'type': 'bytes'}, '4': {'type': 'int'},
        '38': {'type': 'int'}, '39': {'type': 'int'}, '43': {'type': 'bytes'}, '44': {'type': 'bytes'}}},
    '6': {'type': 'int'},
}

# Java Object Serialization of a byte[] (STREAM_MAGIC, STREAM_VERSION, TC_ARRAY, TC_CLASSDESC "[B"); the
# serialVersionUID, flags, field count, TC_ENDBLOCKDATA and TC_NULL follow, then the length and the bytes.
_JAVA_BYTE_ARRAY = b'\xac\xed\x00\x05\x75\x72\x00\x02\x5b\x42'
_CRYPT12_CIPHER = b'\x00\x01'

# The roots a shared storage path can be seen under, with the Android user they name.
_STORAGE_ROOTS = (
    re.compile(r'(?:^|/)(?:user)?data/media/(\d+)/'),
    re.compile(r'(?:^|/)mnt/pass_through/\d+/emulated/(\d+)/'),
    re.compile(r'(?:^|/)mnt/user/\d+/emulated/(\d+)/'),
    re.compile(r'(?:^|/)storage/emulated/(\d+)/'),
)
_APP_FOLDER = re.compile(r'(?:^|/)(WhatsApp(?: Business)?)/(Databases|Backups)/([^/]+)$')
_EXTENSION = re.compile(r'\.crypt(\d+)$')


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def read_varint(data, offset=0):
    """``(value, next offset)`` of a protobuf varint, or ``(None, offset)`` when it is not one."""
    value = shift = 0
    index = offset
    while index < len(data) and shift < 35:
        byte = data[index]
        index += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, index
        shift += 7
    return None, offset


def parse_header(data):
    """The fields of a WhatsApp backup header, read from the first bytes of the file.

    crypt14 and crypt15 files start with a varint size and a BackupPrefix protobuf message; crypt12 files
    start with a 67-byte header that has no protobuf. Returns a dict with ``format`` and the fields found.
    """
    size, start = read_varint(data)
    if size and start + size <= len(data):
        try:
            message, _typedef = decode_message(data[start:start + size], _TYPEDEF)
        except Exception:  # pylint: disable=broad-exception-caught
            message = None
        if isinstance(message, dict):
            c14 = message.get('2') if isinstance(message.get('2'), dict) else {}
            c15 = message.get('3') if isinstance(message.get('3'), dict) else {}
            meta = message.get('4') if isinstance(message.get('4'), dict) else {}
            if c15.get('1') or c14.get('5'):
                key_type = message.get('6', message.get('1'))
                return {
                    'format': 'crypt15' if c15.get('1') else 'crypt14',
                    'header_size': start + size,
                    'key_type': key_type,
                    'key_type_field': '6' if '6' in message else ('1' if '1' in message else ''),
                    'app_version': _text(meta.get('1')),
                    'device_model': _text(meta.get('2')),
                    'jid_suffix': _text(meta.get('3')),
                    'backup_version': meta.get('4'),
                    'export_size': meta.get('38'),
                    'cleaned_db': meta.get('39'),
                    'server_salt': c14.get('3') or b'',
                    'google_id_salt': c14.get('4') or b'',
                }
    if len(data) >= 67 and data[:2] == _CRYPT12_CIPHER:
        return {'format': 'crypt12', 'header_size': 67, 'key_type': None, 'key_type_field': '', 'app_version': '',
                'device_model': '', 'jid_suffix': '', 'backup_version': None, 'export_size': None, 'cleaned_db': None,
                'server_salt': data[3:35], 'google_id_salt': data[35:51]}
    return None


def parse_key_file(data):
    """``(server salt, google id salt)`` of a crypt12/crypt14 key file (a serialized Java byte[]), or None."""
    if not data.startswith(_JAVA_BYTE_ARRAY) or len(data) < 27:
        return None
    # magic and "[B" (10), serialVersionUID (8), flags (1), field count (2), TC_ENDBLOCKDATA, TC_NULL
    if data[18] != 0x02 or data[19:21] != b'\x00\x00' or data[21:23] != b'\x78\x70':
        return None
    length = int.from_bytes(data[23:27], 'big')
    array = data[27:27 + length]
    if length < 83 or len(array) != length or array[:2] != _CRYPT12_CIPHER:
        return None
    if hashlib.sha256(array[35:51]).digest() != array[51:83]:
        return None
    return array[3:35], array[35:51]


def storage_key(relative_path):
    """``(Android user, path below the storage root)`` of a shared storage path; user '' when not named."""
    path = relative_path.replace('\\', '/')
    for pattern in _STORAGE_ROOTS:
        found = pattern.search(path)
        if found:
            return found.group(1), path[found.end():]
    return '', path


def _recorded_times(seeker, file_found):
    """(UTC modification time the seeker recorded, zone-less zip directory time as stored)."""
    info = seeker.file_infos.get(file_found) if seeker else None
    if not info:
        return None, ''
    if info.modification_date:
        try:
            return datetime.datetime.fromtimestamp(int(info.modification_date), datetime.timezone.utc), ''
        except (ValueError, OverflowError, OSError, TypeError):
            return None, ''
    zip_file = getattr(seeker, 'zip_file', None)
    if zip_file is None or info.source_path in getattr(seeker, '_chosen', {}):
        return None, ''
    try:
        stored = zip_file.getinfo(info.source_path).date_time
    except KeyError:
        return None, ''
    return None, '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*stored)


def _digest(path):
    hashed = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            hashed.update(chunk)
    return hashed.hexdigest()


@artifact_processor
def whatsapp_local_backups(context):
    headers = (('Modified (UTC)', 'datetime'), 'Modified (zip entry, as stored)', 'App', 'Storage User', 'Backup Of',
               'Format', 'Key Type (as stored)', 'WhatsApp Version', 'JID Suffix (as stored)',
               'Backup Version (as stored)', 'Cleaned DB (as stored)', 'Matching Key File', 'File Size (bytes)', 'Copies',
               'Source File')
    seeker = context.get_seeker()
    backups, keys = [], []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        relative = context.get_relative_path(file_found)
        if re.search(r'(?:^|/)com\.whatsapp(?:\.w4b)?/files/key$', relative.replace('\\', '/')):
            keys.append((file_found, relative))
        elif _APP_FOLDER.search(relative.replace('\\', '/')) and _EXTENSION.search(relative):
            backups.append((file_found, relative))

    # The same key file under several app data views (data/data, data/user/0, data_mirror) is one key.
    key_salts, seen_keys = [], {}
    for file_found, relative in sorted(keys, key=lambda item: canonical_path(item[1])[1]):
        with open(file_found, 'rb') as handle:
            raw = handle.read(HEADER_LIMIT)
        view = (canonical_path(relative)[0], raw)
        if view in seen_keys:
            continue
        seen_keys[view] = relative
        salts = parse_key_file(raw)
        if salts is None:
            logfunc(f'WhatsApp - Local Backups: {relative} is not a key file this artifact reads')
            continue
        key_salts.append((relative, salts))

    # One row per backup file; the same bytes under several spellings of one user's shared storage are one row.
    grouped = {}
    for file_found, relative in backups:
        user, tail = storage_key(relative)
        group = grouped.setdefault((user, tail, _digest(file_found)), [])
        group.append((file_found, relative))

    rows, sources = [], []
    for (user, _tail, _sha), copies in grouped.items():
        copies.sort(key=lambda item: (len(item[1]), item[1]))
        file_found, relative = copies[0]
        sources.append(file_found)
        app, _folder, name = _APP_FOLDER.search(relative.replace('\\', '/')).groups()
        with open(file_found, 'rb') as handle:
            head = handle.read(HEADER_LIMIT)
        size = os.path.getsize(file_found)
        header = parse_header(head)
        modified, zip_text = _recorded_times(seeker, file_found)
        backup_of = _EXTENSION.sub('', name)
        if header is None:
            logfunc(f'WhatsApp - Local Backups: {relative} has no crypt12, crypt14 or crypt15 header this artifact reads')
            rows.append((modified, zip_text, app, user, backup_of, 'not recognised', '', '', '', '', '', '', size,
                         len(copies), relative))
            continue
        key_type = ''
        if header['key_type'] is not None:
            key_type = f"{KEY_TYPES.get(header['key_type'], 'unknown')} ({header['key_type']})"
        matches = []
        if header['server_salt'] and header['google_id_salt']:
            matches = [path for path, (server, google) in key_salts
                       if server == header['server_salt'] and google == header['google_id_salt']]
        rows.append((modified, zip_text, app, user, backup_of, header['format'], key_type, header['app_version'],
                     header['jid_suffix'],
                     '' if header['backup_version'] is None else header['backup_version'],
                     '' if header['cleaned_db'] is None else header['cleaned_db'],
                     '\n'.join(matches), size, len(copies), relative))
    rows.sort(key=lambda row: (row[2], row[3], row[14]))
    return headers, rows, '\n'.join(sources + [file_found for file_found, _relative in keys])
