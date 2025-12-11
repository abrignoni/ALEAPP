import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, media_to_html, open_sqlite_db_readonly

def get_googleKeepNotes(files_found, report_folder, seeker, wrap_text):
    logfunc("Starting Google Keep Notes script...")

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'keep.db':  
            continue

        logfunc(f"Processing database file: {file_found}")
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT 
                datetime(tree_entity.time_created/1000, 'unixepoch') AS "Time Created",
                datetime(tree_entity.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                datetime(tree_entity.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                tree_entity.title AS "Title",
                text_search_note_content_content.c0text AS "Text",
                tree_entity.last_modifier_email AS "Last Modifier Email",
                account.name AS "Account Name",
                GROUP_CONCAT(blob.file_name, ', ') AS "Attachment Names",
                CASE 
                    tree_entity.is_trashed
                    WHEN 0 THEN 'False' 
                    WHEN 1 THEN 'True'   
                    ELSE 'Unknown'      
                END AS "Deleted"
            FROM 
                tree_entity
            LEFT JOIN 
                text_search_note_content_content ON text_search_note_content_content.docid = tree_entity._id
            LEFT JOIN 
                blob_node ON tree_entity._id = blob_node.tree_entity_id
            LEFT JOIN 
                blob ON blob.blob_id = COALESCE(blob_node.original_id, blob_node.edited_id)
            LEFT JOIN 
                account ON tree_entity.account_id = account._id
            GROUP BY 
                tree_entity._id
            ORDER BY 
                tree_entity.time_created;
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Keep - Notes')
            report.start_artifact_report(report_folder, "Google Keep - Notes")
            report.add_script()
            data_headers = ('Time Created', 'Time Last Updated', 'User Edited Timestamp', 'Title', 'Text', 
                            'Last Modifier Email', 'Account Name', 'Attachment Names', 'Attachment', 'Deleted')
            data_list = []

            for row in all_rows:
                attachment_names = row[7]
                attachment_html = "No Attachments"

                if attachment_names:
                    attachments = attachment_names.split(', ')
                    attachment_html = ", ".join([
                        media_to_html(attachment.strip(), files_found, report_folder) for attachment in attachments
                    ])

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], attachment_html, row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()

            logfunc("Report generated successfully.")
        else:
            logfunc("No Google Keep - Notes data found")
 
        db.close()

__artifacts__ = {
    "GoogleKeepNotes": (
        "Google Keep",
        (
            '*/com.google.android.keep/databases/keep.db*',  
            '*/com.google.android.keep/files/*/image/original/*'  
        ),
        get_googleKeepNotes)
}