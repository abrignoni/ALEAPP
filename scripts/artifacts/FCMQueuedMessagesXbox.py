"""
Copyright 2022, CCL Forensics

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__artifacts_v2__ = {
    "get_fcm_xbox": {
        "name": "FCM - Xbox Messages",
        "description": "Xbox (com.microsoft.xboxone.smartglass) message notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "get_fcm_xbox_party": {
        "name": "FCM - Xbox Party Invites",
        "description": "Xbox party invite notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "user-plus",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "get_fcm_xbox_presence": {
        "name": "FCM - Xbox Presence",
        "description": "Xbox presence notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    }
}

import base64
import datetime
import json
import pathlib

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor, logfunc

_CACHE = {}


def _to_utc(value):
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone(datetime.timezone.utc)
    return value if value else ''


def _unix_ms(ms):
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000, datetime.timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError):
        return ''


def _process_payload(payload):
    processed = []
    for part in payload.get("parts", []):
        content_type = part.get("contentType")
        if content_type == "text":
            processed.append(part.get("text", ""))
        elif content_type == "image":
            processed.extend([
                f"Image attachment id: {part['attachmentId']}",
                f"File type: {part['filetype']}; hash: {base64.b64decode(part['hash']).hex()}; "
                f"dimensions: {part['width']}x{part['height']}",
                f"uri: {part['downloadUri']}"])
        elif content_type == "deeplink":
            processed.append(f"Link text: {part['buttonText']}")
            if part.get("appUri"):
                processed.append(f"App URI: {part['appUri']}")
            if part.get("webUri"):
                processed.append(f"Web URI: {part['webUri']}")
        else:
            logfunc(f"Xbox FCM: unhandled payload content type {content_type}")
    return "\n".join(processed)


def _load(files_found):
    key = tuple(sorted(str(f) for f in files_found))
    if key in _CACHE:
        return _CACHE[key]
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    source = " ".join(str(x) for x in in_dirs)
    messages, parties, presence = [], [], []
    for in_db_path in in_dirs:
        try:
            with FcmIterator(in_db_path) as record_iterator:
                for rec in record_iterator:
                    if rec.package != "com.microsoft.xboxone.smartglass":
                        continue
                    ntype = rec.key_values.get("type")
                    try:
                        if ntype == "MESSAGE":
                            obj = json.loads(rec.key_values["xbl"])
                            content = _process_payload(json.loads(obj["messagePayload"]))
                            messages.append((rec.key, _to_utc(rec.timestamp), obj["conversationId"],
                                             _unix_ms(obj["timestamp"]),
                                             f"{obj['senderGamerTag']} ({obj['senderXuid']})",
                                             obj.get("text", ""), content))
                        elif ntype == "partyInvite":
                            obj = json.loads(rec.key_values["xbl"])["invite_handle"]
                            if obj.get("type") != "invite":
                                logfunc(f"Xbox FCM: unknown partyInvite type {obj.get('type')}")
                                continue
                            parties.append((rec.key, _to_utc(rec.timestamp),
                                            f"{obj['inviteInfo']['senderUniqueModernGamertag']} ({obj['senderXuid']})"))
                        elif ntype == "presence":
                            presence.append((rec.key, _to_utc(rec.timestamp),
                                             f"{rec.key_values['gamertag']} ({rec.key_values['xuid']})"))
                    except (KeyError, ValueError, TypeError) as exc:
                        logfunc(f"Xbox FCM: could not parse {ntype} record: {exc}")
        except Exception as exc:  # pylint: disable=W0718
            logfunc(f"Xbox FCM: error reading {in_db_path}: {exc}")
    _CACHE[key] = (messages, parties, presence, source)
    return _CACHE[key]


@artifact_processor
def get_fcm_xbox(context):
    files_found = context.get_files_found()
    messages, _parties, _presence, source = _load(files_found)
    data_headers = ('FCM Key', ('FCM Timestamp', 'datetime'), 'Conversation ID',
                    ('Message Timestamp', 'datetime'), 'Sender', 'Text', 'Content')
    return data_headers, messages, source


@artifact_processor
def get_fcm_xbox_party(context):
    files_found = context.get_files_found()
    _messages, parties, _presence, source = _load(files_found)
    data_headers = ('FCM Key', ('FCM Timestamp', 'datetime'), 'Sender')
    return data_headers, parties, source


@artifact_processor
def get_fcm_xbox_presence(context):
    files_found = context.get_files_found()
    _messages, _parties, presence, source = _load(files_found)
    data_headers = ('FCM Key', ('FCM Timestamp', 'datetime'), 'User')
    return data_headers, presence, source
