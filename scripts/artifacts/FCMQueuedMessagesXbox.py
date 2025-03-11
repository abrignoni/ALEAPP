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

import datetime
import json
import base64
import pathlib
from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

__version__ = "0.1"
__description__ = """
Reads records from the fcm_queued_messages.ldb leveldb in com.google.android.gms related to com.microsoft.xboxone.smartglass"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"

EXPECTED_PACKAGES = ("com.microsoft.xboxone.smartglass",)
RUN_PER_PACKAGE = False

EPOCH = datetime.datetime(1970, 1, 1)


def unix_ms(ms):
    return EPOCH + datetime.timedelta(milliseconds=ms)


def process_payload(payload):
    processed = []
    for part in payload["parts"]:
        content_type = part["contentType"]
        if content_type == "text":
            processed.append(part["text"])
        elif content_type == "image":
            processed.extend([
                f"<em>Image attachment id: {part['attachmentId']}</em>",
                f"<em>File type: {part['filetype']}; hash: {base64.b64decode(part['hash']).hex()}; " +
                f"dimensions: {part['width']}x{part['height']}</em>",
                f"<em>uri: {part['downloadUri']}</em>"
            ])
        elif content_type == "deeplink":
            processed.append(f"<em>Link text: {part['buttonText']}</em>")
            if part.get("appUri"):
                processed.append(f"<em>App URI: {part['appUri']}</em>")
            if part.get("webUri"):
                processed.append(f"<em>Web URI: {part['webUri']}</em>")
        else:
            print(part)
            raise NotImplementedError(f"Not implemented {content_type} in payload parts")
    return processed


def get_fcm_xbox(files_found, report_folder, seeker, wrap_text):
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    message_headers = ["FCM Key", "FCM Timestamp", "Conversation ID", "Message Timestamp", "Sender", "Text", "Content"]
    message_rows = []
    party_headers = ["FCM Key", "FCM Timestamp", "Sender"]
    party_rows = []
    presence_headers = ["FCM Key", "FCM Timestamp", "User"]
    presence_rows = []

    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == "com.microsoft.xboxone.smartglass":
                    notification_type = rec.key_values["type"]
                    if notification_type == "MESSAGE":
                        obj = json.loads(rec.key_values["xbl"])
                        payload = process_payload(json.loads(obj["messagePayload"]))
                        message_rows.append([
                            rec.key,
                            rec.timestamp,
                            obj["conversationId"],
                            unix_ms(obj["timestamp"]),
                            [obj["senderGamerTag"], obj["senderXuid"]],
                            obj["text"],
                            payload
                        ])

                    elif notification_type == "partyInvite":
                        obj = json.loads(rec.key_values["xbl"])["invite_handle"]
                        if obj["type"] != "invite":
                            raise NotImplementedError("Unknown partyInvite type")
                        party_rows.append([
                            rec.key,
                            rec.timestamp,
                            f"{obj['inviteInfo']['senderUniqueModernGamertag']} ({obj['senderXuid']})"
                        ])
                    elif notification_type == "presence":
                        presence_rows.append([
                            rec.key,
                            rec.timestamp,
                            f"{rec.key_values['gamertag']} ({rec.key_values['xuid']})"
                        ])

    source_files = " ".join(str(x) for x in in_dirs)

    def make_report(title, name, headers, rows):
        report = ArtifactHtmlReport(title)
        report_name = name
        report.start_artifact_report(report_folder, report_name)
        report.add_script()

        report.write_artifact_data_table(headers, rows, source_files)
        report.end_artifact_report()

        scripts.ilapfuncs.tsv(report_folder, headers, rows, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, rows, headers)

    if message_rows:
        make_report(
            "XBox Message Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Xbox Message Notifications",
            message_headers,
            message_rows
        )
    if party_rows:
        make_report(
            "XBox Party Invite Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Xbox Party Invite Notifications",
            party_headers,
            party_rows
        )
    if presence_rows:
        make_report(
            "XBox Presence Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Xbox Presence Notifications",
            presence_headers,
            presence_rows
        )
    if not message_rows and not party_rows and not presence_rows:
        scripts.ilapfuncs.logfunc("No Xbox FCM data found")


__artifacts__ = {
    "FCM_XBox": (
        "Firebase Cloud Messaging",
        ('*/fcm_queued_messages.ldb/*'),
        get_fcm_xbox)
}
