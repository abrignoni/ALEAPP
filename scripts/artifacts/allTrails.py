__artifacts_v2__ = {
    "alltrails_trackpoints": {
        "name": "AllTrails - Trackpoints",
        "description": "Position fixes recorded in the AllTrails trackpoints table, with the "
                       "coordinates, elevation, accuracy, speed and bearing for each point of a "
                       "recorded track",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the trackpoints table of databases/alltrails.\n"
                 "lat and lng are stored as integers. Dividing them by 1,000,000 is the only "
                 "scaling of the stored values that produces a valid coordinate pair, and the "
                 "result falls in the same state as the place names recorded in the database's "
                 "locations table, so that is the scaling used.\n"
                 "Two timestamps are stored per point and both are reported: time and "
                 "systemtime, each Unix epoch milliseconds. They differ by a fraction of a second "
                 "on the tested corpus and nothing in the extraction documents which clock each "
                 "comes from, so neither is presented as authoritative over the other.\n"
                 "Elevation, accuracy, speed and bearing are reported as stored. The units are "
                 "not stated in the database; for speed, metres per second is consistent with "
                 "the recorded track (see the AllTrails - Recorded Activities notes), but the "
                 "column is reported unlabelled rather than converted.\n"
                 "Track ID groups the points of one recording and matches the line the AllTrails "
                 "- Recorded Activities artifact reports.\n"
                 "The database's WAL is load-bearing for this app, so the -wal and -shm sidecars "
                 "are included in the paths above and must travel with the database.",
        "paths": ('*/com.alltrails.alltrails/databases/alltrails*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "pixel7a_a14": "Android 14 | AllTrails | 809 rows",
        },
    },
    "alltrails_recorded_activities": {
        "name": "AllTrails - Recorded Activities",
        "description": "Activities recorded on the device, with the name, the start and end "
                       "times, the total distance, the elevation change and the moving time",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the maps table of databases/alltrails, joined to lines and "
                 "line_geo_stats through map_id, and to users through user_id.\n"
                 "Units are derived from the data rather than documented. On the tested corpus "
                 "speed_average multiplied by time_moving equals distance_total to within a "
                 "metre (1.5784 x 2216 = 3498, against a stored 3497.75), which is consistent "
                 "with distance in metres, speed in metres per second and the two time columns "
                 "in seconds. The column headers say the unit is derived rather than presenting "
                 "it as documented, and they spell metres per second out in full, because an "
                 "abbreviated m/s sanitizes to a column name ending in _ms that reads as "
                 "milliseconds.\n"
                 "time_start and time_end are Unix epoch milliseconds. They are not identical to "
                 "the first and last trackpoint of the matching track: on the tested corpus "
                 "time_start is 0.9 seconds before the first point and time_end 2.6 seconds after "
                 "the last, so the stats bracket the track rather than matching it exactly. That "
                 "still cross-checks the epoch and the scale of both readings.\n"
                 "Activity ID and Privacy Level are reported as stored: the database carries no "
                 "table mapping the activity id to an activity name, and the privacy level is a "
                 "URN string.\n"
                 "A row here is an activity record the app held. Whether the device was carried "
                 "for the whole of it is not established by the record.",
        "paths": ('*/com.alltrails.alltrails/databases/alltrails*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | AllTrails | 1 row",
        },
    },
    "alltrails_photos": {
        "name": "AllTrails - Photos",
        "description": "Photos attached to AllTrails maps and trails, with the recorded local "
                       "path, any coordinates stored against the photo, the owning activity and "
                       "the picture itself where it is present in the extraction",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the map_photos and trail_photos tables of databases/alltrails, "
                 "distinguished by the Record Source column.\n"
                 "The picture is linked by the path the app recorded for it, not by correlation. "
                 "map_photos.local_path holds an absolute on-device path; the file name from that "
                 "path is matched against the extracted files and the match is checked in as "
                 "media. On the tested corpus the recorded path resolved to a file present in the "
                 "extraction under the app's external storage directory.\n"
                 "trail_photos rows carried no local_path in the tested corpus, so those rows are "
                 "reported without a picture. That is the absence of a locally stored copy, not "
                 "evidence the photo never existed.\n"
                 "Where a photo is tied to a location record, both the coordinates and the place "
                 "names from that record are reported. On the tested corpus one of the five "
                 "locations rows carried a latitude and longitude and it is the one the map photo "
                 "points at, so that photo has coordinates while the rows holding only city, "
                 "region and country do not. A place name is not a coordinate and the two are "
                 "reported in separate columns for that reason.",
        "paths": ('*/com.alltrails.alltrails/databases/alltrails*',
                  '*/com.alltrails.alltrails/files/Pictures/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "pixel7a_a14": "Android 14 | AllTrails | 2 rows",
        },
    },
    "alltrails_user": {
        "name": "AllTrails - User",
        "description": "The AllTrails account held on the device, with the user name, the display "
                       "name, the account identifier and the recorded home location",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the users table of databases/alltrails, joined to locations through "
                 "location_id for the recorded place names.\n"
                 "Remote ID is the account identifier AllTrails uses server side, and is the "
                 "value the userlists table references as its user_id. The referral link "
                 "contains the account's own referral code and is reported as stored.\n"
                 "The counts on this row (reviews, followers, tracks, photos) are the values the "
                 "client had cached for the profile.",
        "paths": ('*/com.alltrails.alltrails/databases/alltrails*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | AllTrails | 1 row",
        },
    },
}

import os

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_unix_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records)

# lat and lng are stored as integers; see the artifact notes for the derivation.
COORD_SCALE = 1000000.0


def _db_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'alltrails':
            return file_found
    return None


def _pictures(files_found):
    """Index the extracted picture files by name so a recorded local_path can be
    resolved to the file it names."""
    pictures = {}
    for file_found in files_found:
        file_found = str(file_found)
        if '/Pictures/' in file_found.replace(os.sep, '/'):
            pictures[os.path.basename(file_found)] = file_found
    return pictures


def _coord(value):
    if value is None:
        return ''
    try:
        return round(int(value) / COORD_SCALE, 6)
    except (TypeError, ValueError):
        return ''


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) / 1000)
    except (TypeError, ValueError):
        return ''


@artifact_processor
def alltrails_trackpoints(context):
    source_path = _db_path(context.get_files_found())
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'trackpoints'):
        query = '''
        SELECT time, lat, lng, elevation, accuracy, speed, bearing, systemtime,
               track_id, segment_id, map_id, connectivity, _id
        FROM trackpoints
        ORDER BY time
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                _ms(record[0]),
                _coord(record[1]),
                _coord(record[2]),
                record[3],
                record[4],
                record[5],
                record[6],
                _ms(record[7]),
                record[8],
                record[9],
                record[10],
                record[11] or '',
                record[12],
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Elevation (as stored)',
        'Accuracy (as stored)',
        'Speed (as stored)',
        'Bearing (as stored)',
        ('System Timestamp', 'datetime'),
        'Track ID',
        'Segment ID',
        'Map ID',
        'Connectivity (as stored)',
        'Record ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def alltrails_recorded_activities(context):
    source_path = _db_path(context.get_files_found())
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'maps'):
        query = '''
        SELECT m.created_at, m.name, u.user_name, s.time_start, s.time_end,
               s.distance_total, s.elevation_gain, s.elevation_loss, s.elevation_min,
               s.elevation_max, s.speed_average, s.time_moving, s.time_total,
               m.type, m.activity_id, m.privacy_level, l._id, m.data_uid, m._id
        FROM maps m
        LEFT JOIN users u ON m.user_id = u._id
        LEFT JOIN lines l ON l.map_id = m._id
        LEFT JOIN line_geo_stats s ON s._id = l.line_geo_stats_id
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                record[0],
                record[1],
                record[2],
                _ms(record[3]),
                _ms(record[4]),
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                record[10],
                record[11],
                record[12],
                record[13],
                record[14],
                record[15],
                record[16],
                record[17],
                record[18],
            ))

    data_headers = (
        'Created',
        'Name',
        'User Name',
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        'Total Distance (derived metres)',
        'Elevation Gain (as stored)',
        'Elevation Loss (as stored)',
        'Elevation Min (as stored)',
        'Elevation Max (as stored)',
        'Average Speed (derived metres per second)',
        'Moving Time (derived seconds)',
        'Total Time (derived seconds)',
        'Type',
        'Activity ID (as stored)',
        'Privacy Level (as stored)',
        'Track ID',
        'Data UID',
        'Map ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def alltrails_photos(context):
    files_found = context.get_files_found()
    source_path = _db_path(files_found)
    data_list = []
    if not source_path:
        return _PHOTO_HEADERS, data_list, ''

    pictures = _pictures(files_found)

    def place(location_id):
        """Return (coordinates, place names). A locations row may carry either, or
        neither; they are different kinds of claim and are kept apart."""
        if not location_id:
            return '', '', ''
        query = ('SELECT lat, lng, city, region, country_name FROM locations '
                 f'WHERE _id = {int(location_id)}')
        for record in get_sqlite_db_records(source_path, query):
            names = ', '.join(str(part) for part in record[2:] if part)
            lat = record[0] if record[0] is not None else ''
            lng = record[1] if record[1] is not None else ''
            return lat, lng, names
        return '', '', ''

    def media_for(local_path):
        if not local_path:
            return '', ''
        name = os.path.basename(str(local_path).replace('\\', '/'))
        path = pictures.get(name)
        if not path:
            return '', name
        return check_in_media(path, name) or '', name

    if does_table_exist_in_db(source_path, 'map_photos'):
        query = '''
        SELECT p.created_at, p.local_path, p.title, p.description, m.name, p.location_id,
               p.remote_id, p.like_count, p._id
        FROM map_photos p LEFT JOIN maps m ON p.map_id = m._id
        '''
        for record in get_sqlite_db_records(source_path, query):
            media, name = media_for(record[1])
            lat, lng, names = place(record[5])
            data_list.append((
                record[0], media, name, lat, lng, record[2] or '', record[3] or '',
                record[4] or '', names, record[6], record[7], 'map_photos', record[8],
                record[1] or '',
            ))

    if does_table_exist_in_db(source_path, 'trail_photos'):
        query = '''
        SELECT created_at, local_path, title, description, location_id, remote_id,
               like_count, id
        FROM trail_photos
        '''
        for record in get_sqlite_db_records(source_path, query):
            media, name = media_for(record[1])
            lat, lng, names = place(record[4])
            data_list.append((
                record[0], media, name, lat, lng, record[2] or '', record[3] or '', '',
                names, record[5], record[6], 'trail_photos', record[7], record[1] or '',
            ))

    return _PHOTO_HEADERS, data_list, source_path


_PHOTO_HEADERS = (
    'Created',
    ('Picture', 'media'),
    'File Name',
    'Latitude',
    'Longitude',
    'Title',
    'Description',
    'Activity Name',
    'Recorded Place',
    'Remote ID',
    'Like Count',
    'Record Source',
    'Record ID',
    'Recorded Local Path',
)


@artifact_processor
def alltrails_user(context):
    source_path = _db_path(context.get_files_found())
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'users'):
        query = '''
        SELECT u.user_name, u.first_name, u.last_name, u.remote_id, l.city, l.region,
               l.country_name, l.postal_code, u.pro, u.metric, u.review_count,
               u.follower_count, u.following_count, u.track_count, u.photo_count,
               u.garmin_connected, u.facebook_connected, u.referral_link, u.slug, u._id
        FROM users u LEFT JOIN locations l ON u.location_id = l._id
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                record[0],
                ' '.join(p for p in (record[1], record[2]) if p),
                record[3],
                ', '.join(str(p) for p in (record[4], record[5], record[6], record[7]) if p),
                'Yes' if record[8] else 'No',
                'Yes' if record[9] else 'No',
                record[10],
                record[11],
                record[12],
                record[13],
                record[14],
                'Yes' if record[15] else 'No',
                'Yes' if record[16] else 'No',
                record[17] or '',
                record[18] or '',
                record[19],
            ))

    data_headers = (
        'User Name',
        'Display Name',
        'Remote ID',
        'Recorded Place',
        'Pro Account',
        'Metric Units',
        'Review Count',
        'Follower Count',
        'Following Count',
        'Track Count',
        'Photo Count',
        'Garmin Connected',
        'Facebook Connected',
        'Referral Link',
        'Slug',
        'Record ID',
    )
    return data_headers, data_list, source_path
