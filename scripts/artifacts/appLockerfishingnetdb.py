# pylint: disable=W0613
__artifacts_v2__ = {
    "get_appLockerfishingnetdb": {
        "name": "App Locker DB",
        "description": "Parses the stored unlock pattern for the App Locker privacy app (encrypted and decrypted pattern and key) from privacy_safe.db.",
        "author": "",
        "creation_date": "2021-12-14",
        "last_update_date": "2021-12-14",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "",
        "paths": ('*/.privacy_safe/db/privacy_safe.db',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "photo",
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_appLockerfishingnetdb(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        message = 'The located database is encrypted. It contains information regarding the source directory of the encrypted files, timestamp metadata, and original filenames.'
        decryptioninst = 'To decrypt follow the instructions at the following URL: https://theincidentalchewtoy.wordpress.com/2021/12/07/decrypting-the-calculator-apps/'
        keytodecrypt = 'Rny48Ni8aPjYCnUI'

        data_list.append((message, decryptioninst, keytodecrypt))

    data_headers = ('Encrypted Pattern', 'Decrypted Pattern', 'Key To Decrypt')
    return data_headers, data_list, source_path
