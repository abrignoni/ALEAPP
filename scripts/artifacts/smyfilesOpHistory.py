# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_smyfiles_OpHistory": {
        "name": "My Files Operation History",
        "description": "Extracts Operation History from My Files database",
        "author": "@PensiveHike",
        "creation_date": "2024-06-05",
        "last_update_date": "2024-06-05",
        "requirements": "none",
        "category": "My Files",
        "notes": "Current decode works with Android versions 10-12. Subscripted/accented/unknown characters will be replaced with '?'.",
        "paths": ('*/com.sec.android.app.myfiles/databases/OperationHistory.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "clock",
    }
}

import scripts.artifacts.artGlobals as aG
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

DECODE_DIC = {'a': 'b', 'b': 'a', 'c': 'c', 'd': 'd', 'e': 'f', 'f': 'e', 'g': 'g', 'h': 'p', 'i': 'r', 'j': 'q',
              'k': 's', 'l': 't', 'm': 'v', 'n': 'u', 'o': 'w', 'p': 'h', 'q': 'j', 'r': 'i', 's': 'k', 't': 'l',
              'u': 'n', 'v': 'm', 'w': 'o', 'x': 'x', 'y': 'z', 'z': 'y', '0': '(', '1': '*', '2': ')', '3': '+',
              '4': ',', '5': '.', '6': '-', '7': '/', '8': '8', '9': ':', '(': '0', '*': '1', ')': '2', '+': '3',
              ',': '4', '.': '5', '-': '6', '/': '7', ':': '9', ' ': ' ', '_': '_', '[': '[', ']': '^', '^': ']',
              '£': '£', '&': '%', '%': '&', '\'': '\'', '$': '$', '\"': '!', '!': '\"', '#': '#', '@': '@'}


def check_value(value):
    return DECODE_DIC.get(value, '?')


def process_string(old_string):
    new_string = ''
    for char in old_string:
        if char.isalpha() and char.isupper():
            char = check_value(char.lower()).upper()
        else:
            char = check_value(char)
        new_string += char
    return new_string


def get_db_data(file_found):
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute("""Select * from operation_history""")
        all_rows = cursor.fetchall()
    except:
        all_rows = 0
    db.close()
    return all_rows


def get_user(file_found):
    """If record located within secure folder path, retrieve user value (usually 150)"""
    if '/user/1' in file_found:
        start = file_found.find('/user/') + 6
        return file_found[start:start + 3]
    return 0


@artifact_processor
def get_smyfiles_OpHistory(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    Androidversion = aG.versionf

    if not 9 < int(Androidversion) < 13:
        logfunc(f'Android artifact My Files Operation History is not compatible with Android version {Androidversion}')
        data_headers = ('Account', 'Item Path', 'Operation Date (Handset Timezone)', 'Operation Type', 'Item Count', 'Folder Count', 'Page Type')
        return data_headers, data_list, source_path

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.lower().endswith('.db'):
            continue

        user = get_user(file_found)
        source_path = file_found
        all_rows = get_db_data(file_found)
        if all_rows == 0:
            continue

        for entry in all_rows:
            cipher = entry[1]
            if cipher != '':
                clear_path = process_string(cipher)
            elif cipher[:3] == '#G$':  # not supported, have seen in Android 13/14.
                clear_path = '*unsupported entry*'
            else:
                clear_path = '*blank entry*'
            data_list.append((user, clear_path, entry[2], entry[3], entry[4], entry[5], entry[6]))

    data_headers = ('Account', 'Item Path', 'Operation Date (Handset Timezone)', 'Operation Type', 'Item Count', 'Folder Count', 'Page Type')
    return data_headers, data_list, source_path
