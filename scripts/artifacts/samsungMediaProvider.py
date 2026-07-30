__artifacts_v2__ = {
    "samsungMediaFiles": {
        "name": "Samsung Media Provider - Files",
        "description": "Media files indexed by the Samsung media provider (media.db, files "
                       "table): file path and name, taken/added/modified times, "
                       "coordinates and packed address, the URL and app a captured file "
                       "came from, and the favorite/hidden/trashed/deleted flags.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Media Provider",
        "notes": "The Address column is the packed multi-part string as stored (parts "
                 "separated by '|'). Reference: Cellebrite Location Booklet 2025.",
        "paths": ('*/com.samsung.android.providers.media/databases/media.db*',),
        "output_types": "all",
        "artifact_icon": "image",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.providers.media | 223 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.media | 32 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.media | 4 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.media | 16 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.media | 1439 rows",
        },
    },
    "samsungMediaLocations": {
        "name": "Samsung Media Provider - Locations",
        "description": "Reverse-geocoded places recorded by the Samsung media provider "
                       "(media.db, location table): coordinates with the resolved country, "
                       "locality, street and full address text.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Media Provider",
        "notes": "Reference: Cellebrite Location Booklet 2025.",
        "paths": ('*/com.samsung.android.providers.media/databases/media.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.providers.media | 91 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.media | 15 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.media | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.media | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.media | 116 rows",
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
def samsungMediaFiles(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'media.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT datetaken, date_added, date_modified, _display_name, _data, mime_type,
                   _size, latitude, longitude, addr, bucket_display_name,
                   owner_package_name, captured_url, captured_app, is_favorite, is_hide,
                   is_trashed, deleted
            FROM files
            ORDER BY datetaken DESC
        ''')

        for row in db_records:
            source_path = file_found
            latitude, longitude = _coord_pair(row[7], row[8])
            data_list.append((
                _ts(row[0]),
                _ts(row[1]),
                _ts(row[2]),
                row[3],
                row[4],
                row[5],
                row[6],
                latitude,
                longitude,
                row[9],
                row[10],
                row[11],
                row[12],
                row[13],
                row[14],
                row[15],
                row[16],
                row[17],
            ))

    data_headers = (
        ('Date Taken', 'datetime'),
        ('Date Added', 'datetime'),
        ('Date Modified', 'datetime'),
        'Display Name',
        'Path',
        'MIME Type',
        'Size',
        'Latitude',
        'Longitude',
        'Address',
        'Bucket',
        'Owner Package',
        'Captured URL',
        'Captured App',
        'Is Favorite',
        'Is Hide',
        'Is Trashed',
        'Deleted',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungMediaLocations(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'media.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT latitude, longitude, address_text, country_name, country_code,
                   admin_area, sub_admin_area, locality, sub_locality, street_name,
                   street_number, postal_code
            FROM location
            ORDER BY _id
        ''')

        for row in db_records:
            source_path = file_found
            latitude, longitude = _coord_pair(row[0], row[1])
            data_list.append((latitude, longitude) + tuple(row[2:]))

    data_headers = (
        'Latitude',
        'Longitude',
        'Address Text',
        'Country',
        'Country Code',
        'Admin Area',
        'Sub Admin Area',
        'Locality',
        'Sub Locality',
        'Street Name',
        'Street Number',
        'Postal Code',
    )
    return data_headers, data_list, source_path
