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
    "get_fcm_skype": {
        "name": "FCM - Skype and Teams Messages",
        "description": "Skype (com.skype.raider) and Teams (com.microsoft.teams) message/call notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-01-01",
        "last_update_date": "2022-01-01",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_fcm_skype_notifications": {
        "name": "FCM - Skype and Teams Notifications",
        "description": "Skype/Teams other (e.g. missed-chat-reminder) notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-01-01",
        "last_update_date": "2022-01-01",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "bell",
    }
}

import datetime
import html
import html.entities
import json
import pathlib
import re
import urllib.parse
import xml.etree.ElementTree as etree
from html.parser import HTMLParser

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor, logfunc

_APP_IDS = {"com.skype.raider": "Skype", "com.microsoft.teams": "Teams"}


class JustGetTextParser(HTMLParser):
    def __init__(self, text_list: list):
        super().__init__(convert_charrefs=True)
        self._text_list = text_list

    def handle_data(self, data: str) -> None:
        self._text_list.append(data)

    def handle_entityref(self, name: str) -> None:
        self._text_list.append(chr(html.entities.name2codepoint[name]))

    def handle_charref(self, name: str) -> None:
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        self._text_list.append(c)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("div", "p"):
            self._text_list.append("\n")
        elif tag == "img":
            for k, v in attrs:
                if k == "alt":
                    self._text_list.append(v)
                    break


MESSAGE_TYPES = {"200": "Message", "201": "Message", "302": "Message", "305": "Message", "306": "Message"}
CALL_TYPES = {"107": "Call"}
MISSED_CALL_TYPES = {"110": "MissedCall"}
NOTIFICATION_TYPES = {"404": "Missed chat reminder"}
OTHER_TYPES = {"6": "Unknown", "115": "Unknown", "116": "Unknown", "117": "Unknown",
               "308": "User status change", "601": "Unknown - related to encryption key?",
               "1304": "Unknown", "1306": "Unknown", "1400": "Unknown"}
USER_TYPES = {"801": "User Details", "802": "User Details", "803": "User Details"}
KNOWN_TYPES = MESSAGE_TYPES | CALL_TYPES | MISSED_CALL_TYPES | USER_TYPES | NOTIFICATION_TYPES | OTHER_TYPES

STARTS_WITH_NUMBER = re.compile(r"^\d{1,2}:")
EPOCH = datetime.datetime(1970, 1, 1)


def unix_ms(ms):
    return EPOCH + datetime.timedelta(milliseconds=int(ms))


def _to_utc(value):
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone(datetime.timezone.utc)
    return value if value else ''


def _clean(text):
    '''Flatten the HTML-oriented content to plain text for LAVA/TSV.'''
    return html.unescape(str(text).replace('<em>', '').replace('</em>', ''))


def make_metadata_field(payload: dict, fields: dict, converters: dict):
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
            etree.tostring(content_ele, encoding="utf-8", method="text").decode("utf-8"), "",
            f"URI: {content_ele.get('uri')}", f"Doc ID: {content_ele.get('doc_id')}",
            f"Type: {content_ele.get('type')}"]
        fs_ele = content_ele.find("FileSize")
        og_name = content_ele.find("OriginalName")
        if fs_ele is not None:
            result.append(f"File Size: {fs_ele.get('v')}")
        if og_name is not None:
            result.append(f"Original Name: {og_name.get('v')}")
        result.append("")
        result.append(html.unescape(content))
        return result
    if content.startswith("<div"):
        chunks = []
        JustGetTextParser(chunks).feed(content)
        text = "".join(chunks).strip()
        return ["Text Content:", *text.splitlines(keepends=False), "", "Original Data:",
                html.unescape(content)]
    if content.startswith("<addmember"):
        content_ele = etree.fromstring(content)
        result = [f"Event Time: {unix_ms(content_ele.find('eventtime').text)}",
                  f"Initiator: {content_ele.find('initiator').text}", ""]
        result.extend(f"Target participant: {x.text}" for x in content_ele.findall('target'))
        result.append("")
        result.append(html.unescape(content))
        return result
    if content.startswith("<deletemember"):
        content_ele = etree.fromstring(content)
        result = [f"Event Time: {unix_ms(content_ele.find('eventtime').text)}",
                  f"Initiator: {content_ele.find('initiator').text}"]
        result.extend(f"Removed participant: {x.text}" for x in content_ele.findall('target'))
        result.append("")
        result.append(html.unescape(content))
        return result
    return html.unescape(content)


_CACHE = {}


def _load(files_found):
    key = tuple(sorted(str(f) for f in files_found))
    if key in _CACHE:
        return _CACHE[key]
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    source = " ".join(str(x) for x in in_dirs)
    call_id_to_conversation = {}
    messages, notifications = [], []
    for in_db_path in in_dirs:
        try:
            with FcmIterator(in_db_path) as record_iterator:
                for rec in record_iterator:
                    app_name = _APP_IDS.get(rec.package)
                    if not app_name:
                        continue
                    try:
                        event_type = rec.key_values.get("eventType")
                        if event_type not in KNOWN_TYPES:
                            continue
                        recipient_id = rec.key_values.get("recipientId")
                        ts = _to_utc(rec.timestamp)
                        if event_type in CALL_TYPES:
                            conversation_id = rec.key_values["convoId"]
                            call_id_to_conversation[rec.key_values["callId"]] = conversation_id
                            from_details = [rec.key_values["callerId"]]
                            if display_name := rec.key_values.get("displayName"):
                                from_details.insert(0, urllib.parse.unquote(display_name))
                            metadata = make_metadata_field(
                                rec.key_values,
                                {"Is video call?": "videoCall", "Participant ID": "participantId"}, {})
                            metadata.insert(0, f"FCM Key: {rec.key}")
                            messages.append((ts, app_name, rec.key_values.get("pnhTime"), conversation_id,
                                             recipient_id, "\n".join(from_details), "Call", "\n".join(metadata)))
                        elif event_type in MISSED_CALL_TYPES:
                            conversation_id = rec.key_values.get("conversationId") or \
                                call_id_to_conversation.get(rec.key_values.get("callId"))
                            messages.append((ts, app_name, rec.key_values.get("pnhTime"), conversation_id,
                                             recipient_id, rec.key_values.get("callerMri", conversation_id),
                                             "Missed Call Notification", f"Reason: {rec.key_values.get('reason')}"))
                        elif event_type in MESSAGE_TYPES:
                            conversation_id = STARTS_WITH_NUMBER.sub("", rec.key_values["conversationId"], 1)
                            payload = json.loads(rec.key_values["rawPayload"])
                            metadata = make_metadata_field(
                                payload,
                                {"ID": "id", "Client Message ID": "clientmessageid", "Thread Topic": "threadtopic",
                                 "Conversation Link": "conversationLink", "Message type": "messagetype",
                                 "Content type": "contenttype"}, {})
                            metadata.insert(0, f"FCM Key: {rec.key}")
                            from_details = [payload["from"]]
                            if display_name := payload.get("imdisplayname"):
                                from_details.insert(0, display_name)
                            content = process_content(payload["content"])
                            if isinstance(content, list):
                                content = "\n".join(content)
                            messages.append((ts, app_name, payload.get("originalarrivaltime"), conversation_id,
                                             recipient_id, "\n".join(from_details), _clean(content),
                                             "\n".join(metadata)))
                        elif event_type in NOTIFICATION_TYPES:
                            notifications.append((ts, app_name, rec.key_values.get("title"),
                                                  rec.key_values.get("msg"), rec.key_values.get("recipientId"),
                                                  rec.key_values.get("link")))
                    except (KeyError, ValueError, TypeError, json.JSONDecodeError, etree.ParseError) as exc:
                        logfunc(f"Skype/Teams FCM: could not parse {rec.package} record: {exc}")
        except Exception as exc:  # pylint: disable=W0718
            logfunc(f"Skype/Teams FCM: error reading {in_db_path}: {exc}")
    _CACHE[key] = (messages, notifications, source)
    return _CACHE[key]


@artifact_processor
def get_fcm_skype(files_found, report_folder, seeker, wrap_text):
    messages, _notifications, source = _load(files_found)
    data_headers = (('FCM Timestamp', 'datetime'), 'App', 'Original Timestamp', 'Conversation ID',
                    'Recipient', 'Sender', 'Content', 'Metadata')
    return data_headers, messages, source


@artifact_processor
def get_fcm_skype_notifications(files_found, report_folder, seeker, wrap_text):
    _messages, notifications, source = _load(files_found)
    data_headers = (('Timestamp', 'datetime'), 'App', 'Title', 'Message', 'Recipient', 'Link')
    return data_headers, notifications, source
