# pylint: disable=W0613
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
    "get_fcm_jungrammer": {
        "name": "FCM - Jungrammer",
        "description": "Jungrammer chat-app notifications (kr.jungrammer.*) from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "message",
    }
}

import datetime
import pathlib

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor, logfunc

KNOWN_JUNGRAMMERS = {
    "kr.jungrammer.bluetalk",
    "kr.jungrammer.randomchat",
    "kr.jungrammer.superranchat",
    "kr.jungrammer.talkchat",
}
_RELEVANT_TYPES = {"CONNECT", "MESSAGE", "DISCONNECT", "NOTICE"}


def _to_utc(value):
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone(datetime.timezone.utc)
    return value if value else ''


def _annotation(kv):
    return (f"User ID: {kv.get('userId', '')} \n"
            f"User Key: {kv.get('userKey', '')} \n"
            f"Nickname: {kv.get('nickname', '')} \n"
            f"Country Code: {kv.get('countryCode', '')} \n"
            f"Client Type: {kv.get('clientType', '')}")


@artifact_processor
def get_fcm_jungrammer(files_found, report_folder, seeker, wrap_text):
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    source = " ".join(str(x) for x in in_dirs)
    conversations = {}  # conv_key -> {package, from_token, parties: [], messages: [(ts, type, text)]}

    for in_db_path in in_dirs:
        try:
            with FcmIterator(in_db_path) as record_iterator:
                for rec in record_iterator:
                    if rec.package not in KNOWN_JUNGRAMMERS:
                        continue
                    rtype = rec.key_values.get("type")
                    from_token = rec.key_values.get("fromToken")
                    if rtype not in _RELEVANT_TYPES or not from_token:
                        continue
                    conv_key = f"{rec.package}-{from_token}"
                    conv = conversations.setdefault(
                        conv_key, {"package": rec.package, "from_token": from_token,
                                   "parties": [], "messages": []})
                    ts = _to_utc(rec.timestamp)
                    if rtype == "CONNECT":
                        annotation = _annotation(rec.key_values)
                        conv["parties"].append(annotation)
                        conv["messages"].append((ts, rtype, annotation))
                    else:
                        conv["messages"].append((ts, rtype, rec.key_values.get("message")))
        except Exception as exc:  # pylint: disable=W0718
            logfunc(f"Jungrammer FCM: error reading {in_db_path}: {exc}")

    data_list = []
    for conv_key, conv in conversations.items():
        parties = "\n".join(conv["parties"])
        for ts, mtype, message in conv["messages"]:
            data_list.append((ts, conv_key, conv["package"], parties, conv["from_token"], mtype, message))

    data_headers = (('Timestamp', 'datetime'), 'Conversation Key', 'Package', 'Other Party Details',
                    'From Token', 'Message Type', 'Message')
    return data_headers, data_list, source
