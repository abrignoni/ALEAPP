__artifacts_v2__ = {
    "get_badoo_conn": {
        "name": "BadooConnections",
        "description": "Get Information related to possible connections (messages, views etc) of the user with other users from the Badoo app (com.badoo.mobile)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-05-03",
        "last_update_date": "2023-05-03",
        "requirements": "Python 3.7 or higher",
        "category": "Badoo",
        "notes": "",
        "paths": ('*com.badoo.mobile/databases/CombinedConnectionsDatabase*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "html_columns": ['Avatar URL'],
    }
}

import datetime

from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_badoo_conn(context):
    files_found = context.get_files_found()

    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')
                   and not str(x).endswith('journal')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        Select id, name, gender, origin, sort_timestamp, avatar_url, display_message
        from connection
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} entries in connection")

    data_list = []
    for row in all_rows:
        sort_timestamp = datetime.datetime.fromtimestamp(int(row[4]) / 1000, datetime.timezone.utc) if row[4] else ''
        # The avatar URL is remote, so an <img> here would make opening the report
        # fetch it and disclose the examination to the service. Report the URL as
        # escaped text instead; the evidence is preserved, nothing is fetched.
        avatar_url = esc(row[5]) if row[5] else ''
        data_list.append((row[0], row[1], row[2], row[3], sort_timestamp, avatar_url, row[6]))

    data_headers = ('ID', 'Name', 'Gender', 'Origin', ('Sort Timestamp', 'datetime'), 'Avatar URL', 'Display Message')
    return data_headers, data_list, source_path
