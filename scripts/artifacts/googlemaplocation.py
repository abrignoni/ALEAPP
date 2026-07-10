# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_googlemaplocation": {
        "name": "Googlemaplocation",
        "description": "Parses Google Maps navigation destinations (timestamp, destination and source coordinates, title and address) from the da_destination_history database.",
        "author": "",
        "creation_date": "2021-03-17",
        "last_update_date": "2021-03-17",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('*/com.google.android.apps.maps/databases/da_destination_history*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def convertGeo(s):
    length = len(s)
    if length > 6:
        return s[0: length - 6] + "." + s[length - 6: length]
    return s


@artifact_processor
def get_googlemaplocation(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'journal' in file_found:
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT time/1000, dest_lat, dest_lng, dest_title, dest_address,
                       source_lat, source_lng FROM destination_history;
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, convertGeo(str(row[1])), convertGeo(str(row[2])), row[3], row[4], convertGeo(str(row[5])), convertGeo(str(row[6]))))

    data_headers = (('timestamp', 'datetime'), 'destination_latitude', 'destination_longitude', 'destination_title', 'destination_address', 'source_latitude', 'source_longitude')
    return data_headers, data_list, source_path
