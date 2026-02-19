# Google Messages
# Author:  Josh Hickman (josh@thebinaryhick.blog)
# Date 2021-01-30
# Version: 0.1
# Requirements:  None

import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleMessages(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('bugle_db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(parts);")
        parts_cols = {col[1] for col in cursor.fetchall()}

        has_size = 'file_size_bytes' in parts_cols
        has_cache = 'local_cache_path' in parts_cols
        size_expr = 'parts.file_size_bytes' if has_size else "''"
        cache_expr = 'parts.local_cache_path' if has_cache else (
            'parts.storage_uri' if 'storage_uri' in parts_cols else (
                'parts.uri' if 'uri' in parts_cols else "''"
            )
        )

        query = f'''
        SELECT
        datetime(parts.timestamp/1000,'unixepoch') AS "Timestamp (UTC)",
        parts.content_type AS "Message Type",
        conversations.name AS "Other Participant/Conversation Name",
        participants.display_destination AS "Message Sender",
        parts.text AS "Message",
        CASE
        WHEN {size_expr}=-1 THEN "N/A"
        ELSE {size_expr}
        END AS "Attachment Byte Size",
        {cache_expr} AS "Attachment Location"
        FROM
        parts
        JOIN messages ON messages._id=parts.message_id
        JOIN participants ON participants._id=messages.sender_id
        JOIN conversations ON conversations._id=parts.conversation_id
        ORDER BY "Timestamp (UTC)" ASC
        '''

        try:
            cursor.execute(query)
        except sqlite3.OperationalError as e:
            logfunc(f'Google Messages query failed in {file_found}: {e}')
            db.close()
            continue

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Messages')
            report.start_artifact_report(report_folder, 'Google Messages')
            report.add_script()
            data_headers = ('Message Timestamp (UTC)','Message Type','Other Participant/Conversation Name','Message Sender','Message','Attachment Byte Size','Attachment Location') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Messages data available')
        
        db.close()

__artifacts__ = {
        "GoogleMessages": (
                "Google Messages",
                ('*/com.google.android.apps.messaging/databases/bugle_db*'),
                get_googleMessages)
}
