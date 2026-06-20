# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Oruxmaps": {
        "name": "Oruxmaps - POI",
        "description": "",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('**/oruxmaps/tracklogs/oruxmapstracks.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "get_Oruxmaps_tracks": {
        "name": "Oruxmaps - Tracks",
        "description": "",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('**/oruxmaps/tracklogs/oruxmapstracks.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_Oruxmaps(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('SELECT poilat, poilon, poialt, poitime, poiname FROM pois')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], _ms_to_utc(row[3]), row[4]))

    data_headers = ('poilat', 'poilon', 'poialt', ('poitime', 'datetime'), 'poiname')
    return data_headers, data_list, source_path


@artifact_processor
def get_Oruxmaps_tracks(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT tracks._id, trackname, trackciudad, segname, trkptlat, trkptlon, trkptalt, trkpttime
        FROM tracks, segments, trackpoints
        where tracks._id = segments.segtrack and segments._id = trackpoints.trkptseg
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], _ms_to_utc(row[7])))

    data_headers = ('track id', 'track name', 'track description', 'segment name', 'latitude', 'longitude', 'altimeter', ('datetime', 'datetime'))
    return data_headers, data_list, source_path
