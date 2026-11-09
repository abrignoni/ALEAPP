__artifacts_v2__ = {
    "private_notepad_notes": {
        "name": "Private Notepad - Notes",
        "description": "Notes from Private Notepad - safe notes "
                       "(ru.alexandermalikov.protectednotes), with the title, body and "
                       "attachments decrypted",
        "author": "Jens Grønhøj Stigaard",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per row of the notes table in "
                 "ru.alexandermalikov.protectednotes/databases/notes.db. Date, Created and Delete "
                 "Date are the date, date_created and date_delete columns as stored; which events "
                 "set them was not established from the app's code. A column the database does "
                 "not have is blank. Attachments shows the decrypted image and audio files the "
                 "note's images and audio_files columns name; see Private Notepad - Note "
                 "Attachments for how they are found and for the ones that were not. "
                 "Attachments is blank when a note names no attachment or no named file decrypts. "
                 "In the real extraction 13 notes decrypted and Attachments was blank on all 13 "
                 "rows, because no note named an attachment. "
                 "The data key is AES-128-CBC encrypted (zero IV, PKCS7) under a key built into "
                 "the app, the XOR of two 16-byte constants, and is read from the dek column of "
                 "the service_data table in notes.db or from the encryption_key string in "
                 "shared_prefs/protected_notes_preferences.xml. Where both exist, the one that "
                 "decrypts the container's own notes or passwords is used; see Key Source in "
                 "Private Notepad - App Settings. Text fields are base64 of AES-128-CBC "
                 "ciphertext under the data key with a zero IV and PKCS7 padding. Each database "
                 "is read with the preferences file from the same app data folder and Android "
                 "user. A field that does not decrypt is reported as stored (base64) and the "
                 "failure is logged. Only live rows are read: records in freed database pages "
                 "are not recovered. Times are stored in milliseconds and reported in UTC; a "
                 "time stored as NULL or 0 is blank. Run on one real extraction (app 6.9.1, "
                 "versionCode 108, Android 14), whose database has no service_data table; the "
                 "6.9.1 APK does not name that table either. service_data.dek and app version "
                 "6.11.1 were exercised only on synthetic data.",
        "paths": (
            "*/ru.alexandermalikov.protectednotes/databases/notes.db*",
            "*/ru.alexandermalikov.protectednotes/shared_prefs/protected_notes_preferences.xml",
            "*/ru.alexandermalikov.protectednotes/files/images/*",
            "*/ru.alexandermalikov.protectednotes/files/recordings/*",
        ),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "private_notepad_attachments": {
        "name": "Private Notepad - Note Attachments",
        "description": "Image and audio attachments of Private Notepad notes, decrypted",
        "author": "Jens Grønhøj Stigaard",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per attachment id in the images and audio_files columns of the notes "
                 "table, each a JSON object whose lists hold the ids, and one row per file in the "
                 "attachment folders that no note names. An id from the images column is matched "
                 "to the file of exactly that name in files/images of the same app data folder, "
                 "and an id from the audio_files column to files/recordings. Those folders and the "
                 "file naming were read from the code of the 6.9.1 APK (classes i8.k and i8.d); "
                 "other app versions were not checked, and a file elsewhere is not read. Files are "
                 "decrypted whole with the data key and the media type is taken from the decrypted "
                 "bytes. Status reads Decrypted, Not decrypted (the file did not decrypt under the "
                 "data key), File not found (no file in the extraction carries the id; this is not "
                 "evidence the attachment never existed) or Not named by a note, where Attachment "
                 "is blank if the file did not decrypt. Attachment Type is the column the id came "
                 "from, or the folder for a file no note names, whose name is then given as "
                 "Attachment ID. The files/image_previews folder, the app's cache folder and "
                 "Pictures under Android/data are not read; see Private Notepad - Intruder Photos "
                 "for files/intruder_photos. The real "
                 "extraction had no rows here: its 13 notes named no attachment, files/images was "
                 "empty and files/recordings was absent, so attachment decryption was exercised "
                 "only on synthetic data. "
                 "The data key is AES-128-CBC encrypted (zero IV, PKCS7) under a key built into "
                 "the app, the XOR of two 16-byte constants, and is read from the dek column of "
                 "the service_data table in notes.db or from the encryption_key string in "
                 "shared_prefs/protected_notes_preferences.xml. Where both exist, the one that "
                 "decrypts the container's own notes or passwords is used; see Key Source in "
                 "Private Notepad - App Settings. Text fields are base64 of AES-128-CBC "
                 "ciphertext under the data key with a zero IV and PKCS7 padding. Each database "
                 "is read with the preferences file from the same app data folder and Android "
                 "user. A field that does not decrypt is reported as stored (base64) and the "
                 "failure is logged. Only live rows are read: records in freed database pages "
                 "are not recovered. Times are stored in milliseconds and reported in UTC; a "
                 "time stored as NULL or 0 is blank. Run on one real extraction (app 6.9.1, "
                 "versionCode 108, Android 14), whose database has no service_data table; the "
                 "6.9.1 APK does not name that table either. service_data.dek and app version "
                 "6.11.1 were exercised only on synthetic data.",
        "paths": (
            "*/ru.alexandermalikov.protectednotes/databases/notes.db*",
            "*/ru.alexandermalikov.protectednotes/shared_prefs/protected_notes_preferences.xml",
            "*/ru.alexandermalikov.protectednotes/files/images/*",
            "*/ru.alexandermalikov.protectednotes/files/recordings/*",
        ),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
    "private_notepad_intruder_photos": {
        "name": "Private Notepad - Intruder Photos",
        "description": "Photos in the intruder_photos folder of Private Notepad",
        "author": "Jens Grønhøj Stigaard",
        "creation_date": "2026-11-06",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per file directly in the files/intruder_photos folder of an app data "
                 "folder. The folder name is the app's own; this artifact does not show who appears "
                 "in a photo or why it was taken, and what prompts the app to take one was not "
                 "established. What follows was read from the code of the 6.9.1 APK and was not "
                 "exercised on a real photo. Class d8.f (method m) writes the bytes of a "
                 "Camera.takePicture call to the file with no encryption step, so no key is used "
                 "here; whether other app versions encrypt them was not checked. Class i8.k (method "
                 "e) names the file from System.currentTimeMillis when it creates it, with .jpg "
                 "added. File Name Time is that number in UTC, taken from the name alone, and is "
                 "blank when the name is not a number. Method g of that class deletes the files in "
                 "the folder, so an empty or absent folder does not show that no photo was taken. "
                 "The media type is taken from the bytes. Status reads Image, or Not a recognised "
                 "image with Photo blank. The real extraction had no rows here because the folder "
                 "was absent, so this artifact was exercised only on synthetic data.",
        "paths": ("*/ru.alexandermalikov.protectednotes/files/intruder_photos/*",),
        "output_types": "standard",
        "artifact_icon": "camera",
    },
    "private_notepad_passwords": {
        "name": "Private Notepad - Passwords",
        "description": "Password entries stored in Private Notepad, decrypted",
        "author": "Jens Grønhøj Stigaard",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per row of the passwords table in notes.db; a database without the "
                 "table yields no rows and logs it. Name, Login, Password, Site Address and "
                 "Comment are the password_name, password_login, password_password, "
                 "password_site_address and password_comment columns decrypted. Created is "
                 "date_created as stored. The table held no rows in the real extraction, so "
                 "password decryption was exercised only on synthetic data. "
                 "The data key is AES-128-CBC encrypted (zero IV, PKCS7) under a key built into "
                 "the app, the XOR of two 16-byte constants, and is read from the dek column of "
                 "the service_data table in notes.db or from the encryption_key string in "
                 "shared_prefs/protected_notes_preferences.xml. Where both exist, the one that "
                 "decrypts the container's own notes or passwords is used; see Key Source in "
                 "Private Notepad - App Settings. Text fields are base64 of AES-128-CBC "
                 "ciphertext under the data key with a zero IV and PKCS7 padding. Each database "
                 "is read with the preferences file from the same app data folder and Android "
                 "user. A field that does not decrypt is reported as stored (base64) and the "
                 "failure is logged. Only live rows are read: records in freed database pages "
                 "are not recovered. Times are stored in milliseconds and reported in UTC; a "
                 "time stored as NULL or 0 is blank. Run on one real extraction (app 6.9.1, "
                 "versionCode 108, Android 14), whose database has no service_data table; the "
                 "6.9.1 APK does not name that table either. service_data.dek and app version "
                 "6.11.1 were exercised only on synthetic data.",
        "paths": (
            "*/ru.alexandermalikov.protectednotes/databases/notes.db*",
            "*/ru.alexandermalikov.protectednotes/shared_prefs/protected_notes_preferences.xml",
        ),
        "output_types": "standard",
        "artifact_icon": "key",
    },
    "private_notepad_settings": {
        "name": "Private Notepad - App Settings",
        "description": "Lock screen settings and last usage time recorded by Private Notepad",
        "author": "Jens Grønhøj Stigaard",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-06",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per protected_notes_preferences.xml, or per notes.db whose service table "
                 "has a row when there is no readable preferences file. Values are the preference "
                 "keys last_app_usage_time, show_lock_screen, protection_type, password_hint and "
                 "password_hash. A key the file does not hold is blank. What follows about the "
                 "app's behaviour was read from the code of the 6.9.1 APK and was not exercised "
                 "with a lock set. The app reads an absent protection_type as -1 and an absent "
                 "show_lock_screen as false. Protection Type labels (-1 Disabled, 0 Password, "
                 "1 PIN, 2 Pattern) are the strings the app's own analytics code gives those "
                 "values (class h7.b, method l); any other value reads Unknown. The stored number "
                 "is kept in brackets. Password Hash (hex) is the base64 value decoded to hex. The "
                 "app's hash function (class h7.q, method b) stores base64 of the SHA-1 digest of "
                 "the text it is given and adds no salt of its own. Password Hash (hex) is blank "
                 "when the key is absent; the app also clears the key when called with no "
                 "password, so a blank does not show that no password was ever set. Fake Password "
                 "Hash (hex) is the fake_password_hash key decoded the same way, and is blank when "
                 "the key is absent. The three code paths that set that key (f8.c.x, g8.c.B and "
                 "w7.c.f) call the same hash function first, h7.b0.f clears it, and what entering "
                 "that password does was not established. Password Hint "
                 "is blank when the key is absent or empty; what clears it was not established, so "
                 "a hint does not show that a lock is set. Service Table Protection Type and "
                 "Service Table Password Hash are the first row of the service table in notes.db, "
                 "as stored, and are blank when the table is absent or has no rows. In 6.9.1 the "
                 "only code naming that table reads it on an upgrade and moves the values to the "
                 "preferences; none of it writes to the table, so a value there can be older than "
                 "the preferences and need not be current. The encoding of a stored service hash "
                 "was not established. The is_password_hint_enabled, is_in_fake_password_mode_now "
                 "and incorrect_password_entry_amount preferences are not reported. In the real "
                 "extraction protection_type was -1, show_lock_screen was false, none of "
                 "password_hint, password_hash and fake_password_hash was present and the service "
                 "table had no rows, so Password Hint, Password Hash (hex), Fake Password Hash "
                 "(hex), Service Table Protection Type and Service Table Password Hash were blank "
                 "on its 1 row. Key Source names where the data key "
                 "that decrypts this app data folder's notes was read from, blank when no notes.db "
                 "was found beside it. "
                 "The data key is AES-128-CBC encrypted (zero IV, PKCS7) under a key built into "
                 "the app, the XOR of two 16-byte constants, and is read from the dek column of "
                 "the service_data table in notes.db or from the encryption_key string in "
                 "shared_prefs/protected_notes_preferences.xml. Where both exist, the one that "
                 "decrypts the container's own notes or passwords is used; see Key Source in "
                 "Private Notepad - App Settings. Text fields are base64 of AES-128-CBC "
                 "ciphertext under the data key with a zero IV and PKCS7 padding. Each database "
                 "is read with the preferences file from the same app data folder and Android "
                 "user. A field that does not decrypt is reported as stored (base64) and the "
                 "failure is logged. Only live rows are read: records in freed database pages "
                 "are not recovered. Times are stored in milliseconds and reported in UTC; a "
                 "time stored as NULL or 0 is blank. Run on one real extraction (app 6.9.1, "
                 "versionCode 108, Android 14), whose database has no service_data table; the "
                 "6.9.1 APK does not name that table either. service_data.dek and app version "
                 "6.11.1 were exercised only on synthetic data.",
        "paths": (
            "*/ru.alexandermalikov.protectednotes/databases/notes.db*",
            "*/ru.alexandermalikov.protectednotes/shared_prefs/protected_notes_preferences.xml",
        ),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

import json
import os
import sqlite3
import xml.etree.ElementTree as ET
from base64 import b64decode
from binascii import Error as Base64Error
from datetime import datetime, timedelta, timezone
from functools import cache

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import scripts.filetype as filetype
from scripts.artifacts.storagePathViews import android_user, canonical_path, unique_files
from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, check_in_media, logfunc,
                               open_sqlite_db_readonly)

PACKAGE = 'ru.alexandermalikov.protectednotes'
DATABASE_NAME = 'notes.db'
PREFERENCES_NAME = 'protected_notes_preferences.xml'

# {folder under files/: the attachment type it holds}; i8.k.q and i8.d.v in the 6.9.1 APK
ATTACHMENT_FOLDERS = {'images': 'Image', 'recordings': 'Audio'}

# The IV is zero filled, for the keys, the text fields and the attachments alike
IV = b'\x00' * 16

# Attachments larger than this are not read into memory
MAX_ATTACHMENT_SIZE = 200 * 1024 * 1024  # 200 MB

PROTECTION_TYPES = {'-1': 'Disabled', '0': 'Password', '1': 'PIN', '2': 'Pattern'}

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


@cache
def get_static_key():
    """The key the app builds in: the XOR of two 16-byte constants."""
    part_1 = b64decode('1LcQ+TqXEYT0ZrvM05qqSA==')
    part_2 = b64decode('NdVVT3anQR5ne2RR90HqIw==')
    return bytes(a ^ b for a, b in zip(part_1, part_2))


def aes_cbc_decrypt(key, data):
    return unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(data), AES.block_size)


def decrypt_field(key, stored, label, ident):
    """The decrypted text, or the stored value when it does not decrypt."""
    if not stored:
        return stored
    try:
        return aes_cbc_decrypt(key, b64decode(stored)).decode('utf-8')
    except (Base64Error, ValueError) as e:
        # ValueError covers bad padding, a length that is not a block multiple and bad UTF-8
        logfunc(f'Private Notepad: {label} of {ident} did not decrypt ({e}); reported as stored')
        return stored


def convert_ms_to_utc(ts):
    if not ts:
        return None
    return _UNIX_EPOCH_UTC + timedelta(milliseconds=int(ts))


def file_name(path):
    return str(path).replace('\\', '/').rsplit('/', 1)[-1]


def container_key(context, path):
    """The app data folder a path belongs to, the same for every storage view of it."""
    key, _rank = canonical_path(context.get_relative_path(path))
    return key.partition(f'/{PACKAGE}/')[0]


def get_preferences(prefs_path):
    """{key name: (tag, value)} of the preferences file, or None when it does not parse."""
    try:
        xml_root = ET.parse(prefs_path).getroot()
    except (ET.ParseError, OSError) as e:
        logfunc(f'Private Notepad: unable to parse {prefs_path}: {e}')
        return None
    if xml_root.tag != 'map':
        logfunc(f'Private Notepad: root of {prefs_path} is not map')
        return None
    values = {}
    for element in xml_root:
        name = element.get('name')
        if name is not None:
            values[name] = (element.tag, element.get('value', element.text))
    return values


def preference(prefs, name):
    """The stored value of a preference, or None when the file does not hold it."""
    return prefs.get(name, (None, None))[1]


def table_columns(db, table):
    try:
        return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    except sqlite3.Error:
        return set()


def select_columns(db, table, wanted):
    """Rows of table with the wanted columns in order, NULL for those it lacks."""
    present = table_columns(db, table)
    if not present:
        return None
    columns = ', '.join(f'"{c}"' if c in present else 'NULL' for c in wanted)
    return db.execute(f'SELECT {columns} FROM "{table}"').fetchall()


class Container:
    """One app data folder of the app: its database, preferences, attachments and data key."""

    def __init__(self):
        self.db_path = None
        self.prefs_path = None
        # {attachment type: {file name: path}}
        self.attachment_files = {attachment_type: {} for attachment_type in ATTACHMENT_FOLDERS.values()}
        self.user = ''
        self.key = None
        self.key_source = ''


def get_containers(context):
    """[Container] from the matched files, one for each app data folder."""
    containers = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        _before, segment, inside = relative.partition(f'/{PACKAGE}/')
        if not segment:
            continue
        parts = inside.split('/')
        user = android_user(relative)
        attachment_type = None
        # Android/data can hold a folder of the same name, but it is no app data folder and names no user
        if user and len(parts) == 3 and parts[0] == 'files':
            attachment_type = ATTACHMENT_FOLDERS.get(parts[1])
        is_database = parts == ['databases', DATABASE_NAME]
        is_preferences = parts == ['shared_prefs', PREFERENCES_NAME]
        if not (is_database or is_preferences or attachment_type):
            continue
        container = containers.setdefault(container_key(context, file_found), Container())
        container.user = user
        if is_database:
            container.db_path = file_found
        elif is_preferences:
            container.prefs_path = file_found
        else:
            container.attachment_files[attachment_type][parts[2]] = file_found
    return list(containers.values())


def sample_ciphertext(db):
    """A stored encrypted text field to test a candidate data key on, or None."""
    for table, columns in (('notes', ('title', 'note')),
                           ('passwords', ('password_name', 'password_login', 'password_password'))):
        rows = select_columns(db, table, columns) or []
        for row in rows:
            for value in row:
                if value:
                    return value
    return None


def resolve_key(container, db, static_key):
    """Set the container's data key from the first candidate that decrypts its data."""
    candidates = []
    if db is not None:
        try:
            for (dek,) in db.execute('SELECT dek FROM service_data'):
                candidates.append(('service_data.dek', dek))
        except sqlite3.Error:
            pass
    if container.prefs_path:
        prefs = get_preferences(container.prefs_path) or {}
        stored = prefs.get('encryption_key', (None, None))[1]
        if stored:
            candidates.append(('encryption_key preference', stored))

    sample = sample_ciphertext(db) if db is not None else None
    unwrapped = []
    for source, stored in candidates:
        try:
            key = aes_cbc_decrypt(static_key, b64decode(str(stored).strip()))
        except (Base64Error, ValueError) as e:
            logfunc(f'Private Notepad: data key from {source} did not decrypt: {e}')
            continue
        if len(key) not in (16, 24, 32):
            logfunc(f'Private Notepad: data key from {source} is {len(key)} bytes; not used')
            continue
        unwrapped.append((source, key))
        if sample is None:
            continue
        try:
            aes_cbc_decrypt(key, b64decode(sample)).decode('utf-8')
        except (Base64Error, ValueError):
            logfunc(f'Private Notepad: data key from {source} does not decrypt the notes; trying the next')
            continue
        container.key_source, container.key = source, key
        return
    if unwrapped and sample is None:
        # Nothing stored to test against; the first key that unwraps is all there is
        container.key_source, container.key = unwrapped[0]
        return
    logfunc(f'Private Notepad: no data key found for {container.db_path or container.prefs_path}')


def open_container(container, static_key):
    """The container's database opened read-only with its data key resolved, or None."""
    if container.db_path is None:
        logfunc(f'Private Notepad: no {DATABASE_NAME} beside {container.prefs_path or "the attachment files"}')
        return None
    db = open_sqlite_db_readonly(container.db_path)
    if db is None:
        return None
    resolve_key(container, db, static_key)
    if container.key is None:
        db.close()
        return None
    return db


def read_service_table(db_path):
    """(protection_type, password_hash) of the first row of the service table, as stored.

    Opened apart from the data key: these values are not encrypted, so they are read even
    when no key is found. (None, None) without a database, a table or a row.
    """
    db = open_sqlite_db_readonly(db_path) if db_path else None
    if db is None:
        return None, None
    try:
        rows = select_columns(db, 'service', ('protection_type', 'password_hash'))
    except sqlite3.Error as e:
        logfunc(f'Private Notepad: unable to read the service table of {db_path}: {e}')
        return None, None
    finally:
        db.close()
    return rows[0] if rows else (None, None)


def protection_label(stored):
    """A stored protection type as its label with the number in brackets, or None."""
    if stored is None:
        return None
    return f'{PROTECTION_TYPES.get(str(stored), "Unknown")} ({stored})'


def hash_as_hex(stored):
    """A stored base64 hash as hex, or as stored when it is not base64."""
    if not stored:
        return stored
    try:
        return b64decode(stored.strip()).hex()
    except Base64Error:
        return stored


def file_name_time(name):
    """The UTC time a file name holds as milliseconds before its extension, or None."""
    stem = os.path.splitext(name)[0]
    if not stem.isdigit():
        return None
    try:
        return convert_ms_to_utc(stem)
    except (ValueError, OverflowError):
        return None


def attachment_ids(stored):
    """The ids in an images or audio_files value: every string in the lists of its JSON object."""
    if not stored:
        return []
    try:
        value = json.loads(stored)
    except (TypeError, ValueError):
        logfunc(f'Private Notepad: attachment list is not JSON: {stored!r}')
        return []
    lists = value.values() if isinstance(value, dict) else [value]
    return [str(i) for ids in lists if isinstance(ids, list) for i in ids if i not in (None, '')]


def decrypt_attachment(key, path):
    """The decrypted bytes of an attachment file, or None."""
    try:
        if os.path.getsize(path) > MAX_ATTACHMENT_SIZE:
            logfunc(f'Private Notepad: {path} is larger than {MAX_ATTACHMENT_SIZE} bytes; not read')
            return None
        with open(path, 'rb') as f:
            return aes_cbc_decrypt(key, f.read())
    except (OSError, ValueError):
        return None


def check_in_attachment(path, data):
    kind = filetype.guess(data)
    if kind:
        return check_in_embedded_media(path, data, file_name(path),
                                       force_type=kind.mime, force_extension=kind.extension)
    return check_in_embedded_media(path, data, file_name(path))


def note_attachments(container, db):
    """[(note row, [(type, id, path or None)])] for every note of the container."""
    rows = select_columns(db, 'notes', ('_id', 'date', 'date_created', 'date_delete', 'title', 'note',
                                         'images', 'audio_files'))
    if rows is None:
        logfunc(f'Private Notepad: no notes table in {container.db_path}')
        return []
    result = []
    for row in rows:
        attachments = []
        for attachment_type, stored in (('Image', row[6]), ('Audio', row[7])):
            for attachment_id in attachment_ids(stored):
                attachments.append((attachment_type, attachment_id,
                                    container.attachment_files[attachment_type].get(attachment_id)))
        result.append((row, attachments))
    return result


@artifact_processor
def private_notepad_notes(context):
    data_list = []
    sources = []
    static_key = get_static_key()

    for container in get_containers(context):
        db = open_container(container, static_key)
        if db is None:
            continue
        try:
            notes = note_attachments(container, db)
        except sqlite3.Error as e:
            logfunc(f'Private Notepad: unable to read notes from {container.db_path}: {e}')
            continue
        finally:
            db.close()

        sources.append(container.db_path)
        if container.prefs_path:
            sources.append(container.prefs_path)
        source = context.get_relative_path(container.db_path)
        for (pk, date, date_created, date_delete, title, note, _images, _audio), attachments in notes:
            media = []
            for _type, _id, path in attachments:
                data = decrypt_attachment(container.key, path) if path else None
                if data:
                    media.append(check_in_attachment(path, data))
            media = [ref for ref in media if ref]
            data_list.append((
                convert_ms_to_utc(date),
                convert_ms_to_utc(date_created),
                convert_ms_to_utc(date_delete),
                decrypt_field(container.key, title, 'title', f'note {pk}'),
                decrypt_field(container.key, note, 'body', f'note {pk}'),
                media or None,
                pk,
                source,
            ))

    data_headers = (('Date', 'datetime'), ('Created', 'datetime'), ('Delete Date', 'datetime'), 'Title',
                    'Body', ('Attachments', 'media'), 'Note ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def private_notepad_attachments(context):
    data_list = []
    sources = []
    static_key = get_static_key()

    for container in get_containers(context):
        db = open_container(container, static_key)
        if db is None:
            continue
        try:
            notes = note_attachments(container, db)
        except sqlite3.Error as e:
            logfunc(f'Private Notepad: unable to read notes from {container.db_path}: {e}')
            continue
        finally:
            db.close()

        sources.append(container.db_path)
        source = context.get_relative_path(container.db_path)
        named = set()
        for (pk, date, _created, _deleted, title, _note, _images, _audio), attachments in notes:
            title = decrypt_field(container.key, title, 'title', f'note {pk}')
            for attachment_type, attachment_id, path in attachments:
                if path is None:
                    data_list.append((convert_ms_to_utc(date), None, 'File not found', attachment_type,
                                      attachment_id, pk, title, '', source))
                    continue
                named.add(path)
                sources.append(path)
                data = decrypt_attachment(container.key, path)
                media = check_in_attachment(path, data) if data else None
                status = 'Decrypted' if data else 'Not decrypted'
                data_list.append((convert_ms_to_utc(date), media, status, attachment_type, attachment_id,
                                  pk, title, context.get_relative_path(path), source))

        for attachment_type, files in container.attachment_files.items():
            for name, path in files.items():
                if path in named:
                    continue
                sources.append(path)
                data = decrypt_attachment(container.key, path)
                media = check_in_attachment(path, data) if data else None
                data_list.append((None, media, 'Not named by a note', attachment_type, name, '', '',
                                  context.get_relative_path(path), source))

    data_headers = (('Note Date', 'datetime'), ('Attachment', 'media'), 'Status', 'Attachment Type',
                    'Attachment ID', 'Note ID', 'Note Title', 'Attachment File', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def private_notepad_intruder_photos(context):
    data_list = []
    sources = []

    for file_found in unique_files(context):
        file_found = str(file_found)
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        user = android_user(relative)
        parts = relative.partition(f'/{PACKAGE}/')[2].split('/')
        # Android/data can hold a folder of the same name, but it is no app data folder and names no user
        if not user or len(parts) != 3 or parts[:2] != ['files', 'intruder_photos']:
            continue
        name = parts[2]
        sources.append(file_found)
        kind = filetype.guess(file_found)
        if kind and kind.mime.startswith('image/'):
            media = check_in_media(file_found, name, force_type=kind.mime, force_extension=kind.extension)
            status = 'Image'
        else:
            logfunc(f'Private Notepad: {file_found} is not a recognised image')
            media = None
            status = 'Not a recognised image'
        data_list.append((file_name_time(name), media, status, name, user, context.get_relative_path(file_found)))

    data_headers = (('File Name Time', 'datetime'), ('Photo', 'media'), 'Status', 'File Name', 'Android User',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def private_notepad_passwords(context):
    data_list = []
    sources = []
    static_key = get_static_key()

    for container in get_containers(context):
        db = open_container(container, static_key)
        if db is None:
            continue
        try:
            rows = select_columns(db, 'passwords', ('_id', 'date_created', 'password_name', 'password_login',
                                                    'password_password', 'password_site_address',
                                                    'password_comment'))
        except sqlite3.Error as e:
            logfunc(f'Private Notepad: unable to read passwords from {container.db_path}: {e}')
            continue
        finally:
            db.close()
        if rows is None:
            logfunc(f'Private Notepad: no passwords table in {container.db_path}')
            continue

        sources.append(container.db_path)
        if container.prefs_path:
            sources.append(container.prefs_path)
        source = context.get_relative_path(container.db_path)
        for pk, date_created, *fields in rows:
            name, login, password, site, comment = (
                decrypt_field(container.key, value, label, f'password {pk}')
                for value, label in zip(fields, ('name', 'login', 'password', 'site address', 'comment')))
            data_list.append((convert_ms_to_utc(date_created), name, login, password, site, comment, pk, source))

    data_headers = (('Created', 'datetime'), 'Name', 'Login', 'Password', 'Site Address', 'Comment',
                    'Password ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def private_notepad_settings(context):
    data_list = []
    sources = []
    static_key = get_static_key()

    for container in get_containers(context):
        service_type, service_hash = read_service_table(container.db_path)
        has_service_values = service_type is not None or service_hash is not None
        prefs = get_preferences(container.prefs_path) if container.prefs_path else None
        if prefs is None and not has_service_values:
            continue
        prefs = prefs or {}
        if container.db_path:
            db = open_container(container, static_key)
            if db is not None:
                db.close()

        last_usage = preference(prefs, 'last_app_usage_time')
        try:
            last_usage = convert_ms_to_utc(last_usage)
        except ValueError:
            pass

        if container.prefs_path:
            sources.append(container.prefs_path)
        if has_service_values:
            sources.append(container.db_path)
        data_list.append((last_usage, preference(prefs, 'show_lock_screen'),
                          protection_label(preference(prefs, 'protection_type')),
                          preference(prefs, 'password_hint'), hash_as_hex(preference(prefs, 'password_hash')),
                          hash_as_hex(preference(prefs, 'fake_password_hash')),
                          container.key_source, container.user,
                          protection_label(service_type), service_hash,
                          context.get_relative_path(container.prefs_path or container.db_path)))

    data_headers = (('Last App Usage Time', 'datetime'), 'Show Lock Screen (as stored)', 'Protection Type',
                    'Password Hint', 'Password Hash (hex)', 'Fake Password Hash (hex)', 'Key Source',
                    'Android User',
                    'Service Table Protection Type', 'Service Table Password Hash (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
