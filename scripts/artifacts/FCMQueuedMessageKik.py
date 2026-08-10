__artifacts_v2__ = {
    "fcm_kik": {
        "name": "FCM-KIK Notifications",
        "description": "Kik Notifications from FCM",
        "author": "@jfhyla",
        "creation_date": "2025-07-31",
        "last_update_date": "2025-07-31",
        "last_updated": "2025-07-31",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ("*/fcm_queued_messages.ldb/*"),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "database",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "fcm_kik_blanks": {
        "name": "FCM-KIK Notifications Blanks",
        "description": "Kik Notifications from FCM",
        "author": "@jfhyla",
        "creation_date": "2025-07-31",
        "last_update_date": "2025-07-31",
        "last_updated": "2025-07-31",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ("*/fcm_queued_messages.ldb/*"),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "database",
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
from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor


@artifact_processor
def fcm_kik(context):
    files_found = context.get_files_found()
    # we only need the input data dirs not every matching file
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    rows = []
    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == "kik.android":
                    if rec.key_values.get("body"):
                        rows.append([
                            rec.timestamp,
                            rec.key_values.get("body"),
                            rec.key_values.get("binId"),
                            rec.key_values.get("sts"),
                            rec.key_values.get("id"),
                            rec.key_values.get("google.c.sender.id")
                        ])


    data_headers = ["FCM Timestamp", "Body", "Bin ID", "STS", "ID", "google.c.sender.id"]
    source_files = " ".join(str(x) for x in in_dirs)

    return data_headers, rows, source_files


@artifact_processor
def fcm_kik_blanks(context):
    files_found = context.get_files_found()
    # we only need the input data dirs not every matching file
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    rows = []
    for in_db_path in in_dirs:
        with FcmIterator(in_db_path) as record_iterator:
            for rec in record_iterator:
                if rec.package == "kik.android":
                    if rec.key_values.get("google.c.sender.id") and len(rec.key_values) == 1:
                        rows.append([
                            rec.timestamp,
                            rec.key_values.get("google.c.sender.id")
                        ])

    data_headers = ["FCM Timestamp", "google.c.sender.id"]
    source_files = " ".join(str(x) for x in in_dirs)

    return data_headers, rows, source_files
