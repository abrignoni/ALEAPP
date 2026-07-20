__artifacts_v2__ = {
    "get_appLockerfishingnetpat": {
        "name": "App Locker Pat",
        "description": "Parses the App Locker unlock pattern (encrypted and decrypted) from the share_privacy_safe.xml preferences file.",
        "author": "",
        "creation_date": "2021-12-14",
        "last_update_date": "2021-12-14",
        "requirements": "none",
        "category": "Encrypting Media Apps",
        "notes": "",
        "paths": ('*/com.hld.anzenbokusufake/shared_prefs/share_privacy_safe.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "photo",
    }
}

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_appLockerfishingnetpat(context):
    files_found = context.get_files_found()

    standardKey = '526e7934384e693861506a59436e5549'
    standardIV = '526e7934384e693861506a59436e5549'
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        tree = ET.parse(file_found)
        root = tree.getroot()
        encryptedPattern = root.findall('./string[@name="85B064D26810275C89F1F2CC15E20B442E98874398F16F6717BBD5D34920E3F8"]')[0].text
        cipher = AES.new(bytes.fromhex(standardKey), AES.MODE_CBC, bytes.fromhex(standardIV))
        decryptedPattern = unpad(cipher.decrypt(bytes.fromhex(encryptedPattern)), AES.block_size)

        data_list.append((encryptedPattern, decryptedPattern))

    data_headers = ('Encrypted Pattern', 'Decrypted Pattern')
    return data_headers, data_list, source_path
