__artifacts_v2__ = {
    "get_firefoxTopSites": {
        "name": "Firefox - Top Sites",
        "description": "Parses Firefox top sites (created timestamp, title, URL and default flag) from the top_sites database.",
        "author": "",
        "creation_date": "2022-01-12",
        "last_update_date": "2022-01-12",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/databases/top_sites*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 3 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_firefoxTopSites(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'top_sites':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        title AS Title,
        url AS URL,
        CASE is_default
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END as IsDefault
        FROM top_sites
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3]))

        db.close()

    data_headers = (
        ('Created Timestamp', 'datetime'),
        'Title',
        'URL',
        'Is Default',
    )
    return data_headers, data_list, source_path
