# Google Messages
# Author:  Josh Hickman (josh@thebinaryhick.blog)
# Date 2021-01-30
# Version: 0.1
# Requirements:  None

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_googleMessages(files_found, report_folder, _seeker, _wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('bugle_db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        try:
            cursor.execute("PRAGMA table_info(parts)")
            columns = [column[1] for column in cursor.fetchall()]
        except sqlite3.OperationalError:
            columns = []

        if 'file_size_bytes' in columns:
            file_size_query = '''
            CASE
                WHEN parts.file_size_bytes=-1 THEN "N/A"
                ELSE parts.file_size_bytes
            END'''
        else:
            file_size_query = "'N/A'"

        if 'local_cache_path' in columns:
            local_cache_query = 'parts.local_cache_path'
        else:
            local_cache_query = "'N/A'"

        query = f'''
        SELECT
        datetime(parts.timestamp/1000,'unixepoch') AS "Timestamp (UTC)",
        parts.content_type AS "Message Type",
        conversations.name AS "Other Participant/Conversation Name",
        participants.display_destination AS "Message Sender",
        parts.text AS "Message",
        {file_size_query} AS "Attachment Byte Size",
        {local_cache_query} AS "Attachment Location"
        FROM
        parts
        JOIN messages ON messages._id=parts.message_id
        JOIN participants ON participants._id=messages.sender_id
        JOIN conversations ON conversations._id=parts.conversation_id
        ORDER BY "Timestamp (UTC)" ASC
        '''

        try:
            cursor.execute(query)
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except sqlite3.Error as e:
            logfunc(f'Error executing query in Google Messages: {e}')
            usageentries = 0

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
            
            tsvname = 'Google Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Google Messages'
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