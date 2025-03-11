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

import sys
import pathlib
import datetime
import json
from scripts.ccl.ccl_android_fcm_queued_messages import FcmRecord, FcmIterator
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

__version__ = "0.4.0"
__description__ = """
Reads records from the fcm_queued_messages.ldb leveldb in com.google.android.gms related to com.twitter.android 
(currently only direct messages)"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"

EPOCH = datetime.datetime(1970, 1, 1)


def unix_ms(ms: int):
    return EPOCH + datetime.timedelta(milliseconds=ms)


def process_dm(rec: FcmRecord):
    user_obj = json.loads(rec.key_values["users"])
    notification_data = json.loads(rec.key_values["notification_event_data"])
    sender = f"{user_obj['sender']['screen_name']} ({user_obj['sender']['id']})"
    recipient = f"{user_obj['recipient']['screen_name']} ({user_obj['recipient']['id']})"
    timestamp = unix_ms(int(notification_data["message"]["message_data"]["time"]))
    text = notification_data["message"]["message_data"]["text"]

    conversation_key = tuple([user_obj['sender']['id'], user_obj['recipient']['id']])

    other_party = user_obj['sender']

    entities = []
    if "entities" in notification_data["message"]["message_data"]:
        entity_details = notification_data["message"]["message_data"]["entities"]
        hash_tags = entity_details.get("hashtags")
        symbols = entity_details.get("symbols")
        user_mentions = entity_details.get("user_mentions")
        urls = entity_details.get("urls")

        if hash_tags:
            scripts.ilapfuncs.logfunc("Hashtags present in DMs, these are not currently processed")
        if symbols:
            scripts.ilapfuncs.logfunc("Symbols present in DMs, these are not currently processed")
        if user_mentions:
            scripts.ilapfuncs.logfunc("User mentions present in DMs, these are not currently processed")
        if urls:
            for url in urls:
                entities.append(f"Url: {url['url']} (Expanded: {url['expanded_url']})")

    attachment_details = []
    if "attachment" in notification_data["message"]["message_data"]:
        attachment = notification_data["message"]["message_data"]["attachment"]
        for att_key, att_item in attachment.items():
            if att_key == "card":
                attachment_details.extend([
                    f"URL: {att_item['url']}",
                    f"URL Title: {att_item['binding_values']['title']['string_value']}",
                    f"URL Description: {att_item['binding_values']['description']['string_value']}",
                ])
            elif att_key == "photo":
                attachment_details.extend([
                    f"Photo ID: {att_item['id']}",
                    f"Photo Media URL: {att_item['media_url']}",
                    f"Photo URL: {att_item['url']} (Expanded: {att_item['expanded_url']})",
                    f"Photo Dimensions: {att_item['original_info']['width']}, {att_item['original_info']['height']}"
                ])
            else:
                # print(att_key, att_item)
                scripts.ilapfuncs.logfunc(f"Unknown attachment type {att_key} in DMs, please contact the developer")

    return conversation_key, other_party, (sender, recipient, timestamp, text, entities, attachment_details)


def get_fcm_twitter(files_found, report_folder, seeker, wrap_text):
    channels = set()

    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    rows = []
    data_headers = [
        "Conversation Key", "Other party", "Sender", "Recipient", "Timestamp", "Text", "Entities", "Attachments"
    ]

    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == "com.twitter.android":
                    if "channel" not in rec.key_values:
                        scripts.ilapfuncs.logfunc(f"Record without channel: {rec.key_values}")
                        continue
                    channel = rec.key_values["channel"]

                    if channel == "dms":
                        conv_key, other_party, row = process_dm(rec)
                        rows.append([conv_key, other_party, *row])
                    else:
                        channels.add(channel)

    if rows:
        report = ArtifactHtmlReport("Twitter DM Notifications (Firebase Cloud Messaging Queued Messages)")
        report_name = "FCM-Twitter DM Notifications"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        source_files = " ".join(str(x) for x in in_dirs)

        report.write_artifact_data_table(data_headers, rows, source_files)
        report.end_artifact_report()

        scripts.ilapfuncs.tsv(report_folder, data_headers, rows, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, rows, data_headers)
    else:
        scripts.ilapfuncs.logfunc("No FCM Twitter DM notifications found")

    scripts.ilapfuncs.logfunc("Un-processed 'channels' (contact R&D if you think these are required for your case):")
    scripts.ilapfuncs.logfunc("\n".join(channels))


__artifacts__ = {
    "FCM_Twitter": (
        "Firebase Cloud Messaging",
        ('*/fcm_queued_messages.ldb/*'),
        get_fcm_twitter)
}
