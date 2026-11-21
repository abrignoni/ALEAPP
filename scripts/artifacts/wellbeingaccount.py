__artifacts_v2__ = {
    "get_wellbeingaccount": {
        "name": "wellbeingaccount",
        "description": "Decodes the Google Digital Wellbeing AccountData.pb protobuf file, without a schema.",
        "author": "@ydkhatri, @AlexisBrignoni, Claude",
        "creation_date": "2020-02-25",
        "last_update_date": "2026-11-07",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": ("One row per distinct AccountData.pb per Android user. The protobuf is decoded with "
                  "the vendored blackboxprotobuf, without a schema, so fields are named by their field "
                  "numbers and the meaning of each field is not established here. A length-delimited "
                  "value is first tried as a nested message. One that is not a message is shown as "
                  "text when it decodes as UTF-8, otherwise as hex. Numbers are shown as decoded. "
                  "AOSP's init.rc notes that /data/data is bind-mounted onto /data/user/0 "
                  "(platform/system/core, rootdir/init.rc line 960 at commit a3b721a), so a file under "
                  "either is user 0's, and the two copies are reported once when their bytes match."),
        "paths": ('*/com.google.android.apps.wellbeing/files/AccountData.pb',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "battery",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.wellbeing vc 839927 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.wellbeing vc 762847 | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.apps.wellbeing vc 550467 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.wellbeing vc 495937 | 2 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.wellbeing vc 668567 | 1 row",
        },
        "html_columns": ['Protobuf Parsed Data'],
    }
}

import hashlib
import json
import re

from scripts.blackboxprotobuf import decode_message
from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, logfunc

_USER = re.compile(r'(?:^|/)data/user(?:_de)?/(\d+)/com\.google\.android\.apps\.wellbeing/')
_OWNER = re.compile(r'(?:^|/)data/data/com\.google\.android\.apps\.wellbeing/')


def _android_user(path):
    """The Android user a staged path belongs to; /data/data is user 0's directory."""
    path = str(path).replace('\\', '/')
    match = _USER.search(path)
    if match:
        return match.group(1)
    return '0' if _OWNER.search(path) else ''


def _readable(value):
    """blackboxprotobuf's decoded message with bytes made JSON-safe: UTF-8 text, else hex."""
    if isinstance(value, dict):
        return {key: _readable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_readable(item) for item in value]
    if isinstance(value, (bytes, bytearray)):
        try:
            return bytes(value).decode('utf-8')
        except UnicodeDecodeError:
            return bytes(value).hex()
    return value


@artifact_processor
def get_wellbeingaccount(context):
    data_list = []
    source_paths = []
    seen = set()
    for file_found in sorted(str(path) for path in context.get_files_found()):
        with open(file_found, 'rb') as handle:
            raw = handle.read()
        user = _android_user(file_found)
        key = (user, hashlib.sha256(raw).hexdigest())
        if key in seen:
            continue
        seen.add(key)
        try:
            message, _ = decode_message(raw)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logfunc(f'wellbeingaccount: {context.get_relative_path(file_found)} could not be decoded: {ex}')
            continue
        content = _readable(message)
        pretty = json.dumps(content, indent=4, sort_keys=True, ensure_ascii=False)
        # <br> rather than newlines, so the cell stays on one line in the TSV export.
        data_list.append((user, '<pre id="json">' + esc(pretty).replace('\n', '<br>') + '</pre>',
                          json.dumps(content, sort_keys=True, ensure_ascii=False)))
        source_paths.append(file_found)

    data_headers = ('Android User', 'Protobuf Parsed Data', 'Protobuf Data')
    return data_headers, data_list, '\n'.join(source_paths)
