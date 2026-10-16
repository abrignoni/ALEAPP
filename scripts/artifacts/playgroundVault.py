__artifacts_v2__ = {
    "get_playgroundVault": {
        "name": "Playground Vault",
        "description": "Files in the Playground AppLocker vault folder, decrypted with the AES-GCM key stored in the app's crypto.KEY_256.xml.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-01-16",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "The key file name and its cipher_key entry match the "
                 "shared preferences key store of Facebook's Conceal library "
                 "(SharedPrefsBackedKeyChain.java lines 40 to 42 and 81 to 82, "
                 "https://github.com/facebookarchive/conceal/blob/f73541e79ac392ace032e53e2ef2ed4cc730b3fc/java/com/facebook/android/crypto/keychain/SharedPrefsBackedKeyChain.java#L40-L82). "
                 "Each vault file is read in that library's layout: 2 bytes, a "
                 "12 byte IV, the encrypted content and a 16 byte tag. In "
                 "Conceal the tag also covers an entity name chosen by the "
                 "app, which the file does not store (Encrypt.cpp lines 69 to "
                 "75, https://github.com/facebookarchive/conceal/blob/f73541e79ac392ace032e53e2ef2ed4cc730b3fc/native/cpp/Encrypt.cpp#L69-L75). "
                 "The entity name this app uses is not established, so the "
                 "AES-GCM authentication tag is not verified. Media is output "
                 "only when the decrypted bytes begin with a file signature "
                 "the tool recognises, and Decrypted File Type shows that "
                 "type. A file whose decrypted bytes are not recognised keeps "
                 "its row with Media blank and Decrypted File Type reading "
                 "'Not recognised, not output'. A recognised signature does "
                 "not show the rest of the file decrypted correctly. File "
                 "Name Number is the number that follows EIF or EVF in the "
                 "vault file name, as written. File Name Number As Unix "
                 "Milliseconds is that number read as Unix milliseconds in "
                 "UTC. That the number is a time, and what event it marks, "
                 "are not established. No registered corpus holds this app "
                 "(20 zip listings and 24 tar indexes checked 2026-10-04); "
                 "the reading was exercised on constructed files only.",
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

            # The GCM tag also covers an entity name the file does not store, so it
            # cannot be verified here. Output only bytes with a recognised signature.
            kind = filetype.guess(decrypted)
            if kind:
                thumb = check_in_embedded_media(file_found, decrypted, f'{filename}.{kind.extension}',
                                                force_type=kind.mime, force_extension=kind.extension)
                decrypted_type = kind.mime
            else:
                thumb = None
                decrypted_type = 'Not recognised, not output'
                logfunc(f'Playground Vault file {filename}: decrypted bytes not recognised, media not output')

            match = re.search(r'(?:EIF|EVF)(\d+)', filename)
            name_number = match.group(1) if match else ''
            data_list.append((_ms_to_utc(name_number), name_number, thumb, filename, decrypted_type,
                              context.get_relative_path(file_found)))

    data_headers = (('File Name Number As Unix Milliseconds', 'datetime'), 'File Name Number',
                    ('Media', 'media'), 'Filename', 'Decrypted File Type', 'Full Path')
    return data_headers, data_list, context.get_relative_path(source_path)
