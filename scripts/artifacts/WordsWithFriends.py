# pylint: disable=W0613
__artifacts_v2__ = {
    "get_WordsWithFriends": {
        "name": "WordsWithFriends",
        "description": "Parses in-game chat messages (creation time, message, sender name and email) from the Words With Friends wf_database.sqlite.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/com.zynga.words/db/wf_database.sqlite',),
        "output_types": "standard",
        "artifact_icon": "message",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_WordsWithFriends(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT messages.created_at, messages.conv_id, users.name, users.email_address, messages.text
        FROM messages
        INNER JOIN users ON messages.user_zynga_id = users.zynga_account_id
        ORDER BY messages.created_at DESC
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        creation = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
        data_list.append((creation, row[1], row[2], row[3], row[4]))

    data_headers = (('Chat Message Creation', 'datetime'), 'Message ID', 'User Name', 'User Email', 'Chat Message')
    return data_headers, data_list, source_path
