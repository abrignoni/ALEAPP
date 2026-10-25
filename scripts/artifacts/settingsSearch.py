__artifacts_v2__ = {
    "get_settingsSearch": {
        "name": "Android Settings Search",
        "description": "Search history from the Android Settings search_index.db",
        "author": "segumarc",
        "creation_date": "2026-08-08",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Android Settings",
        "notes": "Every search_index.db found is read once per Android user, and Android User names the "
                 "user whose app folder holds it. Taking the first match instead returned no rows on a "
                 "One UI 8 (Android 16) extraction whose Secure Folder user's copy sorted first and held "
                 "no saved queries while the owner's copy held five."
                 " On the four tested Android 16 extractions the owner's copy held five saved queries and a Secure Folder user's copy, present on three, held none; Android User held one value (0) on every row of each. On the corpus images in sample_data that hold a second Android user's database, the row count equals the sum of the rows in each user's table, counted without ALEAPP.",
        "paths": (
            "*/com.android.settings.intelligence/databases/search_index.db*",
            "*/com.google.android.settings.intelligence/databases/search_index.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "cookbook_a11": "Android 11 | com.android.settings.intelligence | 3 rows",
            "samsungs20_a13": "Android 13 | com.android.settings.intelligence | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.settings.intelligence | 4 rows",
            "russell_a14": "Android 14 | com.google.android.settings.intelligence | 0 rows",
        },
    }
}

from scripts.artifacts.storagePathViews import user_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

@artifact_processor
def get_settingsSearch(context):
    query = """
        SELECT
            datetime(timestamp / 1000, 'unixepoch') AS timestamp,
            query
        FROM saved_queries
        ORDER BY timestamp ASC
    """

    data_list = []
    sources = []
    for source_path, user in user_files(context, "search_index.db"):
        sources.append(source_path)
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0], record[1], user))

    data_headers = (
        ("Timestamp", "datetime"),
        "Query",
        "Android User",
    )

    return data_headers, data_list, '\n'.join(sources)
