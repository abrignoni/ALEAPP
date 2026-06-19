# pylint: disable=W0613
__artifacts_v2__ = {
    "get_waze": {
        "name": "waze",
        "description": "",
        "author": "",
        "creation_date": "2022-01-09",
        "last_update_date": "2022-01-09",
        "requirements": "none",
        "category": "Waze",
        "notes": "",
        "paths": ('*/com.waze/user.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ts_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_waze(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        select
        PLACES.created_time,
        RECENTS.access_time,
        RECENTS.name,
        PLACES.name as "Address",
        round(PLACES.latitude*.000001,6),
        round(PLACES.longitude*.000001,6)
        from PLACES
        join RECENTS on PLACES.id = RECENTS.place_id
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((_ts_to_utc(row[0]), _ts_to_utc(row[1]), row[2], row[3], row[4], row[5]))

    data_headers = (('Created Timestamp', 'datetime'), ('Accessed Timestamp', 'datetime'), 'Location Name', 'Address', 'Latitude', 'Longitude')
    return data_headers, data_list, source_path
