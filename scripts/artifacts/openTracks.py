__artifacts_v2__ = {
    "opentracks_tracks": {
        "name": "OpenTracks - Tracks",
        "description": "Parses recorded tracks from the OpenTracks Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "OpenTracks",
        "sample_data": {
            "emu_a15_oss_v6": "OpenTracks 4.28.2 | 1 rows",
        },
        "notes": "One row per entry in the tracks table of databases/database.db. OpenTracks is "
                 "an open source sport tracking app that records the device's position while a "
                 "recording is running. Each row summarises one recording: its Name (the app "
                 "defaults to the local start time, as on the tested device), Description, "
                 "Activity Type, the Start and Stop times, Total Duration and Moving Duration in "
                 "seconds, Distance in metres, Max Speed in metres per second, and the altitude "
                 "minimum and maximum in metres. Start and Stop are Unix milliseconds "
                 "reported as UTC. The track also stores its own UTC offset in seconds "
                 "(ZoneOffset.ofTotalSeconds, ContentProviderUtils.java line 127 at "
                 "OpenTracksApp/OpenTracks tag v4.28.2, "
                 "ab8791a620a005da514e7659abd159eef10c5696), so Start (Local) and UTC Offset "
                 "report the wall clock the recording was made against rather than an assumed "
                 "zone; the tested track recorded -14400 seconds, which is UTC-4. Altitude Gain (m) "
                 "and Altitude Loss (m) hold the app's cumulative climb and descent and were "
                 "both empty on the tested track because the injected path held a constant "
                 "altitude; they are kept because a blank there is a real statement about the "
                 "recording. The individual positions are in the Trackpoints artifact, "
                 "keyed by Track ID. A track records that the app was recording over that span, "
                 "which is not the same as the device being in motion for all of it; Moving "
                 "Duration is the app's own smaller figure.",
        "paths": ('*/de.dennisguse.opentracks/databases/database.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "opentracks_trackpoints": {
        "name": "OpenTracks - Trackpoints",
        "description": "Parses recorded track positions from the OpenTracks Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "OpenTracks",
        "sample_data": {
            "emu_a15_oss_v6": "OpenTracks 4.28.2 | 15 rows",
        },
        "notes": "One row per entry in the trackpoints table of databases/database.db, joined to "
                 "the track it belongs to. Each row is a position the app logged while recording, "
                 "so the rows are a location history for the recording periods. Latitude and "
                 "Longitude are stored as integers and are divided by 1E6 "
                 "(ContentProviderUtils.java lines 318 and 319 at OpenTracksApp/OpenTracks tag "
                 "v4.28.2, ab8791a620a005da514e7659abd159eef10c5696); on the tested device a "
                 "stored -77034198 reads as -77.034198. Both are empty on the segment rows "
                 "described below. Time is Unix milliseconds reported as UTC, with Time (Local) "
                 "derived from the parent track's recorded UTC offset. Accuracy is the position's "
                 "reported accuracy in metres, Speed is metres per second and Bearing is degrees. "
                 "Type is decoded from the app's TrackPoint.Type enum, -2 Segment start "
                 "(manual), -1 Segment start (automatic), 0 Trackpoint, 1 Segment end (manual), "
                 "2 Sensorpoint and 3 Idle (TrackPoint.java at the same commit); any other value "
                 "is reported as stored. That distinction matters: a -2 row marks a recording "
                 "being started or resumed and a 1 row marks it being stopped, both of which the "
                 "app's own comments attribute to user interaction, while -1 marks a gap the app "
                 "itself decided to break on and 3 marks the device becoming idle. The segment "
                 "rows carry no coordinates. The sensor columns (heart rate, cadence, power, "
                 "temperature) are populated only when a Bluetooth sensor is paired and were "
                 "empty on the tested device, which had none; they are kept because their absence "
                 "is itself worth stating. Track ID held one value on the tested device because "
                 "it carried a single recording, and Speed (m/s) and Bearing were identical "
                 "across every row because the injected positions carried neither; on a device "
                 "recording real movement both vary. KML output is produced from the "
                 "coordinates.",
        "paths": ('*/de.dennisguse.opentracks/databases/database.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "opentracks_markers": {
        "name": "OpenTracks - Markers",
        "description": "Parses markers placed on recorded tracks in the OpenTracks Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "OpenTracks",
        "sample_data": {
            "emu_a15_oss_v6": "OpenTracks 4.28.2 | 0 rows, checked: the markers table is present and empty",
        },
        "notes": "One row per entry in the markers table of databases/database.db, joined to its "
                 "track. A marker is a point placed on a running recording through the app's "
                 "marker function, with a Name, Description, a Marker Type as the app localised "
                 "it, coordinates, Altitude, Accuracy and Bearing, and an optional Photo URL "
                 "pointing at an image the app stored for it. Latitude and Longitude are divided "
                 "by 1E6 as in the Trackpoints artifact, and Time is Unix milliseconds reported "
                 "as UTC with a local rendering from the parent track's recorded offset. Unlike "
                 "a trackpoint, which the app logs on a timer, a marker is placed deliberately, "
                 "so a row records a point someone chose to mark. The markers table was present "
                 "and empty on the tested device because no marker was placed, which is recorded "
                 "as a checked zero rather than omitted. The Photo URL is reported as stored and "
                 "the image it names is not currently resolved to the file on disk; a sample "
                 "carrying a marker photo would close that gap. KML output is produced from the "
                 "coordinates.",
        "paths": ('*/de.dennisguse.opentracks/databases/database.db*',),
        "output_types": "all",
        "artifact_icon": "flag",
    },
}

import datetime

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/database.db'

# TrackPoint.Type at OpenTracksApp/OpenTracks tag v4.28.2 (ab8791a6...).
POINT_TYPES = {
    -2: 'Segment start (manual)',
    -1: 'Segment start (automatic)',
    0: 'Trackpoint',
    1: 'Segment end (manual)',
    2: 'Sensorpoint',
    3: 'Idle',
}


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


def _local(value, offset_seconds):
    """The wall clock the recording was made against, from the track's own stored offset."""
    if not value or offset_seconds is None:
        return ''
    try:
        moment = datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
        shifted = moment.astimezone(datetime.timezone(datetime.timedelta(seconds=int(offset_seconds))))
        return shifted.strftime('%Y-%m-%d %H:%M:%S %z')
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _offset(seconds):
    if seconds is None or seconds == '':
        return ''
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return ''
    sign = '-' if total < 0 else '+'
    hours, rem = divmod(abs(total), 3600)
    return f'UTC{sign}{hours:02d}:{rem // 60:02d}'


def _coord(value):
    """Stored coordinates are the degree value multiplied by 1E6."""
    if value is None or value == '':
        return ''
    try:
        return int(value) / 1E6
    except (TypeError, ValueError):
        return ''


def _lookup(table, value):
    try:
        key = int(value)
    except (TypeError, ValueError):
        return '' if value in (None, '') else f'{value} (as stored)'
    if key in table:
        return table[key]
    return f'{key} (as stored)'


def _seconds(millis):
    if millis is None or millis == '':
        return ''
    try:
        return round(int(millis) / 1000, 3)
    except (TypeError, ValueError):
        return ''


@artifact_processor
def opentracks_tracks(context):
    query = '''SELECT time_start, time_stop, name, description, activity_type_localized,
                      activity_type, duration_total, duration_moving, distance, speed_max,
                      altitude_min, altitude_max, altitude_gain, altitude_loss,
                      time_offset, _id
               FROM tracks ORDER BY time_start DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _local(r[0], r[14]), _ms(r[1]), r[2] or '', r[3] or '',
                r[4] or '', r[5] or '', _seconds(r[6]), _seconds(r[7]), r[8], r[9],
                r[10], r[11], r[12], r[13], _offset(r[14]), r[15],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Start Time', 'datetime'), 'Start (Local)', ('Stop Time', 'datetime'), 'Name',
        'Description', 'Activity Type', 'Activity Type (as stored)', 'Total Duration (s)',
        'Moving Duration (s)', 'Distance (m)', 'Max Speed (m/s)', 'Altitude Min (m)',
        'Altitude Max (m)', 'Altitude Gain (m)', 'Altitude Loss (m)', 'UTC Offset',
        'Track ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def opentracks_trackpoints(context):
    query = '''SELECT p.time, p.latitude, p.longitude, p.elevation, p.accuracy, p.speed,
                      p.bearing, p.type, t.name, p.trackid, p._id, t.time_offset,
                      p.sensor_heartrate, p.sensor_cadence, p.sensor_power,
                      p.sensor_temperature
               FROM trackpoints p
               LEFT JOIN tracks t ON t._id = p.trackid
               ORDER BY p.time ASC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _local(r[0], r[11]), _coord(r[1]), _coord(r[2]), r[3], r[4],
                r[5], r[6], _lookup(POINT_TYPES, r[7]), r[8] or '', r[9], r[10],
                r[12], r[13], r[14], r[15],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Time', 'datetime'), 'Time (Local)', 'Latitude', 'Longitude', 'Altitude (m)',
        'Accuracy (m)', 'Speed (m/s)', 'Bearing', 'Type', 'Track', 'Track ID',
        'Trackpoint ID', 'Heart Rate', 'Cadence', 'Power', 'Temperature', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def opentracks_markers(context):
    query = '''SELECT m.time, m.name, m.description, m.marker_type_localized,
                      m.latitude, m.longitude, m.altitude, m.accuracy, m.bearing,
                      m.photoUrl, t.name, m.trackid, m._id, t.time_offset
               FROM markers m
               LEFT JOIN tracks t ON t._id = m.trackid
               ORDER BY m.time ASC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _local(r[0], r[13]), r[1] or '', r[2] or '', r[3] or '',
                _coord(r[4]), _coord(r[5]), r[6], r[7], r[8], r[9] or '',
                r[10] or '', r[11], r[12],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Time', 'datetime'), 'Time (Local)', 'Name', 'Description', 'Marker Type',
        'Latitude', 'Longitude', 'Altitude (m)', 'Accuracy (m)', 'Bearing', 'Photo URL',
        'Track', 'Track ID', 'Marker ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
