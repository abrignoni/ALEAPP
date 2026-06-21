# pylint: disable=W0613
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
        "artifact_icon": "message-square",
    }
}

import datetime
import email
import os

from scripts.ilapfuncs import artifact_processor, check_in_media


@artifact_processor
def get_offlinePages(files_found, report_folder, seeker, wrap_text):
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
        data_list.append((timestamp, media, web_source, subject, mime_date, file_found))

    data_headers = (
        ('Timestamp', 'datetime'), ('File', 'media'), 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
    return data_headers, data_list, ', '.join(source_paths)
