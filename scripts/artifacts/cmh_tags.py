__artifacts_v2__ = {
    "cmh_tags": {
        "name": "CMH Tags",
        "description": "Parses tags made by Samsung's CMHProvider on image files.",
        "date": "2025-05-05",
        "notes": "No records from deleted files are kept in the database.",
        "author": "Panagiotis Nakoutis - @4n6equals10",
        "requirements": "none",
        "category": "Samsung_CMH",
        "paths": ('*/cmh.db'),
        "function": "get_cmh_tags",
    }
}

import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_cmh_tags(files_found, report_folder, seeker, wrap_text):
#files and tags
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
        f._id as file_id,
        f.title,
        f._data,
        DATETIME(f.date_added, 'unixepoch') as date_added,
        DATETIME(f.date_modified, 'unixepoch') as date_modified,
        f.latitude,
        f.longitude,
        DATETIME(f.datetaken/1000, 'unixepoch') as datetaken,
        f.bucket_display_name,
        f.tags,
        f.color_detected,
        f.action_detected,
        f.image_url,
        f.vendor,
        f.is_edited,
        f.mime_type,
        f.hash_value,
        COALESCE(t.tag_display_name, 'No Tags') AS tag_name,
        COALESCE(t.tag_data, '') AS tag_data,
        ot.image_ocr_tag,
        DATETIME(ot.tag_added_date/1000, 'unixepoch') AS ocr_tag_added_date,
        ot.version
        ut.user_tag_id,
        ut.user_tag_data,
        DATETIME(ut.timestamp/1000, 'unixepoch') as usertag_timestamp
    FROM files f
    LEFT JOIN tag_map tm ON f._id = tm.fk_file_id
    LEFT JOIN tags t ON tm.fk_tag_id = t.tags_id
    LEFT JOIN ocr_tag ot ON f._id = ot.fk_file_id
    ORDER BY f._id;
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung CMH tags')
        report.start_artifact_report(report_folder, f'Samsung CMH tags')
        report.add_script()
        data_headers = ('file id', 'File name', 'Full Path', 'date added', 'date modified', 'latitude', 'longitude', 'date taken', 'bucket display name', 'tags', 'color', 'action', 'URL', 'vendor', 'is edited', 'mime_type', 'hash value', 'Tag name', 'Tag data', 'OCR tag','OCR tag date added', 'version', 'usertag id', 'usertag data', 'usertag timestamp')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21]))
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Samsung CMH tags'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung CMH TAGS'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No Samsung_CMH_Tags available')    
    db.close()