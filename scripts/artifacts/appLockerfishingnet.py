__artifacts_v2__ = {
    "get_appLockerfishingnet": {
        "name": "App Locker",
        "description": "Decrypts media hidden by the App Locker / Calculator vault (.privacy_safe, AES-CBC)",
        "author": "",
        "creation_date": "2021-12-14",
        "last_update_date": "2021-12-14",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "",
        "paths": ('*/.privacy_safe/picture/*', '*/.privacy_safe/video/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

import os
from pathlib import Path

from Crypto.Cipher import AES

import scripts.filetype as filetype
from scripts.ilapfuncs import artifact_processor, logfunc, check_in_media, check_in_embedded_media

# Known hardcoded key/IV used by this vault
STANDARD_KEY = '526e7934384e693861506a59436e5549'
STANDARD_IV = '526e7934384e693861506a59436e5549'


@artifact_processor
def get_appLockerfishingnet(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found) or os.path.getsize(file_found) == 0:
            continue
        filename = os.path.basename(file_found)
        if filename.startswith('~') or filename.startswith('._'):
            continue
        source_path = str(Path(file_found).parents[1])

        if filetype.guess(file_found) is not None:
            # already a recognizable (unencrypted) media file
            thumb = check_in_media(file_found, filename)
            decrypted = 'Not encrypted'
        else:
            # not recognizable -> assume encrypted, decrypt with the known key/IV
            try:
                with open(file_found, 'rb') as target:
                    data = AES.new(bytes.fromhex(STANDARD_KEY), AES.MODE_CBC,
                                   bytes.fromhex(STANDARD_IV)).decrypt(target.read())
                kind = filetype.guess(data)
                if kind:
                    thumb = check_in_embedded_media(file_found, data, f'{filename}.{kind.extension}',
                                                    force_type=kind.mime, force_extension=kind.extension)
                else:
                    thumb = check_in_embedded_media(file_found, data, filename)
                decrypted = 'True'
            except ValueError as ex:
                logfunc(f'Error decrypting {file_found}: {ex}')
                thumb = check_in_media(file_found, filename)
                decrypted = 'False'

        data_list.append((thumb, filename, decrypted, context.get_relative_path(file_found)))

    data_headers = (('Media', 'media'), 'Filename', 'Decrypted?', 'Full Path')
    return data_headers, data_list, context.get_relative_path(source_path)
