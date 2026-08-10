__artifacts_v2__ = {
    "get_blueskysearches": {
        "name": "Bluesky - Searches",
        "description": "User generated searches",
        "author": "DFIRcon 2025 Miami",
        "creation_date": "2024-11-15",
        "last_update_date": "2024-11-15",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/databases/RKStorage*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "search",
    }
}

import json

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_blueskysearches(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('RKStorage'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT key, value
            FROM catalystLocalStorage
            WHERE key like 'searchHistory'
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            searches = json.loads(row[1])
            for item in searches:
                data_list.append((item,))

    data_headers = ('Searches',)
    return data_headers, data_list, source_path
