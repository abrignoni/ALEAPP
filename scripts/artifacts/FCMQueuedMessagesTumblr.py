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
    "get_fcm_tumblr": {
        "name": "FCM - Tumblr Messages",
        "description": "Tumblr message notifications from fcm_queued_messages.ldb (com.tumblr)",
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
    "get_fcm_tumblr_flagged": {
        "name": "FCM - Tumblr Flagged Posts",
        "description": "Tumblr flagged-post / appeal notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-01-01",
        "last_update_date": "2022-01-01",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "flag",
    },
    "get_fcm_tumblr_notifications": {
        "name": "FCM - Tumblr Notifications",
        "description": "Tumblr general (deeplink) notifications from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-01-01",
        "last_update_date": "2022-01-01",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "bell",
    },
    "get_fcm_tumblr_logs": {
        "name": "FCM - Tumblr Logs",
        "description": "Tumblr logging_data push records from fcm_queued_messages.ldb",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-01-01",
        "last_update_date": "2022-01-01",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    }
}

import datetime
import json
import pathlib

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor, logfunc

_CACHE = {}
_FLAG_LABELS = {"post_flagged": "Post Flagged", "appeal_verdict_granted": "Appeal granted",
                "appeal_verdict_denied": "Appeal denied"}


def _to_utc(value):
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value.astimezone(datetime.timezone.utc)
    return value if value else ''


def _load(files_found):
    key = tuple(sorted(str(f) for f in files_found))
    if key in _CACHE:
        return _CACHE[key]
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    source = " ".join(str(x) for x in in_dirs)
    messages, flagged, notifications, logs = [], [], [], []
    for in_db_path in in_dirs:
        try:
            with FcmIterator(in_db_path) as record_iterator:
                for rec in record_iterator:
                    if rec.package != "com.tumblr":
                        continue
                    ts = _to_utc(rec.timestamp)
                    for k, value in rec.key_values.items():
                        try:
                            if k == "logging_data":
                                vo = json.loads(value)
                                logs.append((ts, rec.key, vo.get("push_id"), vo.get("push_type")))
                            elif k == "message":
                                vo = json.loads(value)
                                mtype = vo.get("type")
                                if mtype == "Message":
                                    messages.append((ts, rec.key, vo.get("title"), vo.get("body"),
                                                     vo.get("notification"), vo.get("recipient"),
                                                     vo.get("uuid"),
                                                     (vo.get("conversation") or {}).get("unread")))
                                elif mtype == "DEEPLINK_CATEGORY":
                                    notifications.append((ts, rec.key, vo.get("body")))
                                elif mtype in _FLAG_LABELS:
                                    flagged.append((ts, rec.key, vo.get("to_tumblelog_name"),
                                                    vo.get("post_id"), _FLAG_LABELS[mtype]))
                                # NewPost / untyped / unknown types are ignored
                        except (KeyError, ValueError, TypeError) as exc:
                            logfunc(f"Tumblr FCM: could not parse '{k}' record: {exc}")
        except Exception as exc:  # pylint: disable=W0718
            logfunc(f"Tumblr FCM: error reading {in_db_path}: {exc}")
    _CACHE[key] = (messages, flagged, notifications, logs, source)
    return _CACHE[key]


@artifact_processor
def get_fcm_tumblr(files_found, report_folder, seeker, wrap_text):
    messages, _flagged, _notifications, _logs, source = _load(files_found)
    data_headers = (('Timestamp', 'datetime'), 'FCM Key', 'Title', 'Body', 'Notification',
                    'Recipient', 'Uuid', 'Unread Count')
    return data_headers, messages, source


@artifact_processor
def get_fcm_tumblr_flagged(files_found, report_folder, seeker, wrap_text):
    _messages, flagged, _notifications, _logs, source = _load(files_found)
    data_headers = (('Timestamp', 'datetime'), 'FCM Key', 'Blog Name', 'Post ID', 'Type')
    return data_headers, flagged, source


@artifact_processor
def get_fcm_tumblr_notifications(files_found, report_folder, seeker, wrap_text):
    _messages, _flagged, notifications, _logs, source = _load(files_found)
    data_headers = (('Timestamp', 'datetime'), 'FCM Key', 'Notification')
    return data_headers, notifications, source


@artifact_processor
def get_fcm_tumblr_logs(files_found, report_folder, seeker, wrap_text):
    _messages, _flagged, _notifications, logs, source = _load(files_found)
    data_headers = (('Timestamp', 'datetime'), 'FCM Key', 'Push ID', 'Push Type')
    return data_headers, logs, source
