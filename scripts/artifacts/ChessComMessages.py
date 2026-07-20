__artifacts_v2__ = {
    "get_ChessComMessages": {
        "name": "ChessComMessages",
        "description": "Chess database",
        "author": "",
        "creation_date": "2022-02-23",
        "last_update_date": "2022-02-23",
        "requirements": "none",
        "category": "Chess.com",
        "notes": "",
        "paths": ('*/com.chess/databases/chess-database*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "message",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_ChessComMessages(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT messages.created_at, messages.conversation_id, messages.sender_username, messages.content
        FROM messages
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        sent = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
        data_list.append((sent, row[1], row[2], row[3]))

    data_headers = (('Sent', 'datetime'), 'Conversation', 'Sender', 'Message')
    return data_headers, data_list, source_path
