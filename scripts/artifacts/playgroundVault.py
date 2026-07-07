__artifacts_v2__ = {
    "get_playgroundVault": {
        "name": "Playground Vault",
        "description": "Decrypts media hidden by the Playground AppLocker vault (AES-GCM)",
        "author": "",
        "creation_date": "2022-01-16",
        "last_update_date": "2022-01-16",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "",
        "paths": ('*/playground.develop.applocker/shared_prefs/crypto.KEY_256.xml', '*/applocker/vault/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

import base64
import datetime
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from Crypto.Cipher import AES

import scripts.filetype as filetype
from scripts.ilapfuncs import artifact_processor, logfunc, check_in_embedded_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find_key(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found).startswith('crypto.KEY_256.xml'):
            continue
        try:
            root = ET.parse(file_found).getroot()
            found = root.findall('./string[@name="cipher_key"]')
            if found and found[0].text:
                key = base64.b64decode(found[0].text)
                logfunc('Playground Vault encryption key recovered')
                return key
        except (ET.ParseError, ValueError):
            continue
    return None


@artifact_processor
def get_playgroundVault(context):
    files_found = context.get_files_found()
    key = _find_key(files_found)
    data_list = []
    source_path = ''
    if key:
        for file_found in files_found:
            file_found = str(file_found)
            if not os.path.isfile(file_found):
                continue
            filename = os.path.basename(file_found)
            if filename.startswith('._') or filename.startswith('crypto.KEY_256.xml'):
                continue
            source_path = str(Path(file_found).parents[1])

            try:
                with open(file_found, 'rb') as f:
                    full = f.read()
                if len(full) < 30:
                    continue
                # IV follows the first 2 bytes; the trailing 16 bytes are the GCM tag
                cipher = AES.new(key, AES.MODE_GCM, full[2:14])
                decrypted = cipher.decrypt(full[14:-16])
            except (ValueError, OSError) as ex:
                logfunc(f'Could not decrypt Playground Vault file {filename}: {ex}')
                continue

            kind = filetype.guess(decrypted)
            if kind:
                thumb = check_in_embedded_media(file_found, decrypted, f'{filename}.{kind.extension}',
                                                force_type=kind.mime, force_extension=kind.extension)
            else:
                thumb = check_in_embedded_media(file_found, decrypted, filename)

            match = re.search(r'(?:EIF|EVF)(\d+)', filename)
            enctimestamp = _ms_to_utc(match.group(1)) if match else ''
            data_list.append((thumb, filename, enctimestamp, context.get_relative_path(file_found)))

    data_headers = (('Media', 'media'), 'Filename', ('Encrypted On Timestamp', 'datetime'), 'Full Path')
    return data_headers, data_list, context.get_relative_path(source_path)
