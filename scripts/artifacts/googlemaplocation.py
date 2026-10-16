# pylint: disable=W0718
__artifacts_v2__ = {
    "get_googlemaplocation": {
        "name": "Googlemaplocation",
        "description": "Parses the destination_history table of Google Maps' da_destination_history database: time (read as Unix milliseconds), destination title and address, and destination and source coordinates. The four coordinate columns are reported as stored, under their column names, with no decimal point inserted; the scale of the stored values is not sourced. No tested image is recorded for this artifact.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-17",
        "last_update_date": "2026-10-09",
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


@artifact_processor
def get_googlemaplocation(context):
    files_found = context.get_files_found()

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
            data_list.append((timestamp, row[1], row[2], row[3], row[4], row[5], row[6]))

    data_headers = (('timestamp', 'datetime'), 'dest_lat (as stored)', 'dest_lng (as stored)', 'destination_title', 'destination_address', 'source_lat (as stored)', 'source_lng (as stored)')
    return data_headers, data_list, source_path
