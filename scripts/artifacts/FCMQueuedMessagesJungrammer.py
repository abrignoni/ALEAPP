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

import pathlib
import datetime
import dataclasses
from scripts.ccl.ccl_android_fcm_queued_messages import FcmRecord, FcmIterator
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

__version__ = "0.2.0"
__description__ = """
Reads records from the fcm_queued_messages.ldb leveldb in com.google.android.gms related to various kr.jungrammer apps 
"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"

KNOWN_JUNGRAMMERS = {
    "kr.jungrammer.bluetalk",
    "kr.jungrammer.randomchat",
    "kr.jungrammer.superranchat",
    "kr.jungrammer.talkchat"
}

EXPECTED_PACKAGES = tuple(KNOWN_JUNGRAMMERS)
RUN_PER_PACKAGE = False


def might_be_jungrammer_actually(rec: FcmRecord):
    if rec.package.startswith("kr.jungrammer"):
        return True
    if rec.key_values.get("google.c.sender.id") == "717420241212":
        return True
    if "fromToken" in rec.key_values:
        from_token = rec.key_values["fromToken"].split(":")
        if len(from_token) == 2 and len(from_token[0]) == 22 and len(from_token[1]) == 140:
            return True

    return False


@dataclasses.dataclass(frozen=True, eq=True)
class OtherParty:
    user_id: str
    user_key: str
    nickname: str
    client_type: str
    country_code: str

    def to_annotation(self):
        return (
            f"User ID: {self.user_id} \n" +
            f"User Key: {self.user_key} \n" +
            f"Nickname: {self.nickname} \n" +
            f"Country Code: {self.country_code} \n" +
            f"Client Type: {self.client_type}"
        )


@dataclasses.dataclass(frozen=True)
class Message:
    message: str
    timestamp: datetime.datetime
    message_type: str


class MessagePackage:
    def __init__(self, from_token: str, package: str):
        self.from_token = from_token
        self.package = package
        self.messages: list[Message] = []
        self.other_party_details: list[OtherParty] = []


def get_fcm_jungrammer(files_found, report_folder, seeker, wrap_text):
    in_dirs = set(pathlib.Path(x).parent for x in files_found)

    maybe_jungrammer = set()
    definitely_jungrammer = set()

    conversations: dict[str, MessagePackage] = {}  # key is package-fromToken
    relevant_types = {"CONNECT", "MESSAGE", "DISCONNECT", "NOTICE"}

    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package in KNOWN_JUNGRAMMERS:
                    definitely_jungrammer.add(rec.package)
                    if rec.key_values.get("type") in relevant_types:
                        # special case for some notices not belonging to a conversation
                        if rec.key_values["type"] == "NOTICE" and "fromToken" not in rec.key_values:
                            continue
                        conv_key = f"{rec.package}-{rec.key_values['fromToken']}"
                        conversations.setdefault(conv_key, MessagePackage(rec.key_values['fromToken'], rec.package))

                        if rec.key_values["type"] == "CONNECT":
                            op = OtherParty(
                                rec.key_values["userId"],
                                rec.key_values["userKey"],
                                rec.key_values["nickname"],
                                rec.key_values["clientType"],
                                rec.key_values["countryCode"],
                            )

                            conversations[conv_key].other_party_details.append(op)
                            conversations[conv_key].messages.append(
                                Message(
                                    op.to_annotation(),
                                    rec.timestamp,
                                    rec.key_values["type"]
                                ))
                        else:
                            conversations[conv_key].messages.append(
                                Message(
                                    rec.key_values.get("message"),
                                    rec.timestamp,
                                    rec.key_values["type"]
                                ))

                elif might_be_jungrammer_actually(rec):
                    maybe_jungrammer.add(rec.package)

    if conversations:
        rows = []
        for conv_key, conversation in conversations.items():
            for message in conversation.messages:
                rows.append(
                    [
                        message.timestamp,
                        conv_key,
                        conversation.package,
                        "\n".join(x.to_annotation() for x in conversation.other_party_details),
                        conversation.from_token,
                        message.message_type,
                        message.message
                    ])

        report = ArtifactHtmlReport("Jungrammer Notifications (Firebase Cloud Messaging Queued Messages)")
        report_name = "FCM-Jungrammer Notifications"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        data_headers = [
            "Timestamp", "Conversation Key", "Package", "Other Party Details", "From Token", "Message Type", "Message"
        ]
        source_files = " ".join(str(x) for x in in_dirs)

        report.write_artifact_data_table(data_headers, rows, source_files)
        report.end_artifact_report()

        scripts.ilapfuncs.tsv(report_folder, data_headers, rows, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, rows, data_headers)

        scripts.ilapfuncs.logfunc("Data relating to the following known Jungrammer apps was processed:")
        scripts.ilapfuncs.logfunc("\n".join(definitely_jungrammer))

        if maybe_jungrammer:
            scripts.ilapfuncs.logfunc(
                "The following packages were identified which may also be related to the same set of apps but were not "
                "processed:")
            scripts.ilapfuncs.logfunc("\n".join(maybe_jungrammer))
            scripts.ilapfuncs.logfunc("Please contact the developer of this plugin as this should be easy to fix!")
            scripts.ilapfuncs.logfunc()
    else:
        scripts.ilapfuncs.logfunc("No FCM Jungrammer notifications found")


__artifacts__ = {
    "FCM_Jungrammer": (
        "Firebase Cloud Messaging",
        ('*/fcm_queued_messages.ldb/*'),
        get_fcm_jungrammer)
}
