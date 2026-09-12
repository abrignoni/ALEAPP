__artifacts_v2__ = {
    "samsungMediaFiles": {
        "name": "Samsung Media Provider - Files",
        "description": "Files listed in the Samsung media provider's files table (media.db): "
                       "file path and name, taken, added and modified times, coordinates "
                       "and packed address, the captured URL and captured app values, the "
                       "Is Favorite, Is Hide, Is Trashed and Deleted values as stored, and "
                       "the database each row came from.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Samsung Media Provider",
        "notes": "The Address column is the packed multi-part string as stored (parts "
                 "separated by '|'). Reference: Cellebrite Location Booklet 2025. Every "
                 "media.db the declared path matches is read, except that where one "
                 "user's database appears under more than one of the data/data, data/user "
                 "and data_mirror/data_ce storage paths, only one copy is read. A database "
                 "present only under data_mirror/data_ce is read as well; no tested image "
                 "carries one, and that case was exercised on a constructed tree. On "
                 "cookbook_a11 and samsungs20_a13 a second media.db sits under user/150, "
                 "and each image's system/users/150.xml records user 150 as a managed "
                 "profile named Secure Folder. The Source DB Path column names the "
                 "database each row came from, and the report's located-at line lists "
                 "every database read, including any that returned no rows. Is Hide and "
                 "Deleted held no value on any row of the ten tested images, and Is "
                 "Favorite and Is Trashed held only 0 or no value, so the tested images do "
                 "not show what any other value in those columns records.",
        "paths": ('*/com.samsung.android.providers.media/databases/media.db*',),
        "output_types": "all",
        "artifact_icon": "image",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | com.samsung.android.providers.media | 94 rows",
            "anne_a15": "Android 15 | com.samsung.android.providers.media | 223 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.providers.media | 17 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.providers.media | 30 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.media | 32 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.providers.media | 9 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.media | 2 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.media | 16 rows",
            "sharon_a13": "Android 13 | com.samsung.android.providers.media | 336 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.media | 1439 rows",
        },
    },
    "samsungMediaLocations": {
        "name": "Samsung Media Provider - Locations",
        "description": "Entries in the Samsung media provider's location table (media.db): "
                       "coordinates with country, locality, street and address text, and "
                       "the database each row came from.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Samsung Media Provider",
        "notes": "Reference: Cellebrite Location Booklet 2025. Every media.db the declared "
                 "path matches is read, except that where one user's database appears "
                 "under more than one of the data/data, data/user and data_mirror/data_ce "
                 "storage paths, only one copy is read. A database present only under "
                 "data_mirror/data_ce is read as well; no tested image carries one, and "
                 "that case was exercised on a constructed tree. On cookbook_a11 and "
                 "samsungs20_a13 a second media.db sits under user/150, and each image's "
                 "system/users/150.xml records user 150 as a managed profile named "
                 "Secure Folder; on both images that database held no location rows. The "
                 "Source DB Path column names the database each row came from, and the "
                 "report's located-at line lists every database read, including any that "
                 "returned no rows.",
        "paths": ('*/com.samsung.android.providers.media/databases/media.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | com.samsung.android.providers.media | 119 rows",
            "anne_a15": "Android 15 | com.samsung.android.providers.media | 91 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.providers.media | 2 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.providers.media | 22 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.media | 15 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.providers.media | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.media | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.media | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.providers.media | 48 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.media | 116 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc
from scripts.artifacts.storagePathViews import unique_files


def _media_dbs(context):
    '''Every distinct media.db the seeker staged, without the -wal/-shm sidecars.

    unique_files collapses the storage-view copies of one user's database (data/data,
    data/user/<id>, data_mirror/data_ce/<volume>/<id>) and keeps different users apart,
    because canonical_path keeps the Android user id in its key.'''
    return [file_found for file_found in unique_files(context)
            if file_found.endswith('media.db')]


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
    source_paths = []

    for file_found in _media_dbs(context):
        source_paths.append(file_found)
        source_db = context.get_relative_path(file_found)
        db_records = get_sqlite_db_records(file_found, '''
            SELECT datetaken, date_added, date_modified, _display_name, _data, mime_type,
                   _size, latitude, longitude, addr, bucket_display_name,
                   owner_package_name, captured_url, captured_app, is_favorite, is_hide,
                   is_trashed, deleted
            FROM files
            ORDER BY datetaken DESC
        ''')

        for row in db_records:
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
                source_db,
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
        'Source DB Path',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def samsungMediaLocations(context):
    data_list = []
    source_paths = []

    for file_found in _media_dbs(context):
        source_paths.append(file_found)
        source_db = context.get_relative_path(file_found)
        db_records = get_sqlite_db_records(file_found, '''
            SELECT latitude, longitude, address_text, country_name, country_code,
                   admin_area, sub_admin_area, locality, sub_locality, street_name,
                   street_number, postal_code
            FROM location
            ORDER BY _id
        ''')

        for row in db_records:
            latitude, longitude = _coord_pair(row[0], row[1])
            data_list.append((latitude, longitude) + tuple(row[2:]) + (source_db,))

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
        'Source DB Path',
    )
    return data_headers, data_list, '\n'.join(source_paths)
