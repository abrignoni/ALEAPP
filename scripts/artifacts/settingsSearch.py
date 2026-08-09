__artifacts_v2__ = {
    "get_settingsSearch": {
        "name": "Android Settings Search",
        "description": "Search history from the Android Settings search_index.db",
        "author": "segumarc",
        "creation_date": "2026-08-08",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Android Settings",
        "notes": "",
        "paths": (
            "*/com.android.settings.intelligence/databases/search_index.db*",
            "*/com.google.android.settings.intelligence/databases/search_index.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "search",
    }
}

import datetime
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def get_settingsSearch(context):
    files_found = context.get_files_found()

    source_path = get_file_path(files_found, "search_index.db")

    query = """
        SELECT
            datetime(timestamp / 1000, 'unixepoch') AS timestamp,
            query
        FROM saved_queries
        ORDER BY timestamp ASC
    """

    db_records = get_sqlite_db_records(source_path, query)

    data_list = []

    for record in db_records:
        data_list.append((
            record[0],
            record[1],
        ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Query",
    )

    return data_headers, data_list, source_path