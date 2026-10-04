__artifacts_v2__ = {
    "get_WordsWithFriends": {
        "name": "WordsWithFriends",
        "description": "Parses in-game chat messages (creation time, conversation id as stored in messages.conv_id, message, and the name and email of a matching users row, and the stored user_zynga_id; messages without a matching users row are retained) from the Words With Friends wf_database.sqlite.",
        "author": "@mastenp, @AlexisBrignoni, Codex",
        "creation_date": "2020-03-21",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Chats",
        "notes": "User Name and User Email are reported from a users row matched on messages.user_zynga_id = users.zynga_account_id. These fields remain empty when no users row matches. User Zynga ID reports messages.user_zynga_id as stored; no name or email is inferred from it. Validation used constructed tables because none of the 44 registered Android archives checked contains the target database.",
        "paths": ('*/com.zynga.words/db/wf_database.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_WordsWithFriends(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT messages.created_at, messages.conv_id, users.name, users.email_address, messages.text, messages.user_zynga_id
        FROM messages
        LEFT JOIN users ON messages.user_zynga_id = users.zynga_account_id
        ORDER BY messages.created_at DESC
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        creation = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
        data_list.append((creation, row[1], row[2], row[3], row[4], row[5]))

    data_headers = (('Chat Message Creation', 'datetime'), 'Conversation ID', 'User Name', 'User Email', 'Chat Message', 'User Zynga ID')
    return data_headers, data_list, source_path
