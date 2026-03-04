import itertools
import re
import string
import sqlite3
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, media_to_html, open_sqlite_db_readonly


def sanitize_output_filename(filename, default_name='recovered_file.bin'):
    raw_name = str(filename or '')
    normalized = raw_name.replace('\\', '/')
    safe_name = Path(normalized).name
    safe_name = re.sub(r'[\x00-\x1f<>:"/\\|?*]+', '_', safe_name)
    safe_name = safe_name.strip().strip('.')
    if not safe_name:
        return default_name
    return safe_name


def build_safe_output_path(report_folder, original_filename):
    report_root = Path(report_folder).resolve()
    sanitized_name = sanitize_output_filename(original_filename)
    output_path = (report_root / sanitized_name).resolve()
    try:
        output_path.relative_to(report_root)
    except ValueError:
        output_path = report_root / sanitize_output_filename(None)

    if output_path.exists():
        stem = output_path.stem
        suffix = output_path.suffix
        index = 1
        while True:
            candidate = report_root / f'{stem}_{index}{suffix}'
            if not candidate.exists():
                output_path = candidate
                break
            index += 1
    return output_path


def extract_data_from_db(file_found):
    dict_of_dicts = {}
    list_of_enc_pins = []
    try:
        connection = open_sqlite_db_readonly(file_found)
        set_pointer = connection.cursor()
        set_pointer.execute('''SELECT 
       [file_path_from], 
       [file_name_from], 
       [file_path_new], 
       DATETIME ([time] / 1000, 'unixepoch'), 
       TIME ([viode_time] / 1000, 'unixepoch'), 
       [resolution], 
       [albums].[album_name], 
       [albumstemp].[album_name_temp], 
       [password_id]
        FROM   [hideimagevideo]
       LEFT OUTER JOIN [albums] ON [hideimagevideo].[album_id] = [albums].[_id]
       LEFT OUTER JOIN [albumstemp] ON [hideimagevideo].[album_id] = [albumstemp].[album_temp_id];''')

        db_data = set_pointer.fetchall()
        connection.close()

        for entry in db_data:
            encrypted_filename = entry[2].split('/')[-1]
            new_dict = {}
            new_dict['old_filepath'] = entry[0]
            new_dict['old_filename'] = entry[1]
            new_dict['vault_filepath'] = entry[2]
            new_dict['timestamp'] = entry[3]
            new_dict['vid_length'] = entry[4]
            new_dict['resolution'] = entry[5]
            new_dict['alb_name'] = entry[6]
            new_dict['prev_alb_name'] = entry[7]
            new_dict['password_id'] = entry[8]

            if entry[8] not in list_of_enc_pins:
                list_of_enc_pins.append(entry[8])

            dict_of_dicts[encrypted_filename] = new_dict

        return dict_of_dicts, list_of_enc_pins, file_found
    except (sqlite3.Error, OSError, ValueError, TypeError, AttributeError, IndexError, KeyError):
        return None


def brute_force_pin(encoded_PIN):
    decoded_PIN = None

    pin_len = 3
    logfunc('PIN Hash Identified!\nAttempting PINs from 3 - 15 digits. If PIN len > 8/9 it could take some time.\n')
    # earlier PINs that have been identified
    if encoded_PIN == '1509442':
        pin = 1234
        return pin
    elif encoded_PIN == '1477632':
        pin = 0000
        return pin
    elif encoded_PIN == '-1867378635':
        pin = 123456789
        return pin
    elif encoded_PIN == '-1812067894':
        pin = 25101988
        return pin
    else:
        while pin_len <= 15:
            for numbers in itertools.product(string.digits, repeat=pin_len):

                pin = ''.join(numbers)
                decoded_test_value_string = str(java_string_hashcode(pin))

                if decoded_test_value_string == encoded_PIN:
                    #logfunc(f'Decrypted PIN is: {pin}')
                    return pin
            pin_len += 1

        if decoded_PIN is None:
            print('Sorry. No PIN found.')


def java_string_hashcode(pin):
    hashcode_init = 0
    for iters in pin:
        hashcode_init = (31 * hashcode_init + ord(iters)) & 0xFFFFFFFF
    return ((hashcode_init + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def raw_pin_to_XOR_key(pin):
    if not type(pin) == str:
        pin = str(pin)

    hashed_pin = java_string_hashcode(pin)

    int_XOR_key = hashed_pin & 0xFF
    hex_XOR_key = hex(int_XOR_key)

    return hex_XOR_key

def file_decryption(files_found, dict_of_file_info, dict_of_pin_dicts, report_folder):
    data_list = []
    logfunc('Encrypted files found! File Decryption in progress...')

    for file_found in files_found:
        file_found = str(file_found)
        # the parent folder of the files is base 64 encoded password hash
        # could do further validation is required.
        if file_found.endswith('.bin') and ('.image' in file_found or '.video' in file_found):

            filename_without_ext = Path(file_found).stem
            xor_key = ''
            pin_code = None
            for enc_filename, file_info in dict_of_file_info.items():
                if enc_filename.split('.')[0] == filename_without_ext:
                    file_enc_pin = file_info['password_id']

                    # find xor pin from dictionary
                    for encoded_pin, encoded_pin_info in dict_of_pin_dicts.items():
                        if encoded_pin == file_enc_pin:
                            xor_key = encoded_pin_info['xor_key']
                            pin_code = encoded_pin_info['pin_for_XOR_key']

                    if xor_key != 0:
                        key_to_int = int(xor_key, 16)
                        xor_list = []
                        iter_through_initial_bytes = 0
                        decrypted_file_name = file_info['old_filename']
                        encrypted_file_name = Path(file_info['vault_filepath']).stem + '.bin'
                        with open(file_found, 'rb') as file_to_decrypt:
                            byte = file_to_decrypt.read(1)

                            while byte:
                                if iter_through_initial_bytes < 128:
                                    xord_bytes = int(byte.hex(), 16) ^ key_to_int
                                    xor_list.append(xord_bytes)
                                else:
                                    xor_list.append(int(byte.hex(), 16))

                                iter_through_initial_bytes = iter_through_initial_bytes + 1
                                byte = file_to_decrypt.read(1)

                            xord_bytes_decrypted = bytes(xor_list)
                            decrypted_output_path = build_safe_output_path(report_folder, decrypted_file_name)
                            with open(decrypted_output_path, 'wb') as decryptedFile:
                                decryptedFile.write(xord_bytes_decrypted)
                                decryptedFile.close()

                                tolink = []
                                pathdec = str(decrypted_output_path)
                                tolink.append(pathdec)
                                thumb = media_to_html(pathdec, tolink, report_folder)

                                data_list.append((thumb, file_info['old_filename'], file_info['old_filepath'],
                                                  encrypted_file_name,file_found, file_info['timestamp'],
                                                  file_info['vid_length'],file_info['resolution'],file_info['alb_name'],
                                                  file_info['prev_alb_name'],pin_code, file_info['password_id']))
                        logfunc(f'{encrypted_file_name} decrypted.')
                        if data_list:
                            report = ArtifactHtmlReport('NQ Vault Decrypted Media')
                            report.start_artifact_report(report_folder, 'NQ Vault Decrypted Media')
                            report.add_script()
                            data_headers = ('Media', 'Original Filename', 'Original Filepath', 'Encrypted Filename',
                                            'Full Path','Timestamp','Video Length','File Resolution','Album Name',
                                            'Previous Album Name','Password','Password Hash')
                            maindirectory = str(Path(file_found).parents[1])
                            report.write_artifact_data_table(data_headers, data_list, maindirectory,
                                                             html_no_escape=['Media'])
                            report.end_artifact_report()

                            tsvname = 'NQVault'
                            tsv(report_folder, data_headers, data_list, tsvname)


# MAIN #
def get_NQVault(files_found, report_folder, seeker, wrap_text):
    _ = seeker, wrap_text
    data_list = []
    list_of_enc_pins = []
    dict_of_file_info = {}
    dict_of_pin_dicts = {}
    file_found_pin = ''
    success = 0
    # Get the "encrypted" PIN from DB
    for file_found in files_found:
        if file_found.endswith('322w465ay423xy11'):
            # multiple password hashes may be present, so these are stored as a list
            extraction_result = extract_data_from_db(file_found)
            if extraction_result:
                dict_of_file_info, list_of_enc_pins, file_found_pin = extraction_result
                success = 1
    if success == 0:
        logfunc('No Database DB Found or no hashed PIN present.')
        return

    if len(list_of_enc_pins) > 0:
        for encoded_pin in list_of_enc_pins:
            pin_dict = {}
            # Brute-force encrypted PIN
            pin_for_XOR_key = brute_force_pin(encoded_pin)
            # pin_for_XOR_key is decoded PIN
            pin_dict['pin_for_XOR_key'] = pin_for_XOR_key
            data_list.append((encoded_pin, pin_for_XOR_key))

            # Use decrypted PIN to generate correct XOR key for media decryption (if media present).
            xor_key = raw_pin_to_XOR_key(pin_for_XOR_key)
            pin_dict['xor_key'] = xor_key
            dict_of_pin_dicts[encoded_pin] = pin_dict
            logfunc(f'XOR Key generated from encoded PIN of {encoded_pin}: {xor_key}.'
                    f'\nDecrypted PIN: {pin_for_XOR_key}')

        # Write encrypted/decrypted PIN info to report
        report = ArtifactHtmlReport('NQ Vault Decrypted PIN')
        report.start_artifact_report(report_folder, 'NQ Vault Decrypted PIN')
        report.add_script()
        data_headers = ('Encrypted PIN', 'Decrypted PIN')

        report_source = file_found_pin if file_found_pin else 'NQ Vault Source DB'
        report.write_artifact_data_table(data_headers, data_list, report_source, html_no_escape=['Media'])
        report.end_artifact_report()

        # Media decryption funct
        if dict_of_file_info:
            file_decryption(files_found, dict_of_file_info, dict_of_pin_dicts, report_folder)
        else:
            logfunc('No Encrypted Media Present in Database.')
            return
    else:
        logfunc('No Database DB Found or no hashed PIN present.')


__artifacts__ = {
    "NQVault": (
        "Encrypting Media apps",
        ('*/emulated/0/Android/data/com.netqin.ps/files/Documents/SystemAndroid/Data/322w465ay423xy11',
         '*/SystemAndroid/Data/**', '/media/0/SystemAndroid/Data/322w465ay423xy11'),
        get_NQVault)
}
