# pylint: disable=W0613
__artifacts_v2__ = {
    "get_firefoxCookies": {
        "name": "Firefox - Cookies",
        "description": "",
        "author": "",
        "creation_date": "2022-01-12",
        "last_update_date": "2022-01-12",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/files/mozilla/*.default/cookies.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_firefoxCookies(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'cookies.sqlite':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(lastAccessed/1000000,'unixepoch') AS LastAccessedDate,
        datetime(creationTime/1000000,'unixepoch') AS CreationDate,
        host AS Host,
        name AS Name,
        value AS Value,
        datetime(expiry,'unixepoch') AS ExpirationDate,
        path AS Path
        from moz_cookies
        ORDER BY lastAccessedDate ASC
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        db.close()

    data_headers = (
        ('Last Accessed Timestamp', 'datetime'),
        ('Created Timestamp', 'datetime'),
        'Host',
        'Name',
        'Value',
        ('Expiration Timestamp', 'datetime'),
        'Path',
    )
    return data_headers, data_list, source_path
