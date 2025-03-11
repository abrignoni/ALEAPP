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
import sys
import datetime
import json
import typing
import html
import re
import urllib.parse
from html.parser import HTMLParser
import html.entities
import xml.etree.ElementTree as etree
from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs


__version__ = "0.4.0"
__description__ = """
Reads records from the fcm_queued_messages.ldb leveldb in com.google.android.gms related to com.skype.raider or 
com.microsoft.teams"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"


def prepare_main_args(package: str, input_dir, output_dir):
    if package == "com.skype.raider":
        return [input_dir, output_dir, "-s"]
    elif package == "com.microsoft.teams":
        return [input_dir, output_dir, "-t"]
    raise ValueError(f"Unexpected package: {package}")


class JustGetTextParser(HTMLParser):
    def __init__(self, text_list: list):
        super().__init__(convert_charrefs=True)
        self._text_list = text_list

    def handle_data(self, data: str) -> None:
        self._text_list.append(data)

    def handle_entityref(self, name: str) -> None:
        self._text_list.append(html.entities.name2codepoint[name])

    def handle_charref(self, name: str) -> None:
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        self._text_list.append(c)

    def handle_starttag(self, tag: str, attrs: list[tuple]) -> None:
        if tag in ("div", "p"):
            self._text_list.append("\n")
        elif tag == "img":
            for k, v in attrs:
                if k == "alt":
                    self._text_list.append(v)
                    break


MESSAGE_TYPES = {
    "200": "Message",
    "201": "Message",
    "302": "Message",  # with (url?) attachment?
    "305": "Message",  # with (video?) attachment?
    "306": "Message",  # with (generic file) attachments?
}

CALL_TYPES = {
    "107": "Call",
}

MISSED_CALL_TYPES = {
    "110": "MissedCall"
}

USER_TYPES = {
    "801": "User Details",  # invite?
    "802": "User Details",  # invite?
    "803": "User Details",  # invite?
}

NOTIFICATION_TYPES = {
    "404": "Missed chat reminder"
}

OTHER_TYPES = {
    "6": "Unknown",
    "115": "Unknown",  # something like a status change maybe?
    "116": "Unknown",  # something like a status change maybe?
    "117": "Unknown",  # something like a status change maybe?
    "308": "User status change",  # I think
    "601": "Unknown - related to encryption key?",
    "1304": "Unknown",  # Something to do with groups?
    "1306": "Unknown",
    "1400": "Unknown"
}

KNOWN_TYPES = MESSAGE_TYPES | CALL_TYPES | MISSED_CALL_TYPES | USER_TYPES | NOTIFICATION_TYPES | OTHER_TYPES

STARTS_WITH_NUMBER = re.compile(r"^\d{1,2}:")

EPOCH = datetime.datetime(1970, 1, 1)


def unix_ms(ms: int):
    return EPOCH + datetime.timedelta(milliseconds=ms)


def make_metadata_field(
        payload: dict, fields: dict[str, str], converters: dict[str, typing.Callable[[typing.Any], typing.Any]]):
    result = []
    for field_name, key in fields.items():
        value = payload.get(key)
        if not value:
            continue

        value = converters.get(field_name, lambda x: x)(value)
        result.append(f"{field_name}: {value}")

    return result


def process_content(content: str):
    if content.startswith("<URIObject"):
        content_ele = etree.fromstring(content)
        result = [
            etree.tostring(content_ele, encoding="utf-8", method="text").decode("utf-8"),
            "",
            f"<em>URI: {content_ele.get('uri')}</em>",
            f"<em>Doc ID: {content_ele.get('doc_id')}</em>",
            f"<em>Type: {content_ele.get('type')}</em>"
        ]

        fs_ele = content_ele.find("FileSize")
        og_name = content_ele.find("OriginalName")
        if fs_ele is not None:
            result.append(f"<em>File Size: {fs_ele.get('v')}</em>")
        if og_name is not None:
            result.append(f"<em>Original Name: {og_name.get('v')}</em>")
        result.append("")
        result.append(html.escape(html.unescape(content), quote=False))
        return result
    elif content.startswith("<div"):
        chunks = []
        parser = JustGetTextParser(chunks)
        parser.feed(content)
        text = "".join(chunks).strip()

        result = [
            "<em>Text Content:</em>",
            *text.splitlines(keepends=False),
            "",
            "<em>Original Data:</em>",
            html.escape(html.unescape(content), quote=False)
        ]
        return result
    elif content.startswith("<addmember"):
        content_ele = etree.fromstring(content)
        result = [
            f"<em>Event Time: {unix_ms(int(content_ele.find('eventtime').text))}</em>",
            f"<em>Initiator: {content_ele.find('initiator').text}</em>",
            ""
        ]
        result.extend(f"<em>Target participant: {x.text}</em>" for x in content_ele.findall('target'))
        result.append("")
        result.append(html.escape(html.unescape(content), quote=False))
        return result
    elif content.startswith("<deletemember"):
        content_ele = etree.fromstring(content)
        result = [
            f"<em>Event Time: {unix_ms(int(content_ele.find('eventtime').text))}</em>",
            f"<em>Initiator: {content_ele.find('initiator').text}</em>",
        ]
        result.extend(f"<em>Removed participant: {x.text}</em>" for x in content_ele.findall('target'))
        result.append("")
        result.append(html.escape(html.unescape(content), quote=False))
        return result
    else:
        return html.escape(html.unescape(content), quote=False)


def get_fcm_skype(files_found, report_folder, seeker, wrap_text, mode):
    if mode == "s":
        app_name = "Skype"
        app_id = "com.skype.raider"
        print("Skype mode")
    elif mode == "t":
        app_name = "Teams"
        app_id = "com.microsoft.teams"
        print("Teams mode")
    else:
        raise ValueError(f"Mode '{mode}' not understood.")

    message_table_header = [
        "FCM Timestamp", "Original Timestamp", "Conversation ID", "Recipient", "From", "Content", "Metadata"]
    notification_table_header = ["Timestamp", "Title", "Message", "Recipient", "Link"]

    # in Teams missed calls don't have a conversation ID but the call that was missed does, so we can look them up later
    call_id_to_conversation = {}
    unknown_event_types = set()
    message_rows = []
    notification_rows = []

    # we only need the input data dirs not every matching file
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == app_id:
                    if rec.key_values["eventType"] not in KNOWN_TYPES:
                        unknown_event_types.add(rec.key_values["eventType"])
                        continue

                    event_type = rec.key_values["eventType"]
                    recipient_id = rec.key_values.get("recipientId")

                    if event_type in CALL_TYPES:
                        conversation_id = rec.key_values["convoId"]
                        call_id_to_conversation[rec.key_values["callId"]] = conversation_id

                        from_details = [rec.key_values["callerId"]]
                        if display_name := rec.key_values.get("displayName"):
                            from_details.insert(0, urllib.parse.unquote(display_name))

                        metadata = make_metadata_field(
                            rec.key_values,
                            {
                                "Is video call?": "videoCall",
                                "Participant ID": "participantId"
                            },
                            {}
                        )
                        metadata.insert(0, f"FCM Key: {rec.key}")

                        message_rows.append([
                            rec.timestamp,
                            rec.key_values.get("pnhTime"),  # Teams doesn't always have this.
                            conversation_id,
                            recipient_id,
                            "\n".join(from_details),
                            "<em>Call</em>",
                            "\n".join(metadata)
                        ])

                    elif event_type in MISSED_CALL_TYPES:
                        conversation_id = rec.key_values.get("conversationId")
                        if conversation_id is None:
                            conversation_id = call_id_to_conversation[rec.key_values["callId"]]

                        message_rows.append([
                            rec.timestamp,
                            rec.key_values.get("pnhTime"),  # Teams doesn't always have this
                            conversation_id,
                            recipient_id,
                            rec.key_values.get("callerMri", conversation_id),
                            "<em>Missed Call Notification</em>",
                            f"Reason: {rec.key_values['reason']}"
                        ])

                    elif event_type in MESSAGE_TYPES:
                        conversation_id = rec.key_values["conversationId"]
                        # trim the number at the start for the lookup, so it can be used consistently with calls
                        conversation_id = STARTS_WITH_NUMBER.sub("", conversation_id, 1)
                        payload = json.loads(rec.key_values["rawPayload"])
                        metadata = make_metadata_field(
                            payload,
                            {
                                "ID": "id",
                                "Client Message ID": "clientmessageid",
                                "Thread Topic": "threadtopic",
                                "Conversation Link": "conversationLink",
                                "Message type": "messagetype",
                                "Content type": "contenttype",
                             },
                            {}
                        )
                        metadata.insert(0, f"FCM Key: {rec.key}")
                        from_details = [payload["from"]]
                        if display_name := payload.get("imdisplayname"):
                            from_details.insert(0, display_name)

                        content = process_content(payload["content"])
                        if isinstance(content, list):
                            content = "\n".join(content)

                        message_rows.append([
                            rec.timestamp,
                            payload["originalarrivaltime"],
                            conversation_id,
                            recipient_id,
                            "\n".join(from_details),
                            content,
                            "\n".join(metadata)
                        ])
                    elif event_type in NOTIFICATION_TYPES:
                        # ["Timestamp", "Title", "Message", "Recipient", "Link"]
                        notification_rows.append([
                            rec.timestamp,
                            rec.key_values["title"],
                            rec.key_values["msg"],
                            rec.key_values["recipientId"],
                            rec.key_values["link"]
                        ])

    if message_rows:
        report = ArtifactHtmlReport(f"{app_name} Message Notifications (Firebase Cloud Messaging Queued Messages)")
        report_name = f"FCM-{app_name} Message Notifications"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()

        source_files = " ".join(str(x) for x in in_dirs)

        report.write_artifact_data_table(message_table_header, message_rows, source_files, html_escape=False)
        report.end_artifact_report()

        scripts.ilapfuncs.tsv(report_folder, message_table_header, message_rows, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, message_rows, message_table_header)
    else:
        scripts.ilapfuncs.logfunc(f"No FCM {app_name} message notifications found")

    if notification_rows:
        report = ArtifactHtmlReport(f"{app_name} Other Notifications (Firebase Cloud Messaging Queued Messages)")
        report_name = f"FCM-{app_name} Other Notifications"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()

        source_files = " ".join(str(x) for x in in_dirs)

        report.write_artifact_data_table(notification_table_header, notification_rows, source_files, html_escape=False)
        report.end_artifact_report()

        scripts.ilapfuncs.tsv(report_folder, notification_table_header, notification_rows, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, notification_rows, notification_table_header)
    else:
        scripts.ilapfuncs.logfunc(f"No FCM {app_name} other notifications found")


__artifacts__ = {
    "FCM_Skype": (
        "Firebase Cloud Messaging",
        ('*/fcm_queued_messages.ldb/*'),
        lambda a, b, c, d: get_fcm_skype(a, b, c, d, "s")),
    "FCM_Teams": (
        "Firebase Cloud Messaging",
        ('*/fcm_queued_messages.ldb/*'),
        lambda a, b, c, d: get_fcm_skype(a, b, c, d, "t"))
}
