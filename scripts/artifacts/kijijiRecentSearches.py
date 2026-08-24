__artifacts_v2__ = {
    "get_kijijiRecentSearches": {
        "name": "kijijiRecentSearches",
        "description": "Kijiji Local Recent Searches",
        "author": "Terry Chabot (Krypterry)",
        "creation_date": "2022-05-13",
        "last_update_date": "2022-05-13",
        "requirements": "None",
        "category": "Kijiji",
        "notes": "",
        "paths": ('*/com.ebay.kijiji.ca/databases/searches.*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "search",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_table_exist_in_db

recent_searches_query = '''
    SELECT
        [time],
        keyword,
        thumbnail,
        address,
        latitude,
        longitude,
        distance,
        ad_type,
        price_type,
        CASE min_price WHEN -1 THEN '' ELSE min_price END min_price,
        CASE max_price WHEN -1 THEN '' ELSE max_price END max_price
    FROM recent_searches
    ORDER BY TIME ASC;
'''


@artifact_processor
def get_kijijiRecentSearches(context):
    files_found = context.get_files_found()
    source_path = str(files_found[0])
    logfunc(f'Database file {source_path} is being interrogated...')

    data_list = []
    if does_table_exist_in_db(source_path, 'recent_searches'):
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute(recent_searches_query)
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            date_searched = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((date_searched, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
    else:
        logfunc('The recent_searches table was not found in the database!')

    data_headers = (('Date', 'datetime'), 'Search Keyword', 'Thumbnail', 'Address', 'Latitude', 'Longitude', 'Search Distance', 'Ad Type', 'Price Type', 'Min Price', 'Max Price')
    return data_headers, data_list, source_path
