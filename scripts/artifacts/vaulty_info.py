# pylint: disable=E1101
__artifacts_v2__ = {
    "get_vaulty_info": {
        "name": "vaulty_info",
        "description": "Prefs File",
        "author": "",
        "creation_date": "2022-02-23",
        "last_update_date": "2022-02-23",
        "requirements": "none",
        "category": "Vaulty",
        "notes": "",
        "paths": ('*/com.theronrogers.vaultyfree/shared_prefs/com.theronrogers.vaultyfree_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "lock",
    }
}

import base64
import binascii
from hashlib import md5

import xmltodict

from scripts.ilapfuncs import artifact_processor


def _brute_force(target):
    four_digit_pins = [f"{x:04}" for x in range(0, 10000)]
    six_digit_pins = [f"{x:06}" for x in range(0, 1000000)]
    for item in four_digit_pins + six_digit_pins:
        if md5(item.encode()).hexdigest() == target:
            return item
    return "Brute Force was Unsuccessful - this is not the password"


@artifact_processor
def get_vaulty_info(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    with open(source_path, "r", encoding='utf-8', errors='replace') as file:
        prefs = xmltodict.parse(file.read())

    data_list = []

    strings = prefs["map"]["string"]
    values = {item.get("@name"): item.get("#text") for item in strings}

    password_hash = values.get("password_hash")
    if password_hash:
        md5_hash = binascii.hexlify(base64.decodebytes(password_hash.encode())).decode()
        data_list.append(("Password MD5", md5_hash))
        data_list.append(("Password", _brute_force(md5_hash)))

    if values.get("security_question") is not None:
        data_list.append(("Security Question", values.get("security_question")))

    if values.get("security_answer_hash") is not None:
        answer = binascii.hexlify(base64.decodebytes(values["security_answer_hash"].encode())).decode()
        data_list.append(("Security Answer MD5", answer))

    if values.get("location") is not None:
        data_list.append(("Location", values.get("location")))

    if values.get("drive_account_name") is not None:
        data_list.append(("Drive Account", values.get("drive_account_name")))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
