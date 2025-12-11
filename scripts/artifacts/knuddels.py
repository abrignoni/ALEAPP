__artifacts_v2__ = {
    "knuddels_chats": {
        "name": "Knuddels - Chat Messages",
        "description": "Extracts Knuddels Chats from database files",
        "author": "@As-arsenicum-33",
        "version": "0.0.2",
        "creation_date": "2025-05-04",
        "last_updated": "2025-06-21",
        "requirements": "none",
        "category": "Knuddels",
        "notes": "",
        "paths": ("*/com.knuddels.android/databases/knuddels*"),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-circle",
    }
}

import re
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

@artifact_processor
def knuddels_chats(files_found, report_folder, seeker, wrap_text):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        #if file_found.lower().endswith(("-shm","-wal","-journal")):
        if re.search(r"(?:-shm|-wal|-journal)(?:_\d+)?$", file_found):
            pass
        else:
            query = '''
            SELECT
            datetime(thread.timestamp / 1000, "unixepoch"),
            nickname, 
            message,
            cid,
            thread.sender,
            users.id
            FROM thread, users
            WHERE users.id = thread.sender
            '''
            
            db_records = get_sqlite_db_records(file_found, query)

            for row in db_records:
                db_name = str(file_found).split("databases")[1].split("knuddels")[1]
                # Store conversation keys as strings to ensure unique filtering, as the same ID might exist in a different database
                data_list.append((row[0], row[1], row[2], "chat_" + str(row[3]) + "_" + db_name, file_found, row[4], row[5])) 

    data_headers = ("Timestamp", "User Name", "Message", "Conversation Key", "Source File", "Thread Table UID", "Users Table UID")
    return data_headers, data_list, "See source file(s) below:"            