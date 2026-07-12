__artifacts_v2__ = {
    "get_offlinePages": {
        "name": "Offline Pages (MHTML)",
        "description": "Saved offline web pages (MHTML/MHT archives) with source URL, subject and capture time",
        "author": "",
        "creation_date": "2023-01-25",
        "last_update_date": "2023-01-25",
        "requirements": "none",
        "category": "Offline Pages",
        "notes": "",
        "paths": ('*/*.mhtml', '*/*.mht'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533 | 7 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 2 rows",
            "pixel7a_a14": "Android 14 | com.android.chrome vc 616710133, com.brave.browser vc 426712324, com.microsoft.emmx vc 259210005 | 8 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133 | 12 rows",
            "samsungs20_a13": "Android 13 | com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 7 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333 | 37 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 9 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 8 rows",
        },
    }
}

import datetime
import email
import os

from scripts.ilapfuncs import artifact_processor, check_in_media


@artifact_processor
def get_offlinePages(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        source_paths.append(file_found)

        timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(file_found), tz=datetime.timezone.utc)
        with open(file_found, 'r', errors='replace', encoding='utf-8') as fp:
            message = email.message_from_file(fp)
            web_source = message['Snapshot-Content-Location']
            subject = message['Subject']
            mime_date = message['Date']

        media = check_in_media(file_found, os.path.basename(file_found))
        data_list.append((timestamp, media, web_source, subject, mime_date, context.get_relative_path(file_found)))

    data_headers = (
        ('Timestamp', 'datetime'), ('File', 'media'), 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
    return data_headers, data_list, ', '.join(context.get_relative_path(p) for p in source_paths)
