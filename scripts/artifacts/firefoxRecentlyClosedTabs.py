# pylint: disable=W0613
__artifacts_v2__ = {
    "get_firefoxRecentlyClosedTabs": {
        "name": "Firefox - Recently Closed Tabs",
        "description": "",
        "author": "",
        "creation_date": "2022-01-12",
        "last_update_date": "2022-01-12",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/databases/recently_closed_tabs*',),
        "output_types": "standard",
        "artifact_icon": "globe",
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_firefoxRecentlyClosedTabs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'recently_closed_tabs':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        title as Title,
        url as URL
        FROM recently_closed_tabs
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2]))

        db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Title',
        'URL',
    )
    return data_headers, data_list, source_path
