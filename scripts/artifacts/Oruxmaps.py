__artifacts_v2__ = {
    "get_Oruxmaps": {
        "name": "Oruxmaps - POI",
        "description": "Parses the pois table (time, latitude, longitude, altitude and name) of "
                       "the OruxMaps oruxmapstracks.db database.",
        "author": "@markmckinnon, @AlexisBrignoni, Codex",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "poitime is read as milliseconds since the Unix epoch and shown in UTC. "
                 "That unit comes from two public readers of this database, not from the "
                 "app's own code, for which no public source was found, and it was not "
                 "measured: the database is in none of the registered Android corpus "
                 "listings searched. "
                 "Reference: Autopsy, 'oruxmaps.py', "
                 "https://github.com/sleuthkit/autopsy/blob/cb3dacdcad67abe7cf863c74f10dcdb8e25a5c21/InternalPythonModules/android/oruxmaps.py#L84 "
                 "Reference: optiprime, 'omexport.py', "
                 "https://github.com/optiprime/omexport/blob/0af5535be46f5d0f3bcb988fea202d8920bd8b72/omexport.py#L217 "
                 "The paths also match the database's sidecar files. Only the first matched "
                 "file named oruxmapstracks.db is read. No sample data is recorded "
                 "for this artifact.",
        "paths": ('**/oruxmaps/tracklogs/oruxmapstracks.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "get_Oruxmaps_tracks": {
        "name": "Oruxmaps - Tracks",
        "description": "Parses the tracks, segments and trackpoints tables of the OruxMaps "
                       "oruxmapstracks.db database, one row per trackpoint (time, track name, the "
                       "trackciudad value, segment name, latitude, longitude and altitude), and "
                       "one row for each track or segment that has no trackpoint.",
        "author": "@markmckinnon, @AlexisBrignoni, Codex",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "The trackciudad column holds the "
                 "tracks.trackciudad value as stored; what the app stores "
                 "there is not established. trkpttime is read as milliseconds since the "
                 "Unix epoch and shown in UTC. That unit comes from two public readers of "
                 "this database, not from the app's own code, for which no public source was found, "
                 "and it was not measured: the database is in none of the registered "
                 "Android corpus listings searched. "
                 "Reference: Autopsy, 'oruxmaps.py', "
                 "https://github.com/sleuthkit/autopsy/blob/cb3dacdcad67abe7cf863c74f10dcdb8e25a5c21/InternalPythonModules/android/oruxmaps.py#L147 "
                 "Reference: optiprime, 'omexport.py', "
                 "https://github.com/optiprime/omexport/blob/0af5535be46f5d0f3bcb988fea202d8920bd8b72/omexport.py#L217 "
                 "A track with no segment, and a segment with no trackpoint, each produce "
                 "one row with the missing columns blank. That behaviour was checked on a "
                 "constructed database only. The paths also match the database's sidecar "
                 "files. Only the first matched file named oruxmapstracks.db is read. No "
                 "sample data is recorded for this artifact.",
        "paths": ('**/oruxmaps/tracklogs/oruxmapstracks.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _main_db(files_found):
    # The paths end in .db* and so also match the -wal, -shm and -journal sidecars.
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'oruxmapstracks.db' and os.path.isfile(file_found):
            return file_found
    return ''


@artifact_processor
def get_Oruxmaps(context):
    data_headers = (('poitime', 'datetime'), 'poilat', 'poilon', 'poialt', 'poiname')
    data_list = []
    source_path = _main_db(context.get_files_found())
    if not source_path:
        return data_headers, data_list, source_path
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('SELECT poilat, poilon, poialt, poitime, poiname FROM pois')
    all_rows = cursor.fetchall()
    db.close()

    for row in all_rows:
        data_list.append((_ms_to_utc(row[3]), row[0], row[1], row[2], row[4]))

    return data_headers, data_list, source_path


@artifact_processor
def get_Oruxmaps_tracks(context):
    data_headers = (('trkpttime', 'datetime'), 'track id', 'track name', 'trackciudad', 'segment name', 'latitude', 'longitude', 'altimeter')
    data_list = []
    source_path = _main_db(context.get_files_found())
    if not source_path:
        return data_headers, data_list, source_path
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT tracks._id, trackname, trackciudad, segname, trkptlat, trkptlon, trkptalt, trkpttime
        FROM tracks
        LEFT JOIN segments ON segments.segtrack = tracks._id
        LEFT JOIN trackpoints ON trackpoints.trkptseg = segments._id
    ''')
    all_rows = cursor.fetchall()
    db.close()

    for row in all_rows:
        data_list.append((_ms_to_utc(row[7]), row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

    return data_headers, data_list, source_path
