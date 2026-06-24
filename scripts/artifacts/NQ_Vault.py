__artifacts_v2__ = {
    "get_NQVault": {
        "name": "NQ Vault Decrypted PINs",
        "description": "Recovers NQ Vault (com.netqin.ps) PINs by reversing the stored Java hashcode",
        "author": "",
        "creation_date": "2023-05-19",
        "last_update_date": "2023-05-19",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "",
        "paths": ('*/emulated/0/Android/data/com.netqin.ps/files/Documents/SystemAndroid/Data/322w465ay423xy11',
                  '*/SystemAndroid/Data/**', '/media/0/SystemAndroid/Data/322w465ay423xy11'),
        "output_types": "standard",
        "artifact_icon": "key",
    },
    "get_NQVault_media": {
        "name": "NQ Vault Decrypted Media",
        "description": "Decrypts media hidden by NQ Vault (com.netqin.ps) using the recovered PIN XOR key",
        "author": "",
        "creation_date": "2023-05-19",
        "last_update_date": "2023-05-19",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "",
        "paths": ('*/emulated/0/Android/data/com.netqin.ps/files/Documents/SystemAndroid/Data/322w465ay423xy11',
                  '*/SystemAndroid/Data/**', '/media/0/SystemAndroid/Data/322w465ay423xy11'),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import datetime
import functools
import itertools
import sqlite3
import string
from pathlib import Path

import scripts.filetype as filetype
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, check_in_embedded_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def java_string_hashcode(pin):
    hashcode_init = 0
    for char in pin:
        hashcode_init = (31 * hashcode_init + ord(char)) & 0xFFFFFFFF
    return ((hashcode_init + 0x80000000) & 0xFFFFFFFF) - 0x80000000


@functools.lru_cache(maxsize=None)
def brute_force_pin(encoded_pin):
    # Previously identified PINs (instant)
    known = {'1509442': 1234, '1477632': 0, '-1867378635': 123456789, '-1812067894': 25101988}
    if encoded_pin in known:
        return known[encoded_pin]
    logfunc('PIN hash identified - brute forcing 3-15 digit PINs (long PINs can take a while).')
    for pin_len in range(3, 16):
        for numbers in itertools.product(string.digits, repeat=pin_len):
            pin = ''.join(numbers)
            if str(java_string_hashcode(pin)) == encoded_pin:
                return pin
    return None


def raw_pin_to_xor_key(pin):
    return hex(java_string_hashcode(str(pin)) & 0xFF)


def _extract_data_from_db(file_found):
    try:
        connection = open_sqlite_db_readonly(file_found)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT file_path_from, file_name_from, file_path_new, [time],
                   TIME([viode_time] / 1000, 'unixepoch'), resolution,
                   albums.album_name, albumstemp.album_name_temp, password_id
            FROM hideimagevideo
            LEFT OUTER JOIN albums ON hideimagevideo.album_id = albums._id
            LEFT OUTER JOIN albumstemp ON hideimagevideo.album_id = albumstemp.album_temp_id
        ''')
        db_data = cursor.fetchall()
        connection.close()
    except (sqlite3.Error, OSError, ValueError, TypeError, AttributeError, IndexError, KeyError):
        return {}, [], ''

    dict_of_file_info = {}
    enc_pins = []
    for entry in db_data:
        encrypted_filename = str(entry[2]).split('/')[-1]
        dict_of_file_info[encrypted_filename] = {
            'old_filepath': entry[0], 'old_filename': entry[1], 'vault_filepath': entry[2],
            'timestamp': _ms_to_utc(entry[3]), 'vid_length': entry[4], 'resolution': entry[5],
            'alb_name': entry[6], 'prev_alb_name': entry[7], 'password_id': entry[8],
        }
        if entry[8] not in enc_pins:
            enc_pins.append(entry[8])
    return dict_of_file_info, enc_pins, file_found


def _load_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('322w465ay423xy11'):
            dict_of_file_info, enc_pins, db_path = _extract_data_from_db(file_found)
            if db_path:
                return dict_of_file_info, enc_pins, db_path
    return {}, [], ''


@artifact_processor
def get_NQVault(context):
    _, enc_pins, db_path = _load_db(context.get_files_found())
    data_list = [(encoded_pin, brute_force_pin(encoded_pin)) for encoded_pin in enc_pins]
    data_headers = ('Encrypted PIN', 'Decrypted PIN')
    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def get_NQVault_media(context):
    files_found = context.get_files_found()
    dict_of_file_info, enc_pins, db_path = _load_db(files_found)
    pin_xor = {pin: (raw_pin_to_xor_key(brute_force_pin(pin)), brute_force_pin(pin)) for pin in enc_pins}

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not (file_found.endswith('.bin') and ('.image' in file_found or '.video' in file_found)):
            continue
        stem = Path(file_found).stem
        for enc_filename, info in dict_of_file_info.items():
            if enc_filename.split('.')[0] != stem:
                continue
            pin_info = pin_xor.get(info['password_id'])
            if not pin_info or not pin_info[0]:
                continue
            xor_key, pin_code = pin_info
            key = int(xor_key, 16)

            with open(file_found, 'rb') as f:
                raw = f.read()
            # Only the first 128 bytes are XOR-obfuscated
            decrypted = bytes((b ^ key) if i < 128 else b for i, b in enumerate(raw))

            kind = filetype.guess(decrypted)
            name = info['old_filename'] or f'{stem}.bin'
            if kind:
                thumb = check_in_embedded_media(file_found, decrypted, name,
                                                force_type=kind.mime, force_extension=kind.extension)
            else:
                thumb = check_in_embedded_media(file_found, decrypted, name)

            encrypted_file_name = Path(info['vault_filepath']).stem + '.bin'
            data_list.append((thumb, info['old_filename'], info['old_filepath'], encrypted_file_name,
                              context.get_relative_path(file_found), info['timestamp'], info['vid_length'], info['resolution'],
                              info['alb_name'], info['prev_alb_name'], pin_code, info['password_id']))

    data_headers = (
        ('Media', 'media'), 'Original Filename', 'Original Filepath', 'Encrypted Filename', 'Full Path',
        ('Timestamp', 'datetime'), 'Video Length', 'File Resolution', 'Album Name', 'Previous Album Name',
        'Password', 'Password Hash')
    return data_headers, data_list, context.get_relative_path(db_path)
