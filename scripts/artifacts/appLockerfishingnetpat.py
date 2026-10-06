__artifacts_v2__ = {
    "get_appLockerfishingnetpat": {
        "name": "App Locker - Stored Preference",
        "description": "Reports named stored preferences and fixed AES-CBC operation output as reversible hex. "
                       "The output is not authenticated and does not establish an unlock pattern.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-12-14",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "Uses preference 85B064D26810275C89F1F2CC15E20B442E98874398F16F6717BBD5D34920E3F8, "
                 "the existing fixed key/IV and PKCS7 unpadding. Key applicability and unlock meaning remain unverified.",
        "paths": ('*/com.hld.anzenbokusufake/shared_prefs/share_privacy_safe.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "photo",
    }
}

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


_PREFERENCE = '85B064D26810275C89F1F2CC15E20B442E98874398F16F6717BBD5D34920E3F8'
_KEY = bytes.fromhex('526e7934384e693861506a59436e5549')


def _operation(value):
    if value is None or not value.strip():
        return '', 'No stored text'
    try:
        encrypted = bytes.fromhex(value)
    except ValueError:
        return '', 'Invalid hex text'
    if not encrypted or len(encrypted) % AES.block_size:
        return '', 'Invalid AES block length'
    decrypted = AES.new(_KEY, AES.MODE_CBC, _KEY).decrypt(encrypted)
    try:
        output = unpad(decrypted, AES.block_size)
    except ValueError:
        return '', 'Invalid PKCS7 padding'
    return output.hex(), 'Completed (output not authenticated)'


@artifact_processor
def get_appLockerfishingnetpat(context):
    data_list = []
    sources = []
    for file_found in dict.fromkeys(str(path) for path in context.get_files_found()):
        source = context.get_relative_path(file_found)
        try:
            root = ET.parse(file_found).getroot()
        except (OSError, ET.ParseError) as error:
            logfunc(f'App Locker preference: could not read {source}: {error}')
            continue
        preferences = root.findall(f'./string[@name="{_PREFERENCE}"]')
        if not preferences:
            data_list.append((None, '', 'Missing preference', source))
        for preference in preferences:
            output, status = _operation(preference.text)
            data_list.append((preference.text, output, status, source))
        sources.append(file_found)
    headers = ('Stored Preference Value', 'AES Output (hex)', 'Operation Status')
    if len(sources) > 1:
        headers += ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return headers, data_list, '\n'.join(sources)
