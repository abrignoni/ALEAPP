__artifacts_v2__ = {
    "One Drive": {
        "name": "OneDrive Metadata",
        "description": "Parses the QTMetadata.db from OneDrive",
        "author": "Matt Beers and Anthony Reince",
        "version": "0.0.9",
        "date": "2025-04-17",
        "requirements": "none",
        "category": "Cloud Storage",
        "notes": "",
        "paths": ('*/com.microsoft.skydrive/files/QTMetadata.db*'),
        "function": "get_onedrive",
        "artifact_icon": "cloud"
    }
}

import sqlite3
import os
import mimetypes
import base64

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, open_sqlite_db_readonly

def get_onedrive(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('QTMetadata.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT 
                datetime(items.itemDate/1000,'unixepoch') AS Item_Date,
                items._id,
                items.extension,
                items.name,
                items.ownerName,
                items.sha1Hash, 
                stream_cache.parentID,
                stream_cache.stream_location
            FROM
                items
            LEFT JOIN 
                stream_cache
            ON items._id = stream_cache.parentID
            ORDER BY Item_Date ASC;
            ''')

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    timestamp = row[0]
                    item_id = row[1]
                    extension = row[2] or ''
                    name = row[3]
                    owner = row[4]
                    sha1 = row[5]
                    parent_id = row[6]
                    stream_path = row[7]
                    preview = ''

                    if stream_path:
                        # Normalize for matching
                        stream_path_norm = os.path.normpath(stream_path).lower().lstrip(os.sep)
                        stream_path_tail = os.path.join(*stream_path_norm.split(os.sep)[-6:]).replace('\\', '/')

                        matches = seeker.search(f'*{os.path.basename(stream_path)}')
                        found_file = None

                        for match in matches:
                            match_path_norm = os.path.normpath(str(match)).lower().replace('\\', '/')
                            if stream_path_tail in match_path_norm:
                                found_file = match
                                break

                        if found_file:
                            guessed_mime = mimetypes.types_map.get(f".{extension.lower().lstrip('.')}", None)

                            try:
                                with open(found_file, 'rb') as f:
                                    data = f.read()

                                if guessed_mime:
                                    if guessed_mime.startswith('image'):
                                        b64img = base64.b64encode(data).decode('utf-8')
                                        preview = (
                                            f'<img src="data:{guessed_mime};base64,{b64img}" height="100" '
                                            f'style="border: 1px solid #ccc; border-radius: 6px;" />'
                                        )
                                    elif guessed_mime.startswith('text'):
                                        text = data.decode('utf-8', errors='ignore')[:300]
                                        preview = f'<pre>{text}</pre>'
                                    else:
                                        preview = f"<i>{guessed_mime} ({len(data)} bytes)</i>"
                                else:
                                    preview = f"<i>Unknown file type ({len(data)} bytes)</i>"

                            except Exception as e:
                                preview = f"<i>Error rendering file: {e}</i>"
                        else:
                            preview = "<i>File not found in ZIP/TAR</i>"
                    else:
                        preview = "<i>No stream path provided</i>"

                    data_list.append((
                        timestamp,
                        item_id,
                        extension,
                        name,
                        owner,
                        sha1,
                        parent_id,
                        stream_path,
                        preview
                    ))
            db.close()

    if data_list:
        description = 'OneDrive Metadata'
        report = ArtifactHtmlReport('OneDrive Metadata')
        report.start_artifact_report(report_folder, 'OneDrive Metadata', description)
        report.add_script()
        data_headers = (
            'Item Date', 'ID', 'Extension', 'File or Folder Name', 'Owner Name',
            'Sha1 Hash', 'Parent ID', 'Stream Location', 'Preview')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsvname = 'OneDrive Metadata'
        tsv(report_folder, data_headers[:-1], [row[:-1] for row in data_list], tsvname)

        timeline(report_folder, 'OneDrive Metadata', data_list, data_headers)
    else:
        logfunc('No OneDrive Metadata data available')
