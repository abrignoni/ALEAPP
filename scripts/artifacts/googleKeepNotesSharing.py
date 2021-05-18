import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleKeepNotesSharing(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
            CASE
                shared_timestamp
                WHEN
                    "0"
                THEN
                    ""
                ELSE
                    coalesce(datetime(tree_entity.shared_timestamp /1000, "unixepoch"), "Unknown")
            END AS shared_timestamp,
            list_item.list_parent_id,
            account.name as creator_Email, 
            sharing.email AS Shared_email, 
            title,
            text,
            sync_status, 
            sharing.is_deleted
            FROM 
            account 
            INNER JOIN
            list_item 
            ON 
            list_item.account_id == account._id 
            INNER JOIN 
            tree_entity 
            ON 
            tree_entity._id == list_item._id 
            INNER JOIN 
            sharing 
            ON list_item._id == sharing.tree_entity_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if(usageentries > 0):
            report = ArtifactHtmlReport('Google Keep - Notes Sharing')
            report.start_artifact_report(report_folder,"Google Keep - Notes Sharing")
            report.add_script()
            data_headers = ('Notes Shared Timestamp', 'List Parent ID', 'Creator Email', 'Shared Email', 'Title', 'Text', 'Sync Status','Is deleted')
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], 'Synced' if row[6]==1 else 'Not Synced', 'True' if row[7] == 1 else 'False'))

            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()

            tsvname = "Google Keep - Notes Sharing"
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = "Google Keep - Notes Sharing"
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc("No Google Keep - Notes Sharing data found")
        db.close()
        return
