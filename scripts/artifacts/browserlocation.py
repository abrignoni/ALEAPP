# pylint: disable=W0718
__artifacts_v2__ = {
    "get_browserlocation": {
        "name": "Browser Location",
        "description": "Parses cached geolocation positions (timestamp, latitude, longitude and accuracy) from the Android Browser CachedGeoposition.db.",
        "author": "",
        "creation_date": "2021-03-17",
        "last_update_date": "2021-03-17",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('*/com.android.browser/app_geolocation/CachedGeoposition.db',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_browserlocation(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('-db'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('SELECT timestamp/1000, latitude, longitude, accuracy FROM CachedPosition;')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3]))

    data_headers = (('timestamp', 'datetime'), 'latitude', 'longitude', 'accuracy')
    return data_headers, data_list, source_path
