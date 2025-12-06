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

            # --- Cek Keberadaan Tabel ---
            # Kita cek apakah tabel FTS (text_search...) ada. Jika tidak, kita gunakan tabel list_item.
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='text_search_note_content_content'")
            fts_table = cursor.fetchone()

            # --- Konstruksi Query ---
            if fts_table:
                # Query Asli (Jika tabel FTS ada)
                query = '''
                SELECT 
                    datetime(tree_entity.time_created/1000, 'unixepoch') AS "Time Created",
                    datetime(tree_entity.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                    datetime(tree_entity.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                    tree_entity.title AS Title,
                    text_search_note_content_content.c0text AS "Text",
                    tree_entity.last_modifier_email AS "Last Modifier Email"
                FROM text_search_note_content_content
                INNER JOIN tree_entity ON text_search_note_content_content.docid = tree_entity._id
                '''
            else:
                # Query Alternatif (Menggunakan tabel list_item)
                # Menggunakan GROUP_CONCAT untuk menggabungkan teks jika berupa checklist atau multiline
                query = '''
                SELECT 
                    datetime(tree_entity.time_created/1000, 'unixepoch') AS "Time Created",
                    datetime(tree_entity.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                    datetime(tree_entity.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                    tree_entity.title AS Title,
                    GROUP_CONCAT(list_item.text, char(10)) AS "Text", 
                    tree_entity.last_modifier_email AS "Last Modifier Email"
                FROM tree_entity
                LEFT JOIN list_item ON tree_entity._id = list_item.list_parent_id
                GROUP BY tree_entity._id
                '''

            try:
                cursor.execute(query)
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)

                if usageentries > 0:
                    data_list = []
                    for row in all_rows:
                        data_list.append(row)

                    report = ArtifactHtmlReport('Google Keep Notes')
                    report.start_artifact_report(report_folder, 'Google Keep Notes')
                    report.add_script()
                    data_headers = ('Time Created', 'Time Last Updated', 'User Edited Timestamp', 'Title', 'Text', 'Last Modifier Email')
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()

                    tsvname = 'Google Keep Notes'
                    tsv(report_folder, data_headers, data_list, tsvname)

                    tlactivity = 'Google Keep Notes'
                    timeline(report_folder, tlactivity, data_list, data_headers)

                else:
                    logfunc('No Google Keep Notes data available')
            
            except Exception as e:
                logfunc(f'Error reading Google Keep Notes: {e}')
            
            db.close()