import itertools
import string
from pathlib import Path
from os.path import join

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, media_to_html, open_sqlite_db_readonly

def extract_PIN_from_db(file_found):
    try:
        connection = open_sqlite_db_readonly(file_found)

        set_pointer = connection.cursor()
        set_pointer.execute("SELECT passwd_temp FROM albumstemp")

        encrypted_password = set_pointer.fetchone()[0]

        return encrypted_password, file_found
    except:
        return None


def brute_force_pin(encoded_PIN):

    decoded_PIN = None

    pin_len = 3
    logfunc('Attempting PINs from 3 - 15 digits. If PIN len > 8/9 it could take some time.\n')
    while pin_len <= 15:
        for numbers in itertools.product(string.digits, repeat=pin_len):

            pin = ''.join(numbers)
            decoded_test_value_string = str(java_string_hashcode(pin))

            if decoded_test_value_string == encoded_PIN:
                logfunc(f'Decrypted PIN is: {pin}')
                return pin
        else:
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


def read_file_info(file_found):
    file_match_dict = {}
    print(f'readfileinfo: {file_found}')
    connection = open_sqlite_db_readonly(file_found)

    set_pointer = connection.cursor()
    set_pointer.execute("SELECT file_name_from, file_path_new FROM hideimagevideo")
    
    required_column = set_pointer.fetchall()

    if len(required_column) < 1:
        logfunc('No encrypted media present')
        return
    else:
        for filename in required_column:
            decrypted_filename = filename[0]
            encrypted_filename = filename[1].split('/')[-1]
    
            file_match_dict[decrypted_filename] = encrypted_filename

    return file_match_dict

def file_decryption(files_found, file_match_dict, xor_key, report_folder):

    data_list = []
    logfunc('Encrypted files found! File Decryption in progress...')

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.bin') and ('.image' in file_found or '.video' in file_found):

            filename_without_ext = Path(file_found).stem

            for decrypted_file_name, encrypted_file_name in file_match_dict.items():
                if encrypted_file_name.split('.')[0] == filename_without_ext:

                    key_to_int = int(xor_key, 16)
                    xor_list = []
                    iter_through_initial_bytes = 0

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

                        with open(join(report_folder, decrypted_file_name), 'wb') as decryptedFile:
                            decryptedFile.write(xord_bytes_decrypted)
                            decryptedFile.close()

                            tolink = []
                            pathdec = join(report_folder, decrypted_file_name)
                            tolink.append(pathdec)
                            thumb = media_to_html(pathdec, tolink, report_folder)
                            filename = decrypted_file_name

                            encrypted_file_name = encrypted_file_name.split('.')[0] + '.bin'
                            data_list.append((thumb, filename, encrypted_file_name, file_found,))

                    if data_list:
                        report = ArtifactHtmlReport('NQ Vault Decrypted Media')
                        report.start_artifact_report(report_folder, 'NQ Vault Decrypted Media')
                        report.add_script()
                        data_headers = ('Media', 'Decrypted Filename', 'Encrypted Filename', 'Full Path')
                        maindirectory = str(Path(file_found).parents[1])
                        report.write_artifact_data_table(data_headers, data_list, maindirectory,
                                                         html_no_escape=['Media'])
                        report.end_artifact_report()

                        tsvname = f'NQVault'
                        tsv(report_folder, data_headers, data_list, tsvname)


# MAIN #
def get_NQVault(files_found, report_folder, seeker, wrap_text):
    data_list = []
    sucess = 0
    # Get the "encrypted" PIN from DB

    for file_found in files_found:
        if file_found.endswith('322w465ay423xy11'):
            encoded_PIN, file_found_pin = extract_PIN_from_db(file_found)
            database = file_found
            sucess = 1
    if sucess == 0:
        logfunc('No Database DB Found or no hashed PIN present.')
        return

    if encoded_PIN != None:

        # Brute-force encrypted PIN
        pin_for_XOR_key = brute_force_pin(encoded_PIN)
        data_list.append((encoded_PIN, pin_for_XOR_key))

        # Use decrypted PIN to generate correct XOR key for media decryption (if media present).
        xor_key = raw_pin_to_XOR_key(pin_for_XOR_key)
        logfunc(f'XOR Key generated: {xor_key}')

        # Write encrypted/decrypted PIN info to report
        report = ArtifactHtmlReport('NQ Vault Decrypted PIN')
        report.start_artifact_report(report_folder, 'NQ Vault Decrypted PIN')
        report.add_script()
        data_headers = ('Encrypted PIN', 'Decrypted PIN')

        report.write_artifact_data_table(data_headers, data_list, file_found_pin, html_no_escape=['Media'])
        report.end_artifact_report()

        # This is a dictionary that builds the connection between the encrypted and decrypted media files.
        file_match_dict = read_file_info(database)

        # Media decryption funct
        if file_match_dict:
            file_decryption(files_found, file_match_dict, xor_key, report_folder)
        else:
            logfunc('No Encrypted Media Present in Database.')
            return

__artifacts__ = {
        "NQVault": (
                "Encrypting Media apps",
                ('*/emulated/0/Android/data/com.netqin.ps/files/Documents/SystemAndroid/Data/322w465ay423xy11', '*/SystemAndroid/Data/**', '/media/0/SystemAndroid/Data/322w465ay423xy11'),
                get_NQVault)
}


