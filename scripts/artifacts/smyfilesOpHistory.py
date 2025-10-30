from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly
import scripts.artifacts.artGlobals as aG
from packaging import version

__artifacts_v2__ = {
    "smyfilesOpHistory": {
        "name": "My Files Operation History",
        "description": "Extracts Operation History from My Files database",
        "author": "@PensiveHike",
        "version": "0.1",
        "date": "2024-06-05",
        "requirements": "none",
        "category": "My Files",
        "notes": "Current decode works with Android versions 10-12. Subscripted/accented/unknown characters will be replaced with '?'.",
        "paths": '*/com.sec.android.app.myfiles/databases/OperationHistory.db*',
        "function": "get_smyfiles_OpHistory"
    }
}

# database locations found at
# /data/data/com.sec.android.app.myfiles/databases/OperationHistory.db
# /data/user/150/com.sec.android.app.myfiles/databases/OperationHistory.db


def check_value(value):
    decode_dic = {'a': 'b', 'b': 'a', 'c': 'c', 'd': 'd', 'e': 'f', 'f': 'e', 'g': 'g', 'h': 'p', 'i': 'r', 'j': 'q',
                  'k': 's', 'l': 't', 'm': 'v', 'n': 'u', 'o': 'w', 'p': 'h', 'q': 'j', 'r': 'i', 's': 'k', 't': 'l',
                  'u': 'n', 'v': 'm', 'w': 'o', 'x': 'x', 'y': 'z', 'z': 'y', '0': '(', '1': '*', '2': ')', '3': '+',
                  '4': ',', '5': '.', '6': '-', '7': '/', '8': '8', '9': ':', '(': '0', '*': '1', ')': '2', '+': '3',
                  ',': '4', '.': '5', '-': '6', '/': '7', ':': '9', ' ': ' ', '_': '_', '[': '[', ']': '^', '^': ']',
                  '£': '£', '&': '%', '%': '&', '\'': '\'', '$': '$', '\"': '!', '!': '\"', '#': '#', '@': '@'}
    if value in decode_dic:
        result = decode_dic[value]
    else:
        result = '?'
    return result


def process_string(old_string):
    new_string = ''
    for char in old_string:

        if char.isalpha() and char.isupper():
            char = check_value(char.lower())
            char = char.upper()
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

    return all_rows


def get_user(file_found):
    """If record located within secure folder path, retrieve user value (usually 150)"""
    if '/user/1' in file_found:
        finder = file_found.find('/user/')
        start = finder + 6
        end = start + 3
        user = file_found[start:end]
    else:
        user = 0
    return user


def get_smyfiles_OpHistory(files_found, report_folder, seeker, wrap_text):
    html_source = ''
    Androidversion = aG.versionf

    if not 9 < int(Androidversion) < 13:
        logfunc(f'Android artifact My Files Operation History is not compatible with Android version {Androidversion}')

    else:
        data_list = []
        for file_found in files_found:
            file_found = str(file_found)
            user = get_user(file_found)
            if file_found.lower().endswith('.db'):
                html_source = file_found
                all_rows = get_db_data(file_found)
                usageentries = 0
                if all_rows != 0:
                    usageentries = len(all_rows)

                if usageentries > 0:
                    for entry in all_rows:
                        cipher = entry[1]
                        # mod_ts = entry[2]
                        # op_type = entry[3]
                        # item_count = entry[4]
                        # folder_count = entry[5]
                        # page_type = entry[6]
                        #print(repr(cipher))
                        if cipher != '':
                            clear_path = process_string(cipher)
                        elif cipher[:3] == '#G$':  # not supported, have seen in Android 13/14.
                            clear_path = '*unsupported entry*'
                        else:
                            clear_path = '*blank entry*'
                        data_list.append((user, clear_path, entry[2], entry[3], entry[4], entry[5], entry[6]))

        if data_list:
            report = ArtifactHtmlReport('My Files DB - Operation History')
            report.start_artifact_report(report_folder, 'My Files DB - Operation History')
            report.add_script()
            data_headers = ('Account', 'Item Path', 'Operation Date (Handset Timezone)', 'Operation Type',
                            'Item Count', 'Folder Count', 'Page Type')
            report.write_artifact_data_table(data_headers, data_list, html_source)
            report.end_artifact_report()

            tsvname = f'My Files db - Operation History'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = f'My Files DB - Operation History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No My Files DB Operation History data available')

