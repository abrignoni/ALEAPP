__artifacts_v2__ = {
    "samsungStoryServiceInfo": {
        "name": "Samsung Story Service - Media Info",
        "description": "Media entries indexed by the Samsung story service (dme.db, info "
                       "table): taken/added times, file path, coordinates with the "
                       "resolved place names, detected scene names, face count and the "
                       "moment each entry belongs to.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Story Service",
        "notes": "Reference: Cellebrite Location Booklet 2025.",
        "paths": ('*/com.samsung.storyservice/databases/dme.db*',),
        "output_types": "all",
        "artifact_icon": "image",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.storyservice | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.storyservice | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.storyservice | 4 rows",
            "samsungs20_a13": "Android 13 | com.samsung.storyservice | 16 rows",
            "sharon_a14": "Android 14 | com.samsung.storyservice | 1435 rows",
        },
    },
    "samsungStoryServiceMoments": {
        "name": "Samsung Story Service - Moments",
        "description": "Moments grouped by the Samsung story service (dme.db, moment "
                       "table): the time range each moment covers, its creation time, "
                       "title, media count and recorded place information.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Story Service",
        "notes": "",
        "paths": ('*/com.samsung.storyservice/databases/dme.db*',),
        "output_types": "standard",
        "artifact_icon": "book-open",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.storyservice | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.storyservice | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.storyservice | 2 rows",
            "samsungs20_a13": "Android 13 | com.samsung.storyservice | 4 rows",
            "sharon_a14": "Android 14 | com.samsung.storyservice | 62 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -wal/-shm sidecars and without the
    duplicates extractions carry for the same file (data_mirror, and /data/data next
    to /data/user/0).'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        if 'data_mirror' in file_found:
            continue
        normalized = file_found.replace('\\', '/').replace('/data/data/', '/data/user/0/')
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


def _ts(value):
    if not value:
        return ''
    return convert_unix_ts_to_utc(value)


def _coord_pair(latitude, longitude):
    '''Blank the unset coordinate pair (NULL, or 0/0).'''
    if latitude is None or longitude is None:
        return '', ''
    if latitude == 0 and longitude == 0:
        return '', ''
    return latitude, longitude


@artifact_processor
def samsungStoryServiceInfo(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'dme.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT datetaken, date_added, title, _data, media_type, latitude, longitude,
                   country_name, locality, poi_name, poi_city, street_name, scene_names,
                   face_count, is_delete, moment_id
            FROM info
            ORDER BY datetaken DESC
        ''')

        for row in db_records:
            source_path = file_found
            latitude, longitude = _coord_pair(row[5], row[6])
            data_list.append((
                _ts(row[0]),
                _ts(row[1]),
                row[2],
                row[3],
                row[4],
                latitude,
                longitude,
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                row[12],
                row[13],
                row[14],
                row[15],
            ))

    data_headers = (
        ('Date Taken', 'datetime'),
        ('Date Added', 'datetime'),
        'Title',
        'Path',
        'Media Type',
        'Latitude',
        'Longitude',
        'Country',
        'Locality',
        'POI Name',
        'POI City',
        'Street Name',
        'Scene Names',
        'Face Count',
        'Is Delete',
        'Moment ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungStoryServiceMoments(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'dme.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT start_time, end_time, creation_time, title, media_count, country_name,
                   location, poi_info, street_name_info, type, story_id, moment_id
            FROM moment
            ORDER BY start_time DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                _ts(row[0]),
                _ts(row[1]),
                _ts(row[2]),
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
            ))

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        ('Creation Time', 'datetime'),
        'Title',
        'Media Count',
        'Country',
        'Location',
        'POI Info',
        'Street Name Info',
        'Type',
        'Story ID',
        'Moment ID',
    )
    return data_headers, data_list, source_path
