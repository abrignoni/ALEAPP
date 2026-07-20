__artifacts_v2__ = {
    "get_Twitter": {
        "name": "twitter",
        "description": "Twitter Searches",
        "author": "Kevin Pagano (https://startme.stark4n6.com)",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "None",
        "category": "Twitter",
        "notes": "",
        "paths": ('*/com.twitter.android/databases/*-search.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.twitter.android vc 310480000 | 2 rows",
            "samsungs20_a13": "Android 13 | com.twitter.android vc 311550000 | 2 rows",
            "sharon_a14": "Android 14 | com.twitter.android vc 310542000 | 0 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_Twitter(context):
    files_found = context.get_files_found()
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('-search.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            select time, name, query, query_id, user_search_suggestion, topic_search_suggestion,
            latitude, longitude, radius, location, priority, score
            from search_queries
        ''')
        all_rows = cursor.fetchall()
        db.close()
        for r in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(r[0]) / 1000, datetime.timezone.utc) if r[0] else ''
            data_list.append((timestamp, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11]))

    data_headers = (('Timestamp', 'datetime'), 'Name', 'Query', 'Query ID', 'User Search Suggestion', 'Topic Search Suggestion', 'Latitude', 'Longitude', 'Radius', 'Location', 'Priority', 'Score')
    return data_headers, data_list, source_path
