__artifacts_v2__ = {
    "trailsense_beacons": {
        "name": "Trail Sense - Beacons",
        "description": "Parses saved beacons (locations) from the Trail Sense Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Trail Sense",
        "sample_data": {
            "emu_a15_oss_v4": "Trail Sense 8.1.1 | 2 rows",
        },
        "notes": "One row per entry in the beacons table of databases/trail_sense. Trail Sense is an "
                 "offline hiking and navigation app; a beacon is a location it holds, with a Latitude "
                 "and Longitude, an Elevation in metres (a 50 ft entry on the tested device was stored "
                 "as 15.24), an optional Comment, and an Owner. Owner is decoded from the app's "
                 "BeaconOwner enum, 0 the User value for a beacon added through the app's beacon form, 1 a beacon derived from a recorded "
                 "path, 2 a beacon the app dropped for the last cell signal, 3 from a map, 4 from "
                 "triangulation, 5 from the field guide (BeaconOwner.kt at kylecorry31/Trail-Sense "
                 "696d2f54fbcfeeab94efbf62e778716a9317e524); any other value is reported as stored. "
                 "That distinction matters: the User value marks a beacon added through the app, while the others "
                 "are app-generated, so the tested device held one User beacon and one CellSignal "
                 "beacon named for the last 4G signal. Temporary is the temporary flag, Yes for an "
                 "auto-created beacon the app may discard. Comment is the note field on the beacon and "
                 "was empty on the tested beacons. The beacon_group_id and styling columns (color, "
                 "icon) are not reported. KML output is produced from the coordinates. This table holds "
                 "coordinates the app stored, not positions the device was independently measured at.",
        "paths": ('*/com.kylecorry.trail_sense/databases/trail_sense*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "trailsense_paths": {
        "name": "Trail Sense - Paths",
        "description": "Parses recorded paths (tracks) from the Trail Sense Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Trail Sense",
        "sample_data": {
            "emu_a15_oss_v4": "Trail Sense 8.1.1 | 1 rows",
        },
        "notes": "One row per entry in the paths table of databases/trail_sense. A path is a track the "
                 "app recorded, most often through its Backtrack feature, which logs the device's "
                 "location on a timer. Each row summarises the track: the Name where a name was given to it "
                 "(a Backtrack path is unnamed, which is why Name was empty on the tested device), the "
                 "Start and End times, the Distance in metres, the number of Waypoints, and the "
                 "bounding box of the track as North, East, South and West coordinates. Start and End "
                 "are Unix milliseconds and were UTC on the tested device (01:52 UTC matched the "
                 "device's 21:52 local clock). Temporary is the temporary flag, Yes for a track the app "
                 "may discard. The individual points of each track are in the Waypoints artifact, keyed "
                 "by Path ID. The styling columns are not reported. A path is evidence the app recorded "
                 "the device moving through those points during that time span.",
        "paths": ('*/com.kylecorry.trail_sense/databases/trail_sense*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
    },
    "trailsense_waypoints": {
        "name": "Trail Sense - Waypoints",
        "description": "Parses recorded path waypoints (location history) from the Trail Sense Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Trail Sense",
        "sample_data": {
            "emu_a15_oss_v4": "Trail Sense 8.1.1 | 1 rows",
        },
        "notes": "One row per entry in the waypoints table of databases/trail_sense, which are the "
                 "individual points the app logged along a recorded path (see the Paths artifact). Each "
                 "row is a location the app recorded for the device, with a Latitude, Longitude and "
                 "Altitude in metres, the time it was recorded, the Path ID it belongs to, and the cell "
                 "signal the device saw at that point. Recorded is Unix milliseconds and is reported as "
                 "UTC. Cell Network is decoded from the app's CellNetwork enum by id, 1 NR (5G), 2 LTE "
                 "(4G), 3 CDMA, 4 WCDMA, 5 GSM (2G), 6 TD-SCDMA (CellNetwork.kt in kylecorry31/andromeda); "
                 "Cell Quality is decoded from the Quality enum by position, 0 poor, 1 moderate, 2 good, "
                 "3 unknown (Quality.kt in the same library); on the tested waypoint these read LTE and "
                 "Good, which matched the name of the last-signal beacon the app dropped at the same "
                 "point. Any other value for either is reported as stored, and both are empty where the "
                 "app recorded no cell signal. Unlike the Beacons table, a waypoint is a position the "
                 "app logged from the device's location at that time, so the rows are a location history "
                 "for the recording period. KML output is produced from the coordinates.",
        "paths": ('*/com.kylecorry.trail_sense/databases/trail_sense*',),
        "output_types": "all",
        "artifact_icon": "navigation",
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/trail_sense'

# BeaconOwner.kt at kylecorry31/Trail-Sense 696d2f54fbcfeeab94efbf62e778716a9317e524.
BEACON_OWNERS = {0: 'User', 1: 'Path', 2: 'Cell signal', 3: 'Maps',
                 4: 'Triangulate', 5: 'Field guide'}
# CellNetwork.kt (by id) and Quality.kt (by ordinal) in kylecorry31/andromeda.
CELL_NETWORKS = {1: 'NR (5G)', 2: 'LTE (4G)', 3: 'CDMA', 4: 'WCDMA',
                 5: 'GSM (2G)', 6: 'TD-SCDMA'}
CELL_QUALITY = {0: 'Poor', 1: 'Moderate', 2: 'Good', 3: 'Unknown'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _lookup(table, value):
    if value in table:
        return table[value]
    if value is None or value == '':
        return ''
    return f'{value} (as stored)'


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


@artifact_processor
def trailsense_beacons(context):
    query = '''SELECT name, latitude, longitude, elevation, owner, temporary, comment
               FROM beacons ORDER BY _id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((r[0] or '', r[1], r[2], r[3], _lookup(BEACON_OWNERS, r[4]),
                              _yesno(r[5]), r[6] or '', context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Name', 'Latitude', 'Longitude', 'Elevation (m)', 'Owner',
                    'Temporary', 'Comment', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def trailsense_paths(context):
    query = '''SELECT name, startTime, endTime, distance, numWaypoints,
                      north, east, south, west, temporary, _id
               FROM paths ORDER BY startTime DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[1]), _ms(r[2]), r[0] or '', r[3], r[4],
                              r[5], r[6], r[7], r[8], _yesno(r[9]), r[10],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Name',
                    'Distance (m)', 'Waypoints', 'North', 'East', 'South', 'West',
                    'Temporary', 'Path ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def trailsense_waypoints(context):
    query = '''SELECT createdOn, latitude, longitude, altitude, cellType, cellQuality, pathId, _id
               FROM waypoints ORDER BY createdOn DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1], r[2], r[3], _lookup(CELL_NETWORKS, r[4]),
                              _lookup(CELL_QUALITY, r[5]), r[6], r[7],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Recorded', 'datetime'), 'Latitude', 'Longitude', 'Altitude (m)',
                    'Cell Network', 'Cell Quality', 'Path ID', 'Waypoint ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
