__artifacts_v2__ = {
    "alltrails_trackpoints": {
        "name": "AllTrails - Trackpoints",
        "description": "Position fixes recorded in the AllTrails trackpoints table, with the "
                       "coordinates, elevation, accuracy, speed and bearing for each point of a "
                       "recorded track",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the trackpoints table of databases/alltrails.\n"
                 "lat and lng are stored as integers. On the tested image, dividing them by "
                 "1,000,000 produces a coordinate pair that falls in the same state as the place "
                 "names recorded in the database's locations table, so that is the scaling used; "
                 "the scale is not documented.\nTwo timestamps are stored per point and both are "
                 "reported: time and systemtime, each a 13 digit integer on all 809 rows of "
                 "pixel7a_a14 and read as Unix epoch milliseconds. The milliseconds are kept in "
                 "the HTML and TSV reports; the LAVA database stores a datetime column to the "
                 "whole second. On pixel7a_a14 systemtime is 0.434 to 3.205 seconds later than "
                 "time, and nothing in the extraction "
                 "documents which clock each comes from, so neither is presented as "
                 "authoritative over the other.\nElevation, accuracy, speed and bearing are "
                 "reported as stored. The units are not stated in the database; for speed, "
                 "metres per second is consistent with the recorded track (see the AllTrails - "
                 "Recorded Activities notes), but the column is reported unlabelled rather than "
                 "converted.\nTrack ID is the track_id column as stored. The AllTrails - "
                 "Recorded Activities artifact reports lines._id under the same header; no count "
                 "of how the two columns correspond is recorded here.\nThe -wal and -shm "
                 "sidecars are included "
                 "in the paths above and must travel with the database, because rows can sit in "
                 "the write ahead log.",
        "paths": ('*/com.alltrails.alltrails/databases/alltrails*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "pixel7a_a14": "Android 14 | AllTrails | 809 rows",
        },
    },
    "alltrails_recorded_activities": {
        "name": "AllTrails - Recorded Activities",
        "description": "Activity records held in the AllTrails maps table, with the name, "
                       "the start and end "
                       "times, the total distance, the elevation change and the moving time",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the maps table of databases/alltrails, joined to lines through map_id "
                 "and to line_geo_stats through the line's line_geo_stats_id, and to users "
                 "through user_id.\nUnits are derived from the data rather than documented. On "
                 "the tested corpus speed_average multiplied by time_moving equals distance_total "
                 "to within a metre (1.5784 x 2216 = 3498, against a stored 3497.75), which is "
                 "consistent with distance in metres, speed in metres per second and the two time "
                 "columns in seconds. The column headers say the unit is derived rather than "
                 "presenting it as documented, and they spell metres per second out in full, "
                 "because an abbreviated m/s sanitizes to a column name ending in _ms that reads "
                 "as milliseconds.\ntime_start and time_end are Unix epoch milliseconds. They are "
                 "not identical to the first and last trackpoint of the matching track: on the "
                 "tested corpus the stored time_start is 0.9 seconds before the first point's "
                 "stored time and time_end 2.6 seconds after the last (0.888 and 2.575 seconds "
                 "on the stored millisecond values of pixel7a_a14), so the stats bracket the "
                 "track rather than matching it exactly. The milliseconds are kept in the HTML "
                 "and TSV reports; the LAVA database stores a datetime column to the whole "
                 "second. That "
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
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the map_photos and trail_photos tables of databases/alltrails, "
                 "distinguished by the Record Source column.\n"
                 "The picture is found by the path the app recorded. On pixel7a_a14 "
                 "map_photos.local_path holds an absolute on-device path of the form "
                 "/storage/emulated/<Android user>/Android/data/com.alltrails.alltrails/files/"
                 "Pictures/<file>. The extracted file shown is the one whose path below the "
                 "app's Pictures folder equals the recorded one and whose own path names the "
                 "same Android user (media/<user> or emulated/<user>); it is checked in as "
                 "media. A file that only shares the name, in another subfolder or under "
                 "another Android user, is not used. A recorded path outside that Pictures "
                 "folder, or one with no extracted copy under the same Android user, is "
                 "reported without a picture; File Name and Recorded Local Path are still "
                 "filled. Where one file is extracted under more than one storage path of the "
                 "same user, the first by path order is shown. On pixel7a_a14 the one recorded "
                 "path resolved to a file present in the "
                 "extraction under data/media/0. The handling of a second Android user was "
                 "exercised on constructed paths only; pixel7a_a14 holds this app under "
                 "user 0 alone.\n"
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
        "description": "Rows of the AllTrails users table, with the user name, the display "
                       "name, the account identifier and the recorded home location",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "AllTrails",
        "notes": "Read from the users table of databases/alltrails, joined to locations through "
                 "location_id for the recorded place names.\n"
                 "Remote ID is the remote_id value as stored, and on the tested image equalled "
                 "the user_id stored in the userlists table, which this module does not read; "
                 "no count is recorded. The referral link contains the account's own "
                 "referral code and is reported as stored.\nThe counts on this row (reviews, "
                 "followers, tracks, photos) are reported as stored.",
        "paths": ('*/com.alltrails.alltrails/databases/alltrails*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | AllTrails | 1 row",
        },
    },
}

import os
import re
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, check_in_media,
                               does_table_exist_in_db, get_sqlite_db_records)

# lat and lng are stored as integers; see the artifact notes for the derivation.
COORD_SCALE = 1000000.0

_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _db_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'alltrails':
            return file_found
    return None


# A path inside the app's external Pictures folder, on the device or in the extraction:
# the Android user number where the path carries one, then the path below Pictures.
_PICTURE_PATH = re.compile(
    r'(?:(?:^|/)(?:media|emulated)/(\d+))?/Android/data/com\.alltrails\.alltrails'
    r'/files/Pictures/(.+)$')


def _picture_key(path):
    """Return (Android user or None, path below the Pictures folder), or None when the
    path is not inside the app's external Pictures folder."""
    match = _PICTURE_PATH.search(str(path).replace('\\', '/'))
    if not match:
        return None
    return match.group(1), match.group(2)


def _pictures(files_found):
    """Index the extracted picture files by their path below the Pictures folder, keeping
    every extracted copy and the Android user its path names, so a recorded local_path
    is resolved to the file at that path and not to any file sharing its name."""
    pictures = {}
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        key = _picture_key(file_found)
        if key:
            pictures.setdefault(key[1], []).append((key[0], file_found))
    return pictures


def _resolve_picture(pictures, local_path):
    """Return the extracted file the recorded path names, or None. A copy under another
    Android user is never used; when the recorded path names no user and the copies sit
    under more than one, none is used."""
    key = _picture_key(local_path)
    if not key:
        return None
    user, tail = key
    copies = pictures.get(tail, [])
    if user is not None:
        copies = [copy for copy in copies if copy[0] == user]
    elif len({copy[0] for copy in copies}) > 1:
        return None
    if not copies:
        return None
    return sorted(copy[1] for copy in copies)[0]


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
        return _EPOCH_UTC + timedelta(milliseconds=int(value))
    except (TypeError, ValueError, OverflowError):
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
        path = _resolve_picture(pictures, local_path)
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
