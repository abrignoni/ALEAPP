# pylint: disable=W0613
__artifacts_v2__ = {
    "get_firefoxDownloads": {
        "name": "Firefox - Downloads",
        "description": "Parses Firefox downloads (created time, file name, URL, MIME type, size, status and destination) from the mozac downloads database.",
        "author": "",
        "creation_date": "2022-01-12",
        "last_update_date": "2022-01-12",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/databases/mozac_downloads_database*',),
        "output_types": "standard",
        "artifact_icon": "globe",
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_firefoxDownloads(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'mozac_downloads_database':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        file_name AS FileName,
        url AS URL,
        content_type AS MimeType,
        content_length AS FileSize,
        CASE status
            WHEN 3 THEN 'Paused'
            WHEN 4 THEN 'Canceled'
            WHEN 5 THEN 'Failed'
            WHEN 6 THEN 'Finished'
        END AS Status,
        destination_directory AS DestDir
        FROM downloads
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6]))

        db.close()

    data_headers = (
        ('Created Timestamp', 'datetime'),
        'File Name',
        'URL',
        'MIME Type',
        'File Size (Bytes)',
        'Status',
        'Destination Directory',
    )
    return data_headers, data_list, source_path
