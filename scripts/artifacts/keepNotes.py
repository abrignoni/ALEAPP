#keepNotes.py
__artifacts_v2__ = {
    "keepNotes": {
        "name": "Google Keep Notes",
        "description": "Parses Google Keep Notes",
        "author": "Heather Charpentier",
        "version": "0.0.1",
        "date": "2024-12-02",
        "requirements": "none",
        "category": "Google Keep Notes",
        "notes": "",
        "paths": ('*/data/data/com.google.android.keep/databases/keep.db*'),
        "function": "get_keepNotes"
    }
}

import sqlite3
import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_keepNotes(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)

        if filename.endswith('keep.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            all_rows = []

            primary_query = '''
                SELECT 
                    datetime(T1.time_created/1000, 'unixepoch') AS "Time Created",
                    datetime(T1.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                    datetime(T1.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                    T1.title AS Title,
                    T2.c0text AS "Text",
                    T1.last_modifier_email AS "Last Modifier Email"
                FROM tree_entity T1
                INNER JOIN text_search_note_content_content T2 ON T2.docid = T1._id
            '''
            data_headers = ('Time Created', 'Time Last Updated', 'User Edited Timestamp', 'Title', 'Text', 'Last Modifier Email')

            try:
                cursor.execute(primary_query)
                all_rows = cursor.fetchall()
                logfunc(f'Good main Query for {filename}.')

            except sqlite3.OperationalError as e:
                if 'no such table' in str(e):
                    logfunc(f'Bad Query failed for {filename} missing table: {e}, alternative->')
                    
                    fallback_query = '''
                        SELECT
                            datetime(T1.time_created/1000, 'unixepoch') AS "Time Created",
                            datetime(T1.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                            datetime(T1.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                            T1.title AS Title,
                            T2.note_content_text AS "Text (From Note Changes)",
                            T1.last_modifier_email AS "Last Modifier Email"
                        FROM tree_entity T1
                        LEFT JOIN note_changes T2 ON T1._id = T2.note_id
                        GROUP BY T1._id
                        ORDER BY T1.time_created ASC
                    '''
                    data_headers = ('Time Created', 'Time Last Updated', 'User Edited Timestamp', 'Title', 'Text (From Note Changes)', 'Last Modifier Email')
                    
                    try:
                        cursor.execute(fallback_query)
                        all_rows = cursor.fetchall()
                        logfunc(f'Good Fallback for {filename}.')
                    except Exception as fe:
                        logfunc(f'Bad Fallback, with error: {fe}')
                        continue 
                        
                else:
                    logfunc(f'Error unhandled SQLite Operational Error in {filename}: {e}')
                    raise 

            usageentries = len(all_rows)

            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    data_list.append(row)

                report = ArtifactHtmlReport('Google Keep Notes')
                report.start_artifact_report(report_folder, 'Google Keep Notes')
                report.add_script()
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()

                tsvname = 'Google Keep Notes'
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = 'Google Keep Notes'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc(f'No Google Keep Notes data available')