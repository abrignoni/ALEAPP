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

import json
import pathlib
from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

__version__ = "1.1"
__description__ = """
Reads records from the fcm_queued_messages.ldb leveldb in com.google.android.gms related to com.tumblr"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"


def get_fcm_instagram(files_found, report_folder, seeker, wrap_text):
    # we only need the input data dirs not every matching file
    in_dirs = set(pathlib.Path(x).parent for x in files_found)

    message_headers = ["Timestamp", "fcm_key", "Title", "Body", "Notification", "Recipient", "Uuid", "Unread Count"]
    message_rows = []
    flagged_post_headers = ["Timestamp", "fcm_key", "Blog Name", "Post ID", "Type"]
    flagged_post_rows = []
    notification_headers = ["Timestamp", "fcm_key", "Notification"]
    notification_rows = []
    log_headers = ["Timestamp", "fcm_key", "Push ID", "Push Type"]
    log_rows = []

    # blog_names = set()

    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == "com.tumblr":
                    for key, value in rec.key_values.items():
                        if key == "logging_data":
                            value_obj = json.loads(value)
                            log_rows.append([rec.timestamp, rec.key, value_obj["push_id"], value_obj["push_type"]])
                        elif key == "google.c.sender.id":
                            pass
                        elif key == "message":
                            value_obj = json.loads(value)
                            message_type = value_obj.get("type")
                            if message_type is None:
                                if "check_for_notifications" in value_obj:
                                    continue
                                else:
                                    print(value)
                                    raise ValueError(f"Unknown untyped message")

                            if message_type == "Message":
                                conv_id = value_obj["conversation"]["id"]

                                message_rows.append([
                                    rec.timestamp, rec.key, value_obj["title"], value_obj["body"],
                                    value_obj["notification"], value_obj["recipient"], value_obj["uuid"],
                                    value_obj["conversation"]["unread"]
                                ])

                            elif message_type == "NewPost":
                                pass
                            elif message_type == "DEEPLINK_CATEGORY":
                                notification_rows.append([rec.timestamp, rec.key, value_obj["body"]])
                            elif message_type == "post_flagged":
                                flagged_post_rows.append(
                                    [rec.timestamp, rec.key, value_obj["to_tumblelog_name"],
                                     value_obj["post_id"], "Post Flagged"])
                            elif message_type == "appeal_verdict_granted":
                                flagged_post_rows.append(
                                    [rec.timestamp, rec.key, value_obj["to_tumblelog_name"],
                                     value_obj["post_id"], "Appeal granted"])
                            elif message_type == "appeal_verdict_denied":
                                flagged_post_rows.append(
                                    [rec.timestamp, rec.key, value_obj["to_tumblelog_name"],
                                     value_obj["post_id"], "Appeal denied"])
                            else:
                                raise ValueError(f"Unknown message type: {message_type}")

                        elif key == "blog_name":
                            # blog_names.add(value)  # I think this is a blog managed by the local use, but need to check
                            pass
                        elif key == "check_for_notifications":
                            pass  # just returns true when notifications are checked... maybe useful in niche situations?
                        else:
                            raise ValueError("Unknown key - contact R&D")


    # write reports
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
            "Tumblr Message Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Tumblr Message Notifications",
            message_headers,
            message_rows
        )
    else:
        scripts.ilapfuncs.logfunc("No FCM Tumblr message notifications found")

    if flagged_post_rows:
        make_report(
            "Tumblr Flagged Post Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Tumblr Flagged Post Notifications",
            flagged_post_headers,
            flagged_post_rows
        )
    else:
        scripts.ilapfuncs.logfunc("No FCM Tumblr flagged post notifications found")

    if notification_rows:
        make_report(
            "Tumblr General Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Tumblr General Notifications",
            notification_headers,
            notification_rows
        )
    else:
        scripts.ilapfuncs.logfunc("No FCM Tumblr general notifications found")

    if log_rows:
        make_report(
            "Tumblr Log Notifications (Firebase Cloud Messaging Queued Messages)",
            "FCM-Tumblr Log Notifications",
            log_headers,
            log_rows
        )
    else:
        scripts.ilapfuncs.logfunc("No FCM Tumblr log notifications found")
