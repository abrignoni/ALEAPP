__artifacts_v2__ = {
    "get_ChessWithFriends": {
        "name": "Chess With Friends",
        "description": "Parses Chess With Friends game data",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/com.zynga.chess.googleplay/databases/wf_database.sqlite', '*/data/com.zynga.chess.googleplay/db/wf_database.sqlite'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "layout-grid",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_ChessWithFriends(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        chat_messages.chat_message_id,
        users.name,
        users.email_address,
        chat_messages.message,
        chat_messages.created_at
        FROM chat_messages
        INNER JOIN users ON chat_messages.user_id = users.user_id
        ORDER BY chat_messages.created_at DESC
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4]))

    data_headers = ('Message ID', 'User Name', 'User Email', 'Chat Message', 'Chat Message Creation')
    return data_headers, data_list, source_path
