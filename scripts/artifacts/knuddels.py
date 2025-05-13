__artifacts_v2__ = {
    "get_knuddels_chats": {
        "name": "Knuddels - Chats",
        "description": "Extracts Knuddels Chats from database files",
        "author": "@As-arsenicum-33",
        "version": "0.0.1",
        "date": "2025-05-04",
        "requirements": "none",
        "category": "Knuddels",
        "notes": "",
        "paths": ("*/com.knuddels.android/databases/knuddels*"),
        "function": "get_knuddels_chats"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_knuddels_chats(files_found, report_folder, seeker, wrap_text):
    
    data_list = []

    for file_found in files_found:
        logfunc("knuddels - chats found")
        file_found = str(file_found)

        if file_found.lower().endswith(("-shm","-wal","-journal")):
            pass
        else:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            nickname, message, 
            datetime(thread.timestamp / 1000, "unixepoch"), cid,
            thread.sender, users.id
            FROM thread, users
            WHERE users.id = thread.sender
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:
                for row in all_rows:
                    db_name = str(file_found).split("databases")[1].split("knuddels")[1]
                    # Store conversation keys as strings to ensure unique filtering, as the same ID might exist in a different database
                    data_list.append((row[0], row[1], row[2], "chat_" + str(row[3]) + "_" + db_name, file_found, row[4], row[5])) 

            if len(data_list) > 0:
                report = ArtifactHtmlReport("Knuddels Messages")
                report.start_artifact_report(report_folder, f"Knuddels Messages")
                report.add_script()
                data_headers = ("User Name", "Message", "Timestamp", "Conversation Key", "Source", "Thread Table UID", "Users Table UID")
                report.write_artifact_data_table(data_headers, data_list, "See report")
                report.end_artifact_report()
                
                tsvname = f"Knuddels"
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = f"Knuddels"
                timeline(report_folder, tlactivity, data_list, data_headers)

