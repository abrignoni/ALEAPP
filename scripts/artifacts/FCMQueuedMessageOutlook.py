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

__version__ = "0.2"
__description__ = """
Reads records from the fcm_queued_messages.ldb leveldb in com.google.android.gms related to 
com.microsoft.office.outlook"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"


def get_fcm_outlook(files_found, report_folder, seeker, wrap_text, time_offset):
    # we only need the input data dirs not every matching file
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    rows = []
    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == "com.microsoft.office.outlook":
                    if rec.key_values["type"] == "OutlookPushNotification":
                        hx_message = json.loads(rec.key_values["HxMessage"])
                        for notification in hx_message["NewMailNotifications"]:
                            rows.append([
                                rec.timestamp,
                                notification["ReceivedOrRenewTime"],
                                rec.key,
                                [hx_message["TenantGuid"], hx_message["MailboxGuid"]],
                                notification["Sender"],
                                notification["Topic"],
                                notification["Preview"]
                            ])
                    else:
                        print(rec.key_values)
                        raise ValueError(f"Unknown type {rec.key_values['type']}")

    if rows:
        report = ArtifactHtmlReport("Outlook Notifications (Firebase Cloud Messaging Queued Messages)")
        report_name = "FCM-Outlook Notifications"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        data_headers = ["FCM Timestamp", "Received / Renew Time", "FCM Key", "Tenant / Mailbox GUID", "Sender", "Topic", "Preview"]
        source_files = " ".join(str(x) for x in in_dirs)

        report.write_artifact_data_table(data_headers, rows, source_files)
        report.end_artifact_report()

        scripts.ilapfuncs.tsv(report_folder, data_headers, rows, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, rows, data_headers)
    else:
        scripts.ilapfuncs.logfunc("No FCM Outlook notifications found")


__artifacts__ = {
        "FCM_Outlook": (
                "Firebase Cloud Messaging",
                ('*/fcm_queued_messages.ldb/*'),
                get_fcm_outlook)
}