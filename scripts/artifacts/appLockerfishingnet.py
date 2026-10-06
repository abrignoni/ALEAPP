__artifacts_v2__ = {
    "get_appLockerfishingnet": {
        "name": "App Locker",
        "description": "Applies a fixed AES-CBC key to the files under .privacy_safe/picture and "
                       ".privacy_safe/video that are not already recognised as media, and reports the "
                       "cipher operation outcome separately from any recognised output MIME type.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-12-14",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "CBC output is not authenticated. File signatures are heuristic; key/IV "
                 "applicability and app-version coverage remain uncorroborated.",
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

# Existing fixed key/IV; applicability requires further corroboration.
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

        output_type = ''
        if filetype.guess(file_found) is not None:
            # A recognised input signature does not establish encryption state.
            thumb = check_in_media(file_found, filename)
            operation = 'Not attempted (recognized input)'
        else:
            # Attempt the existing cipher operation on unrecognised input.
            try:
                with open(file_found, 'rb') as target:
                    data = AES.new(bytes.fromhex(STANDARD_KEY), AES.MODE_CBC,
                                   bytes.fromhex(STANDARD_IV)).decrypt(target.read())
                kind = filetype.guess(data)
                if kind:
                    output_type = kind.mime
                    thumb = check_in_embedded_media(file_found, data, f'{filename}.{kind.extension}',
                                                    force_type=kind.mime, force_extension=kind.extension)
                else:
                    thumb = check_in_embedded_media(file_found, data, filename)
                operation = 'Completed (output not authenticated)'
            except ValueError as ex:
                logfunc(f'Cipher operation failed for {file_found}: {ex}')
                thumb = check_in_media(file_found, filename)
                operation = 'Failed'

        data_list.append((thumb, filename, operation, output_type, context.get_relative_path(file_found)))

    data_headers = (('Media', 'media'), 'Filename', 'Cipher Operation', 'Recognized Output Type', 'Full Path')
    return data_headers, data_list, context.get_relative_path(source_path)
