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
    "get_fcm_twitter": {
        "name": "FCM - Twitter DMs",
        "description": "Twitter direct messages recovered from the fcm_queued_messages.ldb leveldb",
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
    }
}

import datetime
import json
import pathlib

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor, logfunc


def _unix_ms(ms):
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000, datetime.timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError):
        return ''


def _process_dm(rec):
    user_obj = json.loads(rec.key_values["users"])
    msg = json.loads(rec.key_values["notification_event_data"])["message"]["message_data"]
    sender = f"{user_obj['sender']['screen_name']} ({user_obj['sender']['id']})"
    recipient = f"{user_obj['recipient']['screen_name']} ({user_obj['recipient']['id']})"
    conv_key = f"{user_obj['sender']['id']}, {user_obj['recipient']['id']}"
    other_party = json.dumps(user_obj['sender'], ensure_ascii=False)

    entities = []
    if "entities" in msg:
        for url in msg["entities"].get("urls") or []:
            entities.append(f"Url: {url['url']} (Expanded: {url['expanded_url']})")
        for label, key in (("Hashtags", "hashtags"), ("Symbols", "symbols"),
                           ("User mentions", "user_mentions")):
            if msg["entities"].get(key):
                logfunc(f"Twitter FCM: {label} present in DMs, not currently processed")

    attachments = []
    for att_key, att_item in (msg.get("attachment") or {}).items():
        if att_key == "card":
            attachments.extend([
                f"URL: {att_item['url']}",
                f"URL Title: {att_item['binding_values']['title']['string_value']}",
                f"URL Description: {att_item['binding_values']['description']['string_value']}"])
        elif att_key == "photo":
            attachments.extend([
                f"Photo ID: {att_item['id']}",
                f"Photo Media URL: {att_item['media_url']}",
                f"Photo URL: {att_item['url']} (Expanded: {att_item['expanded_url']})",
                f"Photo Dimensions: {att_item['original_info']['width']}, {att_item['original_info']['height']}"])
        else:
            logfunc(f"Twitter FCM: unknown attachment type {att_key} in DMs")

    return (conv_key, other_party, sender, recipient, _unix_ms(msg["time"]), msg.get("text", ""),
            "; ".join(entities), "; ".join(attachments))


@artifact_processor
def get_fcm_twitter(files_found, report_folder, seeker, wrap_text):
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    source = " ".join(str(x) for x in in_dirs)
    data_list = []
    for in_db_path in in_dirs:
        try:
            with FcmIterator(in_db_path) as record_iterator:
                for rec in record_iterator:
                    if rec.package != "com.twitter.android":
                        continue
                    if rec.key_values.get("channel") != "dms":
                        continue
                    try:
                        data_list.append(_process_dm(rec))
                    except (KeyError, ValueError, TypeError) as exc:
                        logfunc(f"Twitter FCM: could not parse DM record: {exc}")
        except Exception as exc:  # pylint: disable=W0718
            logfunc(f"Twitter FCM: error reading {in_db_path}: {exc}")

    data_headers = ('Conversation Key', 'Other Party', 'Sender', 'Recipient',
                    ('Timestamp', 'datetime'), 'Text', 'Entities', 'Attachments')
    return data_headers, data_list, source
