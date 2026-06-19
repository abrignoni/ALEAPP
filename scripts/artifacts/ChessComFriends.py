# pylint: disable=W0613
__artifacts_v2__ = {
    "get_ChessComFriends": {
        "name": "ChessComFriends",
        "description": "Chess database",
        "author": "",
        "creation_date": "2022-02-23",
        "last_update_date": "2022-02-23",
        "requirements": "none",
        "category": "Chess.com",
        "notes": "",
        "paths": ('*/com.chess/databases/chess-database*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "grid",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_ChessComFriends(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT friends.id, friends.username, friends.first_name, friends.last_name, friends.last_login_date
        FROM friends
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        last_login = ''
        if row[4]:
            last_login = datetime.datetime.fromtimestamp(int(row[4]), datetime.timezone.utc)
        data_list.append((row[0], row[1], row[2], row[3], last_login))

    data_headers = ('ID', 'Username', 'First Name', 'Last Name', ('Last Login', 'datetime'))
    return data_headers, data_list, source_path
