__artifacts_v2__ = {
    "what3words_saved_places": {
        "name": "what3words - Locations",
        "description": "Rows of the what3words LocationRealm store, with the three word address, "
                       "the stored label, the nearest place and the coordinates",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_LocationRealm table of the app's Realm store "
                 "(files/default.realm) using the vendored realm_parser. The latitude and "
                 "longitude are the coordinates the app stored for the address. Every class_LocationRealm row in the active version of each store is reported. The file's inactive version is not reported. Location Type Value is the locationType "
                 "value as stored; its meaning is not established, so a row is not shown to be a "
                 "saved place by this artifact alone. Each what3words default.realm found is read and the rows are reported together. Copies of one store under different storage paths are read once. Android User is the user the store's path denotes: 0 for data/data, the number in the path for data/user/<n> and the mirrored layouts, and blank for a path under none of them, which includes a rollback snapshot. No column other than Android User separates two stores. Of the 39 images run, 6 held a store, one each. Four gave rows, all for user 0. The other two sit under user 10 and hold no rows in either table. A second store on one image, and a row for a user other than 0, are not exercised on real data.",
        "paths": ('*/com.what3words.android/files/default.realm',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.what3words.android | 2 rows",
        },
    },
    "what3words_lists": {
        "name": "what3words - Location Lists",
        "description": "Rows of the what3words LocationsListsRealm store, with the list label, the "
                       "number of locations in it, the stored createdBy value and the created and "
                       "updated times",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_LocationsListsRealm table of the app's Realm store. "
                 "createdBy (as stored) is the createdBy value; what it identifies is not "
                 "established. isSharedList (as stored) is the isSharedList value with no label "
                 "applied, and is blank where the row holds none. Created and Updated are the createdWhen and updatedAt integers "
                 "shown as UTC. They are read as Unix time, with the unit taken from the size of the number. The epoch and unit are not confirmed from the app's code. On hc_pixel8pro_a16, hc_pixel8pro_a17, sharon_a13 and sharon_a14 (one list row each) createdWhen has 13 digits, read as milliseconds and cut to whole seconds. updatedAt has 10 digits, read as seconds, on three of them and holds no value on sharon_a13. A value of 0 or no value is shown blank. The listTypeId, order, sortBy, collaboratorCount and followerCount columns are not reported. Rows come from the active version of each store, and the file's inactive version is not reported. Each what3words default.realm found is read and the rows are reported together. Copies of one store under different storage paths are read once. Android User is the user the store's path denotes: 0 for data/data, the number in the path for data/user/<n> and the mirrored layouts, and blank for a path under none of them, which includes a rollback snapshot. No column other than Android User separates two stores. Of the 39 images run, 6 held a store, one each. Four gave rows, all for user 0. The other two sit under user 10 and hold no rows in either table. A second store on one image, and a row for a user other than 0, are not exercised on real data.",
        "paths": ('*/com.what3words.android/files/default.realm',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.what3words.android | 1 row",
        },
    },
}

from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc
from scripts.realm_parser import parse_realm_file, realm_rows


def _realm_ts(value):
    """The vendored realm_parser renders Realm date columns as 'YYYY-MM-DD HH:MM:SS UTC';
    turn that into a timezone-aware datetime so it sorts and timelines correctly."""
    if not value or not isinstance(value, str):
        return value
    try:
        return datetime.strptime(value.replace(' UTC', ''), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return value


def _is_what3words_realm(path):
    """Guard: the default.realm name is used by several apps, so confirm this Realm
    actually carries what3words classes before reporting rows."""
    tables = parse_realm_file(path).get("active", {})
    return 'class_LocationRealm' in tables or 'class_LocationsListsRealm' in tables


def _realm_paths(context):
    """Each what3words store, one per Android user and storage view."""
    return [str(path) for path in unique_files(context)
            if str(path).endswith('default.realm') and _is_what3words_realm(str(path))]


@artifact_processor
def what3words_saved_places(context):
    source_paths = _realm_paths(context)
    data_list = []

    for source_path in source_paths:
        user = android_user(context.get_relative_path(source_path))
        for row in realm_rows(source_path, 'class_LocationRealm'):
            data_list.append((
                _realm_ts(row.get('modificationTime')),
                row.get('threeWordAddress'),
                row.get('label'),
                row.get('nearestPlace'),
                row.get('lat'),
                row.get('lng'),
                row.get('countryCode'),
                row.get('language'),
                row.get('locationType'),
                row.get('order'),
                user,
            ))

    data_headers = (
        ('Modification Time', 'datetime'),
        'Three Word Address',
        'Label',
        'Nearest Place',
        'Latitude',
        'Longitude',
        'Country Code',
        'Language',
        'Location Type Value',
        'Order',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def what3words_lists(context):
    source_paths = _realm_paths(context)
    data_list = []

    for source_path in source_paths:
        user = android_user(context.get_relative_path(source_path))
        for row in realm_rows(source_path, 'class_LocationsListsRealm'):
            created_when = row.get('createdWhen')
            updated_at = row.get('updatedAt')
            data_list.append((
                convert_unix_ts_to_utc(created_when) if created_when else '',
                convert_unix_ts_to_utc(updated_at) if updated_at else '',
                row.get('label'),
                row.get('count'),
                row.get('createdBy'),
                row.get('color'),
                '' if row.get('isSharedList') is None else str(row.get('isSharedList')),
                row.get('shareType'),
                row.get('sharedListId'),
                row.get('id'),
                user,
            ))

    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Label',
        'Location Count',
        'createdBy (as stored)',
        'Colour',
        'isSharedList (as stored)',
        'Share Type',
        'Shared List ID',
        'List ID',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)
