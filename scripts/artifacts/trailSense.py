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
                 "BeaconOwner enum, 0 User, 1 Path, 2 CellSignal, 3 Maps, 4 Triangulate, 5 "
                 "FieldGuide (BeaconOwner.kt at kylecorry31/Trail-Sense "
                 "696d2f54fbcfeeab94efbf62e778716a9317e524); any other value is reported as "
                 "stored. The enum names are the app's own, shown here with CellSignal as 'Cell "
                 "signal' and FieldGuide as 'Field guide'; which actions write each value was not "
                 "established here. On the tested device (emu_a15_oss_v4) one beacon had owner "
                 "User and one had owner CellSignal. Temporary is the temporary flag, reported "
                 "as stored. Comment is the note field on the beacon and "
                 "was empty on the tested beacons. The beacon_group_id and styling columns (color, "
                 "icon) are not reported. KML output is produced from the coordinates. This table holds "
                 "coordinates the app stored, not positions the device was independently measured at.",
        "paths": ('*/com.kylecorry.trail_sense/databases/trail_sense*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "trailsense_paths": {
        "name": "Trail Sense - Paths",
        "description": "Parses the paths (tracks) held in the Trail Sense Android app's paths "
                       "table.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Trail Sense",
        "sample_data": {
            "emu_a15_oss_v4": "Trail Sense 8.1.1 | 1 rows",
        },
        "notes": "One row per entry in the paths table of databases/trail_sense. A path is a track the "
                 "app holds. The app can record a path and can also import one from a GPX file "
                 "(app/src/main/java/com/kylecorry/trail_sense/tools/paths/ui/commands/"
                 "ImportPathsCommand.kt "
                 "at kylecorry31/Trail-Sense 696d2f54fbcfeeab94efbf62e778716a9317e524), and this "
                 "table does not by itself say which. Each row summarises the track: the Name "
                 "where one is stored (Name was empty on the tested device; the name column is "
                 "nullable in the app's PathEntity.kt at the same commit), the Start and End "
                 "times, the Distance in metres, the number of Waypoints, and the bounding box of "
                 "the track as North, East, South and West coordinates. Start and End are Unix "
                 "milliseconds and were UTC on the tested device (01:52 UTC matched the device's "
                 "21:52 local clock). Temporary is the temporary flag, reported as stored. The "
                 "individual points of each track are in the Waypoints artifact, keyed by Path "
                 "ID. The styling columns are not reported. A path row holds the start and end "
                 "times stored for the track; it does not establish that the app recorded "
                 "positions on this device during that span.",
        "paths": ('*/com.kylecorry.trail_sense/databases/trail_sense*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
    },
    "trailsense_waypoints": {
        "name": "Trail Sense - Waypoints",
        "description": "Parses the path waypoints held in the Trail Sense Android app's waypoints "
                       "table.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Trail Sense",
        "sample_data": {
            "emu_a15_oss_v4": "Trail Sense 8.1.1 | 1 rows",
        },
        "notes": "One row per entry in the waypoints table of databases/trail_sense, which holds "
                 "the individual points of the paths in the Paths artifact. Each row is a point "
                 "stored for a path, with a Latitude, Longitude and Altitude in metres, the time "
                 "stored for it, the Path ID it belongs to, and the cell network and quality "
                 "values stored with it. Recorded is Unix milliseconds and is reported as UTC. "
                 "Cell Network is decoded from the app's CellNetwork enum by id, 1 NR (5G), 2 LTE "
                 "(4G), 3 CDMA, 4 WCDMA, 5 GSM (2G), 6 TD-SCDMA "
                 "(signal/src/main/java/com/kylecorry/andromeda/signal/CellNetwork.kt at "
                 "kylecorry31/andromeda a13ec8fea2f13f4ce66dc7c7e9c27f3096ae270f); Cell Quality "
                 "is decoded from the Quality enum by position, 0 poor, 1 moderate, 2 good, 3 "
                 "unknown (core/src/main/java/com/kylecorry/andromeda/core/sensors/Quality.kt at "
                 "the same commit; the andromeda version Trail Sense 8.1.1 builds against was not "
                 "checked); on the tested waypoint these read LTE and Good, which matched the "
                 "name of the CellSignal beacon stored at the same point. Any other value for "
                 "either is reported as stored, and both are empty where no cell value is stored. "
                 "Recorded is blank where no time is stored. The app can record a path on the "
                 "device and can import one from a GPX file "
                 "(app/src/main/java/com/kylecorry/trail_sense/tools/paths/ui/commands/"
                 "ImportPathsCommand.kt "
                 "at kylecorry31/Trail-Sense 696d2f54fbcfeeab94efbf62e778716a9317e524); both "
                 "store their points here, and this table does not say which. KML output is "
                 "produced from the coordinates.",
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
