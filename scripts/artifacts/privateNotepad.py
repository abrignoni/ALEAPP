# Script for parsing ru.alexandermalikov.protectednotes
# version 1.0, distributed under the notice below.
# This is an altered version: it was rewritten for ALEAPP and is not the original software.
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

__artifacts_v2__ = {
    "private_notepad_notes": {
        "name": "Private Notepad - Notes",
        "description": "Notes from Private Notepad - safe notes "
                       "(ru.alexandermalikov.protectednotes), with the title, body and "
                       "attachments decrypted",
        "author": "Jens Grønhøj Stigaard, Claude",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-03",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per row of the notes table in "
                 "ru.alexandermalikov.protectednotes/databases/notes.db. Date, Created and Delete "
                 "Date are the date, date_created and date_delete columns as stored; which events "
                 "set them was not established from the app's code. A column the database does "
                 "not have, such as date_created in 6.9.1 if absent there, is blank. Attachments "
                 "shows the decrypted image and audio files the note's images and audio_files "
                 "columns name; see Private Notepad - Note Attachments for how they are found "
                 "and for the ones that were not. "
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
                 "time stored as NULL or 0 is blank. Tested only on synthetic data built with "
                 "the scheme of app versions 6.9.1 and 6.11.1.",
        "paths": ("*/ru.alexandermalikov.protectednotes/*",),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "private_notepad_attachments": {
        "name": "Private Notepad - Note Attachments",
        "description": "Image and audio attachments of Private Notepad notes, decrypted",
        "author": "Jens Grønhøj Stigaard, Claude",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-03",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per attachment id in the images and audio_files columns of the notes "
                 "table, each a JSON object whose lists hold the ids, and one row per file the "
                 "note does not name. An id is matched to a file of the same Android user under a "
                 "ru.alexandermalikov.protectednotes folder, in app data or in shared storage "
                 "under Android/data, whose name equals the id or, failing that, contains it; "
                 "which folder the app writes attachments to was not "
                 "established. Every matching file is a row. Files are decrypted whole with the "
                 "data key and the media type is taken from the decrypted bytes. Status reads "
                 "Decrypted, Not decrypted (the file did not decrypt under the data key), File "
                 "not found (no file in the extraction carries the id; this is not evidence the "
                 "attachment never existed) or Not named by a note. A file is reported as Not "
                 "named by a note only when it decrypts under the data key and its bytes are a "
                 "recognised media type; other files in the app's folders are not reported. "
                 "Attachment Type is the column the id came from. "
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
                 "time stored as NULL or 0 is blank. Tested only on synthetic data built with "
                 "the scheme of app versions 6.9.1 and 6.11.1.",
        "paths": ("*/ru.alexandermalikov.protectednotes/*",),
        "output_types": "standard",
        "artifact_icon": "paperclip",
    },
    "private_notepad_passwords": {
        "name": "Private Notepad - Passwords",
        "description": "Password entries stored in Private Notepad, decrypted",
        "author": "Jens Grønhøj Stigaard, Claude",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-03",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per row of the passwords table in notes.db; a database without the "
                 "table yields no rows and logs it. Name, Login, Password, Site Address and "
                 "Comment are the password_name, password_login, password_password, "
                 "password_site_address and password_comment columns decrypted. Created is "
                 "date_created as stored. "
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
                 "time stored as NULL or 0 is blank. Tested only on synthetic data built with "
                 "the scheme of app versions 6.9.1 and 6.11.1.",
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
        "author": "Jens Grønhøj Stigaard, Claude",
        "creation_date": "2026-11-03",
        "last_update_date": "2026-11-03",
        "requirements": "none",
        "category": "Private Notepad",
        "notes": "One row per protected_notes_preferences.xml. Values are the preference keys "
                 "last_app_usage_time, show_lock_screen, protection_type, password_hint and "
                 "password_hash. A key the file does not hold is blank; the app's default then "
                 "applies, and what that default is was not established. Protection Type labels "
                 "(-1 Disabled, 0 Password, 1 PIN, 2 Pattern) were not verified here; any other "
                 "value reads Unknown. The stored number is kept in brackets. Password Hash is "
                 "the base64 value decoded to hex; the hash algorithm and whether it is salted "
                 "were not established. Key Source names where the data key that decrypts this "
                 "app data folder's notes was read from, blank when no notes.db was found "
                 "beside it. "
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
                 "time stored as NULL or 0 is blank. Tested only on synthetic data built with "
                 "the scheme of app versions 6.9.1 and 6.11.1.",
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
import re
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
from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media, is_sqlite_sidecar, logfunc,
                               open_sqlite_db_readonly)

PACKAGE = 'ru.alexandermalikov.protectednotes'
DATABASE_NAME = 'notes.db'
PREFERENCES_NAME = 'protected_notes_preferences.xml'

# The IV is zero filled, for the keys, the text fields and the attachments alike
IV = b'\x00' * 16

# Attachments larger than this are not read into memory
MAX_ATTACHMENT_SIZE = 200 * 1024 * 1024  # 200 MB

PROTECTION_TYPES = {'-1': 'Disabled', '0': 'Password', '1': 'PIN', '2': 'Pattern'}

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_SHARED_STORAGE_USER = re.compile(r'(?:^|/)(?:data/media|media|storage/emulated)/(\d+)/Android/data/')
_SDCARD = re.compile(r'(?:^|/)sdcard/Android/data/')


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


def storage_user(context, path):
    """The Android user whose app data or shared storage holds path, or ''."""
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    match = _SHARED_STORAGE_USER.search(relative)
    if match:
        return match.group(1)
    if _SDCARD.search(relative):
        return '0'
    return android_user(relative)


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
    """One app data folder of the app: its database, preferences and data key."""

    def __init__(self):
        self.db_path = None
        self.prefs_path = None
        self.user = ''
        self.key = None
        self.key_source = ''


def get_containers(context):
    """([Container], {Android user: [attachment candidate path]}) from the matched files."""
    containers = {}
    candidates = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        name = file_name(file_found)
        _before, segment, inside = str(context.get_relative_path(file_found)).replace('\\', '/').partition(
            f'/{PACKAGE}/')
        if not segment:
            continue
        top_folder = inside.split('/', 1)[0]
        if name == DATABASE_NAME and top_folder == 'databases':
            containers.setdefault(container_key(context, file_found), Container()).db_path = file_found
        elif name == PREFERENCES_NAME and top_folder == 'shared_prefs':
            containers.setdefault(container_key(context, file_found), Container()).prefs_path = file_found
        elif top_folder not in ('databases', 'shared_prefs') and not is_sqlite_sidecar(file_found):
            candidates.setdefault(storage_user(context, file_found), []).append(file_found)
    for container in containers.values():
        container.user = storage_user(context, container.db_path or container.prefs_path)
    return list(containers.values()), candidates


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
        logfunc(f'Private Notepad: no {DATABASE_NAME} beside {container.prefs_path}')
        return None
    db = open_sqlite_db_readonly(container.db_path)
    if db is None:
        return None
    resolve_key(container, db, static_key)
    if container.key is None:
        db.close()
        return None
    return db


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


def find_attachment_files(attachment_id, candidates):
    """The candidate files named attachment_id or, failing that, whose name contains it."""
    exact = [path for path in candidates if file_name(path) == attachment_id]
    return exact or [path for path in candidates if attachment_id in file_name(path)]


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


def note_attachments(container, db, candidates):
    """[(note row, [(type, id, [paths])])] for every note of the container."""
    rows = select_columns(db, 'notes', ('_id', 'date', 'date_created', 'date_delete', 'title', 'note',
                                         'images', 'audio_files'))
    if rows is None:
        logfunc(f'Private Notepad: no notes table in {container.db_path}')
        return []
    user_candidates = candidates.get(container.user, [])
    result = []
    for row in rows:
        attachments = []
        for attachment_type, stored in (('Image', row[6]), ('Audio', row[7])):
            for attachment_id in attachment_ids(stored):
                attachments.append((attachment_type, attachment_id,
                                    find_attachment_files(attachment_id, user_candidates)))
        result.append((row, attachments))
    return result


@artifact_processor
def private_notepad_notes(context):
    data_list = []
    sources = []
    static_key = get_static_key()
    containers, candidates = get_containers(context)

    for container in containers:
        db = open_container(container, static_key)
        if db is None:
            continue
        try:
            notes = note_attachments(container, db, candidates)
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
            for _type, _id, paths in attachments:
                for path in paths:
                    data = decrypt_attachment(container.key, path)
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
    containers, candidates = get_containers(context)

    for container in containers:
        db = open_container(container, static_key)
        if db is None:
            continue
        try:
            notes = note_attachments(container, db, candidates)
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
            for attachment_type, attachment_id, paths in attachments:
                if not paths:
                    data_list.append((convert_ms_to_utc(date), None, 'File not found', attachment_type,
                                      attachment_id, pk, title, '', source))
                    continue
                for path in paths:
                    named.add(path)
                    sources.append(path)
                    data = decrypt_attachment(container.key, path)
                    media = check_in_attachment(path, data) if data else None
                    status = 'Decrypted' if data else 'Not decrypted'
                    data_list.append((convert_ms_to_utc(date), media, status, attachment_type, attachment_id,
                                      pk, title, context.get_relative_path(path), source))

        for path in candidates.get(container.user, []):
            if path in named:
                continue
            data = decrypt_attachment(container.key, path)
            if not data or not filetype.guess(data):
                continue
            sources.append(path)
            data_list.append((None, check_in_attachment(path, data), 'Not named by a note', '', '', '', '',
                              context.get_relative_path(path), source))

    data_headers = (('Note Date', 'datetime'), ('Attachment', 'media'), 'Status', 'Attachment Type',
                    'Attachment ID', 'Note ID', 'Note Title', 'Attachment File', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def private_notepad_passwords(context):
    data_list = []
    sources = []
    static_key = get_static_key()
    containers, _candidates = get_containers(context)

    for container in containers:
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
    containers, _candidates = get_containers(context)

    for container in containers:
        if container.prefs_path is None:
            continue
        prefs = get_preferences(container.prefs_path)
        if prefs is None:
            continue
        if container.db_path:
            db = open_container(container, static_key)
            if db is not None:
                db.close()

        def value(name, prefs=prefs):
            return prefs.get(name, (None, None))[1]

        last_usage = value('last_app_usage_time')
        try:
            last_usage = convert_ms_to_utc(last_usage)
        except ValueError:
            pass
        protection_type = value('protection_type')
        if protection_type is not None:
            protection_type = f'{PROTECTION_TYPES.get(protection_type, "Unknown")} ({protection_type})'
        password_hash = value('password_hash')
        if password_hash:
            try:
                password_hash = b64decode(password_hash.strip()).hex()
            except Base64Error:
                pass

        sources.append(container.prefs_path)
        data_list.append((last_usage, value('show_lock_screen'), protection_type, value('password_hint'),
                          password_hash, container.key_source, container.user,
                          context.get_relative_path(container.prefs_path)))

    data_headers = (('Last App Usage Time', 'datetime'), 'Show Lock Screen (as stored)', 'Protection Type',
                    'Password Hint', 'Password Hash (hex)', 'Key Source', 'Android User', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
